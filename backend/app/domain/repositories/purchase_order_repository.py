"""
Purchase Order Repository Interface

Repository interface for purchase order management with workflow support,
receiving tracking, and supplier integration capabilities.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime, date

from ..entities.purchase_order import PurchaseOrder
from ..enums import PurchaseOrderStatus


class PurchaseOrderRepository(ABC):
    """Repository interface for purchase order management operations."""
    
    # Basic CRUD operations
    @abstractmethod
    async def create(self, purchase_order: PurchaseOrder) -> PurchaseOrder:
        """Create a new purchase order."""
        pass
    
    @abstractmethod
    async def get_by_id(self, business_id: uuid.UUID, order_id: uuid.UUID) -> Optional[PurchaseOrder]:
        """Get purchase order by ID."""
        pass
    
    @abstractmethod
    async def get_by_number(self, business_id: uuid.UUID, po_number: str) -> Optional[PurchaseOrder]:
        """Get purchase order by PO number."""
        pass
    
    @abstractmethod
    async def update(self, purchase_order: PurchaseOrder) -> PurchaseOrder:
        """Update an existing purchase order."""
        pass
    
    @abstractmethod
    async def delete(self, business_id: uuid.UUID, order_id: uuid.UUID) -> bool:
        """Delete a purchase order (only if draft status)."""
        pass
    
    # List and search operations
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def search_orders(
        self,
        business_id: uuid.UUID,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[PurchaseOrder]:
        """Search purchase orders by number, supplier, or line items."""
        pass
    
    @abstractmethod
    async def get_orders_by_status(
        self,
        business_id: uuid.UUID,
        status: PurchaseOrderStatus,
        limit: int = 100,
        offset: int = 0
    ) -> List[PurchaseOrder]:
        """Get purchase orders by status."""
        pass
    
    @abstractmethod
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
        pass
    
    # Status and workflow management
    @abstractmethod
    async def update_status(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        new_status: PurchaseOrderStatus,
        updated_by: str,
        notes: Optional[str] = None
    ) -> bool:
        """Update purchase order status."""
        pass
    
    @abstractmethod
    async def get_orders_pending_approval(
        self,
        business_id: uuid.UUID,
        approval_level: Optional[int] = None
    ) -> List[PurchaseOrder]:
        """Get purchase orders pending approval."""
        pass
    
    @abstractmethod
    async def approve_order(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        approved_by: str,
        approval_level: int,
        notes: Optional[str] = None
    ) -> bool:
        """Approve a purchase order at specific level."""
        pass
    
    @abstractmethod
    async def reject_order(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        rejected_by: str,
        reason: str
    ) -> bool:
        """Reject a purchase order."""
        pass
    
    @abstractmethod
    async def send_to_supplier(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        sent_by: str,
        method: str = "email"
    ) -> bool:
        """Mark purchase order as sent to supplier."""
        pass
    
    # Receiving and fulfillment
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def get_orders_pending_receipt(
        self,
        business_id: uuid.UUID,
        supplier_id: Optional[uuid.UUID] = None,
        overdue_only: bool = False
    ) -> List[PurchaseOrder]:
        """Get purchase orders pending receipt."""
        pass
    
    @abstractmethod
    async def get_partially_received_orders(
        self,
        business_id: uuid.UUID,
        supplier_id: Optional[uuid.UUID] = None
    ) -> List[PurchaseOrder]:
        """Get purchase orders that are partially received."""
        pass
    
    @abstractmethod
    async def get_overdue_orders(
        self,
        business_id: uuid.UUID,
        supplier_id: Optional[uuid.UUID] = None
    ) -> List[PurchaseOrder]:
        """Get purchase orders that are overdue for delivery."""
        pass
    
    @abstractmethod
    async def update_expected_delivery(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        new_expected_date: datetime,
        updated_by: str,
        reason: Optional[str] = None
    ) -> bool:
        """Update expected delivery date."""
        pass
    
    # Line item management
    @abstractmethod
    async def add_line_item(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        line_item_data: Dict[str, Any]
    ) -> bool:
        """Add a line item to a purchase order."""
        pass
    
    @abstractmethod
    async def update_line_item(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        line_item_id: uuid.UUID,
        line_item_data: Dict[str, Any]
    ) -> bool:
        """Update a purchase order line item."""
        pass
    
    @abstractmethod
    async def remove_line_item(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        line_item_id: uuid.UUID
    ) -> bool:
        """Remove a line item from a purchase order."""
        pass
    
    @abstractmethod
    async def get_line_items_for_product(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        status: Optional[PurchaseOrderStatus] = None,
        pending_receipt_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get purchase order line items for a specific product."""
        pass
    
    # Financial calculations and tracking
    @abstractmethod
    async def calculate_order_totals(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID
    ) -> Dict[str, Decimal]:
        """Calculate purchase order totals including taxes and fees."""
        pass
    
    @abstractmethod
    async def get_spending_by_supplier(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get spending analytics for a supplier."""
        pass
    
    @abstractmethod
    async def get_spending_by_category(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get spending breakdown by product category."""
        pass
    
    @abstractmethod
    async def get_budget_analysis(
        self,
        business_id: uuid.UUID,
        budget_period: str = "month",
        category_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get budget vs actual spending analysis."""
        pass
    
    # Analytics and reporting
    @abstractmethod
    async def get_order_analytics(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        supplier_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get purchase order analytics and metrics."""
        pass
    
    @abstractmethod
    async def get_delivery_performance_metrics(
        self,
        business_id: uuid.UUID,
        supplier_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get delivery performance metrics."""
        pass
    
    @abstractmethod
    async def get_order_trends(
        self,
        business_id: uuid.UUID,
        period: str = "month",  # day, week, month, quarter
        periods_count: int = 12
    ) -> List[Dict[str, Any]]:
        """Get purchase order trends over time."""
        pass
    
    @abstractmethod
    async def get_top_products_by_spend(
        self,
        business_id: uuid.UUID,
        limit: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top products by purchase spend."""
        pass
    
    # Approval workflow management
    @abstractmethod
    async def get_approval_history(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID
    ) -> List[Dict[str, Any]]:
        """Get approval history for a purchase order."""
        pass
    
    @abstractmethod
    async def get_orders_for_approver(
        self,
        business_id: uuid.UUID,
        approver_id: str,
        approval_level: int
    ) -> List[PurchaseOrder]:
        """Get purchase orders pending approval by specific approver."""
        pass
    
    @abstractmethod
    async def update_approval_workflow(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        workflow_data: Dict[str, Any]
    ) -> bool:
        """Update approval workflow configuration for an order."""
        pass
    
    # Document management
    @abstractmethod
    async def attach_document(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        document_data: Dict[str, Any]
    ) -> bool:
        """Attach a document to a purchase order."""
        pass
    
    @abstractmethod
    async def get_order_documents(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        document_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get documents attached to a purchase order."""
        pass
    
    @abstractmethod
    async def remove_document(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        document_id: uuid.UUID
    ) -> bool:
        """Remove a document from a purchase order."""
        pass
    
    # Integration and automation
    @abstractmethod
    async def create_from_requisition(
        self,
        business_id: uuid.UUID,
        requisition_data: Dict[str, Any],
        created_by: str
    ) -> PurchaseOrder:
        """Create purchase order from requisition."""
        pass
    
    @abstractmethod
    async def convert_to_invoice(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        invoice_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert received purchase order to invoice."""
        pass
    
    @abstractmethod
    async def sync_with_supplier_system(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID,
        supplier_system_data: Dict[str, Any]
    ) -> bool:
        """Sync purchase order with supplier's system."""
        pass
    
    # Bulk operations
    @abstractmethod
    async def bulk_update_status(
        self,
        business_id: uuid.UUID,
        order_ids: List[uuid.UUID],
        new_status: PurchaseOrderStatus,
        updated_by: str
    ) -> int:
        """Bulk update purchase order status."""
        pass
    
    @abstractmethod
    async def bulk_send_to_suppliers(
        self,
        business_id: uuid.UUID,
        order_ids: List[uuid.UUID],
        sent_by: str
    ) -> int:
        """Bulk send purchase orders to suppliers."""
        pass
    
    @abstractmethod
    async def bulk_approve_orders(
        self,
        business_id: uuid.UUID,
        order_ids: List[uuid.UUID],
        approved_by: str,
        approval_level: int
    ) -> int:
        """Bulk approve purchase orders."""
        pass
    
    # Advanced search and filtering
    @abstractmethod
    async def advanced_search(
        self,
        business_id: uuid.UUID,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Advanced purchase order search with multiple filters."""
        pass
    
    @abstractmethod
    async def get_filter_options(
        self,
        business_id: uuid.UUID
    ) -> Dict[str, List[Any]]:
        """Get available filter options for purchase order search."""
        pass
    
    # Mobile app optimization
    @abstractmethod
    async def get_orders_for_mobile(
        self,
        business_id: uuid.UUID,
        user_id: str,
        status_filter: Optional[List[PurchaseOrderStatus]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get purchase orders optimized for mobile app consumption."""
        pass
    
    @abstractmethod
    async def get_order_summary_for_mobile(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get purchase order summary optimized for mobile display."""
        pass
    
    @abstractmethod
    async def get_pending_actions_for_mobile(
        self,
        business_id: uuid.UUID,
        user_id: str
    ) -> Dict[str, Any]:
        """Get pending purchase order actions for mobile dashboard."""
        pass
    
    # Number generation and validation
    @abstractmethod
    async def generate_po_number(
        self,
        business_id: uuid.UUID,
        prefix: Optional[str] = None
    ) -> str:
        """Generate next purchase order number."""
        pass
    
    @abstractmethod
    async def validate_po_number(
        self,
        business_id: uuid.UUID,
        po_number: str,
        exclude_order_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Validate if PO number is unique."""
        pass
    
    # Count operations
    @abstractmethod
    async def count_orders(
        self,
        business_id: uuid.UUID,
        status: Optional[PurchaseOrderStatus] = None,
        supplier_id: Optional[uuid.UUID] = None
    ) -> int:
        """Count purchase orders with optional filtering."""
        pass
    
    @abstractmethod
    async def get_order_statistics(
        self,
        business_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get purchase order statistics for a date range."""
        pass
    
    # Audit and compliance
    @abstractmethod
    async def get_audit_trail(
        self,
        business_id: uuid.UUID,
        order_id: uuid.UUID
    ) -> List[Dict[str, Any]]:
        """Get complete audit trail for a purchase order."""
        pass
    
    @abstractmethod
    async def get_orders_requiring_review(
        self,
        business_id: uuid.UUID,
        review_criteria: Optional[Dict[str, Any]] = None
    ) -> List[PurchaseOrder]:
        """Get purchase orders requiring review based on business rules."""
        pass 