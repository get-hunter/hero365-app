"""
Invoice Data Transfer Objects

DTOs for invoice management operations following clean architecture principles.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from dataclasses import dataclass

from app.domain.value_objects.address import Address


@dataclass
class InvoiceLineItemDTO:
    """DTO for invoice line items."""
    id: Optional[uuid.UUID] = None
    description: str = ""
    quantity: Decimal = Decimal('1')
    unit_price: Decimal = Decimal('0')
    unit: Optional[str] = None
    category: Optional[str] = None
    discount_type: str = "none"
    discount_value: Decimal = Decimal('0')
    tax_rate: Decimal = Decimal('0')
    notes: Optional[str] = None
    
    # Calculated fields
    line_total: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    final_total: Optional[Decimal] = None

    @classmethod
    def from_entity(cls, line_item) -> 'InvoiceLineItemDTO':
        """Create DTO from domain entity."""
        return cls(
            id=line_item.id,
            description=line_item.description,
            quantity=line_item.quantity,
            unit_price=line_item.unit_price,
            unit=line_item.unit,
            category=line_item.category,
            discount_type=line_item.discount_type.value,
            discount_value=line_item.discount_value,
            tax_rate=line_item.tax_rate,
            notes=line_item.notes,
            line_total=line_item.get_subtotal(),
            discount_amount=line_item.get_discount_amount(),
            tax_amount=line_item.get_tax_amount(),
            final_total=line_item.get_total()
        )


@dataclass
class PaymentDTO:
    """DTO for payment entities."""
    id: uuid.UUID
    amount: Decimal
    payment_date: datetime
    payment_method: str
    status: str
    reference: Optional[str] = None
    transaction_id: Optional[str] = None
    notes: Optional[str] = None
    processed_by: Optional[str] = None
    refunded_amount: Decimal = Decimal('0')
    refund_date: Optional[datetime] = None
    refund_reason: Optional[str] = None

    @classmethod
    def from_entity(cls, payment) -> 'PaymentDTO':
        """Create DTO from domain entity."""
        return cls(
            id=payment.id,
            amount=payment.amount,
            payment_date=payment.payment_date,
            payment_method=payment.payment_method.value,
            status=payment.status.value,
            reference=payment.reference,
            transaction_id=payment.transaction_id,
            notes=payment.notes,
            processed_by=payment.processed_by,
            refunded_amount=payment.refunded_amount,
            refund_date=payment.refund_date,
            refund_reason=payment.refund_reason
        )


@dataclass
class InvoiceDTO:
    """Main DTO for invoice entities."""
    id: uuid.UUID
    business_id: uuid.UUID
    invoice_number: str
    status: str
    client_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    client_address: Optional[Address] = None
    title: str = ""
    description: Optional[str] = None
    line_items: List[InvoiceLineItemDTO] = None
    currency: str = "USD"
    tax_rate: Decimal = Decimal('0')
    tax_type: str = "percentage"
    overall_discount_type: str = "none"
    overall_discount_value: Decimal = Decimal('0')
    payments: List[PaymentDTO] = None
    template_id: Optional[uuid.UUID] = None
    template_data: Dict[str, Any] = None
    estimate_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    contact_id: Optional[uuid.UUID] = None
    tags: List[str] = None
    custom_fields: Dict[str, Any] = None
    internal_notes: Optional[str] = None
    po_number: Optional[str] = None
    created_by: Optional[str] = None
    created_date: datetime = None
    last_modified: datetime = None
    sent_date: Optional[datetime] = None
    viewed_date: Optional[datetime] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    paid_date: Optional[datetime] = None
    
    # Calculated financial fields
    total_amount: Optional[Decimal] = None
    total_payments: Optional[Decimal] = None
    balance_due: Optional[Decimal] = None
    is_paid: Optional[bool] = None
    is_overdue: Optional[bool] = None

    def __post_init__(self):
        if self.line_items is None:
            self.line_items = []
        if self.payments is None:
            self.payments = []
        if self.template_data is None:
            self.template_data = {}
        if self.tags is None:
            self.tags = []
        if self.custom_fields is None:
            self.custom_fields = {}

    @classmethod
    def from_entity(cls, invoice) -> 'InvoiceDTO':
        """Create DTO from domain entity."""
        return cls(
            id=invoice.id,
            business_id=invoice.business_id,
            invoice_number=invoice.invoice_number,
            status=invoice.status.value,
            client_id=invoice.client_id,
            client_name=invoice.client_name,
            client_email=invoice.client_email,
            client_phone=invoice.client_phone,
            client_address=invoice.client_address,
            title=invoice.title,
            description=invoice.description,
            line_items=[InvoiceLineItemDTO.from_entity(item) for item in invoice.line_items],
            currency=invoice.currency.value,
            tax_rate=invoice.tax_rate,
            tax_type=invoice.tax_type.value,
            overall_discount_type=invoice.overall_discount_type.value,
            overall_discount_value=invoice.overall_discount_value,
            payments=[PaymentDTO.from_entity(payment) for payment in invoice.payments],
            template_id=invoice.template_id,
            template_data=invoice.template_data.copy(),
            estimate_id=invoice.estimate_id,
            project_id=invoice.project_id,
            job_id=invoice.job_id,
            contact_id=invoice.contact_id,
            tags=invoice.tags.copy(),
            custom_fields=invoice.custom_fields.copy(),
            internal_notes=invoice.internal_notes,
            po_number=invoice.po_number,
            created_by=invoice.created_by,
            created_date=invoice.created_date,
            last_modified=invoice.last_modified,
            sent_date=invoice.sent_date,
            viewed_date=invoice.viewed_date,
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            paid_date=invoice.paid_date,
            total_amount=invoice.get_total_amount(),
            total_payments=invoice.get_total_payments(),
            balance_due=invoice.get_balance_due(),
            is_paid=invoice.is_paid(),
            is_overdue=invoice.is_overdue()
        )


@dataclass
class CreateInvoiceDTO:
    """DTO for creating new invoices."""
    contact_id: uuid.UUID
    title: str
    description: Optional[str] = None
    line_items: List[dict] = None
    currency: Optional[str] = "USD"
    tax_rate: Optional[float] = 0.0
    tax_type: Optional[str] = "percentage"
    overall_discount_type: Optional[str] = "none"
    overall_discount_value: Optional[float] = 0.0
    template_id: Optional[uuid.UUID] = None
    template_data: Optional[Dict[str, Any]] = None
    estimate_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    internal_notes: Optional[str] = None
    invoice_number: Optional[str] = None
    number_prefix: Optional[str] = "INV"
    po_number: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    payment_net_days: Optional[int] = 30
    early_payment_discount_percentage: Optional[float] = 0.0
    early_payment_discount_days: Optional[int] = 0
    late_fee_percentage: Optional[float] = 0.0
    late_fee_grace_days: Optional[int] = 0
    payment_instructions: Optional[str] = None

    def __post_init__(self):
        if self.line_items is None:
            self.line_items = []
        if self.template_data is None:
            self.template_data = {}
        if self.tags is None:
            self.tags = []
        if self.custom_fields is None:
            self.custom_fields = {}


@dataclass
class CreateInvoiceFromEstimateDTO:
    """DTO for creating invoices from estimates."""
    business_id: uuid.UUID
    estimate_id: uuid.UUID
    title: Optional[str] = None
    description: Optional[str] = None
    invoice_number: Optional[str] = None
    number_prefix: Optional[str] = "INV"
    po_number: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    payment_net_days: Optional[int] = 30
    early_payment_discount_percentage: Optional[float] = 0.0
    early_payment_discount_days: Optional[int] = 0
    late_fee_percentage: Optional[float] = 0.0
    late_fee_grace_days: Optional[int] = 0
    payment_instructions: Optional[str] = None
    internal_notes: Optional[str] = None
    advance_payment_amount: Optional[float] = None
    created_by: Optional[str] = None


@dataclass
class UpdateInvoiceDTO:
    """DTO for updating existing invoices."""
    invoice_id: uuid.UUID
    business_id: uuid.UUID
    title: Optional[str] = None
    description: Optional[str] = None
    line_items: Optional[List[InvoiceLineItemDTO]] = None
    currency: Optional[str] = None
    tax_rate: Optional[Decimal] = None
    tax_type: Optional[str] = None
    overall_discount_type: Optional[str] = None
    overall_discount_value: Optional[Decimal] = None
    template_id: Optional[uuid.UUID] = None
    template_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    internal_notes: Optional[str] = None
    due_date: Optional[date] = None
    payment_net_days: Optional[int] = None
    early_payment_discount_percentage: Optional[Decimal] = None
    early_payment_discount_days: Optional[int] = None
    late_fee_percentage: Optional[Decimal] = None
    late_fee_grace_days: Optional[int] = None
    payment_instructions: Optional[str] = None
    updated_by: Optional[str] = None


@dataclass
class ProcessPaymentDTO:
    """DTO for processing payments."""
    amount: float
    payment_method: str
    reference: Optional[str] = None
    transaction_id: Optional[str] = None
    notes: Optional[str] = None
    payment_date: Optional[datetime] = None


@dataclass
class InvoiceListFilters:
    """DTO for invoice list filtering."""
    status: Optional[str] = None
    contact_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    overdue_only: Optional[bool] = False


@dataclass
class InvoiceSearchCriteria:
    """DTO for invoice search criteria."""
    search_text: Optional[str] = None
    statuses: Optional[List[str]] = None
    contact_ids: Optional[List[uuid.UUID]] = None
    project_ids: Optional[List[uuid.UUID]] = None
    job_ids: Optional[List[uuid.UUID]] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    tags: Optional[List[str]] = None
    created_by: Optional[str] = None
    overdue_only: Optional[bool] = False
    paid_only: Optional[bool] = False

    def __post_init__(self):
        if self.statuses is None:
            self.statuses = []
        if self.contact_ids is None:
            self.contact_ids = []
        if self.project_ids is None:
            self.project_ids = []
        if self.job_ids is None:
            self.job_ids = []
        if self.tags is None:
            self.tags = []
