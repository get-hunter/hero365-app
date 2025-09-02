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
from ...infrastructure.database.repositories.supabase_service_template_repository import SupabaseBusinessServiceRepository
from ...domain.services.default_services_mapping import DefaultServicesMapping
from ...domain.services.slug_utils import SlugUtils
from ...core.db import get_supabase_client

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
        self.default_services_mapping = DefaultServicesMapping()
        # Initialize business service repository
        supabase_client = get_supabase_client()
        self.business_service_repository = SupabaseBusinessServiceRepository(supabase_client)
    
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
                raise EntityNotFoundError("Business", business_id)
            
            # PREFERENCE 1: Use business_services table (primary source)
            try:
                business_services = await self.business_service_repository.list_business_services(
                    business_id=business_uuid,
                    category_id=None,  # TODO: Map category string to UUID if needed
                    is_active=True,
                    is_featured=None,
                    include_template=False
                )
                
                if business_services:
                    logger.info(f"Using business_services table data: {len(business_services)} services")
                    return self._convert_business_services_to_dtos(business_services, emergency_only, limit, offset)
                    
            except Exception as e:
                logger.warning(f"Failed to get business_services for {business_id}: {str(e)}")
            
            # PREFERENCE 2: Use selected service keys from business (fallback 1)
            residential_keys = business.selected_residential_service_keys or []
            commercial_keys = business.selected_commercial_service_keys or []
            all_service_keys = residential_keys + commercial_keys
            
            if all_service_keys:
                logger.info(f"Using selected service keys: {len(all_service_keys)} services")
                return self._convert_service_keys_to_dtos(all_service_keys, business, emergency_only, limit, offset)
            
            # PREFERENCE 3: Use default mapping based on trades (fallback 2)
            logger.info("Using default service mapping based on trades")
            default_services = self.default_services_mapping.get_default_services(
                primary_trade=business.primary_trade,
                secondary_trades=business.secondary_trades or [],
                market_focus=business.market_focus
            )
            
            all_default_keys = default_services['residential'] + default_services['commercial']
            return self._convert_service_keys_to_dtos(all_default_keys, business, emergency_only, limit, offset)
            
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
                raise EntityNotFoundError("Business", business_id)
            
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
                raise EntityNotFoundError("Business", business_id)
            
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
    
    def _convert_business_services_to_dtos(
        self, 
        business_services: List, 
        emergency_only: bool, 
        limit: int, 
        offset: int
    ) -> List[ServiceItemDTO]:
        """Convert business_services table data to ServiceItemDTO objects."""
        service_dtos = []
        
        for service in business_services:
            # Apply emergency filter
            if emergency_only and not getattr(service, 'is_emergency', False):
                continue
            
            # Convert to DTO
            service_dto = ServiceItemDTO(
                id=str(service.id),
                name=service.service_name,
                description=service.description or f"Professional {service.service_name} services",
                category=service.category or "General",
                pricing_model="range" if service.price_min and service.price_max else "quote",
                base_price=float(service.price_min or 0),
                minimum_price=float(service.price_min or 0),
                maximum_price=float(service.price_max or service.price_min or 0),
                estimated_duration_hours=4,  # Default estimate
                is_emergency=getattr(service, 'is_emergency', False),
                is_available=getattr(service, 'is_active', True),
                requires_consultation=service.price_min is None,  # No price = needs quote
                service_areas=[],  # TODO: Get from business
                certifications_required=[],
                equipment_needed=[],
                warranty_years=1
            )
            service_dtos.append(service_dto)
        
        # Apply pagination
        start = offset
        end = offset + limit
        return service_dtos[start:end]
    
    def _convert_service_keys_to_dtos(
        self, 
        service_keys: List[str], 
        business, 
        emergency_only: bool, 
        limit: int, 
        offset: int
    ) -> List[ServiceItemDTO]:
        """Convert service keys to ServiceItemDTO objects using default mapping."""
        service_dtos = []
        
        for service_key in service_keys:
            # Apply emergency filter
            if emergency_only and "emergency" not in service_key.lower():
                continue
            
            # Generate service details from key
            service_name = SlugUtils.service_key_to_display_name(service_key)
            is_emergency = "emergency" in service_key.lower()
            is_installation = "installation" in service_key.lower()
            
            # Estimate pricing based on service type
            if is_installation:
                base_price = 2000.0
                max_price = 8000.0
                duration = 8
            elif is_emergency:
                base_price = 200.0
                max_price = 1200.0
                duration = 2
            else:
                base_price = 150.0
                max_price = 800.0
                duration = 4
            
            service_dto = ServiceItemDTO(
                id=f"key-{service_key}",
                name=service_name,
                description=f"Professional {service_name.lower()} services by {business.name}",
                category="Installation" if is_installation else "Repair" if not is_emergency else "Emergency",
                pricing_model="range",
                base_price=base_price,
                minimum_price=base_price,
                maximum_price=max_price,
                estimated_duration_hours=duration,
                is_emergency=is_emergency,
                is_available=True,
                requires_consultation=is_installation,
                service_areas=business.service_areas or [],
                certifications_required=[],
                equipment_needed=[],
                warranty_years=2 if is_installation else 1
            )
            service_dtos.append(service_dto)
        
        # Apply pagination
        start = offset
        end = offset + limit
        return service_dtos[start:end]
