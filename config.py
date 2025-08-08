"""
Config file that stores secret keys and db connections
"""

import os

class AppConfig:
    """
    App Base Configuration
    """
    SECRET_KEY = os.urandom(32)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SESSION_TIMEOUT_MINUTES = 30
    MAX_LOGIN_ATTEMPTS = 5

    # Logging Configuration
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE_MAX_BYTES = 10485760  # 10MB
    LOG_BACKUP_COUNT = 10

    # Asset Image and Invoice Document upload directory configuration folders
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_SIZE = 5 * 1024 * 1024  # 5MB maximum size
    
    # File upload restrictions
    # Image restrictions
    ALLOWED_IMAGE_EXTENSIONS = {'png'}  # Only allow PNG files
    # Document restrictions
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf'}  # Only allow PDF files

    # Make sure the upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'assets', 'images'), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'assets', 'documents'), exist_ok=True)


class TestingConfig(AppConfig):
    """
    Testing Configuration
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///MTrackerDB.db'

class DevelopmentConfig(AppConfig):
    """
    Development configuration
    """
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///MtracketDB.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///MTrackerDevDB.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(AppConfig):
    """
    Production configuration
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             'postgresql://user:password@localhost/mtrackerprodb')

    # Consider adding SMTP handler settings for error notifications
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['itsupport@mtracker.com']


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# End of file
