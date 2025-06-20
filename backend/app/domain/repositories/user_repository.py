"""
User Repository Interface

Abstract interface for user data access operations.
"""

import uuid
from abc import abstractmethod
from typing import Optional, List

from .base_repository import BaseRepository
from ..entities.user import User
from ..value_objects.email import Email
from ..value_objects.phone import Phone


class UserRepository(BaseRepository[User]):
    """
    User repository interface defining user-specific data access operations.
    
    This interface extends the base repository with user-specific queries
    and operations.
    """
    
    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        """
        Get a user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_phone(self, phone: Phone) -> Optional[User]:
        """
        Get a user by phone number.
        
        Args:
            phone: Phone number to search for
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_supabase_id(self, supabase_id: str) -> Optional[User]:
        """
        Get a user by Supabase ID.
        
        Args:
            supabase_id: Supabase user ID
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def email_exists(self, email: Email, exclude_user_id: Optional[uuid.UUID] = None) -> bool:
        """
        Check if an email address is already in use.
        
        Args:
            email: Email address to check
            exclude_user_id: User ID to exclude from the check (for updates)
            
        Returns:
            True if email exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def phone_exists(self, phone: Phone, exclude_user_id: Optional[uuid.UUID] = None) -> bool:
        """
        Check if a phone number is already in use.
        
        Args:
            phone: Phone number to check
            exclude_user_id: User ID to exclude from the check (for updates)
            
        Returns:
            True if phone exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all active users with pagination.
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of active users
        """
        pass
    
    @abstractmethod
    async def get_superusers(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all superusers with pagination.
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of superusers
        """
        pass
    
    @abstractmethod
    async def count_active_users(self) -> int:
        """
        Count the number of active users.
        
        Returns:
            Number of active users
        """
        pass
    
    @abstractmethod
    async def count_superusers(self) -> int:
        """
        Count the number of superusers.
        
        Returns:
            Number of superusers
        """
        pass
    
    @abstractmethod
    async def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Search users by name, email, or phone.
        
        Args:
            query: Search query
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of users matching the search criteria
        """
        pass 