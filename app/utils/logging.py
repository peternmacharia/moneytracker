"""
Logging configuration utilities
"""

import os
import time
import uuid
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask import g, request

def setup_logger(app):
    """
    A function to configure app logger
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(app.config['LOG_DIR']):
        os.makedirs(app.config['LOG_DIR'])

    # Application logger
    app_logger = logging.getLogger('app')
    app_logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    app_logger.propagate = False

    # Clear existing handlers to avoid duplicates during reloads
    if app_logger.handlers:
        app_logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(app.config['LOG_FORMAT'])

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        os.path.join(app.config['LOG_DIR'], 'app.log'),
        maxBytes=app.config['LOG_FILE_MAX_BYTES'],
        backupCount=app.config['LOG_BACKUP_COUNT']
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))

    # Error-specific file handler
    error_file_handler = RotatingFileHandler(
        os.path.join(app.config['LOG_DIR'], 'error.log'),
        maxBytes=app.config['LOG_FILE_MAX_BYTES'],
        backupCount=app.config['LOG_BACKUP_COUNT']
    )
    error_file_handler.setFormatter(formatter)
    error_file_handler.setLevel(logging.ERROR)

    # Console handler (only in development)
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app_logger.addHandler(console_handler)

    # Add handlers
    app_logger.addHandler(file_handler)
    app_logger.addHandler(error_file_handler)

    # Email handler for errors in production
    if not app.debug and app.config.get('MAIL_SERVER'):
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['MAIL_USERNAME'],
            toaddrs=app.config['ADMINS'],
            subject='Application Error',
            credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']),
            secure=() if app.config.get('MAIL_USE_TLS') else None
        )
        mail_handler.setLevel(logging.ERROR)
        app_logger.addHandler(mail_handler)

    # Register request tracking middleware
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        app_logger.info("[%s] %s %s started", g.request_id, request.method, request.path)

        if app.debug and request.is_json:
            app_logger.debug("[%s] Request Body: %s", g.request_id, request.get_json())

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            app_logger.info("[%s] %s %s completed with status %s in %.4fs",
                            g.request_id, request.method, request.path,
                            response.status_code, elapsed)
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        app_logger.error("[%s] Unhandled exception: %s",
                        getattr(g, 'request_id', 'no_request_id'),
                        str(e),
                        exc_info=True)
        # Always reraise to let other error handlers catch it
        raise e

    # Make app_logger available to the app
    app.logger = app_logger

    return app_logger



# Audit logger setup
def setup_audit_logger(app):
    """
    A function to setup audit logger
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(app.config['LOG_DIR']):
        os.makedirs(app.config['LOG_DIR'])

    # Audit logger
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False

    # Clear handlers to avoid duplicates
    if audit_logger.handlers:
        audit_logger.handlers.clear()

    # Audit log formatter - simplified and structured
    audit_formatter = logging.Formatter('%(asctime)s - %(message)s')

    # Audit file handler (rotating)
    audit_file_handler = RotatingFileHandler(
        os.path.join(app.config['LOG_DIR'], 'audit.log'),
        maxBytes=app.config['LOG_FILE_MAX_BYTES'],
        backupCount=app.config['LOG_BACKUP_COUNT']
    )
    audit_file_handler.setFormatter(audit_formatter)
    audit_file_handler.setLevel(logging.INFO)
    audit_logger.addHandler(audit_file_handler)

    # Make audit_logger available to the app
    app.audit_logger = audit_logger

    return audit_logger

# End of file
