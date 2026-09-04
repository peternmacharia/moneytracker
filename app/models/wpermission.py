"""
app/models/wpermission.py - System permission model
"""

from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, ModelRegistry

if TYPE_CHECKING:
    from .wrpermission import WorkspaceRolePermission


@ModelRegistry.register
class WorkspacePermission(BaseModel):
    """
    System permission model
    """
    __tablename__ = "workspace_permissions"

    name: Mapped[str]       = mapped_column(String(50), unique=True, index=True)
    resource: Mapped[str]   = mapped_column(String(50), index=True)
    action: Mapped[str]     = mapped_column(String(50), index=True)

    # Relationships
    wrole_permissions: Mapped[list["WorkspaceRolePermission"]] = relationship(back_populates="wpermission")


    @property
    def assignment_count(self):
        """
        Get the number of assignments for the permission.
        """
        return len(self.role_permissions)


    def __repr__(self):
        return f'<Permission {self.name!r} ({self.resource!r}:{self.action!r})>'


# End of file
