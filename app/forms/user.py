"""
app/forms/user.py - Forms for user management (create, update).
"""

from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import (DataRequired, Email, Length, Regexp, EqualTo)
from app.forms.base import BaseForm


# ------------------------------------------------------------------
# Individual user self account management
# ------------------------------------------------------------------
class ProfileForm(BaseForm):
    """
    Form for updating user profile information.
    """
    firstname = StringField("First Name", validators=[DataRequired(message="First name is required.")],
                            render_kw={"placeholder": "First Name", "class": "form-control"})
    lastname = StringField("Last Name", validators=[DataRequired(message="Last name is required.")],
                            render_kw={"placeholder": "Last Name", "class": "form-control"})
    email = EmailField("Email", validators=[DataRequired(message="Email is required."), Email()],
                        render_kw={"placeholder": "Email", "class": "form-control"})
    submit = SubmitField("Save Changes", render_kw={"class": "btn btn-success"})


class Enable2FAForm(BaseForm):
    """
    Form for enabling two-factor authentication.
    """
    totp_code = StringField("Authenticator Code", validators=[DataRequired(message="TOTP code is required."),
                                                              Length(min=6, max=6), Regexp(r"^\d{6}$", message="Enter the 6-digit code.")],
                            render_kw={"placeholder": "000000", "class": "form-control", "maxlength": "6"})
    submit = SubmitField("Enable 2FA", render_kw={"class":"btn btn-success"})


class Disable2FAForm(BaseForm):
    """
    Form for disabling two-factor authentication.
    """
    current_password = PasswordField("Current Password", validators=[DataRequired(message="Current password is required.")],
                                     render_kw={"placeholder": "Current Password", "class": "form-control"})
    submit = SubmitField("Disable 2FA", render_kw={"class":"btn btn-outline-danger"})


# End of file
