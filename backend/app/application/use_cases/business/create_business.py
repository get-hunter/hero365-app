"""
Create Business Use Case

Handles the business logic for creating a new business with automatic owner membership.
"""

import uuid
from datetime import datetime
from typing import Optional

from ...dto.business_dto import BusinessCreateDTO, BusinessResponseDTO
from ....domain.repositories.business_repository import BusinessRepository
from ....domain.repositories.business_membership_repository import BusinessMembershipRepository
from ....domain.entities.business import Business, CompanySize, ReferralSource
from ....domain.entities.business_membership import BusinessMembership, BusinessRole, DEFAULT_ROLE_PERMISSIONS
from ....domain.exceptions.domain_exceptions import DomainValidationError, DuplicateEntityError
from ...exceptions.application_exceptions import (
    ApplicationError, ValidationError, BusinessLogicError
)


class CreateBusinessUseCase:
    """
    Use case for creating a new business.
    
    This use case handles the complete business creation process including:
    - Business validation and creation
    - Automatic owner membership creation
    - Transaction-like behavior for consistency
    """
    
    def __init__(
        self,
        business_repository: BusinessRepository,
        membership_repository: BusinessMembershipRepository
    ):
        self.business_repository = business_repository
        self.membership_repository = membership_repository
    
    async def execute(self, dto: BusinessCreateDTO) -> BusinessResponseDTO:
        """
        Execute the create business use case.
        
        Args:
            dto: Business creation data
            
        Returns:
            BusinessResponseDTO: Created business information
            
        Raises:
            ValidationError: If input data is invalid
            BusinessLogicError: If business logic is violated
            ApplicationError: If creation fails
        """
        try:
            # Validate input data
            self._validate_input(dto)
            
            # Check if business name is unique for the owner
            await self._validate_business_name_uniqueness(dto.name, dto.owner_id)
            
            # Create business entity
            business = self._create_business_entity(dto)
            
            # Save business to repository
            created_business = await self.business_repository.create(business)
            
            # Create owner membership
            await self._create_owner_membership(created_business, dto.owner_id)
            
            # Convert to response DTO
            return self._to_response_dto(created_business)
            
        except DomainValidationError as e:
            raise ValidationError(f"Business validation failed: {str(e)}")
        except DuplicateEntityError as e:
            raise BusinessLogicError(f"Business already exists: {str(e)}")
        except Exception as e:
            raise ApplicationError(f"Failed to create business: {str(e)}")
    
    def _validate_input(self, dto: BusinessCreateDTO) -> None:
        """Validate input data."""
        if not dto.name or len(dto.name.strip()) == 0:
            raise ValidationError("Business name is required")
        
        if not dto.industry or len(dto.industry.strip()) == 0:
            raise ValidationError("Industry is required")
        
        if not dto.owner_id:
            raise ValidationError("Owner ID is required")
        
        if dto.industry.lower() == "custom" and not dto.custom_industry:
            raise ValidationError("Custom industry must be specified when industry is 'custom'")
        
        if dto.website and not dto.website.startswith(('http://', 'https://')):
            raise ValidationError("Website must be a valid URL")
        
        if dto.business_email and '@' not in dto.business_email:
            raise ValidationError("Business email must be a valid email address")
    
    async def _validate_business_name_uniqueness(self, name: str, owner_id: str) -> None:
        """Validate that business name is unique for the owner."""
        is_unique = await self.business_repository.is_name_unique_for_owner(name, owner_id)
        if not is_unique:
            raise BusinessLogicError(f"Business with name '{name}' already exists for this owner")
    
    def _create_business_entity(self, dto: BusinessCreateDTO) -> Business:
        """Create business entity from DTO."""
        now = datetime.utcnow()
        
        return Business(
            id=uuid.uuid4(),
            name=dto.name.strip(),
            industry=dto.industry.strip(),
            company_size=dto.company_size,
            owner_id=dto.owner_id,
            custom_industry=dto.custom_industry.strip() if dto.custom_industry else None,
            description=dto.description.strip() if dto.description else None,
            phone_number=dto.phone_number.strip() if dto.phone_number else None,
            business_address=dto.business_address.strip() if dto.business_address else None,
            website=dto.website.strip() if dto.website else None,
            business_email=dto.business_email.strip() if dto.business_email else None,
            selected_features=dto.selected_features.copy(),
            primary_goals=dto.primary_goals.copy(),
            referral_source=dto.referral_source,
            timezone=dto.timezone,
            created_date=now,
            last_modified=now
        )
    
    async def _create_owner_membership(self, business: Business, owner_id: str) -> None:
        """Create owner membership for the business."""
        try:
            membership = BusinessMembership(
                id=uuid.uuid4(),
                business_id=business.id,
                user_id=owner_id,
                role=BusinessRole.OWNER,
                permissions=DEFAULT_ROLE_PERMISSIONS[BusinessRole.OWNER].copy(),
                joined_date=datetime.utcnow()
            )
            
            await self.membership_repository.create(membership)
            
        except Exception as e:
            # In a real implementation, we would want to rollback the business creation
            # For now, we'll let this propagate as an application error
            raise ApplicationError(f"Failed to create owner membership: {str(e)}")
    
    def _to_response_dto(self, business: Business) -> BusinessResponseDTO:
        """Convert business entity to response DTO."""
        return BusinessResponseDTO(
            id=business.id,
            name=business.name,
            industry=business.industry,
            company_size=business.company_size,
            owner_id=business.owner_id,
            custom_industry=business.custom_industry,
            description=business.description,
            phone_number=business.phone_number,
            business_address=business.business_address,
            website=business.website,
            logo_url=business.logo_url,
            business_email=business.business_email,
            business_registration_number=business.business_registration_number,
            tax_id=business.tax_id,
            business_license=business.business_license,
            insurance_number=business.insurance_number,
            selected_features=business.selected_features,
            primary_goals=business.primary_goals,
            referral_source=business.referral_source,
            onboarding_completed=business.onboarding_completed,
            onboarding_completed_date=business.onboarding_completed_date,
            timezone=business.timezone,
            currency=business.currency,
            business_hours=business.business_hours,
            is_active=business.is_active,
            max_team_members=business.max_team_members,
            subscription_tier=business.subscription_tier,
            enabled_features=business.enabled_features,
            created_date=business.created_date,
            last_modified=business.last_modified
        ) 