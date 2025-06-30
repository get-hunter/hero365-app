import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import jwt
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_datetime_utc(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to standardized UTC format without microseconds."""
    if dt is None:
        return None
    # Ensure datetime is in UTC and format without microseconds
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        # Convert to UTC if not already
        utc_dt = dt.utctimetuple()
        return datetime(*utc_dt[:6]).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


async def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    """Send email using the configured email service (Resend)."""
    assert settings.emails_enabled, "Email service is not properly configured"
    
    # Import here to avoid circular imports
    from app.infrastructure.config.dependency_injection import get_email_service
    from app.application.ports.email_service import EmailMessage
    
    email_service = get_email_service()
    
    message = EmailMessage(
        to=[email_to],
        subject=subject,
        html_body=html_content,
        tags=["utility", "test"]
    )
    
    result = await email_service.send_email(message)
    
    if result.success:
        logger.info(f"Email sent successfully to {email_to}")
    else:
        logger.error(f"Failed to send email to {email_to}: {result.error_message}")


def generate_test_email(email_to: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None
