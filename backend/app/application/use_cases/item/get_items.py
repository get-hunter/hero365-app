"""
Get Items Use Case

Business logic for retrieving item information.
"""

import uuid
from typing import Optional

from ...dto.item_dto import ItemDTO, ItemSearchDTO, ItemListDTO, ItemSummaryDTO, ItemStatsDTO
from ...exceptions.application_exceptions import (
    ItemNotFoundError, PermissionDeniedError
)
from ....domain.repositories.item_repository import ItemRepository
from ....domain.entities.item import Item


class GetItemsUseCase:
    """
    Use case for retrieving item information.
    
    This use case handles the business logic for fetching items,
    including permission checks and data formatting.
    """
    
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository
    
    async def get_by_id(self, item_id: uuid.UUID, requesting_user_id: Optional[uuid.UUID] = None,
                       is_superuser: bool = False) -> ItemDTO:
        """
        Get an item by ID.
        
        Args:
            item_id: ID of the item to retrieve
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            ItemDTO containing item data
            
        Raises:
            ItemNotFoundError: If item doesn't exist
            PermissionDeniedError: If user lacks permission
        """
        # Fetch item
        item = await self.item_repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(str(item_id))
        
        # Check permissions
        if not item.can_be_viewed_by(requesting_user_id or uuid.uuid4(), is_superuser):
            raise PermissionDeniedError("view_item", str(item_id))
        
        return self._entity_to_dto(item)
    
    async def get_items(self, search_dto: ItemSearchDTO, 
                       requesting_user_id: Optional[uuid.UUID] = None,
                       is_superuser: bool = False) -> ItemListDTO:
        """
        Get items with search and pagination.
        
        Args:
            search_dto: Search parameters
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            ItemListDTO with paginated results
            
        Raises:
            PermissionDeniedError: If user lacks permission
        """
        # Determine which items to fetch based on permissions
        if search_dto.owner_id:
            # Requesting specific owner's items
            if not self._can_view_user_items(search_dto.owner_id, requesting_user_id, is_superuser):
                raise PermissionDeniedError("view_items", str(search_dto.owner_id))
            
            if search_dto.include_deleted:
                items = await self.item_repository.get_by_owner_id(
                    search_dto.owner_id, search_dto.skip, search_dto.limit
                )
            else:
                items = await self.item_repository.get_active_by_owner_id(
                    search_dto.owner_id, search_dto.skip, search_dto.limit
                )
            
            total_count = await self.item_repository.count_by_owner_id(search_dto.owner_id)
            
        elif is_superuser:
            # Superuser can see all items
            if search_dto.query:
                items = await self.item_repository.search_by_content(
                    search_dto.query, None, search_dto.skip, search_dto.limit
                )
            else:
                items = await self.item_repository.get_all(search_dto.skip, search_dto.limit)
            
            total_count = await self.item_repository.count()
            
        elif requesting_user_id:
            # Regular user can only see their own items
            if search_dto.include_deleted:
                items = await self.item_repository.get_by_owner_id(
                    requesting_user_id, search_dto.skip, search_dto.limit
                )
            else:
                items = await self.item_repository.get_active_by_owner_id(
                    requesting_user_id, search_dto.skip, search_dto.limit
                )
            
            total_count = await self.item_repository.count_by_owner_id(requesting_user_id)
            
        else:
            # Anonymous users can't see any items
            raise PermissionDeniedError("view_items")
        
        # Filter items if search query is provided
        if search_dto.query and not is_superuser:
            # For non-superusers, apply content search within their own items
            items = await self.item_repository.search_by_content(
                search_dto.query, requesting_user_id, search_dto.skip, search_dto.limit
            )
        
        # Convert to DTOs
        item_dtos = [self._entity_to_dto(item) for item in items]
        
        # Calculate pagination info
        page = (search_dto.skip // search_dto.limit) + 1
        has_next = (search_dto.skip + search_dto.limit) < total_count
        has_previous = search_dto.skip > 0
        
        return ItemListDTO(
            items=item_dtos,
            total_count=total_count,
            page=page,
            page_size=search_dto.limit,
            has_next=has_next,
            has_previous=has_previous
        )
    
    async def get_user_items(self, owner_id: uuid.UUID, requesting_user_id: Optional[uuid.UUID] = None,
                            is_superuser: bool = False, skip: int = 0, limit: int = 100) -> ItemListDTO:
        """
        Get items for a specific user.
        
        Args:
            owner_id: ID of the item owner
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            ItemListDTO with user's items
            
        Raises:
            PermissionDeniedError: If user lacks permission
        """
        # Check permissions
        if not self._can_view_user_items(owner_id, requesting_user_id, is_superuser):
            raise PermissionDeniedError("view_items", str(owner_id))
        
        # Get active items for the user
        items = await self.item_repository.get_active_by_owner_id(owner_id, skip, limit)
        total_count = await self.item_repository.count_active_by_owner_id(owner_id)
        
        # Convert to DTOs
        item_dtos = [self._entity_to_dto(item) for item in items]
        
        # Calculate pagination info
        page = (skip // limit) + 1
        has_next = (skip + limit) < total_count
        has_previous = skip > 0
        
        return ItemListDTO(
            items=item_dtos,
            total_count=total_count,
            page=page,
            page_size=limit,
            has_next=has_next,
            has_previous=has_previous
        )
    
    async def get_recent_items(self, owner_id: Optional[uuid.UUID] = None,
                              requesting_user_id: Optional[uuid.UUID] = None,
                              is_superuser: bool = False, days: int = 7,
                              skip: int = 0, limit: int = 100) -> ItemListDTO:
        """
        Get recently created items.
        
        Args:
            owner_id: Optional owner ID to filter by
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            days: Number of days to look back
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            ItemListDTO with recent items
        """
        # Determine owner filter based on permissions
        if owner_id:
            if not self._can_view_user_items(owner_id, requesting_user_id, is_superuser):
                raise PermissionDeniedError("view_items", str(owner_id))
            filter_owner_id = owner_id
        elif is_superuser:
            filter_owner_id = None  # Can see all
        else:
            filter_owner_id = requesting_user_id  # Only own items
        
        # Get recent items
        items = await self.item_repository.get_recent_items(
            filter_owner_id, days, skip, limit
        )
        
        # Convert to DTOs
        item_dtos = [self._entity_to_dto(item) for item in items]
        
        return ItemListDTO(
            items=item_dtos,
            total_count=len(item_dtos),  # For recent items, we don't need total count
            page=1,
            page_size=limit,
            has_next=len(item_dtos) == limit,
            has_previous=False
        )
    
    async def get_item_stats(self, owner_id: Optional[uuid.UUID] = None,
                            requesting_user_id: Optional[uuid.UUID] = None,
                            is_superuser: bool = False) -> ItemStatsDTO:
        """
        Get item statistics.
        
        Args:
            owner_id: Optional owner ID to filter by
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            ItemStatsDTO with statistics
        """
        # Determine owner filter based on permissions
        if owner_id:
            if not self._can_view_user_items(owner_id, requesting_user_id, is_superuser):
                raise PermissionDeniedError("view_items", str(owner_id))
            filter_owner_id = owner_id
        elif is_superuser:
            filter_owner_id = None  # Can see all
        else:
            filter_owner_id = requesting_user_id  # Only own items
        
        if filter_owner_id:
            # User-specific stats
            total_items = await self.item_repository.count_by_owner_id(filter_owner_id)
            active_items = await self.item_repository.count_active_by_owner_id(filter_owner_id)
            deleted_items = total_items - active_items
            
            # Get recent items for recent count
            recent_items = await self.item_repository.get_recent_items(filter_owner_id, 7, 0, 1000)
            recent_items_count = len(recent_items)
            
            # Calculate word count (simplified)
            items = await self.item_repository.get_active_by_owner_id(filter_owner_id, 0, 1000)
            total_word_count = sum(item.get_word_count() for item in items)
            average_word_count = total_word_count / len(items) if items else 0
        else:
            # Global stats (superuser only)
            total_items = await self.item_repository.count()
            # For simplicity, we'll estimate active/deleted split
            active_items = int(total_items * 0.9)  # Assume 90% active
            deleted_items = total_items - active_items
            recent_items_count = 0
            total_word_count = 0
            average_word_count = 0
        
        return ItemStatsDTO(
            total_items=total_items,
            active_items=active_items,
            deleted_items=deleted_items,
            total_word_count=total_word_count,
            average_word_count=average_word_count,
            recent_items_count=recent_items_count
        )
    
    def _can_view_user_items(self, owner_id: uuid.UUID, requesting_user_id: Optional[uuid.UUID],
                            is_superuser: bool) -> bool:
        """
        Check if the requesting user can view items for the owner.
        
        Args:
            owner_id: ID of the item owner
            requesting_user_id: ID of requesting user
            is_superuser: Whether requesting user is superuser
            
        Returns:
            True if items can be viewed, False otherwise
        """
        # Superusers can view any user's items
        if is_superuser:
            return True
        
        # Users can view their own items
        if requesting_user_id and owner_id == requesting_user_id:
            return True
        
        return False
    
    def _entity_to_dto(self, item: Item) -> ItemDTO:
        """
        Convert Item entity to ItemDTO.
        
        Args:
            item: Item entity
            
        Returns:
            ItemDTO
        """
        return ItemDTO(
            id=item.id,
            title=item.title,
            description=item.description,
            owner_id=item.owner_id,
            created_at=item.created_at,
            updated_at=item.updated_at,
            is_deleted=item.is_deleted
        ) 