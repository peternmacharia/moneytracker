"""
Extensions configuration file
"""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Extensions Initialization
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# End of file
