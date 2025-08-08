"""
Admin configuration file that contains admin views and routes.
"""

from flask import Blueprint, render_template
from flask_login import login_required
from app.extensions import db
from app.models.category import Category
from app.models.transaction import Transaction

base_bp = Blueprint('base', __name__, url_prefix='/app')


@base_bp.route('/index/')
@login_required
def index():
    """
    landing page view
    """
    total_categories = Category.query.count() or 0
    total_transactions = Transaction.query.count() or 0

    return render_template('index.html', title='Home',
                        # Organization
                        total_categories=total_categories,
                        total_transactions=total_transactions,
                        DASHBOARD=True)

# End of file
