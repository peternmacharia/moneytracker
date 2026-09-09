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
from app.extensions import init_extensions, db, login_manager
from app.seed_data import init_data
from app.navigation import PUBLIC_SIDEBAR_ITEMS, ADMIN_SIDEBAR_ITEMS
from app.utils.errors import register_error_handlers
from app.utils.filters import register_filters, register_context_processors
from app.models import User
# from app.seed_data import *
# from app.navigation import SIDEBAR_GROUPS
# from app.forms import ContactForm

# Blueprints import
# System routes
# from app.routes.auditlog    import auditlog_bp

# Auth routes
from app.routes.web.auth.auth        import auth_bp
from app.routes.web.auth.permission  import permission_bp
from app.routes.web.auth.role        import role_bp
from app.routes.web.auth.user        import user_bp

# User routes
from app.routes.web.public.main      import public_main_bp
from app.routes.web.public.workspace import workspace_bp

# Admin routes
from app.routes.web.admin.main       import admin_main_bp




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



    # Registration of the App Blueprint View Routes
    # System routes
    # app.register_blueprint(auditlog_bp)

    # Auth routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(user_bp)

    # User routes
    app.register_blueprint(public_main_bp)
    app.register_blueprint(workspace_bp)

    # Admin routes
    app.register_blueprint(admin_main_bp)


    @app.context_processor
    def inject_sidebars():
        return dict(
            public_sidebar_items=PUBLIC_SIDEBAR_ITEMS,
            admin_sidebar_items=ADMIN_SIDEBAR_ITEMS,
        )


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


    # Default app route redirect to app login page
    @app.route('/')
    def index():
        """
        The app landing page
        """
        return render_template("index.html", title="Home")


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