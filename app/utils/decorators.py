"""
app/utils/decorators.py - Custom decorators for route protection and logging
"""

import functools
from functools import wraps
from flask import abort, g
from flask_login import current_user
# from sqlalchemy.exc import SQLAlchemyError

from app.models import Workspace, WorkspaceMember
# from app.services.workspace import get_workspace_access
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


def role_required(*role_names: str):
    """
    Restrict access to users who have at least one of the given roles.
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

            # Role check (any-of) — has_role already handles multiple names
            if not current_user.has_role(*role_names):
                abort(
                    403,
                    description=f"Missing required role: one of {', '.join(role_names)}"
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def workspace_access_required(f):
    @wraps(f)
    def wrapper(workspace_id, *args, **kwargs):
        workspace = Workspace.query.get_or_404(workspace_id)
        is_owner = workspace.owner_id == current_user.id
        is_member = WorkspaceMember.query.filter_by(
            workspace_id=workspace_id, user_id=current_user.id
        ).first() is not None
        if not (is_owner or is_member):
            abort(403)
        g.current_workspace = workspace
        return f(workspace_id=workspace_id, *args, **kwargs)
    return wrapper

# End of file
