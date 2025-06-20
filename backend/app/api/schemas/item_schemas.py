"""
Item API Schemas

Request and response schemas for item endpoints.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ItemCreateRequest(BaseModel):
    """Schema for creating a new item."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    title: str = Field(..., min_length=1, max_length=255, description="Item title")
    description: Optional[str] = Field(None, max_length=2000, description="Item description")


class ItemUpdateRequest(BaseModel):
    """Schema for updating an item."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Item title")
    description: Optional[str] = Field(None, max_length=2000, description="Item description")


class ItemResponse(BaseModel):
    """Schema for item response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    title: str
    description: Optional[str]
    owner_id: uuid.UUID
    is_deleted: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ItemSummaryResponse(BaseModel):
    """Schema for item summary response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    title: str
    summary: str
    owner_id: uuid.UUID
    created_at: Optional[datetime] = None
    word_count: int = 0


class ItemListResponse(BaseModel):
    """Schema for paginated item list response."""
    
    items: List[ItemResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


class ItemStatsResponse(BaseModel):
    """Schema for item statistics response."""
    
    total_items: int
    active_items: int
    deleted_items: int
    total_word_count: int
    average_word_count: float
    recent_items_count: int


class ItemSearchRequest(BaseModel):
    """Schema for item search request."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    query: Optional[str] = Field(None, max_length=255, description="Search query")
    title: Optional[str] = Field(None, max_length=255, description="Title filter")
    include_deleted: bool = Field(False, description="Include deleted items")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date (before)")
    updated_after: Optional[datetime] = Field(None, description="Filter by update date (after)")
    updated_before: Optional[datetime] = Field(None, description="Filter by update date (before)")
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of items to return")


class BulkItemOperationRequest(BaseModel):
    """Schema for bulk operations on items."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    item_ids: List[uuid.UUID] = Field(..., min_length=1, max_length=100, description="List of item IDs")
    operation: str = Field(..., description="Operation to perform: 'delete', 'restore', 'update'")
    operation_data: Optional[dict] = Field(None, description="Additional data for the operation")


class BulkItemOperationResponse(BaseModel):
    """Schema for bulk operation response."""
    
    success: bool
    message: str
    processed_count: int
    failed_count: int
    failed_items: Optional[List[uuid.UUID]] = None 