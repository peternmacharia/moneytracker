"""
Transaction form defination file
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length
from app.models.transaction import TType
from app.forms.shared import BaseForm


class TransactionForm(BaseForm):
    """
    Transaction form defination
    """
    category = SelectField("Category", coerce=str, validators=[DataRequired()],
                           render_kw={"placeholder":"Category",
                                      "class":"form-control form-select",
                                      "required":"required"})
    amount = FloatField("Amount", validators=[DataRequired()],
                        render_kw={"placeholder":"Amount",
                                   "type":"number", "class":"form-control",
                                   "required":"required"})
    description = TextAreaField("Description", validators=[DataRequired()],
                                render_kw={"placeholder": "Description",
                                           "type":"text",
                                           "class": "form-control",
                                           "required":"required"})
    transaction_type = SelectField("Transaction Type", validators=[DataRequired()],
                                   choices=[(method.name, method.value) for method in TType],
                                   render_kw={"placeholder":"Transaction Type",
                                              "class":"form-control form-select",
                                              "required":"required"})

# End of file
