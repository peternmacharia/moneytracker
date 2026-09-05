"""
app/utils/decorators.py - Custom decorators for route protection and logging
"""

import functools
from functools import wraps
from flask import abort
from flask_login import current_user
# from sqlalchemy.exc import SQLAlchemyError

# from app.extensions import db
# from app.models.enums import ActorType, AuditAction


def permission_required(permission_name: str):
    """
    Restrict access to users with a specific permission.
    Works with Flask-Login (session-based auth).
    """

    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            # Ensure user is authenticated
            if not current_user.is_authenticated:
                abort(401, description="Authentication required")

            # Ensure user has role
            if not current_user.role:
                abort(403, description="No role assigned")

            # Permission check
            if not current_user.has_permission(permission_name):
                abort(
                    403,
                    description=f"Missing permission: {permission_name}"
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator

# End of file
