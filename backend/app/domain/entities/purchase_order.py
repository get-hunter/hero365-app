"""
Purchase Order Domain Entity

Represents a purchase order for inventory management with comprehensive business rules,
line items, approval workflows, and receiving tracking.
"""

import uuid
import logging
from datetime import datetime, timezone, date
from typing import Optional, List, Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, Field, validator, computed_field

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError
from .product_enums.enums import PurchaseOrderStatus
from ..shared.enums import CurrencyCode, TaxType
from ..value_objects.address import Address

# Configure logging
logger = logging.getLogger(__name__)


class PurchaseOrderLineItem(BaseModel):
    """Line item for a purchase order."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Line item unique identifier")
    product_id: uuid.UUID = Field(..., description="Product identifier")
    product_sku: str = Field(..., min_length=1, max_length=100, description="Product SKU")
    product_name: str = Field(..., min_length=1, max_length=300, description="Product name")
    description: Optional[str] = Field(None, max_length=500, description="Line item description")
    
    # Quantities
    quantity_ordered: Decimal = Field(..., gt=0, description="Quantity ordered")
    quantity_received: Decimal = Field(default=Decimal('0'), ge=0, description="Quantity received")
    quantity_pending: Decimal = Field(default=Decimal('0'), ge=0, description="Quantity pending receipt")
    
    # Pricing
    unit_cost: Decimal = Field(..., gt=0, description="Unit cost")
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Discount percentage")
    discount_amount: Optional[Decimal] = Field(None, ge=0, description="Discount amount")
    tax_rate: Decimal = Field(default=Decimal('0'), ge=0, le=100, description="Tax rate percentage")
    
    # Unit of measure
    unit_of_measure: str = Field(default="each", max_length=50, description="Unit of measure")
    
    # Delivery information
    expected_delivery_date: Optional[date] = Field(None, description="Expected delivery date")
    actual_delivery_date: Optional[date] = Field(None, description="Actual delivery date")
    
    # Notes
    notes: Optional[str] = Field(None, max_length=500, description="Line item notes")
    
    @validator('quantity_received')
    def validate_quantity_received(cls, v, values):
        if 'quantity_ordered' in values and v > values['quantity_ordered']:
            raise ValueError('Quantity received cannot exceed quantity ordered')
        return v
    
    class Config:
        use_enum_values = True
        json_encoders = {
            uuid.UUID: str,
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }
    
    @computed_field
    @property
    def line_subtotal(self) -> Decimal:
        """Calculate line subtotal before tax."""
        subtotal = self.quantity_ordered * self.unit_cost
        
        if self.discount_amount:
            subtotal -= self.discount_amount
        elif self.discount_percentage:
            subtotal -= subtotal * (self.discount_percentage / Decimal('100'))
        
        return subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @computed_field
    @property
    def tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        return (self.line_subtotal * self.tax_rate / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @computed_field
    @property
    def line_total(self) -> Decimal:
        """Calculate line total including tax."""
        return self.line_subtotal + self.tax_amount
    
    @computed_field
    @property
    def quantity_outstanding(self) -> Decimal:
        """Calculate quantity still outstanding."""
        return self.quantity_ordered - self.quantity_received
    
    @computed_field
    @property
    def is_fully_received(self) -> bool:
        """Check if line item is fully received."""
        return self.quantity_received >= self.quantity_ordered
    
    @computed_field
    @property
    def is_partially_received(self) -> bool:
        """Check if line item is partially received."""
        return self.quantity_received > 0 and not self.is_fully_received
    
    @computed_field
    @property
    def is_overdue(self) -> bool:
        """Check if delivery is overdue."""
        if not self.expected_delivery_date or self.is_fully_received:
            return False
        return date.today() > self.expected_delivery_date
    
    def receive_quantity(self, quantity: Decimal, received_date: Optional[date] = None):
        """Record receipt of quantity."""
        if quantity <= 0:
            raise ValueError("Received quantity must be positive")
        
        if self.quantity_received + quantity > self.quantity_ordered:
            raise BusinessRuleViolationError("Cannot receive more than ordered quantity")
        
        self.quantity_received += quantity
        
        if received_date and not self.actual_delivery_date:
            self.actual_delivery_date = received_date
    
    def is_valid_line_item(self) -> bool:
        """Validate line item data."""
        if self.quantity_ordered <= 0:
            return False
        if self.unit_cost <= 0:
            return False
        if self.quantity_received > self.quantity_ordered:
            return False
        return True


class PurchaseOrder(BaseModel):
    """
    Purchase Order domain entity.
    
    Represents a purchase order with comprehensive business rules,
    line items, approval workflows, and receiving tracking.
    """
    
    # Basic order information
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Purchase order unique identifier")
    business_id: uuid.UUID = Field(..., description="Business identifier")
    po_number: str = Field(..., min_length=1, max_length=50, description="Purchase order number")
    
    # Supplier information
    supplier_id: uuid.UUID = Field(..., description="Supplier identifier")
    supplier_name: str = Field(..., min_length=1, max_length=200, description="Supplier name")
    supplier_contact_name: Optional[str] = Field(None, max_length=200, description="Supplier contact name")
    supplier_email: Optional[str] = Field(None, max_length=255, description="Supplier email")
    supplier_phone: Optional[str] = Field(None, max_length=50, description="Supplier phone")
    
    # Order status and dates
    status: PurchaseOrderStatus = Field(default=PurchaseOrderStatus.DRAFT, description="Purchase order status")
    order_date: date = Field(default_factory=date.today, description="Order date")
    expected_delivery_date: Optional[date] = Field(None, description="Expected delivery date")
    actual_delivery_date: Optional[date] = Field(None, description="Actual delivery date")
    
    # Addresses
    ship_to_address: Optional[Address] = Field(None, description="Shipping address")
    bill_to_address: Optional[Address] = Field(None, description="Billing address")
    
    # Line items
    line_items: List[PurchaseOrderLineItem] = Field(default_factory=list, description="Purchase order line items")
    
    # Financial information
    currency: CurrencyCode = Field(default=CurrencyCode.USD, description="Currency code")
    tax_inclusive: bool = Field(default=False, description="Whether prices include tax")
    
    # Additional costs
    shipping_cost: Optional[Decimal] = Field(None, ge=0, description="Shipping cost")
    handling_cost: Optional[Decimal] = Field(None, ge=0, description="Handling cost")
    other_costs: Optional[Decimal] = Field(None, ge=0, description="Other costs")
    
    # Payment terms
    payment_terms: Optional[str] = Field(None, max_length=100, description="Payment terms")
    discount_terms: Optional[str] = Field(None, max_length=100, description="Discount terms")
    
    # Notes and references
    notes: Optional[str] = Field(None, max_length=2000, description="Purchase order notes")
    internal_notes: Optional[str] = Field(None, max_length=2000, description="Internal notes")
    reference_number: Optional[str] = Field(None, max_length=100, description="Reference number")
    
    # Approval workflow
    requires_approval: bool = Field(default=True, description="Whether order requires approval")
    approved_by: Optional[str] = Field(None, description="User who approved the order")
    approved_date: Optional[datetime] = Field(None, description="Approval date")
    rejection_reason: Optional[str] = Field(None, max_length=500, description="Rejection reason")
    
    # Metadata
    created_by: str = Field(..., description="User who created the order")
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation date")
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last modification date")
    sent_date: Optional[datetime] = Field(None, description="Date order was sent to supplier")
    
    # Business rules validation
    @validator('po_number')
    def validate_po_number(cls, v):
        if not v or v.strip() == "":
            raise ValueError('PO number cannot be empty')
        return v.strip().upper()
    
    @validator('line_items')
    def validate_line_items(cls, v):
        if not v:
            raise ValueError('Purchase order must have at least one line item')
        
        # Validate each line item
        for item in v:
            if not item.is_valid_line_item():
                raise ValueError(f'Invalid line item: {item.product_sku}')
        
        return v
    
    @validator('expected_delivery_date')
    def validate_expected_delivery_date(cls, v, values):
        if v is not None and 'order_date' in values:
            if v < values['order_date']:
                raise ValueError('Expected delivery date cannot be before order date')
        return v
    
    class Config:
        validate_assignment = True
        use_enum_values = True
        json_encoders = {
            uuid.UUID: str,
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    
    # Computed fields
    @computed_field
    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal of all line items."""
        return sum(item.line_subtotal for item in self.line_items)
    
    @computed_field
    @property
    def total_tax(self) -> Decimal:
        """Calculate total tax amount."""
        return sum(item.tax_amount for item in self.line_items)
    
    @computed_field
    @property
    def additional_costs(self) -> Decimal:
        """Calculate total additional costs."""
        return (
            (self.shipping_cost or Decimal('0')) +
            (self.handling_cost or Decimal('0')) +
            (self.other_costs or Decimal('0'))
        )
    
    @computed_field
    @property
    def total_amount(self) -> Decimal:
        """Calculate total purchase order amount."""
        return self.subtotal + self.total_tax + self.additional_costs
    
    @computed_field
    @property
    def total_quantity_ordered(self) -> Decimal:
        """Calculate total quantity ordered across all line items."""
        return sum(item.quantity_ordered for item in self.line_items)
    
    @computed_field
    @property
    def total_quantity_received(self) -> Decimal:
        """Calculate total quantity received across all line items."""
        return sum(item.quantity_received for item in self.line_items)
    
    @computed_field
    @property
    def total_quantity_outstanding(self) -> Decimal:
        """Calculate total quantity outstanding."""
        return self.total_quantity_ordered - self.total_quantity_received
    
    @computed_field
    @property
    def is_fully_received(self) -> bool:
        """Check if all line items are fully received."""
        return all(item.is_fully_received for item in self.line_items)
    
    @computed_field
    @property
    def is_partially_received(self) -> bool:
        """Check if any line items are partially received."""
        return any(item.is_partially_received for item in self.line_items) and not self.is_fully_received
    
    @computed_field
    @property
    def is_approved(self) -> bool:
        """Check if purchase order is approved."""
        return self.approved_by is not None and self.approved_date is not None
    
    @computed_field
    @property
    def is_sent(self) -> bool:
        """Check if purchase order has been sent."""
        return self.sent_date is not None
    
    @computed_field
    @property
    def is_overdue(self) -> bool:
        """Check if delivery is overdue."""
        if not self.expected_delivery_date or self.is_fully_received:
            return False
        return date.today() > self.expected_delivery_date
    
    @computed_field
    @property
    def can_be_edited(self) -> bool:
        """Check if purchase order can be edited."""
        return self.status in [PurchaseOrderStatus.DRAFT]
    
    @computed_field
    @property
    def can_be_approved(self) -> bool:
        """Check if purchase order can be approved."""
        return (
            self.status == PurchaseOrderStatus.DRAFT and
            self.requires_approval and
            not self.is_approved
        )
    
    @computed_field
    @property
    def can_be_sent(self) -> bool:
        """Check if purchase order can be sent."""
        return (
            self.status == PurchaseOrderStatus.DRAFT and
            (not self.requires_approval or self.is_approved) and
            not self.is_sent
        )
    
    # Business logic methods
    def add_line_item(self, line_item: PurchaseOrderLineItem):
        """Add a line item to the purchase order."""
        if not self.can_be_edited:
            raise BusinessRuleViolationError("Cannot add line items to non-draft purchase order")
        
        # Check for duplicate products
        for existing_item in self.line_items:
            if existing_item.product_id == line_item.product_id:
                raise BusinessRuleViolationError("Product already exists in purchase order")
        
        self.line_items.append(line_item)
        self.last_modified = datetime.now(timezone.utc)
    
    def remove_line_item(self, line_item_id: uuid.UUID) -> bool:
        """Remove a line item from the purchase order."""
        if not self.can_be_edited:
            raise BusinessRuleViolationError("Cannot remove line items from non-draft purchase order")
        
        for i, item in enumerate(self.line_items):
            if item.id == line_item_id:
                self.line_items.pop(i)
                self.last_modified = datetime.now(timezone.utc)
                return True
        return False
    
    def update_line_item(self, line_item_id: uuid.UUID, **updates) -> bool:
        """Update a line item."""
        if not self.can_be_edited:
            raise BusinessRuleViolationError("Cannot update line items in non-draft purchase order")
        
        for item in self.line_items:
            if item.id == line_item_id:
                for key, value in updates.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
                self.last_modified = datetime.now(timezone.utc)
                return True
        return False
    
    def approve(self, approved_by: str, approval_date: Optional[datetime] = None):
        """Approve the purchase order."""
        if not self.can_be_approved:
            raise BusinessRuleViolationError("Purchase order cannot be approved")
        
        self.approved_by = approved_by
        self.approved_date = approval_date or datetime.now(timezone.utc)
        self.last_modified = datetime.now(timezone.utc)
        
        logger.info(f"Purchase order {self.po_number} approved by {approved_by}")
    
    def reject(self, reason: str):
        """Reject the purchase order."""
        if self.status != PurchaseOrderStatus.DRAFT:
            raise BusinessRuleViolationError("Only draft purchase orders can be rejected")
        
        self.status = PurchaseOrderStatus.CANCELLED
        self.rejection_reason = reason
        self.last_modified = datetime.now(timezone.utc)
        
        logger.info(f"Purchase order {self.po_number} rejected. Reason: {reason}")
    
    def send_to_supplier(self, sent_date: Optional[datetime] = None):
        """Mark purchase order as sent to supplier."""
        if not self.can_be_sent:
            raise BusinessRuleViolationError("Purchase order cannot be sent")
        
        self.status = PurchaseOrderStatus.SENT
        self.sent_date = sent_date or datetime.now(timezone.utc)
        self.last_modified = datetime.now(timezone.utc)
        
        logger.info(f"Purchase order {self.po_number} sent to supplier {self.supplier_name}")
    
    def confirm_order(self):
        """Confirm the purchase order with supplier."""
        if self.status != PurchaseOrderStatus.SENT:
            raise BusinessRuleViolationError("Only sent purchase orders can be confirmed")
        
        self.status = PurchaseOrderStatus.CONFIRMED
        self.last_modified = datetime.now(timezone.utc)
        
        logger.info(f"Purchase order {self.po_number} confirmed by supplier")
    
    def receive_items(self, receipts: List[Dict[str, Any]]):
        """Process receipt of items."""
        if self.status not in [PurchaseOrderStatus.CONFIRMED, PurchaseOrderStatus.PARTIALLY_RECEIVED]:
            raise BusinessRuleViolationError("Cannot receive items for purchase order in current status")
        
        received_any = False
        
        for receipt in receipts:
            line_item_id = receipt.get('line_item_id')
            quantity = receipt.get('quantity', Decimal('0'))
            received_date = receipt.get('received_date', date.today())
            
            # Find the line item
            for item in self.line_items:
                if item.id == line_item_id:
                    try:
                        item.receive_quantity(quantity, received_date)
                        received_any = True
                    except (ValueError, BusinessRuleViolationError) as e:
                        logger.warning(f"Failed to receive quantity for item {item.product_sku}: {e}")
                    break
        
        if received_any:
            # Update purchase order status
            if self.is_fully_received:
                self.status = PurchaseOrderStatus.RECEIVED
                self.actual_delivery_date = date.today()
            else:
                self.status = PurchaseOrderStatus.PARTIALLY_RECEIVED
            
            self.last_modified = datetime.now(timezone.utc)
            logger.info(f"Received items for purchase order {self.po_number}")
    
    def cancel(self, reason: Optional[str] = None):
        """Cancel the purchase order."""
        if self.status in [PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.CLOSED]:
            raise BusinessRuleViolationError("Cannot cancel completed purchase order")
        
        self.status = PurchaseOrderStatus.CANCELLED
        if reason:
            self.rejection_reason = reason
        self.last_modified = datetime.now(timezone.utc)
        
        logger.info(f"Purchase order {self.po_number} cancelled. Reason: {reason or 'Not specified'}")
    
    def close(self):
        """Close the purchase order."""
        if self.status != PurchaseOrderStatus.RECEIVED:
            raise BusinessRuleViolationError("Only fully received purchase orders can be closed")
        
        self.status = PurchaseOrderStatus.CLOSED
        self.last_modified = datetime.now(timezone.utc)
        
        logger.info(f"Purchase order {self.po_number} closed")
    
    def get_line_item(self, line_item_id: uuid.UUID) -> Optional[PurchaseOrderLineItem]:
        """Get a specific line item by ID."""
        for item in self.line_items:
            if item.id == line_item_id:
                return item
        return None
    
    def get_overdue_items(self) -> List[PurchaseOrderLineItem]:
        """Get list of overdue line items."""
        return [item for item in self.line_items if item.is_overdue]
    
    def calculate_delivery_performance(self) -> Dict[str, Any]:
        """Calculate delivery performance metrics."""
        if not self.expected_delivery_date:
            return {"status": "no_expected_date"}
        
        if not self.actual_delivery_date:
            if date.today() > self.expected_delivery_date:
                return {
                    "status": "overdue",
                    "days_overdue": (date.today() - self.expected_delivery_date).days
                }
            else:
                return {
                    "status": "pending",
                    "days_remaining": (self.expected_delivery_date - date.today()).days
                }
        else:
            if self.actual_delivery_date <= self.expected_delivery_date:
                return {
                    "status": "on_time",
                    "days_early": (self.expected_delivery_date - self.actual_delivery_date).days
                }
            else:
                return {
                    "status": "late",
                    "days_late": (self.actual_delivery_date - self.expected_delivery_date).days
                }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert purchase order to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "po_number": self.po_number,
            "supplier_id": str(self.supplier_id),
            "supplier_name": self.supplier_name,
            "supplier_contact_name": self.supplier_contact_name,
            "supplier_email": self.supplier_email,
            "supplier_phone": self.supplier_phone,
            "status": self.status.value,
            "status_display": self.status.get_display(),
            "order_date": self.order_date.isoformat(),
            "expected_delivery_date": self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            "actual_delivery_date": self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            "ship_to_address": self.ship_to_address.to_dict() if self.ship_to_address else None,
            "bill_to_address": self.bill_to_address.to_dict() if self.bill_to_address else None,
            "line_items": [
                {
                    "id": str(item.id),
                    "product_id": str(item.product_id),
                    "product_sku": item.product_sku,
                    "product_name": item.product_name,
                    "description": item.description,
                    "quantity_ordered": float(item.quantity_ordered),
                    "quantity_received": float(item.quantity_received),
                    "quantity_outstanding": float(item.quantity_outstanding),
                    "unit_cost": float(item.unit_cost),
                    "discount_percentage": float(item.discount_percentage) if item.discount_percentage else None,
                    "discount_amount": float(item.discount_amount) if item.discount_amount else None,
                    "tax_rate": float(item.tax_rate),
                    "line_subtotal": float(item.line_subtotal),
                    "tax_amount": float(item.tax_amount),
                    "line_total": float(item.line_total),
                    "unit_of_measure": item.unit_of_measure,
                    "expected_delivery_date": item.expected_delivery_date.isoformat() if item.expected_delivery_date else None,
                    "actual_delivery_date": item.actual_delivery_date.isoformat() if item.actual_delivery_date else None,
                    "is_fully_received": item.is_fully_received,
                    "is_partially_received": item.is_partially_received,
                    "is_overdue": item.is_overdue,
                    "notes": item.notes
                }
                for item in self.line_items
            ],
            "currency": self.currency.value,
            "tax_inclusive": self.tax_inclusive,
            "subtotal": float(self.subtotal),
            "total_tax": float(self.total_tax),
            "shipping_cost": float(self.shipping_cost) if self.shipping_cost else None,
            "handling_cost": float(self.handling_cost) if self.handling_cost else None,
            "other_costs": float(self.other_costs) if self.other_costs else None,
            "additional_costs": float(self.additional_costs),
            "total_amount": float(self.total_amount),
            "total_quantity_ordered": float(self.total_quantity_ordered),
            "total_quantity_received": float(self.total_quantity_received),
            "total_quantity_outstanding": float(self.total_quantity_outstanding),
            "payment_terms": self.payment_terms,
            "discount_terms": self.discount_terms,
            "notes": self.notes,
            "internal_notes": self.internal_notes,
            "reference_number": self.reference_number,
            "requires_approval": self.requires_approval,
            "approved_by": self.approved_by,
            "approved_date": self.approved_date.isoformat() if self.approved_date else None,
            "rejection_reason": self.rejection_reason,
            "is_approved": self.is_approved,
            "is_sent": self.is_sent,
            "is_fully_received": self.is_fully_received,
            "is_partially_received": self.is_partially_received,
            "is_overdue": self.is_overdue,
            "can_be_edited": self.can_be_edited,
            "can_be_approved": self.can_be_approved,
            "can_be_sent": self.can_be_sent,
            "delivery_performance": self.calculate_delivery_performance(),
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "sent_date": self.sent_date.isoformat() if self.sent_date else None
        }
    
    def __str__(self) -> str:
        return f"PurchaseOrder({self.po_number} - {self.supplier_name})"
    
    def __repr__(self) -> str:
        return f"PurchaseOrder(id={self.id}, po_number='{self.po_number}', status='{self.status}')" 