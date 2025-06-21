"""
Get User Businesses Use Case

Handles the business logic for retrieving all businesses a user is associated with.
"""

from typing import List

from ...dto.business_dto import UserBusinessSummaryDTO, BusinessSummaryDTO, BusinessMembershipResponseDTO
from ....domain.repositories.business_repository import BusinessRepository
from ....domain.repositories.business_membership_repository import BusinessMembershipRepository
from ....domain.repositories.business_invitation_repository import BusinessInvitationRepository
from ....domain.entities.business import Business
from ....domain.entities.business_membership import BusinessMembership, BusinessRole
from ...exceptions.application_exceptions import ApplicationError, ValidationError


class GetUserBusinessesUseCase:
    """
    Use case for retrieving all businesses a user is associated with.
    
    This use case handles:
    - Retrieving businesses where user is a member
    - Combining business and membership information
    - Providing summary information for UI display
    - Including pending invitation counts for owners
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
    
    async def execute(self, user_id: str, skip: int = 0, limit: int = 100) -> List[UserBusinessSummaryDTO]:
        """
        Execute the get user businesses use case.
        
        Args:
            user_id: User ID to get businesses for
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List[UserBusinessSummaryDTO]: List of businesses with user's membership info
            
        Raises:
            ValidationError: If input data is invalid
            ApplicationError: If retrieval fails
        """
        try:
            # Validate input data
            self._validate_input(user_id, skip, limit)
            
            # Get user's business memberships with business information
            user_businesses = await self.business_repository.get_user_businesses(user_id, skip, limit)
            
            # Convert to response DTOs
            result = []
            for business, membership in user_businesses:
                # Get additional information for the business
                team_member_count = await self._get_team_member_count(business.id)
                pending_invitations_count = await self._get_pending_invitations_count(business.id, membership)
                
                # Create business summary
                business_summary = self._create_business_summary(business, team_member_count)
                
                # Create membership response
                membership_response = self._create_membership_response(membership)
                
                # Create user business summary
                user_business_summary = UserBusinessSummaryDTO(
                    business=business_summary,
                    membership=membership_response,
                    is_owner=membership.role == BusinessRole.OWNER,
                    pending_invitations_count=pending_invitations_count
                )
                
                result.append(user_business_summary)
            
            return result
            
        except Exception as e:
            raise ApplicationError(f"Failed to get user businesses: {str(e)}")
    
    def _validate_input(self, user_id: str, skip: int, limit: int) -> None:
        """Validate input data."""
        if not user_id:
            raise ValidationError("User ID is required")
        
        if skip < 0:
            raise ValidationError("Skip must be non-negative")
        
        if limit < 1 or limit > 100:
            raise ValidationError("Limit must be between 1 and 100")
    
    async def _get_team_member_count(self, business_id) -> int:
        """Get team member count for a business."""
        try:
            return await self.membership_repository.count_active_business_members(business_id)
        except Exception:
            # If we can't get the count, return 0 rather than failing the whole operation
            return 0
    
    async def _get_pending_invitations_count(self, business_id, membership: BusinessMembership) -> int:
        """Get pending invitations count for owners/admins."""
        try:
            # Only show pending invitations count to owners and admins
            if membership.role in [BusinessRole.OWNER, BusinessRole.ADMIN]:
                return await self.invitation_repository.count_pending_business_invitations(business_id)
            return 0
        except Exception:
            # If we can't get the count, return 0 rather than failing the whole operation
            return 0
    
    def _create_business_summary(self, business: Business, team_member_count: int) -> BusinessSummaryDTO:
        """Create business summary DTO."""
        return BusinessSummaryDTO(
            id=business.id,
            name=business.name,
            industry=business.industry,
            company_size=business.company_size,
            is_active=business.is_active,
            created_date=business.created_date,
            team_member_count=team_member_count,
            onboarding_completed=business.onboarding_completed
        )
    
    def _create_membership_response(self, membership: BusinessMembership) -> BusinessMembershipResponseDTO:
        """Create membership response DTO."""
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