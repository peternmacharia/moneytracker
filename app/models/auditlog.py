"""
Audit Log model class defination file
"""

from datetime import datetime
from app.extensions import db
from app.models.shared import generate_uuid, TimeStampMixin

class Auditlog(db.Model, TimeStampMixin):
    """
    Audit Log model defination
    """
    __tablename__ = 'auditlogs'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    user_id = db.Column(db.String(50), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=True)
    resource_id = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(200), nullable=True)
    request_id = db.Column(db.String(36), nullable=False)
    details = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Auditlog {self.action} by {self.user_id} at {self.timestamp}>'

# End of file
