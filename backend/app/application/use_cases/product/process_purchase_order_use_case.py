"""
Process Purchase Order Use Case

Handles purchase order creation, approval workflows, and receiving processes.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from app.domain.entities.purchase_order import PurchaseOrder, PurchaseOrderLineItem
from app.domain.entities.product import Product
from app.domain.repositories.purchase_order_repository import PurchaseOrderRepository
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.supplier_repository import SupplierRepository
from app.domain.enums import PurchaseOrderStatus
from app.domain.exceptions.domain_exceptions import (
    DomainValidationError, BusinessRuleViolationError, EntityNotFoundError
)
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class ProcessPurchaseOrderUseCase:
    """Use case for processing purchase orders."""
    
    def __init__(
        self,
        purchase_order_repository: PurchaseOrderRepository,
        product_repository: ProductRepository,
        supplier_repository: SupplierRepository
    ):
        self.purchase_order_repository = purchase_order_repository
        self.product_repository = product_repository
        self.supplier_repository = supplier_repository
    
    async def create_purchase_order(
        self,
        supplier_id: uuid.UUID,
        line_items: List[Dict[str, Any]],
        user_id: str,
        business_id: uuid.UUID,
        notes: Optional[str] = None,
        reference_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new purchase order."""
        try:
            logger.info(f"Creating purchase order for supplier {supplier_id} by user {user_id}")
            
            # Validate permissions
            await self._validate_permissions(business_id, user_id, "create_purchase_order")
            
            # Validate supplier
            supplier = await self._get_and_validate_supplier(supplier_id, business_id)
            
            # Generate PO number if not provided
            po_number = reference_number or await self._generate_po_number(business_id)
            
            # Validate and create line items
            validated_line_items = await self._validate_and_create_line_items(line_items, business_id)
            
            # Calculate totals
            subtotal = sum(item.calculate_line_total() for item in validated_line_items)
            tax_amount = Decimal('0')  # TODO: Calculate tax based on supplier settings
            total_amount = subtotal + tax_amount
            
            # Create purchase order
            purchase_order = PurchaseOrder(
                id=uuid.uuid4(),
                business_id=business_id,
                po_number=po_number,
                supplier_id=supplier_id,
                supplier_name=supplier.company_name,
                status=PurchaseOrderStatus.DRAFT,
                line_items=validated_line_items,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                notes=notes,
                order_date=datetime.utcnow(),
                created_by=user_id,
                created_date=datetime.utcnow(),
                last_modified=datetime.utcnow()
            )
            
            # Save purchase order
            created_po = await self.purchase_order_repository.create(purchase_order)
            
            logger.info(f"Successfully created purchase order {created_po.id} with number {created_po.po_number}")
            
            return {
                "success": True,
                "purchase_order_id": created_po.id,
                "po_number": created_po.po_number,
                "status": created_po.status.value,
                "total_amount": float(created_po.total_amount),
                "line_items_count": len(created_po.line_items)
            }
            
        except Exception as e:
            logger.error(f"Error creating purchase order: {e}")
            if isinstance(e, (DomainValidationError, BusinessRuleViolationError, EntityNotFoundError)):
                raise AppValidationError(str(e))
            raise ApplicationError(f"Failed to create purchase order: {str(e)}")
    
    async def approve_purchase_order(
        self,
        purchase_order_id: uuid.UUID,
        user_id: str,
        business_id: uuid.UUID,
        approval_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Approve a purchase order."""
        try:
            logger.info(f"Approving purchase order {purchase_order_id} by user {user_id}")
            
            # Validate permissions
            await self._validate_permissions(business_id, user_id, "approve_purchase_order")
            
            # Get purchase order
            po = await self.purchase_order_repository.get_by_id(business_id, purchase_order_id)
            if not po:
                raise EntityNotFoundError(f"Purchase order {purchase_order_id} not found")
            
            # Validate can approve
            if po.status != PurchaseOrderStatus.DRAFT:
                raise BusinessRuleViolationError(f"Cannot approve purchase order in {po.status.value} status")
            
            # Update status and approval info
            po.status = PurchaseOrderStatus.APPROVED
            po.approved_by = user_id
            po.approved_date = datetime.utcnow()
            if approval_notes:
                po.notes = f"{po.notes}\n\nApproval Notes: {approval_notes}" if po.notes else f"Approval Notes: {approval_notes}"
            
            # Save updated purchase order
            updated_po = await self.purchase_order_repository.update(po)
            
            logger.info(f"Successfully approved purchase order {purchase_order_id}")
            
            return {
                "success": True,
                "purchase_order_id": updated_po.id,
                "status": updated_po.status.value,
                "approved_by": updated_po.approved_by,
                "approved_date": updated_po.approved_date.isoformat() if updated_po.approved_date else None
            }
            
        except Exception as e:
            logger.error(f"Error approving purchase order: {e}")
            if isinstance(e, (DomainValidationError, BusinessRuleViolationError, EntityNotFoundError)):
                raise AppValidationError(str(e))
            raise ApplicationError(f"Failed to approve purchase order: {str(e)}")
    
    async def send_purchase_order(
        self,
        purchase_order_id: uuid.UUID,
        user_id: str,
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Send approved purchase order to supplier."""
        try:
            logger.info(f"Sending purchase order {purchase_order_id} by user {user_id}")
            
            # Validate permissions
            await self._validate_permissions(business_id, user_id, "send_purchase_order")
            
            # Get purchase order
            po = await self.purchase_order_repository.get_by_id(business_id, purchase_order_id)
            if not po:
                raise EntityNotFoundError(f"Purchase order {purchase_order_id} not found")
            
            # Validate can send
            if po.status != PurchaseOrderStatus.APPROVED:
                raise BusinessRuleViolationError(f"Cannot send purchase order in {po.status.value} status")
            
            # Update status
            po.status = PurchaseOrderStatus.SENT
            po.sent_date = datetime.utcnow()
            po.sent_by = user_id
            
            # Save updated purchase order
            updated_po = await self.purchase_order_repository.update(po)
            
            # TODO: Send email/notification to supplier
            
            logger.info(f"Successfully sent purchase order {purchase_order_id}")
            
            return {
                "success": True,
                "purchase_order_id": updated_po.id,
                "status": updated_po.status.value,
                "sent_date": updated_po.sent_date.isoformat() if updated_po.sent_date else None
            }
            
        except Exception as e:
            logger.error(f"Error sending purchase order: {e}")
            if isinstance(e, (DomainValidationError, BusinessRuleViolationError, EntityNotFoundError)):
                raise AppValidationError(str(e))
            raise ApplicationError(f"Failed to send purchase order: {str(e)}")
    
    async def receive_purchase_order(
        self,
        purchase_order_id: uuid.UUID,
        received_items: List[Dict[str, Any]],
        user_id: str,
        business_id: uuid.UUID,
        partial_receipt: bool = False,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Receive items from purchase order."""
        try:
            logger.info(f"Receiving items for purchase order {purchase_order_id} by user {user_id}")
            
            # Validate permissions
            await self._validate_permissions(business_id, user_id, "receive_purchase_order")
            
            # Get purchase order
            po = await self.purchase_order_repository.get_by_id(business_id, purchase_order_id)
            if not po:
                raise EntityNotFoundError(f"Purchase order {purchase_order_id} not found")
            
            # Validate can receive
            if po.status not in [PurchaseOrderStatus.SENT, PurchaseOrderStatus.CONFIRMED, PurchaseOrderStatus.PARTIAL]:
                raise BusinessRuleViolationError(f"Cannot receive purchase order in {po.status.value} status")
            
            # Process received items
            total_received_value = Decimal('0')
            items_updated = 0
            
            for received_item in received_items:
                line_item_id = uuid.UUID(received_item['line_item_id'])
                quantity_received = Decimal(str(received_item['quantity_received']))
                
                # Find the line item
                line_item = next((item for item in po.line_items if item.id == line_item_id), None)
                if not line_item:
                    continue
                
                # Validate received quantity
                if quantity_received <= 0:
                    continue
                
                if line_item.quantity_received + quantity_received > line_item.quantity_ordered:
                    raise BusinessRuleViolationError(
                        f"Cannot receive more than ordered for item {line_item.product_name}"
                    )
                
                # Update line item
                line_item.quantity_received += quantity_received
                line_item.quantity_pending = line_item.quantity_ordered - line_item.quantity_received
                
                # Update product inventory
                await self.product_repository.update_quantity(
                    business_id, line_item.product_id, quantity_received
                )
                
                # Update product cost if needed
                await self.product_repository.update_cost(
                    business_id, line_item.product_id, line_item.unit_cost, quantity_received
                )
                
                total_received_value += quantity_received * line_item.unit_cost
                items_updated += 1
            
            # Update purchase order status
            all_received = all(item.quantity_received >= item.quantity_ordered for item in po.line_items)
            any_received = any(item.quantity_received > 0 for item in po.line_items)
            
            if all_received:
                po.status = PurchaseOrderStatus.RECEIVED
                po.received_date = datetime.utcnow()
            elif any_received:
                po.status = PurchaseOrderStatus.PARTIAL
            
            po.last_received_date = datetime.utcnow()
            po.received_by = user_id
            if notes:
                po.notes = f"{po.notes}\n\nReceiving Notes: {notes}" if po.notes else f"Receiving Notes: {notes}"
            
            # Save updated purchase order
            updated_po = await self.purchase_order_repository.update(po)
            
            logger.info(f"Successfully received items for purchase order {purchase_order_id}")
            
            return {
                "success": True,
                "purchase_order_id": updated_po.id,
                "status": updated_po.status.value,
                "items_updated": items_updated,
                "total_received_value": float(total_received_value),
                "is_complete": all_received
            }
            
        except Exception as e:
            logger.error(f"Error receiving purchase order: {e}")
            if isinstance(e, (DomainValidationError, BusinessRuleViolationError, EntityNotFoundError)):
                raise AppValidationError(str(e))
            raise ApplicationError(f"Failed to receive purchase order: {str(e)}")
    
    # Helper methods
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str, operation: str) -> None:
        """Validate user has permission for purchase order operation."""
        # TODO: Implement permission checking logic based on operation
        pass
    
    async def _get_and_validate_supplier(self, supplier_id: uuid.UUID, business_id: uuid.UUID):
        """Get and validate supplier."""
        supplier = await self.supplier_repository.get_by_id(business_id, supplier_id)
        if not supplier:
            raise EntityNotFoundError(f"Supplier {supplier_id} not found")
        
        if not supplier.is_active:
            raise BusinessRuleViolationError("Supplier is not active")
        
        return supplier
    
    async def _generate_po_number(self, business_id: uuid.UUID) -> str:
        """Generate unique purchase order number."""
        return await self.purchase_order_repository.get_next_po_number(business_id, "PO")
    
    async def _validate_and_create_line_items(
        self, 
        line_items_data: List[Dict[str, Any]], 
        business_id: uuid.UUID
    ) -> List[PurchaseOrderLineItem]:
        """Validate and create purchase order line items."""
        line_items = []
        
        for item_data in line_items_data:
            product_id = uuid.UUID(item_data['product_id'])
            quantity = Decimal(str(item_data['quantity']))
            unit_cost = Decimal(str(item_data['unit_cost']))
            
            # Validate product
            product = await self.product_repository.get_by_id(business_id, product_id)
            if not product:
                raise EntityNotFoundError(f"Product {product_id} not found")
            
            # Create line item
            line_item = PurchaseOrderLineItem(
                id=uuid.uuid4(),
                product_id=product_id,
                product_sku=product.sku,
                product_name=product.name,
                description=item_data.get('description', ''),
                quantity_ordered=quantity,
                unit_cost=unit_cost,
                discount_percentage=Decimal(str(item_data.get('discount_percentage', 0))),
                tax_rate=Decimal(str(item_data.get('tax_rate', 0))),
                unit_of_measure=product.unit_of_measure.value
            )
            
            line_items.append(line_item)
        
        if not line_items:
            raise BusinessRuleViolationError("Purchase order must have at least one line item")
        
        return line_items 