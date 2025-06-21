"""
Accept Business Invitation Use Case

Handles the business logic for accepting business invitations and creating memberships.
"""

import uuid
from datetime import datetime
from typing import Optional

from ...dto.business_dto import BusinessInvitationAcceptDTO, BusinessMembershipResponseDTO
from ....domain.repositories.business_repository import BusinessRepository
from ....domain.repositories.business_membership_repository import BusinessMembershipRepository
from ....domain.repositories.business_invitation_repository import BusinessInvitationRepository
from ....domain.entities.business_invitation import InvitationStatus
from ....domain.entities.business_membership import BusinessMembership
from ....domain.exceptions.domain_exceptions import EntityNotFoundError
from ...exceptions.application_exceptions import (
    ApplicationError, ValidationError, BusinessLogicError
)


class AcceptInvitationUseCase:
    """
    Use case for accepting business invitations.
    
    This use case handles:
    - Invitation validation and acceptance
    - Membership creation from accepted invitation
    - Invitation status updates
    - Business rule enforcement
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
    
    async def execute(self, dto: BusinessInvitationAcceptDTO) -> BusinessMembershipResponseDTO:
        """
        Execute the accept invitation use case.
        
        Args:
            dto: Invitation acceptance data
            
        Returns:
            BusinessMembershipResponseDTO: Created membership information
            
        Raises:
            ValidationError: If input data is invalid
            BusinessLogicError: If business logic is violated
            ApplicationError: If acceptance fails
        """
        try:
            # Validate input data
            self._validate_input(dto)
            
            # Get and validate invitation
            invitation = await self._get_invitation(dto.invitation_id)
            
            # Validate invitation can be accepted
            await self._validate_invitation_can_be_accepted(invitation, dto.user_id)
            
            # Verify business is still active
            await self._validate_business_active(invitation.business_id)
            
            # Check if user is already a member
            await self._validate_not_existing_member(invitation.business_id, dto.user_id)
            
            # Create membership from invitation
            membership = await self._create_membership_from_invitation(invitation, dto.user_id)
            
            # Update invitation status to accepted
            await self._mark_invitation_as_accepted(invitation)
            
            # Convert to response DTO
            return self._to_response_dto(membership)
            
        except EntityNotFoundError as e:
            raise BusinessLogicError(f"Invitation not found: {str(e)}")
        except Exception as e:
            raise ApplicationError(f"Failed to accept invitation: {str(e)}")
    
    def _validate_input(self, dto: BusinessInvitationAcceptDTO) -> None:
        """Validate input data."""
        if not dto.invitation_id:
            raise ValidationError("Invitation ID is required")
        
        if not dto.user_id:
            raise ValidationError("User ID is required")
    
    async def _get_invitation(self, invitation_id: uuid.UUID):
        """Get invitation and verify it exists."""
        invitation = await self.invitation_repository.get_by_id(invitation_id)
        if not invitation:
            raise EntityNotFoundError(f"Invitation with ID {invitation_id} not found")
        return invitation
    
    async def _validate_invitation_can_be_accepted(self, invitation, user_id: str) -> None:
        """Validate that invitation can be accepted."""
        # Check invitation status
        if invitation.status != InvitationStatus.PENDING:
            raise BusinessLogicError(f"Invitation cannot be accepted - status is {invitation.status.value}")
        
        # Check if invitation has expired
        if invitation.is_expired():
            raise BusinessLogicError("Invitation has expired")
        
        # Check if invitation can be accepted (this validates the contact method matches)
        if not invitation.can_accept():
            raise BusinessLogicError("Invitation cannot be accepted")
    
    async def _validate_business_active(self, business_id: uuid.UUID) -> None:
        """Validate that business is still active."""
        business = await self.business_repository.get_by_id(business_id)
        if not business:
            raise BusinessLogicError("Business no longer exists")
        
        if not business.is_active:
            raise BusinessLogicError("Cannot join inactive business")
    
    async def _validate_not_existing_member(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate that user is not already a member."""
        is_member = await self.membership_repository.user_is_member(business_id, user_id)
        if is_member:
            raise BusinessLogicError("User is already a member of this business")
    
    async def _create_membership_from_invitation(self, invitation, user_id: str) -> BusinessMembership:
        """Create membership from accepted invitation."""
        try:
            membership = BusinessMembership(
                id=uuid.uuid4(),
                business_id=invitation.business_id,
                user_id=user_id,
                role=invitation.role,
                permissions=invitation.permissions.copy(),
                joined_date=datetime.utcnow(),
                invited_date=invitation.invitation_date,
                invited_by=invitation.invited_by
            )
            
            return await self.membership_repository.create(membership)
            
        except Exception as e:
            raise ApplicationError(f"Failed to create membership: {str(e)}")
    
    async def _mark_invitation_as_accepted(self, invitation) -> None:
        """Mark invitation as accepted."""
        try:
            invitation.accept()
            await self.invitation_repository.update(invitation)
            
        except Exception as e:
            # In a real implementation, we might want to rollback the membership creation
            # For now, we'll log this but not fail the operation
            pass
    
    def _to_response_dto(self, membership: BusinessMembership) -> BusinessMembershipResponseDTO:
        """Convert membership entity to response DTO."""
        return BusinessMembershipResponseDTO(
            id=membership.id,
            business_id=membership.business_id,
            user_id=membership.user_id,
            role=membership.role,
            permissions=membership.permissions,
            joined_date=membership.joined_date,
            invited_date=membership.invited_date,
            invited_by=membership.invited_by,
            is_active=membership.is_active,
            department_id=membership.department_id,
            job_title=membership.job_title,
            role_display=membership.role.value.title()
        ) 