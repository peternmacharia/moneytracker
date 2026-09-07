"""
app/models/auditlog.py - This module defines the AuditLog model, which provides an
                        immutable audit trail for all significant system events.

This file was already structurally sound — no changes were needed here.
The bug (and its fix) lives in auditmixin.py. Included here so you have a
complete, matching set of files.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional, Any, Dict
from flask import request, g, has_request_context

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, JSON, Enum as SAEnum, ForeignKey, DateTime, Index
from app.extensions import db
from .base import ModelRegistry, utc_now
from .enums import ActorType
from .auditmixin import serialize_for_audit, make_json_safe

if TYPE_CHECKING:
    from .user import User


@ModelRegistry.register
class AuditLog(db.Model):
    """
    Model representing an audit log entry for tracking user actions and system events.
    """
    __tablename__ = "auditlogs"

    # Primary columns
    id: Mapped[int]                     = mapped_column(Integer, primary_key=True,
                                                        autoincrement=True, index=True)
    user_id: Mapped[int | None]         = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    actor_type: Mapped[ActorType]       = mapped_column(SAEnum(ActorType), index=True)
    action: Mapped[str]                 = mapped_column(String(100), index=True)
    resource_type: Mapped[str]          = mapped_column(String(50), index=True)
    resource_id: Mapped[int | None]     = mapped_column(Integer, index=True)
    resource_name: Mapped[str | None]   = mapped_column(String(200))
    details: Mapped[dict | None]        = mapped_column(JSON, default=dict)

    # Request context
    ip_address: Mapped[str | None]      = mapped_column(String(45), index=True)
    user_agent: Mapped[str | None]      = mapped_column(String(250))
    session_id: Mapped[str | None]      = mapped_column(String(100), index=True)
    request_id: Mapped[str | None]      = mapped_column(String(100), index=True)

    # Timing and metadata
    timestamp: Mapped[datetime]         = mapped_column(DateTime, default=utc_now, index=True)
    duration_ms: Mapped[int | None]     = mapped_column(Integer)  # For performance monitoring
    is_error: Mapped[bool]              = mapped_column(db.Boolean, default=False)
    error_message: Mapped[str | None]   = mapped_column(String(500))

    # Change tracking for before/after values
    old_values: Mapped[dict | None]     = mapped_column(JSON, default=dict)
    new_values: Mapped[dict | None]     = mapped_column(JSON, default=dict)

    # Relationships
    user: Mapped["User"]                = relationship(foreign_keys=[user_id],
                                                       back_populates="auditlogs")

    def __repr__(self):
        return (
            f"<AuditLog id={self.id!r} action={self.action!r} "
            f"resource={self.resource_type!r}:{self.resource_id!r} "
            f"timestamp={self.timestamp!r}>"
        )

    # --------------------------------------------------------------------------
    # Internal helpers
    # --------------------------------------------------------------------------
    @classmethod
    def _get_request_context(cls) -> Dict[str, Optional[str]]:
        """Extract request context safely without raising RuntimeError."""
        if not has_request_context():
            return {}
        forwarded = request.headers.get('X-Forwarded-For')
        ip = forwarded.split(',')[0].strip() if forwarded else request.remote_addr
        return {
            "ip_address": ip,
            "user_agent": request.headers.get('User-Agent'),
            "session_id": getattr(g, 'session_id', None),
            "request_id": getattr(g, 'request_id', None),
        }

    @classmethod
    def _fetch(cls, *, order_by=None, limit: Optional[int] = None, **filters):
        """Internal helper to reduce query boilerplate."""
        q = cls.query
        if filters:
            q = q.filter_by(**filters)
        q = q.order_by(order_by if order_by is not None else cls.timestamp.desc())
        if limit is not None:
            q = q.limit(limit)
        return q.all()

    # --------------------------------------------------------------------------
    # Class Methods for Logging
    # --------------------------------------------------------------------------
    @classmethod
    def log(
        cls,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        resource_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        actor_type: Optional[ActorType] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        is_error: bool = False,
        error_message: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        commit: bool = False,
    ) -> "AuditLog":
        """
        Create and add an audit log entry to the current session.

        commit: Whether to commit immediately. Defaults to False so the
            entry rides along in whatever transaction is already open —
            pass True for standalone calls outside a request/session
            lifecycle that owns its own commit (CLI scripts, one-off
            background jobs).
        """
        if actor_type is None:
            actor_type = ActorType.SYSTEM if user_id is None else ActorType.USER

        ctx = cls._get_request_context()
        if ip_address is None:
            ip_address = ctx.get("ip_address")
        if user_agent is None:
            user_agent = ctx.get("user_agent")
        if session_id is None:
            session_id = ctx.get("session_id")
        if request_id is None:
            request_id = ctx.get("request_id")

        audit_entry = cls(
            user_id=user_id,
            actor_type=actor_type,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=make_json_safe(details) or {},
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            request_id=request_id,
            duration_ms=duration_ms,
            is_error=is_error,
            error_message=error_message,
            old_values=make_json_safe(old_values) or {},
            new_values=make_json_safe(new_values) or {}
        )

        db.session.add(audit_entry)

        if commit:
            db.session.commit()

        return audit_entry

    @classmethod
    def log_create(cls, resource_type: str, instance: Any,
                   actor_id: Optional[int] = None, **kwargs) -> "AuditLog":
        """Log a resource creation."""
        return cls.log(
            action="create",
            resource_type=resource_type,
            resource_id=instance.id,
            resource_name=getattr(instance, 'audit_resource_name', None) or getattr(instance, 'name', str(instance)),
            new_values=serialize_for_audit(instance),
            user_id=actor_id,
            **kwargs
        )

    @classmethod
    def log_update(cls, resource_type: str, instance: Any, old_state: Dict,
                   actor_id: Optional[int] = None, **kwargs) -> "AuditLog":
        """
        Log a resource update with before/after values. `old_state` should be
        a plain dict snapshot taken before the instance was mutated.
        """
        old_state = make_json_safe(old_state) or {}
        new_state = serialize_for_audit(instance)

        changed_fields = {}
        for key, old_val in old_state.items():
            new_val = new_state.get(key)
            if old_val != new_val:
                changed_fields[key] = {"old": old_val, "new": new_val}

        return cls.log(
            action="update",
            resource_type=resource_type,
            resource_id=instance.id,
            resource_name=getattr(instance, 'audit_resource_name', None) or getattr(instance, 'name', str(instance)),
            old_values=old_state,
            new_values=new_state,
            details={"changed_fields": changed_fields},
            user_id=actor_id,
            **kwargs
        )

    @classmethod
    def log_delete(cls, resource_type: str, instance: Any,
                   actor_id: Optional[int] = None, **kwargs) -> "AuditLog":
        """Log a resource deletion."""
        return cls.log(
            action="delete",
            resource_type=resource_type,
            resource_id=instance.id,
            resource_name=getattr(instance, 'audit_resource_name', None) or getattr(instance, 'name', str(instance)),
            old_values=serialize_for_audit(instance),
            user_id=actor_id,
            **kwargs
        )

    @classmethod
    def log_action(cls, action: str, resource_type: str, resource_id: Optional[int] = None,
                   actor_id: Optional[int] = None, **kwargs) -> "AuditLog":
        """Generic action logger for non-CRUD operations."""
        return cls.log(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=actor_id,
            **kwargs
        )

    @classmethod
    def log_error(cls, action: str, resource_type: str, error: Exception,
                  resource_id: Optional[int] = None, actor_id: Optional[int] = None,
                  **kwargs) -> "AuditLog":
        """Log an error that occurred during an action."""
        return cls.log(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            is_error=True,
            error_message=str(error),
            details={"error_type": type(error).__name__},
            user_id=actor_id,
            **kwargs
        )

    @classmethod
    def log_security_event(cls, action: str, resource_type: str,
                           resource_id: Optional[int] = None,
                           actor_id: Optional[int] = None,
                           ip_address: Optional[str] = None,
                           **kwargs) -> "AuditLog":
        """Log a security-related event (login, logout, permission change, etc.)."""
        return cls.log(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address or cls._get_request_context().get("ip_address"),
            actor_type=ActorType.USER,
            user_id=actor_id,
            **kwargs
        )

    @classmethod
    def log_system_event(cls, action: str, resource_type: str,
                         details: Optional[Dict] = None, **kwargs) -> "AuditLog":
        """Log a system-level event (background job, scheduler, etc.)."""
        return cls.log(
            action=action,
            resource_type=resource_type,
            actor_type=ActorType.SYSTEM,
            details=details,
            **kwargs
        )

    # --------------------------------------------------------------------------
    # Query Methods
    # --------------------------------------------------------------------------
    @classmethod
    def get_by_resource(cls, resource_type: str, resource_id: int) -> list["AuditLog"]:
        return cls._fetch(resource_type=resource_type, resource_id=resource_id)

    @classmethod
    def get_by_user(cls, user_id: int, limit: int = 100) -> list["AuditLog"]:
        return cls._fetch(user_id=user_id, limit=limit)

    @classmethod
    def get_by_action(cls, action: str, limit: int = 100) -> list["AuditLog"]:
        return cls._fetch(action=action, limit=limit)

    @classmethod
    def get_recent(cls, limit: int = 100) -> list["AuditLog"]:
        return cls._fetch(limit=limit)

    @classmethod
    def get_by_date_range(cls, start_date: datetime, end_date: datetime) -> list["AuditLog"]:
        return cls.query.filter(
            cls.timestamp >= start_date,
            cls.timestamp <= end_date
        ).order_by(cls.timestamp.desc()).all()

    @classmethod
    def get_errors(cls, limit: int = 50) -> list["AuditLog"]:
        return cls._fetch(is_error=True, limit=limit)

    @classmethod
    def get_security_events(cls, limit: int = 50) -> list["AuditLog"]:
        security_actions = ['login', 'logout', 'login_failed', 'password_change',
                           'permission_change', 'role_assignment', 'role_revocation']
        return cls.query.filter(cls.action.in_(security_actions))\
                   .order_by(cls.timestamp.desc())\
                   .limit(limit).all()

    # --------------------------------------------------------------------------
    # Utility Methods
    # --------------------------------------------------------------------------
    @classmethod
    def get_user_activity_report(cls, user_id: int, start_date: datetime, end_date: datetime):
        return cls.query.filter(
            cls.user_id == user_id,
            cls.timestamp >= start_date,
            cls.timestamp <= end_date
        ).order_by(cls.timestamp.asc()).all()

    # --------------------------------------------------------------------------
    # Context Manager for Automatic Logging
    # --------------------------------------------------------------------------
    @classmethod
    def log_context(cls, action: str, resource_type: str,
                    resource_id: Optional[int] = None, **kwargs):
        """
        Usage:
            with AuditLog.log_context('bulk_import', 'asset', user_id=current_user.id):
                bulk_import_assets(data)
        """
        return _AuditLogContext(cls, action, resource_type, resource_id, **kwargs)


class _AuditLogContext:
    """Context manager for audit logging with duration tracking."""
    def __init__(self, log_class, action, resource_type, resource_id, **kwargs):
        self.log_class = log_class
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.kwargs = kwargs
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = int((datetime.now() - self.start_time).total_seconds() * 1000)

        if exc_type:
            self.log_class.log_error(
                action=self.action,
                resource_type=self.resource_type,
                resource_id=self.resource_id,
                error=exc_val,
                duration_ms=duration_ms,
                **self.kwargs
            )
        else:
            self.log_class.log(
                action=self.action,
                resource_type=self.resource_type,
                resource_id=self.resource_id,
                duration_ms=duration_ms,
                **self.kwargs
            )


# --------------------------------------------------------------------------
# Convenience functions for use in views and services
# --------------------------------------------------------------------------
def log_user_login(user_id: int, success: bool = True,
                   ip_address: Optional[str] = None) -> AuditLog:
    """Log a user login attempt."""
    action = "login_success" if success else "login_failed"
    return AuditLog.log_security_event(
        action=action,
        resource_type="user",
        resource_id=user_id,
        actor_id=user_id if success else None,
        ip_address=ip_address,
        details={"success": success}
    )


def log_user_logout(user_id: int) -> AuditLog:
    """Log a user logout."""
    return AuditLog.log_security_event(
        action="logout",
        resource_type="user",
        resource_id=user_id,
        actor_id=user_id
    )


def log_password_change(user_id: int, changed_by: Optional[int] = None) -> AuditLog:
    """
    Log a password change. Use this alongside (not instead of) AuditMixin's
    automatic tracking on User — this call records *intent* (self-service
    change vs. admin reset), which the generic field-diff can't distinguish.
    """
    return AuditLog.log_security_event(
        action="password_change",
        resource_type="user",
        resource_id=user_id,
        actor_id=changed_by or user_id
    )


def log_permission_change(user_id: int, role_id: int, action: str, changed_by: int) -> AuditLog:
    """Log a permission or role change."""
    return AuditLog.log_security_event(
        action=action,
        resource_type="role_permission",
        resource_id=role_id,
        actor_id=changed_by,
        details={"target_user": user_id, "role_id": role_id}
    )


def log_asset_transaction(asset_id: int, action: str, user_id: int,
                          details: Optional[Dict] = None) -> AuditLog:
    """Log an asset-related transaction."""
    return AuditLog.log_action(
        action=action,
        resource_type="asset",
        resource_id=asset_id,
        actor_id=user_id,
        details=details
    )


# End of file
