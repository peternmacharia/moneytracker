"""
app/routes/user.py - Defines routes related to user management.
"""

# from datetime import datetime, timedelta
import logging
# import pyotp
from flask import (Blueprint, render_template, redirect, url_for, request,
                   flash)
# # from flask_mail import Message
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.extensions import db
from app.models import User, Role
from app.models.base import utc_now
from app.forms import (
    ProfileForm, ChangePasswordForm, Enable2FAForm, Disable2FAForm, 
    DeleteForm)
from app.utils.qrcode import generate_qr_b64
from app.utils.decorators import permission_required

logger = logging.getLogger(__name__)


user_bp = Blueprint("user", __name__, url_prefix="/user",
                    template_folder="../templates/user")


def _populate_role_choices(form):
    """
    Populate the role_id SelectField with active roles.
    """
    roles = Role.query.filter_by(is_active=True).all()
    choices = [(0, "-- Select Role --")]
    for role in roles:
        display = getattr(role, "name", None)
        if not display:
            display = f"{getattr(role, 'name', '')}".strip()
        display = display or f"Role #{role.id}"
        choices.append((role.id, display))
    form.role.choices = choices

# ---------------------------------------------------------------------------
# Individual User Profile Information
# ---------------------------------------------------------------------------
@user_bp.route("/profile")
@login_required
def profile():
    """General Information tab."""
    form = ProfileForm(obj=current_user)
    return render_template(
        "user/profile.html",
        title="My Profile",
        active_tab="general",
        form=form)

@user_bp.route("/profile", methods=["POST"])
@login_required
def profile_update():
    """Handle General Information form submission."""
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        try:
            db.session.commit()
            flash("Profile updated successfully.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("That email address is already in use by another account.", "danger")
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Failed to update profile for user_id=%s", current_user.id)
            flash("Something went wrong while saving your profile. Please try again.", "danger")
        return redirect(url_for("user.profile"))

    return render_template(
        "user/profile.html",
        title="My Profile",
        active_tab="general",
        form=form)


# ---------------------------------------------------------------------------
# Individual Password Management
# ---------------------------------------------------------------------------
@user_bp.route("/profile/password", methods=["GET", "POST"])
@login_required
def profile_password():
    """
    Password Management tab.
    """
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Your current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            current_user.password_changed_at = utc_now()
            try:
                db.session.commit()
                logger.info("Password changed for user_id=%s", current_user.id)
                flash("Password changed successfully.", "success")
                return redirect(url_for("user.profile_password"))
            except SQLAlchemyError:
                db.session.rollback()
                logger.exception("Failed to change password for user_id=%s", current_user.id)
                flash("Something went wrong while changing your password. " \
                "Please try again.", "danger")

    return render_template(
        "user/profile_password.html",
        title="My Profile",
        active_tab="password",
        form=form)


# ---------------------------------------------------------------------------
# Individual 2FA Management
# ---------------------------------------------------------------------------
@user_bp.route("/profile/2fa")
@login_required
def profile_2fa():
    """
    2FA Management tab.
    """
    enable_form = Enable2FAForm()
    disable_form = Disable2FAForm()
    qr_code_b64 = ""

    if not current_user.is_2fa_enabled:
        if not current_user.totp_secret:
            current_user.generate_totp_secret()
            db.session.commit()
        uri = current_user.get_totp_uri(issuer="Pentan AMS")
        qr_code_b64 = generate_qr_b64(uri)

    return render_template(
        "user/profile_2fa.html",
        title="My Profile",
        active_tab="2fa",
        enable_form=enable_form,
        disable_form=disable_form,
        qr_code_b64=qr_code_b64)


@user_bp.route("/profile/2fa/enable", methods=["POST"])
@login_required
def profile_2fa_enable():
    """
    Confirm the TOTP code and turn 2FA on.
    """
    form = Enable2FAForm()

    if form.validate_on_submit():
        if current_user.verify_totp(form.totp_code.data):
            current_user.is_2fa_enabled = True
            try:
                db.session.commit()
                logger.info("2FA enabled for user_id=%s", current_user.id)
                flash("Two-factor authentication is now enabled.", "success")
            except SQLAlchemyError:
                db.session.rollback()
                logger.exception("Failed to enable 2FA for user_id=%s", current_user.id)
                flash("Something went wrong while enabling 2FA. Please try again.", "danger")
        else:
            flash("Invalid code. Please try again.", "danger")
    else:
        flash("Please enter the 6-digit code from your authenticator app.", "danger")

    return redirect(url_for("user.profile_2fa"))


@user_bp.route("/profile/2fa/disable", methods=["POST"])
@login_required
def profile_2fa_disable():
    """
    Turn 2FA off after confirming the user's password.
    """
    form = Disable2FAForm()

    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.is_2fa_enabled = False
            current_user.totp_secret = None
            try:
                db.session.commit()
                logger.info("2FA disabled for user_id=%s", current_user.id)
                flash("Two-factor authentication has been disabled.", "success")
            except SQLAlchemyError:
                db.session.rollback()
                logger.exception("Failed to disable 2FA for user_id=%s", current_user.id)
                flash("Something went wrong while disabling 2FA. Please try again.", "danger")
        else:
            flash("Incorrect password.", "danger")
    else:
        flash("Please confirm your password to disable 2FA.", "danger")

    return redirect(url_for("user.profile_2fa"))



# ---------------------------------------------------------------------------
# Multiple Users Account Management
# ---------------------------------------------------------------------------
@user_bp.route("/list", methods=["GET"])
@login_required
@permission_required("user:view")
def index():
    """
    View for listing users with search, sorting, and pagination.
    """
    page     = request.args.get("page", 1, type=int)
    search   = request.args.get("s", "", type=str).strip()
    sort     = request.args.get("sort", "", type=str)
    dir_     = request.args.get("dir", "asc", type=str)
    per_page = request.args.get("per_page", 25, type=int)
    if per_page not in (25, 35, 50):
        per_page = 25

    query = User.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(User.firstname.ilike(like),
                   User.lastname.ilike(like),
                   Role.name.ilike(like))
        )

    sort_map = {
        "firstname": User.firstname,
        "lastname": User.lastname,
    }
    sort_col = sort_map.get(sort, User.id)  # default order
    if dir_ == "desc":
        sort_col = sort_col.desc()

    paged = query.order_by(sort_col).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "user/list.html",
        users=paged,
        search=search,
        sort=sort,
        dir=dir_,
        per_page=per_page,
        title="Users",
    )


@user_bp.route("/details/<int:user_id>", methods=["GET"])
@login_required
@permission_required("user:view")
def details(user_id):
    """
    View the details of an existing user.
    """
    user = User.query.get_or_404(user_id)

    return render_template("user/details.html", user=user,
                           title=f"User Details: {user.fullname}")


@user_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required("user:create")
def create():
    """
    View for creating a new user.
    """
    form = AddUserForm()
    _populate_role_choices(form)

    if form.validate_on_submit():
        role = form.role.data

        existing = User.query.filter_by(email=form.email.data.strip(), role_id=role).first()
        if existing is not None:
            flash(f"User '{existing.name}' already exists.", "warning")
            return redirect(url_for("user.index"))

        user = User(
            firstname=form.firstname.data.strip(),
            lastname=form.lastname.data.strip(),
            email=form.email.data.strip(),
            phone=form.phone.data.strip(),
            role_id=role,
        )
        user.set_password(form.password.data.strip())
        db.session.add(user)

        try:
            db.session.commit()
            flash(f"User '{user.fullname}' created successfully.", "success")
            logger.info("User created: id=%s name=%s", user.id, user.fullname)
            return redirect(url_for("user.index"))
        except IntegrityError:
            db.session.rollback()
            flash("A User with that email already exists.", "danger")
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error creating user")
            flash("An error occurred while adding a user. Please try again.", "danger")

    return render_template("user/create.html", form=form,
                           title="Add New User")


@user_bp.route("/change_role/<int:user_id>", methods=["GET", "POST"])
@login_required
@permission_required("user:update")
def change_role(user_id):
    """
    View for changing a user's role.
    """
    user = User.query.get_or_404(user_id)
    form = ChangeUserRoleForm(obj=user)
    _populate_role_choices(form)

    if form.validate_on_submit():
        user.role_id = form.role.data

        try:
            db.session.commit()
            flash(f"User '{user.fullname}' role changed successfully.", "success")
            logger.info("User role changed: id=%s new_role_id=%s", user.id, user.role_id)
            return redirect(url_for("user.index"))
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error changing role for user id=%s", user_id)
            flash("An error occurred while changing the user's role. Please try again.", "danger")

    return render_template("user/change_role.html", form=form, user=user,
                           title=f"Change Role: {user.fullname}")


@user_bp.route("/delete/<int:user_id>", methods=["GET", "POST"])
@login_required
@permission_required("user:delete")
def delete(user_id):
    """
    View for deleting a user. Blocked if the user still has
    logs id linked to it.
    """
    user = User.query.get_or_404(user_id)

    log_count = len(user.auditlogs)
    has_dependencies = any([log_count])

    form = DeleteForm()

    if form.validate_on_submit():
        if has_dependencies:
            flash(
                f"Cannot delete '{user.name}': he/she still has "
                f"{log_count} log(s), "
                f"linked to them.",
            )
            return redirect(url_for("user.delete", user_id=user_id))

        try:
            db.session.delete(user)
            db.session.commit()
            flash(f"User '{user.name}' deleted successfully.", "success")
            logger.info("User deleted: id=%s", user_id)
            return redirect(url_for("user.index"))
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error deleting user id=%s", user_id)
            flash("An error occurred while deleting the user. Please try again.", "danger")

    return render_template(
        "user/delete.html",
        form=form,
        user=user,
        log_count=log_count,
        has_dependencies=has_dependencies,
        title=f"Delete User: {user.fullname}"
    )


# End of file: app/routes/user.py
