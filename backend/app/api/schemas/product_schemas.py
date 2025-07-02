"""
Product API Schemas

Pydantic schemas for product and inventory management API endpoints.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator, field_validator

# Core Product Schemas

class ProductPricingTierSchema(BaseModel):
    """Schema for product pricing tiers."""
    min_quantity: Decimal = Field(..., gt=0, description="Minimum quantity for this tier")
    max_quantity: Optional[Decimal] = Field(None, ge=0, description="Maximum quantity for this tier")
    unit_price: Decimal = Field(..., ge=0, description="Unit price for this tier")
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Discount percentage")

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ProductLocationSchema(BaseModel):
    """Schema for product location inventory."""
    location_id: uuid.UUID
    location_name: str = Field(..., min_length=1, max_length=200)
    quantity_on_hand: Decimal = Field(default=Decimal('0'), ge=0)
    quantity_reserved: Decimal = Field(default=Decimal('0'), ge=0)
    bin_location: Optional[str] = Field(None, max_length=100)
    last_counted_date: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }


class ProductSupplierSchema(BaseModel):
    """Schema for product supplier information."""
    supplier_id: uuid.UUID
    supplier_name: str = Field(..., min_length=1, max_length=200)
    supplier_sku: Optional[str] = Field(None, max_length=100)
    cost_price: Decimal = Field(..., ge=0)
    lead_time_days: Optional[int] = Field(None, ge=0)
    minimum_order_quantity: Optional[Decimal] = Field(None, gt=0)
    is_preferred: bool = Field(default=False)
    last_order_date: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }


class CreateProductSchema(BaseModel):
    """Schema for creating products."""
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    name: str = Field(..., min_length=1, max_length=300, description="Product name")
    description: Optional[str] = Field(None, max_length=2000, description="Product description")
    product_type: str = Field("product", description="Product type")
    status: str = Field("active", description="Product status")
    category_id: Optional[uuid.UUID] = Field(None, description="Product category identifier")
    
    # Pricing and costs
    pricing_model: str = Field("fixed", description="Pricing model")
    unit_price: Decimal = Field(default=Decimal('0'), ge=0, description="Base unit price")
    cost_price: Decimal = Field(default=Decimal('0'), ge=0, description="Unit cost")
    markup_percentage: Optional[Decimal] = Field(None, ge=0, description="Markup percentage over cost")
    currency: str = Field("USD", pattern="^[A-Z]{3}$", description="Currency code")
    
    # Inventory settings
    track_inventory: bool = Field(default=True, description="Whether to track inventory")
    unit_of_measure: str = Field("each", description="Unit of measure")
    initial_quantity: Decimal = Field(default=Decimal('0'), ge=0, description="Initial stock quantity")
    reorder_point: Optional[Decimal] = Field(None, ge=0, description="Reorder point quantity")
    reorder_quantity: Optional[Decimal] = Field(None, gt=0, description="Quantity to reorder")
    minimum_quantity: Optional[Decimal] = Field(None, ge=0, description="Minimum stock level")
    maximum_quantity: Optional[Decimal] = Field(None, gt=0, description="Maximum stock level")
    costing_method: str = Field("weighted_average", description="Cost calculation method")
    
    # Physical attributes
    weight: Optional[Decimal] = Field(None, ge=0, description="Product weight")
    weight_unit: Optional[str] = Field(None, max_length=20, description="Weight unit")
    dimensions: Optional[Dict[str, Decimal]] = Field(None, description="Product dimensions")
    
    # Tax settings
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="Tax rate percentage")
    tax_code: Optional[str] = Field(None, max_length=50, description="Tax code")
    is_taxable: bool = Field(default=True, description="Whether product is taxable")
    
    # Supplier
    primary_supplier_id: Optional[uuid.UUID] = Field(None, description="Primary supplier identifier")
    
    # Additional attributes
    barcode: Optional[str] = Field(None, max_length=100, description="Product barcode")
    manufacturer: Optional[str] = Field(None, max_length=200, description="Manufacturer name")
    manufacturer_sku: Optional[str] = Field(None, max_length=100, description="Manufacturer SKU")
    brand: Optional[str] = Field(None, max_length=100, description="Brand name")
    image_urls: Optional[List[str]] = Field(default_factory=list, description="Product image URLs")

    @validator('sku')
    def validate_sku(cls, v):
        if not v or v.strip() == "":
            raise ValueError('SKU cannot be empty')
        return v.strip().upper()

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v)
        }


class UpdateProductSchema(BaseModel):
    """Schema for updating products."""
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    
    # Pricing and costs
    unit_price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    markup_percentage: Optional[Decimal] = Field(None, ge=0)
    
    # Inventory settings
    track_inventory: Optional[bool] = None
    reorder_point: Optional[Decimal] = Field(None, ge=0)
    reorder_quantity: Optional[Decimal] = Field(None, gt=0)
    minimum_quantity: Optional[Decimal] = Field(None, ge=0)
    maximum_quantity: Optional[Decimal] = Field(None, gt=0)
    
    # Physical attributes
    weight: Optional[Decimal] = Field(None, ge=0)
    weight_unit: Optional[str] = Field(None, max_length=20)
    dimensions: Optional[Dict[str, Decimal]] = None
    
    # Tax settings
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    tax_code: Optional[str] = Field(None, max_length=50)
    is_taxable: Optional[bool] = None
    
    # Supplier
    primary_supplier_id: Optional[uuid.UUID] = None
    
    # Additional attributes
    barcode: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=200)
    manufacturer_sku: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    image_urls: Optional[List[str]] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v)
        }


class ProductResponseSchema(BaseModel):
    """Schema for product responses."""
    id: uuid.UUID
    business_id: uuid.UUID
    sku: str
    name: str
    description: Optional[str] = None
    product_type: str
    product_type_display: str
    status: str
    status_display: str
    category_id: Optional[uuid.UUID] = None
    category_name: Optional[str] = None
    
    # Pricing and costs
    pricing_model: str
    unit_price: Decimal
    currency: str
    unit_cost: Decimal
    average_cost: Decimal
    markup_percentage: Optional[Decimal] = None
    margin_percentage: Optional[Decimal] = None
    
    # Inventory quantities
    track_inventory: bool
    quantity_on_hand: Decimal = Decimal('0')
    quantity_reserved: Decimal = Decimal('0')
    quantity_available: Decimal = Decimal('0')
    quantity_on_order: Decimal = Decimal('0')
    
    # Reorder management
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    minimum_quantity: Optional[Decimal] = None
    maximum_quantity: Optional[Decimal] = None
    needs_reorder: bool = False
    is_low_stock: bool = False
    is_out_of_stock: bool = False
    
    # Physical attributes
    unit_of_measure: str
    weight: Optional[Decimal] = None
    weight_unit: Optional[str] = None
    dimensions: Optional[Dict[str, Decimal]] = None
    
    # Tax settings
    tax_rate: Decimal
    tax_code: Optional[str] = None
    is_taxable: bool
    
    # Supplier information
    primary_supplier_id: Optional[uuid.UUID] = None
    suppliers: List[ProductSupplierSchema] = Field(default_factory=list)
    
    # Location inventory
    locations: List[ProductLocationSchema] = Field(default_factory=list)
    
    # Pricing tiers
    pricing_tiers: List[ProductPricingTierSchema] = Field(default_factory=list)
    
    # Additional attributes
    barcode: Optional[str] = None
    manufacturer: Optional[str] = None
    manufacturer_sku: Optional[str] = None
    brand: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)
    
    # Analytics
    times_sold: int = 0
    last_sale_date: Optional[datetime] = None
    last_purchase_date: Optional[datetime] = None
    inventory_value: Decimal = Decimal('0')
    
    # Metadata
    created_by: str
    created_date: datetime
    last_modified: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }


class ProductSummarySchema(BaseModel):
    """Schema for product summary responses."""
    id: uuid.UUID
    sku: str
    name: str
    status: str
    unit_price: Decimal
    quantity_on_hand: Decimal
    quantity_available: Decimal
    is_low_stock: bool
    is_out_of_stock: bool
    category_name: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v)
        }


# Stock Management Schemas

class StockAdjustmentSchema(BaseModel):
    """Schema for stock adjustments."""
    product_id: uuid.UUID
    quantity_change: Decimal = Field(..., description="Quantity change (positive for increase, negative for decrease)")
    adjustment_reason: str = Field(..., min_length=1, max_length=500, description="Reason for adjustment")
    reference_number: Optional[str] = Field(None, max_length=100, description="Reference number")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")

    @validator('quantity_change')
    def validate_quantity_change(cls, v):
        if v == 0:
            raise ValueError('Quantity change cannot be zero')
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v)
        }


class StockMovementResponseSchema(BaseModel):
    """Schema for stock movement responses."""
    id: uuid.UUID
    business_id: uuid.UUID
    product_id: uuid.UUID
    product_sku: Optional[str] = None
    product_name: Optional[str] = None
    movement_type: str
    movement_type_display: str
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    quantity_before: Decimal
    quantity_after: Decimal
    reason: Optional[str] = None
    notes: Optional[str] = None
    reference_number: Optional[str] = None
    movement_date: datetime
    created_by: str
    created_date: datetime
    is_approved: bool
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }


# Product Search and Filter Schemas

class ProductSearchSchema(BaseModel):
    """Schema for product search parameters."""
    search_term: Optional[str] = Field(None, max_length=200, description="Search in SKU, name, description")
    category_id: Optional[uuid.UUID] = Field(None, description="Filter by category")
    status: Optional[str] = Field(None, description="Filter by status")
    product_type: Optional[str] = Field(None, description="Filter by product type")
    supplier_id: Optional[uuid.UUID] = Field(None, description="Filter by supplier")
    low_stock_only: bool = Field(False, description="Show only low stock items")
    out_of_stock_only: bool = Field(False, description="Show only out of stock items")
    needs_reorder_only: bool = Field(False, description="Show only items needing reorder")
    min_price: Optional[Decimal] = Field(None, ge=0, description="Minimum unit price")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Maximum unit price")
    min_quantity: Optional[Decimal] = Field(None, ge=0, description="Minimum quantity on hand")
    max_quantity: Optional[Decimal] = Field(None, ge=0, description="Maximum quantity on hand")
    barcode: Optional[str] = Field(None, max_length=100, description="Filter by barcode")
    manufacturer: Optional[str] = Field(None, max_length=200, description="Filter by manufacturer")
    brand: Optional[str] = Field(None, max_length=100, description="Filter by brand")
    created_from: Optional[date] = Field(None, description="Created from date")
    created_to: Optional[date] = Field(None, description="Created to date")
    created_by: Optional[str] = Field(None, description="Filter by creator")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")
    sort_by: str = Field("name", max_length=50, description="Field to sort by")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")

    @validator('max_price')
    def validate_max_price(cls, v, values):
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v < values['min_price']:
                raise ValueError('max_price must be greater than or equal to min_price')
        return v

    @validator('max_quantity')
    def validate_max_quantity(cls, v, values):
        if v is not None and 'min_quantity' in values and values['min_quantity'] is not None:
            if v < values['min_quantity']:
                raise ValueError('max_quantity must be greater than or equal to min_quantity')
        return v

    @validator('created_to')
    def validate_created_to(cls, v, values):
        if v and 'created_from' in values and values['created_from']:
            if v < values['created_from']:
                raise ValueError('created_to must be greater than or equal to created_from')
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v),
            date: lambda v: v.isoformat()
        }


class ProductListResponseSchema(BaseModel):
    """Schema for product list responses."""
    products: List[ProductResponseSchema]
    total_count: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

    class Config:
        from_attributes = True


# Reorder Management Schemas

class ReorderSuggestionSchema(BaseModel):
    """Schema for reorder suggestions."""
    product_id: uuid.UUID
    sku: str
    name: str
    current_stock: Decimal
    available_stock: Decimal
    reorder_point: Optional[Decimal] = None
    suggested_quantity: Decimal
    unit_cost: Decimal
    suggested_cost: Decimal
    priority: str = Field(..., pattern="^(high|medium|low)$")
    days_until_stockout: Optional[int] = None
    supplier_id: Optional[uuid.UUID] = None
    supplier_name: Optional[str] = None
    lead_time_days: Optional[int] = None
    category_name: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v)
        }


class ReorderSuggestionsResponseSchema(BaseModel):
    """Schema for reorder suggestions response."""
    suggestions: List[ReorderSuggestionSchema]
    total_items: int
    total_suggested_value: Decimal
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    generated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


# Action Response Schemas

class ProductActionResponse(BaseModel):
    """Schema for product action responses."""
    success: bool = True
    message: str
    product_id: Optional[uuid.UUID] = None
    data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: lambda v: str(v)
        }


class StockActionResponse(BaseModel):
    """Schema for stock action responses."""
    success: bool = True
    message: str
    movement_id: Optional[uuid.UUID] = None
    quantity_before: Optional[Decimal] = None
    quantity_after: Optional[Decimal] = None
    quantity_change: Optional[Decimal] = None

    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: lambda v: str(v),
            Decimal: lambda v: float(v)
        } 