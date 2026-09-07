"""
app/models/auditmixin.py: A mixin for auditing model changes.

"""

from datetime import datetime, date, time, timedelta
from uuid import UUID
from enum import Enum
from decimal import Decimal
from typing import Optional, Any, Dict

from flask import logging
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from flask import has_request_context, logging
from flask_login import current_user

from app.models.enums import ActorType

logger = logging.getLogger(__name__)

MASK_VALUE = "***REDACTED***"


def serialize_audit_value(value: Any) -> Any:
    """Convert a single value to a JSON-safe type for audit storage."""
    if value is None:
        return None
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, timedelta):
        return value.total_seconds()
    if isinstance(value, Decimal):
        return str(value)  # preserves exact precision; float() would not
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, UUID):
        return str(value)
    if hasattr(value, "__table__"):
        # A related model instance slipped in (e.g. a relationship
        # attribute) — never dump a whole related row into the audit log.
        return f"<{type(value).__name__} id={getattr(value, 'id', '?')}>"
    return value


def make_json_safe(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Recursively convert dict values to JSON-safe types."""
    if not data:
        return data
    result: Dict[str, Any] = {}
    for k, v in data.items():
        if isinstance(v, dict):
            result[k] = make_json_safe(v)
        elif isinstance(v, list):
            result[k] = [serialize_audit_value(i) for i in v]
        else:
            result[k] = serialize_audit_value(v)
    return result


def serialize_for_audit(instance: Any, mask_value: str = MASK_VALUE) -> Dict[str, Any]:
    """
    Serialize a model instance's columns for storage in old_values/new_values,
    honoring `audit_exclude` (omit the key entirely) and `audit_mask` (keep
    the key, redact the value) if the instance's class defines them.
    """
    exclude = getattr(instance, "audit_exclude", set())
    mask = getattr(instance, "audit_mask", set())
    result: Dict[str, Any] = {}
    for column in instance.__table__.columns:
        name = column.name
        if name in exclude:
            continue
        value = getattr(instance, name)
        result[name] = mask_value if name in mask else serialize_audit_value(value)
    return result


class AuditMixin:
    """Inherit this on any model whose create/update/delete should be
    auto-logged. No route code needed. Typically inherited once, via
    BaseModel — see base.py — rather than added to each model directly."""
    __auditable__ = True
    audit_exclude: set[str] = set()  # e.g. {"password_hash", "totp_secret"}
    audit_mask: set[str] = set()

    @property
    def audit_resource_name(self) -> str:
        return getattr(self, "name", None) or getattr(self, "title", None) or str(getattr(self, "id", ""))


def _current_actor_id():
    if has_request_context() and current_user and current_user.is_authenticated:
        return current_user.id
    return None


def _get_request_context():
    """Shared helper for request context extraction."""
    if not has_request_context():
        return None, None, None, None
    from flask import request, g
    forwarded = request.headers.get("X-Forwarded-For")
    ip = forwarded.split(',')[0].strip() if forwarded else request.remote_addr
    ua = request.headers.get("User-Agent")
    session_id = getattr(g, "session_id", None)
    request_id = getattr(g, "request_id", None)
    return ip, ua, session_id, request_id


@event.listens_for(Session, "before_flush")
def _snapshot_audit_changes(session, flush_context, instances):
    """
    Capture diffs for new/dirty/deleted auditable objects before they flush.
    resource_id/resource_name for update and delete are captured HERE, not
    in after_flush_postexec — a deleted object can raise ObjectDeletedError
    if you touch its attributes once the DELETE has actually executed, and
    this keeps update/delete handling identical instead of one being safe
    by accident.
    """
    buffer = session.info.setdefault("audit_buffer", [])

    for obj in session.new:
        if getattr(obj, "__auditable__", False):
            # PK doesn't exist yet — resolved in after_flush_postexec.
            buffer.append({"obj": obj, "action": "create"})

    for obj in session.dirty:
        if not getattr(obj, "__auditable__", False):
            continue
        if not session.is_modified(obj, include_collections=False):
            continue

        excl = getattr(obj, "audit_exclude", set())
        mask = getattr(obj, "audit_mask", set())
        old, new, changed = {}, {}, {}

        state = inspect(obj)
        mapper = state.mapper

        for attr in mapper.column_attrs:
            key = attr.key
            if key in excl:
                continue
            hist = state.attrs[key].history
            if not hist.has_changes():
                continue
            if key in mask:
                old_val = new_val = MASK_VALUE
            else:
                old_val = serialize_audit_value(hist.deleted[0] if hist.deleted else None)
                new_val = serialize_audit_value(hist.added[0] if hist.added else getattr(obj, key))
            old[key], new[key] = old_val, new_val
            changed[key] = {"old": old_val, "new": new_val}

        if changed:
            buffer.append({
                "obj": obj, "action": "update",
                "resource_id": obj.id, "resource_name": obj.audit_resource_name,
                "old": old, "new": new, "changed": changed,
            })

    for obj in session.deleted:
        if getattr(obj, "__auditable__", False):
            excl = getattr(obj, "audit_exclude", set())
            old = {
                c.name: serialize_audit_value(getattr(obj, c.name))
                for c in obj.__table__.columns if c.name not in excl
            }
            buffer.append({
                "obj": obj, "action": "delete",
                "resource_id": obj.id, "resource_name": obj.audit_resource_name,
                "old": old,
            })

    if buffer:
        logger.debug("audit: buffered %d change(s) for this flush", len(buffer))


@event.listens_for(Session, "after_flush_postexec")
def _write_audit_rows(session, flush_context):
    buffer = session.info.pop("audit_buffer", [])
    if not buffer:
        return

    # Lazy import inside the handler so the module can load without
    # circular dependencies. By the time this runs, every model is
    # already registered and the import succeeds.
    from app.models.auditlog import AuditLog

    actor_id = _current_actor_id()
    ip, ua, session_id, request_id = _get_request_context()

    for item in buffer:
        obj, action = item["obj"], item["action"]
        resource_type = obj.__tablename__

        try:
            if action == "create":
                # Safe to read obj here — freshly inserted, not expired.
                resource_id = getattr(obj, "id", None)
                resource_name = getattr(obj, "audit_resource_name", None)
                AuditLog.log_create(
                    resource_type=resource_type,
                    instance=obj,
                    actor_id=actor_id,
                    ip_address=ip,
                    user_agent=ua,
                    session_id=session_id,
                    request_id=request_id,
                    commit=False,
                )
            elif action == "update":
                AuditLog.log(
                    action="update",
                    resource_type=resource_type,
                    resource_id=item["resource_id"],
                    resource_name=item["resource_name"],
                    old_values=item.get("old"),
                    new_values=item.get("new"),
                    details={"changed_fields": list(item.get("changed", {}))},
                    actor_type=ActorType.USER if actor_id else ActorType.SYSTEM,
                    user_id=actor_id,
                    ip_address=ip,
                    user_agent=ua,
                    session_id=session_id,
                    request_id=request_id,
                    commit=False,
                )
            elif action == "delete":
                AuditLog.log(
                    action="delete",
                    resource_type=resource_type,
                    resource_id=item["resource_id"],
                    resource_name=item["resource_name"],
                    old_values=item.get("old"),
                    actor_type=ActorType.USER if actor_id else ActorType.SYSTEM,
                    user_id=actor_id,
                    ip_address=ip,
                    user_agent=ua,
                    session_id=session_id,
                    request_id=request_id,
                    commit=False,
                )
            logger.debug("audit: queued %s on %s", action, resource_type)
        except Exception:
            # A bug in audit logging should never take down the actual
            # business transaction — but it should never be invisible
            # either. This is the fix for "audit table is empty and I
            # have no idea why": now it logs instead of vanishing.
            logger.exception("audit: failed to record %s on %s", action, resource_type)


# End of file
