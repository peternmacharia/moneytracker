"""
Transaction routes and views configuration file
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy.sql import desc, asc
from app.extensions import db
from app.models.category import Category
from app.models.transaction import Transaction
from app.forms.transaction import TransactionForm

transaction_bp = Blueprint('transaction', __name__, url_prefix='/transactions')


@transaction_bp.route('/index/')
@login_required
# @require_permission('Role', 'read')
# @audit_trail(action="user_registration", resource_type="user")
def index():
    """
    Render Transactions page with search, sort and pagination
    """
    form = TransactionForm()
    form.category.choices = [('', 'Select Category')] + [(c.id, c.name)
                                                         for c in Category.query.all()]

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 15, type=int)

    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'created_at')  # Default sorting by created_at
    sort_order = request.args.get('sort_order', 'desc')  # Default sorting order is descending

    allowed_sort_fields = {
        'category': Transaction.category_id,
        'amount': Transaction.amount,
        'type': Transaction.transaction_type,
        'created_at': Transaction.created_at
    }

    if sort_by not in allowed_sort_fields:
        sort_by = 'created_at'

    # Build query
    query = Transaction.query

    count_transactions = Transaction.query.count()

    # searching
    if search:
        search_filter = (
            Category.name.ilike(f'%{search}%') |
            Transaction.amount.ilike(f'%{search}%')
        )
        query = query.join(Category).filter(search_filter)

    # Sorting
    sort_column = allowed_sort_fields[sort_by]
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    transactions = query.order_by(Transaction.created_at.desc()).paginate(page=page,
                                                                          per_page=page_size)

    if not transactions.items:
        flash('No transaction records added Yet!', 'warning')

    return render_template('user/transaction/index.html',
                           title='Transactions',
                           form=form, search=search,
                           sort_by=sort_by,
                           sort_order=sort_order,
                           page_size=page_size,
                           count_transactions=count_transactions,
                           transactions=transactions,
                           TRANSACTION=True)



@transaction_bp.route('/create/', methods=['GET', 'POST'])
@login_required
# @require_permission('Role', 'create')
def create():
    """
    Add New Transaction View
    """
    form = TransactionForm()
    form.category.choices = [('', 'Select Category')] + [(c.id, c.name)
                                                         for c in Category.query.all()]

    if request.method == 'POST':
        category = form.category.data
        amount = form.amount.data
        description = form.description.data
        transaction_type = form.transaction_type.data

        try:
            new_transaction = Transaction(category_id=category,
                                          amount=amount,
                                          description=description,
                                          transaction_type=transaction_type,
                                          created_by=current_user.id,
                                          updated_by=current_user.id)
            db.session.add(new_transaction)
            db.session.commit()
            flash('Transaction is created successfully!', 'success')
            return redirect(url_for('transaction.index'))
        except ImportError:
            flash('There was an error saving data!', 'danger')
            db.session.rollback()
            return redirect(url_for('transaction.index'))

    return render_template('user/transaction/index.html',
                           title='New Transaction',
                           form=form,
                           TRANSACTION=True)



@transaction_bp.route('/update/<string:transaction_id>/', methods=['GET', 'POST'])
@login_required
# @require_permission('Role', 'update')
def update(transaction_id):
    """
    Update Transaction View or 404 if record id not found
    """
    item = Transaction.query.get_or_404(transaction_id)
    form = TransactionForm(obj=item)
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]

    if request.method == 'POST':
        item.category_id = form.category.data
        item.amount = form.amount.data
        item.description = form.description.data
        item.transaction_type = form.transaction_type.data
        item.updated_by = current_user.id

        error = None

        if error:
            flash(error)
        else:
            try:
                db.session.commit()
                flash('Transaction is updated successfully!', 'success')
                return redirect(url_for('transaction.index'))
            except ImportError:
                flash('There was an error during the update!', 'danger')
                db.session.rollback()
            return redirect(url_for('transaction.index'))

    return render_template('user/transaction/update.html',
                           title='Update Transaction',
                           form=form,
                           TRANSACTION=True)



@transaction_bp.route('/delete/<string:transaction_id>/', methods=['GET', 'POST'])
@login_required
# @require_permission('Role', 'delete')
def delete(transaction_id):
    """
    Delete Transaction View or 404 if record id not found
    """
    item = Transaction.query.get_or_404(transaction_id)
    form = TransactionForm(obj=item)
    form.category.choices = [(c.id, c.name)
                             for c in Category.query.filter(Category.id == item.category_id).first()]

    if request.method == 'POST':
        try:
            db.session.delete(item)
            db.session.commit()
            flash('Transaction is deleted successfully!', 'success')
            return redirect(url_for('transaction.index'))
        except ImportError:
            flash('There was an error during the deletion!', 'danger')
            db.session.rollback()
            return redirect(url_for('transaction.index'))

    return render_template('user/transaction/delete.html',
                           title='Delete Transaction',
                           form=form,
                           TRANSACTION=True)

# End of file
