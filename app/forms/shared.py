"""
app/forms/shared.py - Shared form components and utilities for the application.
"""

from wtforms import SubmitField, BooleanField
from wtforms.validators import DataRequired
from app.forms.base import BaseForm


class ConfirmForm(BaseForm):
    """
    Form for confirming resource item modification or action to be taken.
    """
    confirm = BooleanField("I confirm and understand this action is irreversible!",
                           validators=[DataRequired(message="Please confirm the action")],)
    submit = SubmitField("Confirm", render_kw={"class": "btn btn-outline-success"})


class DeleteForm(BaseForm):
    """
    Form for confirming resource item deletion.
    """
    confirm = BooleanField("I understand this action is irreversible",
                           validators=[DataRequired(message="Please confirm the deletion")],)
    submit = SubmitField("Delete", render_kw={"class": "btn btn-outline-danger"})


# End of file
