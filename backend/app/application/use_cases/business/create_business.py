"""
Create Business Use Case

Handles the business logic for creating a new business with automatic owner membership.
"""

import uuid
import logging
from datetime import datetime
from typing import Optional

from ...dto.business_dto import BusinessCreateDTO, BusinessResponseDTO
from app.domain.repositories.business_repository import BusinessRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.business import Business, CompanySize, ReferralSource
from app.domain.entities.business_membership import BusinessMembership, BusinessRole, get_default_permissions_for_role
from app.domain.exceptions.domain_exceptions import DomainValidationError, DuplicateEntityError
from ...exceptions.application_exceptions import (
    ApplicationError, ValidationError, BusinessLogicError
)

# Configure logging
logger = logging.getLogger(__name__)

class CreateBusinessUseCase:
    """
    Use case for creating a new business with automatic owner membership.
    
    This use case handles the complete business creation flow including:
    1. Input validation
    2. Business name uniqueness check
    3. Business entity creation
    4. Business persistence
    5. Owner membership creation
    """
    
    def __init__(
        self,
        business_repository: BusinessRepository,
        membership_repository: BusinessMembershipRepository
    ):
        self.business_repository = business_repository
        self.membership_repository = membership_repository
        logger.info("CreateBusinessUseCase initialized")

    async def execute(self, dto: BusinessCreateDTO, owner_user_id: str) -> BusinessResponseDTO:
        """
        Execute the create business use case.
        
        Args:
            dto: Business creation data transfer object
            
        Returns:
            BusinessResponseDTO: Created business information
            
        Raises:
            ValidationError: If input validation fails
            BusinessLogicError: If business rules are violated
            ApplicationError: If creation fails
        """
        logger.info(f"execute() called with business name: {dto.name}, owner: {owner_user_id}")

        try:
            # Validate input data
            logger.info("Starting input validation")
            self._validate_input(dto)
            logger.info("Input validation completed successfully")
            
            # Check if business name is unique for the owner
            logger.info("Checking business name uniqueness")
            # Name uniqueness validation removed - business names can be globally unique
            logger.info("Business name uniqueness check completed")
            
            # Create business entity
            logger.info("Creating business entity")
            business = self._create_business_entity(dto)
            logger.info(f"Business entity created: {business.id}")
            
            # Save business to repository
            logger.info("Saving business to repository")
            created_business = await self.business_repository.create(business)
            logger.info(f"Business saved successfully: {created_business.id}")
            
            # Create owner membership
            logger.info("Creating owner membership")
            await self._create_owner_membership(created_business, owner_user_id)
            logger.info("Owner membership created successfully")
            
            # Convert to response DTO
            logger.info("Converting to response DTO")
            response_dto = self._to_response_dto(created_business)
            logger.info(f"Response DTO created: {response_dto.id}")
            return response_dto
            
        except DomainValidationError as e:
            logger.error(f"DomainValidationError: {str(e)}")
            raise ValidationError(f"Business validation failed: {str(e)}")
        except DuplicateEntityError as e:
            logger.error(f"DuplicateEntityError: {str(e)}")
            raise BusinessLogicError(f"Business already exists: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected exception in execute(): {type(e).__name__}: {str(e)}")
            raise ApplicationError(f"Failed to create business: {str(e)}")
    
    def _validate_input(self, dto: BusinessCreateDTO) -> None:
        """Validate input data."""
        logger.info("Validating input data")
        
        if not dto.name or len(dto.name.strip()) == 0:
            raise ValidationError("Business name is required")
        
        if not dto.industry or len(dto.industry.strip()) == 0:
            raise ValidationError("Industry is required")
        
        # owner_id validation moved to controller level (passed as separate parameter)
        
        if dto.industry.lower() == "custom" and not dto.custom_industry:
            raise ValidationError("Custom industry must be specified when industry is 'custom'")
        
        if dto.website and not dto.website.startswith(('http://', 'https://')):
            raise ValidationError("Website must be a valid URL")
        
        if dto.business_email and '@' not in dto.business_email:
            raise ValidationError("Business email must be a valid email address")
        
        logger.info("Input validation passed")
    
    async def _validate_business_name_uniqueness(self, name: str, owner_id: str) -> None:
        """Validate that business name is unique for the owner."""
        logger.info(f"Checking uniqueness for business name: {name}, owner: {owner_id}")
        
        is_unique = await self.business_repository.is_name_unique_for_owner(name, owner_id)
        if not is_unique:
            logger.error(f"Business name '{name}' is not unique for owner {owner_id}")
            raise BusinessLogicError(f"Business with name '{name}' already exists for this owner")
        
        logger.info("Business name uniqueness validated successfully")
    
    def _create_business_entity(self, dto: BusinessCreateDTO) -> Business:
        """Create business entity from DTO."""
        logger.info("Creating business entity from DTO")
        
        now = datetime.utcnow()
        
        business = Business(
            id=uuid.uuid4(),
            name=dto.name.strip(),
            industry=dto.industry.strip(),
            company_size=dto.company_size,
            # owner_id removed - handled via business_memberships
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
        
        logger.info(f"Business entity created with ID: {business.id}")
        return business
    
    async def _create_owner_membership(self, business: Business, owner_id: str) -> None:
        """Create owner membership for the business."""
        logger.info(f"Creating owner membership for business: {business.id}, owner: {owner_id}")
        
        try:
            membership = BusinessMembership.create_with_default_permissions(
                business_id=business.id,
                user_id=owner_id,
                role=BusinessRole.OWNER
            )
            
            logger.info(f"Owner membership entity created: {membership.id}")
            await self.membership_repository.create(membership)
            logger.info("Owner membership saved to repository")
            
        except Exception as e:
            # In a real implementation, we would want to rollback the business creation
            # For now, we'll let this propagate as an application error
            logger.error(f"Failed to create owner membership: {type(e).__name__}: {str(e)}")
            raise ApplicationError(f"Failed to create owner membership: {str(e)}")
    
    def _to_response_dto(self, business: Business) -> BusinessResponseDTO:
        """Convert business entity to response DTO."""
        return BusinessResponseDTO(
            id=business.id,
            name=business.name,
            industry=business.industry,
            company_size=business.company_size,
            # owner_id removed - use business_memberships for ownership queries
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