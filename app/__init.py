"""
Initial system launch configuration file
"""

from flask import Flask, render_template
from flask_login import current_user
from app.extensions import db, login_manager, migrate
from app.utils.logging import setup_logger, setup_audit_logger
from app.models.user import User
from app.models import init_default_data
from app.views.admin.audit import auditlog_bp
from app.views.admin.role import role_bp
from app.views.admin.user import user_bp
from app.views.auth import auth_bp
from app.views.base import base_bp
from app.views.user.category import category_bp
from app.views.user.transaction import transaction_bp
from config import config
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
    app.register_blueprint(role_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(base_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(transaction_bp)



    # Default app route redirect to landing page
    @app.route('/')
    def index():
        """
        The default index page to redirect to landing page
        """
        if current_user.is_authenticated:
            app.logger.info('User accessed Dashboard')
            return render_template('index.html',
                                   title='Home')
        else:
            return render_template('index.html',
                                   title='Home')
        # return redirect(url_for('auth.login'))



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
