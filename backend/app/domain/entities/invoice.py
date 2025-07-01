"""
Invoice Domain Entity

Represents an invoice for completed work with comprehensive payment tracking,
status management, and financial calculations.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, date, timezone, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal, ROUND_HALF_UP

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError
from ..enums import (
    InvoiceStatus, PaymentStatus, PaymentMethod, CurrencyCode, 
    TaxType, DiscountType, EmailStatus
)
from ..value_objects.address import Address


@dataclass
class InvoiceLineItem:
    """Value object for invoice line items."""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    description: str = ""
    quantity: Decimal = Decimal("1")
    unit_price: Decimal = Decimal("0")
    unit: Optional[str] = None
    category: Optional[str] = None
    discount_type: DiscountType = DiscountType.NONE
    discount_value: Decimal = Decimal("0")
    tax_rate: Decimal = Decimal("0")
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate line item data."""
        if not self.description or not self.description.strip():
            raise DomainValidationError("Line item description is required")
        
        if self.quantity <= 0:
            raise DomainValidationError("Quantity must be positive")
        
        if self.unit_price < 0:
            raise DomainValidationError("Unit price cannot be negative")
        
        if self.discount_value < 0:
            raise DomainValidationError("Discount value cannot be negative")
        
        if self.tax_rate < 0:
            raise DomainValidationError("Tax rate cannot be negative")
        
        # Validate discount based on type
        if self.discount_type == DiscountType.PERCENTAGE and self.discount_value > 100:
            raise DomainValidationError("Percentage discount cannot exceed 100%")
    
    def get_subtotal(self) -> Decimal:
        """Calculate line item subtotal before discount."""
        return self.quantity * self.unit_price
    
    def get_discount_amount(self) -> Decimal:
        """Calculate discount amount."""
        if self.discount_type == DiscountType.NONE:
            return Decimal("0")
        elif self.discount_type == DiscountType.PERCENTAGE:
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


@dataclass
class Payment:
    """Value object for invoice payments."""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    amount: Decimal = Decimal("0")
    payment_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payment_method: PaymentMethod = PaymentMethod.CASH
    status: PaymentStatus = PaymentStatus.COMPLETED
    reference: Optional[str] = None
    transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    processed_by: Optional[str] = None
    refunded_amount: Decimal = Decimal("0")
    refund_date: Optional[datetime] = None
    refund_reason: Optional[str] = None
    
    def __post_init__(self):
        """Validate payment data."""
        if self.amount <= 0:
            raise DomainValidationError("Payment amount must be positive")
        
        if self.refunded_amount < 0:
            raise DomainValidationError("Refunded amount cannot be negative")
        
        if self.refunded_amount > self.amount:
            raise DomainValidationError("Refunded amount cannot exceed payment amount")
    
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
                      processed_by: Optional[str] = None) -> None:
        """Process a refund for this payment."""
        if not self.can_refund(amount):
            raise BusinessRuleViolationError("Invalid refund amount")
        
        self.refunded_amount += amount
        self.refund_date = datetime.now(timezone.utc)
        self.refund_reason = reason
        
        # Update status based on refund amount
        if self.is_fully_refunded():
            self.status = PaymentStatus.REFUNDED
        elif self.is_partially_refunded():
            self.status = PaymentStatus.PARTIALLY_REFUNDED


@dataclass
class PaymentTerms:
    """Value object for invoice payment terms."""
    net_days: int = 30
    discount_percentage: Decimal = Decimal("0")
    discount_days: int = 0
    late_fee_percentage: Decimal = Decimal("0")
    late_fee_grace_days: int = 0
    payment_instructions: Optional[str] = None
    
    def __post_init__(self):
        """Validate payment terms."""
        if self.net_days <= 0:
            raise DomainValidationError("Net days must be positive")
        
        if self.discount_percentage < 0 or self.discount_percentage > 100:
            raise DomainValidationError("Discount percentage must be between 0 and 100")
        
        if self.late_fee_percentage < 0:
            raise DomainValidationError("Late fee percentage cannot be negative")
        
        if self.discount_days > self.net_days:
            raise DomainValidationError("Discount days cannot exceed net days")
    
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


@dataclass
class InvoiceEmailTracking:
    """Value object for invoice email tracking."""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    sent_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    opened_date: Optional[datetime] = None
    clicked_date: Optional[datetime] = None
    status: EmailStatus = EmailStatus.PENDING
    recipient_email: Optional[str] = None
    subject: Optional[str] = None
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    tracking_data: Dict[str, Any] = field(default_factory=dict)
    reminder_type: Optional[str] = None  # 'payment_due', 'overdue', 'thank_you'


@dataclass
class InvoiceStatusHistoryEntry:
    """Value object for invoice status history tracking."""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    from_status: Optional[InvoiceStatus] = None
    to_status: InvoiceStatus = InvoiceStatus.DRAFT
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    changed_by: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Invoice:
    """
    Invoice domain entity representing a bill for completed work.
    
    Contains comprehensive business logic for payment tracking, status management,
    financial calculations, and client communication.
    """
    
    # Core identification
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    business_id: uuid.UUID = field(default_factory=uuid.uuid4)
    invoice_number: Optional[str] = None
    
    # Status and lifecycle
    status: InvoiceStatus = InvoiceStatus.DRAFT
    status_history: List[InvoiceStatusHistoryEntry] = field(default_factory=list)
    
    # Client information
    client_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    client_address: Optional[Address] = None
    
    # Invoice details
    title: str = ""
    description: Optional[str] = None
    po_number: Optional[str] = None
    line_items: List[InvoiceLineItem] = field(default_factory=list)
    
    # Financial information
    currency: CurrencyCode = CurrencyCode.USD
    tax_rate: Decimal = Decimal("0")
    tax_type: TaxType = TaxType.PERCENTAGE
    overall_discount_type: DiscountType = DiscountType.NONE
    overall_discount_value: Decimal = Decimal("0")
    
    # Payment information
    payments: List[Payment] = field(default_factory=list)
    payment_terms: PaymentTerms = field(default_factory=PaymentTerms)
    
    # Template and branding
    template_id: Optional[uuid.UUID] = None
    template_data: Dict[str, Any] = field(default_factory=dict)
    
    # Communication tracking
    email_history: List[InvoiceEmailTracking] = field(default_factory=list)
    
    # Relationship tracking
    estimate_id: Optional[uuid.UUID] = None  # Source estimate if converted
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    contact_id: Optional[uuid.UUID] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    internal_notes: Optional[str] = None
    
    # Audit fields
    created_by: Optional[str] = None
    created_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sent_date: Optional[datetime] = None
    viewed_date: Optional[datetime] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    paid_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize and validate invoice."""
        if not self.title or not self.title.strip():
            raise DomainValidationError("Invoice title is required")
        
        if not self.business_id:
            raise DomainValidationError("Business ID is required")
        
        # Set issue_date to created_date if not provided
        if not self.issue_date:
            self.issue_date = self.created_date.date()
        
        # Generate invoice number if not provided
        if not self.invoice_number:
            self.invoice_number = self._generate_invoice_number()
        
        # Set due date if not provided
        if not self.due_date and self.status != InvoiceStatus.DRAFT:
            self.due_date = self.payment_terms.get_due_date(self.issue_date)
        
        # Initialize status history if empty
        if not self.status_history:
            self.add_status_history_entry(None, self.status, self.created_by, "Initial status")
        
        self._validate_business_rules()
    
    def _generate_invoice_number(self) -> str:
        """Generate invoice number."""
        today = date.today()
        return f"INV-{today.strftime('%Y-%m-%d')}-{str(self.id)[:8].upper()}"
    
    def _validate_business_rules(self) -> None:
        """Validate core business rules."""
        # Validate financial values
        if self.tax_rate < 0:
            raise DomainValidationError("Tax rate cannot be negative")
        
        if self.overall_discount_value < 0:
            raise DomainValidationError("Overall discount value cannot be negative")
        
        if self.overall_discount_type == DiscountType.PERCENTAGE and self.overall_discount_value > 100:
            raise DomainValidationError("Percentage discount cannot exceed 100%")
        
        # Validate client information
        if self.status != InvoiceStatus.DRAFT and not self.client_name:
            raise DomainValidationError("Client name is required for sent invoices")
        
        # Validate line items
        if not self.line_items and self.status != InvoiceStatus.DRAFT:
            raise DomainValidationError("At least one line item is required for sent invoices")
    
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
        if self.overall_discount_type == DiscountType.NONE:
            return Decimal("0")
        elif self.overall_discount_type == DiscountType.PERCENTAGE:
            return self.get_subtotal_after_line_discounts() * (self.overall_discount_value / Decimal("100"))
        else:  # FIXED_AMOUNT
            return min(self.overall_discount_value, self.get_subtotal_after_line_discounts())
    
    def get_total_before_tax(self) -> Decimal:
        """Calculate total before tax."""
        return self.get_subtotal_after_line_discounts() - self.get_overall_discount_amount()
    
    def get_tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        if self.tax_type == TaxType.NONE:
            return Decimal("0")
        elif self.tax_type in [TaxType.PERCENTAGE, TaxType.EXCLUSIVE]:
            return self.get_total_before_tax() * (self.tax_rate / Decimal("100"))
        elif self.tax_type == TaxType.FIXED_AMOUNT:
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
    
    def send_invoice(self, sent_by: Optional[str] = None) -> None:
        """Send invoice to client."""
        if not self.can_send():
            raise BusinessRuleViolationError("Invoice cannot be sent in current state")
        
        self.update_status(InvoiceStatus.SENT, sent_by, "Invoice sent to client")
        self.sent_date = datetime.now(timezone.utc)
        
        # Set due date if not already set
        if not self.due_date:
            self.due_date = self.payment_terms.get_due_date(self.issue_date)
    
    def mark_as_viewed(self, viewed_by: Optional[str] = None) -> None:
        """Mark invoice as viewed by client."""
        if self.status == InvoiceStatus.SENT:
            self.update_status(InvoiceStatus.VIEWED, viewed_by, "Invoice viewed by client")
            self.viewed_date = datetime.now(timezone.utc)
    
    def cancel_invoice(self, cancelled_by: Optional[str] = None, reason: Optional[str] = None) -> None:
        """Cancel the invoice."""
        if not self.can_cancel():
            raise BusinessRuleViolationError("Invoice cannot be cancelled in current state")
        
        self.update_status(InvoiceStatus.CANCELLED, cancelled_by, f"Invoice cancelled. {reason or ''}")
    
    def update_status(self, new_status: InvoiceStatus, changed_by: Optional[str] = None, 
                     reason: Optional[str] = None) -> None:
        """Update invoice status with history tracking."""
        if self.status == new_status:
            return
        
        old_status = self.status
        self.status = new_status
        self.last_modified = datetime.now(timezone.utc)
        
        # Set paid date if marked as paid
        if new_status == InvoiceStatus.PAID and not self.paid_date:
            self.paid_date = datetime.now(timezone.utc)
        
        self.add_status_history_entry(old_status, new_status, changed_by, reason)
    
    def _update_status_based_on_payments(self) -> None:
        """Update status based on payment amounts."""
        if self.is_paid():
            if self.status != InvoiceStatus.PAID:
                self.update_status(InvoiceStatus.PAID, None, "Fully paid")
        elif self.is_partially_paid():
            if self.status not in [InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.OVERDUE]:
                self.update_status(InvoiceStatus.PARTIALLY_PAID, None, "Partially paid")
        
        # Check for overdue status
        if self.is_overdue() and self.status not in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED]:
            if self.is_partially_paid():
                self.update_status(InvoiceStatus.OVERDUE, None, "Invoice overdue with partial payment")
            else:
                self.update_status(InvoiceStatus.OVERDUE, None, "Invoice overdue")
    
    def add_status_history_entry(self, from_status: Optional[InvoiceStatus], 
                               to_status: InvoiceStatus, changed_by: Optional[str] = None,
                               reason: Optional[str] = None) -> None:
        """Add entry to status history."""
        entry = InvoiceStatusHistoryEntry(
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            reason=reason
        )
        self.status_history.append(entry)
        
        # Keep only last 20 entries
        if len(self.status_history) > 20:
            self.status_history = self.status_history[-20:]
    
    # Payment management methods
    def add_payment(self, amount: Decimal, payment_method: PaymentMethod = PaymentMethod.CASH,
                   reference: Optional[str] = None, transaction_id: Optional[str] = None,
                   notes: Optional[str] = None, processed_by: Optional[str] = None) -> Payment:
        """Add a payment to the invoice."""
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
        
        self.payments.append(payment)
        self.last_modified = datetime.now(timezone.utc)
        
        # Update status based on payments
        self._update_status_based_on_payments()
        
        return payment
    
    def process_refund(self, payment_id: uuid.UUID, amount: Decimal, 
                      reason: Optional[str] = None, processed_by: Optional[str] = None) -> bool:
        """Process a refund for a specific payment."""
        for payment in self.payments:
            if payment.id == payment_id:
                payment.process_refund(amount, reason, processed_by)
                self.last_modified = datetime.now(timezone.utc)
                
                # Update status if fully refunded
                if all(p.is_fully_refunded() for p in self.payments if p.status == PaymentStatus.COMPLETED):
                    self.update_status(InvoiceStatus.REFUNDED, processed_by, "Invoice fully refunded")
                
                return True
        return False
    
    def mark_as_paid(self, marked_by: Optional[str] = None, payment_method: PaymentMethod = PaymentMethod.CASH,
                    reference: Optional[str] = None) -> None:
        """Mark invoice as fully paid."""
        if not self.can_mark_paid():
            raise BusinessRuleViolationError("Invoice cannot be marked as paid")
        
        remaining_balance = self.get_balance_due()
        if remaining_balance > 0:
            self.add_payment(
                amount=remaining_balance,
                payment_method=payment_method,
                reference=reference,
                notes="Manual payment entry",
                processed_by=marked_by
            )
    
    # Line item management
    def add_line_item(self, description: str, quantity: Decimal, unit_price: Decimal,
                     unit: Optional[str] = None, category: Optional[str] = None,
                     discount_type: DiscountType = DiscountType.NONE,
                     discount_value: Decimal = Decimal("0"),
                     tax_rate: Decimal = Decimal("0"),
                     notes: Optional[str] = None) -> InvoiceLineItem:
        """Add a line item to the invoice."""
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
        self.line_items.append(line_item)
        self.last_modified = datetime.now(timezone.utc)
        return line_item
    
    def remove_line_item(self, line_item_id: uuid.UUID) -> bool:
        """Remove a line item from the invoice."""
        for i, item in enumerate(self.line_items):
            if item.id == line_item_id:
                del self.line_items[i]
                self.last_modified = datetime.now(timezone.utc)
                return True
        return False
    
    def update_line_item(self, line_item_id: uuid.UUID, **updates) -> bool:
        """Update a line item."""
        for item in self.line_items:
            if item.id == line_item_id:
                for key, value in updates.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
                self.last_modified = datetime.now(timezone.utc)
                return True
        return False
    
    # Email tracking
    def add_email_tracking(self, recipient_email: str, subject: str, 
                          reminder_type: Optional[str] = None) -> InvoiceEmailTracking:
        """Add email tracking entry."""
        tracking = InvoiceEmailTracking(
            recipient_email=recipient_email,
            subject=subject,
            sent_date=datetime.now(timezone.utc),
            status=EmailStatus.SENT,
            reminder_type=reminder_type
        )
        self.email_history.append(tracking)
        
        # Keep only last 10 email tracking entries
        if len(self.email_history) > 10:
            self.email_history = self.email_history[-10:]
        
        return tracking
    
    def update_email_tracking(self, tracking_id: uuid.UUID, status: EmailStatus,
                            **tracking_data) -> bool:
        """Update email tracking status."""
        for tracking in self.email_history:
            if tracking.id == tracking_id:
                tracking.status = status
                if status == EmailStatus.DELIVERED:
                    tracking.delivered_date = datetime.now(timezone.utc)
                elif status == EmailStatus.OPENED:
                    tracking.opened_date = datetime.now(timezone.utc)
                elif status == EmailStatus.CLICKED:
                    tracking.clicked_date = datetime.now(timezone.utc)
                
                tracking.tracking_data.update(tracking_data)
                return True
        return False
    
    # Utility methods
    def add_tag(self, tag: str) -> None:
        """Add a tag to the invoice."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.last_modified = datetime.now(timezone.utc)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the invoice."""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.last_modified = datetime.now(timezone.utc)
    
    def set_custom_field(self, field_name: str, value: Any) -> None:
        """Set a custom field value."""
        self.custom_fields[field_name] = value
        self.last_modified = datetime.now(timezone.utc)
    
    def get_custom_field(self, field_name: str, default: Any = None) -> Any:
        """Get a custom field value."""
        return self.custom_fields.get(field_name, default)
    
    # Display methods
    def get_status_display(self) -> str:
        """Get human-readable status."""
        return self.status.get_display()
    
    def get_currency_display(self) -> str:
        """Get human-readable currency."""
        return self.currency.get_display()
    
    def get_client_display_name(self) -> str:
        """Get client display name."""
        return self.client_name or "Unknown Client"
    
    def get_total_display(self) -> str:
        """Get formatted total amount."""
        total = self.round_currency(self.get_total_amount())
        return f"{self.currency.value} {total:,.2f}"
    
    def get_balance_display(self) -> str:
        """Get formatted balance due."""
        balance = self.round_currency(self.get_balance_due())
        return f"{self.currency.value} {balance:,.2f}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert invoice to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "invoice_number": self.invoice_number,
            "status": self.status.value,
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
                    "discount_type": item.discount_type.value,
                    "discount_value": float(item.discount_value),
                    "tax_rate": float(item.tax_rate),
                    "subtotal": float(item.get_subtotal()),
                    "discount_amount": float(item.get_discount_amount()),
                    "total": float(item.get_total()),
                    "notes": item.notes
                }
                for item in self.line_items
            ],
            "currency": self.currency.value,
            "tax_rate": float(self.tax_rate),
            "tax_type": self.tax_type.value,
            "overall_discount_type": self.overall_discount_type.value,
            "overall_discount_value": float(self.overall_discount_value),
            "payments": [
                {
                    "id": str(payment.id),
                    "amount": float(payment.amount),
                    "payment_date": payment.payment_date.isoformat(),
                    "payment_method": payment.payment_method.value,
                    "status": payment.status.value,
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