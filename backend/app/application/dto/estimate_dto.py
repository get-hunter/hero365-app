"""
Estimate Data Transfer Objects

DTOs for estimate management operations following clean architecture principles.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class EstimateLineItemDTO:
    """DTO for estimate line items."""
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
    def from_entity(cls, line_item) -> 'EstimateLineItemDTO':
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
class EstimateDTO:
    """Main DTO for estimate entities."""
    id: uuid.UUID
    business_id: uuid.UUID
    estimate_number: str
    status: str
    document_type: str = "estimate"
    document_type_display: str = "Estimate"
    contact_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    client_address: Optional[Dict[str, Any]] = None
    title: str = ""
    description: Optional[str] = None
    line_items: List[EstimateLineItemDTO] = None
    currency: str = "USD"
    tax_rate: Decimal = Decimal('0')
    tax_type: str = "percentage"
    overall_discount_type: str = "none"
    overall_discount_value: Decimal = Decimal('0')
    terms: Optional[Dict[str, Any]] = None
    advance_payment: Optional[Dict[str, Any]] = None
    template_id: Optional[uuid.UUID] = None
    template_data: Dict[str, Any] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    tags: List[str] = None
    custom_fields: Dict[str, Any] = None
    internal_notes: Optional[str] = None
    valid_until_date: Optional[date] = None
    po_number: Optional[str] = None
    issue_date: Optional[date] = None
    created_by: Optional[str] = None
    created_date: datetime = None
    last_modified: datetime = None
    sent_date: Optional[datetime] = None
    viewed_date: Optional[datetime] = None
    responded_date: Optional[datetime] = None
    
    # Calculated financial fields
    total_amount: Optional[Decimal] = None
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    
    # Status fields
    is_expired: Optional[bool] = None
    days_until_expiry: Optional[int] = None

    def __post_init__(self):
        if self.line_items is None:
            self.line_items = []
        if self.template_data is None:
            self.template_data = {}
        if self.tags is None:
            self.tags = []
        if self.custom_fields is None:
            self.custom_fields = {}
        if self.client_address is None:
            self.client_address = {}
        if self.terms is None:
            self.terms = {}
        if self.advance_payment is None:
            self.advance_payment = {}

    @classmethod
    def from_entity(cls, estimate) -> 'EstimateDTO':
        """Create DTO from domain entity."""
        return cls(
            id=estimate.id,
            business_id=estimate.business_id,
            estimate_number=estimate.estimate_number,
            document_type=estimate.document_type.value,
            document_type_display=estimate.document_type.get_display(),
            status=estimate.status.value,
            contact_id=estimate.contact_id,
            client_name=estimate.client_name,
            client_email=estimate.client_email,
            client_phone=estimate.client_phone,
            client_address=estimate.client_address.to_dict() if estimate.client_address else {},
            title=estimate.title,
            description=estimate.description,
            line_items=[EstimateLineItemDTO.from_entity(item) for item in estimate.line_items],
            currency=estimate.currency.value,
            tax_rate=estimate.tax_rate,
            tax_type=estimate.tax_type.value,
            overall_discount_type=estimate.overall_discount_type.value,
            overall_discount_value=estimate.overall_discount_value,
            terms={
                "payment_terms": estimate.terms.payment_terms or "",
                "validity_period": estimate.terms.validity_days,
                "work_schedule": "",
                "materials_policy": "",
                "change_order_policy": "",
                "warranty_terms": estimate.terms.warranty_period or "",
                "cancellation_policy": "",
                "acceptance_criteria": "",
                "additional_terms": [],
                "expiry_date": estimate.terms.get_expiry_date(estimate.created_date.date()).isoformat()
            } if estimate.terms else {
                "payment_terms": "",
                "validity_period": 30,
                "work_schedule": "",
                "materials_policy": "",
                "change_order_policy": "",
                "warranty_terms": "",
                "cancellation_policy": "",
                "acceptance_criteria": "",
                "additional_terms": []
            },
            advance_payment={
                "amount": estimate.advance_payment.value,
                "percentage": estimate.advance_payment.value if estimate.advance_payment.type.value == "percentage" else Decimal("0"),
                "due_date": estimate.advance_payment.due_date,
                "description": estimate.advance_payment.notes or "",
                "is_required": estimate.advance_payment.required,
                # Additional calculated fields for internal use
                "collected_amount": float(estimate.advance_payment.collected_amount),
                "required_amount": float(estimate.advance_payment.get_required_amount(estimate.get_total_amount())),
                "remaining_amount": float(estimate.advance_payment.get_remaining_amount(estimate.get_total_amount())),
                "is_fully_collected": estimate.advance_payment.is_fully_collected(estimate.get_total_amount())
            } if estimate.advance_payment else {
                "amount": Decimal("0"),
                "percentage": Decimal("0"),
                "due_date": None,
                "description": "",
                "is_required": False
            },
            template_id=estimate.template_id,
            template_data=estimate.template_data.copy(),
            project_id=estimate.project_id,
            job_id=estimate.job_id,
            tags=estimate.tags.copy(),
            custom_fields=estimate.custom_fields.copy(),
            internal_notes=estimate.internal_notes,
            valid_until_date=estimate.terms.get_expiry_date(estimate.created_date.date()),
            po_number=estimate.po_number,
            issue_date=estimate.issue_date,
            created_by=estimate.created_by,
            created_date=estimate.created_date,
            last_modified=estimate.last_modified,
            sent_date=estimate.sent_date,
            viewed_date=estimate.viewed_date,
            responded_date=estimate.responded_date,
            # Financial calculations
            total_amount=estimate.get_total_amount(),
            subtotal=estimate.get_total_before_tax(),
            tax_amount=estimate.get_tax_amount(),
            discount_amount=estimate.get_line_items_discount_total() + estimate.get_overall_discount_amount(),
            # Status calculations
            is_expired=estimate.is_expired(),
            days_until_expiry=estimate.days_until_expiry()
        )


@dataclass
class CreateEstimateDTO:
    """DTO for creating new estimates."""
    contact_id: uuid.UUID
    title: str
    description: Optional[str] = None
    document_type: Optional[str] = "estimate"
    line_items: List[dict] = None
    currency: Optional[str] = "USD"
    tax_rate: Optional[float] = 0.0
    tax_type: Optional[str] = "percentage"
    overall_discount_type: Optional[str] = "none"
    overall_discount_value: Optional[float] = 0.0
    terms: Optional[dict] = None
    advance_payment: Optional[dict] = None
    template_id: Optional[uuid.UUID] = None
    template_data: Optional[Dict[str, Any]] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    internal_notes: Optional[str] = None
    valid_until_date: Optional[date] = None
    estimate_number: Optional[str] = None
    number_prefix: Optional[str] = "EST"
    po_number: Optional[str] = None
    issue_date: Optional[date] = None

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
class UpdateEstimateDTO:
    """DTO for updating existing estimates."""
    title: Optional[str] = None
    description: Optional[str] = None
    document_type: Optional[str] = None
    contact_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    line_items: Optional[List[dict]] = None
    currency: Optional[str] = None
    tax_rate: Optional[float] = None
    tax_type: Optional[str] = None
    overall_discount_type: Optional[str] = None
    overall_discount_value: Optional[float] = None
    terms: Optional[dict] = None
    advance_payment: Optional[dict] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    internal_notes: Optional[str] = None
    valid_until_date: Optional[date] = None
    po_number: Optional[str] = None
    issue_date: Optional[date] = None


@dataclass
class EstimateListFilters:
    """DTO for estimate list filtering."""
    status: Optional[str] = None
    contact_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


@dataclass
class EstimateSearchCriteria:
    """DTO for estimate search criteria."""
    search_term: Optional[str] = None
    status: Optional[str] = None
    document_type: Optional[str] = None
    contact_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    template_id: Optional[uuid.UUID] = None
    currency: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    created_by: Optional[str] = None
    include_expired: bool = False
    sort_by: str = "created_date"
    sort_order: str = "desc"


@dataclass
class EstimateTemplateListFilters:
    """DTO for estimate template list filtering."""
    business_id: uuid.UUID
    template_type: Optional[str] = None
    is_active: Optional[bool] = True
    is_default: Optional[bool] = None
    skip: int = 0
    limit: int = 100


@dataclass
class EstimateTemplateListResponseDTO:
    """DTO for estimate template list responses."""
    templates: List['EstimateTemplateResponseDTO']
    total_count: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


@dataclass
class EstimateTemplateResponseDTO:
    """DTO for estimate template responses."""
    # Required fields (no defaults) must come first
    id: uuid.UUID
    name: str
    template_type: str
    is_active: bool
    is_default: bool
    is_system_template: bool
    usage_count: int
    created_date: datetime
    last_modified: datetime
    
    # Optional fields (with defaults) come last
    business_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    last_used_date: Optional[datetime] = None
    created_by: Optional[str] = None
    tags: List[str] = None
    category: Optional[str] = None
    version: str = "1.0"

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    @classmethod
    def from_entity(cls, template) -> 'EstimateTemplateResponseDTO':
        """Create DTO from domain entity."""
        return cls(
            id=template.id,
            name=template.name,
            template_type=template.template_type.value if hasattr(template.template_type, 'value') else str(template.template_type),
            is_active=template.is_active,
            is_default=template.is_default,
            is_system_template=template.is_system_template,
            usage_count=template.usage_count,
            created_date=template.created_date,
            last_modified=template.last_modified,
            business_id=template.business_id,
            description=template.description,
            last_used_date=template.last_used_date,
            created_by=template.created_by,
            tags=template.tags.copy() if template.tags else [],
            category=template.category,
            version=template.version
        )
