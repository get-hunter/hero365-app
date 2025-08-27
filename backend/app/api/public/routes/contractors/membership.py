"""
Contractor Membership Plans API Routes

Public endpoints for membership plan information following clean architecture patterns.
"""

from fastapi import APIRouter, HTTPException, Path, Depends
from typing import List
import logging

from .schemas import MembershipPlan
from .....application.services.membership_service import MembershipService
from .....application.exceptions.application_exceptions import (
    ApplicationError, 
    ValidationError, 
    EntityNotFoundError
)
from .....infrastructure.config.dependency_injection import (
    get_business_repository,
    get_customer_membership_repository
)

logger = logging.getLogger(__name__)

router = APIRouter()


def get_membership_service():
    """Get membership service with proper dependency injection."""
    business_repo = get_business_repository()
    membership_repo = get_customer_membership_repository()
    return MembershipService(business_repo, membership_repo)


@router.get("/membership-plans/{business_id}", response_model=List[MembershipPlan])
async def get_membership_plans(
    business_id: str = Path(..., description="Business ID"),
    membership_service: MembershipService = Depends(get_membership_service)
):
    """
    Get all active membership plans for a business.
    
    Returns membership plans with pricing, benefits, and discount information
    for display on product pages and checkout flows.
    
    Args:
        business_id: The unique identifier of the business
        membership_service: Injected membership service
        
    Returns:
        List[MembershipPlan]: A list of active membership plans
        
    Raises:
        HTTPException: If the business is not found or retrieval fails
    """
    
    try:
        plans = await membership_service.get_active_membership_plans(business_id)
        
        # Convert DTOs to API response models
        membership_plans = []
        for plan_dto in plans:
            membership_plan = MembershipPlan(
                id=plan_dto.id,
                name=plan_dto.name,
                plan_type=plan_dto.plan_type,
                description=plan_dto.description,
                tagline=plan_dto.tagline,
                price_monthly=plan_dto.price_monthly,
                price_yearly=plan_dto.price_yearly,
                yearly_savings=plan_dto.yearly_savings,
                setup_fee=plan_dto.setup_fee,
                discount_percentage=plan_dto.discount_percentage,
                priority_service=plan_dto.priority_service,
                extended_warranty=plan_dto.extended_warranty,
                maintenance_included=plan_dto.maintenance_included,
                emergency_response=plan_dto.emergency_response,
                free_diagnostics=plan_dto.free_diagnostics,
                annual_tune_ups=plan_dto.annual_tune_ups,
                is_active=plan_dto.is_active,
                is_featured=plan_dto.is_featured,
                popular_badge=plan_dto.popular_badge,
                color_scheme=plan_dto.color_scheme,
                sort_order=plan_dto.sort_order,
                contract_length_months=plan_dto.contract_length_months,
                cancellation_policy=plan_dto.cancellation_policy
            )
            membership_plans.append(membership_plan)
        
        logger.info(f"Retrieved {len(membership_plans)} membership plans for business {business_id}")
        return membership_plans
        
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Invalid business ID: {business_id}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving membership plans for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve membership plans")
    except Exception as e:
        logger.error(f"Unexpected error retrieving membership plans for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
