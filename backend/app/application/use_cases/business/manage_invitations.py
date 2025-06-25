"""
Manage Invitations Use Case

Handles invitation management including listing, canceling, and declining invitations.
"""

import uuid
from typing import List, Optional
from datetime import datetime

from ...dto.business_dto import BusinessInvitationResponseDTO
from ...exceptions.application_exceptions import ValidationError, BusinessLogicError
from app.domain.repositories.business_repository import BusinessRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.repositories.business_invitation_repository import BusinessInvitationRepository
from app.domain.entities.business_invitation import InvitationStatus
from app.domain.entities.business_membership import BusinessRole


class ManageInvitationsUseCase:
    """
    Use case for managing business invitations.
    
    Handles invitation listing, cancellation, and decline operations.
    """
    
    def __init__(
        self,
        business_repository: BusinessRepository,
        membership_repository: BusinessMembershipRepository,
        invitation_repository: BusinessInvitationRepository
    ):
        self.business_repository = business_repository
        self.membership_repository = membership_repository
        self.invitation_repository = invitation_repository
    
    async def get_business_invitations(
        self,
        business_id: uuid.UUID,
        requesting_user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[BusinessInvitationResponseDTO]:
        """
        Get business invitations.
        
        Args:
            business_id: ID of the business
            requesting_user_id: ID of the user making the request
            skip: Number of invitations to skip
            limit: Maximum number of invitations to return
            
        Returns:
            List[BusinessInvitationResponseDTO] with invitation details
            
        Raises:
            ValidationError: If input data is invalid
            BusinessLogicError: If user doesn't have permission
        """
        if not business_id:
            raise ValidationError("Business ID is required")
        
        if not requesting_user_id:
            raise ValidationError("User ID is required")
        
        # Get business
        business = await self.business_repository.get_by_id(business_id)
        if not business:
            raise BusinessLogicError("Business not found")
        
        # Check user permissions
        requesting_membership = await self.membership_repository.get_by_business_and_user(
            business_id, requesting_user_id
        )
        if not requesting_membership or not requesting_membership.is_active:
            raise BusinessLogicError("Access denied: User is not a member of this business")
        
        # Check if user can view invitations
        if not self._can_view_invitations(requesting_membership):
            raise BusinessLogicError("Insufficient permissions to view invitations")
        
        # Get invitations
        invitations = await self.invitation_repository.get_by_business_id(
            business_id, skip=skip, limit=limit
        )
        
        return [invitation.to_dto() for invitation in invitations]
    
    async def cancel_invitation(
        self,
        invitation_id: uuid.UUID,
        requesting_user_id: str
    ) -> bool:
        """
        Cancel a pending invitation.
        
        Args:
            invitation_id: ID of the invitation to cancel
            requesting_user_id: ID of the user making the request
            
        Returns:
            bool: True if successfully cancelled
            
        Raises:
            ValidationError: If input data is invalid
            BusinessLogicError: If user doesn't have permission or invitation not found
        """
        if not invitation_id:
            raise ValidationError("Invitation ID is required")
        
        if not requesting_user_id:
            raise ValidationError("User ID is required")
        
        # Get invitation
        invitation = await self.invitation_repository.get_by_id(invitation_id)
        if not invitation:
            raise BusinessLogicError("Invitation not found")
        
        # Check if invitation can be cancelled
        if invitation.status != InvitationStatus.PENDING:
            raise BusinessLogicError("Only pending invitations can be cancelled")
        
        # Check user permissions
        requesting_membership = await self.membership_repository.get_by_business_and_user(
            invitation.business_id, requesting_user_id
        )
        if not requesting_membership or not requesting_membership.is_active:
            raise BusinessLogicError("Access denied: User is not a member of this business")
        
        # Check if user can cancel invitations
        if not self._can_cancel_invitation(requesting_membership, invitation):
            raise BusinessLogicError("Insufficient permissions to cancel this invitation")
        
        # Cancel invitation
        invitation.cancel()
        await self.invitation_repository.update(invitation)
        
        return True
    
    async def decline_invitation(
        self,
        invitation_id: uuid.UUID,
        declining_user_id: str
    ) -> bool:
        """
        Decline a business invitation.
        
        Args:
            invitation_id: ID of the invitation to decline
            declining_user_id: ID of the user declining the invitation
            
        Returns:
            bool: True if successfully declined
            
        Raises:
            ValidationError: If input data is invalid
            BusinessLogicError: If invitation not found or cannot be declined
        """
        if not invitation_id:
            raise ValidationError("Invitation ID is required")
        
        if not declining_user_id:
            raise ValidationError("User ID is required")
        
        # Get invitation
        invitation = await self.invitation_repository.get_by_id(invitation_id)
        if not invitation:
            raise BusinessLogicError("Invitation not found")
        
        # Check if invitation can be declined
        if invitation.status != InvitationStatus.PENDING:
            raise BusinessLogicError("Only pending invitations can be declined")
        
        # Check if invitation has expired
        if invitation.is_expired():
            raise BusinessLogicError("Invitation has expired")
        
        # Verify this is the intended recipient
        # This could be enhanced to verify email/phone match
        # For now, we'll allow any authenticated user to decline
        
        # Decline invitation
        invitation.decline()
        await self.invitation_repository.update(invitation)
        
        return True
    
    async def get_user_invitations(
        self,
        user_email: Optional[str] = None,
        user_phone: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[BusinessInvitationResponseDTO]:
        """
        Get invitations for a specific user by email or phone.
        
        Args:
            user_email: Email address of the user
            user_phone: Phone number of the user
            skip: Number of invitations to skip
            limit: Maximum number of invitations to return
            
        Returns:
            List[BusinessInvitationResponseDTO] with invitation details
            
        Raises:
            ValidationError: If no contact method provided
        """
        if not user_email and not user_phone:
            raise ValidationError("Either email or phone number is required")
        
        # Get invitations by email or phone
        invitations = []
        
        if user_email:
            email_invitations = await self.invitation_repository.get_by_email(
                user_email, skip=skip, limit=limit
            )
            invitations.extend(email_invitations)
        
        if user_phone:
            phone_invitations = await self.invitation_repository.get_by_phone(
                user_phone, skip=skip, limit=limit
            )
            invitations.extend(phone_invitations)
        
        # Remove duplicates and sort by invitation date
        unique_invitations = {inv.id: inv for inv in invitations}
        sorted_invitations = sorted(
            unique_invitations.values(),
            key=lambda x: x.invitation_date,
            reverse=True
        )
        
        return [invitation.to_dto() for invitation in sorted_invitations[:limit]]
    
    def _can_view_invitations(self, membership) -> bool:
        """Check if user can view business invitations."""
        # Owners and admins can view invitations
        if membership.role in [BusinessRole.OWNER, BusinessRole.ADMIN]:
            return True
        
        # Members with team:invite permission can view invitations
        if membership.has_permission('team:invite'):
            return True
        
        return False
    
    def _can_cancel_invitation(self, membership, invitation) -> bool:
        """Check if user can cancel an invitation."""
        # Owners can cancel any invitation
        if membership.role == BusinessRole.OWNER:
            return True
        
        # Admins with team:invite permission can cancel invitations
        if (membership.role == BusinessRole.ADMIN and 
            membership.has_permission('team:invite')):
            return True
        
        # Users can cancel invitations they sent
        if invitation.invited_by == membership.user_id:
            return True
        
        return False 