"""
Category routes and views configuration file
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy.sql import desc, asc
from app.extensions import db
from app.models.category import Category
from app.forms.category import CatgoryForm

category_bp = Blueprint('category', __name__, url_prefix='/categories')

@category_bp.route('/index/')
@login_required
# @require_permission('Role', 'read')
# @audit_trail(action="user_registration", resource_type="user")
def index():
    """
    Render Roles page with search, sort and pagination
    """
    form = CatgoryForm()

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 15, type=int)

    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'created_at')  # Default sorting by created_at
    sort_order = request.args.get('sort_order', 'desc')  # Default sorting order is descending

    allowed_sort_fields = {
        'name': Category.name,
        'created_at': Category.created_at
    }

    if sort_by not in allowed_sort_fields:
        sort_by = 'created_at'

    # Build query
    query = Category.query

    count_categories = Category.query.count()

    # searching
    if search:
        search_filter = (
            Category.name.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)

    # Sorting
    sort_column = allowed_sort_fields[sort_by]
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    categories = query.order_by(Category.created_at.desc()).paginate(page=page,
                                                                     per_page=page_size)

    if not categories.items:
        flash('No category records added Yet!', 'warning')

    return render_template('user/catgory/index.html',
                           title='Catgories',
                           form=form, search=search,
                           sort_by=sort_by,
                           sort_order=sort_order,
                           page_size=page_size,
                           count_categories=count_categories,
                           categories=categories,
                           CATEGORIES=True)



@category_bp.route('/create/', methods=['GET', 'POST'])
@login_required
# @require_permission('Role', 'create')
def create():
    """
    Add New Catgory View
    """
    form = CatgoryForm()

    if request.method == 'POST':
        name = form.name.data
        color = form.color.data
        icon = form.icon.data

        test = Category.query.filter_by(name=name).first()

        if test:
            flash(f'{name} role already exists!', 'warning')
            return redirect(url_for('category.index'))
        else:
            try:
                new_category = Category(name=name,
                                        color=color,
                                        icon=icon,
                                        created_by=current_user.id,
                                        updated_by=current_user.id)
                db.session.add(new_category)
                db.session.commit()
                flash(f'{name} is created successfully!', 'success')
                return redirect(url_for('category.index'))
            except ImportError:
                flash('There was an error saving data!', 'danger')
                db.session.rollback()
                return redirect(url_for('category.index'))

    return render_template('user/category/index.html',
                           title='New Role',
                           form=form,
                           CATEGORY=True)



@category_bp.route('/update/<string:category_id>/', methods=['GET', 'POST'])
@login_required
# @require_permission('Role', 'update')
def update(category_id):
    """
    Update Category View or 404 if record id not found
    """
    item = Category.query.get_or_404(category_id)
    form = CatgoryForm(obj=item)

    if request.method == 'POST':
        existing_category = Category.query.filter_by(name=form.name.data).first()
        if existing_category and existing_category.id != item.id:
            flash('Catetogy name already exists!', 'warning')
            db.session.rollback()
            return redirect(url_for('category.index'))

        item.name = form.name.data
        item.color = form.color.data
        item.icon = form.icon.data
        item.updated_by = current_user.id

        error = None

        if error:
            flash(error)
        else:
            try:
                db.session.commit()
                flash(f'{item.name} is updated successfully!', 'success')
                return redirect(url_for('category.index'))
            except ImportError:
                flash('There was an error during the update!', 'danger')
                db.session.rollback()
            return redirect(url_for('category.index'))

    return render_template('user/category/update.html',
                           title='Update Category',
                           form=form,
                           CATEGORY=True)



@category_bp.route('/delete/<string:category_id>/', methods=['GET', 'POST'])
@login_required
# @require_permission('Role', 'delete')
def delete(category_id):
    """
    Delete Category View or 404 if record id not found
    """
    item = Category.query.get_or_404(category_id)
    form = CatgoryForm(obj=item)

    if request.method == 'POST':
        try:
            db.session.delete(item)
            db.session.commit()
            flash('Category is deleted successfully!', 'success')
            return redirect(url_for('category.index'))
        except ImportError:
            flash('There was an error during the deletion!', 'danger')
            db.session.rollback()
            return redirect(url_for('category.index'))

    return render_template('user/category/delete.html',
                           title='Delete Category',
                           form=form,
                           CATEGORY=True)

# End of file
