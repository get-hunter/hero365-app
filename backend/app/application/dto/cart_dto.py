"""
Cart Data Transfer Objects

DTOs for cart-related data transfer between application layers.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class CartItemDTO(BaseModel):
    """DTO for cart item information."""
    
    id: str = Field(..., description="Cart item ID")
    cart_id: str = Field(..., description="Cart ID")
    product_id: str = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    quantity: int = Field(..., ge=1, description="Item quantity")
    unit_price: float = Field(..., ge=0, description="Product unit price")
    installation_option_id: Optional[str] = Field(None, description="Installation option ID")
    installation_name: Optional[str] = Field(None, description="Installation option name")
    installation_price: float = Field(default=0.0, ge=0, description="Installation price")
    membership_plan_id: Optional[str] = Field(None, description="Applied membership plan ID")
    discount_percentage: int = Field(default=0, ge=0, le=100, description="Discount percentage")
    created_at: datetime = Field(..., description="Item creation timestamp")
    updated_at: datetime = Field(..., description="Item update timestamp")


class CartDTO(BaseModel):
    """DTO for shopping cart information."""
    
    id: str = Field(..., description="Cart ID")
    business_id: str = Field(..., description="Business ID")
    session_id: Optional[str] = Field(None, description="Session ID for guest users")
    customer_id: Optional[str] = Field(None, description="Customer ID for logged-in users")
    items: List[CartItemDTO] = Field(default_factory=list, description="Cart items")
    subtotal: float = Field(default=0.0, ge=0, description="Cart subtotal")
    tax_amount: float = Field(default=0.0, ge=0, description="Tax amount")
    total: float = Field(default=0.0, ge=0, description="Cart total")
    created_at: datetime = Field(..., description="Cart creation timestamp")
    updated_at: datetime = Field(..., description="Cart update timestamp")
    expires_at: Optional[datetime] = Field(None, description="Cart expiration timestamp")


class AddToCartDTO(BaseModel):
    """DTO for adding items to cart."""
    
    product_id: str = Field(..., description="Product ID")
    product_name: Optional[str] = Field(None, description="Product name")
    quantity: int = Field(..., ge=1, description="Item quantity")
    unit_price: Optional[float] = Field(None, ge=0, description="Product unit price")
    installation_option_id: Optional[str] = Field(None, description="Installation option ID")
    installation_name: Optional[str] = Field(None, description="Installation option name")
    installation_price: Optional[float] = Field(None, ge=0, description="Installation price")
    membership_plan_id: Optional[str] = Field(None, description="Membership plan ID for discounts")
    membership_type: Optional[str] = Field(None, description="Membership type")
    discount_percentage: Optional[int] = Field(None, ge=0, le=100, description="Discount percentage")


class CartSummaryDTO(BaseModel):
    """DTO for cart summary information."""
    
    cart_id: str = Field(..., description="Cart ID")
    item_count: int = Field(..., ge=0, description="Number of items in cart")
    subtotal: float = Field(..., ge=0, description="Cart subtotal")
    tax_amount: float = Field(..., ge=0, description="Tax amount")
    total: float = Field(..., ge=0, description="Cart total")
    has_membership_discounts: bool = Field(default=False, description="Cart has membership discounts applied")
    estimated_delivery_date: Optional[datetime] = Field(None, description="Estimated delivery date")


class UpdateCartItemDTO(BaseModel):
    """DTO for updating cart item quantity."""
    
    quantity: int = Field(..., ge=1, description="New item quantity")
