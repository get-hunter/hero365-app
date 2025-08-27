"""
Product Data Transfer Objects

DTOs for product-related data transfer between application layers.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ProductItemDTO(BaseModel):
    """DTO for basic product information."""
    
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    category: str = Field(..., description="Product category")
    brand: str = Field(..., description="Product brand")
    model: str = Field(..., description="Product model")
    sku: str = Field(..., description="Product SKU")
    price: float = Field(..., description="Product price")
    msrp: Optional[float] = Field(None, description="Manufacturer suggested retail price")
    in_stock: bool = Field(..., description="Product is in stock")
    stock_quantity: int = Field(..., description="Available stock quantity")
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Product specifications")
    warranty_years: Optional[int] = Field(None, description="Warranty period in years")
    energy_rating: Optional[str] = Field(None, description="Energy efficiency rating")


class ProductCatalogDTO(BaseModel):
    """DTO for product catalog with full details and installation options."""
    
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    category: str = Field(..., description="Product category")
    brand: str = Field(..., description="Product brand")
    model: str = Field(..., description="Product model")
    sku: str = Field(..., description="Product SKU")
    unit_price: float = Field(..., description="Product unit price")
    msrp: Optional[float] = Field(None, description="Manufacturer suggested retail price")
    in_stock: bool = Field(..., description="Product is in stock")
    stock_quantity: int = Field(..., description="Available stock quantity")
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Product specifications")
    warranty_years: Optional[int] = Field(None, description="Warranty period in years")
    energy_rating: Optional[str] = Field(None, description="Energy efficiency rating")
    images: List[str] = Field(default_factory=list, description="Product image URLs")
    has_variations: bool = Field(default=False, description="Product has variations")
    is_featured: bool = Field(default=False, description="Product is featured")
    tags: List[str] = Field(default_factory=list, description="Product tags")


class PricingBreakdownDTO(BaseModel):
    """DTO for detailed pricing breakdown."""
    
    product_id: str = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    quantity: int = Field(..., description="Product quantity")
    unit_price: float = Field(..., description="Unit price")
    product_subtotal: float = Field(..., description="Product subtotal")
    installation_option_id: Optional[str] = Field(None, description="Selected installation option ID")
    installation_name: Optional[str] = Field(None, description="Installation option name")
    installation_price: float = Field(default=0.0, description="Installation price")
    subtotal: float = Field(..., description="Subtotal before discounts")
    membership_plan_id: Optional[str] = Field(None, description="Applied membership plan ID")
    membership_plan_name: Optional[str] = Field(None, description="Applied membership plan name")
    discount_percentage: int = Field(default=0, description="Applied discount percentage")
    discount_amount: float = Field(default=0.0, description="Discount amount")
    tax_rate: float = Field(..., description="Tax rate applied")
    tax_amount: float = Field(..., description="Tax amount")
    total: float = Field(..., description="Final total after all calculations")


class ProductInstallationOptionDTO(BaseModel):
    """DTO for product installation options."""
    
    id: str = Field(..., description="Installation option ID")
    name: str = Field(..., description="Installation option name")
    description: str = Field(..., description="Installation description")
    base_install_price: float = Field(..., description="Base installation price")
    estimated_duration_hours: int = Field(..., description="Estimated installation time in hours")
    requires_permit: bool = Field(default=False, description="Installation requires permit")
    includes_materials: bool = Field(default=True, description="Installation includes materials")
    warranty_years: int = Field(default=1, description="Installation warranty in years")
    is_default: bool = Field(default=False, description="Default installation option")


class CreateProductDTO(BaseModel):
    """DTO for creating a new product."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: str = Field(..., min_length=1, max_length=1000, description="Product description")
    category_id: str = Field(..., description="Product category ID")
    brand: str = Field(..., min_length=1, max_length=100, description="Product brand")
    model: str = Field(..., min_length=1, max_length=100, description="Product model")
    sku: str = Field(..., min_length=1, max_length=50, description="Product SKU")
    unit_price: float = Field(..., gt=0, description="Product unit price")
    msrp: Optional[float] = Field(None, gt=0, description="Manufacturer suggested retail price")
    cost_price: Optional[float] = Field(None, ge=0, description="Product cost price")
    stock_quantity: int = Field(default=0, ge=0, description="Initial stock quantity")
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Product specifications")
    warranty_years: Optional[int] = Field(None, ge=0, le=10, description="Warranty period in years")
    energy_rating: Optional[str] = Field(None, max_length=10, description="Energy efficiency rating")
    is_featured: bool = Field(default=False, description="Product is featured")
    tags: List[str] = Field(default_factory=list, description="Product tags")


class ProductDTO(BaseModel):
    """DTO for complete product information."""
    
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    category_id: str = Field(..., description="Product category ID")
    brand: str = Field(..., description="Product brand")
    model: str = Field(..., description="Product model")
    sku: str = Field(..., description="Product SKU")
    unit_price: float = Field(..., description="Product unit price")
    msrp: Optional[float] = Field(None, description="Manufacturer suggested retail price")
    cost_price: Optional[float] = Field(None, description="Product cost price")
    stock_quantity: int = Field(..., description="Stock quantity")
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Product specifications")
    warranty_years: Optional[int] = Field(None, description="Warranty period in years")
    energy_rating: Optional[str] = Field(None, description="Energy efficiency rating")
    is_featured: bool = Field(default=False, description="Product is featured")
    tags: List[str] = Field(default_factory=list, description="Product tags")
    is_active: bool = Field(default=True, description="Product is active")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Update timestamp")


class StockAdjustmentDTO(BaseModel):
    """DTO for stock adjustments."""
    
    product_id: str = Field(..., description="Product ID")
    adjustment_type: str = Field(..., description="Adjustment type (increase, decrease, set)")
    quantity: int = Field(..., description="Adjustment quantity")
    reason: str = Field(..., description="Reason for adjustment")
    reference_number: Optional[str] = Field(None, description="Reference number")
    notes: Optional[str] = Field(None, description="Additional notes")


class ProductSearchCriteria(BaseModel):
    """DTO for product search criteria."""
    
    query: Optional[str] = Field(None, description="Search query")
    category_id: Optional[str] = Field(None, description="Filter by category")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price filter")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price filter")
    in_stock_only: bool = Field(default=True, description="Only show in-stock products")
    featured_only: bool = Field(default=False, description="Only show featured products")
    tags: List[str] = Field(default_factory=list, description="Filter by tags")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Pagination offset")


class ProductListDTO(BaseModel):
    """DTO for product list response."""
    
    products: List[ProductDTO] = Field(default_factory=list, description="List of products")
    total_count: int = Field(..., description="Total number of products")
    has_more: bool = Field(..., description="Whether there are more products")
    offset: int = Field(..., description="Current offset")
    limit: int = Field(..., description="Current limit")


class ProductSummaryDTO(BaseModel):
    """DTO for product summary information."""
    
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    sku: str = Field(..., description="Product SKU")
    unit_price: float = Field(..., description="Product unit price")
    stock_quantity: int = Field(..., description="Stock quantity")
    is_active: bool = Field(default=True, description="Product is active")
    category_name: Optional[str] = Field(None, description="Category name")


class ProductCategoryDTO(BaseModel):
    """DTO for product categories."""
    
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    parent_id: Optional[str] = Field(None, description="Parent category ID")
    is_active: bool = Field(default=True, description="Category is active")
    sort_order: int = Field(default=0, description="Display sort order")
    product_count: int = Field(default=0, description="Number of products in category")
