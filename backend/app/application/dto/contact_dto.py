"""
Contact Data Transfer Objects

DTOs for contact-related data transfer operations.
"""

import uuid
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

from ...domain.entities.contact import ContactType, ContactStatus, ContactSource, ContactPriority, ContactAddress, RelationshipStatus, LifecycleStage
from ...api.schemas.contact_schemas import UserDetailLevel


@dataclass
class ContactAddressDTO:
    """DTO for contact address information."""
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


@dataclass
class UserReferenceBasicDTO:
    """DTO for basic user reference information."""
    id: str
    display_name: str
    email: Optional[str] = None


@dataclass  
class UserReferenceFullDTO:
    """DTO for full user reference information."""
    id: str
    display_name: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    is_active: bool = True


@dataclass
class ContactCreateDTO:
    """DTO for creating a new contact."""
    business_id: uuid.UUID
    contact_type: ContactType
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[ContactAddressDTO] = None
    priority: ContactPriority = ContactPriority.MEDIUM
    source: Optional[ContactSource] = None
    tags: List[str] = None
    notes: Optional[str] = None
    estimated_value: Optional[float] = None
    currency: str = "USD"
    assigned_to: Optional[str] = None
    created_by: Optional[str] = None
    custom_fields: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.custom_fields is None:
            self.custom_fields = {}


@dataclass
class ContactUpdateDTO:
    """DTO for updating contact information."""
    contact_id: uuid.UUID
    business_id: uuid.UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[ContactAddressDTO] = None
    priority: Optional[ContactPriority] = None
    source: Optional[ContactSource] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    estimated_value: Optional[float] = None
    currency: Optional[str] = None
    assigned_to: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class ContactResponseDTO:
    """DTO for contact response data."""
    id: uuid.UUID
    business_id: uuid.UUID
    contact_type: ContactType
    status: ContactStatus
    relationship_status: RelationshipStatus
    lifecycle_stage: LifecycleStage
    first_name: Optional[str]
    last_name: Optional[str]
    company_name: Optional[str]
    job_title: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    mobile_phone: Optional[str]
    website: Optional[str]
    address: Optional[ContactAddressDTO]
    priority: ContactPriority
    source: Optional[ContactSource]
    tags: List[str]
    notes: Optional[str]
    estimated_value: Optional[float]
    currency: str
    assigned_to: Optional[Union[str, UserReferenceBasicDTO, UserReferenceFullDTO]]
    created_by: Optional[Union[str, UserReferenceBasicDTO, UserReferenceFullDTO]]
    custom_fields: Dict[str, Any]
    created_date: Optional[datetime]
    last_modified: Optional[datetime]
    last_contacted: Optional[datetime]
    
    # Computed fields
    display_name: str
    primary_contact_method: str
    type_display: str
    status_display: str
    priority_display: str
    source_display: str
    relationship_status_display: str
    lifecycle_stage_display: str


@dataclass
class ContactListDTO:
    """DTO for contact list with pagination."""
    contacts: List[ContactResponseDTO]
    total_count: int
    page: int
    per_page: int
    has_next: bool
    has_previous: bool


@dataclass
class ContactSearchDTO:
    """DTO for contact search parameters."""
    business_id: uuid.UUID
    search_term: Optional[str] = None
    contact_type: Optional[ContactType] = None
    status: Optional[ContactStatus] = None
    priority: Optional[ContactPriority] = None
    source: Optional[ContactSource] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None
    has_email: Optional[bool] = None
    has_phone: Optional[bool] = None
    min_estimated_value: Optional[float] = None
    max_estimated_value: Optional[float] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_contacted_after: Optional[datetime] = None
    last_contacted_before: Optional[datetime] = None
    never_contacted: Optional[bool] = None
    skip: int = 0
    limit: int = 100
    sort_by: str = "created_date"
    sort_order: str = "desc"  # "asc" or "desc"
    include_user_details: UserDetailLevel = UserDetailLevel.BASIC


@dataclass
class ContactBulkUpdateDTO:
    """DTO for bulk contact updates."""
    business_id: uuid.UUID
    contact_ids: List[uuid.UUID]
    status: Optional[ContactStatus] = None
    priority: Optional[ContactPriority] = None
    assigned_to: Optional[str] = None
    tags_to_add: Optional[List[str]] = None
    tags_to_remove: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class ContactStatisticsDTO:
    """DTO for contact statistics."""
    total_contacts: int
    active_contacts: int
    inactive_contacts: int
    archived_contacts: int
    blocked_contacts: int
    customers: int
    leads: int
    prospects: int
    vendors: int
    partners: int
    contractors: int
    high_priority: int
    medium_priority: int
    low_priority: int
    urgent_priority: int
    with_email: int
    with_phone: int
    assigned_contacts: int
    unassigned_contacts: int
    never_contacted: int
    recently_contacted: int
    high_value_contacts: int
    total_estimated_value: float
    average_estimated_value: float


@dataclass
class ContactConversionDTO:
    """DTO for contact type conversion."""
    contact_id: uuid.UUID
    business_id: uuid.UUID
    from_type: ContactType
    to_type: ContactType
    notes: Optional[str] = None


@dataclass
class ContactAssignmentDTO:
    """DTO for contact assignment operations."""
    business_id: uuid.UUID
    contact_ids: List[uuid.UUID]
    assigned_to: Optional[str] = None  # None to unassign
    notes: Optional[str] = None


@dataclass
class ContactTagOperationDTO:
    """DTO for contact tag operations."""
    business_id: uuid.UUID
    contact_ids: List[uuid.UUID]
    tags: List[str]
    operation: str  # "add", "remove", "replace"


@dataclass
class ContactExportDTO:
    """DTO for contact export operations."""
    business_id: uuid.UUID
    format: str  # "csv", "xlsx", "json"
    filters: Optional[ContactSearchDTO] = None
    fields: Optional[List[str]] = None  # Specific fields to export
    include_custom_fields: bool = True
    include_tags: bool = True


@dataclass
class ContactImportDTO:
    """DTO for contact import operations."""
    business_id: uuid.UUID
    file_data: bytes
    file_format: str  # "csv", "xlsx", "json"
    mapping: Dict[str, str]  # Maps file columns to contact fields
    skip_duplicates: bool = True
    update_existing: bool = False
    default_contact_type: ContactType = ContactType.LEAD
    default_status: ContactStatus = ContactStatus.ACTIVE
    created_by: Optional[str] = None


@dataclass
class ContactImportResultDTO:
    """DTO for contact import results."""
    total_processed: int
    successful_imports: int
    failed_imports: int
    duplicates_skipped: int
    existing_updated: int
    errors: List[Dict[str, Any]]  # List of error details
    imported_contact_ids: List[uuid.UUID] 