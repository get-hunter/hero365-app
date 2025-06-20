"""
Supabase Item Repository Implementation

Repository implementation using Supabase client SDK instead of SQLModel/SQLAlchemy.
This leverages Supabase's built-in features like RLS, real-time subscriptions, and auth integration.
"""

import uuid
from typing import Optional, List
from datetime import datetime, timedelta

from supabase import Client

from ....domain.repositories.item_repository import ItemRepository
from ....domain.entities.item import Item
from ....domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DatabaseError
)


class SupabaseItemRepository(ItemRepository):
    """
    Supabase client implementation of ItemRepository.
    
    This repository uses Supabase client SDK for all database operations,
    leveraging RLS, real-time features, and built-in auth integration.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "items"
    
    async def create(self, item: Item) -> Item:
        """Create a new item in Supabase."""
        try:
            item_data = self._item_to_dict(item)
            
            response = self.client.table(self.table_name).insert(item_data).execute()
            
            if response.data:
                return self._dict_to_item(response.data[0])
            else:
                raise DatabaseError("Failed to create item - no data returned")
                
        except Exception as e:
            raise DatabaseError(f"Failed to create item: {str(e)}")
    
    async def get_by_id(self, item_id: uuid.UUID) -> Optional[Item]:
        """Get item by ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq("id", str(item_id)).execute()
            
            if response.data:
                return self._dict_to_item(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get item by ID: {str(e)}")
    
    async def update(self, item: Item) -> Item:
        """Update item in Supabase."""
        try:
            item_data = self._item_to_dict(item)
            item_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table(self.table_name).update(item_data).eq("id", str(item.id)).execute()
            
            if response.data:
                return self._dict_to_item(response.data[0])
            else:
                raise EntityNotFoundError(f"Item with ID {item.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update item: {str(e)}")
    
    async def delete(self, item_id: uuid.UUID) -> bool:
        """Delete item from Supabase."""
        try:
            response = self.client.table(self.table_name).delete().eq("id", str(item_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete item: {str(e)}")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Item]:
        """Get all items with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").range(skip, skip + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_item(item_data) for item_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get all items: {str(e)}")
    
    async def get_by_owner_id(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Item]:
        """Get items by owner ID with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").eq("owner_id", str(owner_id)).range(skip, skip + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_item(item_data) for item_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get items by owner: {str(e)}")
    
    async def get_active_by_owner_id(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Item]:
        """Get active items by owner ID with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").eq("owner_id", str(owner_id)).eq("is_deleted", False).range(skip, skip + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_item(item_data) for item_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get active items by owner: {str(e)}")
    
    async def get_deleted_by_owner_id(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Item]:
        """Get deleted items by owner ID with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").eq("owner_id", str(owner_id)).eq("is_deleted", True).range(skip, skip + limit - 1).order("deleted_at", desc=True).execute()
            
            return [self._dict_to_item(item_data) for item_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get deleted items by owner: {str(e)}")
    
    async def search_by_content(self, query: str, owner_id: Optional[uuid.UUID] = None, 
                               skip: int = 0, limit: int = 100) -> List[Item]:
        """Search items by content."""
        try:
            # Build the search query
            search_query = self.client.table(self.table_name).select("*").or_(
                f"title.ilike.%{query}%,description.ilike.%{query}%"
            )
            
            if owner_id:
                search_query = search_query.eq("owner_id", str(owner_id))
            
            response = search_query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_item(item_data) for item_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search items: {str(e)}")
    
    async def search_by_title(self, title: str, owner_id: Optional[uuid.UUID] = None, 
                             skip: int = 0, limit: int = 100) -> List[Item]:
        """Search items by title."""
        try:
            # Build the search query
            search_query = self.client.table(self.table_name).select("*").ilike("title", f"%{title}%")
            
            if owner_id:
                search_query = search_query.eq("owner_id", str(owner_id))
            
            response = search_query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_item(item_data) for item_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search items by title: {str(e)}")
    
    async def get_updated_items(self, owner_id: Optional[uuid.UUID] = None,
                               days: int = 7, skip: int = 0, limit: int = 100) -> List[Item]:
        """Get recently updated items."""
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            query = self.client.table(self.table_name).select("*").gte("updated_at", cutoff_date)
            
            if owner_id:
                query = query.eq("owner_id", str(owner_id))
            
            response = query.range(skip, skip + limit - 1).order("updated_at", desc=True).execute()
            
            return [self._dict_to_item(item_data) for item_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get updated items: {str(e)}")
    
    async def count(self) -> int:
        """Get total count of items."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count items: {str(e)}")
    
    async def count_by_owner_id(self, owner_id: uuid.UUID) -> int:
        """Get count of items by owner."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("owner_id", str(owner_id)).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count items by owner: {str(e)}")
    
    async def count_active_by_owner_id(self, owner_id: uuid.UUID) -> int:
        """Get count of active items by owner."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("owner_id", str(owner_id)).eq("is_deleted", False).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count active items by owner: {str(e)}")
    
    async def get_recent_items(self, owner_id: Optional[uuid.UUID] = None, days: int = 7, 
                              skip: int = 0, limit: int = 100) -> List[Item]:
        """Get recently created items."""
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            query = self.client.table(self.table_name).select("*").gte("created_at", cutoff_date)
            
            if owner_id:
                query = query.eq("owner_id", str(owner_id))
            
            response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_item(item_data) for item_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get recent items: {str(e)}")
    
    async def get_old_deleted_items(self, days: int = 30) -> List[Item]:
        """Get old deleted items for cleanup."""
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            response = self.client.table(self.table_name).select("*").eq("is_deleted", True).lte("deleted_at", cutoff_date).order("deleted_at").execute()
            
            return [self._dict_to_item(item_data) for item_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get old deleted items: {str(e)}")
    
    async def bulk_update(self, items: List[Item]) -> List[Item]:
        """Update multiple items in a single transaction."""
        try:
            updated_items = []
            
            # Supabase doesn't have bulk update in the same way, so we'll do individual updates
            # In a real implementation, you might want to use stored procedures or batch operations
            for item in items:
                updated_item = await self.update(item)
                updated_items.append(updated_item)
            
            return updated_items
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk update items: {str(e)}")
    
    async def bulk_delete(self, item_ids: List[uuid.UUID]) -> int:
        """Delete multiple items by IDs."""
        try:
            deleted_count = 0
            
            # Supabase supports IN queries for bulk operations
            str_ids = [str(item_id) for item_id in item_ids]
            response = self.client.table(self.table_name).delete().in_("id", str_ids).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk delete items: {str(e)}")
    
    async def exists(self, item_id: uuid.UUID) -> bool:
        """Check if item exists."""
        try:
            response = self.client.table(self.table_name).select("id").eq("id", str(item_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check item existence: {str(e)}")
    
    async def get_items_by_title_pattern(self, pattern: str, owner_id: Optional[uuid.UUID] = None,
                                        skip: int = 0, limit: int = 100) -> List[Item]:
        """Get items matching title pattern."""
        try:
            query = self.client.table(self.table_name).select("*").ilike("title", f"%{pattern}%")
            
            if owner_id:
                query = query.eq("owner_id", str(owner_id))
            
            response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_item(item_data) for item_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get items by title pattern: {str(e)}")
    
    async def bulk_delete_by_owner_id(self, owner_id: uuid.UUID) -> int:
        """Soft delete all items belonging to an owner."""
        try:
            # Update items to mark them as deleted
            update_data = {
                "is_deleted": True,
                "deleted_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table(self.table_name).update(update_data).eq("owner_id", str(owner_id)).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk delete items by owner: {str(e)}")
    
    async def permanently_delete_by_owner_id(self, owner_id: uuid.UUID) -> int:
        """Permanently delete all items belonging to an owner."""
        try:
            response = self.client.table(self.table_name).delete().eq("owner_id", str(owner_id)).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to permanently delete items by owner: {str(e)}")
    
    def _item_to_dict(self, item: Item) -> dict:
        """Convert Item domain entity to dictionary for Supabase."""
        return {
            "id": str(item.id),
            "title": item.title,
            "description": item.description,
            "owner_id": str(item.owner_id),
            "is_deleted": item.is_deleted,
            "deleted_at": item.deleted_at.isoformat() if item.deleted_at else None,
            "created_at": item.created_at.isoformat() if item.created_at else datetime.utcnow().isoformat(),
            "updated_at": item.updated_at.isoformat() if item.updated_at else datetime.utcnow().isoformat(),
        }
    
    def _dict_to_item(self, data: dict) -> Item:
        """Convert dictionary data from Supabase to Item domain entity."""
        return Item(
            id=uuid.UUID(data["id"]),
            title=data["title"],
            description=data.get("description"),
            owner_id=uuid.UUID(data["owner_id"]),
            is_deleted=data.get("is_deleted", False),
            deleted_at=datetime.fromisoformat(data["deleted_at"].replace("Z", "+00:00")) if data.get("deleted_at") else None,
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")) if data.get("updated_at") else None,
        ) 