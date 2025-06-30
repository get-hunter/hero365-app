"""
Estimate API Schemas

Pydantic schemas for estimate API endpoints.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class EstimateLineItemSchema(BaseModel):
    """Schema for estimate line items."""
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


class EstimateTermsSchema(BaseModel):
    """Schema for estimate terms."""
    payment_terms: str = Field("", max_length=1000)
    validity_period: int = Field(30, ge=1, le=365)
    work_schedule: str = Field("", max_length=1000)
    materials_policy: str = Field("", max_length=1000)
    change_order_policy: str = Field("", max_length=1000)
    warranty_terms: str = Field("", max_length=1000)
    cancellation_policy: str = Field("", max_length=1000)
    acceptance_criteria: str = Field("", max_length=1000)
    additional_terms: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class AdvancePaymentSchema(BaseModel):
    """Schema for advance payment information."""
    amount: Decimal = Field(Decimal('0'), ge=0)
    percentage: Decimal = Field(Decimal('0'), ge=0, le=100)
    due_date: Optional[date] = None
    description: str = Field("", max_length=500)
    is_required: bool = False

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }


class CreateEstimateSchema(BaseModel):
    """Schema for creating estimates."""
    contact_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    line_items: List[EstimateLineItemSchema] = Field(..., min_items=1)
    currency: str = Field("USD", pattern="^[A-Z]{3}$")
    tax_rate: Decimal = Field(Decimal('0'), ge=0, le=100)
    tax_type: str = Field("percentage", pattern="^(percentage|fixed)$")
    overall_discount_type: str = Field("none", pattern="^(none|percentage|fixed)$")
    overall_discount_value: Decimal = Field(Decimal('0'), ge=0)
    terms: Optional[EstimateTermsSchema] = None
    advance_payment: Optional[AdvancePaymentSchema] = None
    template_id: Optional[uuid.UUID] = None
    template_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)
    internal_notes: Optional[str] = Field(None, max_length=2000)
    valid_until_date: Optional[date] = None
    estimate_number: Optional[str] = Field(None, max_length=50)
    number_prefix: str = Field("EST", max_length=10)

    @validator('valid_until_date')
    def validate_valid_until_date(cls, v):
        if v and v <= date.today():
            raise ValueError('Valid until date must be in the future')
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v),
            date: lambda v: v.isoformat()
        }


class UpdateEstimateSchema(BaseModel):
    """Schema for updating estimates."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    line_items: Optional[List[EstimateLineItemSchema]] = Field(None, min_items=1)
    currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    tax_type: Optional[str] = Field(None, pattern="^(percentage|fixed)$")
    overall_discount_type: Optional[str] = Field(None, pattern="^(none|percentage|fixed)$")
    overall_discount_value: Optional[Decimal] = Field(None, ge=0)
    terms: Optional[EstimateTermsSchema] = None
    advance_payment: Optional[AdvancePaymentSchema] = None
    template_id: Optional[uuid.UUID] = None
    template_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    internal_notes: Optional[str] = Field(None, max_length=2000)
    valid_until_date: Optional[date] = None

    @validator('valid_until_date')
    def validate_valid_until_date(cls, v):
        if v and v <= date.today():
            raise ValueError('Valid until date must be in the future')
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v),
            date: lambda v: v.isoformat()
        }


class EstimateResponseSchema(BaseModel):
    """Schema for estimate responses."""
    id: uuid.UUID
    business_id: uuid.UUID
    estimate_number: str
    status: str
    contact_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    client_address: Optional[Dict[str, Any]] = None
    title: str
    description: Optional[str] = None
    line_items: List[EstimateLineItemSchema]
    currency: str
    tax_rate: Decimal
    tax_type: str
    overall_discount_type: str
    overall_discount_value: Decimal
    terms: Optional[EstimateTermsSchema] = None
    advance_payment: Optional[AdvancePaymentSchema] = None
    template_id: Optional[uuid.UUID] = None
    template_data: Dict[str, Any]
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    tags: List[str]
    custom_fields: Dict[str, Any]
    internal_notes: Optional[str] = None
    valid_until_date: Optional[date] = None
    created_by: Optional[str] = None
    created_date: datetime
    last_modified: datetime
    sent_date: Optional[datetime] = None
    viewed_date: Optional[datetime] = None
    accepted_date: Optional[datetime] = None
    
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


class EstimateListResponseSchema(BaseModel):
    """Schema for estimate list responses."""
    estimates: List[EstimateResponseSchema]
    total_count: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

    class Config:
        from_attributes = True


class EstimateSearchSchema(BaseModel):
    """Schema for estimate search parameters."""
    search_term: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, pattern="^(draft|sent|viewed|accepted|rejected|expired|converted)$")
    contact_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    template_id: Optional[uuid.UUID] = None
    currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)
    created_from: Optional[date] = None
    created_to: Optional[date] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    tags: Optional[List[str]] = None
    created_by: Optional[str] = None
    include_expired: bool = True
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    sort_by: str = Field("created_date", pattern="^(created_date|estimate_number|title|total_amount|status|valid_until_date)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")

    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        if v is not None and 'min_amount' in values and values['min_amount'] is not None:
            if v < values['min_amount']:
                raise ValueError('max_amount must be greater than or equal to min_amount')
        return v

    @validator('created_to')
    def validate_created_date_range(cls, v, values):
        if v is not None and 'created_from' in values and values['created_from'] is not None:
            if v < values['created_from']:
                raise ValueError('created_to must be greater than or equal to created_from')
        return v

    @validator('valid_to')
    def validate_valid_date_range(cls, v, values):
        if v is not None and 'valid_from' in values and values['valid_from'] is not None:
            if v < values['valid_from']:
                raise ValueError('valid_to must be greater than or equal to valid_from')
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: lambda v: str(v),
            date: lambda v: v.isoformat()
        }


class EstimateStatusUpdateSchema(BaseModel):
    """Schema for updating estimate status."""
    status: str = Field(..., pattern="^(draft|sent|viewed|accepted|rejected|expired|converted)$")
    notes: Optional[str] = Field(None, max_length=1000)

    class Config:
        from_attributes = True


class EstimateActionResponse(BaseModel):
    """Schema for estimate action responses."""
    message: str
    estimate_id: uuid.UUID
    invoice_id: Optional[uuid.UUID] = None
    success: bool = True

    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: lambda v: str(v)
        }


class EstimateAnalyticsResponse(BaseModel):
    """Schema for estimate analytics responses."""
    total_estimates: int = 0
    draft_estimates: int = 0
    sent_estimates: int = 0
    accepted_estimates: int = 0
    rejected_estimates: int = 0
    expired_estimates: int = 0
    converted_estimates: int = 0
    total_value: float = 0.0
    accepted_value: float = 0.0
    conversion_rate: float = 0.0
    average_value: float = 0.0
    currency: str = "USD"

    class Config:
        from_attributes = True
