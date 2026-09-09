"""
app/routes/role.py - Defines routes related to role management.
"""

import logging

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Role, Permission, RolePermission
from app.forms import (
    CreateRoleForm, UpdateRoleForm, DeleteForm
)
from app.utils.decorators import permission_required

logger = logging.getLogger(__name__)

role_bp = Blueprint("role", __name__, url_prefix="/role",
                      template_folder="../templates/role")


def _permission_choices():
    """
    Build (id, label) choices for the permissions field.
    Sorted by resource/action so a flat list at least reads in a stable,
    predictable order even without grouped headers.
    """
    permissions = Permission.query.order_by(Permission.resource, Permission.action).all()
    return [(p.id, f'{p.name} ({p.resource}:{p.action})') for p in permissions]


def _grouped_permissions():
    """
    Return permissions in the same order used by the choice list so the
    templates can group them consistently by resource.
    """
    permissions = Permission.query.order_by(Permission.resource, Permission.action).all()
    grouped = {}
    for p in permissions:
        grouped.setdefault(p.resource, []).append(p)
    return grouped


@role_bp.route("/list", methods=["GET"])
@login_required
@permission_required("role:view")
def index():
    """
    View for listing roles with search, sorting, and pagination.
    """
    page     = request.args.get("page", 1, type=int)
    search   = request.args.get("s", "", type=str).strip()
    sort     = request.args.get("sort", "", type=str)
    dir_     = request.args.get("dir", "asc", type=str)
    per_page = request.args.get("per_page", 25, type=int)
    if per_page not in (25, 35, 50):
        per_page = 25

    query = Role.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(Role.name.ilike(like),)
        )

    sort_map = {
        "name": Role.name,
    }
    sort_col = sort_map.get(sort, Role.name)  # default order
    if dir_ == "desc":
        sort_col = sort_col.desc()

    paged = query.order_by(sort_col).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "role/list.html",
        roles=paged,
        search=search,
        sort=sort,
        dir=dir_,
        per_page=per_page,
        title="Roles",
    )


@role_bp.route("/details/<int:role_id>", methods=["GET"])
@login_required
@permission_required("role:view")
def details(role_id):
    """
    View the details of an existing role.
    """
    role = Role.query.get_or_404(role_id)

    return render_template("role/details.html", role=role,
                           title=f"Role Details: {role.name}")


@role_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required("role:create")
def create():
    """
    View for creating a new role.
    """
    form = CreateRoleForm()
    form.permissions.choices = _permission_choices()

    if form.validate_on_submit():
        if Role.query.filter_by(name=form.name.data).first():
            flash('A role with that name already exists.', 'danger')
            return render_template(
                'role/create.html',
                form=form,
                title="Create Role",
                role=None,
                permissions_grouped=_grouped_permissions(),
            )

        role = Role(
            name=form.name.data.strip(),
            description=form.description.data.strip()
        )
        for permission_id in form.permissions.data:
            role.role_permissions.append(RolePermission(permission_id=permission_id))

        db.session.add(role)

        try:
            db.session.commit()
            flash(f"Role '{role.name}' created successfully.", "success")
            logger.info("Role created: id=%s name=%s", role.id, role.name)
            return redirect(url_for("role.index"))
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error creating role")
            flash("An error occurred while creating the role. Please try again.", "danger")

    return render_template(
        "role/create.html",
        form=form,
        title="Create Role",
        role=None,
        permissions_grouped=_grouped_permissions(),
        # selected_permissions=selected_permissions,
        # current_permission_ids=[],
    )


@role_bp.route("/update/<int:role_id>", methods=["GET", "POST"])
@login_required
@permission_required("role:update")
def update(role_id):
    """
    View for updating an existing role.
    """
    role = Role.query.get_or_404(role_id)
    form = UpdateRoleForm(obj=role)
    form.permissions.choices = _permission_choices()

    if request.method == "GET":
        # Pre-select the current resource in the dropdown (obj= only handles simple attrs)
        form.permissions.data = [rp.permission_id for rp in role.role_permissions]

    if form.validate_on_submit():
        existing = Role.query.filter(
            Role.name == form.name.data, Role.id != role.id
        ).first()
        if existing:
            flash('A role with that name already exists.', 'danger')
            return render_template(
                'role/update.html',
                form=form,
                role=role,
                title=f"Update Role: {role.name}",
                permissions_grouped=_grouped_permissions(),
                # selected_permissions=selected_permissions,
                # current_permission_ids=current_permission_ids,
            )

        role.name = form.name.data.strip()
        role.description = form.description.data.strip()
        role.is_active = form.is_active.data

        # Diff the permission set: keep what's still selected, drop what
        # isn't, add what's new. cascade="all, delete-orphan" on
        # Role.role_permissions handles deleting the orphaned rows.
        selected_ids = set(form.permissions.data)
        role.role_permissions = [
            rp for rp in role.role_permissions if rp.permission_id in selected_ids
        ]
        current_ids = {rp.permission_id for rp in role.role_permissions}
        for permission_id in selected_ids - current_ids:
            role.role_permissions.append(RolePermission(permission_id=permission_id))

        try:
            db.session.commit()
            flash(f"Role '{role.name}' updated successfully.", "success")
            logger.info("Role updated: id=%s", role.id)
            return redirect(url_for("role.index"))
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error updating role id=%s", role_id)
            flash("An error occurred while updating the role. Please try again.", "danger")

    return render_template(
        "role/update.html",
        form=form,
        role=role,
        title=f"Update Role: {role.name}",
        permissions_grouped=_grouped_permissions(),
    )


@role_bp.route("/delete/<int:role_id>", methods=["GET", "POST"])
@login_required
@permission_required("role:delete")
def delete(role_id):
    """
    View for deleting a role. Blocked if the role still has
    users linked to it.
    """
    role = Role.query.get_or_404(role_id)

    user_count = len(role.users)
    permission_count = len(role.role_permissions)
    has_dependencies = any([user_count, permission_count])

    form = DeleteForm()

    if form.validate_on_submit():
        if has_dependencies:
            flash(
                f"Cannot delete '{role.name}': it still has "
                f"{user_count} User(s) and {permission_count} Permission(s) linked to it. "
                "Reassign these first.", "danger")
            return redirect(url_for("role.delete", role_id=role_id))

        try:
            db.session.delete(role)
            db.session.commit()
            flash(f"Role '{role.name}' deleted successfully.", "success")
            logger.info("Role deleted: id=%s", role_id)
            return redirect(url_for("role.index"))
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error deleting role id=%s", role_id)
            flash("An error occurred while deleting the role. Please try again.", "danger")

    return render_template(
        "role/delete.html",
        form=form,
        role=role,
        user_count=user_count,
        permission_count=permission_count,
        has_dependencies=has_dependencies,
        title=f"Delete Role: {role.name}"
    )


# End of file
