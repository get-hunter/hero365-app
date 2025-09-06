"""
Utility modules for the Hero365 backend application.
"""

# Re-export commonly used functions for backward compatibility
from .email import (
    format_datetime_utc,
    EmailData,
    render_email_template,
    send_email,
    generate_test_email,
    generate_reset_password_email,
    generate_new_account_email,
    generate_password_reset_token,
    verify_password_reset_token
)

from .slug_resolver import (
    normalize_service_slug,
    normalize_location_slug,
    resolve_service_slug,
    get_business_service_slugs,
    get_business_location_slugs,
    validate_service_location_combination
)

__all__ = [
    'format_datetime_utc',
    'EmailData',
    'render_email_template', 
    'send_email',
    'generate_test_email',
    'generate_reset_password_email',
    'generate_new_account_email',
    'generate_password_reset_token',
    'verify_password_reset_token',
    'normalize_service_slug',
    'normalize_location_slug',
    'resolve_service_slug',
    'get_business_service_slugs',
    'get_business_location_slugs',
    'validate_service_location_combination'
]
