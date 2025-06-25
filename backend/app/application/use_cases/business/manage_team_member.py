"""
Manage Team Member Use Case

Handles team member management including role updates and member removal.
"""

import uuid
from typing import Optional

from ...dto.business_dto import BusinessMembershipUpdateDTO, BusinessMembershipResponseDTO
from ...exceptions.application_exceptions import ValidationError, BusinessLogicError
from app.domain.repositories.business_repository import BusinessRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.business_membership import BusinessRole


class ManageTeamMemberUseCase:
    """
    Use case for managing team members.
    
    Handles role updates, permission changes, and member removal with proper validation.
    """
    
    def __init__(
        self,
        business_repository: BusinessRepository,
        membership_repository: BusinessMembershipRepository
    ):
        self.business_repository = business_repository
        self.membership_repository = membership_repository
    
    async def update_member_role(
        self,
        business_id: uuid.UUID,
        membership_id: uuid.UUID,
        update_dto: BusinessMembershipUpdateDTO,
        requesting_user_id: str
    ) -> BusinessMembershipResponseDTO:
        """
        Update a team member's role and permissions.
        
        Args:
            business_id: ID of the business
            membership_id: ID of the membership to update
            update_dto: Membership update data
            requesting_user_id: ID of the user making the request
            
        Returns:
            BusinessMembershipResponseDTO with updated membership
            
        Raises:
            ValidationError: If input data is invalid
            BusinessLogicError: If user doesn't have permission or member not found
        """
        if not business_id:
            raise ValidationError("Business ID is required")
        
        if not membership_id:
            raise ValidationError("Membership ID is required")
        
        if not requesting_user_id:
            raise ValidationError("User ID is required")
        
        # Get business
        business = await self.business_repository.get_by_id(business_id)
        if not business:
            raise BusinessLogicError("Business not found")
        
        # Get requesting user's membership
        requesting_membership = await self.membership_repository.get_by_business_and_user(
            business_id, requesting_user_id
        )
        if not requesting_membership or not requesting_membership.is_active:
            raise BusinessLogicError("Access denied: User is not a member of this business")
        
        # Get target membership
        target_membership = await self.membership_repository.get_by_id(membership_id)
        if not target_membership or target_membership.business_id != business_id:
            raise BusinessLogicError("Team member not found")
        
        # Validate permission to update this member
        if not self._can_update_member_role(requesting_membership, target_membership, update_dto.role):
            raise BusinessLogicError("Insufficient permissions to update this team member")
        
        # Prevent owner from changing their own role
        if (target_membership.user_id == requesting_user_id and 
            target_membership.role == BusinessRole.OWNER):
            raise BusinessLogicError("Business owner cannot change their own role")
        
        # Update membership
        if update_dto.role is not None:
            target_membership.update_role(update_dto.role)
        
        if update_dto.permissions is not None:
            target_membership.update_permissions(update_dto.permissions)
        
        if update_dto.department_id is not None:
            target_membership.update_department(update_dto.department_id)
        
        if update_dto.job_title is not None:
            target_membership.update_job_title(update_dto.job_title)
        
        # Save updated membership
        updated_membership = await self.membership_repository.update(target_membership)
        
        return updated_membership.to_dto()
    
    async def remove_team_member(
        self,
        business_id: uuid.UUID,
        membership_id: uuid.UUID,
        requesting_user_id: str
    ) -> bool:
        """
        Remove a team member from the business.
        
        Args:
            business_id: ID of the business
            membership_id: ID of the membership to remove
            requesting_user_id: ID of the user making the request
            
        Returns:
            bool: True if successfully removed
            
        Raises:
            ValidationError: If input data is invalid
            BusinessLogicError: If user doesn't have permission or member not found
        """
        if not business_id:
            raise ValidationError("Business ID is required")
        
        if not membership_id:
            raise ValidationError("Membership ID is required")
        
        if not requesting_user_id:
            raise ValidationError("User ID is required")
        
        # Get business
        business = await self.business_repository.get_by_id(business_id)
        if not business:
            raise BusinessLogicError("Business not found")
        
        # Get requesting user's membership
        requesting_membership = await self.membership_repository.get_by_business_and_user(
            business_id, requesting_user_id
        )
        if not requesting_membership or not requesting_membership.is_active:
            raise BusinessLogicError("Access denied: User is not a member of this business")
        
        # Get target membership
        target_membership = await self.membership_repository.get_by_id(membership_id)
        if not target_membership or target_membership.business_id != business_id:
            raise BusinessLogicError("Team member not found")
        
        # Validate permission to remove this member
        if not self._can_remove_member(requesting_membership, target_membership):
            raise BusinessLogicError("Insufficient permissions to remove this team member")
        
        # Prevent owner from removing themselves
        if (target_membership.user_id == requesting_user_id and 
            target_membership.role == BusinessRole.OWNER):
            raise BusinessLogicError("Business owner cannot remove themselves")
        
        # Prevent removing the only owner
        if target_membership.role == BusinessRole.OWNER:
            owner_count = await self.membership_repository.count_by_business_and_role(
                business_id, BusinessRole.OWNER
            )
            if owner_count <= 1:
                raise BusinessLogicError("Cannot remove the only business owner")
        
        # Deactivate membership instead of deleting for audit trail
        target_membership.deactivate()
        await self.membership_repository.update(target_membership)
        
        return True
    
    def _can_update_member_role(self, requesting_membership, target_membership, new_role: Optional[BusinessRole]) -> bool:
        """Check if requesting user can update the target member's role."""
        # Owners can update anyone except other owners (unless demoting)
        if requesting_membership.role == BusinessRole.OWNER:
            # Cannot promote someone to owner
            if new_role == BusinessRole.OWNER:
                return False
            return True
        
        # Admins with team:manage permission can update lower-level roles
        if (requesting_membership.role == BusinessRole.ADMIN and 
            requesting_membership.has_permission('team:manage')):
            # Cannot update owners or other admins
            if target_membership.role in [BusinessRole.OWNER, BusinessRole.ADMIN]:
                return False
            # Cannot promote to admin or owner
            if new_role in [BusinessRole.OWNER, BusinessRole.ADMIN]:
                return False
            return True
        
        return False
    
    def _can_remove_member(self, requesting_membership, target_membership) -> bool:
        """Check if requesting user can remove the target member."""
        # Owners can remove anyone except other owners
        if requesting_membership.role == BusinessRole.OWNER:
            return target_membership.role != BusinessRole.OWNER
        
        # Admins with team:manage permission can remove lower-level roles
        if (requesting_membership.role == BusinessRole.ADMIN and 
            requesting_membership.has_permission('team:manage')):
            return target_membership.role not in [BusinessRole.OWNER, BusinessRole.ADMIN]
        
        return False 