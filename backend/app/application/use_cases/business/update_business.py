"""
Update Business Use Case

Updates business information with proper validation and permission checks.
"""

import uuid
from typing import Optional

from ...dto.business_dto import BusinessUpdateDTO, BusinessResponseDTO
from ...exceptions.application_exceptions import ValidationError, BusinessLogicError
from app.domain.repositories.business_repository import BusinessRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.business import Business
from app.domain.entities.business_membership import BusinessRole


class UpdateBusinessUseCase:
    """
    Use case for updating business information.
    
    Only owners and admins with proper permissions can update business details.
    """
    
    def __init__(
        self,
        business_repository: BusinessRepository,
        membership_repository: BusinessMembershipRepository
    ):
        self.business_repository = business_repository
        self.membership_repository = membership_repository
    
    async def execute(
        self, 
        business_id: uuid.UUID, 
        update_dto: BusinessUpdateDTO, 
        requesting_user_id: str
    ) -> BusinessResponseDTO:
        """
        Update business information.
        
        Args:
            business_id: ID of the business to update
            update_dto: Business update data
            requesting_user_id: ID of the user making the request
            
        Returns:
            BusinessResponseDTO with updated business information
            
        Raises:
            ValidationError: If input data is invalid
            BusinessLogicError: If user doesn't have permission or business not found
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
        user_membership = await self.membership_repository.get_by_business_and_user(
            business_id, requesting_user_id
        )
        if not user_membership or not user_membership.is_active:
            raise BusinessLogicError("Access denied: User is not a member of this business")
        
        # Check if user has permission to update business
        if not self._can_update_business(user_membership):
            raise BusinessLogicError("Insufficient permissions to update business")
        
        # Update business fields
        if update_dto.name is not None:
            business.update_name(update_dto.name)
        
        if update_dto.description is not None:
            business.update_description(update_dto.description)
        
        if update_dto.industry is not None:
            business.update_industry(update_dto.industry, update_dto.custom_industry)
        
        if update_dto.phone_number is not None:
            business.update_phone_number(update_dto.phone_number)
        
        if update_dto.business_address is not None:
            business.update_address(update_dto.business_address)
        
        if update_dto.website is not None:
            business.update_website(update_dto.website)
        
        if update_dto.business_email is not None:
            business.update_business_email(update_dto.business_email)
        
        if update_dto.logo_url is not None:
            business.update_logo_url(update_dto.logo_url)
        
        if update_dto.business_registration_number is not None:
            business.update_registration_number(update_dto.business_registration_number)
        
        if update_dto.tax_id is not None:
            business.update_tax_id(update_dto.tax_id)
        
        if update_dto.business_license is not None:
            business.update_business_license(update_dto.business_license)
        
        if update_dto.insurance_number is not None:
            business.update_insurance_number(update_dto.insurance_number)
        
        if update_dto.timezone is not None:
            business.update_timezone(update_dto.timezone)
        
        if update_dto.currency is not None:
            business.update_currency(update_dto.currency)
        
        if update_dto.business_hours is not None:
            business.update_business_hours(update_dto.business_hours)
        
        if update_dto.max_team_members is not None:
            business.update_max_team_members(update_dto.max_team_members)
        
        if update_dto.subscription_tier is not None:
            business.update_subscription_tier(update_dto.subscription_tier)
        
        if update_dto.enabled_features is not None:
            business.update_enabled_features(update_dto.enabled_features)
        
        # Save updated business
        updated_business = await self.business_repository.update(business)
        
        return updated_business.to_dto()
    
    def _can_update_business(self, membership) -> bool:
        """Check if user can update business information."""
        # Owners can always update
        if membership.role == BusinessRole.OWNER:
            return True
        
        # Admins with business:edit permission can update
        if membership.role == BusinessRole.ADMIN and membership.has_permission('business:edit'):
            return True
        
        return False 