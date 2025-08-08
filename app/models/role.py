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

    @property
    def user_list(self):
        """
        Property to get all users with this role
        """
        return [ur.user for ur in self.users]

# End of file
