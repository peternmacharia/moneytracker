"""
Role routes and views configuration file
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy.sql import desc, asc
from app.extensions import db
from app.models.role import Role
from app.forms.role import RoleForm
# from app.decorators.auth import require_permission
# from app.utils.audit import audit_trail

role_bp = Blueprint('role', __name__, url_prefix='/roles')


@role_bp.route('/index/')
@login_required
# @require_permission('Role', 'read')
# @audit_trail(action="user_registration", resource_type="user")
def index():
    """
    Render Roles page with search, sort and pagination
    """
    form = RoleForm()

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 15, type=int)

    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'created_at')  # Default sorting by created_at
    sort_order = request.args.get('sort_order', 'desc')  # Default sorting order is descending

    allowed_sort_fields = {
        'name': Role.name,
        'created_at': Role.created_at
    }

    if sort_by not in allowed_sort_fields:
        sort_by = 'created_at'

    # Build query
    query = Role.query

    count_roles = Role.query.count()

    # searching
    if search:
        search_filter = (
            Role.name.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)

    # Sorting
    sort_column = allowed_sort_fields[sort_by]
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    roles = query.order_by(Role.created_at.desc()).paginate(page=page,
                                                            per_page=page_size)

    if not roles.items:
        flash('No role records added Yet!', 'warning')

    return render_template('role/index.html',
                           title='Roles',
                           form=form, search=search,
                           sort_by=sort_by,
                           sort_order=sort_order,
                           page_size=page_size,
                           count_roles=count_roles,
                           roles=roles,
                           SETTINGS=True,
                           ROLES=True)



@role_bp.route('/create/', methods=['GET', 'POST'])
@login_required
# @require_permission('Role', 'create')
def create():
    """
    Add New Role View
    """
    form = RoleForm()

    if request.method == 'POST':
        name = form.name.data

        test = Role.query.filter_by(name=name).first()

        if test:
            flash(f'{name} role already exists!', 'warning')
            return redirect(url_for('role.index'))
        else:
            try:
                new_role = Role(name=name,
                                created_by=current_user.id,
                                updated_by=current_user.id)
                db.session.add(new_role)
                db.session.commit()
                flash(f'{name} is created successfully!', 'success')
                return redirect(url_for('role.index'))
            except ImportError:
                flash('There was an error saving data!', 'danger')
                db.session.rollback()
                return redirect(url_for('role.index'))

    return render_template('role/index.html',
                           title='New Role',
                           form=form,
                           SETTINGS=True,
                           ROLES=True)



@role_bp.route('/update/<string:role_id>/', methods=['GET', 'POST'])
@login_required
# @require_permission('Role', 'update')
def update(role_id):
    """
    Update Role View or 404 if record id not found
    """
    item = Role.query.get_or_404(role_id)
    form = RoleForm(obj=item)

    if item.name == 'ADMIN':
        flash('The admin role cannot be edited!', 'danger')
        return redirect(url_for('role.index'))

    if request.method == 'POST':
        existing_role = Role.query.filter_by(name=form.name.data).first()
        if existing_role and existing_role.id != item.id:
            flash('Role name already exists!', 'warning')
            db.session.rollback()
            return redirect(url_for('role.index'))

        item.name = form.name.data
        item.updated_by = current_user.id

        error = None

        if error:
            flash(error)
        else:
            try:
                db.session.commit()
                flash(f'{item.name} is updated successfully!', 'success')
                return redirect(url_for('role.index'))
            except ImportError:
                flash('There was an error during the update!', 'danger')
                db.session.rollback()
            return redirect(url_for('role.index'))

    return render_template('role/update.html',
                           title='Update Role',
                           form=form,
                           SETTINGS=True,
                           ROLES=True)



@role_bp.route('/delete/<string:role_id>/', methods=['GET', 'POST'])
@login_required
# @require_permission('Role', 'delete')
def delete(role_id):
    """
    Delete Role View or 404 if record id not found
    """
    item = Role.query.get_or_404(role_id)
    form = RoleForm(obj=item)

    if item.name == 'ADMIN':
        flash('The admin role cannot be deleted!', 'danger')
        return redirect(url_for('role.index'))

    if request.method == 'POST':
        try:
            db.session.delete(item)
            db.session.commit()
            flash('Role is deleted successfully!', 'success')
            return redirect(url_for('role.index'))
        except ImportError:
            flash('There was an error during the deletion!', 'danger')
            db.session.rollback()
            return redirect(url_for('role.index'))

    return render_template('role/delete.html',
                           title='Delete Role',
                           form=form,
                           SETTINGS=True,
                           ROLES=True)

# End of file
