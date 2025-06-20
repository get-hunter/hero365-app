import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Depends

from app.api.deps import CurrentUser
from app.api.controllers.item_controller import ItemController
from app.api.schemas.item_schemas import (
    ItemCreateRequest, ItemUpdateRequest, ItemResponse, 
    ItemListResponse, ItemSearchRequest
)
from app.api.schemas.common_schemas import Message

router = APIRouter(prefix="/items", tags=["items"])


def get_item_controller() -> ItemController:
    """Dependency to get item controller."""
    return ItemController()


@router.get("/", response_model=ItemListResponse)
async def read_items(
    current_user: CurrentUser, 
    skip: int = 0, 
    limit: int = 100,
    controller: ItemController = Depends(get_item_controller)
) -> ItemListResponse:
    """
    Retrieve items using clean architecture.
    """
    # Extract user info from dict
    is_superuser = current_user.get("app_metadata", {}).get("is_superuser", False)
    current_user_id = uuid.UUID(current_user["id"])
    
    # Use controller
    return await controller.get_items(
        current_user_id=current_user_id,
        is_superuser=is_superuser,
        skip=skip,
        limit=limit
    )


@router.get("/{id}", response_model=ItemResponse)
async def read_item(
    current_user: CurrentUser, 
    id: uuid.UUID,
    controller: ItemController = Depends(get_item_controller)
) -> ItemResponse:
    """
    Get item by ID using clean architecture.
    """
    # Extract user info
    current_user_id = uuid.UUID(current_user["id"])
    
    # Use controller
    return await controller.get_item(
        item_id=id,
        current_user_id=current_user_id
    )


@router.post("/", response_model=ItemResponse)
async def create_item(
    *, 
    current_user: CurrentUser, 
    item_in: ItemCreateRequest,
    controller: ItemController = Depends(get_item_controller)
) -> ItemResponse:
    """
    Create new item using clean architecture.
    """
    # Extract user info
    current_user_id = uuid.UUID(current_user["id"])
    
    # Use controller
    return await controller.create_item(
        request=item_in,
        current_user_id=current_user_id
    )


@router.put("/{id}", response_model=ItemResponse)
async def update_item(
    *,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdateRequest,
    controller: ItemController = Depends(get_item_controller)
) -> ItemResponse:
    """
    Update an item using clean architecture.
    """
    # Extract user info
    current_user_id = uuid.UUID(current_user["id"])
    
    # Use controller
    return await controller.update_item(
        item_id=id,
        request=item_in,
        current_user_id=current_user_id
    )


@router.delete("/{id}")
async def delete_item(
    current_user: CurrentUser, 
    id: uuid.UUID,
    controller: ItemController = Depends(get_item_controller)
) -> dict:
    """
    Delete an item using clean architecture.
    """
    # Extract user info
    current_user_id = uuid.UUID(current_user["id"])
    
    # Use controller
    return await controller.delete_item(
        item_id=id,
        current_user_id=current_user_id
    )
