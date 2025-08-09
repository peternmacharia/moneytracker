"""
User model class defination file
"""

from enum import Enum
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.models.shared import generate_uuid, TimeStampMixin

class UserStatus(Enum):
    """
    User Status enum defination
    """
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'

class User(db.Model, UserMixin, TimeStampMixin):
    """
    User model defination
    """
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    fullname = db.Column(db.String(50),nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id'), nullable=False)
    status = db.Column(db.Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    is_2fa_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(36), unique=True, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    # Relationship
    role = db.relationship('Role', backref='users')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """
        A function to set user password
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        A function to check if a user password is correct
        """
        return check_password_hash(self.password, password)

# End of file
