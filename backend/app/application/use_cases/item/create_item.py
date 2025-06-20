"""
Create Item Use Case

Business logic for creating new items.
"""

import uuid
from typing import Optional

from ...dto.item_dto import CreateItemDTO, ItemDTO
from ...exceptions.application_exceptions import (
    ValidationError, UserNotFoundError, PermissionDeniedError
)
from ....domain.entities.item import Item
from ....domain.repositories.item_repository import ItemRepository
from ....domain.repositories.user_repository import UserRepository
from ....domain.exceptions.domain_exceptions import DomainValidationError


class CreateItemUseCase:
    """
    Use case for creating new items.
    
    This use case handles the business logic for item creation,
    including validation, ownership verification, and domain entity creation.
    """
    
    def __init__(self, item_repository: ItemRepository, user_repository: UserRepository):
        self.item_repository = item_repository
        self.user_repository = user_repository
    
    async def execute(self, create_item_dto: CreateItemDTO, 
                     requesting_user_id: Optional[uuid.UUID] = None,
                     is_superuser: bool = False) -> ItemDTO:
        """
        Execute the create item use case.
        
        Args:
            create_item_dto: Data for creating the item
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            ItemDTO containing the created item data
            
        Raises:
            ValidationError: If input validation fails
            UserNotFoundError: If owner user doesn't exist
            PermissionDeniedError: If user lacks permission
        """
        # Validate input
        self._validate_input(create_item_dto)
        
        # Check permissions
        if not self._can_create_item(create_item_dto.owner_id, requesting_user_id, is_superuser):
            raise PermissionDeniedError("create_item", str(create_item_dto.owner_id))
        
        # Verify owner exists
        owner = await self.user_repository.get_by_id(create_item_dto.owner_id)
        if not owner:
            raise UserNotFoundError(str(create_item_dto.owner_id))
        
        # Check if owner can have items
        if not owner.can_access_system():
            raise PermissionDeniedError("create_item", "Owner account is inactive")
        
        # Create item entity
        item = Item(
            id=uuid.uuid4(),
            title=create_item_dto.title,
            description=create_item_dto.description,
            owner_id=create_item_dto.owner_id
        )
        
        # Save to repository
        created_item = await self.item_repository.create(item)
        
        # Convert to DTO
        return self._entity_to_dto(created_item)
    
    def _validate_input(self, dto: CreateItemDTO) -> None:
        """
        Validate the input DTO.
        
        Args:
            dto: CreateItemDTO to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Title is required
        if not dto.title or not dto.title.strip():
            raise ValidationError("title", "Title is required")
        
        # Title length check
        if len(dto.title.strip()) > 255:
            raise ValidationError("title", "Title too long (max 255 characters)")
        
        # Description length check if provided
        if dto.description is not None and len(dto.description) > 1000:
            raise ValidationError("description", "Description too long (max 1000 characters)")
        
        # Owner ID is required
        if not dto.owner_id:
            raise ValidationError("owner_id", "Owner ID is required")
    
    def _can_create_item(self, owner_id: uuid.UUID, requesting_user_id: Optional[uuid.UUID],
                        is_superuser: bool) -> bool:
        """
        Check if the requesting user can create an item for the owner.
        
        Args:
            owner_id: ID of the item owner
            requesting_user_id: ID of requesting user
            is_superuser: Whether requesting user is superuser
            
        Returns:
            True if item can be created, False otherwise
        """
        # Superusers can create items for anyone
        if is_superuser:
            return True
        
        # Users can create items for themselves
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