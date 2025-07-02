"""
Manage Inventory Use Case

Handles stock movements, adjustments, and comprehensive inventory management operations.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from app.domain.entities.product import Product
from app.domain.entities.stock_movement import StockMovement, StockMovementContext
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.stock_movement_repository import StockMovementRepository
from app.domain.enums import StockMovementType
from app.domain.exceptions.domain_exceptions import (
    DomainValidationError, BusinessRuleViolationError, EntityNotFoundError
)
from app.application.dto.product_dto import StockAdjustmentDTO, ProductDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class ManageInventoryUseCase:
    """Use case for managing inventory operations."""
    
    def __init__(
        self,
        product_repository: ProductRepository,
        stock_movement_repository: StockMovementRepository
    ):
        self.product_repository = product_repository
        self.stock_movement_repository = stock_movement_repository
    
    async def adjust_stock(
        self, 
        adjustment: StockAdjustmentDTO, 
        user_id: str, 
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Execute stock adjustment with full audit trail."""
        try:
            logger.info(f"Processing stock adjustment for product {adjustment.product_id} by user {user_id}")
            
            # Validate permissions
            await self._validate_permissions(business_id, user_id, "adjust_inventory")
            
            # Get and validate product
            product = await self._get_and_validate_product(adjustment.product_id, business_id)
            
            # Validate adjustment
            self._validate_stock_adjustment(product, adjustment)
            
            # Calculate before/after quantities
            quantity_before = product.quantity_on_hand
            quantity_after = quantity_before + adjustment.quantity_change
            
            # Ensure stock doesn't go negative
            if quantity_after < 0:
                raise BusinessRuleViolationError(
                    f"Adjustment would result in negative stock. "
                    f"Current: {quantity_before}, Change: {adjustment.quantity_change}"
                )
            
            # Create stock movement record
            movement = StockMovement(
                id=uuid.uuid4(),
                business_id=business_id,
                product_id=adjustment.product_id,
                movement_type=StockMovementType.ADJUSTMENT,
                quantity=adjustment.quantity_change,
                unit_cost=product.unit_cost,
                quantity_before=quantity_before,
                quantity_after=quantity_after,
                cost_before=product.unit_cost,
                cost_after=product.unit_cost,
                context=StockMovementContext(
                    reference_number=adjustment.reference_number
                ),
                reason=adjustment.adjustment_reason,
                notes=adjustment.notes,
                movement_date=datetime.utcnow(),
                created_by=user_id,
                is_approved=True
            )
            
            # Calculate total cost
            movement.total_cost = movement.calculate_total_cost()
            
            # Update product quantities
            await self.product_repository.update_quantity(
                business_id, adjustment.product_id, adjustment.quantity_change
            )
            
            # Save stock movement
            await self.stock_movement_repository.create(movement)
            
            # Get updated product
            updated_product = await self.product_repository.get_by_id(business_id, adjustment.product_id)
            
            logger.info(f"Successfully processed stock adjustment for product {adjustment.product_id}")
            
            return {
                "success": True,
                "movement_id": movement.id,
                "quantity_before": float(quantity_before),
                "quantity_after": float(quantity_after),
                "quantity_change": float(adjustment.quantity_change),
                "product": ProductDTO.from_entity(updated_product) if updated_product else None
            }
            
        except Exception as e:
            logger.error(f"Error processing stock adjustment: {e}")
            if isinstance(e, (DomainValidationError, BusinessRuleViolationError, EntityNotFoundError)):
                raise AppValidationError(str(e))
            raise ApplicationError(f"Failed to process stock adjustment: {str(e)}")
    
    async def transfer_stock(
        self,
        product_id: uuid.UUID,
        from_location_id: uuid.UUID,
        to_location_id: uuid.UUID,
        quantity: Decimal,
        reason: str,
        user_id: str,
        business_id: uuid.UUID,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transfer stock between locations."""
        try:
            logger.info(f"Processing stock transfer for product {product_id} from {from_location_id} to {to_location_id}")
            
            # Validate permissions
            await self._validate_permissions(business_id, user_id, "transfer_inventory")
            
            # Get and validate product
            product = await self._get_and_validate_product(product_id, business_id)
            
            # Validate transfer quantity
            if quantity <= 0:
                raise BusinessRuleViolationError("Transfer quantity must be positive")
            
            # Check if sufficient stock available at source location
            if not await self._check_location_availability(product_id, from_location_id, quantity):
                raise BusinessRuleViolationError(f"Insufficient stock at source location")
            
            # Create stock movement record
            movement = StockMovement(
                id=uuid.uuid4(),
                business_id=business_id,
                product_id=product_id,
                movement_type=StockMovementType.TRANSFER,
                quantity=Decimal('0'),  # Net quantity change is zero for transfers
                unit_cost=product.unit_cost,
                quantity_before=product.quantity_on_hand,
                quantity_after=product.quantity_on_hand,
                cost_before=product.unit_cost,
                cost_after=product.unit_cost,
                from_location_id=from_location_id,
                to_location_id=to_location_id,
                reason=reason,
                notes=notes,
                movement_date=datetime.utcnow(),
                created_by=user_id,
                is_approved=True
            )
            
            # Execute the transfer
            await self.product_repository.transfer_between_locations(
                business_id, product_id, from_location_id, to_location_id, quantity
            )
            
            # Save stock movement
            await self.stock_movement_repository.create(movement)
            
            logger.info(f"Successfully transferred {quantity} units of product {product_id}")
            
            return {
                "success": True,
                "movement_id": movement.id,
                "quantity_transferred": float(quantity),
                "from_location_id": str(from_location_id),
                "to_location_id": str(to_location_id)
            }
            
        except Exception as e:
            logger.error(f"Error processing stock transfer: {e}")
            if isinstance(e, (DomainValidationError, BusinessRuleViolationError, EntityNotFoundError)):
                raise AppValidationError(str(e))
            raise ApplicationError(f"Failed to process stock transfer: {str(e)}")
    
    async def receive_purchase(
        self,
        product_id: uuid.UUID,
        quantity: Decimal,
        unit_cost: Decimal,
        supplier_id: Optional[uuid.UUID],
        purchase_order_id: Optional[uuid.UUID],
        invoice_number: Optional[str],
        user_id: str,
        business_id: uuid.UUID,
        additional_costs: Optional[Dict[str, Decimal]] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Receive purchased inventory."""
        try:
            logger.info(f"Processing purchase receipt for product {product_id}, quantity {quantity}")
            
            # Validate permissions
            await self._validate_permissions(business_id, user_id, "receive_inventory")
            
            # Get and validate product
            product = await self._get_and_validate_product(product_id, business_id)
            
            # Validate purchase data
            if quantity <= 0:
                raise BusinessRuleViolationError("Purchase quantity must be positive")
            if unit_cost < 0:
                raise BusinessRuleViolationError("Unit cost cannot be negative")
            
            # Calculate costs
            shipping_cost = additional_costs.get('shipping', Decimal('0')) if additional_costs else Decimal('0')
            duty_cost = additional_costs.get('duty', Decimal('0')) if additional_costs else Decimal('0')
            other_costs = additional_costs.get('other', Decimal('0')) if additional_costs else Decimal('0')
            
            # Calculate before/after quantities and costs
            quantity_before = product.quantity_on_hand
            quantity_after = quantity_before + quantity
            cost_before = product.unit_cost
            
            # Update average cost if using weighted average
            new_average_cost = cost_before
            if product.costing_method.value == "weighted_average":
                if quantity_before > 0:
                    total_cost_before = quantity_before * cost_before
                    total_cost_added = (quantity * unit_cost) + shipping_cost + duty_cost + other_costs
                    new_average_cost = (total_cost_before + total_cost_added) / quantity_after
                else:
                    new_average_cost = unit_cost
            
            # Create stock movement record
            movement = StockMovement(
                id=uuid.uuid4(),
                business_id=business_id,
                product_id=product_id,
                movement_type=StockMovementType.PURCHASE,
                quantity=quantity,
                unit_cost=unit_cost,
                total_cost=quantity * unit_cost,
                quantity_before=quantity_before,
                quantity_after=quantity_after,
                cost_before=cost_before,
                cost_after=new_average_cost,
                context=StockMovementContext(
                    reference_type="purchase_order" if purchase_order_id else "invoice",
                    reference_id=purchase_order_id,
                    reference_number=invoice_number
                ),
                supplier_id=supplier_id,
                supplier_invoice_number=invoice_number,
                shipping_cost=shipping_cost,
                duty_cost=duty_cost,
                other_costs=other_costs,
                notes=notes,
                movement_date=datetime.utcnow(),
                created_by=user_id,
                is_approved=True
            )
            
            # Calculate landed cost
            movement.landed_cost = movement.calculate_landed_cost()
            
            # Update product quantities and cost
            await self.product_repository.update_quantity(business_id, product_id, quantity)
            await self.product_repository.update_cost(business_id, product_id, unit_cost, quantity)
            
            # Save stock movement
            await self.stock_movement_repository.create(movement)
            
            # Get updated product
            updated_product = await self.product_repository.get_by_id(business_id, product_id)
            
            logger.info(f"Successfully received purchase for product {product_id}")
            
            return {
                "success": True,
                "movement_id": movement.id,
                "quantity_received": float(quantity),
                "unit_cost": float(unit_cost),
                "landed_cost": float(movement.landed_cost),
                "new_average_cost": float(new_average_cost),
                "product": ProductDTO.from_entity(updated_product) if updated_product else None
            }
            
        except Exception as e:
            logger.error(f"Error processing purchase receipt: {e}")
            if isinstance(e, (DomainValidationError, BusinessRuleViolationError, EntityNotFoundError)):
                raise AppValidationError(str(e))
            raise ApplicationError(f"Failed to process purchase receipt: {str(e)}")
    
    async def reserve_stock(
        self,
        product_id: uuid.UUID,
        quantity: Decimal,
        reference_id: uuid.UUID,
        reference_type: str,
        user_id: str,
        business_id: uuid.UUID,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reserve stock for orders/estimates."""
        try:
            logger.info(f"Reserving {quantity} units of product {product_id} for {reference_type} {reference_id}")
            
            # Validate permissions
            await self._validate_permissions(business_id, user_id, "reserve_inventory")
            
            # Get and validate product
            product = await self._get_and_validate_product(product_id, business_id)
            
            # Validate reservation
            if quantity <= 0:
                raise BusinessRuleViolationError("Reservation quantity must be positive")
            
            if product.quantity_available < quantity:
                raise BusinessRuleViolationError(
                    f"Insufficient available stock. Available: {product.quantity_available}, Requested: {quantity}"
                )
            
            # Reserve the quantity
            success = await self.product_repository.reserve_quantity(business_id, product_id, quantity)
            
            if not success:
                raise ApplicationError("Failed to reserve stock")
            
            logger.info(f"Successfully reserved {quantity} units of product {product_id}")
            
            return {
                "success": True,
                "quantity_reserved": float(quantity),
                "remaining_available": float(product.quantity_available - quantity)
            }
            
        except Exception as e:
            logger.error(f"Error reserving stock: {e}")
            if isinstance(e, (DomainValidationError, BusinessRuleViolationError, EntityNotFoundError)):
                raise AppValidationError(str(e))
            raise ApplicationError(f"Failed to reserve stock: {str(e)}")
    
    async def release_reservation(
        self,
        product_id: uuid.UUID,
        quantity: Decimal,
        reference_id: uuid.UUID,
        reference_type: str,
        user_id: str,
        business_id: uuid.UUID,
        reason: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Release reserved stock."""
        try:
            logger.info(f"Releasing {quantity} units of product {product_id} from {reference_type} {reference_id}")
            
            # Validate permissions
            await self._validate_permissions(business_id, user_id, "reserve_inventory")
            
            # Get and validate product
            product = await self._get_and_validate_product(product_id, business_id)
            
            # Validate release
            if quantity <= 0:
                raise BusinessRuleViolationError("Release quantity must be positive")
            
            if product.quantity_reserved < quantity:
                raise BusinessRuleViolationError(
                    f"Cannot release more than reserved. Reserved: {product.quantity_reserved}, Requested: {quantity}"
                )
            
            # Release the reservation
            success = await self.product_repository.release_reservation(business_id, product_id, quantity)
            
            if not success:
                raise ApplicationError("Failed to release reservation")
            
            # Create stock movement record for audit
            movement = StockMovement(
                id=uuid.uuid4(),
                business_id=business_id,
                product_id=product_id,
                movement_type=StockMovementType.RELEASE,
                quantity=Decimal('0'),  # No actual quantity change
                unit_cost=product.unit_cost,
                quantity_before=product.quantity_on_hand,
                quantity_after=product.quantity_on_hand,
                cost_before=product.unit_cost,
                cost_after=product.unit_cost,
                context=StockMovementContext(
                    reference_type=reference_type,
                    reference_id=reference_id
                ),
                reason=reason,
                notes=notes,
                movement_date=datetime.utcnow(),
                created_by=user_id,
                is_approved=True
            )
            
            # Save stock movement
            await self.stock_movement_repository.create(movement)
            
            logger.info(f"Successfully released {quantity} units of product {product_id}")
            
            return {
                "success": True,
                "movement_id": movement.id,
                "quantity_released": float(quantity),
                "remaining_reserved": float(product.quantity_reserved - quantity)
            }
            
        except Exception as e:
            logger.error(f"Error releasing reservation: {e}")
            if isinstance(e, (DomainValidationError, BusinessRuleViolationError, EntityNotFoundError)):
                raise AppValidationError(str(e))
            raise ApplicationError(f"Failed to release reservation: {str(e)}")
    
    # Helper methods
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str, operation: str) -> None:
        """Validate user has permission for inventory operation."""
        # TODO: Implement permission checking logic based on operation
        # For now, we assume all authenticated users can perform inventory operations
        pass
    
    async def _get_and_validate_product(self, product_id: uuid.UUID, business_id: uuid.UUID) -> Product:
        """Get and validate product exists and belongs to business."""
        product = await self.product_repository.get_by_id(business_id, product_id)
        if not product:
            raise EntityNotFoundError(f"Product with ID {product_id} not found")
        return product
    
    def _validate_stock_adjustment(self, product: Product, adjustment: StockAdjustmentDTO) -> None:
        """Validate stock adjustment parameters."""
        if not product.track_inventory:
            raise BusinessRuleViolationError("Cannot adjust stock for products with inventory tracking disabled")
        
        if adjustment.quantity_change == 0:
            raise BusinessRuleViolationError("Stock adjustment quantity cannot be zero")
        
        if not adjustment.adjustment_reason or adjustment.adjustment_reason.strip() == "":
            raise BusinessRuleViolationError("Stock adjustment reason is required")
    
    async def _check_location_availability(
        self, 
        product_id: uuid.UUID, 
        location_id: uuid.UUID, 
        quantity: Decimal
    ) -> bool:
        """Check if sufficient stock is available at location."""
        # TODO: Implement location-specific stock checking
        # For now, return True as multi-location is not fully implemented
        return True 