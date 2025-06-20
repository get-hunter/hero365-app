"""
Item Controller

Clean architecture controller for handling item-related HTTP requests.
"""

import uuid
from typing import Any
from fastapi import HTTPException, status

from ..schemas.item_schemas import (
    ItemCreateRequest, ItemUpdateRequest, ItemResponse, ItemListResponse,
    ItemSearchRequest, ItemStatsResponse, BulkItemOperationRequest,
    BulkItemOperationResponse
)
from ...application.dto.item_dto import CreateItemDTO, UpdateItemDTO, ItemSearchDTO
from ...application.exceptions.application_exceptions import (
    PermissionDeniedError, UserNotFoundError, ItemNotFoundError
)
from ...domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DomainValidationError
)
from ...infrastructure.config.dependency_injection import get_container


class ItemController:
    """
    Controller for item-related operations.
    
    This controller handles HTTP requests and delegates business logic to use cases.
    """
    
    def __init__(self):
        self.container = get_container()
    
    async def create_item(self, request: ItemCreateRequest, current_user_id: uuid.UUID) -> ItemResponse:
        """
        Create a new item.
        
        Args:
            request: Item creation request
            current_user_id: ID of the user creating the item
            
        Returns:
            Created item response
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            # Get use case from container
            create_item_use_case = self.container.get_create_item_use_case()
            
            # Create DTO from request
            create_dto = CreateItemDTO(
                title=request.title,
                owner_id=current_user_id,
                description=request.description
            )
            
            # Execute use case
            item_dto = await create_item_use_case.execute(create_dto, current_user_id)
            
            # Convert DTO to response schema
            return ItemResponse(
                id=item_dto.id,
                title=item_dto.title,
                description=item_dto.description,
                owner_id=item_dto.owner_id,
                is_deleted=item_dto.is_deleted,
                created_at=item_dto.created_at,
                updated_at=item_dto.updated_at
            )
            
        except DomainValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create item: {str(e)}"
            )
    
    async def get_item(self, item_id: uuid.UUID, current_user_id: uuid.UUID) -> ItemResponse:
        """
        Get a single item by ID.
        
        Args:
            item_id: ID of the item to retrieve
            current_user_id: ID of the requesting user
            
        Returns:
            Item response
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            # Get use case from container
            get_items_use_case = self.container.get_get_items_use_case()
            
            # Execute use case to get single item
            result = await get_items_use_case.execute(
                current_user_id=current_user_id,
                item_id=item_id
            )
            
            if not result.items:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found"
                )
            
            # Convert DTO to response schema
            item_dto = result.items[0]
            return ItemResponse(
                id=item_dto.id,
                title=item_dto.title,
                description=item_dto.description,
                owner_id=item_dto.owner_id,
                is_deleted=item_dto.is_deleted,
                created_at=item_dto.created_at,
                updated_at=item_dto.updated_at
            )
            
        except EntityNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        except PermissionDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get item: {str(e)}"
            )
    
    async def get_items(
        self, 
        current_user_id: uuid.UUID, 
        is_superuser: bool = False,
        skip: int = 0, 
        limit: int = 100
    ) -> ItemListResponse:
        """
        Get paginated list of items.
        
        Args:
            current_user_id: ID of the requesting user
            is_superuser: Whether the user is a superuser
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            Paginated item list response
        """
        try:
            # Get use case from container
            get_items_use_case = self.container.get_get_items_use_case()
            
            # Execute use case
            if is_superuser:
                result = await get_items_use_case.execute(
                    current_user_id=current_user_id,
                    skip=skip,
                    limit=limit,
                    admin_access=True
                )
            else:
                result = await get_items_use_case.execute(
                    current_user_id=current_user_id,
                    owner_id=current_user_id,
                    skip=skip,
                    limit=limit
                )
            
            # Convert DTOs to response schemas
            items = [
                ItemResponse(
                    id=item.id,
                    title=item.title,
                    description=item.description,
                    owner_id=item.owner_id,
                    is_deleted=item.is_deleted,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                )
                for item in result.items
            ]
            
            # Calculate pagination info
            total_pages = (result.total_count + limit - 1) // limit
            current_page = (skip // limit) + 1
            has_next = current_page < total_pages
            has_previous = current_page > 1
            
            return ItemListResponse(
                items=items,
                total_count=result.total_count,
                page=current_page,
                page_size=limit,
                has_next=has_next,
                has_previous=has_previous
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get items: {str(e)}"
            )
    
    async def update_item(
        self, 
        item_id: uuid.UUID, 
        request: ItemUpdateRequest, 
        current_user_id: uuid.UUID
    ) -> ItemResponse:
        """
        Update an existing item.
        
        Args:
            item_id: ID of the item to update
            request: Item update request
            current_user_id: ID of the requesting user
            
        Returns:
            Updated item response
        """
        try:
            # Get use case from container
            update_item_use_case = self.container.get_update_item_use_case()
            
            # Create DTO from request
            update_dict = request.model_dump(exclude_unset=True)
            update_dto = UpdateItemDTO(
                item_id=item_id,
                **update_dict
            )
            
            # Execute use case
            item_dto = await update_item_use_case.execute(update_dto, current_user_id)
            
            # Convert DTO to response schema
            return ItemResponse(
                id=item_dto.id,
                title=item_dto.title,
                description=item_dto.description,
                owner_id=item_dto.owner_id,
                is_deleted=item_dto.is_deleted,
                created_at=item_dto.created_at,
                updated_at=item_dto.updated_at
            )
            
        except EntityNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        except PermissionDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        except DomainValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update item: {str(e)}"
            )
    
    async def delete_item(self, item_id: uuid.UUID, current_user_id: uuid.UUID) -> dict:
        """
        Delete an item.
        
        Args:
            item_id: ID of the item to delete
            current_user_id: ID of the requesting user
            
        Returns:
            Success message
        """
        try:
            # Get use case from container
            delete_item_use_case = self.container.get_delete_item_use_case()
            
            # Execute use case
            await delete_item_use_case.execute(item_id, current_user_id)
            
            return {"message": "Item deleted successfully"}
            
        except EntityNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        except PermissionDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete item: {str(e)}"
            )
    
    async def search_items(
        self, 
        search_request: ItemSearchRequest, 
        current_user_id: uuid.UUID,
        is_superuser: bool = False
    ) -> ItemListResponse:
        """
        Search items with filters.
        
        Args:
            search_request: Search criteria
            current_user_id: ID of the requesting user
            is_superuser: Whether the user is a superuser
            
        Returns:
            Filtered item list response
        """
        try:
            # Get use case from container
            get_items_use_case = self.container.get_get_items_use_case()
            
            # Create search DTO
            search_dto = ItemSearchDTO(
                query=search_request.query,
                title=search_request.title,
                owner_id=search_request.owner_id if is_superuser else current_user_id,
                include_deleted=search_request.include_deleted if is_superuser else False,
                created_after=search_request.created_after,
                created_before=search_request.created_before,
                updated_after=search_request.updated_after,
                updated_before=search_request.updated_before,
                skip=search_request.skip,
                limit=search_request.limit
            )
            
            # Execute search
            result = await get_items_use_case.execute_search(search_dto, current_user_id)
            
            # Convert DTOs to response schemas
            items = [
                ItemResponse(
                    id=item.id,
                    title=item.title,
                    description=item.description,
                    owner_id=item.owner_id,
                    is_deleted=item.is_deleted,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                )
                for item in result.items
            ]
            
            # Calculate pagination info
            total_pages = (result.total_count + search_request.limit - 1) // search_request.limit
            current_page = (search_request.skip // search_request.limit) + 1
            has_next = current_page < total_pages
            has_previous = current_page > 1
            
            return ItemListResponse(
                items=items,
                total_count=result.total_count,
                page=current_page,
                page_size=search_request.limit,
                has_next=has_next,
                has_previous=has_previous
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search items: {str(e)}"
            ) 