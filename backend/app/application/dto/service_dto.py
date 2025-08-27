"""
Service Data Transfer Objects

DTOs for service-related data transfer between application layers.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class ServiceItemDTO(BaseModel):
    """DTO for service information."""
    
    id: str = Field(..., description="Service ID")
    name: str = Field(..., description="Service name")
    description: str = Field(..., description="Service description")
    category: str = Field(..., description="Service category")
    pricing_model: str = Field(..., description="Pricing model (fixed, hourly, per_unit)")
    base_price: float = Field(..., description="Base service price")
    minimum_price: float = Field(..., description="Minimum service price")
    maximum_price: Optional[float] = Field(None, description="Maximum service price")
    estimated_duration_hours: int = Field(..., description="Estimated duration in hours")
    is_emergency: bool = Field(default=False, description="Emergency service")
    is_available: bool = Field(default=True, description="Service is available")
    requires_consultation: bool = Field(default=False, description="Requires consultation")
    service_areas: List[str] = Field(default_factory=list, description="Service areas")
    certifications_required: List[str] = Field(default_factory=list, description="Required certifications")
    equipment_needed: List[str] = Field(default_factory=list, description="Equipment needed")
    warranty_years: int = Field(default=1, description="Warranty period in years")


class ServiceCategoryDTO(BaseModel):
    """DTO for service categories."""
    
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    service_count: int = Field(default=0, description="Number of services in category")
    is_active: bool = Field(default=True, description="Category is active")
    sort_order: int = Field(default=0, description="Display sort order")


class ServicePricingDTO(BaseModel):
    """DTO for service pricing calculations."""
    
    service_id: str = Field(..., description="Service ID")
    service_name: str = Field(..., description="Service name")
    base_price: float = Field(..., description="Base service price")
    membership_plan_id: Optional[str] = Field(None, description="Applied membership plan ID")
    membership_plan_name: Optional[str] = Field(None, description="Applied membership plan name")
    discount_percentage: int = Field(default=0, description="Applied discount percentage")
    discount_amount: float = Field(default=0.0, description="Discount amount")
    subtotal: float = Field(..., description="Subtotal after discount")
    tax_rate: float = Field(..., description="Tax rate applied")
    tax_amount: float = Field(..., description="Tax amount")
    total: float = Field(..., description="Final total")
    service_area: Optional[str] = Field(None, description="Service area")
    estimated_hours: Optional[float] = Field(None, description="Estimated hours")
