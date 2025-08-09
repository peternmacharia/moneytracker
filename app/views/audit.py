"""
Audit Log routes and views configuration file
"""

from flask import Blueprint, flash, render_template, request
from flask_login import login_required
from sqlalchemy.sql import desc, asc
from app.models.auditlog import Auditlog
from app.models.user import User

auditlog_bp = Blueprint('auditlog', __name__, url_prefix='/auditlogs')


@auditlog_bp.route('/index/')
@login_required
def index():
    """
    Render Adit log page with search, sort and pagination
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 25, type=int)

    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'created_at')  # Default sorting by created_at
    sort_order = request.args.get('sort_order', 'desc')  # Default sorting order is descending

    allowed_sort_fields = {
        'user_id': Auditlog.user_id,
        'action': Auditlog.action,
        'resource': Auditlog.resource_type,
        'ip_address': Auditlog.ip_address,
        'agent': Auditlog.user_agent,
        'created_at': Auditlog.created_at
    }

    if sort_by not in allowed_sort_fields:
        sort_by = 'created_at'

    # Build query
    query = Auditlog.query

    auditlogs_count = Auditlog.query.count() or 0

    # searching
    if search:
        search_filter = (
            User.username.ilike(f'%{search}%') |
            Auditlog.action.ilike(f'%{search}%') |
            Auditlog.resource_type.ilike(f'%{search}%') |
            Auditlog.user_agent.ilike(f'%{search}%')
        )
        query = query.join(User).filter(search_filter)

    # Sorting
    sort_column = allowed_sort_fields[sort_by]
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    auditlogs = query.order_by(Auditlog.created_at.desc()).paginate(page=page, per_page=page_size)

    if not auditlogs.items:
        flash('No audit logs records added Yet!', 'warning')

    return render_template('audit/index.html',
                           title='Logs',
                           search=search,
                           sort_by=sort_by,
                           sort_order=sort_order,
                           page_size=page_size,
                           auditlogs_count=auditlogs_count,
                           auditlogs=auditlogs,
                           SETTINGS=True,
                           AUDIT_TRAILS=True)

# End of file
