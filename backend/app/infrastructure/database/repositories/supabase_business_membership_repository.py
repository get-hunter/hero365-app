"""
Supabase Business Membership Repository Implementation

Repository implementation using Supabase client SDK for business membership operations.
"""

import uuid
from typing import Optional, List
from datetime import datetime
import json

from supabase import Client

from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.business_membership import BusinessMembership, BusinessRole
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DuplicateEntityError, DatabaseError
)


class SupabaseBusinessMembershipRepository(BusinessMembershipRepository):
    """
    Supabase client implementation of BusinessMembershipRepository.
    
    This repository uses Supabase client SDK for all business membership database operations.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "business_memberships"
    
    async def create(self, membership: BusinessMembership) -> BusinessMembership:
        """Create a new business membership in Supabase."""
        try:
            membership_data = self._membership_to_dict(membership)
            
            response = self.client.table(self.table_name).insert(membership_data).execute()
            
            if response.data:
                return self._dict_to_membership(response.data[0])
            else:
                raise DatabaseError("Failed to create membership - no data returned")
                
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateEntityError(f"User is already a member of this business")
            raise DatabaseError(f"Failed to create membership: {str(e)}")
    
    async def get_by_id(self, membership_id: uuid.UUID) -> Optional[BusinessMembership]:
        """Get business membership by ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq("id", str(membership_id)).execute()
            
            if response.data:
                return self._dict_to_membership(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get membership by ID: {str(e)}")
    
    async def get_by_business_and_user(self, business_id: uuid.UUID, user_id: str) -> Optional[BusinessMembership]:
        """Get business membership by business ID and user ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("user_id", user_id).execute()
            
            if response.data:
                return self._dict_to_membership(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get membership by business and user: {str(e)}")
    
    async def get_by_user_and_business(self, user_id: str, business_id: uuid.UUID) -> Optional[BusinessMembership]:
        """Get business membership by user ID and business ID (alias for get_by_business_and_user)."""
        return await self.get_by_business_and_user(business_id, user_id)
    
    async def get_business_members(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[BusinessMembership]:
        """Get all members of a specific business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).range(skip, skip + limit - 1).order("joined_date", desc=True).execute()
            
            return [self._dict_to_membership(membership_data) for membership_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get business members: {str(e)}")
    
    async def get_user_memberships(self, user_id: str, skip: int = 0, limit: int = 100) -> List[BusinessMembership]:
        """Get all business memberships for a specific user."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "user_id", user_id
            ).range(skip, skip + limit - 1).order("joined_date", desc=True).execute()
            
            return [self._dict_to_membership(membership_data) for membership_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user memberships: {str(e)}")
    
    async def get_active_business_members(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[BusinessMembership]:
        """Get active members of a specific business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("is_active", True).range(skip, skip + limit - 1).order("joined_date", desc=True).execute()
            
            return [self._dict_to_membership(membership_data) for membership_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get active business members: {str(e)}")
    
    async def get_members_by_role(self, business_id: uuid.UUID, role: BusinessRole, skip: int = 0, limit: int = 100) -> List[BusinessMembership]:
        """Get business members by role."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("role", role.value).range(skip, skip + limit - 1).order("joined_date", desc=True).execute()
            
            return [self._dict_to_membership(membership_data) for membership_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get members by role: {str(e)}")
    
    async def get_business_owner(self, business_id: uuid.UUID) -> Optional[BusinessMembership]:
        """Get the owner membership for a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("role", BusinessRole.OWNER.value).execute()
            
            if response.data:
                return self._dict_to_membership(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get business owner: {str(e)}")
    
    async def update(self, membership: BusinessMembership) -> BusinessMembership:
        """Update an existing business membership."""
        try:
            membership_data = self._membership_to_dict(membership)
            
            response = self.client.table(self.table_name).update(membership_data).eq(
                "id", str(membership.id)
            ).execute()
            
            if response.data:
                return self._dict_to_membership(response.data[0])
            else:
                raise EntityNotFoundError(f"Membership with ID {membership.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update membership: {str(e)}")
    
    async def delete(self, membership_id: uuid.UUID) -> bool:
        """Delete a business membership (hard delete)."""
        try:
            response = self.client.table(self.table_name).delete().eq("id", str(membership_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete membership: {str(e)}")
    
    async def deactivate(self, membership_id: uuid.UUID) -> bool:
        """Deactivate a business membership (soft delete)."""
        try:
            response = self.client.table(self.table_name).update({
                "is_active": False
            }).eq("id", str(membership_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to deactivate membership: {str(e)}")
    
    async def count_business_members(self, business_id: uuid.UUID) -> int:
        """Get count of all members in a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count business members: {str(e)}")
    
    async def count_active_business_members(self, business_id: uuid.UUID) -> int:
        """Get count of active members in a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).eq("is_active", True).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count active business members: {str(e)}")
    
    async def count_user_memberships(self, user_id: str) -> int:
        """Get count of business memberships for a user."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("user_id", user_id).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count user memberships: {str(e)}")
    
    async def exists(self, membership_id: uuid.UUID) -> bool:
        """Check if a business membership exists."""
        try:
            response = self.client.table(self.table_name).select("id").eq("id", str(membership_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check membership existence: {str(e)}")
    
    async def user_is_member(self, business_id: uuid.UUID, user_id: str) -> bool:
        """Check if a user is a member of a business."""
        try:
            response = self.client.table(self.table_name).select("id").eq(
                "business_id", str(business_id)
            ).eq("user_id", user_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check user membership: {str(e)}")
    
    async def user_is_active_member(self, business_id: uuid.UUID, user_id: str) -> bool:
        """Check if a user is an active member of a business."""
        try:
            response = self.client.table(self.table_name).select("id").eq(
                "business_id", str(business_id)
            ).eq("user_id", user_id).eq("is_active", True).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check active user membership: {str(e)}")
    
    async def get_members_with_permission(self, business_id: uuid.UUID, permission: str, skip: int = 0, limit: int = 100) -> List[BusinessMembership]:
        """Get business members who have a specific permission."""
        try:
            # Use Supabase JSONB contains operator to check permissions
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).contains("permissions", [permission]).eq("is_active", True).range(
                skip, skip + limit - 1
            ).order("joined_date", desc=True).execute()
            
            return [self._dict_to_membership(membership_data) for membership_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get members with permission: {str(e)}")
    
    def _membership_to_dict(self, membership: BusinessMembership) -> dict:
        """Convert BusinessMembership entity to dictionary for Supabase."""
        return {
            "id": str(membership.id),
            "business_id": str(membership.business_id),
            "user_id": membership.user_id,
            "role": membership.role.value,
            "permissions": membership.permissions,  # Send as list directly, not JSON string
            "joined_date": membership.joined_date.isoformat(),
            "invited_date": membership.invited_date.isoformat() if membership.invited_date else None,
            "invited_by": membership.invited_by,
            "is_active": membership.is_active,
            "department_id": str(membership.department_id) if membership.department_id else None,
            "job_title": membership.job_title
        }
    
    def _dict_to_membership(self, data: dict) -> BusinessMembership:
        """Convert dictionary from Supabase to BusinessMembership entity."""
        return BusinessMembership(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            user_id=data["user_id"],
            role=BusinessRole(data["role"]),
            permissions=data["permissions"],  # Already a list from JSONB, no need to parse
            joined_date=datetime.fromisoformat(data["joined_date"]),
            invited_date=datetime.fromisoformat(data["invited_date"]) if data.get("invited_date") else None,
            invited_by=data.get("invited_by"),
            is_active=data.get("is_active", True),
            department_id=uuid.UUID(data["department_id"]) if data.get("department_id") else None,
            job_title=data.get("job_title")
        ) 