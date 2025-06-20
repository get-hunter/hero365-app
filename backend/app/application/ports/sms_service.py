"""
SMS Service Port

Interface for SMS service operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class SMSPriority(Enum):
    """SMS priority levels."""
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class SMSMessage:
    """SMS message structure."""
    to: str  # Phone number
    message: str
    from_number: Optional[str] = None
    priority: SMSPriority = SMSPriority.NORMAL
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[str] = None  # ISO format datetime


@dataclass
class SMSResult:
    """SMS send result."""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    cost: Optional[float] = None


class SMSServicePort(ABC):
    """
    SMS service port interface.
    
    This interface defines the contract for sending SMS messages
    and managing SMS-related operations.
    """
    
    @abstractmethod
    async def send_sms(self, message: SMSMessage) -> SMSResult:
        """
        Send a single SMS message.
        
        Args:
            message: SMS message to send
            
        Returns:
            SMSResult with send status and details
        """
        pass
    
    @abstractmethod
    async def send_bulk_sms(self, messages: List[SMSMessage]) -> List[SMSResult]:
        """
        Send multiple SMS messages.
        
        Args:
            messages: List of SMS messages to send
            
        Returns:
            List of SMSResult for each message
        """
        pass
    
    @abstractmethod
    async def send_verification_code(self, phone_number: str, code: str,
                                   app_name: Optional[str] = None) -> SMSResult:
        """
        Send a verification code via SMS.
        
        Args:
            phone_number: Recipient phone number
            code: Verification code
            app_name: Optional app name to include in message
            
        Returns:
            SMSResult with send status and details
        """
        pass
    
    @abstractmethod
    async def send_password_reset_code(self, phone_number: str, code: str,
                                      app_name: Optional[str] = None) -> SMSResult:
        """
        Send a password reset code via SMS.
        
        Args:
            phone_number: Recipient phone number
            code: Reset code
            app_name: Optional app name to include in message
            
        Returns:
            SMSResult with send status and details
        """
        pass
    
    @abstractmethod
    async def send_welcome_sms(self, phone_number: str, user_name: str,
                              app_name: Optional[str] = None) -> SMSResult:
        """
        Send a welcome SMS to a new user.
        
        Args:
            phone_number: Recipient phone number
            user_name: User's name
            app_name: Optional app name
            
        Returns:
            SMSResult with send status and details
        """
        pass
    
    @abstractmethod
    async def send_notification_sms(self, phone_number: str, message: str) -> SMSResult:
        """
        Send a general notification SMS.
        
        Args:
            phone_number: Recipient phone number
            message: SMS message content
            
        Returns:
            SMSResult with send status and details
        """
        pass
    
    @abstractmethod
    async def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate a phone number format and carrier.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if phone number is valid
        """
        pass
    
    @abstractmethod
    async def get_sms_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the delivery status of a sent SMS.
        
        Args:
            message_id: Message ID returned from send operation
            
        Returns:
            Dictionary with SMS status information
        """
        pass
    
    @abstractmethod
    async def get_delivery_statistics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get SMS delivery statistics for a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary with delivery statistics
        """
        pass
    
    @abstractmethod
    async def get_account_balance(self) -> Dict[str, Any]:
        """
        Get SMS service account balance and usage information.
        
        Returns:
            Dictionary with account information
        """
        pass 