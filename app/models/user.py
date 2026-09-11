"""
User model class defination file
"""

from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING, List
import secrets
import pyotp
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .base import BaseModel, utc_now, to_utc_naive

if TYPE_CHECKING:
    from .role import Role
    from .notification import Notification
    from .workspace import Workspace
    from .wmember import WorkspaceMember


class User(UserMixin, BaseModel):
    """
    User model defination
    """
    __tablename__ = "users"

    email: Mapped[str]                              = mapped_column(String(200), unique=True,
                                                                    index=True)
    password_hash: Mapped[str]                      = mapped_column(String(256))
    firstname: Mapped[str]                          = mapped_column(String(50))
    lastname: Mapped[str]                           = mapped_column(String(50))
    country: Mapped[str]                            = mapped_column(String(50))
    currency: Mapped[str]                           = mapped_column(String(3))
    timezone: Mapped[str]                           = mapped_column(String(50), default="UTC")
    avatar_url: Mapped[str | None]                  = mapped_column(Text)
    role_id: Mapped[str]                            = mapped_column(ForeignKey("roles.id"))
    last_login: Mapped[DateTime | None]             = mapped_column(DateTime)
    last_logout: Mapped[DateTime | None]            = mapped_column(DateTime)
    login_count: Mapped[int | None]                 = mapped_column(Integer, default=0)
    password_changed_at: Mapped[DateTime | None]    = mapped_column(DateTime)
    password_reset_token: Mapped[str | None]        = mapped_column(String(256))
    password_reset_expires_at: Mapped[DateTime | None]= mapped_column(DateTime)
    is_email_verified: Mapped[bool]                 = mapped_column(Boolean, default=False)
    email_verification_token: Mapped[str | None]    = mapped_column(String(256))
    email_verification_expires_at: Mapped[DateTime | None] = mapped_column(DateTime)
    email_verified_at: Mapped[DateTime | None]      = mapped_column(DateTime)
    is_active: Mapped[bool]                         = mapped_column(Boolean, default=True)
    is_locked: Mapped[bool]                         = mapped_column(Boolean, default=False)
    locked_until: Mapped[DateTime | None]           = mapped_column(DateTime)
    lock_reason: Mapped[str | None]                 = mapped_column(String(255))
    locked_by: Mapped[int | None]                   = mapped_column(ForeignKey("users.id"))
    locked_at: Mapped[DateTime | None]              = mapped_column(DateTime)
    failed_login_attempts: Mapped[int | None]       = mapped_column(Integer, default=0)
    last_failed_login_at: Mapped[DateTime | None]   = mapped_column(DateTime)
    mfa_enabled: Mapped[bool]                       = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[str | None]                  = mapped_column(String(36))

    # Relationships
    role: Mapped["Role"]                            = relationship(back_populates="users")

    # Reference to other models for back_populates
    notifications: Mapped[list["Notification"]]     = relationship(back_populates="user")
    workspaces: Mapped[List["Workspace"]]           = relationship(back_populates="owner",
                                                                   cascade="all, delete-orphan")
    memberships: Mapped[List["WorkspaceMember"]]    = relationship(back_populates="user",
                                                                   cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email!r}>"

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def fullname(self):
        """
        Convenience property to get the user's full name.
        """
        return f"{self.firstname} {self.lastname}"
    
    @property
    def log_count(self):
        """
        Get the number of logs for the user.
        """
        return len(self.auditlogs)

    @property
    def is_account_locked(self) -> bool:
        """
        Check if the account is currently locked.
        Returns True if locked and lock period hasn't expired.
        """
        if not self.is_locked or self.locked_until is None:
            return False

        now = utc_now()
        locked_until_aware = self.locked_until
        if locked_until_aware.tzinfo is None:
            locked_until_aware = locked_until_aware.replace(tzinfo=timezone.utc)
 
        if now < locked_until_aware:
            return True
 
        # Lock period has expired — auto-unlock.
        self.unlock_account()
        # Note: Need to commit in the calling function
        return False

    @property
    def lock_time_remaining(self) -> int | None:
        """
        Get remaining lock time in minutes.
        Returns None if account is not locked or no expiration.
        """
        if not self.is_locked or self.locked_until is None:
            return None

        now = utc_now()
        locked_until_aware = self.locked_until
        if locked_until_aware.tzinfo is None:
            locked_until_aware = locked_until_aware.replace(tzinfo=timezone.utc)
 
        if now >= locked_until_aware:
            return 0
        # max(1, ...) avoids showing "0 minutes" when under 60s remain.
        return max(1, (locked_until_aware - now).seconds // 60)


    # ------------------------------------------------------------------
    # Password management methods
    # ------------------------------------------------------------------
    def set_password(self, password: str) -> None:
        """
        A function to set a user password (hashes the password)
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        A function to check a user password (compares the hash)
        """
        return check_password_hash(self.password_hash, password)


    # ------------------------------------------------------------------
    # Two-factor authentication methods
    # ------------------------------------------------------------------
    def generate_totp_secret(self) -> str:
        """
        Generate and store a new TOTP secret for this user.
        """
        self.mfa_secret = pyotp.random_base32()
        return self.mfa_secret

    def get_totp_uri(self, issuer: str = "MoneyTracker") -> str:
        """
        Build the otpauth:// URI used to render the QR code.
        Generates a secret first if one doesn't exist yet.
        """
        if not self.mfa_secret:
            self.generate_totp_secret()
        return pyotp.TOTP(self.mfa_secret).provisioning_uri(
            name=self.email, issuer_name=issuer
        )

    def verify_totp(self, code: str) -> bool:
        """
        Verify a 6-digit TOTP code against the stored secret.
        """
        if not self.mfa_secret:
            return False
        return pyotp.TOTP(self.mfa_secret).verify(code, valid_window=1)


    # ------------------------------------------------------------------
    # Account status methods
    # ------------------------------------------------------------------
    def is_valid_account(self) -> bool:
        """
        Check if the account is active and email is verified
        """
        return self.is_active and self.is_email_verified


    # ------------------------------------------------------------------
    # Account lock/unlock methods
    # ------------------------------------------------------------------
    def lock_account(self, reason: str = None, locked_by_user_id: int = None,
                     duration_minutes: int = 10) -> None:
        """
        Lock the user account with an optional reason and duration.
        
        Args:
            reason: Reason for locking the account (optional)
            locked_by_user_id: ID of the user who locked the account (optional)
            duration_minutes: Duration to lock the account in minutes (default: 10)
        """
        self.is_locked = True
        self.locked_until = utc_now() + timedelta(minutes=duration_minutes)
        self.lock_reason = reason
        self.locked_by = locked_by_user_id
        self.locked_at = utc_now()

    def unlock_account(self, unlocked_by_user_id: int = None) -> None:
        """
        Unlock the account by resetting the lock status and failed login attempts.
        
        Args:
            unlocked_by_user_id: ID of the user who unlocked the account (optional)
        """
        self.is_locked = False
        self.locked_until = None
        self.lock_reason = None
        self.locked_by = None
        self.locked_at = None
        self.failed_login_attempts = 0
        self.last_failed_login_at = None

    def record_failed_login(self) -> None:
        """
        Record a failed login attempt by incrementing the failed login attempts
        and updating the last failed login timestamp.
        """
        self.failed_login_attempts = (self.failed_login_attempts or 0) + 1
        self.last_failed_login_at = utc_now()

        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account(
                reason=f"Account locked due to {self.failed_login_attempts} failed login attempts",
                duration_minutes=10
            )

    def record_login(self) -> None:
        """
        Record a successful login attempt by updating the last login timestamp,
        incrementing the login count, and resetting failed login attempts.
        """
        self.last_login = utc_now()
        self.login_count = (self.login_count or 0) + 1
        self.failed_login_attempts = 0
        self.last_failed_login_at = None

        # Unlock account if it was temporarily locked and lock period has expired
        if self.is_locked and self.locked_until is not None:
            now = utc_now()
            if self.locked_until.tzinfo is None:
                locked_until_aware = self.locked_until.replace(tzinfo=timezone.utc)
            else:
                locked_until_aware = self.locked_until
            if now >= locked_until_aware:
                self.unlock_account()

    # ------------------------------------------------------------------
    # Authentication and authorization methods
    # ------------------------------------------------------------------
    def has_role(self, *role_name) -> bool:
        """
        Check if user has any of the specified roles
        """
        if not self.role:
            return False
        return self.role.name in role_name

    def has_permission(self, permission_name: str) -> bool:
        """
        Check if user has a given permission
        """
        if not self.is_authenticated or not self.role:
            return False
        return permission_name in {
            rp.permission.name for rp in self.role.role_permissions
        }

    def list_permissions(self) -> list[str]:
        """
        List all permissions the user has (for display purposes)
        """
        if not self.role:
            return []
        return sorted(self.role.permission_names)


    # ------------------------------------------------------------------
    # Token management and verification methods
    # ------------------------------------------------------------------
    def _token_valid(self, token: str, stored_token: str | None,
                     expires_at: datetime | None) -> bool:
        """Check token match and expiry. Safe against naive/aware mismatches."""
        return bool(
            stored_token and
            expires_at and
            secrets.compare_digest(stored_token, token) and
            utc_now() < to_utc_naive(expires_at)
        )
    
    
    def generate_password_reset_token(self) -> str:
        """
        Generates a token to be used for password reset
        """
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_expires_at = utc_now() + timedelta(hours=1)
        return self.password_reset_token

    def verify_password_reset_token(self, token: str) -> bool:
        """Verify a password-reset token and return True if valid, False otherwise."""
        return self._token_valid(
            token,
            self.password_reset_token,
            self.password_reset_expires_at,
        )

    def clear_password_reset_token(self) -> None:
        """
        Clear the password reset token and its expiration time.
        """
        self.password_reset_token = None
        self.password_reset_expires_at = None

    def generate_email_verification_token(self) -> str:
        """
        Generates a token to be used for email verification
        """
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_expires_at = utc_now() + timedelta(hours=24)
        return self.email_verification_token

    def verify_email_verification_token(self, token: str) -> bool:
        """Verify an email-verification token and return True if valid, False otherwise."""
        if not self._token_valid(
            token,
            self.email_verification_token,
            self.email_verification_expires_at,
        ):
            return False

        self.is_email_verified = True
        self.email_verified_at = utc_now()
        self.email_verification_token = None
        self.email_verification_expires_at = None
        return True


# End of file
