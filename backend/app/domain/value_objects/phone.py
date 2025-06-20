"""
Phone Value Object

Immutable value object representing a phone number with validation.
"""

import re
from dataclasses import dataclass
from typing import Union

from ..exceptions.domain_exceptions import DomainValidationError


@dataclass(frozen=True)
class Phone:
    """
    Phone value object that ensures phone number validity.
    
    This is an immutable value object that validates phone format
    and provides consistent behavior for phone number handling.
    """
    
    value: str
    
    def __post_init__(self):
        """Validate phone number format after initialization."""
        if not self.value:
            raise DomainValidationError("Phone number cannot be empty")
        
        # Normalize the phone number
        normalized = self._normalize_phone(self.value)
        
        if not self._is_valid_phone(normalized):
            raise DomainValidationError(f"Invalid phone number format: {self.value}")
        
        if len(self.value) > 20:
            raise DomainValidationError("Phone number too long (max 20 characters)")
        
        # Store the normalized value
        object.__setattr__(self, 'value', normalized)
    
    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """
        Normalize phone number by removing non-digit characters except +.
        
        Args:
            phone: Raw phone number string
            
        Returns:
            Normalized phone number
        """
        # Keep only digits and + sign
        normalized = re.sub(r'[^\d+]', '', phone.strip())
        return normalized
    
    @staticmethod
    def _is_valid_phone(phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Normalized phone number to validate
            
        Returns:
            True if phone format is valid, False otherwise
        """
        if not phone:
            return False
        
        # Basic phone validation patterns
        patterns = [
            r'^\+?\d{10,15}$',  # International format with optional +
            r'^\d{10}$',        # US format (10 digits)
            r'^\+1\d{10}$',     # US format with country code
        ]
        
        return any(re.match(pattern, phone) for pattern in patterns)
    
    def get_country_code(self) -> str:
        """
        Extract country code from phone number if present.
        
        Returns:
            Country code (e.g., '+1') or empty string if not present
        """
        if self.value.startswith('+'):
            # Find where the country code ends (usually 1-3 digits after +)
            match = re.match(r'^(\+\d{1,3})', self.value)
            return match.group(1) if match else ''
        return ''
    
    def get_national_number(self) -> str:
        """
        Get the national part of the phone number (without country code).
        
        Returns:
            National phone number without country code
        """
        country_code = self.get_country_code()
        if country_code:
            return self.value[len(country_code):]
        return self.value
    
    def is_mobile(self) -> bool:
        """
        Check if the phone number appears to be a mobile number.
        
        Returns:
            True if the number appears to be mobile (basic heuristic)
        """
        national = self.get_national_number()
        
        # Basic mobile number patterns (this is a simplified check)
        mobile_patterns = [
            r'^[67]\d{8}$',     # Many countries use 6xx, 7xx for mobile
            r'^[89]\d{8}$',     # Some countries use 8xx, 9xx for mobile
            r'^1[3-9]\d{8}$',   # China mobile pattern
        ]
        
        return any(re.match(pattern, national) for pattern in mobile_patterns)
    
    def format_display(self) -> str:
        """
        Format phone number for display purposes.
        
        Returns:
            Formatted phone number string
        """
        if self.value.startswith('+'):
            # International format
            country_code = self.get_country_code()
            national = self.get_national_number()
            
            if len(national) == 10:  # US format
                return f"{country_code} ({national[:3]}) {national[3:6]}-{national[6:]}"
            else:
                return f"{country_code} {national}"
        else:
            # National format
            if len(self.value) == 10:  # US format
                return f"({self.value[:3]}) {self.value[3:6]}-{self.value[6:]}"
            else:
                return self.value
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Union['Phone', str]) -> bool:
        if isinstance(other, Phone):
            return self.value == other.value
        elif isinstance(other, str):
            try:
                other_phone = Phone(other)
                return self.value == other_phone.value
            except DomainValidationError:
                return False
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    @classmethod
    def create(cls, value: str) -> 'Phone':
        """
        Factory method to create a Phone instance.
        
        Args:
            value: Phone string to create Phone object from
            
        Returns:
            Phone instance
            
        Raises:
            DomainValidationError: If phone format is invalid
        """
        return cls(value.strip()) 