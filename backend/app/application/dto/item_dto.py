"""
Item Data Transfer Objects

DTOs for transferring item data between application layers.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CreateItemDTO:
    """DTO for creating a new item."""
    
    title: str
    owner_id: uuid.UUID
    description: Optional[str] = None


@dataclass
class UpdateItemDTO:
    """DTO for updating item information."""
    
    title: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ItemDTO:
    """DTO for item data transfer."""
    
    id: uuid.UUID
    title: str
    description: Optional[str]
    owner_id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False


@dataclass
class ItemSummaryDTO:
    """DTO for item summary information (limited data)."""
    
    id: uuid.UUID
    title: str
    summary: str
    owner_id: uuid.UUID
    created_at: Optional[datetime] = None
    word_count: int = 0


@dataclass
class ItemListDTO:
    """DTO for paginated item list."""
    
    items: list[ItemDTO]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


@dataclass
class ItemSearchDTO:
    """DTO for item search parameters."""
    
    query: Optional[str] = None
    title: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None
    include_deleted: bool = False
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    skip: int = 0
    limit: int = 100


@dataclass
class ItemStatsDTO:
    """DTO for item statistics."""
    
    total_items: int
    active_items: int
    deleted_items: int
    total_word_count: int
    average_word_count: float
    recent_items_count: int  # Items created in last 7 days


@dataclass
class BulkItemOperationDTO:
    """DTO for bulk operations on items."""
    
    item_ids: list[uuid.UUID]
    operation: str  # 'delete', 'restore', 'update'
    operation_data: Optional[dict] = None 