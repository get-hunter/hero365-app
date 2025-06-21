"""
Supabase Business Invitation Repository Implementation

Repository implementation using Supabase client SDK for business invitation operations.
"""

import uuid
from typing import Optional, List
from datetime import datetime, timedelta
import json

from supabase import Client

from ....domain.repositories.business_invitation_repository import BusinessInvitationRepository
from ....domain.entities.business_invitation import BusinessInvitation, InvitationStatus, BusinessRole
from ....domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DuplicateEntityError, DatabaseError
)


class SupabaseBusinessInvitationRepository(BusinessInvitationRepository):
    """
    Supabase client implementation of BusinessInvitationRepository.
    
    This repository uses Supabase client SDK for all business invitation database operations.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "business_invitations"
    
    async def create(self, invitation: BusinessInvitation) -> BusinessInvitation:
        """Create a new business invitation in Supabase."""
        try:
            invitation_data = self._invitation_to_dict(invitation)
            
            response = self.client.table(self.table_name).insert(invitation_data).execute()
            
            if response.data:
                return self._dict_to_invitation(response.data[0])
            else:
                raise DatabaseError("Failed to create invitation - no data returned")
                
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateEntityError(f"Active invitation already exists for this recipient")
            raise DatabaseError(f"Failed to create invitation: {str(e)}")
    
    async def get_by_id(self, invitation_id: uuid.UUID) -> Optional[BusinessInvitation]:
        """Get business invitation by ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq("id", str(invitation_id)).execute()
            
            if response.data:
                return self._dict_to_invitation(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invitation by ID: {str(e)}")
    
    async def get_business_invitations(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """Get all invitations for a specific business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).range(skip, skip + limit - 1).order("invitation_date", desc=True).execute()
            
            return [self._dict_to_invitation(invitation_data) for invitation_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get business invitations: {str(e)}")
    
    async def get_pending_business_invitations(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """Get pending invitations for a specific business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", InvitationStatus.PENDING.value).range(
                skip, skip + limit - 1
            ).order("invitation_date", desc=True).execute()
            
            return [self._dict_to_invitation(invitation_data) for invitation_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get pending business invitations: {str(e)}")
    
    async def get_user_invitations_by_email(self, email: str, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """Get all invitations for a user by email."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "invited_email", email
            ).range(skip, skip + limit - 1).order("invitation_date", desc=True).execute()
            
            return [self._dict_to_invitation(invitation_data) for invitation_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user invitations by email: {str(e)}")
    
    async def get_user_invitations_by_phone(self, phone: str, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """Get all invitations for a user by phone."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "invited_phone", phone
            ).range(skip, skip + limit - 1).order("invitation_date", desc=True).execute()
            
            return [self._dict_to_invitation(invitation_data) for invitation_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user invitations by phone: {str(e)}")
    
    async def get_pending_user_invitations_by_email(self, email: str, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """Get pending invitations for a user by email."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "invited_email", email
            ).eq("status", InvitationStatus.PENDING.value).range(
                skip, skip + limit - 1
            ).order("invitation_date", desc=True).execute()
            
            return [self._dict_to_invitation(invitation_data) for invitation_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get pending user invitations by email: {str(e)}")
    
    async def get_pending_user_invitations_by_phone(self, phone: str, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """Get pending invitations for a user by phone."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "invited_phone", phone
            ).eq("status", InvitationStatus.PENDING.value).range(
                skip, skip + limit - 1
            ).order("invitation_date", desc=True).execute()
            
            return [self._dict_to_invitation(invitation_data) for invitation_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get pending user invitations by phone: {str(e)}")
    
    async def get_invitations_by_status(self, status: InvitationStatus, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """Get invitations by status."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "status", status.value
            ).range(skip, skip + limit - 1).order("invitation_date", desc=True).execute()
            
            return [self._dict_to_invitation(invitation_data) for invitation_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invitations by status: {str(e)}")
    
    async def get_expired_invitations(self, skip: int = 0, limit: int = 100) -> List[BusinessInvitation]:
        """Get expired invitations that haven't been marked as expired."""
        try:
            now = datetime.utcnow()
            
            response = self.client.table(self.table_name).select("*").eq(
                "status", InvitationStatus.PENDING.value
            ).lt("expiry_date", now.isoformat()).range(
                skip, skip + limit - 1
            ).order("expiry_date", desc=True).execute()
            
            return [self._dict_to_invitation(invitation_data) for invitation_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get expired invitations: {str(e)}")
    
    async def update(self, invitation: BusinessInvitation) -> BusinessInvitation:
        """Update an existing business invitation."""
        try:
            invitation_data = self._invitation_to_dict(invitation)
            
            response = self.client.table(self.table_name).update(invitation_data).eq(
                "id", str(invitation.id)
            ).execute()
            
            if response.data:
                return self._dict_to_invitation(response.data[0])
            else:
                raise EntityNotFoundError(f"Invitation with ID {invitation.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update invitation: {str(e)}")
    
    async def delete(self, invitation_id: uuid.UUID) -> bool:
        """Delete a business invitation."""
        try:
            response = self.client.table(self.table_name).delete().eq("id", str(invitation_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete invitation: {str(e)}")
    
    async def count_business_invitations(self, business_id: uuid.UUID) -> int:
        """Get count of all invitations for a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count business invitations: {str(e)}")
    
    async def count_pending_business_invitations(self, business_id: uuid.UUID) -> int:
        """Get count of pending invitations for a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).eq("status", InvitationStatus.PENDING.value).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count pending business invitations: {str(e)}")
    
    async def count_user_invitations_by_email(self, email: str) -> int:
        """Get count of invitations for a user by email."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("invited_email", email).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count user invitations by email: {str(e)}")
    
    async def count_user_invitations_by_phone(self, phone: str) -> int:
        """Get count of invitations for a user by phone."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("invited_phone", phone).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count user invitations by phone: {str(e)}")
    
    async def exists(self, invitation_id: uuid.UUID) -> bool:
        """Check if a business invitation exists."""
        try:
            response = self.client.table(self.table_name).select("id").eq("id", str(invitation_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check invitation existence: {str(e)}")
    
    async def has_pending_invitation(self, business_id: uuid.UUID, email: Optional[str] = None, phone: Optional[str] = None) -> bool:
        """Check if there's a pending invitation for a business and contact method."""
        try:
            query = self.client.table(self.table_name).select("id").eq(
                "business_id", str(business_id)
            ).eq("status", InvitationStatus.PENDING.value)
            
            if email:
                query = query.eq("invited_email", email)
            elif phone:
                query = query.eq("invited_phone", phone)
            else:
                return False
            
            response = query.execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check pending invitation: {str(e)}")
    
    async def mark_expired_invitations(self) -> int:
        """Mark all expired pending invitations as expired."""
        try:
            now = datetime.utcnow()
            
            response = self.client.table(self.table_name).update({
                "status": InvitationStatus.EXPIRED.value
            }).eq("status", InvitationStatus.PENDING.value).lt("expiry_date", now.isoformat()).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to mark expired invitations: {str(e)}")
    
    async def cleanup_expired_invitations(self, days_old: int = 30) -> int:
        """Delete expired invitations older than specified days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            response = self.client.table(self.table_name).delete().in_(
                "status", [InvitationStatus.EXPIRED.value, InvitationStatus.DECLINED.value, InvitationStatus.CANCELLED.value]
            ).lt("invitation_date", cutoff_date.isoformat()).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to cleanup expired invitations: {str(e)}")
    
    def _invitation_to_dict(self, invitation: BusinessInvitation) -> dict:
        """Convert BusinessInvitation entity to dictionary for Supabase."""
        return {
            "id": str(invitation.id),
            "business_id": str(invitation.business_id),
            "business_name": invitation.business_name,
            "invited_email": invitation.invited_email,
            "invited_phone": invitation.invited_phone,
            "invited_by": invitation.invited_by,
            "invited_by_name": invitation.invited_by_name,
            "role": invitation.role.value,
            "permissions": json.dumps(invitation.permissions),
            "invitation_date": invitation.invitation_date.isoformat(),
            "expiry_date": invitation.expiry_date.isoformat(),
            "status": invitation.status.value,
            "message": invitation.message,
            "accepted_date": invitation.accepted_date.isoformat() if invitation.accepted_date else None,
            "declined_date": invitation.declined_date.isoformat() if invitation.declined_date else None
        }
    
    def _dict_to_invitation(self, data: dict) -> BusinessInvitation:
        """Convert dictionary from Supabase to BusinessInvitation entity."""
        return BusinessInvitation(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            business_name=data["business_name"],
            invited_by=data["invited_by"],
            invited_by_name=data["invited_by_name"],
            role=BusinessRole(data["role"]),
            permissions=json.loads(data["permissions"]),
            invitation_date=datetime.fromisoformat(data["invitation_date"]),
            expiry_date=datetime.fromisoformat(data["expiry_date"]),
            status=InvitationStatus(data["status"]),
            invited_email=data.get("invited_email"),
            invited_phone=data.get("invited_phone"),
            message=data.get("message"),
            accepted_date=datetime.fromisoformat(data["accepted_date"]) if data.get("accepted_date") else None,
            declined_date=datetime.fromisoformat(data["declined_date"]) if data.get("declined_date") else None
        ) 