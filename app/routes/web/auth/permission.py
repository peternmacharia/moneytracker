"""
app/routes/permission.py - Defines routes related to permission management.
"""

import logging

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.extensions import db
from app.models import Permission
from app.models.base import ModelRegistry
from app.forms import (
    CreatePermissionForm, UpdatePermissionForm, DeleteForm
)
from app.utils.decorators import permission_required

logger = logging.getLogger(__name__)

permission_bp = Blueprint("permission", __name__, url_prefix="/permission",
                      template_folder="../templates/permission")


def _populate_resource_choices(form):
    """
    Populate the resource SelectField with registered models.
    """
    models = ModelRegistry.get_available_models()
    choices = [('', '-- Select Resource --')]
    for model in models:
        choices.append((model, model))
    form.resource.choices = choices


@permission_bp.route("/list", methods=["GET"])
@login_required
@permission_required("permission:view")
def index():
    """
    View for listing permissions with search, sorting, and pagination.
    """
    page     = request.args.get("page", 1, type=int)
    search   = request.args.get("s", "", type=str).strip()
    sort     = request.args.get("sort", "", type=str)
    dir_     = request.args.get("dir", "asc", type=str)
    per_page = request.args.get("per_page", 25, type=int)
    if per_page not in (25, 35, 50):
        per_page = 25

    query = Permission.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(Permission.resource.ilike(like), Permission.action.ilike(like))
        )

    sort_map = {
        "resource": Permission.resource,
        "action": Permission.action,
    }
    sort_col = sort_map.get(sort, Permission.name)  # default order
    if dir_ == "desc":
        sort_col = sort_col.desc()

    paged = query.order_by(sort_col).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "permission/list.html",
        permissions=paged,
        search=search,
        sort=sort,
        dir=dir_,
        per_page=per_page,
        title="Permissions",
    )


@permission_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required("permission:create")
def create():
    """
    View for creating a new permission.
    """
    form = CreatePermissionForm()
    _populate_resource_choices(form)

    if form.validate_on_submit():
        resource = form.resource.data.strip()

        existing = Permission.query.filter_by(name=form.name.data.strip()).first()
        if existing is not None:
            flash(f"Permission '{existing.name}' already exists.", "warning")
            return redirect(url_for("permission.index"))

        permission = Permission(
            name=resource + ":" + form.action.data.strip(),
            resource=resource,
            action=form.action.data.strip()
        )
        db.session.add(permission)

        try:
            db.session.commit()
            flash(f"Permission '{permission.name}' created successfully.", "success")
            logger.info("Permission created: id=%s name=%s", permission.id, permission.name)
            return redirect(url_for("permission.index"))
        except IntegrityError:
            db.session.rollback()
            flash("A Permission with that name already exists.", "danger")
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error creating permission")
            flash("An error occurred while creating the permission. Please try again.", "danger")

    return render_template("permission/create.html", form=form,
                           title="Create Permission")


@permission_bp.route("/update/<permission_id>", methods=["GET", "POST"])
@login_required
@permission_required("permission:update")
def update(permission_id):
    """
    View for updating an existing permission.
    """
    permission = Permission.query.get_or_404(permission_id)
    form = UpdatePermissionForm(obj=permission)
    _populate_resource_choices(form)

    if request.method == "GET":
        # Pre-select the current resource in the dropdown (obj= only handles simple attrs)
        form.resource.data = permission.resource

    if form.validate_on_submit():
        resource = form.resource.data.strip()

        permission.name = resource + ":" + form.action.data.strip()
        permission.resource = resource
        permission.action = form.action.data.strip()

        try:
            db.session.commit()
            flash(f"Permission '{permission.name}' updated successfully.", "success")
            logger.info("Permission updated: id=%s", permission.id)
            return redirect(url_for("permission.index"))
        except IntegrityError:
            db.session.rollback()
            flash("A Permission with that name already exists.", "danger")
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error updating permission id=%s", permission_id)
            flash("An error occurred while updating the permission. Please try again.", "danger")

    return render_template("permission/update.html", form=form, permission=permission,
                           title=f"Update Permission: {permission.name}")


@permission_bp.route("/delete/<permission_id>", methods=["GET", "POST"])
@login_required
@permission_required("permission:delete")
def delete(permission_id):
    """
    View for deleting a permission. Blocked if the permission still has
    roles linked to it.
    """
    permission = Permission.query.get_or_404(permission_id)

    assignment_count = len(permission.role_permissions)
    has_dependencies = any([assignment_count])

    form = DeleteForm()

    if form.validate_on_submit():
        if has_dependencies:
            flash(
                f"Cannot delete '{permission.name}': it still has "
                f"{assignment_count} Assignment(s) linked to it. "
                "Reassign these first.", "danger")
            return redirect(url_for("permission.delete", permission_id=permission_id))

        try:
            db.session.delete(permission)
            db.session.commit()
            flash(f"Permission '{permission.name}' deleted successfully.", "success")
            logger.info("Permission deleted: id=%s", permission_id)
            return redirect(url_for("permission.index"))
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error deleting permission id=%s", permission_id)
            flash("An error occurred while deleting the permission. Please try again.", "danger")

    return render_template(
        "permission/delete.html",
        form=form,
        permission=permission,
        assignment_count=assignment_count,
        has_dependencies=has_dependencies,
        title=f"Delete Permission: {permission.name}"
    )


# End of file
