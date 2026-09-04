"""
app/models/role_permission.py - Association model between Role and Permission
"""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, ForeignKey
from app.extensions import db
from .base import ModelRegistry, utc_now

if TYPE_CHECKING:
    from .role import Role
    from .permission import Permission


@ModelRegistry.register
class RolePermission(db.Model):
    """
    Association model between Role and Permission
    """
    __tablename__ = "role_permissions"

    role_id: Mapped[int]                        = mapped_column(ForeignKey("roles.id"),
                                                                primary_key=True, index=True)
    permission_id: Mapped[int]                  = mapped_column(ForeignKey("permissions.id"),
                                                                primary_key=True, index=True)

    # Relationships
    role: Mapped["Role"] = relationship(back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship(back_populates="role_permissions")


# End of file
