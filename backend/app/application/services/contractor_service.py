"""
Contractor Service Application Service

Orchestrates contractor service-related business operations and use cases.
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal

from ..dto.service_dto import (
    ServiceItemDTO,
    ServiceCategoryDTO,
    ServicePricingDTO
)
from ..exceptions.application_exceptions import (
    ApplicationError,
    ValidationError,
    EntityNotFoundError
)
from ...domain.repositories.business_repository import BusinessRepository

logger = logging.getLogger(__name__)


class ContractorService:
    """
    Application service for contractor service operations.
    
    Handles business logic for service catalog, pricing, and availability,
    following clean architecture principles.
    """
    
    def __init__(
        self,
        business_repository: BusinessRepository
    ):
        self.business_repository = business_repository
    
    async def get_business_services(
        self,
        business_id: str,
        category: Optional[str] = None,
        emergency_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[ServiceItemDTO]:
        """
        Get services for a business with filtering options.
        
        Args:
            business_id: Business identifier
            category: Optional category filter
            emergency_only: Only return emergency services
            limit: Maximum number of services to return
            offset: Pagination offset
            
        Returns:
            List of service items as DTOs
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If parameters are invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError(f"Business not found: {business_id}")
            
            # TODO: Implement proper service repository
            # For now, return sample data
            sample_services = [
                ServiceItemDTO(
                    id="service-1",
                    name="HVAC System Installation",
                    description="Complete HVAC system installation for residential and commercial properties",
                    category="Installation",
                    pricing_model="fixed",
                    base_price=2500.0,
                    minimum_price=2000.0,
                    maximum_price=5000.0,
                    estimated_duration_hours=8,
                    is_emergency=False,
                    is_available=True,
                    requires_consultation=True,
                    service_areas=["Austin", "Round Rock", "Cedar Park"],
                    certifications_required=["EPA 608", "NATE Certified"],
                    equipment_needed=["Installation tools", "Refrigerant recovery unit"],
                    warranty_years=5
                ),
                ServiceItemDTO(
                    id="service-2",
                    name="Emergency HVAC Repair",
                    description="24/7 emergency HVAC repair services",
                    category="Repair",
                    pricing_model="hourly",
                    base_price=150.0,
                    minimum_price=150.0,
                    maximum_price=500.0,
                    estimated_duration_hours=2,
                    is_emergency=True,
                    is_available=True,
                    requires_consultation=False,
                    service_areas=["Austin", "Round Rock", "Cedar Park", "Georgetown"],
                    certifications_required=["EPA 608"],
                    equipment_needed=["Diagnostic tools", "Common repair parts"],
                    warranty_years=1
                )
            ]
            
            # Apply filters
            filtered_services = []
            for service in sample_services:
                if category and service.category != category:
                    continue
                if emergency_only and not service.is_emergency:
                    continue
                filtered_services.append(service)
            
            # Apply pagination
            start = offset
            end = offset + limit
            paginated_services = filtered_services[start:end]
            
            logger.info(f"Retrieved {len(paginated_services)} services for business {business_id}")
            return paginated_services
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error retrieving services for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve services: {str(e)}")
    
    async def get_service_categories(
        self,
        business_id: str
    ) -> List[ServiceCategoryDTO]:
        """
        Get service categories for a business.
        
        Args:
            business_id: Business identifier
            
        Returns:
            List of service categories as DTOs
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If business ID is invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError(f"Business not found: {business_id}")
            
            # TODO: Implement proper service category repository
            # For now, return sample data
            sample_categories = [
                ServiceCategoryDTO(
                    id="cat-1",
                    name="Installation",
                    description="New system installations",
                    service_count=5,
                    is_active=True,
                    sort_order=1
                ),
                ServiceCategoryDTO(
                    id="cat-2",
                    name="Repair",
                    description="System repairs and troubleshooting",
                    service_count=8,
                    is_active=True,
                    sort_order=2
                ),
                ServiceCategoryDTO(
                    id="cat-3",
                    name="Maintenance",
                    description="Preventive maintenance services",
                    service_count=6,
                    is_active=True,
                    sort_order=3
                )
            ]
            
            logger.info(f"Retrieved {len(sample_categories)} service categories for business {business_id}")
            return sample_categories
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error retrieving service categories for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve service categories: {str(e)}")
    
    async def calculate_service_pricing(
        self,
        business_id: str,
        service_id: str,
        membership_plan_id: Optional[str] = None,
        service_area: Optional[str] = None,
        estimated_hours: Optional[float] = None
    ) -> ServicePricingDTO:
        """
        Calculate pricing for a service with membership discounts.
        
        Args:
            business_id: Business identifier
            service_id: Service identifier
            membership_plan_id: Optional membership plan for discounts
            service_area: Service area for location-based pricing
            estimated_hours: Estimated hours for hourly services
            
        Returns:
            Service pricing breakdown
            
        Raises:
            EntityNotFoundError: If business or service doesn't exist
            ValidationError: If parameters are invalid
            ApplicationError: If calculation fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError(f"Business not found: {business_id}")
            
            # TODO: Get service from repository
            # For now, use sample pricing
            base_price = Decimal("150.00")
            if estimated_hours:
                base_price = base_price * Decimal(str(estimated_hours))
            
            # Apply membership discount if specified
            discount_percentage = 0
            discount_amount = Decimal("0")
            membership_plan_name = None
            
            if membership_plan_id:
                # TODO: Get membership plan and apply discount
                discount_percentage = 10  # Sample 10% discount
                discount_amount = base_price * Decimal("0.10")
                membership_plan_name = "Residential Plan"  # Sample
            
            # Calculate final pricing
            subtotal = base_price - discount_amount
            tax_rate = Decimal("0.08")  # 8% tax
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount
            
            return ServicePricingDTO(
                service_id=service_id,
                service_name="Sample Service",  # TODO: Get from repository
                base_price=float(base_price),
                membership_plan_id=membership_plan_id,
                membership_plan_name=membership_plan_name,
                discount_percentage=discount_percentage,
                discount_amount=float(discount_amount),
                subtotal=float(subtotal),
                tax_rate=float(tax_rate),
                tax_amount=float(tax_amount),
                total=float(total),
                service_area=service_area,
                estimated_hours=estimated_hours
            )
            
        except ValueError as e:
            raise ValidationError(f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error calculating service pricing: {str(e)}")
            raise ApplicationError(f"Failed to calculate service pricing: {str(e)}")
