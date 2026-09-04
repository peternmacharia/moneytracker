"""
app/models/notification.py - Notification model
"""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Boolean, DateTime, Enum, ForeignKey
from app.extensions import db
from .base import ModelRegistry, utc_now

if TYPE_CHECKING:
    from .user import User


@ModelRegistry.register
class Notification(db.Model):
    """
    Notification model.
    """
    __tablename__ = "notifications"

    id: Mapped[int]                         = mapped_column(Integer, primary_key=True,
                                                            autoincrement=True, index=True)
    user_id: Mapped[int]                    = mapped_column(ForeignKey("users.id"),
                                                            index=True)
    workspace_id: Mapped[int]               = mapped_column(ForeignKey("workspaces.id"),
                                                            index=True)
    title: Mapped[str]                      = mapped_column(String(100))
    message: Mapped[str]                    = mapped_column(Text)
    channel: Mapped[str]                    = mapped_column(String(50))
    type: Mapped[str]                       = mapped_column(String(50))
    is_urgent: Mapped[bool]                 = mapped_column(Boolean, default=False)
    is_read: Mapped[bool]                   = mapped_column(Boolean, index=True)
    created_at: Mapped[datetime]            = mapped_column(DateTime, default=utc_now)
    read_at: Mapped[datetime | None]        = mapped_column(DateTime)


    # Relationships
    user: Mapped["User"]                    = relationship(back_populates="notifications")

    def mark_read(self):
        """
        Mark this notification as read. Caller must commit.
        """
        self.is_read = True
        self.read_at = utc_now()

    def mark_unread(self):
        """
        Mark this notification as unread.
        """
        self.is_read = False
        self.read_at = None
    
    @classmethod
    def get_unread_count(cls, user_id: int) -> int:
        """
        Get count of unread notifications for a user.
        """
        return cls.query.filter_by(user_id=user_id, is_read=False).count()

    @classmethod
    def mark_all_read(cls, user_id: int) -> int:
        """
        Mark all notifications as read for a user.
        """
        return cls.query.filter_by(user_id=user_id, is_read=False).update(
            {"is_read": True, "read_at": utc_now()}
        )


    def __repr__(self):
        return f"<Notification {self.title!r} read={self.is_read!r}>"

# End of file