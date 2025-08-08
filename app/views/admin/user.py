"""
User configuration file that contains user views and routes.
"""

from flask import (Blueprint, current_app, flash, redirect, render_template, request, url_for)
from flask_login import login_required, current_user
from sqlalchemy.sql import desc, asc
from app.extensions import db
# from app.models.role import Role
from app.models.user import User
from app.models.country import Country
from app.models.department import Department
# from app.views.auth import permission_required, role_required
from app.forms.user import UserForm, UserDetailsForm, UserUpdateForm, ChangePasswordForm
# from app.decorators.auth import require_permission

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/index/')
@login_required
def index():
    """
    Render User page with search, sort and pagination
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 15, type=int)

    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'last_login')  # Default sorting by created_at
    sort_order = request.args.get('sort_order', 'desc')  # Default sorting order is descending

    allowed_sort_fields = {
        'username': User.username,
        'status': User.status,
        'last_login': User.last_login,
        'created_at': User.created_at
    }

    if sort_by not in allowed_sort_fields:
        sort_by = 'last_login'

    # Build query
    query = User.query

    count_users = User.query.count()

    # searching
    if search:
        search_filter = (
            User.username.ilike(f'%{search}%') |
            Country.name.ilike(f'%{search}%') |
            Department.name.ilike(f'%{search}%')
        )
        query = query.join(Country).join(Department).filter(search_filter)

    # Sorting
    sort_column = allowed_sort_fields[sort_by]
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    users = query.order_by(User.created_at.desc()).paginate(page=page,
                                                            per_page=page_size)

    if not users.items:
        flash('No user records added Yet!', 'warning')

    return render_template('user/index.html',
                           title='Users',
                           search=search,
                           sort_by=sort_by,
                           sort_order=sort_order,
                           page_size=page_size,
                           users=users,
                           count_users=count_users,
                           SETTINGS=True,
                           USERS=True)


@user_bp.route('/details/<string:user_id>/', methods=['GET'])
@login_required
def details(user_id):
    """
    User Details View or 404 if record id not found
    """
    item = User.query.get_or_404(user_id)
    form = UserDetailsForm(obj=item)
    form.country.choices = [(c.id, c.name)
                            for c in Country.query.filter(Country.id == item.country_id)]
    form.department.choices = [(d.id, d.name)
                               for d in Department.query.filter(Department.id == item.department_id)]

    if not item:
        flash('No user details added yet!', 'warning')

    return render_template('user/details.html',
                           title='User Details',
                           item=item,
                           form=form,
                           SETTINGS=True,
                           USERS=True)


@user_bp.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    """
    Add New User View
    """
    form = UserForm()
    form.country.choices = [('', 'Select Country')] + [(c.id, c.name)
                                                   for c in Country.query.all()]
    form.department.choices = [('', 'Select Department')] + [(d.id, d.name)
                                                         for d in Department.query.all()]

    if request.method == 'POST':
        username = form.username.data
        phone = form.phone.data
        email = form.email.data
        password = form.password.data
        country = form.country.data
        department = form.department.data
        is_2fa_enabled = form.is_2fa_enabled.data

        error = None

        if error:
            flash(error)

        test = User.query.filter_by(username=username).first()

        if test:
            flash(f'{username} already exists!', 'warning')
            return redirect(url_for('user.index'))
        else:
            try:
                new_user = User(username=username,
                                phone=phone,
                                email=email,
                                country_id=country,
                                department_id=department,
                                is_2fa_enabled=is_2fa_enabled,
                                created_by=current_user.id,
                                updated_by=current_user.id)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()

                flash(f'{username} is created successfully!', 'success')
                return redirect(url_for('user.index'))
            except ImportError:
                flash('There was an error saving data!', 'danger')
                db.session.rollback()
                return redirect(url_for('user.index'))

    return render_template('user/create.html',
                           title='New User',
                           form=form,
                           SETTINGS=True,
                           USERS=True)


@user_bp.route('/update/<string:user_id>/', methods=['GET', 'POST'])
@login_required
def update(user_id):
    """
    Update User View or 404 if record id not found
    """
    item = User.query.get_or_404(user_id)
    form = UserUpdateForm(obj=item)
    form.country.choices = [(c.id, c.name)
                            for c in Country.query.all()]
    form.department.choices = [(d.id, d.name)
                               for d in Department.query.all()]

    if item.username == 'SUPERADMIN':
        flash('The Super User cannot be edited!', 'danger')
        return redirect(url_for('user.index'))

    if request.method == 'POST':
        item.phone = form.phone.data
        item.email = form.email.data
        item.country_id = form.country.data
        item.department_id = form.department.data
        item.updated_by = current_user.id

        error = None

        if error:
            flash(error)
        else:
            try:
                db.session.commit()
                flash('User is updated successfully!', 'success')
                return redirect(url_for('user.index'))
            except ImportError:
                flash('There was an error during the update!', 'danger')
                db.session.rollback()
                return redirect(url_for('user.index'))

    return render_template('user/update.html',
                           title='Update User',
                           form=form,
                           SETTINGS=True,
                           USERS=True)


@user_bp.route('/changepassword/<string:user_id>/', methods=['GET', 'POST'])
@login_required
def changepassword(user_id):
    """
    Change Password User View or 404 if record id not found
    """

    if current_user.id != user_id and not current_user.role.name in ['ADMIN', 'SUPER']:
        flash('You do not have permission to change this password!', 'danger')
        return redirect(url_for('user.index'))

    item = User.query.get_or_404(user_id)
    form = ChangePasswordForm()

    if item.username == 'SUPERADMIN' and current_user.id != user_id:
        flash('The super user password cannot be edited!', 'danger')
        return redirect(url_for('user.index'))

    # if request.method == 'POST':
        # item.password = form.new_password.data
        # item.set_password(form.new_password.data)

        # if error:
        #     flash(error)
        # else:
        #     try:
        #         db.session.commit()
        #         flash('User password is updated successfully!', 'success')
        #         return redirect(url_for('user.index'))
        #     except ImportError:
        #         flash('There was an error during the update!', 'danger')
        #         db.session.rollback()
        #         return redirect(url_for('user.index'))
    if request.method == 'POST':
        if form.new_password.data != form.confirm_password.data:
            flash('Password and confirmation do not match!', 'danger')
        elif len(form.new_password.data) < 8:
            flash('Password must be at least 8 characters long!', 'danger')
        else:
            try:
                item.set_password(form.new_password.data)
                db.session.commit()

                # Log the password change
                current_app.logger.info(f"Password changed for user {item.username} "
                                        f"by {current_user.username}")

                flash('User password has been updated successfully!', 'success')

                # If user changed their own password, redirect to profile
                if current_user.id == user_id:
                    return redirect(url_for('user.profile', user_id=user_id))
                else:
                    return redirect(url_for('user.index'))

            except ImportError:
                current_app.logger.error('Error changing password')
                flash('There was an error during the update!', 'danger')
                db.session.rollback()
                return redirect(url_for('user.index'))

    return render_template('user/changepassword.html',
                           title='Change Password',
                           item=item,
                           form=form,
                           SETTINGS=True,
                           USERS=True)



@user_bp.route('/delete/<string:user_id>/', methods=['GET', 'POST'])
@login_required
def delete(user_id):
    """
    Delete User View or 404 if record id not found
    """
    item = User.query.get_or_404(user_id)
    form = UserDetailsForm(obj=item)
    form.country.choices = [(c.id, c.name)
                            for c in Country.query.all()]
    form.department.choices = [(d.id, d.name)
                               for d in Department.query.all()]

    if item.username == 'SUPERADMIN':
        flash('The super user cannot be deleted!', 'danger')
        return redirect(url_for('user.index'))

    if request.method == 'POST':
        try:
            db.session.delete(item)
            db.session.commit()
            flash('User is deleted successfully!', 'success')
            return redirect(url_for('user.index'))
        except ImportError:
            flash('There was an error during the deletion!', 'danger')
            db.session.rollback()
            return redirect(url_for('user.index'))

    return render_template('user/delete.html',
                           title='Delete User',
                           form=form,
                           SETTINGS=True,
                           USERS=True)

# End of file
