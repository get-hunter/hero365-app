"""
Get Business Detail Use Case

Retrieves detailed business information including team members, departments, and statistics.
"""

import uuid
from typing import Optional

from ...dto.business_dto import BusinessDetailResponseDTO, BusinessMembershipResponseDTO
from ...exceptions.application_exceptions import ValidationError, BusinessLogicError
from app.domain.repositories.business_repository import BusinessRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.repositories.business_invitation_repository import BusinessInvitationRepository


class GetBusinessDetailUseCase:
    """
    Use case for retrieving detailed business information.
    
    Includes business profile, team members, departments, and relevant statistics.
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
    
    async def execute(self, business_id: uuid.UUID, requesting_user_id: str) -> BusinessDetailResponseDTO:
        """
        Get detailed business information.
        
        Args:
            business_id: ID of the business to retrieve
            requesting_user_id: ID of the user making the request
            
        Returns:
            BusinessDetailResponseDTO with complete business information
            
        Raises:
            ValidationError: If business_id is invalid
            BusinessLogicError: If user doesn't have access to business
        """
        if not business_id:
            raise ValidationError("Business ID is required")
        
        if not requesting_user_id:
            raise ValidationError("User ID is required")
        
        # Get business
        business = await self.business_repository.get_by_id(business_id)
        if not business:
            raise BusinessLogicError("Business not found")
        
        # Check if user has access to this business
        user_membership = await self.membership_repository.get_by_business_and_user(
            business_id, requesting_user_id
        )
        if not user_membership or not user_membership.is_active:
            raise BusinessLogicError("Access denied: User is not a member of this business")
        
        # Get all team members
        team_members = await self.membership_repository.get_by_business_id(
            business_id, skip=0, limit=1000  # Get all members
        )
        
        # Get pending invitations
        pending_invitations = await self.invitation_repository.get_by_business_id(
            business_id, skip=0, limit=100
        )
        pending_invitations_list = [inv for inv in pending_invitations if inv.status.name == 'pending']
        
        # Convert business to DTO
        business_dto = business.to_dto()
        
        # Convert team members to DTOs
        team_member_dtos = [member.to_dto() for member in team_members if member.is_active]
        
        # Find owner membership
        owner_membership = next((member for member in team_members if member.role.name == 'owner'), user_membership)
        
        # Create detailed business DTO
        detail_dto = BusinessDetailResponseDTO(
            business=business_dto,
            user_membership=user_membership.to_dto(),
            team_members=team_member_dtos,
            pending_invitations=[inv.to_dto() for inv in pending_invitations_list],
            total_members=len(team_member_dtos),
            owner_membership=owner_membership.to_dto()
        )
        
        return detail_dto 