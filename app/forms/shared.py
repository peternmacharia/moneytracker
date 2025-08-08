"""
Base form defination file to be shared with all system forms
"""

from flask_wtf import FlaskForm

class BaseForm(FlaskForm):
    """
    Base form with enhanced label rendering for required fields
    """
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        # Add required markers to all required fields
        for field in self:
            if hasattr(field, 'validators'):
                for validator in field.validators:
                    if validator.__class__.__name__ == 'DataRequired':
                        field.label.text = field.label.text + ' *'
                        break

# End of file
