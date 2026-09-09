"""
app/routes/auth.py - Defines routes related to authentication, including login, logout,
                    password reset, and 2FA management.
"""

from datetime import datetime
import logging
import pyotp
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, session, current_app)
# from flask_mail import Message
from flask_login import login_required, current_user, login_user, logout_user
# from sqlalchemy.exc import SQLAlchemyError
from app.services.mailer import (send_verification_email, send_password_reset_email,
                                 send_verified_confirmation_email, send_password_changed_email)

from app.extensions import db
from app.models import User, Role
from app.models.base import utc_now
from app.forms import (
    LoginForm,
    SignupForm,
    TwoFactorForm,
    ResendVerificationForm,
    RequestResetForm,
    ResetPasswordForm,
    ChangePasswordForm)

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth",
                    template_folder="../templates/auth")

POST_LOGIN_ENDPOINT = "main.dashboard"

PASSWORD_CHANGE_EXEMPT_ENDPOINTS = {
    "auth.change_password",
    "auth.logout",
    "static",
}


# @auth_bp.before_app_request
# def enforce_password_change():
#     """
#     Any authenticated user who has never changed their (admin-issued
#     temporary) password is redirected to the change-password page,
#     regardless of which URL they requested.
#     """
#     if current_user.is_authenticated and not current_user.password_changed_at:
#         if request.endpoint not in PASSWORD_CHANGE_EXEMPT_ENDPOINTS:
#             current_app.logger.info("Redirecting user to change password | user_id=%s | ip=%s", current_user.id, request.remote_addr)
#             return redirect(url_for("auth.change_password"))
#     return None


# ----------------------------------------------------------------------
# Email verification
# ----------------------------------------------------------------------
@auth_bp.route("/verify-email/<token>")
def verify_email(token):
    """
    Verify a user's email address using a token sent via email.
    """
    user = User.query.filter_by(email_verification_token=token).first()

    if user is None or not user.verify_email_verification_token(token):
        current_app.logger.warning("Invalid or expired email verification token used | token=%s | ip=%s", token, request.remote_addr)
        flash("Invalid or expired verification link.", "danger")
        return redirect(url_for("auth.resend_verification"))

    db.session.commit()
    send_verified_confirmation_email(user)
    current_app.logger.info("Email verified successfully | user_id=%s | ip=%s", user.id, request.remote_addr)
    flash("Your email has been verified. You can now log in.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/resend-verification", methods=["GET", "POST"])
def resend_verification():
    """
    Resend email verification link.
    """
    form = ResendVerificationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        current_app.logger.info("Resending email verification | user_id=%s | ip=%s", user.id if user else "unknown", request.remote_addr)
        if user and not user.is_email_verified:
            token = user.generate_email_verification_token()
            db.session.commit()
            send_verification_email(user, token)
            current_app.logger.info("Verification email sent | user_id=%s | ip=%s", user.id, request.remote_addr)
        # Same message either way so we don't reveal which emails are registered.
        flash("If that account exists and is unverified, a new email has been sent.", "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/resend_verification.html", form=form,
                           title="Resend Verification Email")


# ----------------------------------------------------------------------
# New user signup
# ----------------------------------------------------------------------
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Allow new users to create an account.
    """
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = SignupForm()
    if form.validate_on_submit():
        firstname = form.firstname.data.strip()
        lastname = form.lastname.data.strip()
        email = form.email.data.lower().strip()
        country = form.country.data.strip()
        currency = form.currency.data.strip()
        timezone = form.timezone.data.strip()
        avatar = form.avatar.data or None
        password = form.password.data

        # Check if role already exists
        existing_role = Role.query.filter_by(name="user").first()
        if not existing_role:
            current_app.logger.error("Role 'user' not found | ip=%s", request.remote_addr)
            flash("An error occurred while creating your account.", "danger")
            return render_template("auth/signup.html", form=form, title="Sign Up")
        role = existing_role.id

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            current_app.logger.warning("Attempt to create duplicate account | email=%s | ip=%s", email, request.remote_addr)
            flash("An account with that email already exists.", "danger")
            return render_template("auth/signup.html", form=form, title="Sign Up")

        # Create new user
        user = User(
            email=email,
            firstname=firstname,
            lastname=lastname,
            country=country,
            currency=currency,
            timezone=timezone,
            avatar=avatar,
            role_id=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Generate and send verification token
        token = user.generate_email_verification_token()
        send_verification_email(user, token)

        current_app.logger.info("New user created and verification email sent | user_id=%s | ip=%s", user.id, request.remote_addr)
        flash("Your account has been created. Please check your email for a verification link.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html", form=form, title="Sign Up")


# ----------------------------------------------------------------------
# Login (first factor) + TOTP verification (second factor)
# ----------------------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Admin login — email + password, with optional TOTP step.
    """
    if current_user.is_authenticated:
        current_app.logger.info("User id=%s already authenticated, redirecting to dashboard | ip=%s",
                                current_user.id, request.remote_addr)
        return redirect(url_for(POST_LOGIN_ENDPOINT))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        password = form.password.data

        # Find user
        user = User.query.filter_by(email=email).first()

        # Handle non-existent user
        if not user:
            current_app.logger.warning("Invalid login attempt | email=%s | ip=%s", email, request.remote_addr)
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form, title="Sign In")

        # --- ACCOUNT LOCK CHECK ---
        if user.is_account_locked:
            if user.locked_until:
                remaining = (user.locked_until - datetime.now()).seconds // 60
                if remaining > 0:
                    current_app.logger.warning("Login attempt on locked account | user_id=%s | ip=%s", user.id, request.remote_addr)
                    flash(f'Account is locked. Please try again in {remaining} minutes.', 'warning')
                    return render_template("auth/login.html", form=form, title="Sign In")
            # If locked_until is None or expired, unlock
            user.unlock_account()
            db.session.commit()
            current_app.logger.info("Account auto-unlocked after lock expiry | user_id=%s | ip=%s", user.id, request.remote_addr)
            flash('Account unlocked. Please try again.', 'info')
            return render_template("auth/login.html", form=form, title="Sign In")

        # --- PASSWORD CHECK ---
        if not user.check_password(password):
            # Record failed attempt (this will auto-lock if >= 5)
            user.record_failed_login()
            db.session.commit()

            # Check if account got locked
            if user.is_account_locked:
                current_app.logger.warning("Account locked due to repeated failed login attempts | user_id=%s | ip=%s", user.id, request.remote_addr)
                flash("This account has been locked due to repeated failed login attempts. "
                      "Try again later after 10 minutes.", "danger")
            else:
                remaining_attempts = 5 - user.failed_login_attempts
                current_app.logger.warning("Failed login attempt | user_id=%s | ip=%s", user.id, request.remote_addr)
                flash(f"Invalid email or password. You have {remaining_attempts} "
                      f"more attempt(s) before your account is locked.", "warning")

            return render_template("auth/login.html", form=form, title="Sign In")

        # --- POST-PASSWORD CHECKS ---
        # Ensure account isn't locked (shouldn't happen, but just in case)
        if user.is_account_locked:
            current_app.logger.warning("Login attempt on locked account | user_id=%s | ip=%s", user.id, request.remote_addr)
            flash("Account is locked. Please contact administrator.", "danger")
            return render_template("auth/login.html", form=form, title="Sign In")

        # Check if account is active
        if not user.is_active:
            current_app.logger.warning("Login attempt on deactivated account | user_id=%s | ip=%s", user.id, request.remote_addr)
            flash("This account has been deactivated. Contact an administrator.", "warning")
            return render_template("auth/login.html", form=form, title="Sign In")

        # Check if email is verified
        if not user.is_email_verified:
            current_app.logger.warning("Login attempt on unverified email | user_id=%s | ip=%s", user.id, request.remote_addr)
            flash("Please verify your email before logging in.", "warning")
            return render_template("auth/login.html", form=form, title="Sign In")

        # --- 2FA CHECK ---
        if user.is_2fa_enabled:
            session["pre_2fa_user_id"] = user.id
            current_app.logger.info("Password verified, awaiting 2FA verification | user_id=%s | ip=%s", user.id, request.remote_addr)
            return redirect(url_for("auth.verify_2fa"))

        # --- SUCCESSFUL LOGIN ---
        user.record_login()
        db.session.commit()
        login_user(user)
        current_app.logger.info("User logged in successfully | user_id=%s | ip=%s", user.id, request.remote_addr)

        # Check if password needs to be changed
        if not user.password_changed_at:
            current_app.logger.info("Login redirected to force password change | user_id=%s | ip=%s", user.id, request.remote_addr)
            flash("Please change your password.", "info")
            return redirect(url_for("auth.change_password"))

        # Redirect
        next_page = request.args.get("next")
        flash(f"Welcome back, {user.fullname}!", "success")
        return redirect(next_page or url_for(POST_LOGIN_ENDPOINT))

    return render_template("auth/login.html", form=form, title="Sign In")


@auth_bp.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    """
    Second-factor verification for users with TOTP-based 2FA enabled.
    """
    user_id = session.get("pre_2fa_user_id")
    if not user_id:
        current_app.logger.warning("2FA verification attempted without valid session | ip=%s", request.remote_addr)
        flash("Please login to continue.", "info")
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    if user is None:
        current_app.logger.warning("2FA verification attempted for non-existent user | user_id=%s | ip=%s", user_id, request.remote_addr)
        session.pop("pre_2fa_user_id", None)
        flash("Please login to continue.", "info")
        return redirect(url_for("auth.login"))

    form = TwoFactorForm()
    if form.validate_on_submit():
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(form.token.data, valid_window=1):
            session.pop("pre_2fa_user_id", None)

            user.record_login()
            db.session.commit()
            login_user(user)
            current_app.logger.info("2FA verification successful | user_id=%s | ip=%s", user.id, request.remote_addr)
            flash(f"Welcome back, {user.fullname}!", "success")

            if not user.password_changed_at:
                current_app.logger.info("Login redirected to force password change after 2FA | user_id=%s | ip=%s", user.id, request.remote_addr)
                flash("Please change your password.", "info")
                return redirect(url_for("auth.change_password"))

            return redirect(url_for(POST_LOGIN_ENDPOINT))

        current_app.logger.warning("Invalid 2FA token submitted | user_id=%s | ip=%s", user.id, request.remote_addr)
        flash("Invalid authentication code.", "danger")
        # form.add_form_error("Invalid authentication code.")

    return render_template("auth/verify_2fa.html", form=form, title="Two-Factor Authentication")


# ----------------------------------------------------------------------
# Forced / voluntary password change
# ----------------------------------------------------------------------
@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """
    Change password route. This is required on first login after an admin
    creates a new account, and can be used voluntarily afterward.
    """
    forced = not current_user.password_changed_at

    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            current_app.logger.warning("Failed password change attempt | user_id=%s | ip=%s", current_user.id, request.remote_addr)
            flash("Current password is incorrect.", "danger")
            return render_template("auth/change_password.html", form=form, forced=forced)

        current_user.set_password(form.new_password.data)
        current_user.password_changed_at = utc_now()
        db.session.commit()

        send_password_changed_email(current_user)

        current_app.logger.info("Password changed successfully | user_id=%s | ip=%s", current_user.id, request.remote_addr)
        flash("Your password has been updated.", "success")
        return redirect(url_for(POST_LOGIN_ENDPOINT))

    return render_template("auth/change_password.html", form=form, forced=forced,
                           title="Change Password")


# ----------------------------------------------------------------------
# Logout
# ----------------------------------------------------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    """
    Log the user out and redirect to the login page.
    """
    logout_user()
    current_app.logger.info("User logged out | ip=%s", request.remote_addr)
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


# ----------------------------------------------------------------------
# Forgot-password reset
# ----------------------------------------------------------------------
@auth_bp.route("/reset-password-request", methods=["GET", "POST"])
def reset_password_request():
    """
    Request a password reset email. If the email is registered, a reset link
    will be sent. If not, the user will still see a success message to avoid
    revealing which emails are registered.
    """
    if current_user.is_authenticated:
        return redirect(url_for(POST_LOGIN_ENDPOINT))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user:
            # Note: User.generate_password_reset_token() sets
            # password_reset_token as a side effect but does not return
            # it, so we read it back off the user object.
            user.generate_password_reset_token()
            db.session.commit()
            send_password_reset_email(user, user.password_reset_token)
            current_app.logger.info("Password reset requested | user_id=%s | ip=%s", user.id, request.remote_addr)
        else:
            current_app.logger.info("Password reset requested for non-existent user | email=%s | ip=%s", form.email.data.lower().strip(), request.remote_addr)
        flash("If that email is registered, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password_request.html", form=form,
                           title="Request Password Reset")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """
    Reset password using a token sent via email. If the token is valid, the user
    can set a new password. If not, they are redirected to the reset request page.
    """
    user = User.query.filter_by(password_reset_token=token).first()

    if user is None or not user.verify_password_reset_token(token):
        current_app.logger.warning("Invalid or expired password reset token used | token=%s | ip=%s", token, request.remote_addr)
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("auth.reset_password_request"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_password_reset_token()
        user.password_changed_at = utc_now()
        user.unlock_account()
        db.session.commit()

        send_password_changed_email(user)

        current_app.logger.info("Password changed successfully | user_id=%s | ip=%s", user.id, request.remote_addr)
        flash("Your password has been reset. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form,
                           title="Reset Password")


# End of file
