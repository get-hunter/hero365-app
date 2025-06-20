"""
Application Ports Package

Port interfaces (adapters pattern) for external services and dependencies.
These interfaces define contracts for external services without specifying implementation.
"""

from .email_service import (
    EmailServicePort, EmailMessage, EmailResult, EmailTemplate, 
    EmailAttachment, EmailPriority
)
from .sms_service import (
    SMSServicePort, SMSMessage, SMSResult, SMSPriority
)
from .auth_service import (
    AuthServicePort, AuthUser, AuthToken, AuthResult, AuthProvider
)

__all__ = [
    # Email service
    "EmailServicePort",
    "EmailMessage", 
    "EmailResult",
    "EmailTemplate",
    "EmailAttachment",
    "EmailPriority",
    
    # SMS service
    "SMSServicePort",
    "SMSMessage",
    "SMSResult", 
    "SMSPriority",
    
    # Authentication service
    "AuthServicePort",
    "AuthUser",
    "AuthToken",
    "AuthResult",
    "AuthProvider",
] 