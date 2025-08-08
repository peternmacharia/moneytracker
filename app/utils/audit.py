"""
Audit logging utilities for tracking user actions across the application
"""

import json
import uuid
from datetime import datetime
from functools import wraps
from contextlib import contextmanager
import sqlalchemy.exc
from flask import g, request, current_app
from app.extensions import db
from app.models.auditlog import Auditlog  # Adjust import based on your model location

def log_audit(action, resource_type=None, resource_id=None, description=None, details=None):
    """
    Log an audit event both to file and database
    """
    try:
        # Get user ID if available, otherwise use 'anonymous'
        user_id = 'anonymous'
        if hasattr(g, 'user') and g.user:
            user_id = g.user.id

        # Get request ID or generate a new one
        request_id = getattr(g, 'request_id', str(uuid.uuid4()))

        # Create log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'request_id': request_id,
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'description': description,
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.user_agent.string if request and request.user_agent else None,
            'details': json.dumps(details) if details else None
        }

        # Log to audit log file
        try:
            current_app.audit_logger.info(json.dumps(log_entry))
        except (AttributeError, TypeError) as logger_error:
            current_app.logger.error(f'Failed to write to audit log file: {str(logger_error)}')

        # Store in database
        try:
            audit_record = Auditlog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
                ip_address=log_entry['ip_address'],
                user_agent=log_entry['user_agent'],
                request_id=log_entry['request_id'],
                details=log_entry['details']
            )
            db.session.add(audit_record)
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as db_error:
            current_app.logger.error(f'Failed to write audit record to database: {str(db_error)}')
            # Rollback the session to avoid transaction issues
            db.session.rollback()

    except (AttributeError, TypeError, ValueError) as e:
        # These are the most likely errors when accessing attributes or formatting data
        current_app.logger.error(f'Error preparing audit log data: {str(e)}')


def audit_trail(action, resource_type=None):
    """
    A decorator function for audit logging
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resource_id = kwargs.get('id', None)
            try:
                # Call the route function
                response = f(*args, **kwargs)

                # Log successful action
                log_audit(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    description=f"Successfully performed {action}",
                    details={"status": "success", "resource_id": resource_id}
                )

                return response

            except (sqlalchemy.exc.SQLAlchemyError, ValueError, TypeError) as e:
                # Handle database and data validation errors
                log_audit(
                    action=f"{action}_failed",
                    resource_type=resource_type,
                    resource_id=resource_id,
                    description=f"Failed to perform {action}: {str(e)}",
                    details={"status": "error",
                             "message": str(e),
                             "error_type": e.__class__.__name__}
                )
                # Re-raise the exception
                raise
            except Exception as e:
                # Handle other unexpected errors
                current_app.logger.error(f"Unexpected error in {action}: {str(e)}", exc_info=True)
                log_audit(
                    action=f"{action}_failed",
                    resource_type=resource_type,
                    resource_id=resource_id,
                    description=f"Failed to perform {action} due to unexpected error",
                    details={"status": "error",
                             "message": str(e),
                             "error_type": e.__class__.__name__}
                )
                # Re-raise the exception
                raise

        return decorated_function
    return decorator


@contextmanager
def audit_context(action, resource_type=None, resource_id=None, description=None):
    """
    Context manager for audit logging
    """
    try:
        # Yield control back to the calling code
        yield

        # If no exception was raised, log success
        log_audit(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description or f"Successfully performed {action}",
            details={"status": "success"}
        )

    except Exception as e:
        # Log failure and re-raise
        log_audit(
            action=f"{action}_failed",
            resource_type=resource_type,
            resource_id=resource_id,
            description=f"Failed to perform {action}: {str(e)}",
            details={"status": "error", "message": str(e)}
        )
        raise


def log_bulk_audit(action, resource_type, resource_ids, description=None, details=None):
    """
    Log a bulk operation to the audit trail
    """
    log_audit(
        action=action,
        resource_type=resource_type,
        resource_id=",".join(str(id) for id in resource_ids),
        description=description or f"Bulk {action} on {len(resource_ids)} {resource_type} items",
        details={"resource_ids": resource_ids, **(details or {})}
    )

# End of file
