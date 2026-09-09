"""
app/models/enums.py - All application enumerations.
"""

from enum import Enum

# ---------------------------------------------------------------------------
# Auditlog
# ---------------------------------------------------------------------------
class ActorType(str, Enum):
    """
    Who or what triggered the action.
    """
    USER   = "user"    # authenticated human user
    SYSTEM = "system"  # background job / scheduler / internal process


class NotificationCategory(str, Enum):
    """
    Notification category.
    """
    INFO    = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR   = "error"

# End of file
