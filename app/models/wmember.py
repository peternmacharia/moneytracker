"""
app/models/wmember.py - WorkspaceMember model representing members of workspaces in the system
"""

from typing import TYPE_CHECKING, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, ForeignKey
from .base import BaseModel, ModelRegistry

if TYPE_CHECKING:
    from .user import User
    from .workspace import Workspace
    from .wrole import WorkspaceRole


@ModelRegistry.register
class WorkspaceMember(BaseModel):
    """
    WorkspaceMember model representing members of workspaces in the system
    """
    __tablename__ = "workspace_members"

    workspace_id: Mapped[str]           = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"),
                                                        index=True)
    user_id: Mapped[str]                = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),
                                                        index=True)
    role_id: Mapped[str]                = mapped_column(ForeignKey("workspace_roles.id"))

    # Relationships
    workspace: Mapped["Workspace"]      = relationship(back_populates="members")
    user: Mapped["User"]                = relationship(back_populates="memberships")
    wrole: Mapped["WorkspaceRole"]       = relationship(back_populates="members")


    def __repr__(self):
        return f'<WorkspaceMember {self.user_id!r} - {self.workspace_id!r}>'


# End of file
