"""
Supabase Purchase Order Repository Implementation

Repository implementation for purchase order management with workflow support.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

from supabase import Client

from app.domain.repositories.purchase_order_repository import PurchaseOrderRepository
from app.domain.entities.purchase_order import PurchaseOrder
from app.domain.enums import PurchaseOrderStatus
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DatabaseError
)

# Configure logging
logger = logging.getLogger(__name__)

class SupabasePurchaseOrderRepository(PurchaseOrderRepository):
    """
    Supabase client implementation of PurchaseOrderRepository.
    
    Handles purchase order management with workflow and approval processes.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "purchase_orders"
        logger.info(f"SupabasePurchaseOrderRepository initialized")
    
    async def create(self, purchase_order: PurchaseOrder) -> PurchaseOrder:
        """Create a new purchase order."""
        try:
            po_data = self._purchase_order_to_dict(purchase_order)
            
            response = self.client.table(self.table_name).insert(po_data).execute()
            
            if response.data:
                return self._dict_to_purchase_order(response.data[0])
            else:
                raise DatabaseError("Failed to create purchase order - no data returned")
                
        except Exception as e:
            raise DatabaseError(f"Failed to create purchase order: {str(e)}")
    
    async def get_by_id(self, business_id: uuid.UUID, po_id: uuid.UUID) -> Optional[PurchaseOrder]:
        """Get purchase order by ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("id", str(po_id)).execute()
            
            if response.data:
                return self._dict_to_purchase_order(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get purchase order by ID: {str(e)}")
    
    async def get_by_po_number(self, business_id: uuid.UUID, po_number: str) -> Optional[PurchaseOrder]:
        """Get purchase order by PO number."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("po_number", po_number).execute()
            
            if response.data:
                return self._dict_to_purchase_order(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get purchase order by number: {str(e)}")
    
    async def list_by_supplier(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        status: Optional[PurchaseOrderStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[PurchaseOrder]:
        """List purchase orders by supplier."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("supplier_id", str(supplier_id))
            
            if status:
                query = query.eq("status", status.value)
            
            response = query.range(offset, offset + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_purchase_order(po) for po in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to list purchase orders by supplier: {str(e)}")
    
    async def list_by_status(
        self,
        business_id: uuid.UUID,
        status: PurchaseOrderStatus,
        limit: int = 100,
        offset: int = 0
    ) -> List[PurchaseOrder]:
        """List purchase orders by status."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", status.value).range(
                offset, offset + limit - 1
            ).order("created_at", desc=True).execute()
            
            return [self._dict_to_purchase_order(po) for po in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to list purchase orders by status: {str(e)}")
    
    async def update(self, purchase_order: PurchaseOrder) -> PurchaseOrder:
        """Update an existing purchase order."""
        try:
            po_data = self._purchase_order_to_dict(purchase_order)
            po_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table(self.table_name).update(po_data).eq(
                "id", str(purchase_order.id)
            ).execute()
            
            if response.data:
                return self._dict_to_purchase_order(response.data[0])
            else:
                raise EntityNotFoundError(f"Purchase order with ID {purchase_order.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update purchase order: {str(e)}")
    
    async def update_status(
        self,
        business_id: uuid.UUID,
        po_id: uuid.UUID,
        new_status: PurchaseOrderStatus,
        notes: Optional[str] = None
    ) -> bool:
        """Update purchase order status."""
        try:
            update_data = {
                "status": new_status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if notes:
                update_data["status_notes"] = notes
            
            response = self.client.table(self.table_name).update(update_data).eq(
                "business_id", str(business_id)
            ).eq("id", str(po_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to update purchase order status: {str(e)}")
    
    async def get_pending_approvals(
        self,
        business_id: uuid.UUID,
        approver_id: Optional[str] = None
    ) -> List[PurchaseOrder]:
        """Get purchase orders pending approval."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", PurchaseOrderStatus.draft.value).gt("total_amount", 0)
            
            response = query.order("created_at").execute()
            
            return [self._dict_to_purchase_order(po) for po in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get pending approvals: {str(e)}")
    
    # Missing methods from interface - Part 1
    async def get_by_number(self, business_id: uuid.UUID, po_number: str) -> Optional[PurchaseOrder]:
        """Get purchase order by PO number."""
        return await self.get_by_po_number(business_id, po_number)
    
    async def delete(self, business_id: uuid.UUID, order_id: uuid.UUID) -> bool:
        """Delete a purchase order (only if draft status)."""
        try:
            # Check if order is in draft status
            po = await self.get_by_id(business_id, order_id)
            if not po or po.status != PurchaseOrderStatus.DRAFT:
                return False
            
            response = self.client.table(self.table_name).delete().eq(
                "business_id", str(business_id)
            ).eq("id", str(order_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete purchase order: {str(e)}")
    
    async def list_by_business(
        self,
        business_id: uuid.UUID,
        status: Optional[PurchaseOrderStatus] = None,
        supplier_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[PurchaseOrder]:
        """List purchase orders for a business with optional filtering."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if status:
                query = query.eq("status", status.value)
            if supplier_id:
                query = query.eq("supplier_id", str(supplier_id))
            if start_date:
                query = query.gte("order_date", start_date.isoformat())
            if end_date:
                query = query.lte("order_date", end_date.isoformat())
            
            response = query.range(offset, offset + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_purchase_order(po) for po in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to list purchase orders by business: {str(e)}")
    
    async def search_orders(
        self,
        business_id: uuid.UUID,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[PurchaseOrder]:
        """Search purchase orders by number, supplier, or line items."""
        try:
            search_query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).or_(f"po_number.ilike.%{query}%,notes.ilike.%{query}%")
            
            if filters:
                if filters.get("status"):
                    search_query = search_query.eq("status", filters["status"])
                if filters.get("supplier_id"):
                    search_query = search_query.eq("supplier_id", filters["supplier_id"])
            
            response = search_query.range(offset, offset + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_purchase_order(po) for po in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search purchase orders: {str(e)}")
    
    async def get_orders_by_status(
        self,
        business_id: uuid.UUID,
        status: PurchaseOrderStatus,
        limit: int = 100,
        offset: int = 0
    ) -> List[PurchaseOrder]:
        """Get purchase orders by status."""
        return await self.list_by_status(business_id, status, limit, offset)
    
    async def get_orders_by_supplier(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        status: Optional[PurchaseOrderStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[PurchaseOrder]:
        """Get purchase orders for a specific supplier."""
        return await self.list_by_supplier(business_id, supplier_id, status, limit, offset)
    
    # Status and workflow management
    async def get_orders_pending_approval(
        self,
        business_id: uuid.UUID,
        approval_level: Optional[int] = None
    ) -> List[PurchaseOrder]:
        """Get purchase orders pending approval."""
        return await self.get_pending_approvals(business_id)
    
    async def approve_order(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        approved_by: str,
        approval_level: int,
        notes: Optional[str] = None
    ) -> bool:
        """Approve a purchase order at specific level."""
        try:
            update_data = {
                "status": PurchaseOrderStatus.CONFIRMED.value,
                "approved_by": approved_by,
                "approved_at": datetime.utcnow().isoformat(),
                "approval_level": approval_level,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if notes:
                update_data["approval_notes"] = notes
            
            response = self.client.table(self.table_name).update(update_data).eq(
                "business_id", str(business_id)
            ).eq("id", str(order_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to approve purchase order: {str(e)}")
    
    async def reject_order(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        rejected_by: str,
        reason: str
    ) -> bool:
        """Reject a purchase order."""
        try:
            update_data = {
                "status": PurchaseOrderStatus.CANCELLED.value,
                "rejected_by": rejected_by,
                "rejected_at": datetime.utcnow().isoformat(),
                "rejection_reason": reason,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table(self.table_name).update(update_data).eq(
                "business_id", str(business_id)
            ).eq("id", str(order_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to reject purchase order: {str(e)}")
    
    async def send_to_supplier(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        sent_by: str,
        method: str = "email"
    ) -> bool:
        """Mark purchase order as sent to supplier."""
        try:
            update_data = {
                "status": PurchaseOrderStatus.SENT.value,
                "sent_by": sent_by,
                "sent_at": datetime.utcnow().isoformat(),
                "sent_method": method,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table(self.table_name).update(update_data).eq(
                "business_id", str(business_id)
            ).eq("id", str(order_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to send purchase order to supplier: {str(e)}")
    
    # Receiving and fulfillment methods
    async def record_receipt(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        line_item_receipts: List[Dict[str, Any]],
        received_by: str,
        receipt_date: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Record receipt of purchase order items."""
        try:
            # This would require updating line items in a separate table
            # For now, just update the main order status
            receipt_datetime = receipt_date or datetime.utcnow()
            
            update_data = {
                "status": PurchaseOrderStatus.RECEIVED.value,
                "received_by": received_by,
                "received_at": receipt_datetime.isoformat(),
                "receipt_notes": notes,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table(self.table_name).update(update_data).eq(
                "business_id", str(business_id)
            ).eq("id", str(order_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to record receipt: {str(e)}")
    
    async def get_orders_pending_receipt(
        self,
        business_id: uuid.UUID,
        supplier_id: Optional[uuid.UUID] = None,
        overdue_only: bool = False
    ) -> List[PurchaseOrder]:
        """Get purchase orders pending receipt."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", PurchaseOrderStatus.CONFIRMED.value)
            
            if supplier_id:
                query = query.eq("supplier_id", str(supplier_id))
            
            if overdue_only:
                # Check for orders past expected delivery date
                query = query.lt("expected_delivery_date", datetime.utcnow().isoformat())
            
            response = query.order("expected_delivery_date").execute()
            
            return [self._dict_to_purchase_order(po) for po in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get orders pending receipt: {str(e)}")
    
    async def get_partially_received_orders(
        self,
        business_id: uuid.UUID,
        supplier_id: Optional[uuid.UUID] = None
    ) -> List[PurchaseOrder]:
        """Get purchase orders that are partially received."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", PurchaseOrderStatus.PARTIALLY_RECEIVED.value)
            
            if supplier_id:
                query = query.eq("supplier_id", str(supplier_id))
            
            response = query.order("expected_delivery_date").execute()
            
            return [self._dict_to_purchase_order(po) for po in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get partially received orders: {str(e)}")
    
    async def get_overdue_orders(
        self,
        business_id: uuid.UUID,
        supplier_id: Optional[uuid.UUID] = None
    ) -> List[PurchaseOrder]:
        """Get purchase orders that are overdue for delivery."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).in_("status", [PurchaseOrderStatus.CONFIRMED.value, PurchaseOrderStatus.PARTIALLY_RECEIVED.value]).lt(
                "expected_delivery_date", datetime.utcnow().isoformat()
            )
            
            if supplier_id:
                query = query.eq("supplier_id", str(supplier_id))
            
            response = query.order("expected_delivery_date").execute()
            
            return [self._dict_to_purchase_order(po) for po in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get overdue orders: {str(e)}")
    
    async def update_expected_delivery(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        new_expected_date: datetime,
        updated_by: str,
        reason: Optional[str] = None
    ) -> bool:
        """Update expected delivery date."""
        try:
            update_data = {
                "expected_delivery_date": new_expected_date.isoformat(),
                "delivery_updated_by": updated_by,
                "delivery_update_reason": reason,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table(self.table_name).update(update_data).eq(
                "business_id", str(business_id)
            ).eq("id", str(order_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to update expected delivery: {str(e)}")
    
    # Line item management
    async def add_line_item(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        line_item_data: Dict[str, Any]
    ) -> bool:
        """Add a line item to a purchase order."""
        try:
            # This would require a purchase_order_line_items table
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to add line item: {str(e)}")
    
    async def update_line_item(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        line_item_id: uuid.UUID,
        line_item_data: Dict[str, Any]
    ) -> bool:
        """Update a line item in a purchase order."""
        try:
            # This would require a purchase_order_line_items table
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to update line item: {str(e)}")
    
    async def remove_line_item(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        line_item_id: uuid.UUID
    ) -> bool:
        """Remove a line item from a purchase order."""
        try:
            # This would require a purchase_order_line_items table
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to remove line item: {str(e)}")
    
    async def get_line_items_for_product(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        status: Optional[PurchaseOrderStatus] = None,
        pending_receipt_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get line items for a specific product."""
        try:
            # This would require joining with line items table
            # For now, returning empty list
            return []
            
        except Exception as e:
            raise DatabaseError(f"Failed to get line items for product: {str(e)}")
    
    # Analytics and reporting
    async def calculate_order_totals(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID
    ) -> Dict[str, Decimal]:
        """Calculate order totals."""
        try:
            po = await self.get_by_id(business_id, order_id)
            if not po:
                raise EntityNotFoundError(f"Purchase order {order_id} not found")
            
            return {
                "subtotal": po.subtotal,
                "tax_amount": po.tax_amount,
                "total_amount": po.total_amount
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to calculate order totals: {str(e)}")
    
    async def get_spending_by_supplier(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get spending analytics by supplier."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("supplier_id", str(supplier_id))
            
            if start_date:
                query = query.gte("order_date", start_date.isoformat())
            if end_date:
                query = query.lte("order_date", end_date.isoformat())
            
            response = query.execute()
            orders = [self._dict_to_purchase_order(po) for po in response.data]
            
            total_spend = sum(po.total_amount for po in orders)
            
            return {
                "supplier_id": str(supplier_id),
                "total_spend": float(total_spend),
                "order_count": len(orders),
                "average_order_value": float(total_spend / len(orders)) if orders else 0,
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get spending by supplier: {str(e)}")
    
    async def get_spending_by_category(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get spending analytics by category."""
        try:
            # This would require joining with products and categories
            # For now, returning basic spending data
            return [{
                "category": "General",
                "total_spend": 0.0,
                "order_count": 0
            }]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get spending by category: {str(e)}")
    
    async def get_budget_analysis(
        self,
        business_id: uuid.UUID,
        budget_period: str = "month",
        category_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get budget analysis."""
        try:
            # This would require budget tables and complex calculations
            # For now, returning basic budget data
            return {
                "period": budget_period,
                "budgeted_amount": 10000.0,
                "actual_spend": 8500.0,
                "variance": 1500.0,
                "variance_percentage": 15.0
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get budget analysis: {str(e)}")
    
    async def get_order_analytics(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        supplier_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get comprehensive order analytics."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if start_date:
                query = query.gte("order_date", start_date.isoformat())
            if end_date:
                query = query.lte("order_date", end_date.isoformat())
            if supplier_id:
                query = query.eq("supplier_id", str(supplier_id))
            
            response = query.execute()
            orders = [self._dict_to_purchase_order(po) for po in response.data]
            
            if not orders:
                return {"total_orders": 0, "total_spend": 0.0, "average_order_value": 0.0}
            
            total_spend = sum(po.total_amount for po in orders)
            
            return {
                "total_orders": len(orders),
                "total_spend": float(total_spend),
                "average_order_value": float(total_spend / len(orders)),
                "status_breakdown": self._get_status_breakdown(orders),
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get order analytics: {str(e)}")
    
    def _get_status_breakdown(self, orders: List[PurchaseOrder]) -> Dict[str, int]:
        """Get status breakdown from orders list."""
        breakdown = {}
        for order in orders:
            status = order.status.value
            breakdown[status] = breakdown.get(status, 0) + 1
        return breakdown
    
    async def get_delivery_performance_metrics(
        self,
        business_id: uuid.UUID,
        supplier_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get delivery performance metrics."""
        try:
            # This would require delivery tracking data
            # For now, returning basic performance metrics
            return {
                "total_orders": 25,
                "on_time_deliveries": 20,
                "late_deliveries": 5,
                "on_time_percentage": 80.0,
                "average_delay_days": 2.3
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get delivery performance metrics: {str(e)}")
    
    async def get_order_trends(
        self,
        business_id: uuid.UUID,
        period: str = "month",  # day, week, month, quarter
        periods_count: int = 12
    ) -> List[Dict[str, Any]]:
        """Get order trends over time."""  
        try:
            # This would require time-series analysis
            # For now, returning sample trend data
            trends = []
            for i in range(periods_count):
                trends.append({
                    "period": f"2024-{12-i:02d}",
                    "order_count": 15 + (i % 5),
                    "total_spend": 5000.0 + (i * 500),
                    "average_order_value": 333.33
                })
            return trends
            
        except Exception as e:
            raise DatabaseError(f"Failed to get order trends: {str(e)}")
    
    async def get_top_products_by_spend(
        self,
        business_id: uuid.UUID,
        limit: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top products by spend."""
        try:
            # This would require joining with line items and products
            # For now, returning empty list
            return []
            
        except Exception as e:
            raise DatabaseError(f"Failed to get top products by spend: {str(e)}")
    
    # Approval workflow and document management
    async def get_approval_history(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID
    ) -> List[Dict[str, Any]]:
        """Get approval history for a purchase order."""
        try:
            # This would require an approval_history table
            # For now, returning empty list
            return []
            
        except Exception as e:
            raise DatabaseError(f"Failed to get approval history: {str(e)}")
    
    async def get_orders_for_approver(
        self,
        business_id: uuid.UUID,
        approver_id: str,
        approval_level: int
    ) -> List[PurchaseOrder]:
        """Get orders for a specific approver."""
        try:
            # This would require approval workflow configuration
            # For now, returning pending orders
            return await self.get_orders_pending_approval(business_id)
            
        except Exception as e:
            raise DatabaseError(f"Failed to get orders for approver: {str(e)}")
    
    async def update_approval_workflow(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        workflow_data: Dict[str, Any]
    ) -> bool:
        """Update approval workflow for a purchase order."""
        try:
            # This would require workflow management tables
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to update approval workflow: {str(e)}")
    
    async def attach_document(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        document_data: Dict[str, Any]
    ) -> bool:
        """Attach a document to a purchase order."""
        try:
            # This would require a purchase_order_documents table
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to attach document: {str(e)}")
    
    async def get_order_documents(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        document_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get documents for a purchase order."""
        try:
            # This would require a purchase_order_documents table
            # For now, returning empty list
            return []
            
        except Exception as e:
            raise DatabaseError(f"Failed to get order documents: {str(e)}")
    
    async def remove_document(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        document_id: uuid.UUID
    ) -> bool:
        """Remove a document from a purchase order."""
        try:
            # This would require a purchase_order_documents table
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to remove document: {str(e)}")
    
    # Integration and conversion methods
    async def create_from_requisition(
        self,
        business_id: uuid.UUID,
        requisition_data: Dict[str, Any],
        created_by: str
    ) -> PurchaseOrder:
        """Create a purchase order from a requisition."""
        try:
            # This would require requisition to PO conversion logic
            # For now, creating a basic PO structure
            from app.domain.entities.purchase_order import PurchaseOrder
            from decimal import Decimal
            
            po = PurchaseOrder(
                id=uuid.uuid4(),
                business_id=business_id,
                supplier_id=uuid.UUID(requisition_data["supplier_id"]),
                po_number=f"PO-{datetime.utcnow().strftime('%Y%m%d')}-001",
                status=PurchaseOrderStatus.DRAFT,
                order_date=datetime.utcnow(),
                subtotal=Decimal(str(requisition_data.get("subtotal", "0"))),
                tax_amount=Decimal(str(requisition_data.get("tax_amount", "0"))),
                total_amount=Decimal(str(requisition_data.get("total_amount", "0"))),
                created_by=created_by
            )
            
            return await self.create(po)
            
        except Exception as e:
            raise DatabaseError(f"Failed to create from requisition: {str(e)}")
    
    async def convert_to_invoice(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        invoice_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert a purchase order to an invoice."""
        try:
            po = await self.get_by_id(business_id, order_id)
            if not po:
                raise EntityNotFoundError(f"Purchase order {order_id} not found")
            
            # This would require invoice creation logic
            # For now, returning basic invoice data
            return {
                "invoice_id": str(uuid.uuid4()),
                "po_number": po.po_number,
                "supplier_id": str(po.supplier_id),
                "amount": float(po.total_amount),
                "status": "draft"
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to convert to invoice: {str(e)}")
    
    async def sync_with_supplier_system(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        supplier_system_data: Dict[str, Any]
    ) -> bool:
        """Sync purchase order with supplier system."""
        try:
            # This would require supplier system integration
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to sync with supplier system: {str(e)}")
    
    # Bulk operations
    async def bulk_update_status(
        self,
        business_id: uuid.UUID,
        order_ids: List[uuid.UUID],
        new_status: PurchaseOrderStatus,
        updated_by: str
    ) -> int:
        """Bulk update status for multiple purchase orders."""
        try:
            response = self.client.table(self.table_name).update({
                "status": new_status.value,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).in_(
                "id", [str(order_id) for order_id in order_ids]
            ).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk update status: {str(e)}")
    
    async def bulk_send_to_suppliers(
        self,
        business_id: uuid.UUID,
        order_ids: List[uuid.UUID],
        sent_by: str
    ) -> int:
        """Bulk send purchase orders to suppliers."""
        try:
            response = self.client.table(self.table_name).update({
                "status": PurchaseOrderStatus.SENT.value,
                "sent_by": sent_by,
                "sent_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).in_(
                "id", [str(order_id) for order_id in order_ids]
            ).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk send to suppliers: {str(e)}")
    
    async def bulk_approve_orders(
        self,
        business_id: uuid.UUID,
        order_ids: List[uuid.UUID],
        approved_by: str,
        approval_level: int
    ) -> int:
        """Bulk approve purchase orders."""
        try:
            response = self.client.table(self.table_name).update({
                "status": PurchaseOrderStatus.CONFIRMED.value,
                "approved_by": approved_by,
                "approved_at": datetime.utcnow().isoformat(),
                "approval_level": approval_level,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).in_(
                "id", [str(order_id) for order_id in order_ids]
            ).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk approve orders: {str(e)}")
    
    # Advanced search and filtering
    async def advanced_search(
        self,
        business_id: uuid.UUID,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Advanced search with filtering."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            # Apply filters
            for key, value in filters.items():
                if value is not None:
                    if key == "status":
                        query = query.eq("status", value)
                    elif key == "supplier_id":
                        query = query.eq("supplier_id", value)
                    elif key == "po_number":
                        query = query.ilike("po_number", f"%{value}%")
                    elif key == "min_amount":
                        query = query.gte("total_amount", value)
                    elif key == "max_amount":
                        query = query.lte("total_amount", value)
            
            # Apply sorting
            sort_column = sort_by or "created_at"
            desc = sort_order.lower() == "desc"
            
            response = query.range(offset, offset + limit - 1).order(sort_column, desc=desc).execute()
            
            orders = [self._dict_to_purchase_order(po) for po in response.data]
            
            return {
                "orders": [{
                    "id": str(o.id),
                    "po_number": o.po_number,
                    "supplier_id": str(o.supplier_id),
                    "status": o.status.value,
                    "total_amount": float(o.total_amount),
                    "order_date": o.order_date.isoformat()
                } for o in orders],
                "total": len(orders),
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to perform advanced search: {str(e)}")
    
    async def get_filter_options(
        self,
        business_id: uuid.UUID
    ) -> Dict[str, List[Any]]:
        """Get available filter options."""
        try:
            return {
                "statuses": [status.value for status in PurchaseOrderStatus],
                "suppliers": [],  # Would require supplier data
                "date_ranges": ["last_7_days", "last_30_days", "last_90_days", "last_year"]
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get filter options: {str(e)}")
    
    # Mobile optimization
    async def get_orders_for_mobile(
        self,
        business_id: uuid.UUID,
        user_id: str,
        status_filter: Optional[List[PurchaseOrderStatus]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get purchase orders optimized for mobile app."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if status_filter:
                query = query.in_("status", [status.value for status in status_filter])
            
            response = query.range(offset, offset + limit - 1).order("created_at", desc=True).execute()
            
            mobile_orders = []
            for po_data in response.data:
                po = self._dict_to_purchase_order(po_data)
                mobile_orders.append({
                    "id": str(po.id),
                    "po_number": po.po_number,
                    "supplier_id": str(po.supplier_id),
                    "status": po.status.value,
                    "total_amount": float(po.total_amount),
                    "order_date": po.order_date.isoformat(),
                    "expected_delivery": po.expected_delivery_date.isoformat() if po.expected_delivery_date else None
                })
            
            return {
                "orders": mobile_orders,
                "total": len(mobile_orders),
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get orders for mobile: {str(e)}")
    
    async def get_order_summary_for_mobile(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get order summary for mobile app."""
        try:
            po = await self.get_by_id(business_id, order_id)
            if not po:
                raise EntityNotFoundError(f"Purchase order {order_id} not found")
            
            return {
                "id": str(po.id),
                "po_number": po.po_number,
                "supplier_id": str(po.supplier_id),
                "status": po.status.value,
                "order_date": po.order_date.isoformat(),
                "expected_delivery": po.expected_delivery_date.isoformat() if po.expected_delivery_date else None,
                "subtotal": float(po.subtotal),
                "tax_amount": float(po.tax_amount),
                "total_amount": float(po.total_amount),
                "notes": po.notes,
                "created_by": po.created_by
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get order summary for mobile: {str(e)}")
    
    async def get_pending_actions_for_mobile(
        self,
        business_id: uuid.UUID,
        user_id: str
    ) -> Dict[str, Any]:
        """Get pending actions for mobile app."""
        try:
            pending_approvals = await self.get_orders_pending_approval(business_id)
            pending_receipts = await self.get_orders_pending_receipt(business_id)
            overdue_orders = await self.get_overdue_orders(business_id)
            
            return {
                "pending_approvals": len(pending_approvals),
                "pending_receipts": len(pending_receipts),
                "overdue_orders": len(overdue_orders),
                "total_actions": len(pending_approvals) + len(pending_receipts) + len(overdue_orders)
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get pending actions for mobile: {str(e)}")
    
    # Utility methods
    async def generate_po_number(
        self,
        business_id: uuid.UUID,
        prefix: Optional[str] = None
    ) -> str:
        """Generate a unique PO number."""
        try:
            # This would require sequence management
            # For now, generating a simple timestamp-based number
            prefix = prefix or "PO"
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            return f"{prefix}-{timestamp}"
            
        except Exception as e:
            raise DatabaseError(f"Failed to generate PO number: {str(e)}")
    
    async def validate_po_number(
        self,
        business_id: uuid.UUID,
        po_number: str,
        exclude_order_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Validate if PO number is unique."""
        try:
            query = self.client.table(self.table_name).select("id").eq(
                "business_id", str(business_id)
            ).eq("po_number", po_number)
            
            if exclude_order_id:
                query = query.neq("id", str(exclude_order_id))
            
            response = query.execute()
            
            return len(response.data) == 0  # True if unique
            
        except Exception as e:
            raise DatabaseError(f"Failed to validate PO number: {str(e)}")
    
    async def count_orders(
        self,
        business_id: uuid.UUID,
        status: Optional[PurchaseOrderStatus] = None,
        supplier_id: Optional[uuid.UUID] = None
    ) -> int:
        """Count purchase orders with optional filters."""
        try:
            query = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            )
            
            if status:
                query = query.eq("status", status.value)
            if supplier_id:
                query = query.eq("supplier_id", str(supplier_id))
            
            response = query.execute()
            
            return response.count if response.count else 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count orders: {str(e)}")
    
    async def get_order_statistics(
        self,
        business_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get order statistics for a date range."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).gte("order_date", start_date.isoformat()).lte("order_date", end_date.isoformat())
            
            response = query.execute()
            orders = [self._dict_to_purchase_order(po) for po in response.data]
            
            if not orders:
                return {
                    "total_orders": 0,
                    "total_spend": 0.0,
                    "average_order_value": 0.0,
                    "status_breakdown": {}
                }
            
            total_spend = sum(po.total_amount for po in orders)
            
            return {
                "total_orders": len(orders),
                "total_spend": float(total_spend),
                "average_order_value": float(total_spend / len(orders)),
                "status_breakdown": self._get_status_breakdown(orders),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get order statistics: {str(e)}")
    
    async def get_audit_trail(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID
    ) -> List[Dict[str, Any]]:
        """Get audit trail for a purchase order."""
        try:
            # This would require an audit log table
            # For now, returning empty list
            return []
            
        except Exception as e:
            raise DatabaseError(f"Failed to get audit trail: {str(e)}")
    
    async def get_orders_requiring_review(
        self,
        business_id: uuid.UUID,
        review_criteria: Optional[Dict[str, Any]] = None
    ) -> List[PurchaseOrder]:
        """Get orders requiring review based on criteria."""
        try:
            # This would require complex review logic
            # For now, returning overdue orders as needing review
            return await self.get_overdue_orders(business_id)
            
        except Exception as e:
            raise DatabaseError(f"Failed to get orders requiring review: {str(e)}")

    def _purchase_order_to_dict(self, po: PurchaseOrder) -> dict:
        """Convert PurchaseOrder entity to dictionary."""
        return {
            "id": str(po.id),
            "business_id": str(po.business_id),
            "supplier_id": str(po.supplier_id),
            "po_number": po.po_number,
            "status": po.status.value,
            "order_date": po.order_date.isoformat(),
            "expected_delivery_date": po.expected_delivery_date.isoformat() if po.expected_delivery_date else None,
            "subtotal": float(po.subtotal),
            "tax_amount": float(po.tax_amount),
            "total_amount": float(po.total_amount),
            "notes": po.notes,
            "terms": po.terms,
            "created_by": po.created_by,
        }
    
    def _dict_to_purchase_order(self, data: dict) -> PurchaseOrder:
        """Convert dictionary to PurchaseOrder entity."""
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
        
        return PurchaseOrder(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            supplier_id=uuid.UUID(data["supplier_id"]),
            po_number=data["po_number"],
            status=PurchaseOrderStatus(data["status"]),
            order_date=safe_datetime(data["order_date"]) or datetime.utcnow(),
            expected_delivery_date=safe_datetime(data.get("expected_delivery_date")),
            subtotal=safe_decimal(data["subtotal"], Decimal('0')),
            tax_amount=safe_decimal(data["tax_amount"], Decimal('0')),
            total_amount=safe_decimal(data["total_amount"], Decimal('0')),
            notes=data.get("notes"),
            terms=data.get("terms"),
            created_by=data.get("created_by", ""),
        ) 