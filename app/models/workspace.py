"""
app/models/workspace.py - Workspace model representing workspaces in the system
"""

from typing import TYPE_CHECKING, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, ForeignKey
from .base import BaseModel, ModelRegistry

if TYPE_CHECKING:
    from .user import User
    from .wmember import WorkspaceMember


@ModelRegistry.register
class Workspace(BaseModel):
    """
    Workspace model representing workspaces in the system
    """
    __tablename__ = "workspaces"

    owner_id: Mapped[str]               = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),
                                                        index=True)
    name: Mapped[str]                   = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None]     = mapped_column(Text)
    is_active: Mapped[bool]             = mapped_column(Boolean, default=True)
    is_shareable: Mapped[bool]          = mapped_column(Boolean, default=False)

    # Relationships
    owner: Mapped["User"]               = relationship(back_populates="workspaces")
    members: Mapped[List["WorkspaceMember"]] = relationship(back_populates="workspace",
                                                            cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Role {self.name!r}>'


# End of file
