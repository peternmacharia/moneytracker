"""
app/forms/permission.py - Forms for permission management.
"""

from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from app.forms.base import BaseForm


class CreatePermissionForm(BaseForm):
    """
    Form for creating a new permission.
    """
    resource = SelectField('Resource Name', validators=[DataRequired(message="Resource Name is required.")],
                           render_kw={"placeholder": "Resource Name", "class": "form-select"})
    action = StringField("Action", validators=[DataRequired(message="Action is required.")],
                         render_kw={"placeholder": "Enter action", "class": "form-control"})
    submit = SubmitField("Create", render_kw={"class": "btn btn-success"})


class UpdatePermissionForm(CreatePermissionForm):
    """
    Form for updating an existing permission.
    """
    submit = SubmitField("Update", render_kw={"class": "btn btn-primary"})


# End of file
