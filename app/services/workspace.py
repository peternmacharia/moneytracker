"""
app/services/workspace.py
This module contains functions related to workspaces and their members.
"""

from app.models import Workspace, WorkspaceMember

def get_user_workspaces(user):
    """Workspaces the user owns, unioned with ones shared with them."""
    owned = Workspace.query.filter_by(owner_id=user.id)
    shared = Workspace.query.join(WorkspaceMember).filter(WorkspaceMember.user_id == user.id)
    return owned.union(shared).order_by(Workspace.name).all()


def build_workspace_sidebar_groups(user):
    groups = []
    for ws in get_user_workspaces(user):
        groups.append({
            "type": "group",
            "label": ws.name,
            "icon": "bi-buildings",
            "collapse_id": f"workspace{ws.id}Menu",
            "always_visible": True,
            "links": [
                {"label": "Overview",    "endpoint": "workspace.details",     "icon": "bi-info-circle",
                 "endpoint_params": {"workspace_id": ws.id}},
                {"label": "Income",      "endpoint": "",      "icon": "bi-cash-coin",
                 "endpoint_params": {"workspace_id": ws.id}},
                {"label": "Departments", "endpoint": "", "icon": "bi-building",
                 "endpoint_params": {"workspace_id": ws.id}},
                {"label": "Employees",   "endpoint": "",   "icon": "bi-people",
                 "endpoint_params": {"workspace_id": ws.id}},
            ],
        })
    return groups


# End of file
