"""
Configuration Infrastructure

Configuration and dependency injection setup.
Contains service factories, dependency containers, and configuration management.
"""

from .dependency_injection import (
    DependencyContainer,
    get_container,
    reset_container,
    get_user_repository,
    get_item_repository,
    get_auth_service,
    get_email_service,
    get_sms_service
)

__all__ = [
    "DependencyContainer",
    "get_container",
    "reset_container",
    "get_user_repository",
    "get_item_repository",
    "get_auth_service",
    "get_email_service",
    "get_sms_service",
] 