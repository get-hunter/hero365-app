"""
Invoice Domain Entity

Represents an invoice for completed work with comprehensive payment tracking,
status management, and financial calculations.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, Field, field_validator, model_validator, UUID4, BeforeValidator

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError
from .invoice_enums.enums import InvoiceStatus, PaymentStatus
from ..shared.enums import PaymentMethod, CurrencyCode, TaxType, DiscountType
from .estimate_enums.enums import EmailStatus
from ..value_objects.address import Address

# Configure logging
logger = logging.getLogger(__name__)


# Custom Pydantic validators for automatic string-to-enum conversion
def validate_invoice_status(v) -> InvoiceStatus:
    """Convert string to InvoiceStatus enum."""
    if isinstance(v, str):
        logger.debug(f"Converting status string '{v}' to InvoiceStatus enum")
        return InvoiceStatus(v)
    return v

def validate_payment_status(v) -> PaymentStatus:
    """Convert string to PaymentStatus enum."""
    if isinstance(v, str):
        return PaymentStatus(v)
    return v

def validate_payment_method(v) -> PaymentMethod:
    """Convert string to PaymentMethod enum."""
    if isinstance(v, str):
        return PaymentMethod(v)
    return v

def validate_currency_code(v) -> CurrencyCode:
    """Convert string to CurrencyCode enum."""
    if isinstance(v, str):
        return CurrencyCode(v)
    return v

def validate_tax_type(v) -> TaxType:
    """Convert string to TaxType enum."""
    if isinstance(v, str):
        return TaxType(v)
    return v

def validate_discount_type(v) -> DiscountType:
    """Convert string to DiscountType enum."""
    if isinstance(v, str):
        return DiscountType(v)
    return v

def validate_email_status(v) -> EmailStatus:
    """Convert string to EmailStatus enum."""
    if isinstance(v, str):
        return EmailStatus(v)
    return v


class InvoiceLineItem(BaseModel):
    """Value object for invoice line items."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    id: UUID4 = Field(default_factory=uuid.uuid4)
    description: str = Field(default="", min_length=1)
    quantity: Decimal = Field(default=Decimal("1"), gt=0)
    unit_price: Decimal = Field(default=Decimal("0"), ge=0)
    unit: Optional[str] = None
    category: Optional[str] = None
    discount_type: Annotated[DiscountType, BeforeValidator(validate_discount_type)] = DiscountType.NONE
    discount_value: Decimal = Field(default=Decimal("0"), ge=0)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0)
    notes: Optional[str] = None
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate description is not empty."""
        if not v or not v.strip():
            raise ValueError("Line item description is required")
        return v.strip()
    
    @model_validator(mode='after')
    def validate_discount_percentage(self):
        """Validate discount percentage doesn't exceed 100%."""
        discount_type_value = self.discount_type.value if hasattr(self.discount_type, 'value') else self.discount_type
        if discount_type_value == DiscountType.PERCENTAGE.value and self.discount_value > 100:
            raise ValueError("Percentage discount cannot exceed 100%")
        return self
    
    def get_subtotal(self) -> Decimal:
        """Calculate line item subtotal before discount."""
        return self.quantity * self.unit_price
    
    def get_discount_amount(self) -> Decimal:
        """Calculate discount amount."""
        discount_type_value = self.discount_type.value if hasattr(self.discount_type, 'value') else self.discount_type
        if discount_type_value == DiscountType.NONE.value:
            return Decimal("0")
        elif discount_type_value == DiscountType.PERCENTAGE.value:
            return self.get_subtotal() * (self.discount_value / Decimal("100"))
        else:  # FIXED_AMOUNT
            return min(self.discount_value, self.get_subtotal())
    
    def get_total_after_discount(self) -> Decimal:
        """Calculate total after discount, before tax."""
        return self.get_subtotal() - self.get_discount_amount()
    
    def get_tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        return self.get_total_after_discount() * (self.tax_rate / Decimal("100"))
    
    def get_total(self) -> Decimal:
        """Calculate final line item total including tax."""
        return self.get_total_after_discount() + self.get_tax_amount()


class Payment(BaseModel):
    """Value object for invoice payments."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    id: UUID4 = Field(default_factory=uuid.uuid4)
    amount: Decimal = Field(default=Decimal("0"), gt=0)
    payment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payment_method: Annotated[PaymentMethod, BeforeValidator(validate_payment_method)] = PaymentMethod.CASH
    status: Annotated[PaymentStatus, BeforeValidator(validate_payment_status)] = PaymentStatus.COMPLETED
    reference: Optional[str] = None
    transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    processed_by: Optional[str] = None
    refunded_amount: Decimal = Field(default=Decimal("0"), ge=0)
    refund_date: Optional[datetime] = None
    refund_reason: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_refund_amount(self):
        """Validate refunded amount doesn't exceed payment amount."""
        if self.refunded_amount > self.amount:
            raise ValueError("Refunded amount cannot exceed payment amount")
        return self
    
    def get_net_amount(self) -> Decimal:
        """Calculate net payment amount after refunds."""
        return self.amount - self.refunded_amount
    
    def is_fully_refunded(self) -> bool:
        """Check if payment is fully refunded."""
        return self.refunded_amount >= self.amount
    
    def is_partially_refunded(self) -> bool:
        """Check if payment is partially refunded."""
        return self.refunded_amount > 0 and self.refunded_amount < self.amount
    
    def can_refund(self, amount: Decimal) -> bool:
        """Check if a refund amount is valid."""
        return (self.status == PaymentStatus.COMPLETED and 
                amount > 0 and 
                self.refunded_amount + amount <= self.amount)
    
    def process_refund(self, amount: Decimal, reason: Optional[str] = None,
                      processed_by: Optional[str] = None) -> 'Payment':
        """Process a refund for this payment. Returns new Payment instance."""
        if not self.can_refund(amount):
            raise BusinessRuleViolationError("Invalid refund amount")
        
        new_refunded_amount = self.refunded_amount + amount
        new_status = self.status
        
        # Update status based on refund amount
        if new_refunded_amount >= self.amount:
            new_status = PaymentStatus.REFUNDED
        elif new_refunded_amount > 0:
            new_status = PaymentStatus.PARTIALLY_REFUNDED
        
        return self.model_copy(update={
            'refunded_amount': new_refunded_amount,
            'refund_date': datetime.now(timezone.utc),
            'refund_reason': reason,
            'status': new_status
        })


class PaymentTerms(BaseModel):
    """Value object for invoice payment terms."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    net_days: int = Field(default=30, gt=0)
    discount_percentage: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    discount_days: int = Field(default=0, ge=0)
    late_fee_percentage: Decimal = Field(default=Decimal("0"), ge=0)
    late_fee_grace_days: int = Field(default=0, ge=0)
    payment_instructions: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_discount_days(self):
        """Validate discount days don't exceed net days."""
        if self.discount_days > self.net_days:
            raise ValueError("Discount days cannot exceed net days")
        return self
    
    def get_due_date(self, issue_date: date) -> date:
        """Calculate invoice due date."""
        return issue_date + timedelta(days=self.net_days)
    
    def get_discount_date(self, issue_date: date) -> date:
        """Calculate early payment discount date."""
        return issue_date + timedelta(days=self.discount_days)
    
    def is_eligible_for_discount(self, issue_date: date, payment_date: date) -> bool:
        """Check if payment is eligible for early payment discount."""
        return (self.discount_percentage > 0 and 
                payment_date <= self.get_discount_date(issue_date))
    
    def calculate_discount_amount(self, total_amount: Decimal) -> Decimal:
        """Calculate early payment discount amount."""
        return total_amount * (self.discount_percentage / Decimal("100"))
    
    def is_overdue(self, issue_date: date, current_date: Optional[date] = None) -> bool:
        """Check if invoice is overdue."""
        if current_date is None:
            current_date = date.today()
        return current_date > self.get_due_date(issue_date)
    
    def get_late_fee_amount(self, total_amount: Decimal, issue_date: date, 
                           current_date: Optional[date] = None) -> Decimal:
        """Calculate late fee amount."""
        if not self.is_overdue(issue_date, current_date):
            return Decimal("0")
        
        if current_date is None:
            current_date = date.today()
        
        days_overdue = (current_date - self.get_due_date(issue_date)).days
        if days_overdue <= self.late_fee_grace_days:
            return Decimal("0")
        
        return total_amount * (self.late_fee_percentage / Decimal("100"))


class InvoiceEmailTracking(BaseModel):
    """Value object for invoice email tracking."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    id: UUID4 = Field(default_factory=uuid.uuid4)
    sent_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    opened_date: Optional[datetime] = None
    clicked_date: Optional[datetime] = None
    status: Annotated[EmailStatus, BeforeValidator(validate_email_status)] = EmailStatus.PENDING
    recipient_email: Optional[str] = None
    subject: Optional[str] = None
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    tracking_data: Dict[str, Any] = Field(default_factory=dict)
    reminder_type: Optional[str] = None  # 'payment_due', 'overdue', 'thank_you'


class InvoiceStatusHistoryEntry(BaseModel):
    """Value object for invoice status history tracking."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    id: UUID4 = Field(default_factory=uuid.uuid4)
    from_status: Optional[Annotated[InvoiceStatus, BeforeValidator(validate_invoice_status)]] = None
    to_status: Annotated[InvoiceStatus, BeforeValidator(validate_invoice_status)] = InvoiceStatus.DRAFT
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    changed_by: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


class Invoice(BaseModel):
    """
    Invoice domain entity representing a bill for completed work.
    
    Contains comprehensive business logic for payment tracking, status management,
    financial calculations, and client communication.
    """
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    # Core identification
    id: UUID4 = Field(default_factory=uuid.uuid4)
    business_id: UUID4 = Field(default_factory=uuid.uuid4)
    invoice_number: Optional[str] = None
    
    # Status and lifecycle
    status: Annotated[InvoiceStatus, BeforeValidator(validate_invoice_status)] = InvoiceStatus.DRAFT
    status_history: List[InvoiceStatusHistoryEntry] = Field(default_factory=list)
    
    # Client information
    client_id: Optional[UUID4] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    client_address: Optional[Address] = None
    
    # Invoice details
    title: str = Field(default="", min_length=1)
    description: Optional[str] = None
    po_number: Optional[str] = None
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    
    # Financial information
    currency: Annotated[CurrencyCode, BeforeValidator(validate_currency_code)] = CurrencyCode.USD
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0)
    tax_type: Annotated[TaxType, BeforeValidator(validate_tax_type)] = TaxType.PERCENTAGE
    overall_discount_type: Annotated[DiscountType, BeforeValidator(validate_discount_type)] = DiscountType.NONE
    overall_discount_value: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Payment information
    payments: List[Payment] = Field(default_factory=list)
    payment_terms: PaymentTerms = Field(default_factory=PaymentTerms)
    
    # Template and branding
    template_id: Optional[UUID4] = None
    template_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Communication tracking
    email_history: List[InvoiceEmailTracking] = Field(default_factory=list)
    
    # Relationship tracking
    estimate_id: Optional[UUID4] = None  # Source estimate if converted
    project_id: Optional[UUID4] = None
    job_id: Optional[UUID4] = None
    contact_id: Optional[UUID4] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    internal_notes: Optional[str] = None
    
    # Audit fields
    created_by: Optional[str] = None
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sent_date: Optional[datetime] = None
    viewed_date: Optional[datetime] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    paid_date: Optional[datetime] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty."""
        if not v or not v.strip():
            raise ValueError("Invoice title is required")
        return v.strip()
    
    @field_validator('overall_discount_value')
    @classmethod
    def validate_discount_value(cls, v, values):
        """Validate discount value based on type."""
        # Note: In Pydantic v2, we need to use model_validator for cross-field validation
        return v
    
    @model_validator(mode='after')
    def validate_business_rules(self):
        """Validate core business rules and initialize fields."""
        # Helper function to get enum value (handles both string and enum types)
        def get_enum_value(field_value):
            return field_value.value if hasattr(field_value, 'value') else field_value
        
        # Validate discount based on type
        discount_type_value = get_enum_value(self.overall_discount_type)
        if discount_type_value == DiscountType.PERCENTAGE.value and self.overall_discount_value > 100:
            raise ValueError("Percentage discount cannot exceed 100%")
        
        # Get current status value for comparisons
        status_value = get_enum_value(self.status)
        
        # Validate client information for non-draft invoices
        if status_value != InvoiceStatus.DRAFT.value and not self.client_name:
            raise ValueError("Client name is required for sent invoices")
        
        # Validate line items for non-draft invoices
        if not self.line_items and status_value != InvoiceStatus.DRAFT.value:
            raise ValueError("At least one line item is required for sent invoices")
        
        # Set issue_date to created_date if not provided
        if not self.issue_date:
            self.issue_date = self.created_date.date()
        
        # Set due date if not provided
        if not self.due_date and status_value != InvoiceStatus.DRAFT.value:
            self.due_date = self.payment_terms.get_due_date(self.issue_date)
        
        return self
    
    def _generate_invoice_number(self) -> str:
        """Generate invoice number."""
        today = date.today()
        return f"INV-{today.strftime('%Y-%m-%d')}-{str(self.id)[:8].upper()}"
    

    
    # Financial calculation methods
    def get_line_items_subtotal(self) -> Decimal:
        """Calculate total of all line items subtotals."""
        return sum(item.get_subtotal() for item in self.line_items)
    
    def get_line_items_discount_total(self) -> Decimal:
        """Calculate total discount from line items."""
        return sum(item.get_discount_amount() for item in self.line_items)
    
    def get_subtotal_after_line_discounts(self) -> Decimal:
        """Calculate subtotal after line item discounts."""
        return self.get_line_items_subtotal() - self.get_line_items_discount_total()
    
    def get_overall_discount_amount(self) -> Decimal:
        """Calculate overall discount amount."""
        discount_type_value = self.overall_discount_type.value if hasattr(self.overall_discount_type, 'value') else self.overall_discount_type
        if discount_type_value == DiscountType.NONE.value:
            return Decimal("0")
        elif discount_type_value == DiscountType.PERCENTAGE.value:
            return self.get_subtotal_after_line_discounts() * (self.overall_discount_value / Decimal("100"))
        else:  # FIXED_AMOUNT
            return min(self.overall_discount_value, self.get_subtotal_after_line_discounts())
    
    def get_total_before_tax(self) -> Decimal:
        """Calculate total before tax."""
        return self.get_subtotal_after_line_discounts() - self.get_overall_discount_amount()
    
    def get_tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        tax_type_value = self.tax_type.value if hasattr(self.tax_type, 'value') else self.tax_type
        if tax_type_value == TaxType.NONE.value:
            return Decimal("0")
        elif tax_type_value in [TaxType.PERCENTAGE.value, TaxType.EXCLUSIVE.value]:
            return self.get_total_before_tax() * (self.tax_rate / Decimal("100"))
        elif tax_type_value == TaxType.FIXED_AMOUNT.value:
            return self.tax_rate
        else:  # INCLUSIVE tax is already included in line item prices
            return Decimal("0")
    
    def get_total_amount(self) -> Decimal:
        """Calculate invoice total amount."""
        return self.get_total_before_tax() + self.get_tax_amount()
    
    def get_late_fee_amount(self) -> Decimal:
        """Calculate current late fee amount."""
        return self.payment_terms.get_late_fee_amount(
            self.get_total_amount(), 
            self.issue_date
        )
    
    def get_amount_due(self) -> Decimal:
        """Calculate amount due including late fees."""
        return self.get_total_amount() + self.get_late_fee_amount() - self.get_total_payments()
    
    def get_total_payments(self) -> Decimal:
        """Calculate total amount paid."""
        return sum(payment.get_net_amount() for payment in self.payments 
                  if payment.status == PaymentStatus.COMPLETED)
    
    def get_balance_due(self) -> Decimal:
        """Calculate remaining balance due."""
        return max(Decimal("0"), self.get_amount_due())
    
    def round_currency(self, amount: Decimal) -> Decimal:
        """Round amount to currency precision."""
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Payment tracking methods
    def is_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.get_balance_due() == Decimal("0")
    
    def is_partially_paid(self) -> bool:
        """Check if invoice is partially paid."""
        return self.get_total_payments() > 0 and not self.is_paid()
    
    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        if self.is_paid() or not self.due_date:
            return False
        return self.payment_terms.is_overdue(self.issue_date)
    
    def days_overdue(self) -> int:
        """Get number of days overdue."""
        if not self.is_overdue():
            return 0
        return (date.today() - self.due_date).days
    
    def days_until_due(self) -> Optional[int]:
        """Get days until due date."""
        if self.is_paid() or not self.due_date:
            return None
        days = (self.due_date - date.today()).days
        return max(0, days)
    
    # Status management methods
    def can_send(self) -> bool:
        """Check if invoice can be sent."""
        return (self.status == InvoiceStatus.DRAFT and 
                self.client_name and 
                self.line_items and
                (self.client_email or self.client_phone))
    
    def can_mark_paid(self) -> bool:
        """Check if invoice can be marked as paid."""
        return (self.status in [InvoiceStatus.SENT, InvoiceStatus.VIEWED, 
                               InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.OVERDUE] and
                not self.is_paid())
    
    def can_cancel(self) -> bool:
        """Check if invoice can be cancelled."""
        return self.status not in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED]
    
    def send_invoice(self, sent_by: Optional[str] = None) -> 'Invoice':
        """Send invoice to client. Returns new Invoice instance."""
        if not self.can_send():
            raise BusinessRuleViolationError("Invoice cannot be sent in current state")
        
        now = datetime.now(timezone.utc)
        new_due_date = self.due_date or self.payment_terms.get_due_date(self.issue_date)
        
        # Create new status history entry
        new_entry = InvoiceStatusHistoryEntry(
            from_status=self.status,
            to_status=InvoiceStatus.SENT,
            changed_by=sent_by,
            reason="Invoice sent to client"
        )
        
        return self.model_copy(update={
            'status': InvoiceStatus.SENT,
            'sent_date': now,
            'due_date': new_due_date,
            'last_modified': now,
            'status_history': self.status_history + [new_entry]
        })
    
    def mark_as_viewed(self, viewed_by: Optional[str] = None) -> 'Invoice':
        """Mark invoice as viewed by client. Returns new Invoice instance."""
        if self.status == InvoiceStatus.SENT:
            now = datetime.now(timezone.utc)
            new_entry = InvoiceStatusHistoryEntry(
                from_status=self.status,
                to_status=InvoiceStatus.VIEWED,
                changed_by=viewed_by,
                reason="Invoice viewed by client"
            )
            
            return self.model_copy(update={
                'status': InvoiceStatus.VIEWED,
                'viewed_date': now,
                'last_modified': now,
                'status_history': self.status_history + [new_entry]
            })
        return self
    
    def cancel_invoice(self, cancelled_by: Optional[str] = None, reason: Optional[str] = None) -> 'Invoice':
        """Cancel the invoice. Returns new Invoice instance."""
        if not self.can_cancel():
            raise BusinessRuleViolationError("Invoice cannot be cancelled in current state")
        
        now = datetime.now(timezone.utc)
        new_entry = InvoiceStatusHistoryEntry(
            from_status=self.status,
            to_status=InvoiceStatus.CANCELLED,
            changed_by=cancelled_by,
            reason=f"Invoice cancelled. {reason or ''}"
        )
        
        return self.model_copy(update={
            'status': InvoiceStatus.CANCELLED,
            'last_modified': now,
            'status_history': self.status_history + [new_entry]
        })
    
    def update_status(self, new_status: InvoiceStatus, changed_by: Optional[str] = None, 
                     reason: Optional[str] = None) -> 'Invoice':
        """Update invoice status with history tracking. Returns new Invoice instance."""
        if self.status == new_status:
            return self
        
        now = datetime.now(timezone.utc)
        new_entry = InvoiceStatusHistoryEntry(
            from_status=self.status,
            to_status=new_status,
            changed_by=changed_by,
            reason=reason
        )
        
        update_data = {
            'status': new_status,
            'last_modified': now,
            'status_history': self.status_history + [new_entry]
        }
        
        # Set paid date if marked as paid
        if new_status == InvoiceStatus.PAID and not self.paid_date:
            update_data['paid_date'] = now
        
        return self.model_copy(update=update_data)
    
    def _update_status_based_on_payments(self) -> 'Invoice':
        """Update status based on payment amounts. Returns new Invoice instance."""
        if self.is_paid():
            if self.status != InvoiceStatus.PAID:
                return self.update_status(InvoiceStatus.PAID, None, "Fully paid")
        elif self.is_partially_paid():
            if self.status not in [InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.OVERDUE]:
                return self.update_status(InvoiceStatus.PARTIALLY_PAID, None, "Partially paid")
        
        # Check for overdue status
        if self.is_overdue() and self.status not in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED]:
            if self.is_partially_paid():
                return self.update_status(InvoiceStatus.OVERDUE, None, "Invoice overdue with partial payment")
            else:
                return self.update_status(InvoiceStatus.OVERDUE, None, "Invoice overdue")
        
        return self
    
    def add_status_history_entry(self, from_status: Optional[InvoiceStatus], 
                               to_status: InvoiceStatus, changed_by: Optional[str] = None,
                               reason: Optional[str] = None) -> 'Invoice':
        """Add entry to status history. Returns new Invoice instance."""
        entry = InvoiceStatusHistoryEntry(
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            reason=reason
        )
        
        new_history = self.status_history + [entry]
        
        # Keep only last 20 entries
        if len(new_history) > 20:
            new_history = new_history[-20:]
        
        return self.model_copy(update={'status_history': new_history})
    
    # Payment management methods
    def add_payment(self, amount: Decimal, payment_method: PaymentMethod = PaymentMethod.CASH,
                   reference: Optional[str] = None, transaction_id: Optional[str] = None,
                   notes: Optional[str] = None, processed_by: Optional[str] = None) -> tuple['Invoice', Payment]:
        """Add a payment to the invoice. Returns new Invoice instance and Payment."""
        if amount <= 0:
            raise DomainValidationError("Payment amount must be positive")
        
        if amount > self.get_amount_due():
            raise DomainValidationError("Payment amount cannot exceed amount due")
        
        payment = Payment(
            amount=amount,
            payment_method=payment_method,
            reference=reference,
            transaction_id=transaction_id,
            notes=notes,
            processed_by=processed_by
        )
        
        # Create new invoice with payment added
        invoice_with_payment = self.model_copy(update={
            'payments': self.payments + [payment],
            'last_modified': datetime.now(timezone.utc)
        })
        
        # Update status based on payments
        final_invoice = invoice_with_payment._update_status_based_on_payments()
        
        return final_invoice, payment
    
    def process_refund(self, payment_id: uuid.UUID, amount: Decimal, 
                      reason: Optional[str] = None, processed_by: Optional[str] = None) -> tuple['Invoice', bool]:
        """Process a refund for a specific payment. Returns new Invoice instance and success flag."""
        for i, payment in enumerate(self.payments):
            if payment.id == payment_id:
                updated_payment = payment.process_refund(amount, reason, processed_by)
                
                # Create new payments list with updated payment
                new_payments = self.payments.copy()
                new_payments[i] = updated_payment
                
                # Create new invoice with updated payments
                invoice_with_refund = self.model_copy(update={
                    'payments': new_payments,
                    'last_modified': datetime.now(timezone.utc)
                })
                
                # Update status if fully refunded
                if all(p.is_fully_refunded() for p in new_payments if p.status == PaymentStatus.COMPLETED):
                    final_invoice = invoice_with_refund.update_status(InvoiceStatus.REFUNDED, processed_by, "Invoice fully refunded")
                    return final_invoice, True
                
                return invoice_with_refund, True
        
        return self, False
    
    def mark_as_paid(self, marked_by: Optional[str] = None, payment_method: PaymentMethod = PaymentMethod.CASH,
                    reference: Optional[str] = None) -> 'Invoice':
        """Mark invoice as fully paid. Returns new Invoice instance."""
        if not self.can_mark_paid():
            raise BusinessRuleViolationError("Invoice cannot be marked as paid")
        
        remaining_balance = self.get_balance_due()
        if remaining_balance > 0:
            final_invoice, _ = self.add_payment(
                amount=remaining_balance,
                payment_method=payment_method,
                reference=reference,
                notes="Manual payment entry",
                processed_by=marked_by
            )
            return final_invoice
        
        return self
    
    # Line item management
    def add_line_item(self, description: str, quantity: Decimal, unit_price: Decimal,
                     unit: Optional[str] = None, category: Optional[str] = None,
                     discount_type: DiscountType = DiscountType.NONE,
                     discount_value: Decimal = Decimal("0"),
                     tax_rate: Decimal = Decimal("0"),
                     notes: Optional[str] = None) -> tuple['Invoice', InvoiceLineItem]:
        """Add a line item to the invoice. Returns new Invoice instance and line item."""
        line_item = InvoiceLineItem(
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            unit=unit,
            category=category,
            discount_type=discount_type,
            discount_value=discount_value,
            tax_rate=tax_rate,
            notes=notes
        )
        
        new_invoice = self.model_copy(update={
            'line_items': self.line_items + [line_item],
            'last_modified': datetime.now(timezone.utc)
        })
        
        return new_invoice, line_item
    
    def remove_line_item(self, line_item_id: uuid.UUID) -> tuple['Invoice', bool]:
        """Remove a line item from the invoice. Returns new Invoice instance and success flag."""
        for i, item in enumerate(self.line_items):
            if item.id == line_item_id:
                new_line_items = self.line_items.copy()
                del new_line_items[i]
                
                new_invoice = self.model_copy(update={
                    'line_items': new_line_items,
                    'last_modified': datetime.now(timezone.utc)
                })
                
                return new_invoice, True
        return self, False
    
    def update_line_item(self, line_item_id: uuid.UUID, **updates) -> tuple['Invoice', bool]:
        """Update a line item. Returns new Invoice instance and success flag."""
        for i, item in enumerate(self.line_items):
            if item.id == line_item_id:
                # Create updated line item using Pydantic's model_copy
                updated_item = item.model_copy(update=updates)
                
                # Create new line items list with updated item
                new_line_items = self.line_items.copy()
                new_line_items[i] = updated_item
                
                new_invoice = self.model_copy(update={
                    'line_items': new_line_items,
                    'last_modified': datetime.now(timezone.utc)
                })
                
                return new_invoice, True
        return self, False
    
    # Email tracking
    def add_email_tracking(self, recipient_email: str, subject: str, 
                          reminder_type: Optional[str] = None) -> tuple['Invoice', InvoiceEmailTracking]:
        """Add email tracking entry. Returns new Invoice instance and tracking entry."""
        tracking = InvoiceEmailTracking(
            recipient_email=recipient_email,
            subject=subject,
            sent_date=datetime.now(timezone.utc),
            status=EmailStatus.SENT,
            reminder_type=reminder_type
        )
        
        new_email_history = self.email_history + [tracking]
        
        # Keep only last 10 email tracking entries
        if len(new_email_history) > 10:
            new_email_history = new_email_history[-10:]
        
        new_invoice = self.model_copy(update={'email_history': new_email_history})
        
        return new_invoice, tracking
    
    def update_email_tracking(self, tracking_id: uuid.UUID, status: EmailStatus,
                            **tracking_data) -> tuple['Invoice', bool]:
        """Update email tracking status. Returns new Invoice instance and success flag."""
        for i, tracking in enumerate(self.email_history):
            if tracking.id == tracking_id:
                now = datetime.now(timezone.utc)
                update_data = {'status': status}
                
                if status == EmailStatus.DELIVERED:
                    update_data['delivered_date'] = now
                elif status == EmailStatus.OPENED:
                    update_data['opened_date'] = now
                elif status == EmailStatus.CLICKED:
                    update_data['clicked_date'] = now
                
                # Update tracking data
                new_tracking_data = tracking.tracking_data.copy()
                new_tracking_data.update(tracking_data)
                update_data['tracking_data'] = new_tracking_data
                
                # Create updated tracking entry
                updated_tracking = tracking.model_copy(update=update_data)
                
                # Create new email history with updated entry
                new_email_history = self.email_history.copy()
                new_email_history[i] = updated_tracking
                
                new_invoice = self.model_copy(update={'email_history': new_email_history})
                
                return new_invoice, True
        return self, False
    
    # Utility methods
    def add_tag(self, tag: str) -> 'Invoice':
        """Add a tag to the invoice. Returns new Invoice instance."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            return self.model_copy(update={
                'tags': self.tags + [tag],
                'last_modified': datetime.now(timezone.utc)
            })
        return self
    
    def remove_tag(self, tag: str) -> 'Invoice':
        """Remove a tag from the invoice. Returns new Invoice instance."""
        tag = tag.strip().lower()
        if tag in self.tags:
            new_tags = [t for t in self.tags if t != tag]
            return self.model_copy(update={
                'tags': new_tags,
                'last_modified': datetime.now(timezone.utc)
            })
        return self
    
    def set_custom_field(self, field_name: str, value: Any) -> 'Invoice':
        """Set a custom field value. Returns new Invoice instance."""
        new_custom_fields = self.custom_fields.copy()
        new_custom_fields[field_name] = value
        
        return self.model_copy(update={
            'custom_fields': new_custom_fields,
            'last_modified': datetime.now(timezone.utc)
        })
    
    def get_custom_field(self, field_name: str, default: Any = None) -> Any:
        """Get a custom field value."""
        return self.custom_fields.get(field_name, default)
    
    # Display methods
    def get_status_display(self) -> str:
        """Get human-readable status."""
        if hasattr(self.status, 'get_display'):
            return self.status.get_display()
        return str(self.status)
    
    def get_currency_display(self) -> str:
        """Get human-readable currency."""
        if hasattr(self.currency, 'get_display'):
            return self.currency.get_display()
        return str(self.currency)
    
    def get_client_display_name(self) -> str:
        """Get client display name."""
        return self.client_name or "Unknown Client"
    
    def get_total_display(self) -> str:
        """Get formatted total amount."""
        total = self.round_currency(self.get_total_amount())
        currency_value = self.currency.value if hasattr(self.currency, 'value') else str(self.currency)
        return f"{currency_value} {total:,.2f}"
    
    def get_balance_display(self) -> str:
        """Get formatted balance due."""
        balance = self.round_currency(self.get_balance_due())
        currency_value = self.currency.value if hasattr(self.currency, 'value') else str(self.currency)
        return f"{currency_value} {balance:,.2f}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert invoice to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "invoice_number": self.invoice_number,
            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),
            "status_display": self.get_status_display(),
            "client_id": str(self.client_id) if self.client_id else None,
            "client_name": self.client_name,
            "client_email": self.client_email,
            "client_phone": self.client_phone,
            "client_address": self.client_address.to_dict() if self.client_address else None,
            "title": self.title,
            "description": self.description,
            "po_number": self.po_number,
            "line_items": [
                {
                    "id": str(item.id),
                    "description": item.description,
                    "quantity": float(item.quantity),
                    "unit_price": float(item.unit_price),
                    "unit": item.unit,
                    "category": item.category,
                    "discount_type": item.discount_type.value if hasattr(item.discount_type, 'value') else str(item.discount_type),
                    "discount_value": float(item.discount_value),
                    "tax_rate": float(item.tax_rate),
                    "subtotal": float(item.get_subtotal()),
                    "discount_amount": float(item.get_discount_amount()),
                    "total": float(item.get_total()),
                    "notes": item.notes
                }
                for item in self.line_items
            ],
            "currency": self.currency.value if hasattr(self.currency, 'value') else str(self.currency),
            "tax_rate": float(self.tax_rate),
            "tax_type": self.tax_type.value if hasattr(self.tax_type, 'value') else str(self.tax_type),
            "overall_discount_type": self.overall_discount_type.value if hasattr(self.overall_discount_type, 'value') else str(self.overall_discount_type),
            "overall_discount_value": float(self.overall_discount_value),
            "payments": [
                {
                    "id": str(payment.id),
                    "amount": float(payment.amount),
                    "payment_date": payment.payment_date.isoformat(),
                    "payment_method": payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method),
                    "status": payment.status.value if hasattr(payment.status, 'value') else str(payment.status),
                    "reference": payment.reference,
                    "transaction_id": payment.transaction_id,
                    "notes": payment.notes,
                    "processed_by": payment.processed_by,
                    "refunded_amount": float(payment.refunded_amount),
                    "net_amount": float(payment.get_net_amount())
                }
                for payment in self.payments
            ],
            "payment_terms": {
                "net_days": self.payment_terms.net_days,
                "discount_percentage": float(self.payment_terms.discount_percentage),
                "discount_days": self.payment_terms.discount_days,
                "late_fee_percentage": float(self.payment_terms.late_fee_percentage),
                "late_fee_grace_days": self.payment_terms.late_fee_grace_days,
                "payment_instructions": self.payment_terms.payment_instructions
            },
            "template_id": str(self.template_id) if self.template_id else None,
            "estimate_id": str(self.estimate_id) if self.estimate_id else None,
            "project_id": str(self.project_id) if self.project_id else None,
            "job_id": str(self.job_id) if self.job_id else None,
            "contact_id": str(self.contact_id) if self.contact_id else None,
            "tags": self.tags,
            "custom_fields": self.custom_fields,
            "internal_notes": self.internal_notes,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "sent_date": self.sent_date.isoformat() if self.sent_date else None,
            "viewed_date": self.viewed_date.isoformat() if self.viewed_date else None,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "paid_date": self.paid_date.isoformat() if self.paid_date else None,
            # Calculated fields
            "line_items_subtotal": float(self.get_line_items_subtotal()),
            "total_discount": float(self.get_line_items_discount_total() + self.get_overall_discount_amount()),
            "tax_amount": float(self.get_tax_amount()),
            "total_amount": float(self.get_total_amount()),
            "late_fee_amount": float(self.get_late_fee_amount()),
            "amount_due": float(self.get_amount_due()),
            "total_payments": float(self.get_total_payments()),
            "balance_due": float(self.get_balance_due()),
            "is_paid": self.is_paid(),
            "is_partially_paid": self.is_partially_paid(),
            "is_overdue": self.is_overdue(),
            "days_overdue": self.days_overdue(),
            "days_until_due": self.days_until_due(),
            "total_display": self.get_total_display(),
            "balance_display": self.get_balance_display()
        }
    
    def __str__(self) -> str:
        return f"Invoice({self.invoice_number} - {self.get_client_display_name()} - {self.get_status_display()})"
    
    def __repr__(self) -> str:
        return (f"Invoice(id={self.id}, number={self.invoice_number}, "
                f"client={self.client_name}, status={self.status}, "
                f"total={self.get_total_amount()}, balance={self.get_balance_due()})") 