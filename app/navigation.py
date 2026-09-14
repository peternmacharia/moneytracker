"""
app/navigation.py
This module defines the navigation structure for the application, including sidebar groups and their corresponding links.
Each group contains a label, an icon, a collapse ID for toggling visibility, and a list of links. Each link has a label,
an endpoint for routing, an icon, and an optional permission requirement.
"""

PUBLIC_SIDEBAR_ITEMS = [
    {"type": "link", "label": "Dashboard", "endpoint": "public_main.dashboard", "icon": "bi-speedometer2"},

    {"type": "workspace_groups"},

    {
        "type": "group",
        "label": "Access Control", "icon": "bi-shield-lock", "collapse_id": "accessSubmenu",
        "links": [
            {"label": "Users",       "endpoint": "user.index",       "icon": "bi-person-lines-fill", "perm": "user:view"},
            {"label": "Roles",       "endpoint": "role.index",       "icon": "bi-person-gear",       "perm": "role:view"},
            {"label": "Permissions", "endpoint": "permission.index", "icon": "bi-lock",              "perm": "permission:view"},
        ],
    },

    {"type": "link", "label": "Notifications", "endpoint": "", "icon": "bi-bell"},
]



ADMIN_SIDEBAR_ITEMS = [
    {"type": "link", "label": "Dashboard", "endpoint": "admin_main.dashboard", "icon": "bi-speedometer2"},

    {
        "type": "group",
        "label": "People & Org", "icon": "bi-buildings", "collapse_id": "orgSubmenu",
        "links": [
            {"label": "Organization", "endpoint": "",        "icon": "bi-buildings", "perm": "organization:view"},
            {"label": "Departments",  "endpoint": "", "icon": "bi-building",  "perm": "department:view"},
            {"label": "Employees",    "endpoint": "",   "icon": "bi-people",    "perm": "employee:view"},
        ],
    },

    {
        "type": "group",
        "label": "Access Control", "icon": "bi-shield-lock", "collapse_id": "accessSubmenu",
        "links": [
            {"label": "Users",       "endpoint": "user.index",       "icon": "bi-person-lines-fill", "perm": "user:view"},
            {"label": "Roles",       "endpoint": "role.index",       "icon": "bi-person-gear",       "perm": "role:view"},
            {"label": "Permissions", "endpoint": "permission.index", "icon": "bi-lock",              "perm": "permission:view"},
        ],
    },
    
    {"type": "link", "label": "Notifications", "endpoint": "", "icon": "bi-bell"},
]