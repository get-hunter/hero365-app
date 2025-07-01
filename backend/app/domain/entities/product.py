"""
Product Domain Entity

Represents a product in the inventory management system with comprehensive business rules,
pricing calculations, stock management, and supplier integration.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, Field, validator, computed_field

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError
from ..enums import (
    ProductType, ProductStatus, PricingModel, UnitOfMeasure, 
    InventoryMethod, CostingMethod, CurrencyCode, TaxType
)
from ..value_objects.address import Address

# Configure logging
logger = logging.getLogger(__name__)


class ProductPricingTier(BaseModel):
    """Pricing tier for volume-based pricing."""
    min_quantity: Decimal = Field(..., gt=0, description="Minimum quantity for this tier")
    max_quantity: Optional[Decimal] = Field(None, ge=0, description="Maximum quantity for this tier")
    unit_price: Decimal = Field(..., ge=0, description="Unit price for this tier")
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Discount percentage")
    
    @validator('max_quantity')
    def validate_max_quantity(cls, v, values):
        if v is not None and 'min_quantity' in values and v <= values['min_quantity']:
            raise ValueError('max_quantity must be greater than min_quantity')
        return v
    
    def calculate_tier_price(self, quantity: Decimal) -> Decimal:
        """Calculate price for given quantity in this tier."""
        if self.discount_percentage:
            return self.unit_price * (Decimal('100') - self.discount_percentage) / Decimal('100')
        return self.unit_price
    
    def applies_to_quantity(self, quantity: Decimal) -> bool:
        """Check if this tier applies to the given quantity."""
        if quantity < self.min_quantity:
            return False
        if self.max_quantity is not None and quantity > self.max_quantity:
            return False
        return True


class ProductLocation(BaseModel):
    """Product inventory at a specific location."""
    location_id: uuid.UUID = Field(..., description="Location identifier")
    location_name: str = Field(..., min_length=1, max_length=200, description="Location name")
    quantity_on_hand: Decimal = Field(default=Decimal('0'), ge=0, description="Quantity on hand at location")
    quantity_reserved: Decimal = Field(default=Decimal('0'), ge=0, description="Reserved quantity at location")
    bin_location: Optional[str] = Field(None, max_length=100, description="Bin/shelf location")
    last_counted_date: Optional[datetime] = Field(None, description="Last physical count date")
    
    @computed_field
    @property
    def quantity_available(self) -> Decimal:
        """Calculate available quantity at location."""
        return self.quantity_on_hand - self.quantity_reserved
    
    def can_fulfill_quantity(self, requested_quantity: Decimal) -> bool:
        """Check if location can fulfill requested quantity."""
        return self.quantity_available >= requested_quantity


class ProductSupplier(BaseModel):
    """Supplier information for a product."""
    supplier_id: uuid.UUID = Field(..., description="Supplier identifier")
    supplier_name: str = Field(..., min_length=1, max_length=200, description="Supplier name")
    supplier_sku: Optional[str] = Field(None, max_length=100, description="Supplier's SKU for this product")
    cost_price: Decimal = Field(..., ge=0, description="Cost price from supplier")
    lead_time_days: Optional[int] = Field(None, ge=0, description="Lead time in days")
    minimum_order_quantity: Optional[Decimal] = Field(None, gt=0, description="Minimum order quantity")
    is_preferred: bool = Field(default=False, description="Is this the preferred supplier")
    last_order_date: Optional[datetime] = Field(None, description="Last order date")
    
    def calculate_landed_cost(self, shipping_cost: Decimal = Decimal('0'), 
                             duty_cost: Decimal = Decimal('0')) -> Decimal:
        """Calculate total landed cost including shipping and duties."""
        return self.cost_price + shipping_cost + duty_cost


class Product(BaseModel):
    """
    Product domain entity with comprehensive inventory management.
    
    Represents a product in the business catalog with full inventory tracking,
    pricing, supplier management, and business rules.
    """
    
    # Basic product information
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Product unique identifier")
    business_id: uuid.UUID = Field(..., description="Business identifier")
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    name: str = Field(..., min_length=1, max_length=300, description="Product name")
    description: Optional[str] = Field(None, max_length=2000, description="Product description")
    
    # Product classification
    product_type: ProductType = Field(default=ProductType.PRODUCT, description="Product type")
    status: ProductStatus = Field(default=ProductStatus.ACTIVE, description="Product status")
    category_id: Optional[uuid.UUID] = Field(None, description="Product category identifier")
    category_name: Optional[str] = Field(None, max_length=200, description="Category name")
    
    # Inventory tracking configuration
    track_inventory: bool = Field(default=True, description="Whether to track inventory for this product")
    inventory_method: InventoryMethod = Field(default=InventoryMethod.PERPETUAL, description="Inventory tracking method")
    costing_method: CostingMethod = Field(default=CostingMethod.WEIGHTED_AVERAGE, description="Cost calculation method")
    
    # Stock quantities
    quantity_on_hand: Decimal = Field(default=Decimal('0'), ge=0, description="Total quantity on hand")
    quantity_reserved: Decimal = Field(default=Decimal('0'), ge=0, description="Reserved quantity")
    quantity_on_order: Decimal = Field(default=Decimal('0'), ge=0, description="Quantity on purchase orders")
    quantity_allocated: Decimal = Field(default=Decimal('0'), ge=0, description="Allocated to orders")
    
    # Reorder management
    reorder_point: Optional[Decimal] = Field(None, ge=0, description="Reorder point quantity")
    reorder_quantity: Optional[Decimal] = Field(None, gt=0, description="Quantity to reorder")
    minimum_quantity: Optional[Decimal] = Field(None, ge=0, description="Minimum stock level")
    maximum_quantity: Optional[Decimal] = Field(None, gt=0, description="Maximum stock level")
    safety_stock: Optional[Decimal] = Field(None, ge=0, description="Safety stock quantity")
    
    # Cost tracking
    unit_cost: Decimal = Field(default=Decimal('0'), ge=0, description="Current unit cost")
    average_cost: Decimal = Field(default=Decimal('0'), ge=0, description="Weighted average cost")
    last_cost: Decimal = Field(default=Decimal('0'), ge=0, description="Last purchase cost")
    standard_cost: Optional[Decimal] = Field(None, ge=0, description="Standard cost for accounting")
    
    # Pricing
    pricing_model: PricingModel = Field(default=PricingModel.FIXED, description="Pricing model")
    unit_price: Decimal = Field(default=Decimal('0'), ge=0, description="Base unit price")
    currency: CurrencyCode = Field(default=CurrencyCode.USD, description="Currency code")
    markup_percentage: Optional[Decimal] = Field(None, ge=0, description="Markup percentage over cost")
    margin_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Profit margin percentage")
    
    # Pricing tiers for volume discounts
    pricing_tiers: List[ProductPricingTier] = Field(default_factory=list, description="Volume-based pricing tiers")
    
    # Physical attributes
    unit_of_measure: UnitOfMeasure = Field(default=UnitOfMeasure.EACH, description="Unit of measure")
    weight: Optional[Decimal] = Field(None, ge=0, description="Product weight")
    weight_unit: Optional[str] = Field(None, max_length=20, description="Weight unit (kg, lb, etc.)")
    dimensions: Optional[Dict[str, Decimal]] = Field(None, description="Product dimensions (length, width, height)")
    
    # Tax settings
    tax_type: TaxType = Field(default=TaxType.NONE, description="Tax type")
    tax_rate: Decimal = Field(default=Decimal('0'), ge=0, le=100, description="Tax rate percentage")
    tax_code: Optional[str] = Field(None, max_length=50, description="Tax code for accounting")
    is_taxable: bool = Field(default=True, description="Whether product is taxable")
    
    # Supplier information
    suppliers: List[ProductSupplier] = Field(default_factory=list, description="Product suppliers")
    primary_supplier_id: Optional[uuid.UUID] = Field(None, description="Primary supplier identifier")
    
    # Location-based inventory
    locations: List[ProductLocation] = Field(default_factory=list, description="Inventory by location")
    
    # Images and attachments
    image_urls: List[str] = Field(default_factory=list, description="Product image URLs")
    attachment_urls: List[str] = Field(default_factory=list, description="Product attachment URLs")
    
    # Metadata
    barcode: Optional[str] = Field(None, max_length=100, description="Product barcode")
    manufacturer: Optional[str] = Field(None, max_length=200, description="Manufacturer name")
    manufacturer_sku: Optional[str] = Field(None, max_length=100, description="Manufacturer SKU")
    brand: Optional[str] = Field(None, max_length=100, description="Brand name")
    
    # Analytics and tracking
    times_sold: int = Field(default=0, ge=0, description="Number of times sold")
    last_sale_date: Optional[datetime] = Field(None, description="Last sale date")
    last_purchase_date: Optional[datetime] = Field(None, description="Last purchase date")
    created_by: str = Field(..., description="User who created the product")
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation date")
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last modification date")
    
    # Business rules validation
    @validator('sku')
    def validate_sku(cls, v):
        if not v or v.strip() == "":
            raise ValueError('SKU cannot be empty')
        # SKU should be alphanumeric with hyphens and underscores allowed
        import re
        if not re.match(r'^[A-Za-z0-9_-]+$', v.strip()):
            raise ValueError('SKU can only contain letters, numbers, hyphens, and underscores')
        return v.strip().upper()
    
    @validator('quantity_reserved')
    def validate_reserved_quantity(cls, v, values):
        if 'quantity_on_hand' in values and v > values['quantity_on_hand']:
            raise ValueError('Reserved quantity cannot exceed quantity on hand')
        return v
    
    @validator('reorder_quantity')
    def validate_reorder_quantity(cls, v, values):
        if v is not None and 'minimum_quantity' in values and values['minimum_quantity'] is not None:
            if v < values['minimum_quantity']:
                raise ValueError('Reorder quantity should be at least the minimum quantity')
        return v
    
    @validator('pricing_tiers')
    def validate_pricing_tiers(cls, v):
        if not v:
            return v
        
        # Sort tiers by min_quantity
        v.sort(key=lambda tier: tier.min_quantity)
        
        # Validate no overlapping tiers
        for i in range(len(v) - 1):
            current_tier = v[i]
            next_tier = v[i + 1]
            
            if current_tier.max_quantity is not None:
                if current_tier.max_quantity >= next_tier.min_quantity:
                    raise ValueError('Pricing tiers cannot overlap')
            
        return v
    
    class Config:
        validate_assignment = True
        use_enum_values = True
        json_encoders = {
            uuid.UUID: str,
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
    
    # Computed fields
    @computed_field
    @property
    def quantity_available(self) -> Decimal:
        """Calculate quantity available for sale."""
        return self.quantity_on_hand - self.quantity_reserved - self.quantity_allocated
    
    @computed_field
    @property
    def quantity_committed(self) -> Decimal:
        """Calculate total committed quantity (reserved + allocated)."""
        return self.quantity_reserved + self.quantity_allocated
    
    @computed_field
    @property
    def total_quantity(self) -> Decimal:
        """Calculate total quantity including on order."""
        return self.quantity_on_hand + self.quantity_on_order
    
    @computed_field
    @property
    def inventory_value(self) -> Decimal:
        """Calculate total inventory value at current cost."""
        return self.quantity_on_hand * self.unit_cost
    
    # Business logic methods
    def calculate_selling_price(self, quantity: Decimal = Decimal('1'), 
                               customer_id: Optional[uuid.UUID] = None) -> Decimal:
        """
        Calculate selling price based on quantity and customer.
        
        Args:
            quantity: Quantity being purchased
            customer_id: Customer identifier for custom pricing
            
        Returns:
            Calculated unit price
        """
        if self.pricing_model == PricingModel.FIXED:
            return self._calculate_tiered_price(quantity)
        elif self.pricing_model == PricingModel.HOURLY:
            return self.unit_price  # Base hourly rate
        elif self.pricing_model == PricingModel.CUSTOM:
            # Custom pricing logic can be implemented here
            return self.unit_price
        else:
            return self._calculate_tiered_price(quantity)
    
    def _calculate_tiered_price(self, quantity: Decimal) -> Decimal:
        """Calculate price based on quantity tiers."""
        if not self.pricing_tiers:
            return self.unit_price
        
        for tier in self.pricing_tiers:
            if tier.applies_to_quantity(quantity):
                return tier.calculate_tier_price(quantity)
        
        # If no tier applies, use base price
        return self.unit_price
    
    def calculate_markup_price(self) -> Decimal:
        """Calculate price based on markup percentage."""
        if self.markup_percentage is None:
            return self.unit_price
        
        markup_multiplier = Decimal('1') + (self.markup_percentage / Decimal('100'))
        return self.unit_cost * markup_multiplier
    
    def calculate_margin_percentage(self) -> Decimal:
        """Calculate current profit margin percentage."""
        if self.unit_price == 0 or self.unit_cost == 0:
            return Decimal('0')
        
        margin = (self.unit_price - self.unit_cost) / self.unit_price * Decimal('100')
        return margin.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def is_low_stock(self) -> bool:
        """Check if product is below reorder point."""
        if self.reorder_point is None or not self.track_inventory:
            return False
        return self.quantity_available <= self.reorder_point
    
    def is_out_of_stock(self) -> bool:
        """Check if product is out of stock."""
        if not self.track_inventory:
            return False
        return self.quantity_available <= 0
    
    def needs_reorder(self) -> bool:
        """Check if product needs to be reordered."""
        return self.is_low_stock() and self.quantity_on_order == 0
    
    def suggest_reorder_quantity(self) -> Optional[Decimal]:
        """Suggest quantity to reorder based on business rules."""
        if not self.needs_reorder():
            return None
        
        if self.reorder_quantity:
            return self.reorder_quantity
        
        # If no reorder quantity set, suggest bringing to maximum or double the reorder point
        if self.maximum_quantity:
            return self.maximum_quantity - self.quantity_available
        elif self.reorder_point:
            return self.reorder_point * 2
        
        return None
    
    def can_fulfill_quantity(self, requested_quantity: Decimal, 
                           location_id: Optional[uuid.UUID] = None) -> bool:
        """
        Check if product can fulfill requested quantity.
        
        Args:
            requested_quantity: Quantity requested
            location_id: Specific location to check (optional)
            
        Returns:
            True if quantity can be fulfilled
        """
        if not self.track_inventory:
            return True
        
        if location_id:
            for location in self.locations:
                if location.location_id == location_id:
                    return location.can_fulfill_quantity(requested_quantity)
            return False
        
        return self.quantity_available >= requested_quantity
    
    def get_preferred_supplier(self) -> Optional[ProductSupplier]:
        """Get the preferred supplier for this product."""
        if self.primary_supplier_id:
            for supplier in self.suppliers:
                if supplier.supplier_id == self.primary_supplier_id:
                    return supplier
        
        # If no primary supplier set, return the first preferred supplier
        for supplier in self.suppliers:
            if supplier.is_preferred:
                return supplier
        
        # If no preferred supplier, return the first supplier
        return self.suppliers[0] if self.suppliers else None
    
    def update_average_cost(self, new_cost: Decimal, quantity: Decimal):
        """
        Update average cost using weighted average method.
        
        Args:
            new_cost: New unit cost
            quantity: Quantity purchased at new cost
        """
        if self.costing_method != CostingMethod.WEIGHTED_AVERAGE:
            return
        
        current_value = self.quantity_on_hand * self.average_cost
        new_value = quantity * new_cost
        total_quantity = self.quantity_on_hand + quantity
        
        if total_quantity > 0:
            self.average_cost = (current_value + new_value) / total_quantity
            self.average_cost = self.average_cost.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    
    def reserve_quantity(self, quantity: Decimal) -> bool:
        """
        Reserve quantity for an order.
        
        Args:
            quantity: Quantity to reserve
            
        Returns:
            True if successfully reserved
        """
        if not self.can_fulfill_quantity(quantity):
            return False
        
        self.quantity_reserved += quantity
        self.last_modified = datetime.now(timezone.utc)
        return True
    
    def release_reservation(self, quantity: Decimal):
        """
        Release reserved quantity.
        
        Args:
            quantity: Quantity to release
        """
        self.quantity_reserved = max(Decimal('0'), self.quantity_reserved - quantity)
        self.last_modified = datetime.now(timezone.utc)
    
    def adjust_quantity(self, quantity_change: Decimal, reason: str = "Manual adjustment"):
        """
        Adjust quantity on hand.
        
        Args:
            quantity_change: Change in quantity (positive or negative)
            reason: Reason for adjustment
        """
        new_quantity = self.quantity_on_hand + quantity_change
        
        if new_quantity < 0:
            raise BusinessRuleViolationError("Adjustment would result in negative inventory")
        
        self.quantity_on_hand = new_quantity
        self.last_modified = datetime.now(timezone.utc)
        
        # Log the adjustment (this would typically be handled by a stock movement service)
        logger.info(f"Product {self.sku} quantity adjusted by {quantity_change}. Reason: {reason}")
    
    def is_active(self) -> bool:
        """Check if product is active and available for sale."""
        return self.status == ProductStatus.ACTIVE
    
    def can_be_sold(self) -> bool:
        """Check if product can be sold."""
        if not self.is_active():
            return False
        
        if self.track_inventory and self.is_out_of_stock():
            return False
        
        return True
    
    def get_status_display(self) -> str:
        """Get human-readable status display."""
        if self.status == ProductStatus.ACTIVE and self.track_inventory:
            if self.is_out_of_stock():
                return "Out of Stock"
            elif self.is_low_stock():
                return "Low Stock"
        
        return self.status.get_display()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert product to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "product_type": self.product_type.value,
            "product_type_display": self.product_type.get_display(),
            "status": self.status.value,
            "status_display": self.get_status_display(),
            "category_id": str(self.category_id) if self.category_id else None,
            "category_name": self.category_name,
            "track_inventory": self.track_inventory,
            "inventory_method": self.inventory_method.value,
            "costing_method": self.costing_method.value,
            "quantity_on_hand": float(self.quantity_on_hand),
            "quantity_reserved": float(self.quantity_reserved),
            "quantity_available": float(self.quantity_available),
            "quantity_on_order": float(self.quantity_on_order),
            "reorder_point": float(self.reorder_point) if self.reorder_point else None,
            "reorder_quantity": float(self.reorder_quantity) if self.reorder_quantity else None,
            "unit_cost": float(self.unit_cost),
            "average_cost": float(self.average_cost),
            "unit_price": float(self.unit_price),
            "currency": self.currency.value,
            "markup_percentage": float(self.markup_percentage) if self.markup_percentage else None,
            "margin_percentage": float(self.calculate_margin_percentage()),
            "pricing_model": self.pricing_model.value,
            "unit_of_measure": self.unit_of_measure.value,
            "is_low_stock": self.is_low_stock(),
            "is_out_of_stock": self.is_out_of_stock(),
            "needs_reorder": self.needs_reorder(),
            "inventory_value": float(self.inventory_value),
            "image_urls": self.image_urls,
            "barcode": self.barcode,
            "manufacturer": self.manufacturer,
            "brand": self.brand,
            "times_sold": self.times_sold,
            "last_sale_date": self.last_sale_date.isoformat() if self.last_sale_date else None,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat(),
            "last_modified": self.last_modified.isoformat()
        }
    
    def __str__(self) -> str:
        return f"Product({self.sku}: {self.name})"
    
    def __repr__(self) -> str:
        return f"Product(id={self.id}, sku='{self.sku}', name='{self.name}', status='{self.status}')" 