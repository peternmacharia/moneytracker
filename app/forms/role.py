"""
Role form defination file
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length
from app.forms.shared import BaseForm

class RoleForm(BaseForm):
    """
    Role form defination
    """
    name = StringField("Role", validators=[DataRequired(), Length(max=10)],
                       render_kw={"placeholder":"Role",
                                  "class":"form-control",
                                  "required":"required"})


class RoleDetailsForm(FlaskForm):
    """
    Role Details form defination
    """
    name = StringField("Role", render_kw={"placeholder":"First Name",
                                          "class":"form-control fw-bold",
                                          "readonly":"readonly", "disabled":"True"})

# End of file
