"""
This file contains utility decorators for the applications.
"""

from functools import wraps
from flask import abort, request, current_app as app
from flask_login import current_user, login_required

def require_role(role):
    """
    Decorator to check if current user has required role
    
    Args:
        role_name: Name of the required role
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            if not current_user.is_active:
                abort(403)

            if not current_user.has_role(role):
                app.logger.warning(
                    f"User {current_user.username} denied access to {request.endpoint} "
                    f"- missing role: {role}"
                )
                abort(403)

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def admin_required(f):
    """Shortcut decorator for admin-only access"""
    return require_role('admin')(f)

def check_role(role_name, user=None):
    """Programmatically check role"""
    user = user or current_user
    if not user.is_authenticated:
        return False
    return user.has_role(role_name)

# End of file
