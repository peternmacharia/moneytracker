"""
Role form defination file
"""

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

# End of file
