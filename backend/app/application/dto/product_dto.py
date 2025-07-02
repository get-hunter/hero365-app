"""
Product Data Transfer Objects

DTOs for product and inventory management operations following clean architecture principles.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from dataclasses import dataclass

from app.domain.enums import ProductType, ProductStatus, PricingModel, UnitOfMeasure, CostingMethod
from app.domain.value_objects.address import Address


@dataclass
class ProductPricingTierDTO:
    """DTO for product pricing tiers."""
    min_quantity: Decimal
    max_quantity: Optional[Decimal] = None
    unit_price: Decimal = Decimal('0')
    discount_percentage: Optional[Decimal] = None

    @classmethod
    def from_entity(cls, tier) -> 'ProductPricingTierDTO':
        """Create DTO from domain entity."""
        return cls(
            min_quantity=tier.min_quantity,
            max_quantity=tier.max_quantity,
            unit_price=tier.unit_price,
            discount_percentage=tier.discount_percentage
        )


@dataclass
class ProductLocationDTO:
    """DTO for product location inventory."""
    location_id: uuid.UUID
    location_name: str
    quantity_on_hand: Decimal = Decimal('0')
    quantity_reserved: Decimal = Decimal('0')
    quantity_available: Decimal = Decimal('0')
    bin_location: Optional[str] = None
    last_counted_date: Optional[datetime] = None

    @classmethod
    def from_entity(cls, location) -> 'ProductLocationDTO':
        """Create DTO from domain entity."""
        return cls(
            location_id=location.location_id,
            location_name=location.location_name,
            quantity_on_hand=location.quantity_on_hand,
            quantity_reserved=location.quantity_reserved,
            quantity_available=location.quantity_available,
            bin_location=location.bin_location,
            last_counted_date=location.last_counted_date
        )


@dataclass
class ProductSupplierDTO:
    """DTO for product supplier information."""
    supplier_id: uuid.UUID
    supplier_name: str
    supplier_sku: Optional[str] = None
    cost_price: Decimal = Decimal('0')
    lead_time_days: Optional[int] = None
    minimum_order_quantity: Optional[Decimal] = None
    is_preferred: bool = False
    last_order_date: Optional[datetime] = None

    @classmethod
    def from_entity(cls, supplier) -> 'ProductSupplierDTO':
        """Create DTO from domain entity."""
        return cls(
            supplier_id=supplier.supplier_id,
            supplier_name=supplier.supplier_name,
            supplier_sku=supplier.supplier_sku,
            cost_price=supplier.cost_price,
            lead_time_days=supplier.lead_time_days,
            minimum_order_quantity=supplier.minimum_order_quantity,
            is_preferred=supplier.is_preferred,
            last_order_date=supplier.last_order_date
        )


# Create Product DTOs
@dataclass
class CreateProductDTO:
    """DTO for creating a new product."""
    business_id: uuid.UUID
    sku: str
    name: str
    description: Optional[str] = None
    product_type: ProductType = ProductType.PRODUCT
    status: ProductStatus = ProductStatus.ACTIVE
    category_id: Optional[uuid.UUID] = None
    
    # Pricing
    pricing_model: PricingModel = PricingModel.FIXED
    unit_price: Decimal = Decimal('0')
    cost_price: Decimal = Decimal('0')
    markup_percentage: Optional[Decimal] = None
    
    # Physical attributes
    unit_of_measure: UnitOfMeasure = UnitOfMeasure.EACH
    weight: Optional[Decimal] = None
    dimensions: Optional[Dict[str, Decimal]] = None
    
    # Inventory
    track_inventory: bool = True
    initial_quantity: Decimal = Decimal('0')
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    costing_method: CostingMethod = CostingMethod.WEIGHTED_AVERAGE
    
    # Tax settings
    tax_rate: Optional[Decimal] = None
    is_taxable: bool = True
    
    # Supplier information
    primary_supplier_id: Optional[uuid.UUID] = None
    
    # Media and metadata
    barcode: Optional[str] = None
    manufacturer: Optional[str] = None
    brand: Optional[str] = None


@dataclass
class UpdateProductDTO:
    """DTO for updating an existing product."""
    name: Optional[str] = None
    description: Optional[str] = None
    long_description: Optional[str] = None
    status: Optional[ProductStatus] = None
    category_id: Optional[uuid.UUID] = None
    
    # Pricing
    unit_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    minimum_price: Optional[Decimal] = None
    markup_percentage: Optional[Decimal] = None
    
    # Physical attributes
    weight: Optional[Decimal] = None
    weight_unit: Optional[str] = None
    dimensions: Optional[Dict[str, Decimal]] = None
    
    # Inventory settings
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    minimum_quantity: Optional[Decimal] = None
    maximum_quantity: Optional[Decimal] = None
    
    # Tax settings
    tax_rate: Optional[Decimal] = None
    tax_code: Optional[str] = None
    is_taxable: Optional[bool] = None
    
    # Supplier information
    primary_supplier_id: Optional[uuid.UUID] = None
    supplier_sku: Optional[str] = None
    lead_time_days: Optional[int] = None
    
    # Media and metadata
    image_urls: Optional[List[str]] = None
    barcode: Optional[str] = None
    manufacturer: Optional[str] = None
    manufacturer_sku: Optional[str] = None
    brand: Optional[str] = None
    
    # Pricing tiers
    pricing_tiers: Optional[List[ProductPricingTierDTO]] = None
    
    # Notes
    notes: Optional[str] = None


@dataclass
class ProductDTO:
    """DTO for product entity with full information."""
    id: uuid.UUID
    business_id: uuid.UUID
    sku: str
    name: str
    description: Optional[str] = None
    product_type: ProductType = ProductType.PRODUCT
    status: ProductStatus = ProductStatus.ACTIVE
    category_id: Optional[uuid.UUID] = None
    
    # Pricing
    pricing_model: PricingModel = PricingModel.FIXED
    unit_price: Decimal = Decimal('0')
    cost_price: Decimal = Decimal('0')
    markup_percentage: Optional[Decimal] = None
    
    # Physical attributes
    unit_of_measure: UnitOfMeasure = UnitOfMeasure.EACH
    weight: Optional[Decimal] = None
    dimensions: Optional[Dict[str, Decimal]] = None
    
    # Inventory
    track_inventory: bool = True
    quantity_on_hand: Decimal = Decimal('0')
    quantity_reserved: Decimal = Decimal('0')
    quantity_available: Decimal = Decimal('0')
    
    # Reorder management
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    
    # Cost tracking
    costing_method: CostingMethod = CostingMethod.WEIGHTED_AVERAGE
    unit_cost: Decimal = Decimal('0')
    average_cost: Decimal = Decimal('0')
    
    # Calculated fields
    inventory_value: Decimal = Decimal('0')
    is_low_stock: bool = False
    is_out_of_stock: bool = False
    needs_reorder: bool = False
    
    # Tax settings
    tax_rate: Optional[Decimal] = None
    is_taxable: bool = True
    
    # Supplier information
    primary_supplier_id: Optional[uuid.UUID] = None
    
    # Media and metadata
    barcode: Optional[str] = None
    manufacturer: Optional[str] = None
    brand: Optional[str] = None
    
    # Analytics
    times_sold: int = 0
    last_sale_date: Optional[datetime] = None
    
    # Audit fields
    created_by: str = ""
    created_date: datetime = datetime.utcnow()
    last_modified: datetime = datetime.utcnow()

    @classmethod
    def from_entity(cls, product) -> 'ProductDTO':
        """Create DTO from domain entity."""
        return cls(
            id=product.id,
            business_id=product.business_id,
            sku=product.sku,
            name=product.name,
            description=product.description,
            product_type=product.product_type,
            status=product.status,
            category_id=getattr(product, 'category_id', None),
            pricing_model=product.pricing_model,
            unit_price=product.unit_price,
            cost_price=getattr(product, 'cost_price', product.unit_cost),
            markup_percentage=product.markup_percentage,
            unit_of_measure=product.unit_of_measure,
            weight=product.weight,
            dimensions=product.dimensions,
            track_inventory=product.track_inventory,
            quantity_on_hand=product.quantity_on_hand,
            quantity_reserved=product.quantity_reserved,
            quantity_available=product.quantity_available,
            reorder_point=getattr(product, 'reorder_point', None),
            reorder_quantity=getattr(product, 'reorder_quantity', None),
            costing_method=product.costing_method,
            unit_cost=product.unit_cost,
            average_cost=product.average_cost,
            inventory_value=product.inventory_value,
            is_low_stock=product.is_low_stock(),
            is_out_of_stock=product.is_out_of_stock(),
            needs_reorder=product.needs_reorder(),
            tax_rate=getattr(product, 'tax_rate', None),
            is_taxable=getattr(product, 'is_taxable', True),
            primary_supplier_id=getattr(product, 'primary_supplier_id', None),
            barcode=product.barcode,
            manufacturer=product.manufacturer,
            brand=product.brand,
            times_sold=product.times_sold,
            last_sale_date=product.last_sale_date,
            created_by=product.created_by,
            created_date=product.created_date,
            last_modified=product.last_modified
        )


@dataclass 
class ProductSummaryDTO:
    """DTO for product summary in lists."""
    id: uuid.UUID
    sku: str
    name: str
    description: Optional[str] = None
    product_type: ProductType = ProductType.PRODUCT
    status: ProductStatus = ProductStatus.ACTIVE
    unit_price: Decimal = Decimal('0')
    quantity_available: Decimal = Decimal('0')
    is_low_stock: bool = False
    is_out_of_stock: bool = False

    @classmethod
    def from_entity(cls, product) -> 'ProductSummaryDTO':
        """Create summary DTO from domain entity."""
        return cls(
            id=product.id,
            sku=product.sku,
            name=product.name,
            description=product.description,
            product_type=product.product_type,
            status=product.status,
            unit_price=product.unit_price,
            quantity_available=product.quantity_available,
            is_low_stock=product.is_low_stock(),
            is_out_of_stock=product.is_out_of_stock()
        )


@dataclass
class ProductSearchCriteria:
    """DTO for product search criteria."""
    query: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    product_type: Optional[ProductType] = None
    status: Optional[ProductStatus] = None
    low_stock_only: bool = False
    out_of_stock_only: bool = False
    sort_by: Optional[str] = None
    sort_order: str = "asc"


@dataclass
class ProductListDTO:
    """DTO for paginated product lists."""
    products: List[ProductSummaryDTO]
    total_count: int
    has_more: bool
    offset: int
    limit: int


# Inventory Management DTOs
@dataclass
class StockAdjustmentDTO:
    """DTO for stock adjustments."""
    product_id: uuid.UUID
    quantity_change: Decimal
    adjustment_reason: str
    reference_number: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class StockMovementDTO:
    """DTO for stock movements."""
    id: uuid.UUID
    product_id: uuid.UUID
    product_sku: str
    product_name: str
    movement_type: str
    quantity: Decimal
    movement_date: datetime
    created_by: str
    unit_cost: Optional[Decimal] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    location_id: Optional[uuid.UUID] = None
    location_name: Optional[str] = None
    
    # Calculated fields
    movement_value: Optional[Decimal] = None
    running_balance: Optional[Decimal] = None

    @classmethod
    def from_entity(cls, movement) -> 'StockMovementDTO':
        """Create DTO from domain entity."""
        return cls(
            id=movement.id,
            product_id=movement.product_id,
            product_sku=movement.product_sku,
            product_name=movement.product_name,
            movement_type=movement.movement_type.value,
            quantity=movement.quantity,
            unit_cost=movement.unit_cost,
            movement_date=movement.movement_date,
            reference_number=movement.reference_number,
            notes=movement.notes,
            location_id=movement.location_id,
            location_name=getattr(movement, 'location_name', None),
            created_by=movement.created_by,
            movement_value=movement.calculate_movement_value(),
            running_balance=getattr(movement, 'running_balance', None)
        )


@dataclass
class InventoryReportDTO:
    """DTO for inventory reports."""
    report_date: datetime
    total_products: int
    total_inventory_value: Decimal
    low_stock_count: int
    out_of_stock_count: int
    reorder_needed_count: int
    products_by_category: Dict[str, int]
    top_selling_products: List[ProductSummaryDTO]
    slow_moving_products: List[ProductSummaryDTO]


@dataclass
class ProductAvailabilityDTO:
    """DTO for product availability checking."""
    product_id: uuid.UUID
    sku: str
    name: str
    requested_quantity: Decimal
    available_quantity: Decimal
    is_available: bool
    shortage: Decimal = Decimal('0')
    estimated_availability_date: Optional[datetime] = None
    alternative_products: Optional[List[ProductSummaryDTO]] = None


# Mobile-optimized DTOs
@dataclass
class MobileProductDTO:
    """DTO optimized for mobile app consumption."""
    id: uuid.UUID
    sku: str
    name: str
    description: Optional[str] = None
    unit_price: Decimal = Decimal('0')
    unit_of_measure: UnitOfMeasure = UnitOfMeasure.EACH
    available_quantity: Decimal = Decimal('0')
    is_available: bool = True
    category_name: Optional[str] = None
    image_url: Optional[str] = None
    barcode: Optional[str] = None

    @classmethod
    def from_entity(cls, product) -> 'MobileProductDTO':
        """Create mobile DTO from domain entity."""
        return cls(
            id=product.id,
            sku=product.sku,
            name=product.name,
            description=product.description,
            unit_price=product.unit_price,
            unit_of_measure=product.unit_of_measure,
            available_quantity=product.quantity_available,
            is_available=not product.is_out_of_stock(),
            category_name=getattr(product, 'category_name', None),
            image_url=getattr(product, 'image_urls', [None])[0] if getattr(product, 'image_urls', []) else None,
            barcode=product.barcode
        )


@dataclass
class MobileProductCatalogDTO:
    """DTO for mobile product catalog."""
    products: List[MobileProductDTO]
    categories: List[Dict[str, Any]]
    has_more: bool
    total_count: int 