"""
Login and New User registration forms
"""

from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo
from app.forms.shared import BaseForm
from app.models.user import UserStatus


class LoginForm(BaseForm):
    """
    User Login form defination
    """
    email = StringField("Email Address", validators=[DataRequired(), Length(max=100)],
                        render_kw={"placeholder":"Email",
                                   "type":"email", "class":"form-control",
                                   "required":"required"})
    password = StringField("Password", validators=[DataRequired()],
                           render_kw={"placeholder":"Password",
                                      "type":"password", "class":"form-control",
                                      "required":"required"})


class AdminRegistrationForm(BaseForm):
    """
    Admin Registration form defination
    """
    firstname = StringField("First Name", validators=[DataRequired(), Length(max=20)],
                            render_kw={"placeholder":"First Name",
                                      "class":"form-control",
                                      "required":"required"})
    lastname = StringField("Last Name", validators=[DataRequired(), Length(max=20)],
                            render_kw={"placeholder":"Last Name",
                                      "class":"form-control",
                                      "required":"required"})
    username = StringField("Username", validators=[DataRequired(), Length(max=20)],
                           render_kw={"placeholder":"Username",
                                      "class":"form-control",
                                      "required":"required"})
    phone = StringField("Phone Number", validators=[DataRequired(), Length(max=20)],
                        render_kw={"placeholder":"Phone Number",
                                   "type":"tel", "class":"form-control",
                                   "required":"required"})
    email = StringField("Email Address", validators=[DataRequired(), Length(max=100)],
                        render_kw={"placeholder":"Email",
                                   "type":"email", "class":"form-control",
                                   "required":"required"})
    password = StringField("Password", validators=[DataRequired()],
                           render_kw={"placeholder":"Password",
                                      "type":"password", "class":"form-control",
                                      "required":"required"})
    role = SelectField("Role", coerce=str, validators=[DataRequired()],
                       render_kw={"placeholder":"Department",
                                  "class":"form-control form-select",
                                  "required":"required"})
    status = SelectField("User Status",
                         choices=[(model.name, model.value) for model in UserStatus],
                         render_kw={"placeholder":"Status",
                                    "class":"form-control fw-bold",
                                    "readonly":"readonly", "disabled":"True"})


class TwoFactorForm(BaseForm):
    """
    Two Factor Authentication form defination
    """
    verification_code = StringField("Verification Code",
                                    validators=[DataRequired(), Length(max=32)],
                                    render_kw={"placeholder":"Verification Code",
                                               "class":"form-control",
                                               "required":"required"})


class ChangePasswordForm(BaseForm):
    """
    User Change password form defination
    """
    new_password = StringField("New Password", validators=[DataRequired()],
                               render_kw={"placeholder":"New Password",
                                          "type":"password", "class":"form-control",
                                          "required":"required"})
    confirm_password = StringField("Confirm Password",
                                   validators=[DataRequired(),
                                               EqualTo('new_password',
                                                       message='Passwords must match')],
                                   render_kw={"placeholder":"Confirm Password",
                                              "type":"password", "class":"form-control",
                                              "required":"required"})

# End of file
