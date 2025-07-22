"""
Estimate DTOs for application layer

Data Transfer Objects for estimate operations with validation and transformation.
"""

import uuid
from typing import Optional, List, Dict, Any, Union, Annotated
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator, UUID4, BeforeValidator

from app.domain.entities.estimate import Estimate
from app.domain.entities.estimate_enums.enums import EstimateStatus, DocumentType
from app.domain.shared.enums import CurrencyCode, DiscountType, TaxType


# Validated enum field types for DTOs (same as domain entity)
def validate_estimate_status(v) -> EstimateStatus:
    """Convert string to EstimateStatus enum."""
    if isinstance(v, str):
        # Use the parse_from_string method for better string handling
        parsed_status = EstimateStatus.parse_from_string(v)
        if parsed_status:
            return parsed_status
        # Fallback to direct enum constructor for backward compatibility
        return EstimateStatus(v)
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

# Define validated enum field types for DTOs
EstimateStatusField = Annotated[EstimateStatus, BeforeValidator(validate_estimate_status)]
CurrencyField = Annotated[CurrencyCode, BeforeValidator(validate_currency_code)]
DocumentTypeField = Annotated[DocumentType, BeforeValidator(validate_document_type)]
TaxTypeField = Annotated[TaxType, BeforeValidator(validate_tax_type)]
DiscountTypeField = Annotated[DiscountType, BeforeValidator(validate_discount_type)]


class EstimateFilters(BaseModel):
    """Unified filters for estimate queries."""
    
    # Status and lifecycle filters
    status: Optional[EstimateStatus] = Field(None, description="Filter by estimate status")
    status_list: Optional[List[EstimateStatus]] = Field(None, description="Filter by multiple statuses")
    
    # Relationship filters
    contact_id: Optional[UUID4] = Field(None, description="Filter by contact ID")
    project_id: Optional[UUID4] = Field(None, description="Filter by project ID")
    job_id: Optional[UUID4] = Field(None, description="Filter by job ID")
    template_id: Optional[UUID4] = Field(None, description="Filter by template ID")
    
    # Date range filters
    date_from: Optional[date] = Field(None, description="Filter estimates from this date")
    date_to: Optional[date] = Field(None, description="Filter estimates to this date")
    created_from: Optional[datetime] = Field(None, description="Filter by creation date from")
    created_to: Optional[datetime] = Field(None, description="Filter by creation date to")
    sent_from: Optional[datetime] = Field(None, description="Filter by sent date from")
    sent_to: Optional[datetime] = Field(None, description="Filter by sent date to")
    
    # Value range filters
    min_value: Optional[Decimal] = Field(None, ge=0, description="Minimum estimate value")
    max_value: Optional[Decimal] = Field(None, ge=0, description="Maximum estimate value")
    
    # Currency and financial filters
    currency: Optional[CurrencyCode] = Field(None, description="Filter by currency")
    
    # Client filters
    client_name_contains: Optional[str] = Field(None, min_length=1, max_length=200, description="Filter by client name containing text")
    client_email: Optional[str] = Field(None, description="Filter by client email")
    
    # Content filters
    title_contains: Optional[str] = Field(None, min_length=1, max_length=300, description="Filter by title containing text")
    description_contains: Optional[str] = Field(None, min_length=1, description="Filter by description containing text")
    estimate_number_contains: Optional[str] = Field(None, min_length=1, description="Filter by estimate number containing text")
    
    # Special filters
    is_expired: Optional[bool] = Field(None, description="Filter expired estimates")
    is_expiring_soon: Optional[bool] = Field(None, description="Filter estimates expiring soon")
    expiring_days: Optional[int] = Field(default=7, ge=1, le=365, description="Days threshold for expiring soon")
    has_advance_payment: Optional[bool] = Field(None, description="Filter estimates with advance payment")
    
    # Search
    search_term: Optional[str] = Field(None, min_length=1, description="General search term")
    
    # Sorting
    sort_by: Optional[str] = Field(
        default="created_date", 
        description="Sort field",
        pattern="^(created_date|last_modified|title|status|total_amount|client_name|estimate_number)$"
    )
    sort_desc: bool = Field(default=True, description="Sort in descending order")
    
    # Tags and metadata
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    has_tags: Optional[bool] = Field(None, description="Filter estimates with or without tags")
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        """Validate date range consistency."""
        date_from = values.get('date_from')
        if date_from and v and v < date_from:
            raise ValueError("date_to must be after date_from")
        return v
    
    @validator('max_value')
    def validate_value_range(cls, v, values):
        """Validate value range consistency."""
        min_value = values.get('min_value')
        if min_value and v and v < min_value:
            raise ValueError("max_value must be greater than min_value")
        return v
    
    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        return any([
            self.status, self.status_list, self.contact_id, self.project_id, self.job_id,
            self.date_from, self.date_to, self.min_value, self.max_value,
            self.currency, self.client_name_contains, self.client_email,
            self.title_contains, self.description_contains, self.estimate_number_contains,
            self.is_expired, self.is_expiring_soon, self.has_advance_payment,
            self.search_term, self.tags, self.has_tags is not None
        ])
    
    def to_query_dict(self) -> Dict[str, Any]:
        """Convert filters to dictionary for repository queries."""
        filters = {}
        
        # Add non-None filters
        for field, value in self.dict(exclude_none=True).items():
            if field not in ['sort_by', 'sort_desc', 'expiring_days']:
                filters[field] = value
        
        return filters

    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            UUID4: lambda v: str(v),
            uuid.UUID: lambda v: str(v),
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }
    }


class EstimateCreateDTO(BaseModel):
    """DTO for creating estimates."""
    
    # Required fields
    title: str = Field(..., min_length=1, max_length=300, description="Estimate title")
    business_id: UUID4 = Field(..., description="Business ID")
    
    # Optional core fields
    description: Optional[str] = Field(None, max_length=2000, description="Estimate description")
    po_number: Optional[str] = Field(None, max_length=100, description="Purchase order number")
    
    # Client information
    contact_id: Optional[UUID4] = Field(None, description="Contact ID")
    client_name: Optional[str] = Field(None, max_length=200, description="Client name")
    client_email: Optional[str] = Field(None, max_length=254, description="Client email")
    client_phone: Optional[str] = Field(None, max_length=20, description="Client phone")
    
    # Financial settings
    currency: CurrencyField = Field(default=CurrencyCode.USD)
    tax_rate: Decimal = Field(default=Decimal('0'), ge=0, description="Tax rate percentage")
    tax_type: TaxTypeField = Field(default=TaxType.PERCENTAGE)
    
    # Project relationships
    project_id: Optional[UUID4] = Field(None, description="Project ID")
    job_id: Optional[UUID4] = Field(None, description="Job ID")
    template_id: Optional[UUID4] = Field(None, description="Template ID")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Estimate tags")
    internal_notes: Optional[str] = Field(None, max_length=2000, description="Internal notes")
    created_by: Optional[str] = Field(None, max_length=100, description="Created by user")

    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            UUID4: lambda v: str(v),
            Decimal: lambda v: float(v)
        }
    }


class EstimateUpdateDTO(BaseModel):
    """DTO for updating estimates."""
    
    # Core fields
    title: Optional[str] = Field(None, min_length=1, max_length=300, description="Estimate title")
    description: Optional[str] = Field(None, max_length=2000, description="Estimate description")
    po_number: Optional[str] = Field(None, max_length=100, description="Purchase order number")
    
    # Client information
    client_name: Optional[str] = Field(None, max_length=200, description="Client name")
    client_email: Optional[str] = Field(None, max_length=254, description="Client email")
    client_phone: Optional[str] = Field(None, max_length=20, description="Client phone")
    
    # Financial settings
    tax_rate: Optional[Decimal] = Field(None, ge=0, description="Tax rate percentage")
    tax_type: Optional[TaxType] = Field(None)
    
    # Project relationships
    project_id: Optional[UUID4] = Field(None, description="Project ID")
    job_id: Optional[UUID4] = Field(None, description="Job ID")
    
    # Metadata
    tags: Optional[List[str]] = Field(None, description="Estimate tags")
    internal_notes: Optional[str] = Field(None, max_length=2000, description="Internal notes")

    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            UUID4: lambda v: str(v),
            Decimal: lambda v: float(v)
        }
    }


class EstimateDTO(BaseModel):
    """DTO for estimate representation."""
    
    # Core identification
    id: UUID4
    business_id: UUID4
    estimate_number: str
    
    # Document classification
    document_type: DocumentTypeField
    
    # Status and lifecycle
    status: EstimateStatusField
    
    # Client information
    contact_id: Optional[UUID4] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    client_address: Optional[Any] = None
    
    # Core content
    title: str
    description: Optional[str] = None
    po_number: Optional[str] = None
    line_items: Optional[List[Any]] = Field(default_factory=list, description="Estimate line items")
    
    # Financial information
    currency: CurrencyField
    tax_rate: Decimal
    tax_type: TaxTypeField
    overall_discount_type: Optional[DiscountTypeField] = None
    overall_discount_value: Optional[Decimal] = None
    
    # Project relationships
    project_id: Optional[UUID4] = None
    job_id: Optional[UUID4] = None
    template_id: Optional[UUID4] = None
    converted_to_invoice_id: Optional[UUID4] = None
    
    # Business objects
    terms: Optional[Any] = None
    advance_payment: Optional[Any] = None
    
    # Template and metadata
    template_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)
    internal_notes: Optional[str] = None
    
    # Dates
    created_date: datetime
    last_modified: datetime
    sent_date: Optional[datetime] = None
    viewed_date: Optional[datetime] = None
    responded_date: Optional[datetime] = None
    conversion_date: Optional[datetime] = None
    valid_until_date: Optional[date] = None
    issue_date: Optional[date] = None
    
    # Calculated fields
    line_items_count: int = Field(0, description="Number of line items")
    total_amount: Decimal = Field(Decimal('0'), description="Total estimate amount")
    status_display: str = Field("", description="Human-readable status")
    currency_display: str = Field("", description="Human-readable currency")
    client_display_name: str = Field("", description="Display name for client")
    document_type_display: str = Field("", description="Human-readable document type")
    is_expired: bool = Field(False, description="Whether estimate is expired")
    days_until_expiry: Optional[int] = Field(None, description="Days until expiry")
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    created_by: Optional[str] = None

    @classmethod
    def from_entity(cls, estimate: Estimate) -> "EstimateDTO":
        """Create DTO from domain entity."""
        return cls(
            id=estimate.id,
            business_id=estimate.business_id,
            estimate_number=estimate.estimate_number or "",
            document_type=estimate.document_type,
            status=estimate.status,
            contact_id=estimate.contact_id,
            client_name=estimate.client_name,
            client_email=estimate.client_email,
            client_phone=estimate.client_phone,
            client_address=estimate.client_address,
            title=estimate.title,
            description=estimate.description,
            po_number=estimate.po_number,
            line_items=estimate.line_items,
            currency=estimate.currency,
            tax_rate=estimate.tax_rate,
            tax_type=estimate.tax_type,
            overall_discount_type=estimate.overall_discount_type,
            overall_discount_value=estimate.overall_discount_value,
            project_id=estimate.project_id,
            job_id=estimate.job_id,
            template_id=estimate.template_id,
            converted_to_invoice_id=estimate.converted_to_invoice_id,
            terms=estimate.terms,
            advance_payment=estimate.advance_payment,
            template_data=estimate.template_data,
            custom_fields=estimate.custom_fields,
            internal_notes=estimate.internal_notes,
            created_date=estimate.created_date,
            last_modified=estimate.last_modified,
            sent_date=estimate.sent_date,
            viewed_date=estimate.viewed_date,
            responded_date=estimate.responded_date,
            conversion_date=estimate.conversion_date,
            valid_until_date=estimate.valid_until_date,
            issue_date=estimate.issue_date,
            line_items_count=len(estimate.line_items),
            total_amount=estimate.get_total_amount(),
            status_display=estimate.get_status_display() if hasattr(estimate.status, 'get_display') else str(estimate.status).title(),
            currency_display=estimate.get_currency_display() if hasattr(estimate.currency, 'get_display') else str(estimate.currency),
            client_display_name=estimate.get_client_display_name(),
            document_type_display=estimate.get_document_type_display() if hasattr(estimate.document_type, 'get_display') else str(estimate.document_type).title(),
            is_expired=estimate.is_expired(),
            days_until_expiry=estimate.days_until_expiry(),
            tags=estimate.tags,
            created_by=estimate.created_by
        )

    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            UUID4: lambda v: str(v),
            uuid.UUID: lambda v: str(v),
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat() if v else None
        }
    }


# Template DTOs (simplified for compatibility)
class EstimateTemplateListFilters(BaseModel):
    """Filters for estimate template listing."""
    
    name_contains: Optional[str] = Field(None, description="Filter by template name")
    category: Optional[str] = Field(None, description="Filter by template category")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    created_by: Optional[str] = Field(None, description="Filter by creator")
    
    # Sorting
    sort_by: Optional[str] = Field(default="name", description="Sort field")
    sort_desc: bool = Field(default=False, description="Sort in descending order")

    model_config = {
        "use_enum_values": True
    }


class EstimateTemplateResponseDTO(BaseModel):
    """DTO for estimate template representation."""
    
    id: UUID4
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True
    created_date: datetime
    created_by: Optional[str] = None

    @classmethod
    def from_entity(cls, template: Any) -> "EstimateTemplateResponseDTO":
        """Create DTO from domain entity."""
        return cls(
            id=template.id,
            name=template.name,
            description=template.description,
            category=template.category,
            is_active=template.is_active,
            created_date=template.created_date,
            created_by=template.created_by
        )

    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            UUID4: lambda v: str(v),
            datetime: lambda v: v.isoformat() if v else None
        }
    }


class EstimateTemplateListResponseDTO(BaseModel):
    """DTO for estimate template list response."""
    
    templates: List[EstimateTemplateResponseDTO]
    total_count: int = 0
    page: int = 1
    per_page: int = 50
    has_next: bool = False
    has_prev: bool = False

    model_config = {
        "use_enum_values": True
    }
