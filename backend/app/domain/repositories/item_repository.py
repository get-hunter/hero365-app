"""
Item Repository Interface

Abstract interface for item data access operations.
"""

import uuid
from abc import abstractmethod
from typing import Optional, List

from .base_repository import BaseRepository
from ..entities.item import Item


class ItemRepository(BaseRepository[Item]):
    """
    Item repository interface defining item-specific data access operations.
    
    This interface extends the base repository with item-specific queries
    and operations.
    """
    
    @abstractmethod
    async def get_by_owner_id(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Item]:
        """
        Get items by owner ID with pagination.
        
        Args:
            owner_id: ID of the item owner
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of items owned by the user
        """
        pass
    
    @abstractmethod
    async def get_active_by_owner_id(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Item]:
        """
        Get active (non-deleted) items by owner ID with pagination.
        
        Args:
            owner_id: ID of the item owner
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of active items owned by the user
        """
        pass
    
    @abstractmethod
    async def get_deleted_by_owner_id(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Item]:
        """
        Get deleted items by owner ID with pagination.
        
        Args:
            owner_id: ID of the item owner
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of deleted items owned by the user
        """
        pass
    
    @abstractmethod
    async def count_by_owner_id(self, owner_id: uuid.UUID) -> int:
        """
        Count items by owner ID.
        
        Args:
            owner_id: ID of the item owner
            
        Returns:
            Total number of items owned by the user
        """
        pass
    
    @abstractmethod
    async def count_active_by_owner_id(self, owner_id: uuid.UUID) -> int:
        """
        Count active items by owner ID.
        
        Args:
            owner_id: ID of the item owner
            
        Returns:
            Number of active items owned by the user
        """
        pass
    
    @abstractmethod
    async def search_by_title(self, title: str, owner_id: Optional[uuid.UUID] = None, 
                             skip: int = 0, limit: int = 100) -> List[Item]:
        """
        Search items by title.
        
        Args:
            title: Title to search for
            owner_id: Optional owner ID to filter by
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of items matching the title search
        """
        pass
    
    @abstractmethod
    async def search_by_content(self, query: str, owner_id: Optional[uuid.UUID] = None,
                               skip: int = 0, limit: int = 100) -> List[Item]:
        """
        Search items by title and description content.
        
        Args:
            query: Search query for title and description
            owner_id: Optional owner ID to filter by
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of items matching the content search
        """
        pass
    
    @abstractmethod
    async def get_recent_items(self, owner_id: Optional[uuid.UUID] = None,
                              days: int = 7, skip: int = 0, limit: int = 100) -> List[Item]:
        """
        Get recently created items.
        
        Args:
            owner_id: Optional owner ID to filter by
            days: Number of days to look back
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of recently created items
        """
        pass
    
    @abstractmethod
    async def get_updated_items(self, owner_id: Optional[uuid.UUID] = None,
                               days: int = 7, skip: int = 0, limit: int = 100) -> List[Item]:
        """
        Get recently updated items.
        
        Args:
            owner_id: Optional owner ID to filter by
            days: Number of days to look back
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of recently updated items
        """
        pass
    
    @abstractmethod
    async def bulk_delete_by_owner_id(self, owner_id: uuid.UUID) -> int:
        """
        Mark all items by owner as deleted (soft delete).
        
        Args:
            owner_id: ID of the item owner
            
        Returns:
            Number of items marked as deleted
        """
        pass
    
    @abstractmethod
    async def permanently_delete_by_owner_id(self, owner_id: uuid.UUID) -> int:
        """
        Permanently delete all items by owner.
        
        Args:
            owner_id: ID of the item owner
            
        Returns:
            Number of items permanently deleted
        """
        pass 