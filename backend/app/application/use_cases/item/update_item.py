"""
Update Item Use Case

Business logic for updating existing items.
"""

import uuid
from typing import Optional

from ...dto.item_dto import UpdateItemDTO, ItemDTO
from ...exceptions.application_exceptions import (
    ValidationError, ItemNotFoundError, PermissionDeniedError
)
from ....domain.repositories.item_repository import ItemRepository


class UpdateItemUseCase:
    """
    Use case for updating existing items.
    
    This use case handles the business logic for item updates,
    including validation, permission checks, and entity modification.
    """
    
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository
    
    async def execute(self, item_id: uuid.UUID, update_item_dto: UpdateItemDTO,
                     requesting_user_id: Optional[uuid.UUID] = None,
                     is_superuser: bool = False) -> ItemDTO:
        """
        Execute the update item use case.
        
        Args:
            item_id: ID of the item to update
            update_item_dto: Data for updating the item
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            ItemDTO containing the updated item data
            
        Raises:
            ValidationError: If input validation fails
            ItemNotFoundError: If item doesn't exist
            PermissionDeniedError: If user lacks permission
        """
        # Validate input
        self._validate_input(update_item_dto)
        
        # Fetch existing item
        item = await self.item_repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(str(item_id))
        
        # Check permissions
        if not item.can_be_modified_by(requesting_user_id or uuid.uuid4(), is_superuser):
            raise PermissionDeniedError("modify_item", str(item_id))
        
        # Apply updates to the entity
        has_changes = False
        
        if update_item_dto.title is not None:
            item.update_title(update_item_dto.title)
            has_changes = True
        
        if update_item_dto.description is not None:
            item.update_description(update_item_dto.description)
            has_changes = True
        
        # Only save if there were actual changes
        if has_changes:
            updated_item = await self.item_repository.update(item)
        else:
            updated_item = item
        
        return self._entity_to_dto(updated_item)
    
    async def bulk_update(self, item_ids: list[uuid.UUID], update_item_dto: UpdateItemDTO,
                         requesting_user_id: Optional[uuid.UUID] = None,
                         is_superuser: bool = False) -> list[ItemDTO]:
        """
        Update multiple items at once.
        
        Args:
            item_ids: List of item IDs to update
            update_item_dto: Data for updating the items
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            List of ItemDTO containing the updated items
            
        Raises:
            ValidationError: If input validation fails
            ItemNotFoundError: If any item doesn't exist
            PermissionDeniedError: If user lacks permission for any item
        """
        # Validate input
        self._validate_input(update_item_dto)
        
        if not item_ids:
            raise ValidationError("item_ids", "At least one item ID is required")
        
        if len(item_ids) > 100:
            raise ValidationError("item_ids", "Maximum 100 items can be updated at once")
        
        # Fetch all items and validate permissions
        items = []
        for item_id in item_ids:
            item = await self.item_repository.get_by_id(item_id)
            if not item:
                raise ItemNotFoundError(str(item_id))
            
            if not item.can_be_modified_by(requesting_user_id or uuid.uuid4(), is_superuser):
                raise PermissionDeniedError("modify_item", str(item_id))
            
            items.append(item)
        
        # Apply updates to all items
        updated_items = []
        for item in items:
            has_changes = False
            
            if update_item_dto.title is not None:
                item.update_title(update_item_dto.title)
                has_changes = True
            
            if update_item_dto.description is not None:
                item.update_description(update_item_dto.description)
                has_changes = True
            
            if has_changes:
                updated_item = await self.item_repository.update(item)
            else:
                updated_item = item
                
            updated_items.append(updated_item)
        
        return [self._entity_to_dto(item) for item in updated_items]
    
    async def restore_item(self, item_id: uuid.UUID, requesting_user_id: Optional[uuid.UUID] = None,
                          is_superuser: bool = False) -> ItemDTO:
        """
        Restore a soft-deleted item.
        
        Args:
            item_id: ID of the item to restore
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            ItemDTO containing the restored item data
            
        Raises:
            ItemNotFoundError: If item doesn't exist
            PermissionDeniedError: If user lacks permission
            ValidationError: If item is not deleted
        """
        # Fetch item (including deleted ones)
        item = await self.item_repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(str(item_id))
        
        # Check permissions
        if not item.can_be_modified_by(requesting_user_id or uuid.uuid4(), is_superuser):
            raise PermissionDeniedError("restore_item", str(item_id))
        
        # Check if item is actually deleted
        if not item.is_deleted:
            raise ValidationError("item_state", "Item is not deleted")
        
        # Restore the item
        item.restore()
        updated_item = await self.item_repository.update(item)
        
        return self._entity_to_dto(updated_item)
    
    def _validate_input(self, dto: UpdateItemDTO) -> None:
        """
        Validate the input DTO.
        
        Args:
            dto: UpdateItemDTO to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # At least one field must be provided for update
        if dto.title is None and dto.description is None:
            raise ValidationError("update_data", "At least one field must be updated")
        
        # Title validation if provided
        if dto.title is not None:
            if not dto.title.strip():
                raise ValidationError("title", "Title cannot be empty")
            
            if len(dto.title.strip()) > 255:
                raise ValidationError("title", "Title too long (max 255 characters)")
        
        # Description validation if provided
        if dto.description is not None and len(dto.description) > 1000:
            raise ValidationError("description", "Description too long (max 1000 characters)")
    
    def _entity_to_dto(self, item) -> ItemDTO:
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