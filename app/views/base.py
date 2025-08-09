"""
Admin configuration file that contains admin views and routes.
"""

from flask import Blueprint, render_template
from flask_login import login_required
# from app.models.category import Category
# from app.models.transaction import Transaction

base_bp = Blueprint('base', __name__, url_prefix='/app')


@base_bp.route('/user/')
@login_required
def user():
    """
    User landing page view
    """
    return render_template('user/dashboard.html',
                           title='Dashboard',
                           DASHBOARD=True)

@base_bp.route('/admin/')
@login_required
def admin():
    """
    Admin landing page view
    """
    return render_template('admin/dashboard.html',
                           title='Dashboard',
                           DASHBOARD=True)

# End of file
