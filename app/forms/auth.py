"""
app/forms/auth.py - Defines form classes related to authentication and user management,
                    such as login, password reset, and 2FA management.
"""

# from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import (StringField, PasswordField, EmailField, SelectField, SubmitField)
from wtforms.validators import DataRequired, Email, Length, EqualTo
from .base import BaseForm
from app.utils.geo import COUNTRIES, CURRENCIES, TIMEZONES

PLACEHOLDER = "-- Select --"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


class LoginForm(BaseForm):
    """
    Login form for system users.
    """
    email = EmailField("Email", validators=[DataRequired(message="Email is required."), Email()],
                       render_kw={"placeholder": "Email", "class": "form-control", "autocomplete": "email"})
    password = PasswordField("Password", validators=[DataRequired(message="Password is required.")],
                             render_kw={"placeholder": "Password", "class": "form-control"})
    submit = SubmitField("Sign in", render_kw={"class": "btn btn-success w-100"})


class SignupForm(BaseForm):
    """
    Signup form for new users.
    """
    firstname = StringField("First Name", validators=[DataRequired(message="First name is required.")],
                            render_kw={"placeholder": "First Name", "class": "form-control"})
    lastname = StringField("Last Name", validators=[DataRequired(message="Last name is required.")],
                           render_kw={"placeholder": "Last Name", "class": "form-control"})
    email = EmailField("Email", validators=[DataRequired(message="Email is required."), Email()],
                       render_kw={"placeholder": "Email", "class": "form-control"})
    country = SelectField("Country", choices=[("", PLACEHOLDER)] + COUNTRIES,
                          validators=[DataRequired(message="Country is required.")],
                          render_kw={"placeholder": "Country", "class": "form-select"})
    currency = SelectField("Currency", choices=[("", PLACEHOLDER)] + CURRENCIES,
                           validators=[DataRequired(message="Currency is required.")],
                           render_kw={"placeholder": "Currency", "class": "form-select"})
    timezone = SelectField("Timezone", choices=[("", PLACEHOLDER)] + TIMEZONES,
                           validators=[DataRequired(message="Timezone is required.")],
                           render_kw={"placeholder": "Timezone", "class": "form-select"})
    avatar = FileField("Choose Avatar", validators=[FileAllowed([ext.lstrip(".") for ext in IMAGE_EXTENSIONS],
                                                                "That file type isn't allowed.",),
                                            FileSize(max_size=5 * 1024 * 1024, message="File must be under 5MB."),],
                        render_kw={"type":"file", "class":"form-control", "accept":",".join(IMAGE_EXTENSIONS)})
    submit = SubmitField("Sign up", render_kw={"class": "btn btn-success w-100"})


class SetPasswordForm(BaseForm):
    """
    Set a new password for the user, typically used after email verification or password reset.
    """
    password = PasswordField("New Password", validators=[DataRequired(message="New password is required."),
                                                         Length(min=8, message="Password must be at least 8 characters.")],
                             render_kw={"placeholder": "New password", "class": "form-control"})
    confirm_password = PasswordField("Confirm New Password",
                                     validators=[DataRequired(message="Please confirm your new password."),
                                                 EqualTo("password", message="Passwords must match.")],
                                     render_kw={"placeholder": "Repeat password", "class": "form-control"})
    submit = SubmitField("Set Password", render_kw={"class":"btn btn-success w-100"})



class TwoFactorForm(BaseForm):
    """
    Second-factor form for TOTP-based 2FA.
    """
    token = StringField("Authentication Code", validators=[DataRequired(message="Authentication code is required."),
                                                           Length(min=6, max=6, message="Enter the 6-digit code.")],
                        render_kw={"placeholder":"Authentication Code", "class":"form-control"})
    submit = SubmitField("Verify", render_kw={"class":"btn btn-success w-100"})


class ResendVerificationForm(BaseForm):
    """
    Request a new email verification link, if the original link is expired
    """
    email = EmailField("Email", validators=[DataRequired(message="Email is required."), Email()],
                       render_kw={"placeholder":"Email", "class":"form-control"})
    submit = SubmitField("Resend Verification Email", render_kw={"class":"btn btn-primary w-100"})


class RequestResetForm(BaseForm):
    """
    Request a password reset email
    """
    email = EmailField("Email", validators=[DataRequired(message="Email is required."), Email()],
                       render_kw={"placeholder":"Email", "class":"form-control"})
    submit = SubmitField("Send Reset Link", render_kw={"class":"btn btn-primary w-100"})


class ResetPasswordForm(BaseForm):
    """
    Set a new password using a reset token.
    """
    password = PasswordField("New Password", validators=[DataRequired(message="New password is required."),
                                                         Length(min=8, message="Password must be at least 8 characters.")],
                             render_kw={"placeholder": "New password", "class": "form-control"})
    confirm_password = PasswordField("Confirm New Password",
                                     validators=[DataRequired(message="Please confirm your new password."),
                                                 EqualTo("password", message="Passwords must match.")],
                                     render_kw={"placeholder": "Repeat password", "class": "form-control"})
    submit = SubmitField("Reset Password", render_kw={"class":"btn btn-primary w-100"})


class ChangePasswordForm(BaseForm):
    """
    Used by an authenticated user to change their own password - required
    on first login after an admin creates their account (detected via
    User.password_changed_at being unset), and usable any time afterward
    from account settings.
    """
    current_password = PasswordField("Current Password", validators=[DataRequired(message="Current password is required.")],
                                     render_kw={"placeholder":"Current Password", "class":"form-control"})
    new_password = PasswordField("New Password",validators=[DataRequired(message="New password is required."),
                                                            Length(min=8, message="Password must be at least 8 characters.")],
                                 render_kw={"placeholder": "New password", "class": "form-control"})
    confirm_new_password = PasswordField("Confirm New Password", validators=[DataRequired(message="Please confirm your new password."),
                                                                             EqualTo("new_password", message="Passwords must match.")],
                                         render_kw={"placeholder": "Repeat password", "class": "form-control"})
    submit = SubmitField("Reset Password", render_kw={"class":"btn btn-primary w-100"})


# End of file
