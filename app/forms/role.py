"""
app/forms/role.py - Forms for role management.
"""

from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired
from app.forms.base import BaseForm


class CreateRoleForm(BaseForm):
    """
    Form for creating a new role.
    """
    name = StringField("Role Name", validators=[DataRequired(message="Role name is required")],
                       render_kw={"class": "form-control"})
    description = TextAreaField("Description",
                                render_kw={"placeholder": "Enter role description", "class": "form-control", "rows": 3})
    permissions = SelectMultipleField('Permissions',
                                      validators=[DataRequired(message="Please select at least one permission")],
                                      choices=[],
                                      coerce=str,
                                      render_kw={"placeholder": "Select permissions"})
    submit = SubmitField("Create", render_kw={"class": "btn btn-success"})


class UpdateRoleForm(CreateRoleForm):
    """
    Form for updating an existing role.
    """
    is_active = BooleanField("Is Active?")
    submit = SubmitField("Update", render_kw={"class": "btn btn-primary"})


# End of file
