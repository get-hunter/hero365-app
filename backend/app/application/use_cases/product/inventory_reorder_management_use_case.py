"""
Inventory Reorder Management Use Case

Handles automated reorder suggestions and inventory planning.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from app.domain.entities.product import Product
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.supplier_repository import SupplierRepository
from app.domain.repositories.purchase_order_repository import PurchaseOrderRepository
from app.domain.enums import ProductStatus
from app.domain.exceptions.domain_exceptions import (
    DomainValidationError, BusinessRuleViolationError, EntityNotFoundError
)
from app.application.dto.product_dto import ProductDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class InventoryReorderManagementUseCase:
    """Use case for inventory reorder management and optimization."""
    
    def __init__(
        self,
        product_repository: ProductRepository,
        supplier_repository: SupplierRepository,
        purchase_order_repository: PurchaseOrderRepository
    ):
        self.product_repository = product_repository
        self.supplier_repository = supplier_repository
        self.purchase_order_repository = purchase_order_repository
    
    async def get_reorder_suggestions(
        self,
        business_id: uuid.UUID,
        user_id: str,
        category_id: Optional[uuid.UUID] = None,
        supplier_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get automated reorder suggestions for products."""
        try:
            logger.info(f"Generating reorder suggestions for business {business_id}")
            
            # Get products needing reorder
            products_needing_reorder = await self.product_repository.get_products_needing_reorder(
                business_id, location_id=None
            )
            
            # Apply filters
            if category_id:
                products_needing_reorder = [p for p in products_needing_reorder if p.category_id == category_id]
            
            if supplier_id:
                products_needing_reorder = [p for p in products_needing_reorder if p.primary_supplier_id == supplier_id]
            
            # Generate suggestions
            suggestions = []
            total_suggested_value = Decimal('0')
            
            for product in products_needing_reorder:
                suggestion = self._generate_product_reorder_suggestion(product)
                suggestions.append(suggestion)
                total_suggested_value += suggestion['suggested_cost']
            
            return {
                "suggestions": suggestions,
                "total_items": len(suggestions),
                "total_suggested_value": float(total_suggested_value),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating reorder suggestions: {e}")
            raise ApplicationError(f"Failed to generate reorder suggestions: {str(e)}")
    
    async def calculate_optimal_order_quantities(
        self,
        business_id: uuid.UUID,
        product_ids: List[uuid.UUID],
        user_id: str,
        forecast_days: int = 90
    ) -> Dict[str, Any]:
        """Calculate optimal order quantities using economic order quantity (EOQ) model."""
        try:
            logger.info(f"Calculating optimal order quantities for {len(product_ids)} products")
            
            # Validate permissions
            await self._validate_permissions(business_id, user_id, "view_inventory_reports")
            
            optimizations = []
            total_optimization_savings = Decimal('0')
            
            for product_id in product_ids:
                product = await self.product_repository.get_by_id(business_id, product_id)
                if not product:
                    continue
                
                optimization = await self._calculate_eoq_for_product(product, forecast_days)
                optimizations.append(optimization)
                total_optimization_savings += optimization.get('potential_savings', Decimal('0'))
            
            logger.info(f"Completed optimization calculations for {len(optimizations)} products")
            
            return {
                "optimizations": optimizations,
                "total_items": len(optimizations),
                "total_potential_savings": float(total_optimization_savings),
                "forecast_period_days": forecast_days,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating optimal order quantities: {e}")
            raise ApplicationError(f"Failed to calculate optimal order quantities: {str(e)}")
    
    async def generate_purchase_recommendations(
        self,
        business_id: uuid.UUID,
        user_id: str,
        group_by_supplier: bool = True,
        min_order_value: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Generate purchase recommendations grouped by supplier."""
        try:
            logger.info(f"Generating purchase recommendations for business {business_id}")
            
            # Validate permissions
            await self._validate_permissions(business_id, user_id, "create_purchase_order")
            
            # Get reorder suggestions
            suggestions_response = await self.get_reorder_suggestions(business_id, user_id)
            suggestions = suggestions_response['suggestions']
            
            if not group_by_supplier:
                return {
                    "recommendations": suggestions,
                    "total_items": len(suggestions),
                    "total_value": suggestions_response['total_suggested_value']
                }
            
            # Group by supplier
            supplier_recommendations = {}
            
            for suggestion in suggestions:
                supplier_id = suggestion.get('supplier_id')
                if not supplier_id:
                    continue
                
                supplier_name = suggestion.get('supplier_name', 'Unknown Supplier')
                
                if supplier_id not in supplier_recommendations:
                    supplier_recommendations[supplier_id] = {
                        "supplier_id": supplier_id,
                        "supplier_name": supplier_name,
                        "items": [],
                        "total_value": Decimal('0'),
                        "item_count": 0,
                        "lead_time_days": suggestion.get('lead_time_days', 0),
                        "priority_items": 0
                    }
                
                supplier_recommendations[supplier_id]["items"].append(suggestion)
                supplier_recommendations[supplier_id]["total_value"] += suggestion['suggested_cost']
                supplier_recommendations[supplier_id]["item_count"] += 1
                
                if suggestion['priority'] == 'high':
                    supplier_recommendations[supplier_id]["priority_items"] += 1
            
            # Filter by minimum order value if specified
            if min_order_value:
                supplier_recommendations = {
                    k: v for k, v in supplier_recommendations.items()
                    if v["total_value"] >= min_order_value
                }
            
            # Convert to list and sort by priority and value
            recommendations_list = list(supplier_recommendations.values())
            recommendations_list.sort(key=lambda x: (-x["priority_items"], -x["total_value"]))
            
            # Convert Decimal to float for JSON serialization
            for rec in recommendations_list:
                rec["total_value"] = float(rec["total_value"])
                for item in rec["items"]:
                    item["suggested_cost"] = float(item["suggested_cost"])
            
            logger.info(f"Generated purchase recommendations for {len(recommendations_list)} suppliers")
            
            return {
                "supplier_recommendations": recommendations_list,
                "total_suppliers": len(recommendations_list),
                "total_items": sum(rec["item_count"] for rec in recommendations_list),
                "total_value": sum(rec["total_value"] for rec in recommendations_list),
                "high_priority_suppliers": len([r for r in recommendations_list if r["priority_items"] > 0])
            }
            
        except Exception as e:
            logger.error(f"Error generating purchase recommendations: {e}")
            raise ApplicationError(f"Failed to generate purchase recommendations: {str(e)}")
    
    async def update_reorder_parameters(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        reorder_point: Optional[Decimal],
        reorder_quantity: Optional[Decimal],
        minimum_quantity: Optional[Decimal],
        maximum_quantity: Optional[Decimal],
        user_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """Update reorder parameters for a product."""
        try:
            logger.info(f"Updating reorder parameters for product {product_id}")
            
            # Validate permissions
            await self._validate_permissions(business_id, user_id, "manage_inventory")
            
            # Get product
            product = await self.product_repository.get_by_id(business_id, product_id)
            if not product:
                raise EntityNotFoundError(f"Product {product_id} not found")
            
            # Update parameters
            if reorder_point is not None:
                product.reorder_point = reorder_point
            if reorder_quantity is not None:
                product.reorder_quantity = reorder_quantity
            if minimum_quantity is not None:
                product.minimum_quantity = minimum_quantity
            if maximum_quantity is not None:
                product.maximum_quantity = maximum_quantity
            
            # Validate parameters
            self._validate_reorder_parameters(product)
            
            # Update product
            updated_product = await self.product_repository.update(product)
            
            logger.info(f"Successfully updated reorder parameters for product {product_id}")
            
            return {
                "success": True,
                "product_id": updated_product.id,
                "reorder_point": float(updated_product.reorder_point) if updated_product.reorder_point else None,
                "reorder_quantity": float(updated_product.reorder_quantity) if updated_product.reorder_quantity else None,
                "minimum_quantity": float(updated_product.minimum_quantity) if updated_product.minimum_quantity else None,
                "maximum_quantity": float(updated_product.maximum_quantity) if updated_product.maximum_quantity else None
            }
            
        except Exception as e:
            logger.error(f"Error updating reorder parameters: {e}")
            if isinstance(e, (DomainValidationError, BusinessRuleViolationError, EntityNotFoundError)):
                raise AppValidationError(str(e))
            raise ApplicationError(f"Failed to update reorder parameters: {str(e)}")
    
    # Helper methods
    def _generate_product_reorder_suggestion(self, product: Product) -> Dict[str, Any]:
        """Generate reorder suggestion for a specific product."""
        suggested_quantity = product.suggest_reorder_quantity() or product.reorder_quantity or Decimal('10')
        unit_cost = product.unit_cost or Decimal('0')
        suggested_cost = suggested_quantity * unit_cost
        
        return {
            "product_id": str(product.id),
            "sku": product.sku,
            "name": product.name,
            "current_stock": float(product.quantity_on_hand),
            "suggested_quantity": float(suggested_quantity),
            "unit_cost": float(unit_cost),
            "suggested_cost": suggested_cost,
            "supplier_id": str(product.primary_supplier_id) if product.primary_supplier_id else None
        }
    
    def _validate_reorder_parameters(self, product: Product) -> None:
        """Validate reorder parameters are consistent."""
        if product.reorder_point is not None and product.reorder_point < 0:
            raise BusinessRuleViolationError("Reorder point cannot be negative")
        
        if product.reorder_quantity is not None and product.reorder_quantity <= 0:
            raise BusinessRuleViolationError("Reorder quantity must be positive")
        
        if (product.minimum_quantity is not None and 
            product.maximum_quantity is not None and 
            product.minimum_quantity > product.maximum_quantity):
            raise BusinessRuleViolationError("Minimum quantity cannot be greater than maximum quantity")
        
        if (product.reorder_point is not None and 
            product.minimum_quantity is not None and 
            product.reorder_point < product.minimum_quantity):
            raise BusinessRuleViolationError("Reorder point should be at least the minimum quantity")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str, operation: str) -> None:
        """Validate user has permission for inventory operation."""
        # TODO: Implement permission checking logic based on operation
        pass 

    async def _calculate_eoq_for_product(self, product: Product, forecast_days: int) -> Dict[str, Any]:
        """Calculate Economic Order Quantity for a product."""
        # Simplified EOQ calculation
        # EOQ = sqrt((2 * demand * ordering_cost) / holding_cost)
        
        # Estimate annual demand based on historical data
        annual_demand = (product.times_sold / 90) * 365 if product.times_sold > 0 else 100
        
        # Estimate costs (these would ideally be configurable per business)
        ordering_cost = Decimal('50')  # Cost per order
        holding_cost_rate = Decimal('0.20')  # 20% of item cost per year
        unit_cost = product.unit_cost or Decimal('10')
        holding_cost_per_unit = unit_cost * holding_cost_rate
        
        # Calculate EOQ
        if holding_cost_per_unit > 0:
            eoq = (2 * annual_demand * ordering_cost / holding_cost_per_unit) ** 0.5
            eoq = Decimal(str(eoq)).quantize(Decimal('1'))
        else:
            eoq = product.reorder_quantity or Decimal('10')
        
        # Calculate potential savings
        current_order_qty = product.reorder_quantity or Decimal('10')
        current_annual_cost = (annual_demand / current_order_qty) * ordering_cost + (current_order_qty / 2) * holding_cost_per_unit
        optimal_annual_cost = (annual_demand / eoq) * ordering_cost + (eoq / 2) * holding_cost_per_unit
        potential_savings = max(Decimal('0'), current_annual_cost - optimal_annual_cost)
        
        return {
            "product_id": str(product.id),
            "sku": product.sku,
            "name": product.name,
            "current_reorder_quantity": float(current_order_qty),
            "optimal_order_quantity": float(eoq),
            "estimated_annual_demand": float(annual_demand),
            "ordering_cost": float(ordering_cost),
            "holding_cost_per_unit": float(holding_cost_per_unit),
            "current_annual_cost": float(current_annual_cost),
            "optimal_annual_cost": float(optimal_annual_cost),
            "potential_savings": potential_savings
        } 