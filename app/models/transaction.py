"""
Transaction model class defination file
"""

from enum import Enum
from app.extensions import db
from app.models.shared import generate_uuid, TimeStampMixin

class TType(Enum):
    """
    Transaction Type enum defination
    """
    INCOME = 'income'
    EXPENSE = 'expense'

class Transaction(db.Model, TimeStampMixin):
    """
    Transaction model defination
    """
    __tablename__ = 'transactions'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    transaction_type = db.Column(db.Enum(TType), nullable=False)
    # Relationship
    category = db.relationship('Category', backref='transactions')

    def __repr__(self):
        return f'<Transaction {self.category_id}>'

# End of file
