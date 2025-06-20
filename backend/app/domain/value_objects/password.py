"""
Password Value Object

Immutable value object representing a password with validation and hashing.
"""

import re
import hashlib
import secrets
from dataclasses import dataclass
from typing import Union

from ..exceptions.domain_exceptions import DomainValidationError


@dataclass(frozen=True)
class Password:
    """
    Password value object that ensures password security requirements.
    
    This is an immutable value object that validates password strength
    and provides secure hashing capabilities.
    """
    
    value: str
    is_hashed: bool = False
    
    def __post_init__(self):
        """Validate password after initialization."""
        if not self.value:
            raise DomainValidationError("Password cannot be empty")
        
        if not self.is_hashed:
            # Validate plain text password
            self._validate_password_strength(self.value)
            
            if len(self.value) < 8:
                raise DomainValidationError("Password must be at least 8 characters long")
            
            if len(self.value) > 128:
                raise DomainValidationError("Password too long (max 128 characters)")
        else:
            # Validate hashed password format
            if not self._is_valid_hash(self.value):
                raise DomainValidationError("Invalid password hash format")
    
    def _validate_password_strength(self, password: str) -> None:
        """
        Validate password strength requirements.
        
        Args:
            password: Plain text password to validate
            
        Raises:
            DomainValidationError: If password doesn't meet strength requirements
        """
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise DomainValidationError("Password must contain at least one uppercase letter")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise DomainValidationError("Password must contain at least one lowercase letter")
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            raise DomainValidationError("Password must contain at least one digit")
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise DomainValidationError("Password must contain at least one special character")
        
        # Check for common weak passwords
        weak_passwords = {
            'password', '12345678', 'qwerty', 'abc123', 'password123',
            'admin', 'letmein', 'welcome', 'monkey', '123456789'
        }
        if password.lower() in weak_passwords:
            raise DomainValidationError("Password is too common and weak")
    
    def _is_valid_hash(self, hash_value: str) -> bool:
        """
        Check if the value is a valid password hash.
        
        Args:
            hash_value: Hash string to validate
            
        Returns:
            True if valid hash format, False otherwise
        """
        # Check for bcrypt hash format
        if hash_value.startswith('$2b$') or hash_value.startswith('$2a$') or hash_value.startswith('$2y$'):
            return len(hash_value) == 60
        
        # Check for argon2 hash format
        if hash_value.startswith('$argon2'):
            return len(hash_value) > 50
        
        # Check for pbkdf2 hash format
        if hash_value.startswith('pbkdf2'):
            return len(hash_value) > 50
        
        return False
    
    def hash(self) -> 'Password':
        """
        Hash the password if it's not already hashed.
        
        Returns:
            New Password instance with hashed value
            
        Raises:
            DomainValidationError: If password is already hashed
        """
        if self.is_hashed:
            raise DomainValidationError("Password is already hashed")
        
        # Simple hash for demo - in production, use bcrypt or argon2
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac('sha256', 
                                   self.value.encode('utf-8'), 
                                   salt.encode('utf-8'), 
                                   100000)
        hash_value = f"pbkdf2_sha256$100000${salt}${hashed.hex()}"
        
        return Password(value=hash_value, is_hashed=True)
    
    def verify(self, plain_password: str) -> bool:
        """
        Verify a plain text password against this hashed password.
        
        Args:
            plain_password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
            
        Raises:
            DomainValidationError: If this password is not hashed
        """
        if not self.is_hashed:
            raise DomainValidationError("Cannot verify against unhashed password")
        
        try:
            # Parse the hash components
            parts = self.value.split('$')
            if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
                return False
            
            iterations = int(parts[1])
            salt = parts[2]
            stored_hash = parts[3]
            
            # Hash the provided password with the same salt
            test_hash = hashlib.pbkdf2_hmac('sha256',
                                          plain_password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          iterations)
            
            return secrets.compare_digest(stored_hash, test_hash.hex())
        except (ValueError, IndexError):
            return False
    
    def get_strength_score(self) -> int:
        """
        Get password strength score (0-100).
        
        Returns:
            Password strength score
            
        Raises:
            DomainValidationError: If password is hashed
        """
        if self.is_hashed:
            raise DomainValidationError("Cannot calculate strength of hashed password")
        
        score = 0
        
        # Length bonus
        if len(self.value) >= 8:
            score += 25
        if len(self.value) >= 12:
            score += 15
        if len(self.value) >= 16:
            score += 10
        
        # Character variety bonus
        if re.search(r'[a-z]', self.value):
            score += 10
        if re.search(r'[A-Z]', self.value):
            score += 10
        if re.search(r'\d', self.value):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', self.value):
            score += 20
        
        return min(score, 100)
    
    def __str__(self) -> str:
        if self.is_hashed:
            return f"[HASHED PASSWORD: {self.value[:20]}...]"
        else:
            return "[PLAIN PASSWORD: ****]"
    
    def __eq__(self, other: Union['Password', str]) -> bool:
        if isinstance(other, Password):
            return self.value == other.value and self.is_hashed == other.is_hashed
        elif isinstance(other, str) and not self.is_hashed:
            return self.value == other
        return False
    
    def __hash__(self) -> int:
        return hash((self.value, self.is_hashed))
    
    @classmethod
    def create_plain(cls, value: str) -> 'Password':
        """
        Factory method to create a plain text Password instance.
        
        Args:
            value: Plain text password
            
        Returns:
            Password instance
            
        Raises:
            DomainValidationError: If password is invalid
        """
        return cls(value=value, is_hashed=False)
    
    @classmethod
    def create_hashed(cls, value: str) -> 'Password':
        """
        Factory method to create a hashed Password instance.
        
        Args:
            value: Hashed password
            
        Returns:
            Password instance
            
        Raises:
            DomainValidationError: If hash format is invalid
        """
        return cls(value=value, is_hashed=True) 