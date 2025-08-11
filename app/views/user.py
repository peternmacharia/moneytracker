"""
User configuration file that contains user views and routes.
"""

from flask import (Blueprint, current_app, flash, redirect, render_template, request, url_for)
from flask_login import login_required, current_user
from sqlalchemy.sql import desc, asc
from app.extensions import db
from app.models.user import User
from app.models.role import Role
from app.forms.user import UserForm, UserDetailsForm, UserUpdateForm
from app.forms.auth import ChangePasswordForm


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
            Role.name.ilike(f'%{search}%')
        )
        query = query.join(Role).filter(search_filter)

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
    form.role.choices = [(r.id, r.name)
                         for r in Role.query.filter(Role.id == item.role_id)]

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
    user_role = Role.query.filter_by(name="USER").first()

    if request.method == 'POST':
        firstname = form.firstname.data
        lastname = form.lastname.data
        fullname = firstname + " " + lastname
        username = form.username.data
        phone = form.phone.data
        email = form.email.data
        password = form.password.data
        role = user_role

        error = None

        if error:
            flash(error)

        test = User.query.filter_by(username=username).first()

        if test:
            flash(f'{username} already exists!', 'warning')
            return redirect(url_for('user.index'))
        else:
            try:
                new_user = User(firstname=firstname,
                                lastname=lastname,
                                fullname=fullname,
                                username=username,
                                phone=phone,
                                email=email,
                                role_id=role,
                                created_by='self',
                                updated_by='self')
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

    if item.username == 'ADMIN':
        flash('The admin user cannot be edited!', 'danger')
        return redirect(url_for('user.index'))

    if request.method == 'POST':
        item.firstname = form.firstname.data
        item.lastname = form.lastname.data
        item.fullname = form.firstname.data + " " + form.lastname.data
        item.phone = form.phone.data
        item.email = form.email.data
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
    form.role.choices = [(r.id, r.name) for r in Role.query.all()]
    form.role.data = item.role_id

    if item.username == 'ADMIN':
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
