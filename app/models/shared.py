"""
Shared clasess and functions
"""

import uuid
from enum import Enum
from datetime import datetime
from app.extensions import db

def generate_uuid():
    """
    A function to generate UUID for primary keys
    """
    return str(uuid.uuid4())


class TimeStampMixin:
    """
    A timestamp mixin function
    """
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    created_by = db.Column(db.String(36), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    updated_by = db.Column(db.String(36), nullable=False)

# End of shared classes defination file
