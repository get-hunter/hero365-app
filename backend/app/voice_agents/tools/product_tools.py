"""
Voice agent tools for product and inventory management.
Provides voice-activated inventory operations for Hero365.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from decimal import Decimal

from livekit.agents import function_tool

from app.infrastructure.config.dependency_injection import DependencyContainer
from app.application.use_cases.product.create_product_use_case import CreateProductUseCase
from app.application.use_cases.product.manage_inventory_use_case import ManageInventoryUseCase
from app.application.use_cases.product.inventory_reorder_management_use_case import InventoryReorderManagementUseCase
from app.application.dto.product_dto import (
    CreateProductDTO,
    StockAdjustmentDTO,
    ProductDTO,
)
from app.domain.enums import ProductType, ProductStatus, PricingModel, UnitOfMeasure, CostingMethod

logger = logging.getLogger(__name__)

# Global context storage for the worker environment
_current_context: Dict[str, Any] = {}

def set_current_context(context: Dict[str, Any]) -> None:
    """Set the current agent context."""
    global _current_context
    _current_context = context

def get_current_context() -> Dict[str, str]:
    """Get current business and user context from agent."""
    global _current_context
    if not _current_context.get("business_id") or not _current_context.get("user_id"):
        logger.warning("Agent context not available for product tools")
        return {"business_id": "", "user_id": ""}
    return {
        "business_id": _current_context.get("business_id", ""),
        "user_id": _current_context.get("user_id", "")
    }


@function_tool
async def create_product(
    name: str,
    sku: str,
    product_type: str = "product",
    unit_price: float = 0.0,
    cost_price: float = 0.0,
    description: Optional[str] = None,
    unit_of_measure: str = "each",
    track_inventory: bool = True,
    initial_quantity: int = 0,
    reorder_point: Optional[int] = None,
    reorder_quantity: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a new product for the business.
    
    Args:
        name: Product name
        sku: Product SKU (Stock Keeping Unit)
        product_type: Type of product (product, service, digital)
        unit_price: Selling price per unit
        cost_price: Cost price per unit
        description: Product description
        unit_of_measure: Unit of measurement (each, hour, pound, etc.)
        track_inventory: Whether to track inventory for this product
        initial_quantity: Initial stock quantity
        reorder_point: Minimum stock level before reordering
        reorder_quantity: Quantity to reorder when stock is low
    
    Returns:
        Dictionary with product creation result
    """
    try:
        container = DependencyContainer()
        create_product_use_case = container.get_create_product_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to create product. Please try again."
            }
        
        # Convert string enums
        try:
            product_type_enum = ProductType(product_type.upper())
        except ValueError:
            product_type_enum = ProductType.PRODUCT
            
        try:
            unit_of_measure_enum = UnitOfMeasure(unit_of_measure.upper())
        except ValueError:
            unit_of_measure_enum = UnitOfMeasure.EACH
        
        product_dto = CreateProductDTO(
            business_id=uuid.UUID(business_id),
            sku=sku,
            name=name,
            description=description,
            product_type=product_type_enum,
            status=ProductStatus.ACTIVE,
            pricing_model=PricingModel.FIXED,
            unit_price=Decimal(str(unit_price)),
            cost_price=Decimal(str(cost_price)),
            unit_of_measure=unit_of_measure_enum,
            track_inventory=track_inventory,
            initial_quantity=Decimal(str(initial_quantity)),
            reorder_point=Decimal(str(reorder_point)) if reorder_point else None,
            reorder_quantity=Decimal(str(reorder_quantity)) if reorder_quantity else None,
            costing_method=CostingMethod.FIFO
        )
        
        result = await create_product_use_case.execute(product_dto, user_id, business_id)
        
        logger.info(f"Created product via voice agent: {result.id}")
        
        return {
            "success": True,
            "product_id": str(result.id),
            "name": result.name,
            "sku": result.sku,
            "unit_price": float(result.unit_price),
            "cost_price": float(result.cost_price),
            "initial_quantity": float(result.initial_quantity),
            "message": f"Product '{name}' created successfully with SKU '{sku}'"
        }
        
    except Exception as e:
        logger.error(f"Error creating product via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create product. Please try again."
        }


@function_tool
async def check_stock_levels(product_name: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    """
    Check current stock levels for products.
    
    Args:
        product_name: Optional product name to search for (if not provided, shows all products)
        limit: Maximum number of products to return
    
    Returns:
        Dictionary with current stock levels
    """
    try:
        container = DependencyContainer()
        product_repository = container.get_product_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to check stock levels. Please try again."
            }
        
        # Get products with stock information
        if product_name:
            products = await product_repository.search_by_name(
                business_id=uuid.UUID(business_id),
                search_term=product_name,
                limit=limit
            )
        else:
            products = await product_repository.get_all(
                business_id=uuid.UUID(business_id),
                skip=0,
                limit=limit
            )
        
        stock_info = []
        low_stock_count = 0
        
        for product in products:
            if product.track_inventory:
                is_low_stock = (product.reorder_point and 
                               product.quantity_on_hand <= product.reorder_point)
                
                if is_low_stock:
                    low_stock_count += 1
                
                stock_info.append({
                    "product_id": str(product.id),
                    "name": product.name,
                    "sku": product.sku,
                    "quantity_on_hand": float(product.quantity_on_hand),
                    "quantity_available": float(product.quantity_available),
                    "reorder_point": float(product.reorder_point) if product.reorder_point else None,
                    "is_low_stock": is_low_stock,
                    "unit_of_measure": product.unit_of_measure.value
                })
        
        logger.info(f"Retrieved stock levels for {len(stock_info)} products via voice agent")
        
        return {
            "success": True,
            "products": stock_info,
            "total_count": len(stock_info),
            "low_stock_count": low_stock_count,
            "message": f"Found {len(stock_info)} products. {low_stock_count} products are low on stock."
        }
        
    except Exception as e:
        logger.error(f"Error checking stock levels via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to check stock levels. Please try again."
        }


@function_tool
async def adjust_stock(
    product_name: str,
    quantity_change: int,
    reason: str,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Adjust stock levels for a product.
    
    Args:
        product_name: Name or SKU of the product
        quantity_change: Change in quantity (positive for increase, negative for decrease)
        reason: Reason for the adjustment (e.g., "damaged", "found", "correction")
        notes: Additional notes about the adjustment
    
    Returns:
        Dictionary with adjustment result
    """
    try:
        container = DependencyContainer()
        product_repository = container.get_product_repository()
        manage_inventory_use_case = container.get_manage_inventory_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to adjust stock. Please try again."
            }
        
        # Find the product
        products = await product_repository.search_by_name(
            business_id=uuid.UUID(business_id),
            search_term=product_name,
            limit=1
        )
        
        if not products:
            return {
                "success": False,
                "error": "Product not found",
                "message": f"No product found matching '{product_name}'"
            }
        
        product = products[0]
        
        # Create adjustment DTO
        adjustment_dto = StockAdjustmentDTO(
            product_id=product.id,
            quantity_change=Decimal(str(quantity_change)),
            adjustment_reason=reason,
            notes=notes,
            reference_number=f"VA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        # Execute the adjustment
        result = await manage_inventory_use_case.adjust_stock(
            adjustment_dto, user_id, uuid.UUID(business_id)
        )
        
        logger.info(f"Stock adjusted for product {product.name} via voice agent")
        
        return {
            "success": True,
            "product_name": product.name,
            "quantity_change": quantity_change,
            "new_quantity": float(result.get("new_quantity", 0)),
            "reason": reason,
            "message": f"Stock adjusted for {product.name}. Change: {quantity_change:+d}, New quantity: {result.get('new_quantity', 0)}"
        }
        
    except Exception as e:
        logger.error(f"Error adjusting stock via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to adjust stock. Please try again."
        }


@function_tool
async def get_reorder_suggestions(limit: int = 10) -> Dict[str, Any]:
    """
    Get products that need to be reordered.
    
    Args:
        limit: Maximum number of suggestions to return
    
    Returns:
        Dictionary with reorder suggestions
    """
    try:
        container = DependencyContainer()
        inventory_reorder_use_case = container.get_inventory_reorder_management_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to get reorder suggestions. Please try again."
            }
        
        # Get reorder suggestions
        suggestions = await inventory_reorder_use_case.get_reorder_suggestions(
            business_id=uuid.UUID(business_id),
            user_id=user_id
        )
        
        # Limit the results
        limited_suggestions = suggestions.get("suggestions", [])[:limit]
        
        logger.info(f"Retrieved {len(limited_suggestions)} reorder suggestions via voice agent")
        
        return {
            "success": True,
            "suggestions": limited_suggestions,
            "total_count": len(limited_suggestions),
            "total_suggested_value": suggestions.get("total_suggested_value", 0),
            "message": f"Found {len(limited_suggestions)} products that need reordering"
        }
        
    except Exception as e:
        logger.error(f"Error getting reorder suggestions via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get reorder suggestions. Please try again."
        }


@function_tool
async def search_products(search_term: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search products by name, SKU, or description.
    
    Args:
        search_term: Text to search for in product names, SKUs, or descriptions
        limit: Maximum number of products to return
    
    Returns:
        Dictionary with search results
    """
    try:
        container = DependencyContainer()
        product_repository = container.get_product_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to search products. Please try again."
            }
        
        # Search products
        products = await product_repository.search_by_name(
            business_id=uuid.UUID(business_id),
            search_term=search_term,
            limit=limit
        )
        
        product_results = []
        for product in products:
            product_results.append({
                "id": str(product.id),
                "name": product.name,
                "sku": product.sku,
                "product_type": product.product_type.value,
                "unit_price": float(product.unit_price),
                "cost_price": float(product.unit_cost) if product.unit_cost else 0,
                "quantity_on_hand": float(product.quantity_on_hand) if product.track_inventory else None,
                "status": product.status.value,
                "unit_of_measure": product.unit_of_measure.value
            })
        
        logger.info(f"Found {len(product_results)} products matching '{search_term}' via voice agent")
        
        return {
            "success": True,
            "products": product_results,
            "search_term": search_term,
            "total_count": len(product_results),
            "message": f"Found {len(product_results)} products matching '{search_term}'"
        }
        
    except Exception as e:
        logger.error(f"Error searching products via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to search products. Please try again."
        }


@function_tool 
async def get_product_details(product_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific product.
    
    Args:
        product_name: Name or SKU of the product
    
    Returns:
        Dictionary with product details
    """
    try:
        container = DependencyContainer()
        product_repository = container.get_product_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to get product details. Please try again."
            }
        
        # Find the product
        products = await product_repository.search_by_name(
            business_id=uuid.UUID(business_id),
            search_term=product_name,
            limit=1
        )
        
        if not products:
            return {
                "success": False,
                "error": "Product not found",
                "message": f"No product found matching '{product_name}'"
            }
        
        product = products[0]
        
        logger.info(f"Retrieved product details for {product.name} via voice agent")
        
        return {
            "success": True,
            "product": {
                "id": str(product.id),
                "name": product.name,
                "sku": product.sku,
                "description": product.description,
                "product_type": product.product_type.value,
                "status": product.status.value,
                "unit_price": float(product.unit_price),
                "cost_price": float(product.unit_cost) if product.unit_cost else 0,
                "unit_of_measure": product.unit_of_measure.value,
                "track_inventory": product.track_inventory,
                "quantity_on_hand": float(product.quantity_on_hand) if product.track_inventory else None,
                "quantity_available": float(product.quantity_available) if product.track_inventory else None,
                "reorder_point": float(product.reorder_point) if product.reorder_point else None,
                "reorder_quantity": float(product.reorder_quantity) if product.reorder_quantity else None,
                "created_date": product.created_date.isoformat() if product.created_date else None
            },
            "message": f"Product details for '{product.name}'"
        }
        
    except Exception as e:
        logger.error(f"Error getting product details via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get product details. Please try again."
        } 