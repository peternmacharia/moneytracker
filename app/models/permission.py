"""
app/models/permission.py - System permission model
"""

from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, ModelRegistry

if TYPE_CHECKING:
    from .rpermission import RolePermission


@ModelRegistry.register
class Permission(BaseModel):
    """
    System permission model
    """
    __tablename__ = "permissions"

    name: Mapped[str]       = mapped_column(String(50), unique=True, index=True)
    resource: Mapped[str]   = mapped_column(String(50), index=True)
    action: Mapped[str]     = mapped_column(String(50), index=True)

    # Relationships
    role_permissions: Mapped[list["RolePermission"]] = relationship(back_populates="permission")


    @property
    def assignment_count(self):
        """
        Get the number of assignments for the permission.
        """
        return len(self.role_permissions)


    def __repr__(self):
        return f'<Permission {self.name!r} ({self.resource!r}:{self.action!r})>'


# End of file
