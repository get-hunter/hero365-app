"""
Email Service Port

Interface for email service operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class EmailPriority(Enum):
    """Email priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class EmailTemplate:
    """Email template configuration."""
    template_id: str
    subject: str
    variables: Dict[str, Any]


@dataclass
class EmailAttachment:
    """Email attachment configuration."""
    filename: str
    content: bytes
    content_type: str


@dataclass
class EmailMessage:
    """Email message structure."""
    to: List[str]
    subject: str
    html_body: Optional[str] = None
    text_body: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    reply_to: Optional[str] = None
    priority: EmailPriority = EmailPriority.NORMAL
    attachments: Optional[List[EmailAttachment]] = None
    template: Optional[EmailTemplate] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EmailResult:
    """Email send result."""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None


class EmailServicePort(ABC):
    """
    Email service port interface.
    
    This interface defines the contract for sending emails
    and managing email-related operations.
    """
    
    @abstractmethod
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """
        Send a single email message.
        
        Args:
            message: Email message to send
            
        Returns:
            EmailResult with send status and details
        """
        pass
    
    @abstractmethod
    async def send_bulk_emails(self, messages: List[EmailMessage]) -> List[EmailResult]:
        """
        Send multiple email messages.
        
        Args:
            messages: List of email messages to send
            
        Returns:
            List of EmailResult for each message
        """
        pass
    
    @abstractmethod
    async def send_template_email(self, template: EmailTemplate, 
                                 to: List[str], **kwargs) -> EmailResult:
        """
        Send an email using a predefined template.
        
        Args:
            template: Email template configuration
            to: List of recipient email addresses
            **kwargs: Additional email parameters
            
        Returns:
            EmailResult with send status and details
        """
        pass
    
    @abstractmethod
    async def send_welcome_email(self, to_email: str, user_name: str, 
                                activation_link: Optional[str] = None) -> EmailResult:
        """
        Send a welcome email to a new user.
        
        Args:
            to_email: Recipient email address
            user_name: User's full name
            activation_link: Optional account activation link
            
        Returns:
            EmailResult with send status and details
        """
        pass
    
    @abstractmethod
    async def send_password_reset_email(self, to_email: str, user_name: str,
                                       reset_link: str, reset_token: str) -> EmailResult:
        """
        Send a password reset email.
        
        Args:
            to_email: Recipient email address
            user_name: User's full name
            reset_link: Password reset link
            reset_token: Reset token for verification
            
        Returns:
            EmailResult with send status and details
        """
        pass
    
    @abstractmethod
    async def send_verification_email(self, to_email: str, user_name: str,
                                     verification_link: str, verification_code: str) -> EmailResult:
        """
        Send an email verification message.
        
        Args:
            to_email: Recipient email address
            user_name: User's full name
            verification_link: Email verification link
            verification_code: Verification code
            
        Returns:
            EmailResult with send status and details
        """
        pass
    
    @abstractmethod
    async def send_notification_email(self, to_email: str, user_name: str,
                                     subject: str, message: str,
                                     action_link: Optional[str] = None) -> EmailResult:
        """
        Send a general notification email.
        
        Args:
            to_email: Recipient email address
            user_name: User's full name
            subject: Email subject
            message: Email message content
            action_link: Optional action link
            
        Returns:
            EmailResult with send status and details
        """
        pass
    
    @abstractmethod
    async def validate_email_address(self, email: str) -> bool:
        """
        Validate an email address format and deliverability.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email is valid and deliverable
        """
        pass
    
    @abstractmethod
    async def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the delivery status of a sent email.
        
        Args:
            message_id: Message ID returned from send operation
            
        Returns:
            Dictionary with email status information
        """
        pass
    
    @abstractmethod
    async def get_delivery_statistics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get email delivery statistics for a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary with delivery statistics
        """
        pass 