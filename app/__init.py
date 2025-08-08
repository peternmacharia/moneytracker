"""
Initial system launch configuration file
"""

import logging
import uuid
import time
from logging.handlers import RotatingFileHandler
from logging.handlers import SMTPHandler
import os
import json
from functools import wraps
from datetime import datetime

import importlib
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base

from flask import Flask, redirect, url_for, current_app, request, g, abort
from flask_login import current_user
from app.extensions import db, login_manager, migrate
from app.utils.logging import setup_logger, setup_audit_logger
from app.models.auditlog import Auditlog
from app.models.permission import Permission
from app.models.user import User
from app.models import init_default_data
from app.views.audit import auditlog_bp
from app.views.role import role_bp
from app.views.permission import permission_bp
from app.views.user import user_bp
from app.views.role_permission import role_permission_bp
from app.views.user_role import user_role_bp
from app.views.auth import auth_bp
from app.views.base import base_bp
from app.views.category import category_bp
from app.views.transaction import transaction_bp
from config import config
# from dbsetup import db_initialize
# from views.errors import register_error_handlers

# Application factory function that created the app
def create_app(config_class='default'):
    """
    Application factory function that creates and configures the app
    """
    app = Flask(__name__, instance_relative_config=True)
    # application = app
    app.config.from_object(config[config_class])
    app.config.from_pyfile('config.py', silent=True)

    # Set up logging
    setup_logger(app)
    setup_audit_logger(app)

    # Database and other Extension Initialization
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'



    # Registration of the App Blueprint View Routes
    app.register_blueprint(auditlog_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(role_permission_bp)
    app.register_blueprint(user_role_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(base_bp)
    app.register_blueprint(country_bp)
    app.register_blueprint(region_bp)
    app.register_blueprint(center_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(asset_category_bp)
    app.register_blueprint(asset_brand_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(asset_bp)
    app.register_blueprint(asset_assignment_bp)
    app.register_blueprint(asset_transfer_bp)
    app.register_blueprint(asset_maintenance_bp)
    app.register_blueprint(depreciation_bp)
    app.register_blueprint(disposal_bp)



    # Default app route redirect to app login page
    @app.route('/')
    def index():
        """
        Redirect default landing page to login page
        """
        app.logger.info('User accessed Dashboard')
        return redirect(url_for('auth.login'))



    # Comma formater for larger numbers
    @app.template_filter('comma_format')
    def comma_format(value):
        if value is None:
            return "0"
        return f"{value:,.2f}"



    @login_manager.user_loader
    def load_user(user_id):
        """
        A function to load a logged in user
        """
        return User.query.get(user_id)


    # Register error handlers
    # register_error_handlers(app)



    with app.app_context():
        db.create_all()
        init_default_data()


    return app

# End of file
