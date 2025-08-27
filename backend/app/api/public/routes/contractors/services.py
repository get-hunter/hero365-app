"""
Contractor Services API Routes (Clean Architecture)

Public endpoints for retrieving contractor services and pricing following clean architecture patterns.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List
import logging

from .schemas import ServiceItem, ServiceCategory, MembershipPlan, ServicePricing, ServicePricingCategory
from .....application.services.contractor_service import ContractorService
from .....application.exceptions.application_exceptions import (
    ApplicationError,
    ValidationError,
    EntityNotFoundError
)
from .....infrastructure.config.dependency_injection import get_business_repository

logger = logging.getLogger(__name__)

router = APIRouter()


def get_contractor_service():
    """Get contractor service with proper dependency injection."""
    business_repo = get_business_repository()
    return ContractorService(business_repo)


@router.get("/services/{business_id}", response_model=List[ServiceItem])
async def get_contractor_services(
    business_id: str = Path(..., description="Business ID"),
    category: Optional[str] = Query(None, description="Filter by service category"),
    emergency_only: bool = Query(False, description="Show only emergency services"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of services to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    contractor_service: ContractorService = Depends(get_contractor_service)
):
    """
    Get contractor services offered by a business.
    
    Returns list of services with pricing and availability information.
    
    Args:
        business_id: The unique identifier of the business
        category: Optional category filter
        emergency_only: Only return emergency services
        limit: Maximum number of services to return
        offset: Pagination offset
        contractor_service: Injected contractor service
        
    Returns:
        List[ServiceItem]: A list of services
        
    Raises:
        HTTPException: If the business is not found or retrieval fails
    """
    
    try:
        service_dtos = await contractor_service.get_business_services(
            business_id=business_id,
            category=category,
            emergency_only=emergency_only,
            limit=limit,
            offset=offset
        )
        
        # Convert DTOs to API response models
        service_items = []
        for service_dto in service_dtos:
            service_item = ServiceItem(
                id=service_dto.id,
                name=service_dto.name,
                description=service_dto.description,
                category=service_dto.category,
                base_price=service_dto.base_price,
                price_range_min=service_dto.minimum_price,
                price_range_max=service_dto.maximum_price,
                pricing_unit=service_dto.pricing_model,
                duration_minutes=int(service_dto.estimated_duration_hours * 60),
                is_emergency=service_dto.is_emergency,
                requires_quote=service_dto.requires_consultation,
                available=service_dto.is_available,
                service_areas=service_dto.service_areas,
                keywords=[]  # TODO: Add keywords to DTO
            )
            service_items.append(service_item)
        
        return service_items
        
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Invalid parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving services for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve services")
    except Exception as e:
        logger.error(f"Unexpected error retrieving services for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/service-categories/{business_id}", response_model=List[ServiceCategory])
async def get_contractor_service_categories(
    business_id: str = Path(..., description="Business ID"),
    contractor_service: ContractorService = Depends(get_contractor_service)
):
    """
    Get service categories for a business.
    
    Returns list of service categories with service counts for navigation.
    
    Args:
        business_id: The unique identifier of the business
        contractor_service: Injected contractor service
        
    Returns:
        List[ServiceCategory]: A list of service categories
        
    Raises:
        HTTPException: If the business is not found or retrieval fails
    """
    
    try:
        category_dtos = await contractor_service.get_service_categories(business_id)
        
        # Convert DTOs to API response models
        categories = []
        for category_dto in category_dtos:
            category = ServiceCategory(
                id=category_dto.id,
                name=category_dto.name,
                description=category_dto.description,
                service_count=category_dto.service_count,
                sort_order=category_dto.sort_order
            )
            categories.append(category)
        
        return categories
        
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Invalid business ID: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving service categories for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve service categories")
    except Exception as e:
        logger.error(f"Unexpected error retrieving service categories for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/service-pricing/{business_id}/{service_id}", response_model=ServicePricing)
async def get_service_pricing(
    business_id: str = Path(..., description="Business ID"),
    service_id: str = Path(..., description="Service ID"),
    membership_plan_id: Optional[str] = Query(None, description="Membership plan ID for discounts"),
    service_area: Optional[str] = Query(None, description="Service area for location-based pricing"),
    estimated_hours: Optional[float] = Query(None, ge=0.5, le=24, description="Estimated hours for hourly services"),
    contractor_service: ContractorService = Depends(get_contractor_service)
):
    """
    Calculate pricing for a service with membership discounts.
    
    Args:
        business_id: The unique identifier of the business
        service_id: The unique identifier of the service
        membership_plan_id: Optional membership plan for discounts
        service_area: Service area for location-based pricing
        estimated_hours: Estimated hours for hourly services
        contractor_service: Injected contractor service
        
    Returns:
        ServicePricing: Detailed service pricing breakdown
        
    Raises:
        HTTPException: If the business or service is not found
    """
    
    try:
        pricing_dto = await contractor_service.calculate_service_pricing(
            business_id=business_id,
            service_id=service_id,
            membership_plan_id=membership_plan_id,
            service_area=service_area,
            estimated_hours=estimated_hours
        )
        
        service_pricing = ServicePricing(
            service_id=pricing_dto.service_id,
            service_name=pricing_dto.service_name,
            base_price=pricing_dto.base_price,
            membership_plan_id=pricing_dto.membership_plan_id,
            membership_plan_name=pricing_dto.membership_plan_name,
            discount_percentage=pricing_dto.discount_percentage,
            discount_amount=pricing_dto.discount_amount,
            subtotal=pricing_dto.subtotal,
            tax_rate=pricing_dto.tax_rate,
            tax_amount=pricing_dto.tax_amount,
            total=pricing_dto.total,
            service_area=pricing_dto.service_area,
            estimated_hours=pricing_dto.estimated_hours
        )
        
        return service_pricing
        
    except EntityNotFoundError as e:
        logger.warning(f"Business or service not found: {business_id}/{service_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Invalid parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error calculating service pricing for {service_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate service pricing")
    except Exception as e:
        logger.error(f"Unexpected error calculating service pricing for {service_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
