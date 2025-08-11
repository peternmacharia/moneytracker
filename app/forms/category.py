"""
Category form defination file
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
from app.forms.shared import BaseForm


class CatgoryForm(BaseForm):
    """
    Category form defination
    """
    name = StringField("Category Name", validators=[DataRequired(), Length(max=50)],
                       render_kw={"placeholder":"Category Name",
                                  "class":"form-control",
                                  "required":"required"})
    description = TextAreaField("Description",
                                render_kw={"placeholder":"Description",
                                           "class":"form-control"})
    icon = StringField("Icon", validators=[Length(max=20)],
                       render_kw={"placeholder":"Icon",
                                  "class":"form-control"})

class CatgoryDetailsForm(FlaskForm):
    """
    Category Details form defination
    """
    name = StringField("Category Name",
                       render_kw={"placeholder":"First Name",
                                  "class":"form-control fw-bold",
                                  "readonly":"readonly", "disabled":"True"})
    description = TextAreaField("Description",
                                render_kw={"placeholder":"First Name",
                                           "class":"form-control fw-bold",
                                           "readonly":"readonly", "disabled":"True"})
    icon = StringField("Icon", render_kw={"placeholder":"First Name",
                                          "class":"form-control fw-bold",
                                          "readonly":"readonly", "disabled":"True"})

# End of file
