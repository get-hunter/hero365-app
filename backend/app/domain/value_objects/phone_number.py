"""
Phone Number Value Object
Handles international phone number validation, formatting, and storage
"""

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class PhoneNumber(BaseModel):
    """
    International phone number value object supporting E.164 format.
    
    Provides validation, formatting, and country code extraction for
    international phone numbers to support global expansion.
    """
    
    # E.164 format (international standard) - primary storage
    e164: Optional[str] = Field(None, description="E.164 format: +1234567890")
    
    # Country code
    country_code: Optional[str] = Field(None, description="Country code: 1, 44, 49, etc.")
    
    # Display format
    display: Optional[str] = Field(None, description="Formatted for display: +1 (555) 123-4567")
    
    @field_validator('e164')
    @classmethod
    def validate_e164(cls, v: Optional[str]) -> Optional[str]:
        """Validate E.164 format"""
        if v is None:
            return v
        
        # E.164 format: +[country code][national number]
        # Length: 7-15 digits (including country code)
        # Must start with +
        if not re.match(r'^\+[1-9]\d{6,14}$', v):
            raise ValueError('Phone number must be in valid E.164 format (+1234567890)')
        
        return v
    
    @classmethod
    def from_input(cls, phone_input: str, default_country_code: str = '1') -> 'PhoneNumber':
        """
        Create PhoneNumber from user input with automatic normalization.
        
        Args:
            phone_input: Raw phone number input
            default_country_code: Default country code if not provided
            
        Returns:
            PhoneNumber object with normalized values
        """
        if not phone_input:
            return cls()
        
        # Clean input - remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_input)
        
        # Normalize to E.164 format
        e164 = cls._normalize_to_e164(cleaned, default_country_code)
        
        if e164:
            country_code = cls._extract_country_code(e164)
            display = cls._format_for_display(e164, country_code)
            
            return cls(
                e164=e164,
                country_code=country_code,
                display=display
            )
        
        # If normalization failed, return None or raise exception
        return cls()
    
    @staticmethod
    def _normalize_to_e164(cleaned: str, default_country_code: str) -> Optional[str]:
        """Normalize cleaned phone number to E.164 format"""
        
        # If already in E.164 format, validate and return
        if cleaned.startswith('+'):
            if re.match(r'^\+[1-9]\d{6,14}$', cleaned):
                return cleaned
            return None
        
        # If starts with country code without +, add +
        if len(cleaned) > 10:
            result = '+' + cleaned
            if re.match(r'^\+[1-9]\d{6,14}$', result):
                return result
        
        # Assume national number, add default country code
        if len(cleaned) >= 7:
            result = '+' + default_country_code + cleaned
            if re.match(r'^\+[1-9]\d{6,14}$', result):
                return result
        
        return None
    
    @staticmethod
    def _extract_country_code(e164: str) -> str:
        """Extract country code from E.164 phone number"""
        # Remove the + and extract country code
        digits = e164[1:]
        
        # Common country code patterns
        if digits.startswith('1') and len(digits) == 11:  # US/Canada
            return '1'
        elif digits.startswith('44'):  # UK
            return '44'
        elif digits.startswith('49'):  # Germany
            return '49'
        elif digits.startswith('33'):  # France
            return '33'
        elif digits.startswith('34'):  # Spain
            return '34'
        elif digits.startswith('39'):  # Italy
            return '39'
        elif digits.startswith('52'):  # Mexico
            return '52'
        elif digits.startswith('55'):  # Brazil
            return '55'
        elif digits.startswith('86'):  # China
            return '86'
        elif digits.startswith('91'):  # India
            return '91'
        else:
            # Fallback: try 1-3 digit country codes
            for length in [1, 2, 3]:
                if len(digits) > length + 6:  # Ensure enough digits for national number
                    return digits[:length]
            return digits[:3]  # Default fallback
    
    @staticmethod
    def _format_for_display(e164: str, country_code: str) -> str:
        """Format phone number for display based on country"""
        national_number = e164[len(country_code) + 1:]
        
        if country_code == '1':  # US/Canada: +1 (XXX) XXX-XXXX
            if len(national_number) == 10:
                return f"+1 ({national_number[:3]}) {national_number[3:6]}-{national_number[6:]}"
        elif country_code == '44':  # UK: +44 XXXX XXX XXX
            if len(national_number) >= 10:
                return f"+44 {national_number[:4]} {national_number[4:7]} {national_number[7:]}"
        elif country_code == '49':  # Germany: +49 XXX XXXXXXXX
            if len(national_number) >= 10:
                return f"+49 {national_number[:3]} {national_number[3:]}"
        elif country_code == '33':  # France: +33 X XX XX XX XX
            if len(national_number) == 9:
                return f"+33 {national_number[0]} {national_number[1:3]} {national_number[3:5]} {national_number[5:7]} {national_number[7:]}"
        
        # Default format: +CC XXXXXXXXX
        return f"+{country_code} {national_number}"
    
    def is_valid(self) -> bool:
        """Check if phone number is valid (has E.164 format)"""
        return self.e164 is not None
    
    def is_country(self, country_code: str) -> bool:
        """Check if phone number belongs to specific country"""
        return self.country_code == country_code
    
    def for_sms(self) -> Optional[str]:
        """Get phone number in format suitable for SMS services (E.164)"""
        return self.e164
    
    def for_display(self) -> str:
        """Get phone number formatted for display"""
        return self.display or self.e164 or ""
    
    def for_storage(self) -> Optional[str]:
        """Get phone number in format for database storage (E.164)"""
        return self.e164
    
    def __str__(self) -> str:
        """String representation uses display format"""
        return self.for_display()
    
    def __bool__(self) -> bool:
        """Phone number is truthy if it has any value"""
        return bool(self.e164)


# Convenience functions for common operations
def normalize_phone(phone_input: str, default_country_code: str = '1') -> PhoneNumber:
    """Normalize phone number input to PhoneNumber object"""
    return PhoneNumber.from_input(phone_input, default_country_code)


def is_valid_phone(phone_input: str, default_country_code: str = '1') -> bool:
    """Check if phone number input is valid"""
    return normalize_phone(phone_input, default_country_code).is_valid()


def format_phone_for_display(phone_input: str, default_country_code: str = '1') -> str:
    """Format phone number for display"""
    return normalize_phone(phone_input, default_country_code).for_display()


def get_phone_e164(phone_input: str, default_country_code: str = '1') -> Optional[str]:
    """Get phone number in E.164 format"""
    return normalize_phone(phone_input, default_country_code).for_storage()
