"""
Role model class defination file
"""

from app.extensions import db
from app.models.shared import generate_uuid, TimeStampMixin

class Role(db.Model, TimeStampMixin):
    """
    Role model defination
    """
    __tablename__ = 'roles'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(10), unique=True, nullable=False)

    def __repr__(self):
        return f'<Role {self.name}>'

# End of file
