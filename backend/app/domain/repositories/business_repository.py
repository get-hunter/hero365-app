"""
Business Repository Interface

Defines the contract for business data access operations.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.business import Business


class BusinessRepository(ABC):
    """
    Repository interface for Business entity operations.
    
    This interface defines the contract for all business data access operations,
    following the Repository pattern to abstract database implementation details.
    """
    
    @abstractmethod
    async def create(self, business: Business) -> Business:
        """
        Create a new business.
        
        Args:
            business: Business entity to create
            
        Returns:
            Created business entity with generated ID and timestamps
            
        Raises:
            DuplicateEntityError: If business name already exists for owner
            DatabaseError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, business_id: uuid.UUID) -> Optional[Business]:
        """
        Get business by ID.
        
        Args:
            business_id: Unique identifier of the business
            
        Returns:
            Business entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_owner(self, owner_id: str, skip: int = 0, limit: int = 100) -> List[Business]:
        """
        Get businesses owned by a specific user.
        
        Args:
            owner_id: ID of the business owner
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of business entities owned by the user
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_user_businesses(self, user_id: str, skip: int = 0, limit: int = 100) -> List[tuple[Business, 'BusinessMembership']]:
        """
        Get all businesses where user is a member (owner or team member).
        
        Args:
            user_id: ID of the user
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of tuples containing (Business, BusinessMembership) pairs
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def update(self, business: Business) -> Business:
        """
        Update an existing business.
        
        Args:
            business: Business entity with updated information
            
        Returns:
            Updated business entity
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            DuplicateEntityError: If business name conflicts
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    async def delete(self, business_id: uuid.UUID) -> bool:
        """
        Delete a business (soft delete by setting is_active = False).
        
        Args:
            business_id: ID of the business to delete
            
        Returns:
            True if business was deleted, False if business wasn't found
            
        Raises:
            DatabaseError: If deletion fails
        """
        pass
    
    @abstractmethod
    async def get_active_businesses(self, skip: int = 0, limit: int = 100) -> List[Business]:
        """
        Get active businesses with pagination.
        
        Args:
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of active business entities
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def search_businesses(self, query: str, skip: int = 0, limit: int = 100) -> List[Business]:
        """
        Search businesses by name, industry, or description.
        
        Args:
            query: Search query string
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of matching business entities
            
        Raises:
            DatabaseError: If search fails
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Get total count of all businesses.
        
        Returns:
            Total number of businesses
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def count_active(self) -> int:
        """
        Get count of active businesses.
        
        Returns:
            Number of active businesses
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def count_by_owner(self, owner_id: str) -> int:
        """
        Get count of businesses owned by a specific user.
        
        Args:
            owner_id: ID of the business owner
            
        Returns:
            Number of businesses owned by the user
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def exists(self, business_id: uuid.UUID) -> bool:
        """
        Check if a business exists.
        
        Args:
            business_id: ID of the business to check
            
        Returns:
            True if business exists, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass
    
    @abstractmethod
    async def is_name_unique_for_owner(self, name: str, owner_id: str, exclude_business_id: Optional[uuid.UUID] = None) -> bool:
        """
        Check if business name is unique for a specific owner.
        
        Args:
            name: Business name to check
            owner_id: ID of the business owner
            exclude_business_id: Business ID to exclude from check (for updates)
            
        Returns:
            True if name is unique for the owner, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass
    
    @abstractmethod
    async def get_by_industry(self, industry: str, skip: int = 0, limit: int = 100) -> List[Business]:
        """
        Get businesses by industry.
        
        Args:
            industry: Industry name
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of businesses in the specified industry
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_recent_businesses(self, days: int = 7, skip: int = 0, limit: int = 100) -> List[Business]:
        """
        Get recently created businesses.
        
        Args:
            days: Number of days to look back
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of recently created business entities
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass 