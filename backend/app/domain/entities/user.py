"""
User Domain Entity

Represents a user in the business domain with associated business rules and behaviors.
"""

import uuid
from dataclasses import dataclass
from typing import Optional

from ..value_objects.email import Email
from ..value_objects.phone import Phone
from ..exceptions.domain_exceptions import DomainValidationError


@dataclass
class User:
    """
    User entity representing the core business concept of a user.
    
    This entity contains business logic and rules that apply to users
    regardless of how they are stored or presented.
    """
    
    id: uuid.UUID
    email: Optional[Email]
    phone: Optional[Phone]
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    supabase_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate business rules after initialization."""
        self._validate_contact_info()
        self._validate_name()
    
    def _validate_contact_info(self) -> None:
        """Ensure user has at least one contact method."""
        if not self.email and not self.phone:
            raise DomainValidationError("User must have either email or phone number")
    
    def _validate_name(self) -> None:
        """Validate full name if provided."""
        if self.full_name is not None and len(self.full_name.strip()) == 0:
            raise DomainValidationError("Full name cannot be empty")
    
    def update_profile(self, full_name: Optional[str] = None, 
                      email: Optional[Email] = None, 
                      phone: Optional[Phone] = None) -> None:
        """
        Update user profile information.
        
        Args:
            full_name: New full name
            email: New email address
            phone: New phone number
            
        Raises:
            DomainValidationError: If the update violates business rules
        """
        # Store original values for rollback if validation fails
        original_name = self.full_name
        original_email = self.email
        original_phone = self.phone
        
        try:
            if full_name is not None:
                self.full_name = full_name
            if email is not None:
                self.email = email
            if phone is not None:
                self.phone = phone
            
            # Validate after changes
            self._validate_contact_info()
            self._validate_name()
            
        except DomainValidationError:
            # Rollback changes
            self.full_name = original_name
            self.email = original_email
            self.phone = original_phone
            raise
    
    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate the user account."""
        if self.is_superuser:
            raise DomainValidationError("Cannot deactivate superuser account")
        self.is_active = False
    
    def grant_superuser_privileges(self) -> None:
        """Grant superuser privileges to the user."""
        if not self.is_active:
            raise DomainValidationError("Cannot grant superuser privileges to inactive user")
        self.is_superuser = True
    
    def revoke_superuser_privileges(self) -> None:
        """Revoke superuser privileges from the user."""
        self.is_superuser = False
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.is_active and self.is_superuser
    
    def can_access_system(self) -> bool:
        """Check if user can access the system."""
        return self.is_active
    
    def get_display_name(self) -> str:
        """Get the display name for the user."""
        if self.full_name:
            return self.full_name
        if self.email:
            return str(self.email)
        if self.phone:
            return str(self.phone)
        return f"User {self.id}"
    
    def __str__(self) -> str:
        return f"User({self.get_display_name()})"
    
    def __repr__(self) -> str:
        return (f"User(id={self.id}, email={self.email}, phone={self.phone}, "
                f"full_name='{self.full_name}', is_active={self.is_active}, "
                f"is_superuser={self.is_superuser})") 