"""
Product-Service Association Domain Entity

Represents the relationship between products and services for 
context-driven merchandising and recommendations.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AssociationType(str, Enum):
    """Types of product-service associations."""
    REQUIRED = "required"        # Required for this service
    RECOMMENDED = "recommended"  # Recommended for this service  
    OPTIONAL = "optional"        # Optional add-on
    UPSELL = "upsell"           # Upsell opportunity
    ACCESSORY = "accessory"     # Accessory/complementary product
    REPLACEMENT = "replacement"  # Replacement part/component


class ProductServiceAssociation(BaseModel):
    """Product-Service Association entity."""
    
    id: UUID
    business_id: UUID
    product_id: UUID
    service_id: UUID
    association_type: AssociationType
    display_order: int = Field(default=0, description="Display order for sorting")
    is_featured: bool = Field(default=False, description="Featured association")
    service_discount_percentage: int = Field(
        default=0, 
        ge=0, 
        le=100, 
        description="Discount percentage when purchased with service"
    )
    bundle_price: Optional[Decimal] = Field(None, description="Special bundle price")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True


class ProductServiceAssociationCreate(BaseModel):
    """Create product-service association request."""
    
    product_id: UUID
    service_id: UUID
    association_type: AssociationType
    display_order: int = 0
    is_featured: bool = False
    service_discount_percentage: int = Field(default=0, ge=0, le=100)
    bundle_price: Optional[Decimal] = None
    notes: Optional[str] = None


class ProductServiceAssociationUpdate(BaseModel):
    """Update product-service association request."""
    
    association_type: Optional[AssociationType] = None
    display_order: Optional[int] = None
    is_featured: Optional[bool] = None
    service_discount_percentage: Optional[int] = Field(None, ge=0, le=100)
    bundle_price: Optional[Decimal] = None
    notes: Optional[str] = None
