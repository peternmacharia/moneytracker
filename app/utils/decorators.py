"""
app/utils/decorators.py - Custom decorators for route protection and logging
"""

import functools
from functools import wraps
from flask import abort
from flask_login import current_user
# from sqlalchemy.exc import SQLAlchemyError

# from app.extensions import db
from app.models.auditlog import AuditLog
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


# def audit_action(
#     action: AuditAction | str,
#     resource_type: str | None = None,
#     # Dynamic callables — receive (return_value, *args, **kwargs)
#     get_resource_id=None,
#     get_old_value=None,
#     get_new_value=None,
#     get_details=None,
#     # Static fallbacks used when the corresponding callable is not provided
#     resource_id: str | None = None,
#     old_value:   dict | None = None,
#     new_value:   dict | None = None,
#     details:     dict | None = None,
#     # Actor override (rarely needed — auto-resolved from Flask-Login)
#     actor_type: ActorType | str | None = None,
#     ):
#     """
#     Decorator that writes an AuditLog entry after the view function returns.
#     Prefer inline AuditLog.log() calls in views for precision; use this
#     decorator for routes where a simple entry is sufficient.

#     Resource id is read from the 'election_id', 'voter_id', or 'id' URL kwarg.
#     """
#     def decorator(fn):
#         @functools.wraps(fn)
#         def wrapper(*args, **kwargs):
#             result = fn(*args, **kwargs)
#             # --- Resolve all dynamic fields from the function result + args ---
#             resolved_resource_id = (
#                 get_resource_id(result, *args, **kwargs)
#                 if callable(get_resource_id) else resource_id
#             )
#             resolved_old_value = (
#                 get_old_value(result, *args, **kwargs)
#                 if callable(get_old_value) else old_value
#             )
#             resolved_new_value = (
#                 get_new_value(result, *args, **kwargs)
#                 if callable(get_new_value) else new_value
#             )
#             resolved_details = (
#                 get_details(result, *args, **kwargs)
#                 if callable(get_details) else details
#             )

#             AuditLog.log(
#                 action        = action,
#                 resource_type = resource_type,
#                 resource_id   = resolved_resource_id,
#                 old_value     = resolved_old_value,
#                 new_value     = resolved_new_value,
#                 details       = resolved_details,
#                 actor_type    = actor_type,
#             )

#             return result
#         return wrapper
#     return decorator

# End of file
