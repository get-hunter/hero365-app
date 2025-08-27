"""
Shopping Cart Domain Entities

Domain entities for shopping cart functionality.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class CartItem(BaseModel):
    """Cart item domain entity."""
    
    id: uuid.UUID = Field(..., description="Cart item ID")
    cart_id: uuid.UUID = Field(..., description="Cart ID")
    product_id: uuid.UUID = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    product_sku: str = Field(..., description="Product SKU")
    quantity: int = Field(..., ge=1, description="Item quantity")
    unit_price: Decimal = Field(..., ge=0, description="Product unit price")
    installation_option_id: Optional[uuid.UUID] = Field(None, description="Installation option ID")
    installation_option_name: Optional[str] = Field(None, description="Installation option name")
    installation_price: Decimal = Field(default=Decimal('0'), ge=0, description="Installation price")
    membership_plan_id: Optional[uuid.UUID] = Field(None, description="Applied membership plan ID")
    discount_percentage: int = Field(default=0, ge=0, le=100, description="Discount percentage")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Item creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Item update timestamp")
    
    def calculate_item_total(self) -> Decimal:
        """Calculate total for this cart item including installation."""
        base_total = (self.unit_price + self.installation_price) * self.quantity
        discount_amount = base_total * Decimal(self.discount_percentage) / Decimal('100')
        return base_total - discount_amount
    
    def calculate_discount_amount(self) -> Decimal:
        """Calculate discount amount for this item."""
        base_total = (self.unit_price + self.installation_price) * self.quantity
        return base_total * Decimal(self.discount_percentage) / Decimal('100')


class ShoppingCart(BaseModel):
    """Shopping cart domain entity."""
    
    id: uuid.UUID = Field(..., description="Cart ID")
    business_id: uuid.UUID = Field(..., description="Business ID")
    session_id: Optional[str] = Field(None, description="Session ID for guest users")
    customer_id: Optional[str] = Field(None, description="Customer ID for logged-in users")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_phone: Optional[str] = Field(None, description="Customer phone")
    cart_status: str = Field(default="active", description="Cart status")
    currency_code: str = Field(default="USD", description="Currency code")
    items: List[CartItem] = Field(default_factory=list, description="Cart items")
    membership_type: Optional[str] = Field(None, description="Membership type")
    membership_verified: bool = Field(default=False, description="Membership verification status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Cart creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Cart update timestamp")
    expires_at: Optional[datetime] = Field(None, description="Cart expiration timestamp")
    
    def calculate_subtotal(self) -> Decimal:
        """Calculate cart subtotal."""
        return sum(item.calculate_item_total() for item in self.items)
    
    def calculate_total_savings(self) -> Decimal:
        """Calculate total savings from discounts."""
        return sum(item.calculate_discount_amount() for item in self.items)
    
    def calculate_tax_amount(self, tax_rate: Decimal = Decimal('0.08')) -> Decimal:
        """Calculate tax amount."""
        return self.calculate_subtotal() * tax_rate
    
    def calculate_total(self, tax_rate: Decimal = Decimal('0.08')) -> Decimal:
        """Calculate cart total including tax."""
        return self.calculate_subtotal() + self.calculate_tax_amount(tax_rate)
    
    def get_item_count(self) -> int:
        """Get total number of items in cart."""
        return len(self.items)
    
    def add_item(self, item: CartItem) -> None:
        """Add an item to the cart."""
        # Check if item already exists (same product and installation option)
        existing_item = None
        for cart_item in self.items:
            if (cart_item.product_id == item.product_id and 
                cart_item.installation_option_id == item.installation_option_id):
                existing_item = cart_item
                break
        
        if existing_item:
            # Update quantity of existing item
            existing_item.quantity += item.quantity
            existing_item.updated_at = datetime.now(timezone.utc)
        else:
            # Add new item
            self.items.append(item)
        
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_item(self, item_id: uuid.UUID) -> bool:
        """Remove an item from the cart."""
        for i, item in enumerate(self.items):
            if item.id == item_id:
                del self.items[i]
                self.updated_at = datetime.now(timezone.utc)
                return True
        return False
    
    def update_item_quantity(self, item_id: uuid.UUID, quantity: int) -> bool:
        """Update item quantity."""
        for item in self.items:
            if item.id == item_id:
                if quantity <= 0:
                    return self.remove_item(item_id)
                item.quantity = quantity
                item.updated_at = datetime.now(timezone.utc)
                self.updated_at = datetime.now(timezone.utc)
                return True
        return False
    
    def clear_items(self) -> None:
        """Clear all items from cart."""
        self.items.clear()
        self.updated_at = datetime.now(timezone.utc)
