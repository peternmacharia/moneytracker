# """
# Initial system launch configuration file
# """

# import os
# from flask import Flask, render_template
# from flask_login import current_user
# from app.config import get_config
# from app.extensions import db, login_manager, migrate
# from app.utils.logging import setup_logger, setup_audit_logger
# from app.models.user import User
# from app.models import init_default_data
# from app.views.audit import auditlog_bp
# from app.views.role import role_bp
# from app.views.adminuser import admin_bp
# from app.views.user import user_bp
# from app.views.auth import auth_bp
# from app.views.base import base_bp
# from app.views.category import category_bp
# from app.views.transaction import transaction_bp
# # from app.config import config
# # from views.errors import register_error_handlers

# # Application factory function that created the app
# # def create_app(config_class='default'):
# def create_app(config_name=None):
#     """
#     Application factory function that creates and configures the app
#     """
#     # app = Flask(__name__, instance_relative_config=True)
#     # # application = app
#     # app.config.from_object(config[config_class])
#     # app.config.from_pyfile('config.py', silent=True)

#     app = Flask(__name__)

#     if config_name is None:
#         config_name = os.environ.get("FLASK_ENV", "development")
#     app.config.from_object(get_config(config_name))

#     # Set up logging
#     setup_logger(app)
#     setup_audit_logger(app)

#     # Database and other Extension Initialization
#     db.init_app(app)
#     migrate.init_app(app, db)
#     login_manager.init_app(app)
#     login_manager.login_view = 'auth.login'



#     # Registration of the App Blueprint View Routes
#     app.register_blueprint(auditlog_bp)
#     app.register_blueprint(role_bp)
#     app.register_blueprint(user_bp)
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(base_bp)
#     app.register_blueprint(category_bp)
#     app.register_blueprint(transaction_bp)



#     # Default app route redirect to landing page
#     @app.route('/')
#     def index():
#         """
#         The default index page to redirect to landing page
#         """
#         if current_user.is_authenticated:
#             app.logger.info('User accessed Index page')
#             return render_template('index.html',
#                                    title='Home')
#         else:
#             return render_template('index.html',
#                                    title='Home')
    
#     @app.route('/contact/')
#     def contact():
#         """
#         Contact page
#         """
#         if current_user.is_authenticated:
#             app.logger.info('User accessed ContactUs Page')
#             return render_template('contact.html',
#                                    title='Contact',
#                                    CONTACT=True)
#         else:
#             return render_template('contact.html',
#                                    title='Contact Us',
#                                    CONTACT=True)



#     # Comma formater for larger numbers
#     @app.template_filter('comma_format')
#     def comma_format(value):
#         if value is None:
#             return "0"
#         return f"{value:,.2f}"



#     @login_manager.user_loader
#     def load_user(user_id):
#         """
#         A function to load a logged in user
#         """
#         return User.query.get(user_id)


#     # Register error handlers
#     # register_error_handlers(app)



#     with app.app_context():
#         db.create_all()
#         init_default_data()


#     return app

# # End of file



"""
app/__init__.py  — Application factory and initialization of the app
"""

import os
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, flash, current_app
from flask_mail import Message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_config
from app.extensions import init_extensions, db, login_manager, mail
# from app.seed_data import init_data
from app.utils.errors import register_error_handlers
from app.utils.filters import register_filters, register_context_processors
from app.seed_data import *
from app.navigation import SIDEBAR_GROUPS
# from app.forms import ContactForm

# # Blueprints
from app.routes.auth        import auth_bp
from app.routes.main        import main_bp
from app.routes.user        import user_bp
from app.routes.permission  import permission_bp
from app.routes.role        import role_bp


def create_app(config_name=None):
    """
    Application factory function that creates and configures the app
    """
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    cfg = get_config(config_name)
    app.config.from_object(cfg)
    cfg.init_app(app) 

    init_extensions(app)
    register_commands(app)

    register_filters(app)
    register_context_processors(app)
    register_error_handlers(app)



    # # Registration of the App Blueprint View Routes
    # # app.register_blueprint(auditlog_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(role_bp)

    @app.context_processor
    def inject_current_year():
        """Inject current year into all templates"""
        return {'current_year': datetime.now().year}

    @login_manager.user_loader
    def load_user(user_id):
        """
        A function to load a logged in user
        """
        return db.session.get(User, user_id)

    @app.context_processor
    def inject_sidebar():
        return dict(sidebar_groups=SIDEBAR_GROUPS)

    # Default app route redirect to app login page
    @app.route('/')
    def index():
        """
        Loading default landing page
        """
        current_app.logger.info("Loading default landing page | ip=%s", request.remote_addr)
        return redirect(url_for('main.index'))


    with app.app_context():
        db.session.execute(db.text("SELECT 1"))
        print("Database connected ✅!")

    return app


def register_commands(app):
    """Register Flask CLI commands."""

    @app.cli.command("seed-db")
    def seed_db():
        """Seed the database with initial data."""
        init_data()
        print("✔ Database seeded.\n")

    @app.cli.command("create-tables")
    def create_tables():
        """Create all database tables (development only)."""
        with app.app_context():
            db.create_all()
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print("✅ Tables created successfully!")
            print(f"📋 Tables created: {tables}.\n")

    @app.cli.command("drop-tables")
    def drop_tables():
        """Drop all database tables (DANGER!)."""
        if input("⚠️ This will delete ALL data. Type 'YES' to continue: ") == "YES":
            with app.app_context():
                db.drop_all()
                print("✔ Tables dropped.\n")
        else:
            print("❌ Operation cancelled.\n")

    @app.cli.command("reset-db")
    def reset_db():
        """Drop and recreate all database tables."""
        if input("⚠️ This will delete ALL data. Type 'YES' to continue: ") == "YES":
            with app.app_context():
                db.drop_all()
                db.create_all()
                print("✔ Database reset successfully.\n")
        else:
            print("❌ Operation cancelled.\n")


# End of file