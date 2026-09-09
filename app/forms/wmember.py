"""
app/forms/wmember.py - Forms for workspace member management.
"""

from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email
from app.forms.base import BaseForm


class CreateWMemberForm(BaseForm):
    """
    Form for creating a new workspace member.
    """
    workspace = SelectField("Workspace", coerce=str, validators=[DataRequired(message="Workspace is required")],
                       render_kw={"placeholder":"Select Workspace", "class": "form-select"})
    member_email = StringField("New Member Email", validators=[DataRequired(message="Email is required."), Email()],
                        render_kw={"placeholder": "New Member Email", "class": "form-control"})
    role = SelectField("Role", coerce=str, validators=[DataRequired(message="Role is required")],
                       render_kw={"placeholder":"Select Role", "class": "form-select"})
    submit = SubmitField("Create", render_kw={"class": "btn btn-success"})


class UpdateWMemberForm(CreateWMemberForm):
    """
    Form for updating an existing workspace member.
    """
    submit = SubmitField("Update", render_kw={"class": "btn btn-primary"})


# End of file
