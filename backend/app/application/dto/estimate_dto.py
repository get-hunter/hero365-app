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
            line_total=line_item.get_line_total(),
            discount_amount=line_item.get_discount_amount(),
            tax_amount=line_item.get_tax_amount(),
            final_total=line_item.get_final_total()
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
    title: str = ""
    description: Optional[str] = None
    line_items: List[EstimateLineItemDTO] = None
    currency: str = "USD"
    tax_rate: Decimal = Decimal('0')
    tax_type: str = "percentage"
    overall_discount_type: str = "none"
    overall_discount_value: Decimal = Decimal('0')
    template_id: Optional[uuid.UUID] = None
    template_data: Dict[str, Any] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    tags: List[str] = None
    custom_fields: Dict[str, Any] = None
    internal_notes: Optional[str] = None
    valid_until_date: Optional[date] = None
    created_by: Optional[str] = None
    created_date: datetime = None
    last_modified: datetime = None
    
    # Calculated financial fields
    total_amount: Optional[Decimal] = None

    def __post_init__(self):
        if self.line_items is None:
            self.line_items = []
        if self.template_data is None:
            self.template_data = {}
        if self.tags is None:
            self.tags = []
        if self.custom_fields is None:
            self.custom_fields = {}

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
            title=estimate.title,
            description=estimate.description,
            line_items=[EstimateLineItemDTO.from_entity(item) for item in estimate.line_items],
            currency=estimate.currency.value,
            tax_rate=estimate.tax_rate,
            tax_type=estimate.tax_type.value,
            overall_discount_type=estimate.overall_discount_type.value,
            overall_discount_value=estimate.overall_discount_value,
            template_id=estimate.template_id,
            template_data=estimate.template_data.copy(),
            project_id=estimate.project_id,
            job_id=estimate.job_id,
            tags=estimate.tags.copy(),
            custom_fields=estimate.custom_fields.copy(),
            internal_notes=estimate.internal_notes,
            valid_until_date=estimate.valid_until_date,
            created_by=estimate.created_by,
            created_date=estimate.created_date,
            last_modified=estimate.last_modified,
            total_amount=estimate.get_total_amount()
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
