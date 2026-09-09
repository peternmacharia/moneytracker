# app/forms/base.py
"""
app/forms/base.py - Defines the BaseForm class, which is the parent class for all forms
                    in the application.
"""

from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask import flash


class BaseForm(FlaskForm):
    """
    Base form class shared by all application forms.
 
    Provides:
      - Automatic '*' suffix on labels for DataRequired fields
      - add_error()            — attach an error to a named field
      - add_form_error()       — attach a non-field form-level error
      - get_field_errors()     — get errors for a specific field
      - has_errors()           — check if form has any errors
      - get_all_errors()       — get all errors as a flat list
      - flash_errors()         — flash all form errors
      - populate_from_object() — populate form from model instance
      - update_object()        — update model instance from form data
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mark_required_fields()

    def _mark_required_fields(self):
        """
        Automatically add '*' suffix to labels of fields with DataRequired validator.
        """
        for field in self:
            if hasattr(field, "validators"):
                for validator in field.validators:
                    if isinstance(validator, DataRequired):
                        if not field.label.text.endswith(" *"):
                            field.label.text += " *"
                        break

    def add_error(self, field_name: str, message: str) -> "BaseForm":
        """
        Attach an error message to a specific field.
        
        Args:
            field_name: Name of the field to add error to
            message: Error message to display
        
        Returns:
            self (for method chaining)
        """
        field = getattr(self, field_name, None)
        if field:
            field.errors.append(message)
        else:
            # If field doesn't exist, add as form error
            self.add_form_error(f"Field '{field_name}': {message}")
        return self

    def add_form_error(self, message: str) -> "BaseForm":
        """
        Attach a form-level error not tied to any field.
        
        Args:
            message: Error message to display
        
        Returns:
            self (for method chaining)
        """
        self.errors.setdefault("_form", []).append(message)
        return self

    def get_field_errors(self, field_name: str) -> list:
        """
        Get all errors for a specific field.
        
        Args:
            field_name: Name of the field to get errors for
        
        Returns:
            List of error messages for the field
        """
        field = getattr(self, field_name, None)
        if field and field.errors:
            return field.errors
        return []

    def has_errors(self) -> bool:
        """
        Check if the form has any errors (field or form-level).
        
        Returns:
            True if form has errors, False otherwise
        """
        if self.errors:
            return True

        # Check field errors
        for field in self:
            if field.errors:
                return True

        return False

    def get_all_errors(self) -> dict:
        """
        Get all errors (field and form-level) as a dictionary.
        
        Returns:
            Dictionary with field names as keys and error messages as values
        """
        all_errors = {}

        # Add field errors
        for field_name, field in self._fields.items():
            if field.errors:
                all_errors[field_name] = field.errors

        # Add form errors
        if "_form" in self.errors:
            all_errors["_form"] = self.errors["_form"]

        return all_errors

    def get_flat_errors(self) -> list:
        """
        Get all errors as a flat list of strings.
        
        Returns:
            List of all error messages
        """
        errors = []

        # Add field errors
        for field_name, field in self._fields.items():
            if field.errors:
                for error in field.errors:
                    errors.append(f"{field.label.text}: {error}")

        # Add form errors
        if "_form" in self.errors:
            for error in self.errors["_form"]:
                errors.append(error)

        return errors

    def flash_errors(self, category: str = "danger") -> None:
        """
        Flash all form errors using Flask's flash function.
        
        Args:
            category: Flash message category (default: "danger")
        """
        for error in self.get_flat_errors():
            flash(error, category)

    def populate_from_object(self, obj, fields: list = None) -> "BaseForm":
        """
        Populate form fields from a model object.
        
        Args:
            obj: Model object with attribute data
            fields: Optional list of field names to populate (populates all if None)
        
        Returns:
            self (for method chaining)
        """
        if fields is None:
            fields = [field.name for field in self]

        for field_name in fields:
            if hasattr(self, field_name) and hasattr(obj, field_name):
                field = getattr(self, field_name)
                value = getattr(obj, field_name)
                field.data = value

        return self

    def update_object(self, obj, fields: list = None) -> "BaseForm":
        """
        Update a model object with form data.
        
        Args:
            obj: Model object to update
            fields: Optional list of field names to update (updates all if None)
        
        Returns:
            self (for method chaining)
        """
        if fields is None:
            fields = [field.name for field in self if field.name != 'csrf_token']

        for field_name in fields:
            if hasattr(self, field_name) and hasattr(obj, field_name):
                field = getattr(self, field_name)
                if field.data is not None:
                    setattr(obj, field_name, field.data)

        return self

    def validate_on_submit_with_errors(self) -> bool:
        """
        Validate form on submit and flash errors if validation fails.
        
        Returns:
            True if form is valid, False otherwise
        """
        if self.validate_on_submit():
            return True
        else:
            self.flash_errors()
            return False


class ModelForm(BaseForm):
    """
    Extended BaseForm for model-specific forms with additional functionality.
    
    Provides:
      - Automatic model relationship handling
      - Query-based choices for select fields
      - Form-specific model operations
    """

    def __init__(self, *args, **kwargs):
        self._obj = kwargs.pop('obj', None)
        super().__init__(*args, **kwargs)

        # If obj is provided, populate form from it
        if self._obj:
            self.populate_from_object(self._obj)

    def save(self, commit: bool = True) -> object:
        """
        Save the form data to the model instance.
        Must be implemented by child classes.
        
        Args:
            commit: Whether to commit the transaction
        
        Returns:
            The saved model instance
        """
        raise NotImplementedError("Subclasses must implement save() method")

    def delete(self, commit: bool = True) -> bool:
        """
        Delete the associated model instance.
        Must be implemented by child classes.
        
        Args:
            commit: Whether to commit the transaction
        
        Returns:
            True if deletion was successful
        """
        raise NotImplementedError("Subclasses must implement delete() method")


# End of file
