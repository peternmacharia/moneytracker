"""
Transaction model class defination file
"""

from enum import Enum
from datetime import datetime
from app.extensions import db
from app.models.shared import generate_uuid

class TType(Enum):
    """
    Transaction Type enum defination
    """
    INCOME = 'income'
    EXPENSE = 'expense'

class Transaction(db.Model):
    """
    Transaction model defination
    """
    __tablename__ = 'transactions'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    transaction_type = db.Column(db.Enum(TType), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.now().date())
    created_at = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    # Relationship
    category = db.relationship('Category', backref='transactions')
    user = db.relationship('User', backref='transactions')

    def __repr__(self):
        return f'<Transaction {self.category_id}>'

# End of file
