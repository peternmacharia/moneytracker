"""
Category model class defination file
"""

from app.extensions import db
from app.models.shared import generate_uuid, TimeStampMixin

class Category(db.Model, TimeStampMixin):
    """
    Category model defination
    """
    __tablename__ = 'categories'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#6366f1')
    icon = db.Column(db.String(20), default='💰')

    def __repr__(self):
        return f'<Category {self.name}>'

# End of file
