"""
Money Tracker - Configuration Classes
app/config.py
"""

import os
import logging
from logging import StreamHandler, FileHandler
# from urllib.parse import quote_plus
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    """
    Base Configuration
    """

    # Application
    APP_NAME = 'Money Tracker'
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.dirname(BASE_DIR)

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
    LOG_FILE = os.path.join(LOG_DIR, "app.log")
    ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")
    os.makedirs(LOG_DIR, exist_ok=True) 

    # File Upload Configuration
    MAX_CONTENT_SIZE = 5 * 1024 * 1024  # 5MB maximum size
    ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv",}
    UPLOADS_FOLDER = os.path.join(BASE_DIR, "uploads")

    # Asset Image and Invoice Document upload directories
    IMAGES_FOLDER = os.path.join(UPLOADS_FOLDER, "images")
    DOCUMENTS_FOLDER = os.path.join(UPLOADS_FOLDER, "documents")

    # Create upload directories
    os.makedirs(UPLOADS_FOLDER, exist_ok=True)
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)

    # Consider adding SMTP handler settings for error notifications
    # Email Configuration (using SendGrid as example)
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

    # Session settings (base — overridden per environment below)
    # PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    # REMEMBER_COOKIE_DURATION   = timedelta(days=1)

    @classmethod
    def init_app(cls, app):
        """Shared logging setup — runs for every environment."""
        fmt = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )

        console = StreamHandler()
        console.setFormatter(fmt)

        app_fh = FileHandler(cls.LOG_FILE)
        app_fh.setLevel(logging.INFO)
        app_fh.setFormatter(fmt)

        error_fh = FileHandler(cls.ERROR_LOG_FILE)
        error_fh.setLevel(logging.ERROR)
        error_fh.setFormatter(fmt)

        app.logger.setLevel(cls.LOG_LEVEL)
        app.logger.addHandler(console)
        app.logger.addHandler(app_fh)
        app.logger.addHandler(error_fh)

class TestingConfig(AppConfig):
    """
    Testing Configuration
    """
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL_DEV")
    # DB_DEV_PASSWORD = quote_plus(os.environ.get("DB_DEV_PASSWORD"))

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(AppConfig):
    """
    Development configuration
    """
    DEBUG = True
    LOG_LEVEL = logging.DEBUG
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL_DEV")
    # DB_DEV_PASSWORD = quote_plus(os.environ.get("DB_DEV_PASSWORD"))

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_SECURE = False


class ProductionConfig(AppConfig):
    """
    Production configuration
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL_PRO")
    # DB_PRO_PASSWORD = quote_plus(os.environ.get("DB_PRO_PASSWORD"))

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    # SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    REMEMBER_COOKIE_DURATION   = timedelta(days=1)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Get configuration based on environment
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    return config.get(config_name, DevelopmentConfig)


# End of file
