"""
app/main.py - Defines the main application routes, including the dashboard and public-facing pages.
"""

from datetime import datetime, timezone
from typing import Dict
from flask import (Blueprint, render_template, request)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from app.models import (User)
from app.models.enums import ActorType

# main_bp = Blueprint("main", __name__,)
admin_main_bp = Blueprint("admin_main", __name__, template_folder="../templates/admin/")


# ── Public routes ────────────────────────────────────────────────────────
@admin_main_bp.route("/dashboard")
@login_required
def dashboard() -> str:
    """
    The admin dashboard page.
    Displays key metrics and recent activity.
    
    Returns:
        str: Rendered dashboard template
    """
    return render_template("admin/dashboard.html", title="Dashboard", today=datetime.now(timezone.utc))
    # # Get recent assets
    # recent_assets = (Asset.query
    #                  .order_by(Asset.created_at.desc())
    #                  .limit(5)
    #                  .all())

    # # Get counts efficiently using one query per table
    # stats: Dict[str, int] = {
    #     "departments": Department.query.count(),
    #     "categories": Category.query.count(),
    #     "subcategories": SubCategory.query.count(),
    #     "active_assets": Asset.query.filter(Asset.is_active == True).count(),
    #     "active_users": User.query.filter(User.is_active == True).count(),
    #     "assignments": Asset.query.filter(Asset.is_assigned == True).count(),
    #     "maintenance": Asset.query.filter(Asset.is_under_maintenance == True).count(),
    #     "disposals": Asset.query.filter(Asset.is_disposed == True).count(),
    #     "softwares": Software.query.count()
    # }

    # # ── Asset count grouped by category, for the chart ──────────────────
    # category_stats = (
    #     Category.query
    #     .outerjoin(Asset, Asset.category_id == Category.id)
    #     .with_entities(Category.name, func.count(Asset.id))
    #     .group_by(Category.id, Category.name)
    #     .order_by(Category.name)
    #     .all()
    # )
    # category_labels = [row[0] for row in category_stats]
    # category_data = [row[1] for row in category_stats]

    # ✅ Log the dashboard view (fixed audit log)
    # try:
    #     AuditLog.log(
    #         action="view_dashboard",
    #         resource_type="dashboard",
    #         user_id=current_user.id,
    #         actor_type=ActorType.USER,
    #         ip_address=request.remote_addr,
    #         user_agent=request.headers.get('User-Agent'),
    #         details={
    #             "stats": stats,
    #             "recent_assets": [asset.id for asset in recent_assets[:3]]
    #         },
    #         commit=True  # Commit immediately or remove for batch commit
    #     )
    # except SQLAlchemyError as e:
    #     # Log error but don't fail the request
    #     print(f"Warning: Failed to log dashboard view: {e}")

    # # ✅ No need for db.session.commit() here - it's a read operation

    # return render_template(
    #     "dashboard.html",
    #     title="Dashboard",
    #     recent_assets=recent_assets,
    #     stats=stats,
    #     category_labels=category_labels,
    #     category_data=category_data,
    #     today=datetime.now(timezone.utc),
    #     DASHBOARD=True
    # )

# End of file
