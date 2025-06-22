"""
Contact API Schemas

Request and response schemas for contact management endpoints.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator, field_serializer
from enum import Enum

from ...utils import format_datetime_utc


# Enum schemas
class ContactTypeSchema(str, Enum):
    """Schema for contact types."""
    CUSTOMER = "customer"
    LEAD = "lead"
    PROSPECT = "prospect"
    VENDOR = "vendor"
    PARTNER = "partner"
    CONTRACTOR = "contractor"


class ContactStatusSchema(str, Enum):
    """Schema for contact status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    BLOCKED = "blocked"


class ContactPrioritySchema(str, Enum):
    """Schema for contact priority."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ContactSourceSchema(str, Enum):
    """Schema for contact source."""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    ADVERTISING = "advertising"
    COLD_OUTREACH = "cold_outreach"
    EVENT = "event"
    PARTNER = "partner"
    EXISTING_CUSTOMER = "existing_customer"
    DIRECT = "direct"
    OTHER = "other"


# Address schema
class ContactAddressSchema(BaseModel):
    """Schema for contact address."""
    street_address: Optional[str] = Field(None, max_length=200, description="Street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State or province")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal or ZIP code")
    country: Optional[str] = Field(None, max_length=100, description="Country")


# Request schemas
class ContactCreateRequest(BaseModel):
    """Request schema for creating a contact."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    
    contact_type: ContactTypeSchema = Field(..., description="Type of contact")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    company_name: Optional[str] = Field(None, max_length=200, description="Company name")
    job_title: Optional[str] = Field(None, max_length=100, description="Job title")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    mobile_phone: Optional[str] = Field(None, max_length=20, description="Mobile phone number")
    website: Optional[str] = Field(None, max_length=200, description="Website URL")
    address: Optional[ContactAddressSchema] = Field(None, description="Contact address")
    priority: ContactPrioritySchema = Field(ContactPrioritySchema.MEDIUM, description="Contact priority")
    source: Optional[ContactSourceSchema] = Field(None, description="How contact was acquired")
    tags: List[str] = Field(default_factory=list, description="Contact tags")
    notes: Optional[str] = Field(None, max_length=5000, description="Additional notes")
    estimated_value: Optional[float] = Field(None, ge=0, description="Estimated value in USD")
    currency: str = Field("USD", max_length=3, description="Currency code")
    assigned_to: Optional[str] = Field(None, description="User ID of assigned team member")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")
    
    @field_validator('website')
    @classmethod
    def validate_website(cls, v):
        if v and not (v.startswith(('http://', 'https://')) or '.' in v):
            raise ValueError('Website must be a valid URL or domain')
        return v
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        if len(v) != 3:
            raise ValueError('Currency must be a 3-letter ISO code')
        return v.upper()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        # Remove empty tags and duplicates
        return list(set([tag.strip().lower() for tag in v if tag.strip()]))
    
    def model_validate(cls, values):
        """Validate that at least one name or company name is provided."""
        if not any([values.get('first_name'), values.get('last_name'), values.get('company_name')]):
            raise ValueError('At least one of first_name, last_name, or company_name is required')
        
        if not any([values.get('email'), values.get('phone'), values.get('mobile_phone')]):
            raise ValueError('At least one contact method (email, phone, or mobile_phone) is required')
        
        return values


class ContactUpdateRequest(BaseModel):
    """Request schema for updating a contact."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    company_name: Optional[str] = Field(None, max_length=200, description="Company name")
    job_title: Optional[str] = Field(None, max_length=100, description="Job title")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    mobile_phone: Optional[str] = Field(None, max_length=20, description="Mobile phone number")
    website: Optional[str] = Field(None, max_length=200, description="Website URL")
    address: Optional[ContactAddressSchema] = Field(None, description="Contact address")
    priority: Optional[ContactPrioritySchema] = Field(None, description="Contact priority")
    source: Optional[ContactSourceSchema] = Field(None, description="How contact was acquired")
    tags: Optional[List[str]] = Field(None, description="Contact tags")
    notes: Optional[str] = Field(None, max_length=5000, description="Additional notes")
    estimated_value: Optional[float] = Field(None, ge=0, description="Estimated value in USD")
    currency: Optional[str] = Field(None, max_length=3, description="Currency code")
    assigned_to: Optional[str] = Field(None, description="User ID of assigned team member")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields")
    
    @field_validator('website')
    @classmethod
    def validate_website(cls, v):
        if v and not (v.startswith(('http://', 'https://')) or '.' in v):
            raise ValueError('Website must be a valid URL or domain')
        return v
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        if v and len(v) != 3:
            raise ValueError('Currency must be a 3-letter ISO code')
        return v.upper() if v else v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            # Remove empty tags and duplicates
            return list(set([tag.strip().lower() for tag in v if tag.strip()]))
        return v


class ContactSearchRequest(BaseModel):
    """Request schema for searching contacts."""
    search_term: Optional[str] = Field(None, max_length=200, description="Search term")
    contact_type: Optional[ContactTypeSchema] = Field(None, description="Filter by contact type")
    status: Optional[ContactStatusSchema] = Field(None, description="Filter by status")
    priority: Optional[ContactPrioritySchema] = Field(None, description="Filter by priority")
    source: Optional[ContactSourceSchema] = Field(None, description="Filter by source")
    assigned_to: Optional[str] = Field(None, description="Filter by assigned user")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (OR operation)")
    has_email: Optional[bool] = Field(None, description="Filter contacts with/without email")
    has_phone: Optional[bool] = Field(None, description="Filter contacts with/without phone")
    min_estimated_value: Optional[float] = Field(None, ge=0, description="Minimum estimated value")
    max_estimated_value: Optional[float] = Field(None, ge=0, description="Maximum estimated value")
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    last_contacted_after: Optional[datetime] = Field(None, description="Last contacted after date")
    last_contacted_before: Optional[datetime] = Field(None, description="Last contacted before date")
    never_contacted: Optional[bool] = Field(None, description="Filter never contacted contacts")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")
    sort_by: str = Field("created_date", description="Field to sort by")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")


class ContactBulkUpdateRequest(BaseModel):
    """Request schema for bulk contact updates."""
    contact_ids: List[uuid.UUID] = Field(..., min_items=1, max_items=1000, description="Contact IDs to update")
    status: Optional[ContactStatusSchema] = Field(None, description="New status")
    priority: Optional[ContactPrioritySchema] = Field(None, description="New priority")
    assigned_to: Optional[str] = Field(None, description="User ID to assign contacts to")
    tags_to_add: Optional[List[str]] = Field(None, description="Tags to add")
    tags_to_remove: Optional[List[str]] = Field(None, description="Tags to remove")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields to update")


class ContactConversionRequest(BaseModel):
    """Request schema for contact type conversion."""
    to_type: ContactTypeSchema = Field(..., description="Target contact type")
    notes: Optional[str] = Field(None, max_length=500, description="Conversion notes")


class ContactAssignmentRequest(BaseModel):
    """Request schema for contact assignment."""
    contact_ids: List[uuid.UUID] = Field(..., min_items=1, max_items=1000, description="Contact IDs to assign")
    assigned_to: Optional[str] = Field(None, description="User ID to assign to (null to unassign)")
    notes: Optional[str] = Field(None, max_length=500, description="Assignment notes")


class ContactTagOperationRequest(BaseModel):
    """Request schema for contact tag operations."""
    contact_ids: List[uuid.UUID] = Field(..., min_items=1, max_items=1000, description="Contact IDs")
    tags: List[str] = Field(..., min_items=1, description="Tags to operate on")
    operation: str = Field(..., pattern="^(add|remove|replace)$", description="Operation type")


# Response schemas
class ContactResponse(BaseModel):
    """Response schema for contact data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="Contact ID")
    business_id: uuid.UUID = Field(..., description="Business ID")
    contact_type: ContactTypeSchema = Field(..., description="Contact type")
    status: ContactStatusSchema = Field(..., description="Contact status")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    company_name: Optional[str] = Field(None, description="Company name")
    job_title: Optional[str] = Field(None, description="Job title")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    mobile_phone: Optional[str] = Field(None, description="Mobile phone number")
    website: Optional[str] = Field(None, description="Website URL")
    address: Optional[ContactAddressSchema] = Field(None, description="Contact address")
    priority: ContactPrioritySchema = Field(..., description="Contact priority")
    source: Optional[ContactSourceSchema] = Field(None, description="Contact source")
    tags: List[str] = Field(default_factory=list, description="Contact tags")
    notes: Optional[str] = Field(None, description="Additional notes")
    estimated_value: Optional[float] = Field(None, description="Estimated value")
    currency: str = Field(..., description="Currency code")
    assigned_to: Optional[str] = Field(None, description="Assigned user ID")
    created_by: Optional[str] = Field(None, description="Creator user ID")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")
    created_date: Optional[datetime] = Field(None, description="Creation date")
    last_modified: Optional[datetime] = Field(None, description="Last modification date")
    last_contacted: Optional[datetime] = Field(None, description="Last contact date")
    
    # Computed fields
    display_name: str = Field(..., description="Display name")
    primary_contact_method: str = Field(..., description="Primary contact method")
    type_display: str = Field(..., description="Human-readable type")
    status_display: str = Field(..., description="Human-readable status")
    priority_display: str = Field(..., description="Human-readable priority")
    source_display: str = Field(..., description="Human-readable source")
    
    @field_serializer('created_date', 'last_modified', 'last_contacted')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class ContactListResponse(BaseModel):
    """Response schema for contact list with pagination."""
    contacts: List[ContactResponse] = Field(..., description="List of contacts")
    total_count: int = Field(..., description="Total number of contacts")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of contacts per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")


class ContactStatisticsResponse(BaseModel):
    """Response schema for contact statistics."""
    total_contacts: int = Field(..., description="Total number of contacts")
    active_contacts: int = Field(..., description="Number of active contacts")
    inactive_contacts: int = Field(..., description="Number of inactive contacts")
    archived_contacts: int = Field(..., description="Number of archived contacts")
    blocked_contacts: int = Field(..., description="Number of blocked contacts")
    customers: int = Field(..., description="Number of customers")
    leads: int = Field(..., description="Number of leads")
    prospects: int = Field(..., description="Number of prospects")
    vendors: int = Field(..., description="Number of vendors")
    partners: int = Field(..., description="Number of partners")
    contractors: int = Field(..., description="Number of contractors")
    high_priority: int = Field(..., description="Number of high priority contacts")
    medium_priority: int = Field(..., description="Number of medium priority contacts")
    low_priority: int = Field(..., description="Number of low priority contacts")
    urgent_priority: int = Field(..., description="Number of urgent priority contacts")
    with_email: int = Field(..., description="Number of contacts with email")
    with_phone: int = Field(..., description="Number of contacts with phone")
    assigned_contacts: int = Field(..., description="Number of assigned contacts")
    unassigned_contacts: int = Field(..., description="Number of unassigned contacts")
    never_contacted: int = Field(..., description="Number of never contacted contacts")
    recently_contacted: int = Field(..., description="Number of recently contacted contacts")
    high_value_contacts: int = Field(..., description="Number of high value contacts")
    total_estimated_value: float = Field(..., description="Total estimated value")
    average_estimated_value: float = Field(..., description="Average estimated value")


class ContactBulkOperationResponse(BaseModel):
    """Response schema for bulk operations."""
    updated_count: int = Field(..., description="Number of contacts updated")
    success: bool = Field(..., description="Whether operation was successful")
    message: str = Field(..., description="Operation result message")


class ContactExportResponse(BaseModel):
    """Response schema for contact export."""
    file_url: str = Field(..., description="URL to download exported file")
    file_name: str = Field(..., description="Name of exported file")
    format: str = Field(..., description="Export format")
    total_contacts: int = Field(..., description="Number of contacts exported")
    expires_at: datetime = Field(..., description="When download link expires")
    
    @field_serializer('expires_at')
    def serialize_expires_at(self, value: datetime) -> str:
        return format_datetime_utc(value)


class ContactImportResponse(BaseModel):
    """Response schema for contact import."""
    total_processed: int = Field(..., description="Total records processed")
    successful_imports: int = Field(..., description="Number of successful imports")
    failed_imports: int = Field(..., description="Number of failed imports")
    duplicates_skipped: int = Field(..., description="Number of duplicates skipped")
    existing_updated: int = Field(..., description="Number of existing contacts updated")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Import errors")
    imported_contact_ids: List[uuid.UUID] = Field(default_factory=list, description="IDs of imported contacts")


# Common response schemas
class MessageResponse(BaseModel):
    """Generic message response."""
    message: str = Field(..., description="Response message")
    success: bool = Field(True, description="Whether operation was successful")


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    code: Optional[str] = Field(None, description="Error code") 