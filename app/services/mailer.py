"""
app/utils/mailer.py - Centralized email-sending helpers, shared by the
auth and admin_users blueprints so email copy/formatting lives in one
place. Token generation and db.session.commit() stay in the calling
route - these functions only format and send.
"""

from flask import url_for
from flask_mail import Message

from app.extensions import mail


def send_email(subject: str, recipient: str, body: str) -> None:
    """
    Send a plain-text email via Flask-Mail.
    Requires MAIL_SERVER / MAIL_USERNAME / MAIL_PASSWORD / MAIL_DEFAULT_SENDER
    to be set in your app config.
    """
    msg = Message(subject=subject, recipients=[recipient], body=body)
    mail.send(msg)


def send_account_invite_email(user, token: str, password: str) -> None:
    """
    Sent once, when an admin creates a new system-user account.
    Contains the email-verification link and the temporary password.
    """
    verify_url = url_for("auth.verify_email", token=token, _external=True)
    send_email(
        subject="Your account has been created",
        recipient=user.email,
        body=(
            f"Hi {user.firstname},\n\n"
            "An account has been created for you. Please verify your email "
            "using the link below, then log in with your password.\n\n"
            f"Verify your account: {verify_url}\n"
            f"Your password: {password}\n\n"
            "If you were not expecting this, please ignore this email."
        ),
    )


def send_verification_email(user, token: str) -> None:
    """
    Sent when a user (or admin) requests a fresh verification link.
    """
    verify_url = url_for("auth.verify_email", token=token, _external=True)
    send_email(
        subject="Verify your account",
        recipient=user.email,
        body=(
            f"Hi {user.firstname},\n\n"
            f"Please verify your account using the link below:\n{verify_url}"
        ),
    )


def send_password_reset_email(user, token: str) -> None:
    """
    Sent for the forgot-password flow.
    """
    reset_url = url_for("auth.reset_password", token=token, _external=True)
    send_email(
        subject="Reset your password",
        recipient=user.email,
        body=(
            f"Hi {user.firstname},\n\n"
            "Reset your password using the link below (valid for 1 hour):\n"
            f"{reset_url}\n\n"
            "If you did not request this, you can safely ignore this email."
        ),
    )


def send_verified_confirmation_email(user) -> None:
    """
    Sent once, immediately after a user successfully verifies their email.
    """
    send_email(
        subject="Your email has been verified",
        recipient=user.email,
        body=(
            f"Hi {user.firstname},\n\n"
            "Your email address has been successfully verified. You can now "
            "log in to your account."
        ),
    )


def send_password_changed_email(user) -> None:
    """
    Sent immediately after a user's password is successfully changed or reset.
    """
    send_email(
        subject="Your password has been changed",
        recipient=user.email,
        body=(
            f"Hi {user.firstname},\n\n"
            "This is a confirmation that your password was just reset.\n\n"
            "If you did not make this change, please change your password"
            "immediately, as your account may be compromised."
        ),
    )


# End of file
