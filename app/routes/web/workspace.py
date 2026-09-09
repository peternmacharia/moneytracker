"""
app/routes/workspace.py - Defines routes related to workspace management.
"""

import logging

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Workspace
from app.forms import (
    CreateWorkspaceForm, UpdateWorkspaceForm, DeleteForm
)
from app.utils.decorators import permission_required

logger = logging.getLogger(__name__)

workspace_bp = Blueprint("workspace", __name__, url_prefix="/workspace",
                      template_folder="../templates/workspace")


@workspace_bp.route("/list", methods=["GET"])
@login_required
@permission_required("workspace:view")
def index():
    """
    View for listing workspaces with search, sorting, and pagination.
    """
    page     = request.args.get("page", 1, type=int)
    search   = request.args.get("s", "", type=str).strip()
    sort     = request.args.get("sort", "", type=str)
    dir_     = request.args.get("dir", "asc", type=str)
    per_page = request.args.get("per_page", 25, type=int)
    if per_page not in (25, 35, 50):
        per_page = 25

    query = Workspace.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(Workspace.name.ilike(like),)
        )

    sort_map = {
        "name": Workspace.name,
    }
    sort_col = sort_map.get(sort, Workspace.name)  # default order
    if dir_ == "desc":
        sort_col = sort_col.desc()

    paged = query.order_by(sort_col).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "workspace/list.html",
        workspaces=paged,
        search=search,
        sort=sort,
        dir=dir_,
        per_page=per_page,
        title="Workspaces",
    )


@workspace_bp.route("/details/<int:workspace_id>", methods=["GET"])
@login_required
@permission_required("workspace:view")
def details(workspace_id):
    """
    View the details of an existing workspace.
    """
    workspace = Workspace.query.get_or_404(workspace_id)

    return render_template("workspace/details.html", workspace=workspace,
                           title=f"Workspace Details: {workspace.name}")


@workspace_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required("workspace:create")
def create():
    """
    View for creating a new workspace.
    """
    form = CreateWorkspaceForm()

    if form.validate_on_submit():
        if Workspace.query.filter_by(name=form.name.data, owner_id=current_user.id).first():
            flash('A workspace with that name already exists.', 'danger')
            return render_template("workspace/create.html", form=form, title="Create Workspace",)

        workspace = Workspace(
            owner_id=current_user.id,
            name=form.name.data.strip(),
            description=form.description.data or "None",
            is_shared=form.is_shared.data,
        )

        db.session.add(workspace)

        try:
            db.session.commit()
            flash(f"Workspace '{workspace.name}' created successfully.", "success")
            logger.info("Workspace created: id=%s name=%s", workspace.id, workspace.name)
            return redirect(url_for("workspace.index"))
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error creating workspace")
            flash("An error occurred while creating the workspace. Please try again.", "danger")

    return render_template("workspace/create.html", form=form, title="Create Workspace",)


@workspace_bp.route("/update/<int:workspace_id>", methods=["GET", "POST"])
@login_required
@permission_required("workspace:update")
def update(workspace_id):
    """
    View for updating an existing workspace.
    """
    workspace = Workspace.query.get_or_404(workspace_id)
    form = UpdateWorkspaceForm(obj=workspace)

    if form.validate_on_submit():
        existing = Workspace.query.filter(
            Workspace.name == form.name.data, Workspace.id != workspace.id
        ).first()
        if existing:
            flash('A workspace with that name already exists.', 'danger')
            return render_template(
                "workspace/update.html",
                form=form,
                workspace=workspace,
                title=f"Update Workspace: {workspace.name}",
            )

        workspace.name = form.name.data.strip()
        workspace.description = form.description.data or "None"
        workspace.is_shared = form.is_shared.data
        workspace.is_active = form.is_active.data

        try:
            db.session.commit()
            flash(f"Workspace '{workspace.name}' updated successfully.", "success")
            logger.info("Workspace updated: id=%s", workspace.id)
            return redirect(url_for("workspace.index"))
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error updating workspace id=%s", workspace.id)
            flash("An error occurred while updating the workspace. Please try again.", "danger")

    return render_template(
        "workspace/update.html",
        form=form,
        workspace=workspace,
        title=f"Update Workspace: {workspace.name}",
    )


@workspace_bp.route("/delete/<int:workspace_id>", methods=["GET", "POST"])
@login_required
@permission_required("workspace:delete")
def delete(workspace_id):
    """
    View for deleting a workspace. Blocked if the workspace still has
    users linked to it.
    """
    workspace = Workspace.query.get_or_404(workspace_id)

    user_count = len(workspace.users)
    permission_count = len(workspace.workspace_permissions)
    has_dependencies = any([user_count, permission_count])

    form = DeleteForm()

    if form.validate_on_submit():
        if has_dependencies:
            flash(
                f"Cannot delete '{workspace.name}': it still has "
                f"{user_count} User(s) and {permission_count} Permission(s) linked to it. "
                "Reassign these first.", "danger")
            return redirect(url_for("workspace.delete", workspace_id=workspace.id))

        try:
            db.session.delete(workspace)
            db.session.commit()
            flash(f"Workspace '{workspace.name}' deleted successfully.", "success")
            logger.info("Workspace deleted: id=%s", workspace.id)
            return redirect(url_for("workspace.index"))
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error deleting workspace id=%s", workspace.id)
            flash("An error occurred while deleting the workspace. Please try again.", "danger")

    return render_template(
        "workspace/delete.html",
        form=form,
        workspace=workspace,
        user_count=user_count,
        permission_count=permission_count,
        has_dependencies=has_dependencies,
        title=f"Delete Workspace: {workspace.name}"
    )


# End of file
