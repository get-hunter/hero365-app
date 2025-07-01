"""
Invoice API Schemas

Pydantic schemas for invoice API endpoints.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class InvoiceLineItemSchema(BaseModel):
    """Schema for invoice line items."""
    id: Optional[uuid.UUID] = None
    description: str = Field(..., min_length=1, max_length=500)
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    discount_type: str = Field("none", pattern="^(none|percentage|fixed)$")
    discount_value: Decimal = Field(Decimal('0'), ge=0)
    tax_rate: Decimal = Field(Decimal('0'), ge=0, le=100)
    notes: Optional[str] = Field(None, max_length=1000)
    
    # Calculated fields (read-only)
    line_total: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    final_total: Optional[Decimal] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v)
        }


class PaymentSchema(BaseModel):
    """Schema for payment entities."""
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

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }


class CreateInvoiceSchema(BaseModel):
    """Schema for creating invoices."""
    contact_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    line_items: List[InvoiceLineItemSchema] = Field(..., min_items=1)
    currency: str = Field("USD", pattern="^[A-Z]{3}$")
    tax_rate: Decimal = Field(Decimal('0'), ge=0, le=100)
    tax_type: str = Field("percentage", pattern="^(percentage|fixed)$")
    overall_discount_type: str = Field("none", pattern="^(none|percentage|fixed)$")
    overall_discount_value: Decimal = Field(Decimal('0'), ge=0)
    template_id: Optional[uuid.UUID] = None
    template_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    estimate_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)
    internal_notes: Optional[str] = Field(None, max_length=2000)
    invoice_number: Optional[str] = Field(None, max_length=50)
    number_prefix: str = Field("INV", max_length=10)
    due_date: Optional[date] = None
    payment_net_days: int = Field(30, ge=0, le=365)
    early_payment_discount_percentage: Decimal = Field(Decimal('0'), ge=0, le=100)
    early_payment_discount_days: int = Field(0, ge=0, le=365)
    late_fee_percentage: Decimal = Field(Decimal('0'), ge=0, le=100)
    late_fee_grace_days: int = Field(0, ge=0, le=365)
    payment_instructions: Optional[str] = Field(None, max_length=1000)

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v),
            date: lambda v: v.isoformat()
        }


class CreateInvoiceFromEstimateSchema(BaseModel):
    """Schema for creating invoices from estimates."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    invoice_number: Optional[str] = Field(None, max_length=50)
    number_prefix: str = Field("INV", max_length=10)
    due_date: Optional[date] = None
    payment_net_days: int = Field(30, ge=0, le=365)
    early_payment_discount_percentage: Decimal = Field(Decimal('0'), ge=0, le=100)
    early_payment_discount_days: int = Field(0, ge=0, le=365)
    late_fee_percentage: Decimal = Field(Decimal('0'), ge=0, le=100)
    late_fee_grace_days: int = Field(0, ge=0, le=365)
    payment_instructions: Optional[str] = Field(None, max_length=1000)
    internal_notes: Optional[str] = Field(None, max_length=2000)

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }


class UpdateInvoiceSchema(BaseModel):
    """Schema for updating invoices."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    line_items: Optional[List[InvoiceLineItemSchema]] = Field(None, min_items=1)
    currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    tax_type: Optional[str] = Field(None, pattern="^(percentage|fixed)$")
    overall_discount_type: Optional[str] = Field(None, pattern="^(none|percentage|fixed)$")
    overall_discount_value: Optional[Decimal] = Field(None, ge=0)
    template_id: Optional[uuid.UUID] = None
    template_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    internal_notes: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[date] = None
    payment_net_days: Optional[int] = Field(None, ge=0, le=365)
    early_payment_discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    early_payment_discount_days: Optional[int] = Field(None, ge=0, le=365)
    late_fee_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    late_fee_grace_days: Optional[int] = Field(None, ge=0, le=365)
    payment_instructions: Optional[str] = Field(None, max_length=1000)

    @validator('due_date')
    def validate_due_date(cls, v):
        if v and v <= date.today():
            raise ValueError('Due date must be in the future')
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v),
            date: lambda v: v.isoformat()
        }


class ProcessPaymentSchema(BaseModel):
    """Schema for processing payments."""
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(cash|check|credit_card|debit_card|bank_transfer|online_payment|other)$")
    reference: Optional[str] = Field(None, max_length=100)
    transaction_id: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    payment_date: Optional[datetime] = None

    @validator('payment_date')
    def validate_payment_date(cls, v):
        if v and v > datetime.utcnow():
            raise ValueError('Payment date cannot be in the future')
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class InvoiceResponseSchema(BaseModel):
    """Schema for invoice responses."""
    id: uuid.UUID
    business_id: uuid.UUID
    invoice_number: str
    status: str
    client_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    client_address: Optional[Dict[str, Any]] = None
    title: str
    description: Optional[str] = None
    line_items: List[InvoiceLineItemSchema]
    currency: str
    tax_rate: Decimal
    tax_type: str
    overall_discount_type: str
    overall_discount_value: Decimal
    payments: List[PaymentSchema]
    template_id: Optional[uuid.UUID] = None
    template_data: Dict[str, Any]
    estimate_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    contact_id: Optional[uuid.UUID] = None
    tags: List[str]
    custom_fields: Dict[str, Any]
    internal_notes: Optional[str] = None
    created_by: Optional[str] = None
    created_date: datetime
    last_modified: datetime
    sent_date: Optional[datetime] = None
    viewed_date: Optional[datetime] = None
    due_date: Optional[date] = None
    paid_date: Optional[datetime] = None
    
    # Financial summary
    financial_summary: Dict[str, Optional[float]]
    
    # Status information
    status_info: Dict[str, Any]

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class InvoiceListResponseSchema(BaseModel):
    """Schema for invoice list responses."""
    invoices: List[InvoiceResponseSchema]
    total_count: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

    class Config:
        from_attributes = True


class InvoiceSearchSchema(BaseModel):
    """Schema for invoice search parameters."""
    search_term: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, pattern="^(draft|sent|viewed|paid|partially_paid|overdue|cancelled|void)$")
    contact_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    estimate_id: Optional[uuid.UUID] = None
    currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)
    created_from: Optional[date] = None
    created_to: Optional[date] = None
    due_from: Optional[date] = None
    due_to: Optional[date] = None
    paid_from: Optional[date] = None
    paid_to: Optional[date] = None
    tags: Optional[List[str]] = None
    created_by: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    sort_by: str = Field("created_date", pattern="^(created_date|invoice_number|title|total_amount|status|due_date)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")

    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        if v is not None and 'min_amount' in values and values['min_amount'] is not None:
            if v < values['min_amount']:
                raise ValueError('max_amount must be greater than or equal to min_amount')
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: lambda v: str(v),
            date: lambda v: v.isoformat()
        }


class InvoiceStatusUpdateSchema(BaseModel):
    """Schema for updating invoice status."""
    status: str = Field(..., pattern="^(draft|sent|viewed|paid|partially_paid|overdue|cancelled|void)$")
    notes: Optional[str] = Field(None, max_length=1000)

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    """Schema for payment responses."""
    payment_id: uuid.UUID
    invoice_id: uuid.UUID
    amount: Decimal
    payment_method: str
    payment_date: datetime
    status: str = "completed"
    reference: Optional[str] = None
    transaction_id: Optional[str] = None
    notes: Optional[str] = None
    success: bool = True
    message: str = "Payment processed successfully"

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }


class NextInvoiceNumberSchema(BaseModel):
    """Schema for next invoice number response."""
    next_number: str = Field(..., description="The next available invoice number")
    prefix: str = Field(..., description="The prefix used for the number")
    
    class Config:
        from_attributes = True
