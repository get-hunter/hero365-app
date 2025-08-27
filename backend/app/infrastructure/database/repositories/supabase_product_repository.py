"""
Supabase Product Repository Implementation

Repository implementation using Supabase client SDK for product management operations
with comprehensive inventory tracking, cost management, and mobile optimization.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta

from supabase import Client

from app.domain.repositories.product_repository import ProductRepository
from app.domain.entities.product import Product
from app.domain.entities.product_enums.enums import ProductType, ProductStatus, CostingMethod
from app.domain.shared.enums import PricingModel, UnitOfMeasure, CurrencyCode
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DuplicateEntityError, DatabaseError
)

# Configure logging
logger = logging.getLogger(__name__)

class SupabaseProductRepository(ProductRepository):
    """
    Supabase client implementation of ProductRepository.
    
    This repository uses Supabase client SDK for all product database operations,
    leveraging RLS, real-time features, and comprehensive inventory management.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "products"
        logger.info(f"SupabaseProductRepository initialized with client: {self.client}")
    
    # Basic CRUD operations
    async def create(self, product: Product) -> Product:
        """Create a new product in Supabase."""
        logger.info(f"create() called for product: {product.name}, SKU: {product.sku}")
        
        try:
            product_data = self._product_to_dict(product)
            logger.info(f"Product data prepared: {product_data['name']}")
            
            response = self.client.table(self.table_name).insert(product_data).execute()
            logger.info(f"Supabase response received: data={response.data is not None}")
            
            if response.data:
                logger.info(f"Product created successfully: {response.data[0]['id']}")
                return self._dict_to_product(response.data[0])
            else:
                logger.error("Failed to create product - no data returned from Supabase")
                raise DatabaseError("Failed to create product - no data returned")
                
        except Exception as e:
            logger.error(f"Exception in create(): {type(e).__name__}: {str(e)}")
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateEntityError(f"Product with SKU '{product.sku}' already exists")
            raise DatabaseError(f"Failed to create product: {str(e)}")
    
    async def get_by_id(self, business_id: uuid.UUID, product_id: uuid.UUID) -> Optional[Product]:
        """Get product by ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("id", str(product_id)).execute()
            
            if response.data:
                return self._dict_to_product(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get product by ID: {str(e)}")
    
    async def get_by_sku(self, business_id: uuid.UUID, sku: str) -> Optional[Product]:
        """Get product by SKU."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("sku", sku).execute()
            
            if response.data:
                return self._dict_to_product(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get product by SKU: {str(e)}")
    
    async def update(self, product: Product) -> Product:
        """Update an existing product."""
        try:
            product_data = self._product_to_dict(product)
            product_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table(self.table_name).update(product_data).eq(
                "id", str(product.id)
            ).execute()
            
            if response.data:
                return self._dict_to_product(response.data[0])
            else:
                raise EntityNotFoundError(f"Product with ID {product.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateEntityError(f"Product SKU conflicts with existing product")
            raise DatabaseError(f"Failed to update product: {str(e)}")
    
    async def delete(self, business_id: uuid.UUID, product_id: uuid.UUID) -> bool:
        """Delete a product (soft delete)."""
        try:
            response = self.client.table(self.table_name).update({
                "is_active": False,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq("id", str(product_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete product: {str(e)}")
    
    # List and search operations
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
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if status:
                query = query.eq("status", status.value)
            if product_type:
                query = query.eq("product_type", product_type.value)
            if category_id:
                query = query.eq("category_id", str(category_id))
            
            response = query.range(offset, offset + limit - 1).order("name").execute()
            
            return [self._dict_to_product(product_data) for product_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to list products: {str(e)}")
    
    async def search_products(
        self,
        business_id: uuid.UUID,
        query: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Product]:
        """Search products by name, SKU, or description."""
        try:
            search_query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).or_(
                f"name.ilike.%{query}%,sku.ilike.%{query}%,description.ilike.%{query}%"
            )
            
            if filters:
                if "status" in filters:
                    search_query = search_query.eq("status", filters["status"])
                if "product_type" in filters:
                    search_query = search_query.eq("product_type", filters["product_type"])
                if "category_id" in filters:
                    search_query = search_query.eq("category_id", str(filters["category_id"]))
            
            response = search_query.range(offset, offset + limit - 1).order("name").execute()
            
            return [self._dict_to_product(product_data) for product_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search products: {str(e)}")
    
    async def get_by_category(
        self,
        business_id: uuid.UUID,
        category_id: uuid.UUID,
        include_subcategories: bool = False,
        status: Optional[ProductStatus] = None
    ) -> List[Product]:
        """Get products by category."""
        try:
            if include_subcategories:
                # Get category path and find all products in subcategories
                category_response = self.client.table("product_categories").select("path").eq(
                    "id", str(category_id)
                ).execute()
                
                if category_response.data:
                    category_path = category_response.data[0]["path"]
                    # Find all categories that start with this path
                    subcategory_response = self.client.table("product_categories").select("id").like(
                        "path", f"{category_path}%"
                    ).execute()
                    
                    category_ids = [cat["id"] for cat in subcategory_response.data]
                    
                    query = self.client.table(self.table_name).select("*").eq(
                        "business_id", str(business_id)
                    ).in_("category_id", category_ids)
                else:
                    query = self.client.table(self.table_name).select("*").eq(
                        "business_id", str(business_id)
                    ).eq("category_id", str(category_id))
            else:
                query = self.client.table(self.table_name).select("*").eq(
                    "business_id", str(business_id)
                ).eq("category_id", str(category_id))
            
            if status:
                query = query.eq("status", status.value)
            
            response = query.order("name").execute()
            
            return [self._dict_to_product(product_data) for product_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get products by category: {str(e)}")
    
    # Inventory management operations
    async def get_low_stock_products(
        self,
        business_id: uuid.UUID,
        location_id: Optional[uuid.UUID] = None
    ) -> List[Product]:
        """Get products that are below their reorder point."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("track_inventory", True).filter(
                "current_stock", "lte", "reorder_point"
            ).eq("status", ProductStatus.active.value)
            
            response = query.order("name").execute()
            
            return [self._dict_to_product(product_data) for product_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get low stock products: {str(e)}")
    
    async def get_out_of_stock_products(
        self,
        business_id: uuid.UUID,
        location_id: Optional[uuid.UUID] = None
    ) -> List[Product]:
        """Get products that are out of stock."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("track_inventory", True).eq("current_stock", 0).eq("status", ProductStatus.active.value)
            
            response = query.order("name").execute()
            
            return [self._dict_to_product(product_data) for product_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get out of stock products: {str(e)}")
    
    async def get_products_needing_reorder(
        self,
        business_id: uuid.UUID,
        location_id: Optional[uuid.UUID] = None
    ) -> List[Product]:
        """Get products that need to be reordered."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("track_inventory", True).filter(
                "current_stock", "lte", "reorder_point"
            ).gt("reorder_quantity", 0).eq("status", ProductStatus.active.value)
            
            response = query.order("name").execute()
            
            return [self._dict_to_product(product_data) for product_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get products needing reorder: {str(e)}")
    
    async def update_quantity(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity_change: Decimal,
        location_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Update product quantity."""
        try:
            # Get current stock first
            current_response = self.client.table(self.table_name).select("current_stock").eq(
                "business_id", str(business_id)
            ).eq("id", str(product_id)).execute()
            
            if not current_response.data:
                raise EntityNotFoundError(f"Product with ID {product_id} not found")
            
            current_stock = Decimal(str(current_response.data[0]["current_stock"]))
            new_stock = current_stock + quantity_change
            
            # Ensure stock doesn't go negative
            if new_stock < 0:
                new_stock = Decimal('0')
            
            response = self.client.table(self.table_name).update({
                "current_stock": float(new_stock),
                "last_inventory_update": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq("id", str(product_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to update product quantity: {str(e)}")
    
    async def reserve_quantity(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: Decimal,
        location_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Reserve product quantity for an order."""
        try:
            # Get current reserved stock
            current_response = self.client.table(self.table_name).select("reserved_stock").eq(
                "business_id", str(business_id)
            ).eq("id", str(product_id)).execute()
            
            if not current_response.data:
                raise EntityNotFoundError(f"Product with ID {product_id} not found")
            
            current_reserved = Decimal(str(current_response.data[0]["reserved_stock"]))
            new_reserved = current_reserved + quantity
            
            response = self.client.table(self.table_name).update({
                "reserved_stock": float(new_reserved),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq("id", str(product_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to reserve product quantity: {str(e)}")
    
    async def release_reservation(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: Decimal,
        location_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Release reserved product quantity."""
        try:
            # Get current reserved stock
            current_response = self.client.table(self.table_name).select("reserved_stock").eq(
                "business_id", str(business_id)
            ).eq("id", str(product_id)).execute()
            
            if not current_response.data:
                raise EntityNotFoundError(f"Product with ID {product_id} not found")
            
            current_reserved = Decimal(str(current_response.data[0]["reserved_stock"]))
            new_reserved = max(Decimal('0'), current_reserved - quantity)
            
            response = self.client.table(self.table_name).update({
                "reserved_stock": float(new_reserved),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq("id", str(product_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to release reserved quantity: {str(e)}")
    
    # Cost and pricing operations
    async def update_cost(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        new_cost: Decimal,
        quantity: Optional[Decimal] = None
    ) -> bool:
        """Update product cost using appropriate costing method."""
        try:
            # Get current product data
            current_response = self.client.table(self.table_name).select(
                "cost_price, weighted_average_cost, costing_method, current_stock"
            ).eq("business_id", str(business_id)).eq("id", str(product_id)).execute()
            
            if not current_response.data:
                raise EntityNotFoundError(f"Product with ID {product_id} not found")
            
            current_data = current_response.data[0]
            costing_method = current_data["costing_method"]
            current_stock = Decimal(str(current_data["current_stock"]))
            current_weighted_avg = Decimal(str(current_data["weighted_average_cost"]))
            
            update_data = {
                "last_cost": float(new_cost),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update weighted average cost for appropriate methods
            if costing_method == CostingMethod.weighted_average.value:
                if current_stock > 0 and quantity:
                    total_value = (current_weighted_avg * current_stock) + (new_cost * quantity)
                    total_quantity = current_stock + quantity
                    new_weighted_avg = total_value / total_quantity
                    update_data["weighted_average_cost"] = float(new_weighted_avg)
                else:
                    update_data["weighted_average_cost"] = float(new_cost)
            
            # Update cost price for fixed cost methods
            if costing_method in [CostingMethod.standard_cost.value, CostingMethod.specific_identification.value]:
                update_data["cost_price"] = float(new_cost)
            
            response = self.client.table(self.table_name).update(update_data).eq(
                "business_id", str(business_id)
            ).eq("id", str(product_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to update product cost: {str(e)}")
    
    async def get_product_cost_history(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get product cost history from stock movements."""
        try:
            response = self.client.table("stock_movements").select(
                "movement_date, unit_cost, quantity, movement_type"
            ).eq("business_id", str(business_id)).eq("product_id", str(product_id)).gt(
                "unit_cost", 0
            ).order("movement_date", desc=True).limit(limit).execute()
            
            return response.data
            
        except Exception as e:
            raise DatabaseError(f"Failed to get product cost history: {str(e)}")
    
    async def calculate_inventory_value(
        self,
        business_id: uuid.UUID,
        category_id: Optional[uuid.UUID] = None,
        location_id: Optional[uuid.UUID] = None
    ) -> Decimal:
        """Calculate total inventory value."""
        try:
            query = self.client.table(self.table_name).select(
                "current_stock, weighted_average_cost"
            ).eq("business_id", str(business_id)).eq("track_inventory", True)
            
            if category_id:
                query = query.eq("category_id", str(category_id))
            
            response = query.execute()
            
            total_value = Decimal('0')
            for product_data in response.data:
                stock = Decimal(str(product_data["current_stock"]))
                cost = Decimal(str(product_data["weighted_average_cost"]))
                total_value += stock * cost
            
            return total_value
            
        except Exception as e:
            raise DatabaseError(f"Failed to calculate inventory value: {str(e)}")
    
    # Mobile app optimization
    async def get_products_for_mobile(
        self,
        business_id: uuid.UUID,
        category_id: Optional[uuid.UUID] = None,
        search_query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get products optimized for mobile app consumption."""
        try:
            query = self.client.table(self.table_name).select(
                "id, sku, name, description, unit_price, current_stock, status, product_type, unit_of_measure"
            ).eq("business_id", str(business_id)).eq("is_active", True)
            
            if category_id:
                query = query.eq("category_id", str(category_id))
            
            if search_query:
                query = query.or_(f"name.ilike.%{search_query}%,sku.ilike.%{search_query}%")
            
            response = query.range(offset, offset + limit - 1).order("name").execute()
            
            return {
                "products": response.data,
                "total_count": len(response.data),
                "has_more": len(response.data) == limit
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get products for mobile: {str(e)}")
    
    async def get_product_availability_for_estimate(
        self,
        business_id: uuid.UUID,
        product_ids: List[uuid.UUID],
        quantities: List[Decimal],
        location_id: Optional[uuid.UUID] = None
    ) -> Dict[uuid.UUID, Dict[str, Any]]:
        """Check product availability for estimate/invoice creation."""
        try:
            response = self.client.table(self.table_name).select(
                "id, name, sku, current_stock, reserved_stock, available_stock, unit_price, track_inventory"
            ).eq("business_id", str(business_id)).in_(
                "id", [str(pid) for pid in product_ids]
            ).execute()
            
            availability = {}
            product_map = {pid: qty for pid, qty in zip(product_ids, quantities)}
            
            for product_data in response.data:
                product_id = uuid.UUID(product_data["id"])
                requested_qty = product_map.get(product_id, Decimal('0'))
                available_qty = Decimal(str(product_data["available_stock"]))
                
                availability[product_id] = {
                    "name": product_data["name"],
                    "sku": product_data["sku"],
                    "requested_quantity": float(requested_qty),
                    "available_quantity": float(available_qty),
                    "is_available": not product_data["track_inventory"] or available_qty >= requested_qty,
                    "unit_price": product_data["unit_price"],
                    "shortage": max(0, float(requested_qty - available_qty)) if product_data["track_inventory"] else 0
                }
            
            return availability
            
        except Exception as e:
            raise DatabaseError(f"Failed to check product availability: {str(e)}")
    
    # Count operations
    async def count_products(
        self,
        business_id: uuid.UUID,
        status: Optional[ProductStatus] = None,
        category_id: Optional[uuid.UUID] = None
    ) -> int:
        """Count products with optional filtering."""
        try:
            query = self.client.table(self.table_name).select("id", count="exact").eq("business_id", str(business_id))
            
            if status:
                query = query.eq("status", status.value)
            if category_id:
                query = query.eq("category_id", str(category_id))
            
            response = query.execute()
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count products: {str(e)}")
    
    async def exists_by_sku(
        self,
        business_id: uuid.UUID,
        sku: str,
        exclude_product_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if a product with the given SKU exists."""
        try:
            query = self.client.table(self.table_name).select("id").eq("business_id", str(business_id)).eq("sku", sku)
            
            if exclude_product_id:
                query = query.neq("id", str(exclude_product_id))
            
            response = query.execute()
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check SKU existence: {str(e)}")
    
    # Supplier and supplier integration
    async def get_products_by_supplier(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        status: Optional[ProductStatus] = None
    ) -> List[Product]:
        """Get products from a specific supplier."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("primary_supplier_id", str(supplier_id))
            
            if status:
                query = query.eq("status", status.value)
            
            response = query.order("name").execute()
            
            return [self._dict_to_product(product) for product in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get products by supplier: {str(e)}")
    
    async def update_supplier_info(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        supplier_id: uuid.UUID,
        supplier_data: Dict[str, Any]
    ) -> bool:
        """Update supplier information for a product."""
        try:
            update_data = {
                "primary_supplier_id": str(supplier_id),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if "supplier_sku" in supplier_data:
                update_data["supplier_sku"] = supplier_data["supplier_sku"]
            if "lead_time_days" in supplier_data:
                update_data["lead_time_days"] = supplier_data["lead_time_days"]
            
            response = self.client.table(self.table_name).update(update_data).eq(
                "business_id", str(business_id)
            ).eq("id", str(product_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to update supplier info: {str(e)}")
    
    # Location management
    async def get_products_at_location(
        self,
        business_id: uuid.UUID,
        location_id: uuid.UUID,
        status: Optional[ProductStatus] = None
    ) -> List[Product]:
        """Get products available at a specific location."""
        try:
            # For now, return all products since multi-location is not fully implemented in schema
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).gt("current_stock", 0)
            
            if status:
                query = query.eq("status", status.value)
            
            response = query.order("name").execute()
            
            return [self._dict_to_product(product) for product in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get products at location: {str(e)}")
    
    async def transfer_between_locations(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        from_location_id: uuid.UUID,
        to_location_id: uuid.UUID,
        quantity: Decimal
    ) -> bool:
        """Transfer product quantity between locations."""
        try:
            # For now, this is a placeholder since multi-location is not fully implemented
            # In a full implementation, this would update location-specific stock tables
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to transfer between locations: {str(e)}")
    
    # Analytics and reporting
    async def get_product_analytics(
        self,
        business_id: uuid.UUID,
        product_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get product analytics and performance metrics."""
        try:
            query = self.client.table(self.table_name).select(
                "id, name, sku, total_sold, total_revenue, current_stock, status, reorder_point"
            ).eq("business_id", str(business_id))
            
            if product_id:
                query = query.eq("id", str(product_id))
            if category_id:
                query = query.eq("category_id", str(category_id))
            
            response = query.execute()
            
            analytics = {
                "total_products": len(response.data),
                "total_inventory_value": 0,
                "total_revenue": 0,
                "total_sold": 0,
                "out_of_stock_count": 0,
                "low_stock_count": 0,
                "products": []
            }
            
            for product in response.data:
                analytics["total_revenue"] += float(product.get("total_revenue", 0))
                analytics["total_sold"] += float(product.get("total_sold", 0))
                current_stock = product.get("current_stock", 0)
                reorder_point = product.get("reorder_point", 0)
                
                if current_stock == 0:
                    analytics["out_of_stock_count"] += 1
                elif reorder_point and current_stock <= reorder_point:
                    analytics["low_stock_count"] += 1
                
                analytics["products"].append({
                    "id": product["id"],
                    "name": product["name"],
                    "sku": product["sku"],
                    "total_sold": product.get("total_sold", 0),
                    "total_revenue": product.get("total_revenue", 0),
                    "current_stock": current_stock
                })
            
            return analytics
            
        except Exception as e:
            raise DatabaseError(f"Failed to get product analytics: {str(e)}")
    
    async def get_top_selling_products(
        self,
        business_id: uuid.UUID,
        limit: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top selling products."""
        try:
            response = self.client.table(self.table_name).select(
                "id, name, sku, total_sold, total_revenue"
            ).eq("business_id", str(business_id)).gt("total_sold", 0).order(
                "total_sold", desc=True
            ).limit(limit).execute()
            
            return response.data
            
        except Exception as e:
            raise DatabaseError(f"Failed to get top selling products: {str(e)}")
    
    async def get_slow_moving_products(
        self,
        business_id: uuid.UUID,
        days_threshold: int = 90,
        limit: int = 20
    ) -> List[Product]:
        """Get products with no sales in specified period."""
        try:
            threshold_date = datetime.utcnow() - timedelta(days=days_threshold)
            
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).or_(
                f"last_sold_date.is.null,last_sold_date.lt.{threshold_date.isoformat()}"
            ).gt("current_stock", 0).order("last_sold_date").limit(limit)
            
            response = query.execute()
            
            return [self._dict_to_product(product) for product in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get slow moving products: {str(e)}")
    
    # Bulk operations
    async def bulk_update_status(
        self,
        business_id: uuid.UUID,
        product_ids: List[uuid.UUID],
        status: ProductStatus
    ) -> int:
        """Bulk update product status."""
        try:
            update_data = {
                "status": status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table(self.table_name).update(update_data).eq(
                "business_id", str(business_id)
            ).in_("id", [str(pid) for pid in product_ids]).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk update status: {str(e)}")
    
    async def bulk_update_pricing(
        self,
        business_id: uuid.UUID,
        updates: List[Dict[str, Any]]
    ) -> int:
        """Bulk update product pricing."""
        try:
            updated_count = 0
            
            for update in updates:
                product_id = update.get("product_id")
                update_data = {
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                if "unit_price" in update:
                    update_data["unit_price"] = float(update["unit_price"])
                if "cost_price" in update:
                    update_data["cost_price"] = float(update["cost_price"])
                if "markup_percentage" in update:
                    update_data["markup_percentage"] = float(update["markup_percentage"])
                
                response = self.client.table(self.table_name).update(update_data).eq(
                    "business_id", str(business_id)
                ).eq("id", str(product_id)).execute()
                
                if response.data:
                    updated_count += 1
            
            return updated_count
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk update pricing: {str(e)}")
    
    async def bulk_adjust_inventory(
        self,
        business_id: uuid.UUID,
        adjustments: List[Dict[str, Any]]
    ) -> int:
        """Bulk adjust inventory quantities."""
        try:
            updated_count = 0
            
            for adjustment in adjustments:
                product_id = adjustment.get("product_id")
                quantity_change = Decimal(str(adjustment.get("quantity_change", 0)))
                
                # Get current stock
                current_response = self.client.table(self.table_name).select("current_stock").eq(
                    "business_id", str(business_id)
                ).eq("id", str(product_id)).execute()
                
                if current_response.data:
                    current_stock = Decimal(str(current_response.data[0]["current_stock"]))
                    new_stock = max(Decimal('0'), current_stock + quantity_change)
                    
                    update_response = self.client.table(self.table_name).update({
                        "current_stock": float(new_stock),
                        "available_stock": float(new_stock),  # Simplified for now
                        "last_inventory_update": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }).eq("business_id", str(business_id)).eq("id", str(product_id)).execute()
                    
                    if update_response.data:
                        updated_count += 1
            
            return updated_count
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk adjust inventory: {str(e)}")
    
    # Advanced search and filtering
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
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            # Apply filters
            if "status" in filters:
                query = query.eq("status", filters["status"])
            if "product_type" in filters:
                query = query.eq("product_type", filters["product_type"])
            if "category_id" in filters:
                query = query.eq("category_id", str(filters["category_id"]))
            if "supplier_id" in filters:
                query = query.eq("primary_supplier_id", str(filters["supplier_id"]))
            if "min_price" in filters:
                query = query.gte("unit_price", filters["min_price"])
            if "max_price" in filters:
                query = query.lte("unit_price", filters["max_price"])
            if "low_stock" in filters and filters["low_stock"]:
                query = query.filter("current_stock", "lte", "reorder_point")
            if "search_term" in filters:
                term = filters["search_term"]
                query = query.or_(f"name.ilike.%{term}%,sku.ilike.%{term}%,description.ilike.%{term}%")
            
            # Apply sorting
            if sort_by:
                desc = sort_order.lower() == "desc"
                query = query.order(sort_by, desc=desc)
            else:
                query = query.order("name")
            
            # Get total count
            count_response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).execute()
            
            # Apply pagination
            response = query.range(offset, offset + limit - 1).execute()
            
            return {
                "products": [self._dict_to_product(product) for product in response.data],
                "total_count": count_response.count or 0,
                "has_more": len(response.data) == limit,
                "offset": offset,
                "limit": limit
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to perform advanced search: {str(e)}")
    
    async def get_filter_options(
        self,
        business_id: uuid.UUID
    ) -> Dict[str, List[Any]]:
        """Get available filter options for product search."""
        try:
            # Get distinct values for filter options
            categories_response = self.client.table("product_categories").select(
                "id, name"
            ).eq("business_id", str(business_id)).eq("is_active", True).execute()
            
            suppliers_response = self.client.table("suppliers").select(
                "id, company_name"
            ).eq("business_id", str(business_id)).eq("is_active", True).execute()
            
            return {
                "statuses": [{"value": status.value, "label": status.display_name()} for status in ProductStatus],
                "product_types": [{"value": ptype.value, "label": ptype.display_name()} for ptype in ProductType],
                "categories": [{"value": cat["id"], "label": cat["name"]} for cat in categories_response.data],
                "suppliers": [{"value": sup["id"], "label": sup["company_name"]} for sup in suppliers_response.data]
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get filter options: {str(e)}")
    
    # Helper methods for data conversion
    def _product_to_dict(self, product: Product) -> dict:
        """Convert Product entity to dictionary for Supabase storage."""
        return {
            "id": str(product.id),
            "business_id": str(product.business_id),
            "category_id": str(product.category_id) if product.category_id else None,
            "sku": product.sku,
            "name": product.name,
            "description": product.description,
            "long_description": product.long_description,
            "product_type": product.product_type.value,
            "status": product.status.value,
            "pricing_model": product.pricing_model.value,
            "unit_price": float(product.unit_price),
            "cost_price": float(product.cost_price),
            "minimum_price": float(product.minimum_price) if product.minimum_price else None,
            "markup_percentage": float(product.markup_percentage) if product.markup_percentage else None,
            "unit_of_measure": product.unit_of_measure.value,
            "weight": float(product.weight) if product.weight else None,
            "dimensions": product.dimensions,
            "track_inventory": product.track_inventory,
            "current_stock": float(product.current_stock),
            "reserved_stock": float(product.reserved_stock),
            "available_stock": float(product.available_stock),
            "reorder_point": float(product.reorder_point) if product.reorder_point else None,
            "reorder_quantity": float(product.reorder_quantity) if product.reorder_quantity else None,
            "minimum_stock_level": float(product.minimum_stock_level) if product.minimum_stock_level else None,
            "maximum_stock_level": float(product.maximum_stock_level) if product.maximum_stock_level else None,
            "costing_method": product.costing_method.value,
            "weighted_average_cost": float(product.weighted_average_cost),
            "last_cost": float(product.last_cost) if product.last_cost else None,
            "standard_cost": float(product.standard_cost) if product.standard_cost else None,
            "inventory_account": product.inventory_account,
            "cost_of_goods_sold_account": product.cost_of_goods_sold_account,
            "income_account": product.income_account,
            "tax_rate": float(product.tax_rate) if product.tax_rate else None,
            "tax_category": product.tax_category,
            "is_taxable": product.is_taxable,
            "primary_supplier_id": str(product.primary_supplier_id) if product.primary_supplier_id else None,
            "supplier_sku": product.supplier_sku,
            "lead_time_days": product.lead_time_days,
            "barcode": product.barcode,
            "qr_code": product.qr_code,
            "images": product.images,
            "attachments": product.attachments,
            "notes": product.notes,
            "tags": product.tags,
            "is_active": product.is_active,
            "is_featured": product.is_featured,
            "is_digital": product.is_digital,
            "total_sold": float(product.total_sold),
            "total_revenue": float(product.total_revenue),
            "last_sold_date": product.last_sold_date.isoformat() if product.last_sold_date else None,
            "last_purchased_date": product.last_purchased_date.isoformat() if product.last_purchased_date else None,
            "last_inventory_update": product.last_inventory_update.isoformat() if product.last_inventory_update else None,
            "created_by": product.created_by,
            "updated_by": product.updated_by,
        }
    
    def _dict_to_product(self, data: dict) -> Product:
        """Convert dictionary from Supabase to Product entity."""
        def safe_decimal(value, default=None):
            if value is None:
                return default
            return Decimal(str(value))
        
        def safe_datetime(value):
            if value is None:
                return None
            if isinstance(value, str):
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            return value
        
        # Derive product_type from available database fields
        if data.get("is_digital", False):
            product_type = ProductType.DIGITAL
        elif data.get("has_variations", False):
            product_type = ProductType.BUNDLE
        else:
            product_type = ProductType.PRODUCT
        
        try:
            # Create minimal Product entity with only absolutely required fields
            product = Product(
                id=uuid.UUID(data["id"]),
                business_id=uuid.UUID(data["business_id"]),
                sku=data["sku"],
                name=data["name"],
                description=data.get("description"),
                product_type=product_type,
                status=ProductStatus(data.get("status", "active")),
                category_id=uuid.UUID(data["category_id"]) if data.get("category_id") else None,
                track_inventory=data.get("track_inventory", True),
                quantity_on_hand=safe_decimal(data.get("current_stock"), Decimal('0')),
                unit_price=safe_decimal(data.get("unit_price"), Decimal('0')),
                unit_cost=safe_decimal(data.get("cost_price"), Decimal('0')),
                is_active=data.get("is_active", True),
                created_at=safe_datetime(data.get("created_at")) or datetime.utcnow(),
                updated_at=safe_datetime(data.get("updated_at")) or datetime.utcnow(),
                created_by=data.get("created_by") or "system",  # Required field, handle null
                updated_by=data.get("updated_by") or "system",  # Add this too for consistency
            )
            return product
        except Exception as e:
            logger.error(f"Failed to create product entity: {e}")
            raise 