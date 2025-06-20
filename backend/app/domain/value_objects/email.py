"""
Email Value Object

Immutable value object representing an email address with validation.
"""

import re
from dataclasses import dataclass
from typing import Union

from ..exceptions.domain_exceptions import DomainValidationError


@dataclass(frozen=True)
class Email:
    """
    Email value object that ensures email address validity.
    
    This is an immutable value object that validates email format
    and provides consistent behavior for email handling.
    """
    
    value: str
    
    def __post_init__(self):
        """Validate email format after initialization."""
        if not self.value:
            raise DomainValidationError("Email address cannot be empty")
        
        if not self._is_valid_email(self.value):
            raise DomainValidationError(f"Invalid email format: {self.value}")
        
        if len(self.value) > 255:
            raise DomainValidationError("Email address too long (max 255 characters)")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """
        Validate email format using regex.
        
        Args:
            email: Email string to validate
            
        Returns:
            True if email format is valid, False otherwise
        """
        # Basic email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email.strip()) is not None
    
    def get_domain(self) -> str:
        """
        Extract the domain part of the email address.
        
        Returns:
            Domain part of the email (e.g., 'example.com' from 'user@example.com')
        """
        return self.value.split('@')[1]
    
    def get_local_part(self) -> str:
        """
        Extract the local part of the email address.
        
        Returns:
            Local part of the email (e.g., 'user' from 'user@example.com')
        """
        return self.value.split('@')[0]
    
    def is_business_email(self) -> bool:
        """
        Check if the email appears to be a business email.
        
        Returns:
            True if the email domain is not a common personal email provider
        """
        personal_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'icloud.com', 'aol.com', 'live.com', 'msn.com'
        }
        return self.get_domain().lower() not in personal_domains
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Union['Email', str]) -> bool:
        if isinstance(other, Email):
            return self.value.lower() == other.value.lower()
        elif isinstance(other, str):
            return self.value.lower() == other.lower()
        return False
    
    def __hash__(self) -> int:
        return hash(self.value.lower())
    
    @classmethod
    def create(cls, value: str) -> 'Email':
        """
        Factory method to create an Email instance.
        
        Args:
            value: Email string to create Email object from
            
        Returns:
            Email instance
            
        Raises:
            DomainValidationError: If email format is invalid
        """
        return cls(value.strip().lower()) 