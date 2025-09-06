"""
Contractor Profile API Routes

Public endpoints for retrieving contractor profile information.
"""

from fastapi import APIRouter, HTTPException, Path, Depends
from typing import List
import logging

from .schemas import ProfessionalProfile
from app.application.services.profile_service import ProfileService
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError, EntityNotFoundError
)
from app.infrastructure.config.dependency_injection import get_business_repository

logger = logging.getLogger(__name__)

router = APIRouter()


def get_profile_service():
    """Dependency injection for ProfileService."""
    business_repo = get_business_repository()
    return ProfileService(business_repo)


@router.get("/profile/{business_id}", response_model=ProfessionalProfile)
async def get_contractor_profile(
    business_id: str = Path(..., description="Business ID"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """
    Get complete contractor profile information.
    
    Returns business details, contact information, service areas, and credentials.
    
    Args:
        business_id: The unique identifier of the business
        profile_service: Injected profile service
        
    Returns:
        ProfessionalProfile: Complete business profile information
        
    Raises:
        HTTPException: If business not found or retrieval fails
    """
    
    try:
        # Get profile from service layer
        profile_dto = await profile_service.get_business_profile(business_id)
        
        # Determine primary trade cleanly without relying on deprecated fields
        primary_trade = None
        if getattr(profile_dto, 'trades', None) and len(profile_dto.trades) > 0:
            primary_trade = profile_dto.trades[0]
        elif getattr(profile_dto, 'industry', None):
            # Back-compat: ProfileService currently maps industry from primary_trade_slug
            primary_trade = profile_dto.industry

        normalized_trade = (primary_trade or 'general').lower()

        # Convert DTO to API response model (no direct dependency on deprecated business fields)
        profile_data = {
            "business_id": profile_dto.id,
            "business_name": profile_dto.name,
            "trade_type": normalized_trade,
            "description": profile_dto.description or f"Professional {normalized_trade} provider",
            "phone": profile_dto.phone_number or "",
            "email": profile_dto.business_email or "",
            "address": profile_dto.business_address or "",
            "city": profile_dto.city or "",
            "state": profile_dto.state or "",
            "postal_code": profile_dto.postal_code or "",
            "website": profile_dto.website,
            # Business no longer carries service areas directly; empty list until ServiceAreasService integration
            "service_areas": profile_dto.service_areas,
            "emergency_service": True,  # TODO: Add to business entity
            "years_in_business": profile_dto.years_in_business or 10,
            "license_number": profile_dto.business_license,
            "insurance_verified": profile_dto.is_verified,
            "average_rating": 4.8,  # TODO: Calculate from reviews
            "total_reviews": 150,  # TODO: Count from reviews
            "certifications": []  # TODO: Add certifications to business entity
        }
        
        return ProfessionalProfile(**profile_data)
        
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error for business {business_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving profile for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")
    except Exception as e:
        logger.error(f"Unexpected error retrieving profile for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")