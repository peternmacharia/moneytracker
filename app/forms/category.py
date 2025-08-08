"""
Category form defination file
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length
from app.forms.shared import BaseForm


class CatgoryForm(BaseForm):
    """
    Category form defination
    """
    name = StringField("First Name", validators=[DataRequired(), Length(max=50)],
                            render_kw={"placeholder":"First Name",
                                      "class":"form-control",
                                      "required":"required"})
    color = StringField("Color", validators=[Length(max=7)],
                            render_kw={"placeholder":"Color",
                                      "class":"form-control"})
    icon = StringField("Icon", validators=[Length(max=20)],
                           render_kw={"placeholder":"Icon",
                                      "class":"form-control"})

# End of file
