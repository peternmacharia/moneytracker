"""
Category model class defination file
"""

from datetime import datetime
from app.extensions import db
from app.models.shared import generate_uuid

class Category(db.Model):
    """
    Category model defination
    """
    __tablename__ = 'categories'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(20), default='💰')
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    # Relationships
    user = db.relationship('User', backref='categories')

    def __repr__(self):
        return f'<Category {self.name}>'

# End of file
