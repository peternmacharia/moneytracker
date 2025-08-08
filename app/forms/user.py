"""
User form defination file
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo
from app.forms.shared import BaseForm


class UserForm(BaseForm):
    """
    User Registration form defination
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
    confirm_password = StringField("Confirm Password",
                                   validators=[DataRequired(),
                                               EqualTo('new_password',
                                                       message='Passwords must match')],
                                   render_kw={"placeholder":"Confirm Password",
                                              "type":"password", "class":"form-control",
                                              "required":"required"})


class UserDetailsForm(FlaskForm):
    """
    User Details form defination
    """
    firstname = StringField("First Name", render_kw={"placeholder":"First Name",
                                                     "class":"form-control fw-bold",
                                                     "readonly":"readonly", "disabled":"True"})
    lastname = StringField("Last Name", render_kw={"placeholder":"Last Name",
                                                   "class":"form-control fw-bold",
                                                   "readonly":"readonly", "disabled":"True"})
    username = StringField("Username", render_kw={"placeholder":"Username",
                                                  "class":"form-control fw-bold",
                                                  "readonly":"readonly", "disabled":"True"})
    phone = StringField("Phone Number", render_kw={"placeholder":"Phone Number",
                                                   "class":"form-control fw-bold",
                                                   "readonly":"readonly", "disabled":"True"})
    email = StringField("Email Address", render_kw={"placeholder":"Email",
                                                    "class":"form-control fw-bold",
                                                    "readonly":"readonly", "disabled":"True"})
    role = SelectField("Role", coerce=str,
                       render_kw={"placeholder":"Role",
                                  "class":"form-control fw-bold",
                                  "readonly":"readonly", "disabled":"True"})
    is_2fa_enabled  = BooleanField("Enable 2FA?", render_kw={"placeholder":"Enable 2FA?",
                                                             "type":"checkbox",
                                                             "class":"form-check-input"})


class UserUpdateForm(BaseForm):
    """
    User Update form defination
    """
    firstname = StringField("First Name", validators=[DataRequired(), Length(max=20)],
                            render_kw={"placeholder":"First Name",
                                      "class":"form-control",
                                      "required":"required"})
    lastname = StringField("Last Name", validators=[DataRequired(), Length(max=20)],
                            render_kw={"placeholder":"Last Name",
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


# End of file
