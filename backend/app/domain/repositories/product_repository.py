"""
Product Repository Interface

Repository interface for product management with comprehensive CRUD operations,
inventory tracking, and search capabilities.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime

from ..entities.product import Product
from ..enums import ProductType, ProductStatus, PricingModel


class ProductRepository(ABC):
    """Repository interface for product management operations."""
    
    # Basic CRUD operations
    @abstractmethod
    async def create(self, product: Product) -> Product:
        """Create a new product."""
        pass
    
    @abstractmethod
    async def get_by_id(self, business_id: uuid.UUID, product_id: uuid.UUID) -> Optional[Product]:
        """Get product by ID."""
        pass
    
    @abstractmethod
    async def get_by_sku(self, business_id: uuid.UUID, sku: str) -> Optional[Product]:
        """Get product by SKU."""
        pass
    
    @abstractmethod
    async def update(self, product: Product) -> Product:
        """Update an existing product."""
        pass
    
    @abstractmethod
    async def delete(self, business_id: uuid.UUID, product_id: uuid.UUID) -> bool:
        """Delete a product."""
        pass
    
    # List and search operations
    @abstractmethod
    async def list_by_business(
        self,
        business_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
        status: Optional[ProductStatus] = None,
        product_type: Optional[ProductType] = None,
        category_id: Optional[uuid.UUID] = None
    ) -> List[Product]:
        """List products for a business with optional filtering."""
        pass
    
    @abstractmethod
    async def search_products(
        self,
        business_id: uuid.UUID,
        query: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Product]:
        """Search products by name, SKU, or description."""
        pass
    
    @abstractmethod
    async def get_by_category(
        self,
        business_id: uuid.UUID,
        category_id: uuid.UUID,
        include_subcategories: bool = False,
        status: Optional[ProductStatus] = None
    ) -> List[Product]:
        """Get products by category."""
        pass
    
    # Inventory management operations
    @abstractmethod
    async def get_low_stock_products(
        self,
        business_id: uuid.UUID,
        location_id: Optional[uuid.UUID] = None
    ) -> List[Product]:
        """Get products that are below their reorder point."""
        pass
    
    @abstractmethod
    async def get_out_of_stock_products(
        self,
        business_id: uuid.UUID,
        location_id: Optional[uuid.UUID] = None
    ) -> List[Product]:
        """Get products that are out of stock."""
        pass
    
    @abstractmethod
    async def get_products_needing_reorder(
        self,
        business_id: uuid.UUID,
        location_id: Optional[uuid.UUID] = None
    ) -> List[Product]:
        """Get products that need to be reordered."""
        pass
    
    @abstractmethod
    async def update_quantity(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity_change: Decimal,
        location_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Update product quantity."""
        pass
    
    @abstractmethod
    async def reserve_quantity(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: Decimal,
        location_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Reserve product quantity for an order."""
        pass
    
    @abstractmethod
    async def release_reservation(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: Decimal,
        location_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Release reserved product quantity."""
        pass
    
    # Cost and pricing operations
    @abstractmethod
    async def update_cost(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        new_cost: Decimal,
        quantity: Optional[Decimal] = None
    ) -> bool:
        """Update product cost using appropriate costing method."""
        pass
    
    @abstractmethod
    async def get_product_cost_history(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get product cost history."""
        pass
    
    @abstractmethod
    async def calculate_inventory_value(
        self,
        business_id: uuid.UUID,
        category_id: Optional[uuid.UUID] = None,
        location_id: Optional[uuid.UUID] = None
    ) -> Decimal:
        """Calculate total inventory value."""
        pass
    
    # Supplier and supplier integration
    @abstractmethod
    async def get_products_by_supplier(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        status: Optional[ProductStatus] = None
    ) -> List[Product]:
        """Get products from a specific supplier."""
        pass
    
    @abstractmethod
    async def update_supplier_info(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        supplier_id: uuid.UUID,
        supplier_data: Dict[str, Any]
    ) -> bool:
        """Update supplier information for a product."""
        pass
    
    # Location management
    @abstractmethod
    async def get_products_at_location(
        self,
        business_id: uuid.UUID,
        location_id: uuid.UUID,
        status: Optional[ProductStatus] = None
    ) -> List[Product]:
        """Get products available at a specific location."""
        pass
    
    @abstractmethod
    async def transfer_between_locations(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        from_location_id: uuid.UUID,
        to_location_id: uuid.UUID,
        quantity: Decimal
    ) -> bool:
        """Transfer product quantity between locations."""
        pass
    
    # Analytics and reporting
    @abstractmethod
    async def get_product_analytics(
        self,
        business_id: uuid.UUID,
        product_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get product analytics and performance metrics."""
        pass
    
    @abstractmethod
    async def get_top_selling_products(
        self,
        business_id: uuid.UUID,
        limit: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top selling products."""
        pass
    
    @abstractmethod
    async def get_slow_moving_products(
        self,
        business_id: uuid.UUID,
        days_threshold: int = 90,
        limit: int = 20
    ) -> List[Product]:
        """Get products with no sales in specified period."""
        pass
    
    # Bulk operations
    @abstractmethod
    async def bulk_update_status(
        self,
        business_id: uuid.UUID,
        product_ids: List[uuid.UUID],
        status: ProductStatus
    ) -> int:
        """Bulk update product status."""
        pass
    
    @abstractmethod
    async def bulk_update_pricing(
        self,
        business_id: uuid.UUID,
        updates: List[Dict[str, Any]]
    ) -> int:
        """Bulk update product pricing."""
        pass
    
    @abstractmethod
    async def bulk_adjust_inventory(
        self,
        business_id: uuid.UUID,
        adjustments: List[Dict[str, Any]]
    ) -> int:
        """Bulk adjust inventory quantities."""
        pass
    
    # Mobile app optimization
    @abstractmethod
    async def get_products_for_mobile(
        self,
        business_id: uuid.UUID,
        category_id: Optional[uuid.UUID] = None,
        search_query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get products optimized for mobile app consumption."""
        pass
    
    @abstractmethod
    async def get_product_availability_for_estimate(
        self,
        business_id: uuid.UUID,
        product_ids: List[uuid.UUID],
        quantities: List[Decimal],
        location_id: Optional[uuid.UUID] = None
    ) -> Dict[uuid.UUID, Dict[str, Any]]:
        """Check product availability for estimate/invoice creation."""
        pass
    
    # Advanced search and filtering
    @abstractmethod
    async def advanced_search(
        self,
        business_id: uuid.UUID,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Advanced product search with multiple filters."""
        pass
    
    @abstractmethod
    async def get_filter_options(
        self,
        business_id: uuid.UUID
    ) -> Dict[str, List[Any]]:
        """Get available filter options for product search."""
        pass
    
    # Count operations
    @abstractmethod
    async def count_products(
        self,
        business_id: uuid.UUID,
        status: Optional[ProductStatus] = None,
        category_id: Optional[uuid.UUID] = None
    ) -> int:
        """Count products with optional filtering."""
        pass
    
    @abstractmethod
    async def exists_by_sku(
        self,
        business_id: uuid.UUID,
        sku: str,
        exclude_product_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if a product with the given SKU exists."""
        pass 