"""
app/forms/workspace.py - Forms for role management.
"""

from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired
from app.forms.base import BaseForm


class CreateWorkspaceForm(BaseForm):
    """
    Form for creating a new workspace.
    """
    name = StringField("Workspace Name", validators=[DataRequired(message="Workspace name is required")],
                       render_kw={"placeholder": "Workspace name", "class": "form-control"})
    description = TextAreaField("Description",
                                render_kw={"placeholder": "Enter workspace description", "class": "form-control", "rows": 3})
    is_shared = BooleanField("Is Shared?")
    submit = SubmitField("Create", render_kw={"class": "btn btn-success"})
    

class UpdateWorkspaceForm(CreateWorkspaceForm):
    """
    Form for updating an existing workspace.
    """
    is_active = BooleanField("Is Active?")
    submit = SubmitField("Update", render_kw={"class": "btn btn-primary"})


# End of file
