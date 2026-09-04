"""
app/models/workspace_role_permission.py - Association model between Workspace Role and Permission
"""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, ForeignKey
from app.extensions import db
from .base import ModelRegistry, utc_now

if TYPE_CHECKING:
    from .wrole import WorkspaceRole
    from .wpermission import WorkspacePermission


@ModelRegistry.register
class WorkspaceRolePermission(db.Model):
    """
    Association model between Workspace Role and Permission
    """
    __tablename__ = "workspace_role_permissions"

    wrole_id: Mapped[str]                        = mapped_column(ForeignKey("workspace_roles.id"),
                                                                primary_key=True, index=True)
    wpermission_id: Mapped[str]                  = mapped_column(ForeignKey("workspace_permissions.id"),
                                                                primary_key=True, index=True)

    # Relationships
    wrole: Mapped["WorkspaceRole"] = relationship(back_populates="wrole_permissions")
    wpermission: Mapped["WorkspacePermission"] = relationship(back_populates="wrole_permissions")

    def __repr__(self):
        return f'<WorkspaceRolePermission {self.wrole_id!r} - {self.wpermission_id!r}>'

# End of file
