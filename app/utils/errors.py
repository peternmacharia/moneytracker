"""
app/utils/errors.py - Centralized error handling for the app
"""

from flask import render_template, flash, redirect, url_for
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(400)
    def bad_request(e):
        flash('Bad request. Please check your input and try again.', 'warning')
        return render_template('errors/400.html', error=e), 400

    @app.errorhandler(401)
    def unauthorized(e):
        flash('Authentication required. Please log in to continue.', 'error')
        return redirect(url_for('auth.login'))

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html', error=e), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html', error=e), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        app.logger.error(f'Internal error: {str(e)}')
        return render_template('errors/500.html', error=e), 500

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(e):
        db.session.rollback()
        app.logger.error(f'Database error: {str(e)}')
        return render_template('errors/500.html', error=e), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP errors to their respective handlers
        if isinstance(e, HTTPException):
            return e

        db.session.rollback()
        app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
        return render_template('errors/500.html', error=e), 500

# End of file
