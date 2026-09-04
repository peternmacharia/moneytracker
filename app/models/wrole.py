"""
app/models/wrole.py - Role model representing user roles in the system
"""

from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean
from .base import BaseModel, ModelRegistry

if TYPE_CHECKING:
    from .wmember import WorkspaceMember
    from .wrpermission import WorkspaceRolePermission


@ModelRegistry.register
class WorkspaceRole(BaseModel):
    """
    Role model representing user roles in the system
    """
    __tablename__ = "workspace_roles"

    name: Mapped[str]                   = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None]     = mapped_column(Text)
    is_active: Mapped[bool]             = mapped_column(Boolean, default=True)

    # Relationships
    members: Mapped[list["WorkspaceMember"]]            = relationship(back_populates="wrole")
    wrole_permissions: Mapped[list["WorkspaceRolePermission"]]  = relationship(back_populates="wrole",
                                                                               cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Role {self.name!r}>'


    # Model properties
    @property
    def permissions(self):
        """
        Return list of Permission objects
        """
        return [
            rp.permission
            for rp in self.role_permissions
        ]

    @property
    def permission_names(self):
        """
        Return set of permission names (fast lookup)
        """
        return {
            rp.permission.name
            for rp in self.role_permissions
        }


    # Check permission at role level
    def has_permission(self, permission_name: str) -> bool:
        """
        Check permission at role level
        """
        return permission_name in self.permission_names

    @property
    def user_count(self):
        """
        Get the number of users for the role.
        """
        return len(self.users)

    @property
    def permission_count(self):
        """
        Get the number of permissions for the role.
        """
        return len(self.role_permissions)


# End of file
