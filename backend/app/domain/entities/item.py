"""
Item Domain Entity

Represents an item in the business domain with associated business rules and behaviors.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..exceptions.domain_exceptions import DomainValidationError, InvalidOperationError


@dataclass
class Item:
    """
    Item entity representing the core business concept of an item.
    
    This entity contains business logic and rules that apply to items
    regardless of how they are stored or presented.
    """
    
    id: uuid.UUID
    title: str
    description: Optional[str]
    owner_id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    
    def __post_init__(self):
        """Validate business rules after initialization."""
        self._validate_title()
        self._validate_description()
        
        # Set timestamps if not provided
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.utcnow())
        if self.updated_at is None:
            object.__setattr__(self, 'updated_at', datetime.utcnow())
    
    def _validate_title(self) -> None:
        """Validate item title."""
        if not self.title or not self.title.strip():
            raise DomainValidationError("Item title cannot be empty")
        
        if len(self.title.strip()) > 255:
            raise DomainValidationError("Item title too long (max 255 characters)")
        
        # Normalize title by removing extra whitespace
        normalized_title = ' '.join(self.title.split())
        object.__setattr__(self, 'title', normalized_title)
    
    def _validate_description(self) -> None:
        """Validate item description."""
        if self.description is not None:
            if len(self.description) > 1000:
                raise DomainValidationError("Item description too long (max 1000 characters)")
            
            # Normalize description
            if self.description.strip() == '':
                object.__setattr__(self, 'description', None)
            else:
                object.__setattr__(self, 'description', self.description.strip())
    
    def update_content(self, title: Optional[str] = None, 
                      description: Optional[str] = None) -> None:
        """
        Update item content.
        
        Args:
            title: New title for the item
            description: New description for the item
            
        Raises:
            DomainValidationError: If the update violates business rules
            InvalidOperationError: If the item is deleted
        """
        if self.is_deleted:
            raise InvalidOperationError("update_content", "Cannot update deleted item")
        
        # Store original values for rollback if validation fails
        original_title = self.title
        original_description = self.description
        
        try:
            if title is not None:
                object.__setattr__(self, 'title', title)
                self._validate_title()
            
            if description is not None:
                object.__setattr__(self, 'description', description)
                self._validate_description()
            
            # Update timestamp
            object.__setattr__(self, 'updated_at', datetime.utcnow())
            
        except DomainValidationError:
            # Rollback changes
            object.__setattr__(self, 'title', original_title)
            object.__setattr__(self, 'description', original_description)
            raise
    
    def mark_as_deleted(self) -> None:
        """
        Mark the item as deleted (soft delete).
        
        Raises:
            InvalidOperationError: If the item is already deleted
        """
        if self.is_deleted:
            raise InvalidOperationError("mark_as_deleted", "Item is already deleted")
        
        object.__setattr__(self, 'is_deleted', True)
        object.__setattr__(self, 'updated_at', datetime.utcnow())
    
    def restore(self) -> None:
        """
        Restore a deleted item.
        
        Raises:
            InvalidOperationError: If the item is not deleted
        """
        if not self.is_deleted:
            raise InvalidOperationError("restore", "Item is not deleted")
        
        object.__setattr__(self, 'is_deleted', False)
        object.__setattr__(self, 'updated_at', datetime.utcnow())
    
    def is_owned_by(self, user_id: uuid.UUID) -> bool:
        """
        Check if the item is owned by the specified user.
        
        Args:
            user_id: User ID to check ownership against
            
        Returns:
            True if the item is owned by the user, False otherwise
        """
        return self.owner_id == user_id
    
    def can_be_edited_by(self, user_id: uuid.UUID, is_superuser: bool = False) -> bool:
        """
        Check if the item can be edited by the specified user.
        
        Args:
            user_id: User ID to check edit permissions
            is_superuser: Whether the user is a superuser
            
        Returns:
            True if the user can edit the item, False otherwise
        """
        if self.is_deleted:
            return False
        
        return self.is_owned_by(user_id) or is_superuser
    
    def can_be_viewed_by(self, user_id: uuid.UUID, is_superuser: bool = False) -> bool:
        """
        Check if the item can be viewed by the specified user.
        
        Args:
            user_id: User ID to check view permissions
            is_superuser: Whether the user is a superuser
            
        Returns:
            True if the user can view the item, False otherwise
        """
        # In this simple implementation, only owners and superusers can view items
        # This could be extended to support public items, sharing, etc.
        return self.is_owned_by(user_id) or is_superuser
    
    def get_summary(self) -> str:
        """
        Get a summary of the item.
        
        Returns:
            Brief summary of the item
        """
        if self.description:
            # Return first 100 characters of description
            summary = self.description[:100]
            if len(self.description) > 100:
                summary += "..."
            return summary
        return "No description"
    
    def get_word_count(self) -> int:
        """
        Get the word count of the item's content.
        
        Returns:
            Total word count of title and description
        """
        word_count = len(self.title.split()) if self.title else 0
        if self.description:
            word_count += len(self.description.split())
        return word_count
    
    def has_description(self) -> bool:
        """
        Check if the item has a description.
        
        Returns:
            True if item has a non-empty description, False otherwise
        """
        return self.description is not None and len(self.description.strip()) > 0
    
    def get_age_in_days(self) -> int:
        """
        Get the age of the item in days.
        
        Returns:
            Number of days since the item was created
        """
        if self.created_at:
            return (datetime.utcnow() - self.created_at).days
        return 0
    
    def __str__(self) -> str:
        status = " (deleted)" if self.is_deleted else ""
        return f"Item({self.title}{status})"
    
    def __repr__(self) -> str:
        return (f"Item(id={self.id}, title='{self.title}', "
                f"owner_id={self.owner_id}, is_deleted={self.is_deleted})") 