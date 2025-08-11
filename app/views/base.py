"""
Admin configuration file that contains admin views and routes.
"""

import calendar
from datetime import datetime
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app.extensions import db
# from app.models.category import Category
from app.models.transaction import Transaction, TType

base_bp = Blueprint('base', __name__, url_prefix='/app')


@base_bp.route('/dashboard/')
@login_required
def dashboard():
    """
    User landing page view
    """
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc()).limit(5).all()

    # Calculate current month totals
    current_month = datetime.now().month
    current_year = datetime.now().year

    monthly_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == TType.INCOME,
        extract('month', Transaction.date) == current_month,
        extract('year', Transaction.date) == current_year,
        Transaction.user_id == current_user.id
    ).scalar() or 0

    monthly_expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == TType.EXPENSE,
        extract('month', Transaction.date) == current_month,
        extract('year', Transaction.date) == current_year,
        Transaction.user_id == current_user.id
    ).scalar() or 0

    balance = monthly_income - monthly_expenses


    return render_template('dashboard.html',
                           title='Dashboard',
                           recent_transactions=recent_transactions,
                           monthly_income=monthly_income,
                           monthly_expenses=monthly_expenses,
                           balance=balance,
                           current_month=calendar.month_name[current_month],
                           DASHBOARD=True)

# End of file
