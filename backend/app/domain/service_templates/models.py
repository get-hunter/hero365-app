from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ServiceCategory(BaseModel):
    """Standardized service category across trades."""
    id: UUID
    name: str
    description: Optional[str] = None
    slug: str
    trade_types: List[str] = Field(..., description="Trade types this category applies to")
    category_type: str = Field(..., description="Type: equipment, service_type, specialization")
    icon: Optional[str] = Field(None, description="Lucide icon name")
    parent_id: Optional[UUID] = None
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceTemplate(BaseModel):
    """Pre-defined industry-standard service template."""
    id: UUID
    category_id: UUID
    name: str
    description: str
    trade_types: List[str] = Field(..., description="Which trades typically offer this service")
    service_type: str = Field(..., description="product, service, maintenance_plan, emergency")
    pricing_model: str = Field(..., description="fixed, hourly, per_unit, quote_required, tiered")
    default_unit_price: Optional[Decimal] = None
    price_range_min: Optional[Decimal] = None  
    price_range_max: Optional[Decimal] = None
    unit_of_measure: str = "service"
    estimated_duration_hours: Optional[Decimal] = None
    tags: List[str] = Field(default_factory=list)
    is_common: bool = Field(False, description="Most businesses in this trade offer this")
    is_emergency: bool = False
    requires_license: bool = False
    skill_level: Optional[str] = Field(None, description="basic, intermediate, advanced, expert")
    prerequisites: List[str] = Field(default_factory=list)
    upsell_templates: List[UUID] = Field(default_factory=list)
    seasonal_demand: Optional[Dict] = None
    metadata: Dict = Field(default_factory=dict)
    usage_count: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessService(BaseModel):
    """Business-specific instance of a service."""
    id: UUID
    business_id: UUID
    service_name: str  # Maps to database 'service_name'
    service_slug: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None  # Maps to database 'category' (not category_id)
    price_type: str = "range"  # Maps to database 'price_type' (not pricing_model)
    price_min: Optional[Decimal] = None
    price_max: Optional[Decimal] = None
    price_unit: Optional[str] = None
    is_emergency: bool = False
    is_commercial: bool = False
    is_residential: bool = True
    is_active: bool = True
    display_order: int = 0  # Maps to database 'display_order' (not sort_order)
    adopted_from_slug: Optional[str] = None
    template_version: int = 1
    pricing_config: Dict = Field(default_factory=dict)
    booking_settings: Dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessServiceBundle(BaseModel):
    """Package deals combining multiple services."""
    id: UUID
    business_id: UUID
    name: str
    description: Optional[str] = None
    service_ids: List[UUID] = Field(..., description="References to business_services.id")
    bundle_price: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: bool = True
    is_seasonal: bool = False
    is_featured: bool = False
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    max_bookings: Optional[int] = None
    current_bookings: int = 0
    terms_and_conditions: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceTemplateAdoption(BaseModel):
    """Track how businesses customize templates."""
    id: UUID
    template_id: UUID
    business_id: UUID
    business_service_id: UUID
    customizations: Dict = Field(default_factory=dict)
    adopted_at: datetime

    class Config:
        from_attributes = True


# Request/Response Models

class ServiceTemplateListRequest(BaseModel):
    trade_types: Optional[List[str]] = None
    category_id: Optional[UUID] = None
    is_common_only: bool = False
    is_emergency_only: bool = False
    search: Optional[str] = None
    tags: Optional[List[str]] = None
    skill_level: Optional[str] = None
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)


class AdoptServiceTemplateRequest(BaseModel):
    template_id: UUID
    customizations: Optional[Dict] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "template_id": "123e4567-e89b-12d3-a456-426614174000",
                "customizations": {
                    "name": "Emergency AC Repair & Diagnosis",
                    "unit_price": 199.00,
                    "description": "Fast emergency AC repair with same-day service guarantee",
                    "service_areas": ["Miami", "Fort Lauderdale"],
                    "warranty_terms": "90-day parts and labor warranty"
                }
            }
        }


class CreateCustomServiceRequest(BaseModel):
    category_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    pricing_model: str = Field(..., pattern="^(fixed|hourly|per_unit|quote_required|tiered)$")
    unit_price: Optional[Decimal] = Field(None, ge=0)
    minimum_price: Optional[Decimal] = Field(None, ge=0)
    unit_of_measure: str = "service"
    estimated_duration_hours: Optional[Decimal] = Field(None, gt=0)
    is_emergency: bool = False
    requires_booking: bool = True
    service_areas: List[str] = Field(default_factory=list)
    warranty_terms: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    custom_fields: Dict = Field(default_factory=dict)


class BulkAdoptServicesRequest(BaseModel):
    """Adopt multiple service templates at once (useful for onboarding)."""
    template_adoptions: List[AdoptServiceTemplateRequest]
    business_trade_types: List[str] = Field(..., description="Business trade types for filtering")
    
    class Config:
        schema_extra = {
            "example": {
                "template_adoptions": [
                    {
                        "template_id": "123e4567-e89b-12d3-a456-426614174000",
                        "customizations": {"unit_price": 149.00}
                    },
                    {
                        "template_id": "456e7890-e89b-12d3-a456-426614174001", 
                        "customizations": {"name": "Premium AC Installation"}
                    }
                ],
                "business_trade_types": ["hvac"]
            }
        }


class ServiceCategoryWithServices(ServiceCategory):
    """Service category with its associated services."""
    services: List[BusinessService] = Field(default_factory=list)
    service_count: int = 0


class ServiceTemplateWithStats(ServiceTemplate):
    """Service template with usage statistics."""
    adoption_rate: float = Field(0.0, description="Percentage of businesses that adopt this template")
    average_customization_rate: float = Field(0.0, description="How often it gets customized")
    category: ServiceCategory
    

class BusinessServiceWithTemplate(BusinessService):
    """Business service with its template information."""
    template: Optional[ServiceTemplate] = None
    category: ServiceCategory
