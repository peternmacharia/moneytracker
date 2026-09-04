"""
app/extensions.py  — Initialization of Flask extensions used in the app
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail


db              = SQLAlchemy()
migrate         = Migrate()
login_manager   = LoginManager()
mail            = Mail()


def init_extensions(app):
    """Initialize all Flask extensions with the app instance."""
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Single login_manager — handles User sessions
    login_manager.login_view            = "auth.login"
    login_manager.login_message         = "Please sign in to continue."
    login_manager.session_protection    = "basic"
    login_manager.init_app(app)

    return app

# End of file
