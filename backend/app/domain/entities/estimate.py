"""
Estimate Domain Entity

Represents an estimate for work to be performed with comprehensive business rules,
financial calculations, status management, and client communication tracking.
"""

import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime, date, timezone, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal, ROUND_HALF_UP

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError
from ..enums import (
    EstimateStatus, CurrencyCode, TaxType, DiscountType, 
    AdvancePaymentType, EmailStatus, TemplateType, DocumentType
)
from ..value_objects.address import Address

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class EstimateLineItem:
    """Value object for estimate line items."""
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
class AdvancePayment:
    """Value object for advance payment requirements."""
    required: bool = False
    type: AdvancePaymentType = AdvancePaymentType.NONE
    value: Decimal = Decimal("0")
    due_date: Optional[date] = None
    collected_amount: Decimal = Decimal("0")
    collected_date: Optional[datetime] = None
    collection_method: Optional[str] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate advance payment data."""
        if self.required and self.type == AdvancePaymentType.NONE:
            raise DomainValidationError("Advance payment type required when advance payment is required")
        
        if self.value < 0:
            raise DomainValidationError("Advance payment value cannot be negative")
        
        if self.collected_amount < 0:
            raise DomainValidationError("Collected amount cannot be negative")
        
        if self.type == AdvancePaymentType.PERCENTAGE and self.value > 100:
            raise DomainValidationError("Percentage advance payment cannot exceed 100%")
    
    def get_required_amount(self, estimate_total: Decimal) -> Decimal:
        """Calculate required advance payment amount."""
        if not self.required or self.type == AdvancePaymentType.NONE:
            return Decimal("0")
        elif self.type == AdvancePaymentType.PERCENTAGE:
            return estimate_total * (self.value / Decimal("100"))
        else:  # FIXED_AMOUNT
            return self.value
    
    def get_remaining_amount(self, estimate_total: Decimal) -> Decimal:
        """Calculate remaining advance payment amount."""
        required = self.get_required_amount(estimate_total)
        return max(Decimal("0"), required - self.collected_amount)
    
    def is_fully_collected(self, estimate_total: Decimal) -> bool:
        """Check if advance payment is fully collected."""
        return self.get_remaining_amount(estimate_total) == Decimal("0")


@dataclass
class EstimateTerms:
    """Value object for estimate terms and conditions."""
    payment_terms: Optional[str] = None
    validity_days: int = 30
    warranty_period: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate terms."""
        if self.validity_days <= 0:
            raise DomainValidationError("Validity days must be positive")
    
    def get_expiry_date(self, issue_date: date) -> date:
        """Calculate estimate expiry date."""
        return issue_date + timedelta(days=self.validity_days)
    
    def is_expired(self, issue_date: date) -> bool:
        """Check if estimate is expired."""
        return date.today() > self.get_expiry_date(issue_date)


@dataclass
class EmailTracking:
    """Value object for email delivery tracking."""
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


@dataclass
class StatusHistoryEntry:
    """Value object for status history tracking."""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    from_status: Optional[EstimateStatus] = None
    to_status: EstimateStatus = EstimateStatus.DRAFT
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    changed_by: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Estimate:
    """
    Estimate domain entity representing a quote for work to be performed.
    
    Contains comprehensive business logic for status management, financial calculations,
    client communication, and conversion to invoices.
    """
    
    # Core identification
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    business_id: uuid.UUID = field(default_factory=uuid.uuid4)
    estimate_number: Optional[str] = None
    document_type: DocumentType = DocumentType.ESTIMATE
    
    # Status and lifecycle
    status: EstimateStatus = EstimateStatus.DRAFT
    status_history: List[StatusHistoryEntry] = field(default_factory=list)
    
    # Client information
    client_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    client_address: Optional[Address] = None
    
    # Estimate details
    title: str = ""
    description: Optional[str] = None
    line_items: List[EstimateLineItem] = field(default_factory=list)
    
    # Financial information
    currency: CurrencyCode = CurrencyCode.USD
    tax_rate: Decimal = Decimal("0")
    tax_type: TaxType = TaxType.PERCENTAGE
    overall_discount_type: DiscountType = DiscountType.NONE
    overall_discount_value: Decimal = Decimal("0")
    
    # Advance payment
    advance_payment: AdvancePayment = field(default_factory=AdvancePayment)
    
    # Terms and conditions
    terms: EstimateTerms = field(default_factory=EstimateTerms)
    
    # Template and branding
    template_id: Optional[uuid.UUID] = None
    template_data: Dict[str, Any] = field(default_factory=dict)
    
    # Communication tracking
    email_history: List[EmailTracking] = field(default_factory=list)
    
    # Project relationships
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    contact_id: Optional[uuid.UUID] = None
    
    # Conversion tracking
    converted_to_invoice_id: Optional[uuid.UUID] = None
    conversion_date: Optional[datetime] = None
    
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
    responded_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize and validate estimate."""
        if not self.title or not self.title.strip():
            raise DomainValidationError("Estimate title is required")
        
        if not self.business_id:
            raise DomainValidationError("Business ID is required")
        
        # Generate estimate number if not provided
        if not self.estimate_number:
            self.estimate_number = self._generate_estimate_number()
        
        # Initialize status history if empty
        if not self.status_history:
            self.add_status_history_entry(None, self.status, self.created_by, "Initial status")
        
        self._validate_business_rules()
    
    def _generate_estimate_number(self) -> str:
        """Generate estimate number."""
        today = date.today()
        return f"EST-{today.strftime('%Y-%m-%d')}-{str(self.id)[:8].upper()}"
    
    def _validate_business_rules(self) -> None:
        """Validate core business rules."""
        # Validate financial values
        if self.tax_rate < 0:
            raise DomainValidationError("Tax rate cannot be negative")
        
        if self.overall_discount_value < 0:
            raise DomainValidationError("Overall discount value cannot be negative")
        
        if self.overall_discount_type == DiscountType.PERCENTAGE and self.overall_discount_value > 100:
            raise DomainValidationError("Percentage discount cannot exceed 100%")
        
        # Client and line item validation is enforced in send_estimate() method
        # This allows loading legacy data without validation errors
    
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
        """Calculate final total amount."""
        return self.get_total_before_tax() + self.get_tax_amount()
    
    def get_advance_payment_amount(self) -> Decimal:
        """Calculate required advance payment amount."""
        return self.advance_payment.get_required_amount(self.get_total_amount())
    
    def get_balance_due(self) -> Decimal:
        """Calculate balance due after advance payment."""
        return self.get_total_amount() - self.advance_payment.collected_amount
    
    def round_currency(self, amount: Decimal) -> Decimal:
        """Round amount to currency precision."""
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Status management methods
    def can_send(self) -> bool:
        """Check if estimate can be sent."""
        return (self.status == EstimateStatus.DRAFT and 
                self.client_name and 
                self.line_items and
                (self.client_email or self.client_phone))
    
    def can_approve(self) -> bool:
        """Check if estimate can be approved."""
        return self.status in [EstimateStatus.SENT, EstimateStatus.VIEWED]
    
    def can_reject(self) -> bool:
        """Check if estimate can be rejected."""
        return self.status in [EstimateStatus.SENT, EstimateStatus.VIEWED]
    
    def can_convert_to_invoice(self) -> bool:
        """Check if estimate can be converted to invoice."""
        return self.status == EstimateStatus.APPROVED
    
    def can_cancel(self) -> bool:
        """Check if estimate can be cancelled."""
        return self.status not in [EstimateStatus.CANCELLED, EstimateStatus.CONVERTED, EstimateStatus.EXPIRED]
    
    def is_expired(self) -> bool:
        """Check if estimate is expired."""
        if self.status in [EstimateStatus.APPROVED, EstimateStatus.REJECTED, 
                          EstimateStatus.CANCELLED, EstimateStatus.CONVERTED]:
            return False
        
        return self.terms.is_expired(self.created_date.date())
    
    def send_estimate(self, sent_by: Optional[str] = None) -> None:
        """Send estimate to client."""
        if not self.can_send():
            missing_requirements = []
            if not self.client_name:
                missing_requirements.append("client name")
            if not self.line_items:
                missing_requirements.append("line items") 
            if not (self.client_email or self.client_phone):
                missing_requirements.append("client email or phone")
            
            raise BusinessRuleViolationError(f"Estimate cannot be sent - missing: {', '.join(missing_requirements)}")
        
        self.update_status(EstimateStatus.SENT, sent_by, "Estimate sent to client")
        self.sent_date = datetime.now(timezone.utc)
    
    def mark_as_viewed(self, viewed_by: Optional[str] = None) -> None:
        """Mark estimate as viewed by client."""
        if self.status == EstimateStatus.SENT:
            self.update_status(EstimateStatus.VIEWED, viewed_by, "Estimate viewed by client")
            self.viewed_date = datetime.now(timezone.utc)
    
    def approve_estimate(self, approved_by: Optional[str] = None, notes: Optional[str] = None) -> None:
        """Approve the estimate."""
        if not self.can_approve():
            raise BusinessRuleViolationError("Estimate cannot be approved in current state")
        
        self.update_status(EstimateStatus.APPROVED, approved_by, f"Estimate approved. {notes or ''}")
        self.responded_date = datetime.now(timezone.utc)
    
    def reject_estimate(self, rejected_by: Optional[str] = None, reason: Optional[str] = None) -> None:
        """Reject the estimate."""
        if not self.can_reject():
            raise BusinessRuleViolationError("Estimate cannot be rejected in current state")
        
        self.update_status(EstimateStatus.REJECTED, rejected_by, f"Estimate rejected. {reason or ''}")
        self.responded_date = datetime.now(timezone.utc)
    
    def cancel_estimate(self, cancelled_by: Optional[str] = None, reason: Optional[str] = None) -> None:
        """Cancel the estimate."""
        if not self.can_cancel():
            raise BusinessRuleViolationError("Estimate cannot be cancelled in current state")
        
        self.update_status(EstimateStatus.CANCELLED, cancelled_by, f"Estimate cancelled. {reason or ''}")
    
    def mark_as_converted(self, converted_by: Optional[str] = None, invoice_id: Optional[uuid.UUID] = None) -> None:
        """Mark estimate as converted to invoice."""
        if not self.can_convert_to_invoice():
            raise BusinessRuleViolationError("Estimate cannot be converted in current state")
        
        self.update_status(EstimateStatus.CONVERTED, converted_by, "Estimate converted to invoice")
        self.conversion_date = datetime.now(timezone.utc)
        self.converted_to_invoice_id = invoice_id
    
    def mark_as_expired(self, marked_by: Optional[str] = None) -> None:
        """Mark estimate as expired."""
        if self.status in [EstimateStatus.SENT, EstimateStatus.VIEWED] and self.is_expired():
            self.update_status(EstimateStatus.EXPIRED, marked_by, "Estimate expired")
    
    def update_status(self, new_status: EstimateStatus, changed_by: Optional[str] = None, 
                     reason: Optional[str] = None) -> None:
        """Update estimate status with history tracking."""
        if self.status == new_status:
            return
        
        old_status = self.status
        self.status = new_status
        self.last_modified = datetime.now(timezone.utc)
        
        self.add_status_history_entry(old_status, new_status, changed_by, reason)
    
    def add_status_history_entry(self, from_status: Optional[EstimateStatus], 
                               to_status: EstimateStatus, changed_by: Optional[str] = None,
                               reason: Optional[str] = None) -> None:
        """Add entry to status history."""
        entry = StatusHistoryEntry(
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            reason=reason
        )
        self.status_history.append(entry)
        
        # Keep only last 20 entries
        if len(self.status_history) > 20:
            self.status_history = self.status_history[-20:]
    
    # Line item management
    def add_line_item(self, description: str, quantity: Decimal, unit_price: Decimal,
                     unit: Optional[str] = None, category: Optional[str] = None,
                     discount_type: DiscountType = DiscountType.NONE,
                     discount_value: Decimal = Decimal("0"),
                     tax_rate: Decimal = Decimal("0"),
                     notes: Optional[str] = None) -> EstimateLineItem:
        """Add a line item to the estimate."""
        line_item = EstimateLineItem(
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
        """Remove a line item from the estimate."""
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
    def add_email_tracking(self, recipient_email: str, subject: str) -> EmailTracking:
        """Add email tracking entry."""
        tracking = EmailTracking(
            recipient_email=recipient_email,
            subject=subject,
            sent_date=datetime.now(timezone.utc),
            status=EmailStatus.SENT
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
        """Add a tag to the estimate."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.last_modified = datetime.now(timezone.utc)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the estimate."""
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
    
    def days_until_expiry(self) -> Optional[int]:
        """Get days until expiry."""
        if self.status in [EstimateStatus.APPROVED, EstimateStatus.REJECTED, 
                          EstimateStatus.CANCELLED, EstimateStatus.CONVERTED]:
            return None
        
        expiry_date = self.terms.get_expiry_date(self.created_date.date())
        days = (expiry_date - date.today()).days
        return max(0, days)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert estimate to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "estimate_number": self.estimate_number,
            "document_type": self.document_type.value,
            "document_type_display": self.document_type.get_display(),
            "status": self.status.value,
            "status_display": self.get_status_display(),
            "client_id": str(self.client_id) if self.client_id else None,
            "client_name": self.client_name,
            "client_email": self.client_email,
            "client_phone": self.client_phone,
            "client_address": self.client_address.to_dict() if self.client_address else None,
            "title": self.title,
            "description": self.description,
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
            "advance_payment": {
                "required": self.advance_payment.required,
                "type": self.advance_payment.type.value,
                "value": float(self.advance_payment.value),
                "due_date": self.advance_payment.due_date.isoformat() if self.advance_payment.due_date else None,
                "collected_amount": float(self.advance_payment.collected_amount),
                "required_amount": float(self.get_advance_payment_amount()),
                "remaining_amount": float(self.advance_payment.get_remaining_amount(self.get_total_amount()))
            },
            "terms": {
                "payment_terms": self.terms.payment_terms,
                "validity_days": self.terms.validity_days,
                "warranty_period": self.terms.warranty_period,
                "terms_and_conditions": self.terms.terms_and_conditions,
                "notes": self.terms.notes,
                "expiry_date": self.terms.get_expiry_date(self.created_date.date()).isoformat()
            },
            "template_id": str(self.template_id) if self.template_id else None,
            "project_id": str(self.project_id) if self.project_id else None,
            "job_id": str(self.job_id) if self.job_id else None,
            "contact_id": str(self.contact_id) if self.contact_id else None,
            "converted_to_invoice_id": str(self.converted_to_invoice_id) if self.converted_to_invoice_id else None,
            "conversion_date": self.conversion_date.isoformat() if self.conversion_date else None,
            "tags": self.tags,
            "custom_fields": self.custom_fields,
            "internal_notes": self.internal_notes,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "sent_date": self.sent_date.isoformat() if self.sent_date else None,
            "viewed_date": self.viewed_date.isoformat() if self.viewed_date else None,
            "responded_date": self.responded_date.isoformat() if self.responded_date else None,
            # Calculated fields
            "line_items_subtotal": float(self.get_line_items_subtotal()),
            "total_discount": float(self.get_line_items_discount_total() + self.get_overall_discount_amount()),
            "tax_amount": float(self.get_tax_amount()),
            "total_amount": float(self.get_total_amount()),
            "balance_due": float(self.get_balance_due()),
            "is_expired": self.is_expired(),
            "days_until_expiry": self.days_until_expiry(),
            "total_display": self.get_total_display()
        }
    
    def __str__(self) -> str:
        return f"Estimate({self.estimate_number} - {self.get_client_display_name()} - {self.get_status_display()})"
    
    def __repr__(self) -> str:
        return (f"Estimate(id={self.id}, number={self.estimate_number}, "
                f"client={self.client_name}, status={self.status}, "
                f"total={self.get_total_amount()})") 