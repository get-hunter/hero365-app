"""
Delete Item Use Case

Business logic for deleting items.
"""

import uuid
from typing import Optional

from ...exceptions.application_exceptions import (
    ItemNotFoundError, PermissionDeniedError, ValidationError
)
from ....domain.repositories.item_repository import ItemRepository


class DeleteItemUseCase:
    """
    Use case for deleting items.
    
    This use case handles the business logic for item deletion,
    including permission checks and soft/hard delete operations.
    """
    
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository
    
    async def soft_delete(self, item_id: uuid.UUID, requesting_user_id: Optional[uuid.UUID] = None,
                         is_superuser: bool = False) -> bool:
        """
        Soft delete an item (mark as deleted).
        
        Args:
            item_id: ID of the item to delete
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            True if item was successfully deleted
            
        Raises:
            ItemNotFoundError: If item doesn't exist
            PermissionDeniedError: If user lacks permission
            ValidationError: If item is already deleted
        """
        # Fetch item
        item = await self.item_repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(str(item_id))
        
        # Check permissions
        if not item.can_be_deleted_by(requesting_user_id or uuid.uuid4(), is_superuser):
            raise PermissionDeniedError("delete_item", str(item_id))
        
        # Check if item is already deleted
        if item.is_deleted:
            raise ValidationError("item_state", "Item is already deleted")
        
        # Soft delete the item
        item.soft_delete()
        await self.item_repository.update(item)
        
        return True
    
    async def hard_delete(self, item_id: uuid.UUID, requesting_user_id: Optional[uuid.UUID] = None,
                         is_superuser: bool = False) -> bool:
        """
        Hard delete an item (permanently remove).
        
        Args:
            item_id: ID of the item to delete
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            True if item was successfully deleted
            
        Raises:
            ItemNotFoundError: If item doesn't exist
            PermissionDeniedError: If user lacks permission
        """
        # Fetch item
        item = await self.item_repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(str(item_id))
        
        # Check permissions - only superusers can hard delete
        if not is_superuser:
            raise PermissionDeniedError("hard_delete_item", str(item_id))
        
        # Hard delete the item
        await self.item_repository.delete(item_id)
        
        return True
    
    async def bulk_soft_delete(self, item_ids: list[uuid.UUID], 
                              requesting_user_id: Optional[uuid.UUID] = None,
                              is_superuser: bool = False) -> int:
        """
        Soft delete multiple items.
        
        Args:
            item_ids: List of item IDs to delete
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            Number of items successfully deleted
            
        Raises:
            ValidationError: If no items provided or too many items
            ItemNotFoundError: If any item doesn't exist
            PermissionDeniedError: If user lacks permission for any item
        """
        # Validate input
        if not item_ids:
            raise ValidationError("item_ids", "At least one item ID is required")
        
        if len(item_ids) > 100:
            raise ValidationError("item_ids", "Maximum 100 items can be deleted at once")
        
        # Fetch all items and validate permissions
        items_to_delete = []
        for item_id in item_ids:
            item = await self.item_repository.get_by_id(item_id)
            if not item:
                raise ItemNotFoundError(str(item_id))
            
            if not item.can_be_deleted_by(requesting_user_id or uuid.uuid4(), is_superuser):
                raise PermissionDeniedError("delete_item", str(item_id))
            
            # Skip already deleted items
            if not item.is_deleted:
                items_to_delete.append(item)
        
        # Soft delete all items
        deleted_count = 0
        for item in items_to_delete:
            item.soft_delete()
            await self.item_repository.update(item)
            deleted_count += 1
        
        return deleted_count
    
    async def bulk_hard_delete(self, item_ids: list[uuid.UUID], 
                              requesting_user_id: Optional[uuid.UUID] = None,
                              is_superuser: bool = False) -> int:
        """
        Hard delete multiple items.
        
        Args:
            item_ids: List of item IDs to delete
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            Number of items successfully deleted
            
        Raises:
            ValidationError: If no items provided or too many items
            ItemNotFoundError: If any item doesn't exist
            PermissionDeniedError: If user lacks permission
        """
        # Validate input
        if not item_ids:
            raise ValidationError("item_ids", "At least one item ID is required")
        
        if len(item_ids) > 100:
            raise ValidationError("item_ids", "Maximum 100 items can be deleted at once")
        
        # Only superusers can hard delete
        if not is_superuser:
            raise PermissionDeniedError("hard_delete_items")
        
        # Verify all items exist before deleting any
        for item_id in item_ids:
            item = await self.item_repository.get_by_id(item_id)
            if not item:
                raise ItemNotFoundError(str(item_id))
        
        # Hard delete all items
        deleted_count = 0
        for item_id in item_ids:
            await self.item_repository.delete(item_id)
            deleted_count += 1
        
        return deleted_count
    
    async def delete_user_items(self, owner_id: uuid.UUID, 
                               requesting_user_id: Optional[uuid.UUID] = None,
                               is_superuser: bool = False,
                               hard_delete: bool = False) -> int:
        """
        Delete all items belonging to a user.
        
        Args:
            owner_id: ID of the user whose items to delete
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            hard_delete: Whether to hard delete (permanent) or soft delete
            
        Returns:
            Number of items successfully deleted
            
        Raises:
            PermissionDeniedError: If user lacks permission
        """
        # Check permissions
        can_delete_user_items = (
            is_superuser or 
            (requesting_user_id and owner_id == requesting_user_id)
        )
        
        if not can_delete_user_items:
            raise PermissionDeniedError("delete_user_items", str(owner_id))
        
        # Hard delete requires superuser permission
        if hard_delete and not is_superuser:
            raise PermissionDeniedError("hard_delete_user_items", str(owner_id))
        
        # Get all items for the user
        items = await self.item_repository.get_by_owner_id(owner_id, 0, 10000)
        
        deleted_count = 0
        for item in items:
            if hard_delete:
                await self.item_repository.delete(item.id)
            else:
                if not item.is_deleted:
                    item.soft_delete()
                    await self.item_repository.update(item)
            deleted_count += 1
        
        return deleted_count
    
    async def cleanup_deleted_items(self, days_old: int = 30,
                                   requesting_user_id: Optional[uuid.UUID] = None,
                                   is_superuser: bool = False) -> int:
        """
        Permanently delete soft-deleted items older than specified days.
        
        Args:
            days_old: Number of days after which to permanently delete items
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            Number of items permanently deleted
            
        Raises:
            PermissionDeniedError: If user lacks permission
        """
        # Only superusers can perform cleanup
        if not is_superuser:
            raise PermissionDeniedError("cleanup_items")
        
        # Get old deleted items
        old_deleted_items = await self.item_repository.get_old_deleted_items(days_old)
        
        # Permanently delete them
        deleted_count = 0
        for item in old_deleted_items:
            await self.item_repository.delete(item.id)
            deleted_count += 1
        
        return deleted_count 