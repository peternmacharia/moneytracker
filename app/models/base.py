"""
app/models/base.py - Base mixin model
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


def _uuid() -> str:
    """
    A function to generate string UUID primary keys
    """
    return str(uuid.uuid4().hex)


def utc_now() -> datetime:
    """
    A function to return the current date and time
    using the utc timezone
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_utc_naive(dt: datetime) -> datetime:
    """Convert any datetime to naive UTC; pass naive values through unchanged."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


class BaseModel(db.Model):
    """
    A mixin class for adding timestamp fields to models
    """
    __abstract__ = True

    id: Mapped[str]                         = mapped_column(String(36), primary_key=True, default=_uuid,
                                                            index=True)
    created_at: Mapped[datetime]  = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime]  = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class ModelRegistry:
    """
    Registry for tracking available models in the application
    """
    _models = set()

    @classmethod
    def register(cls, model_class):
        """
        Register a model class
        """
        cls._models.add(model_class.__name__.lower())
        return model_class  # Return the class to allow use as a decorator

    @classmethod
    def get_available_models(cls):
        """
        Get the list of registered model names
        """
        return sorted(list(cls._models))


# End of file
