"""
Profile Application Service

Service layer for business profile management operations.
"""

import uuid
import logging
from typing import Optional

from ..dto.profile_dto import BusinessProfileDTO, ProfileSummaryDTO
from ...domain.repositories.business_repository import BusinessRepository
from ..exceptions.application_exceptions import (
    ApplicationError, ValidationError, EntityNotFoundError
)

logger = logging.getLogger(__name__)


class ProfileService:
    """
    Application service for profile management.
    
    Encapsulates business logic for profile operations and coordinates
    between the domain and infrastructure layers.
    """
    
    def __init__(self, business_repository: BusinessRepository):
        self.business_repository = business_repository
        logger.info("ProfileService initialized")
    
    async def get_business_profile(self, business_id: str) -> BusinessProfileDTO:
        """
        Get complete business profile information.
        
        Args:
            business_id: Business identifier
            
        Returns:
            Business profile as DTO
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If business_id is invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Get business from repository
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError("Business", business_id)
            
            # Convert domain entity to DTO
            profile_dto = BusinessProfileDTO(
                id=str(business.id),
                name=business.name,
                industry=business.primary_trade_slug,
                description=business.description,
                phone_number=business.phone_number,
                business_email=business.business_email,
                business_address=business.address,  # Use address field instead of business_address
                city=business.city,
                state=business.state,
                postal_code=business.postal_code,
                website=business.website,
                # Business entity no longer stores service areas directly; leave empty for now
                service_areas=[],
                # Use primary trade slug as a single trade indicator; activities live elsewhere
                trades=[business.primary_trade_slug] if business.primary_trade_slug else [],
                business_license=business.business_license,
                years_in_business=business.years_in_business,  # This field exists now
                is_active=business.is_active,
                is_verified=False  # Field doesn't exist on Business entity yet
            )
            
            logger.info(f"Retrieved profile for business {business_id}")
            return profile_dto
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error retrieving profile for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve profile: {str(e)}")
    
    async def get_profile_summary(self, business_id: str) -> ProfileSummaryDTO:
        """
        Get business profile summary information.
        
        Args:
            business_id: Business identifier
            
        Returns:
            Profile summary as DTO
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If business_id is invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Get business from repository
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError("Business", business_id)
            
            # Convert to summary DTO
            summary_dto = ProfileSummaryDTO(
                business_id=str(business.id),
                business_name=business.name,
                primary_trade=business.get_primary_trade(),
                service_area_count=len(business.service_areas or []),
                is_emergency_available=True  # TODO: Add emergency service field to business entity
            )
            
            logger.info(f"Retrieved profile summary for business {business_id}")
            return summary_dto
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error retrieving profile summary for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve profile summary: {str(e)}")
