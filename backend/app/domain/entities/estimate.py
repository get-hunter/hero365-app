"""
Estimate Domain Entity

Represents an estimate for work to be performed with comprehensive business rules,
financial calculations, status management, and client communication tracking.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any, Union, Annotated
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, Field, validator, model_validator, UUID4, BeforeValidator

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError
from ..enums import (
    EstimateStatus, CurrencyCode, TaxType, DiscountType, 
    AdvancePaymentType, EmailStatus, TemplateType, DocumentType
)
from ..value_objects.address import Address

# Configure logging
logger = logging.getLogger(__name__)


# Custom Pydantic validators for automatic string-to-enum conversion
def validate_estimate_status(v) -> EstimateStatus:
    """Convert string to EstimateStatus enum."""
    if isinstance(v, str):
        logger.debug(f"Converting status string '{v}' to EstimateStatus enum")
        return EstimateStatus(v)
    logger.debug(f"Status value is already an enum: {type(v)}")
    return v

def validate_currency_code(v) -> CurrencyCode:
    """Convert string to CurrencyCode enum."""
    if isinstance(v, str):
        return CurrencyCode(v)
    return v

def validate_document_type(v) -> DocumentType:
    """Convert string to DocumentType enum."""
    if isinstance(v, str):
        return DocumentType(v)
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

def validate_advance_payment_type(v) -> AdvancePaymentType:
    """Convert string to AdvancePaymentType enum."""
    if isinstance(v, str):
        return AdvancePaymentType(v)
    return v

def validate_email_status(v) -> EmailStatus:
    """Convert string to EmailStatus enum."""
    if isinstance(v, str):
        return EmailStatus(v)
    return v

# Define validated enum field types
EstimateStatusField = Annotated[EstimateStatus, BeforeValidator(validate_estimate_status)]
CurrencyField = Annotated[CurrencyCode, BeforeValidator(validate_currency_code)]
DocumentTypeField = Annotated[DocumentType, BeforeValidator(validate_document_type)]
TaxTypeField = Annotated[TaxType, BeforeValidator(validate_tax_type)]
DiscountTypeField = Annotated[DiscountType, BeforeValidator(validate_discount_type)]
AdvancePaymentTypeField = Annotated[AdvancePaymentType, BeforeValidator(validate_advance_payment_type)]
EmailStatusField = Annotated[EmailStatus, BeforeValidator(validate_email_status)]


class EstimateLineItem(BaseModel):
    """Value object for estimate line items."""
    id: UUID4 = Field(default_factory=uuid.uuid4)
    description: str = Field(..., min_length=1, description="Line item description")
    quantity: Decimal = Field(default=Decimal("1"), gt=0, description="Item quantity")
    unit_price: Decimal = Field(default=Decimal("0"), ge=0, description="Unit price")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    category: Optional[str] = Field(None, max_length=100, description="Item category")
    discount_type: DiscountTypeField = Field(default=DiscountType.NONE)
    discount_value: Decimal = Field(default=Decimal("0"), ge=0, description="Discount value")
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, description="Tax rate percentage")
    notes: Optional[str] = Field(None, max_length=500, description="Line item notes")
    
    @validator('discount_value')
    def validate_discount_value(cls, v, values):
        """Validate discount value based on discount type."""
        discount_type = values.get('discount_type')
        if discount_type == DiscountType.PERCENTAGE and v > 100:
            raise ValueError("Percentage discount cannot exceed 100%")
        return v
    
    @validator('description')
    def validate_description(cls, v):
        """Validate description is not empty."""
        if not v or not v.strip():
            raise ValueError("Line item description is required")
        return v.strip()
    
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

    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            Decimal: lambda v: float(v),
            UUID4: lambda v: str(v)
        }
    }


class AdvancePayment(BaseModel):
    """Value object for advance payment requirements."""
    required: bool = Field(default=False)
    type: AdvancePaymentTypeField = Field(default=AdvancePaymentType.NONE)
    value: Decimal = Field(default=Decimal("0"), ge=0, description="Advance payment value")
    due_date: Optional[date] = Field(None, description="Payment due date")
    collected_amount: Decimal = Field(default=Decimal("0"), ge=0, description="Amount collected")
    collected_date: Optional[datetime] = Field(None, description="Collection date")
    collection_method: Optional[str] = Field(None, max_length=100, description="Collection method")
    reference: Optional[str] = Field(None, max_length=200, description="Payment reference")
    notes: Optional[str] = Field(None, max_length=500, description="Payment notes")
    
    @model_validator(mode='after')
    def validate_advance_payment(self):
        """Validate advance payment consistency."""
        if self.required and self.type == AdvancePaymentType.NONE:
            raise ValueError("Advance payment type required when advance payment is required")
        
        if self.type == AdvancePaymentType.PERCENTAGE and self.value > 100:
            raise ValueError("Percentage advance payment cannot exceed 100%")
            
        return self
    
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

    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }
    }


class EstimateTerms(BaseModel):
    """Value object for estimate terms and conditions."""
    payment_terms: Optional[str] = Field(None, max_length=500, description="Payment terms")
    validity_days: int = Field(default=30, gt=0, description="Validity period in days")
    warranty_period: Optional[str] = Field(None, max_length=200, description="Warranty period")
    terms_and_conditions: Optional[str] = Field(None, max_length=2000, description="Terms and conditions")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    def get_expiry_date(self, issue_date: date) -> date:
        """Calculate estimate expiry date."""
        return issue_date + timedelta(days=self.validity_days)
    
    def is_expired(self, issue_date: date) -> bool:
        """Check if estimate is expired."""
        return date.today() > self.get_expiry_date(issue_date)


class EmailTracking(BaseModel):
    """Value object for email delivery tracking."""
    id: UUID4 = Field(default_factory=uuid.uuid4)
    sent_date: Optional[datetime] = Field(None, description="Email sent timestamp")
    delivered_date: Optional[datetime] = Field(None, description="Email delivered timestamp")
    opened_date: Optional[datetime] = Field(None, description="Email opened timestamp")
    clicked_date: Optional[datetime] = Field(None, description="Email clicked timestamp")
    status: EmailStatusField = Field(default=EmailStatus.PENDING)
    recipient_email: Optional[str] = Field(None, description="Recipient email address")
    subject: Optional[str] = Field(None, max_length=200, description="Email subject")
    message_id: Optional[str] = Field(None, max_length=100, description="Message ID")
    error_message: Optional[str] = Field(None, max_length=500, description="Error message")
    tracking_data: Dict[str, Any] = Field(default_factory=dict, description="Additional tracking data")

    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            UUID4: lambda v: str(v),
            datetime: lambda v: v.isoformat() if v else None
        }
    }


class StatusHistoryEntry(BaseModel):
    """Value object for status history tracking."""
    id: UUID4 = Field(default_factory=uuid.uuid4)
    from_status: Optional[EstimateStatusField] = Field(None, description="Previous status")
    to_status: EstimateStatusField = Field(default=EstimateStatus.DRAFT, description="New status")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    changed_by: Optional[str] = Field(None, max_length=100, description="User who changed status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for change")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")

    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            UUID4: lambda v: str(v),
            datetime: lambda v: v.isoformat() if v else None
        }
    }


class Estimate(BaseModel):
    """
    Estimate domain entity representing a price quote for potential work.
    
    Contains comprehensive business logic for estimate creation, validation,
    expiry tracking, and conversion to invoices.
    """
    
    # Core identification
    id: UUID4 = Field(default_factory=uuid.uuid4)
    business_id: UUID4 = Field(..., description="Business ID")
    estimate_number: Optional[str] = Field(None, max_length=50, description="Estimate number")
    
    # Document classification
    document_type: DocumentTypeField = Field(default=DocumentType.ESTIMATE)
    
    # Status and lifecycle
    status: EstimateStatusField = Field(default=EstimateStatus.DRAFT)
    status_history: List[StatusHistoryEntry] = Field(default_factory=list)
    
    # Client information
    contact_id: Optional[UUID4] = Field(None, description="Contact ID")
    client_name: Optional[str] = Field(None, max_length=200, description="Client name")
    client_email: Optional[str] = Field(None, max_length=254, description="Client email")
    client_phone: Optional[str] = Field(None, max_length=20, description="Client phone")
    client_address: Optional[Address] = Field(None, description="Client address")
    
    # Core content
    title: str = Field(..., min_length=1, max_length=300, description="Estimate title")
    description: Optional[str] = Field(None, max_length=2000, description="Estimate description")
    po_number: Optional[str] = Field(None, max_length=100, description="Purchase order number")
    
    # Line items and pricing
    line_items: List[EstimateLineItem] = Field(default_factory=list)
    currency: CurrencyField = Field(default=CurrencyCode.USD)
    tax_rate: Decimal = Field(default=Decimal('0'), ge=0, description="Tax rate percentage")
    tax_type: TaxTypeField = Field(default=TaxType.PERCENTAGE)
    overall_discount_type: DiscountTypeField = Field(default=DiscountType.NONE)
    overall_discount_value: Decimal = Field(default=Decimal('0'), ge=0, description="Overall discount value")
    
    # Terms and conditions
    terms: Optional[EstimateTerms] = Field(default_factory=EstimateTerms)
    advance_payment: Optional[AdvancePayment] = Field(default_factory=AdvancePayment)
    
    # Project relationships
    project_id: Optional[UUID4] = Field(None, description="Project ID")
    job_id: Optional[UUID4] = Field(None, description="Job ID")
    
    # Template information
    template_id: Optional[UUID4] = Field(None, description="Template ID")
    template_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Time tracking
    issue_date: Optional[date] = Field(None, description="Issue date")
    valid_until_date: Optional[date] = Field(None, description="Valid until date")
    conversion_date: Optional[datetime] = Field(None, description="Conversion date")
    
    # Communication tracking
    email_history: List[EmailTracking] = Field(default_factory=list)
    
    # Conversion tracking
    converted_to_invoice_id: Optional[UUID4] = Field(None, description="Converted invoice ID")
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    internal_notes: Optional[str] = Field(None, max_length=2000, description="Internal notes")
    
    # Audit fields
    created_by: Optional[str] = Field(None, max_length=100, description="Created by user")
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sent_date: Optional[datetime] = Field(None, description="Sent date")
    viewed_date: Optional[datetime] = Field(None, description="Viewed date")
    responded_date: Optional[datetime] = Field(None, description="Responded date")

    @validator('overall_discount_value')
    def validate_overall_discount(cls, v, values):
        """Validate overall discount based on type."""
        discount_type = values.get('overall_discount_type')
        if discount_type == DiscountType.PERCENTAGE and v > 100:
            raise ValueError("Percentage discount cannot exceed 100%")
        return v
    
    @validator('title')
    def validate_title(cls, v):
        """Validate title is not empty."""
        if not v or not v.strip():
            raise ValueError("Estimate title is required")
        return v.strip()
    
    @model_validator(mode='after')
    def validate_estimate(self):
        """Validate estimate business rules."""
        # Set issue_date to created_date if not provided
        if not self.issue_date and self.created_date:
            self.issue_date = self.created_date.date()
        
        # Generate estimate number if not provided
        if not self.estimate_number:
            today = date.today()
            self.estimate_number = f"EST-{today.strftime('%Y-%m-%d')}-{str(self.id)[:8].upper()}"
        
        return self

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
        if not self.advance_payment:
            return Decimal("0")
        return self.advance_payment.get_required_amount(self.get_total_amount())
    
    def get_balance_due(self) -> Decimal:
        """Calculate balance due after advance payment."""
        if not self.advance_payment:
            return self.get_total_amount()
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
        
        if not self.terms:
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
            if str(item.id) == str(line_item_id):
                del self.line_items[i]
                self.last_modified = datetime.now(timezone.utc)
                return True
        return False
    
    def update_line_item(self, line_item_id: uuid.UUID, **updates) -> bool:
        """Update a line item."""
        for item in self.line_items:
            if str(item.id) == str(line_item_id):
                # Create updated item with new data
                updated_data = item.dict()
                updated_data.update(updates)
                updated_item = EstimateLineItem(**updated_data)
                
                # Replace in list
                item_index = self.line_items.index(item)
                self.line_items[item_index] = updated_item
                
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
            if str(tracking.id) == str(tracking_id):
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
    
    # Display methods - now clean and simple since enums are guaranteed
    def get_status_display(self) -> str:
        """Get human-readable status."""
        return self.status.get_display()
    
    def get_currency_display(self) -> str:
        """Get human-readable currency."""
        return self.currency.get_display()
    
    def get_document_type_display(self) -> str:
        """Get human-readable document type."""
        return self.document_type.get_display()
    
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
        
        if not self.terms:
            return None
        
        expiry_date = self.terms.get_expiry_date(self.created_date.date())
        days = (expiry_date - date.today()).days
        return max(0, days)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert estimate to dictionary representation."""
        # Use Pydantic's built-in serialization with custom handling
        base_dict = self.dict()
        
        # Add computed fields
        base_dict.update({
            "status_display": self.get_status_display(),
            "currency_display": self.get_currency_display(),
            "client_display_name": self.get_client_display_name(),
            "line_items_subtotal": float(self.get_line_items_subtotal()),
            "total_discount": float(self.get_line_items_discount_total() + self.get_overall_discount_amount()),
            "tax_amount": float(self.get_tax_amount()),
            "total_amount": float(self.get_total_amount()),
            "balance_due": float(self.get_balance_due()),
            "is_expired": self.is_expired(),
            "days_until_expiry": self.days_until_expiry(),
            "total_display": self.get_total_display()
        })
        
        # Handle advance payment calculations
        if self.advance_payment:
            base_dict["advance_payment"].update({
                "required_amount": float(self.get_advance_payment_amount()),
                "remaining_amount": float(self.advance_payment.get_remaining_amount(self.get_total_amount()))
            })
        
        # Handle terms expiry
        if self.terms:
            base_dict["terms"]["expiry_date"] = self.terms.get_expiry_date(self.created_date.date()).isoformat()
        
        return base_dict
    
    def __str__(self) -> str:
        return f"Estimate({self.estimate_number} - {self.get_client_display_name()} - {self.get_status_display()})"
    
    def __repr__(self) -> str:
        return (f"Estimate(id={self.id}, number={self.estimate_number}, "
                f"client={self.client_name}, status={self.status}, "
                f"total={self.get_total_amount()})")

    model_config = {
        "use_enum_values": True,
        "validate_by_name": True,
        "validate_assignment": True,
        "json_encoders": {
            UUID4: lambda v: str(v),
            uuid.UUID: lambda v: str(v),
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        },
        "json_schema_extra": {
            "example": {
                "title": "Kitchen Renovation Estimate",
                "description": "Complete kitchen renovation including cabinets, countertops, and appliances",
                "client_name": "John Doe",
                "client_email": "john@example.com",
                "line_items": [
                    {
                        "description": "Kitchen Cabinets",
                        "quantity": 1,
                        "unit_price": 5000.00,
                        "unit": "set"
                    }
                ],
                "currency": "USD",
                "status": "draft"
            }
        }
    } 