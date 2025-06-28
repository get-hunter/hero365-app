"""
Contact API Schemas

Request and response schemas for contact management endpoints.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator, field_serializer, model_validator
from enum import Enum

from ...utils import format_datetime_utc
# Import centralized enums
from ...domain.enums import (
    ContactType, ContactStatus, ContactPriority, ContactSource,
    RelationshipStatus, LifecycleStage
)
from ..converters import EnumConverter, SupabaseConverter


# User reference schemas
class UserReferenceBasic(BaseModel):
    """Basic user reference information."""
    id: str = Field(..., description="User ID")
    display_name: str = Field(..., description="User display name")
    email: Optional[str] = Field(None, description="User email")


class UserReferenceFull(BaseModel):
    """Full user reference information."""
    id: str = Field(..., description="User ID")
    display_name: str = Field(..., description="User display name")
    email: Optional[str] = Field(None, description="User email")
    full_name: Optional[str] = Field(None, description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: Optional[str] = Field(None, description="Business role")
    department: Optional[str] = Field(None, description="Department")
    is_active: bool = Field(True, description="Active status")


# Enum for user detail inclusion levels
class UserDetailLevel(str, Enum):
    """User detail inclusion levels."""
    NONE = "none"
    BASIC = "basic"
    FULL = "full"


# Use centralized enums directly as API schemas
ContactTypeSchema = ContactType
ContactStatusSchema = ContactStatus  
ContactPrioritySchema = ContactPriority
ContactSourceSchema = ContactSource
RelationshipStatusSchema = RelationshipStatus
LifecycleStageSchema = LifecycleStage


class InteractionTypeSchema(str, Enum):
    """Schema for interaction types."""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    PROPOSAL = "proposal"
    QUOTE = "quote"
    CONTRACT = "contract"
    SERVICE = "service"
    FOLLOW_UP = "follow_up"
    NOTE = "note"


# Address schema
class ContactAddressSchema(BaseModel):
    """Schema for contact address."""
    street_address: Optional[str] = Field(None, max_length=200, description="Street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State or province")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal or ZIP code")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    latitude: Optional[float] = Field(default=None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[float] = Field(default=None, ge=-180, le=180, description="Longitude coordinate")
    access_notes: Optional[str] = Field(default=None, max_length=500, description="Access notes for service visits")
    place_id: Optional[str] = Field(default=None, max_length=255, description="Google Places ID")
    formatted_address: Optional[str] = Field(default=None, max_length=500, description="Full formatted address")
    address_type: Optional[str] = Field(default=None, max_length=50, description="Address type (residential, commercial, etc.)")

    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v):
        """Allow empty postal codes but validate format if provided."""
        if v is not None and v.strip() == "":
            return None  # Convert empty strings to None
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "street_address": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "postal_code": "12345",
                "country": "US",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "access_notes": "Ring doorbell twice",
                "place_id": "ChIJ2eUgeAK6j4ARbn5u_wAGqWA",
                "formatted_address": "123 Main St, Anytown, CA 12345, USA",
                "address_type": "residential"
            }
        }
    }


# Status history schema
class StatusHistoryEntrySchema(BaseModel):
    """Schema for status history entry."""
    id: uuid.UUID = Field(..., description="Status history entry ID")
    from_status: Optional[RelationshipStatusSchema] = Field(None, description="Previous status")
    to_status: RelationshipStatusSchema = Field(..., description="New status")
    timestamp: datetime = Field(..., description="Change timestamp")
    changed_by: str = Field(..., description="User who made the change")
    reason: Optional[str] = Field(None, description="Reason for status change")
    
    @field_serializer('timestamp')
    def serialize_datetime(self, value: datetime) -> str:
        return format_datetime_utc(value)


# Interaction schemas
class ContactInteractionCreateRequest(BaseModel):
    """Request schema for creating contact interaction."""
    type: InteractionTypeSchema = Field(..., description="Type of interaction")
    description: str = Field(..., min_length=1, max_length=1000, description="Interaction description")
    outcome: Optional[str] = Field(None, max_length=200, description="Interaction outcome")
    next_action: Optional[str] = Field(None, max_length=500, description="Next action to take")
    scheduled_follow_up: Optional[datetime] = Field(None, description="Scheduled follow-up date")


class ContactInteractionUpdateRequest(BaseModel):
    """Request schema for updating contact interaction."""
    type: Optional[InteractionTypeSchema] = Field(None, description="Type of interaction")
    description: Optional[str] = Field(None, min_length=1, max_length=1000, description="Interaction description")
    outcome: Optional[str] = Field(None, max_length=200, description="Interaction outcome")
    next_action: Optional[str] = Field(None, max_length=500, description="Next action to take")
    scheduled_follow_up: Optional[datetime] = Field(None, description="Scheduled follow-up date")


class ContactInteractionResponse(BaseModel):
    """Response schema for contact interaction."""
    id: uuid.UUID = Field(..., description="Interaction ID")
    contact_id: uuid.UUID = Field(..., description="Contact ID")
    type: InteractionTypeSchema = Field(..., description="Type of interaction")
    description: str = Field(..., description="Interaction description")
    timestamp: datetime = Field(..., description="Interaction timestamp")
    outcome: Optional[str] = Field(None, description="Interaction outcome")
    next_action: Optional[str] = Field(None, description="Next action to take")
    scheduled_follow_up: Optional[datetime] = Field(None, description="Scheduled follow-up date")
    performed_by: Union[str, UserReferenceBasic, UserReferenceFull] = Field(..., description="User who performed the interaction (ID or object based on include_user_details)")
    
    @field_serializer('timestamp', 'scheduled_follow_up')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class ContactInteractionListResponse(BaseModel):
    """Response schema for contact interaction list."""
    interactions: List[ContactInteractionResponse] = Field(default_factory=list)
    total: int = Field(..., description="Total number of interactions")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items per page")


# Status update schemas
class ContactStatusUpdateRequest(BaseModel):
    """Request schema for updating contact relationship status."""
    relationship_status: RelationshipStatusSchema = Field(..., description="New relationship status")
    lifecycle_stage: Optional[LifecycleStageSchema] = Field(None, description="New lifecycle stage (optional, will be auto-set if not provided)")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


class ContactStatusUpdateResponse(BaseModel):
    """Response schema for contact status update."""
    contact_id: uuid.UUID = Field(..., description="Contact ID")
    old_status: RelationshipStatusSchema = Field(..., description="Previous relationship status")
    new_status: RelationshipStatusSchema = Field(..., description="New relationship status")
    old_lifecycle_stage: LifecycleStageSchema = Field(..., description="Previous lifecycle stage")
    new_lifecycle_stage: LifecycleStageSchema = Field(..., description="New lifecycle stage")
    changed_by: str = Field(..., description="User who made the change")
    timestamp: datetime = Field(..., description="Change timestamp")
    reason: Optional[str] = Field(None, description="Reason for status change")
    
    @field_serializer('timestamp')
    def serialize_datetime(self, value: datetime) -> str:
        return format_datetime_utc(value)


# Request schemas
class ContactCreateRequest(BaseModel):
    """Request schema for creating a new contact."""
    contact_type: ContactTypeSchema = Field(..., description="Type of contact")
    relationship_status: Optional[RelationshipStatusSchema] = Field(None, description="Relationship status (auto-set based on contact_type if not provided)")
    lifecycle_stage: Optional[LifecycleStageSchema] = Field(None, description="Lifecycle stage (auto-set based on relationship_status if not provided)")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name")
    company_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Company name")
    job_title: Optional[str] = Field(None, max_length=100, description="Job title")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    mobile_phone: Optional[str] = Field(None, max_length=20, description="Mobile phone number")
    website: Optional[str] = Field(None, max_length=200, description="Website URL")
    address: Optional[ContactAddressSchema] = Field(None, description="Contact address")
    priority: ContactPrioritySchema = Field(ContactPrioritySchema.MEDIUM, description="Contact priority")
    source: Optional[ContactSourceSchema] = Field(None, description="Contact source")
    tags: List[str] = Field(default_factory=list, description="Contact tags")
    notes: Optional[str] = Field(None, description="Additional notes")
    estimated_value: Optional[float] = Field(None, ge=0, description="Estimated value")
    currency: str = Field("USD", min_length=3, max_length=3, description="Currency code")
    assigned_to: Optional[str] = Field(None, description="Assigned user ID")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")
    
    @field_validator('email')
    @classmethod
    def validate_email_or_phone_required(cls, v, info):
        """At least one contact method (email or phone) must be provided."""
        # Note: This validation will be enhanced in the use case layer
        return v


class ContactUpdateRequest(BaseModel):
    """Request schema for updating a contact."""
    contact_type: Optional[ContactTypeSchema] = Field(None, description="Type of contact")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name")
    company_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Company name")
    job_title: Optional[str] = Field(None, max_length=100, description="Job title")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    mobile_phone: Optional[str] = Field(None, max_length=20, description="Mobile phone number")
    website: Optional[str] = Field(None, max_length=200, description="Website URL")
    address: Optional[ContactAddressSchema] = Field(None, description="Contact address")
    priority: Optional[ContactPrioritySchema] = Field(None, description="Contact priority")
    source: Optional[ContactSourceSchema] = Field(None, description="Contact source")
    tags: Optional[List[str]] = Field(None, description="Contact tags")
    notes: Optional[str] = Field(None, description="Additional notes")
    estimated_value: Optional[float] = Field(None, ge=0, description="Estimated value")
    currency: Optional[str] = Field(None, min_length=3, max_length=3, description="Currency code")
    assigned_to: Optional[str] = Field(None, description="Assigned user ID")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields")


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
    include_user_details: UserDetailLevel = Field(UserDetailLevel.BASIC, description="Level of user detail to include")


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
    """Response schema for contact data with robust validation."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Contact ID")
    business_id: uuid.UUID = Field(..., description="Business ID")
    contact_type: ContactTypeSchema = Field(..., description="Contact type")
    status: ContactStatusSchema = Field(..., description="Contact status")
    relationship_status: RelationshipStatusSchema = Field(..., description="Relationship status")
    lifecycle_stage: LifecycleStageSchema = Field(..., description="Lifecycle stage")
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
    currency: str = Field("USD", description="Currency code")
    assigned_to: Optional[Union[str, UserReferenceBasic, UserReferenceFull]] = Field(None, description="Assigned user (ID or object based on include_user_details)")
    created_by: Optional[Union[str, UserReferenceBasic, UserReferenceFull]] = Field(None, description="Creator user (ID or object based on include_user_details)")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")
    
    # Status and interaction history
    status_history: List[StatusHistoryEntrySchema] = Field(default_factory=list, description="Status change history")
    interaction_history: List[ContactInteractionResponse] = Field(default_factory=list, description="Recent interactions")
    
    # Timestamps
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
    relationship_status_display: str = Field(..., description="Human-readable relationship status")
    lifecycle_stage_display: str = Field(..., description="Human-readable lifecycle stage")
    
    # Field validators for robust enum handling from Supabase
    @field_validator('contact_type', mode='before')
    @classmethod
    def validate_contact_type(cls, v):
        return EnumConverter.safe_contact_type(v)
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_contact_status(v)
    
    @field_validator('relationship_status', mode='before')
    @classmethod
    def validate_relationship_status(cls, v):
        return EnumConverter.safe_relationship_status(v)
    
    @field_validator('lifecycle_stage', mode='before')
    @classmethod
    def validate_lifecycle_stage(cls, v):
        return EnumConverter.safe_lifecycle_stage(v)
    
    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, v):
        return EnumConverter.safe_contact_priority(v)
    
    @field_validator('source', mode='before')
    @classmethod
    def validate_source(cls, v):
        return EnumConverter.safe_contact_source(v)
    
    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        return SupabaseConverter.parse_list_field(v, [])
    
    @field_validator('custom_fields', mode='before')
    @classmethod
    def validate_custom_fields(cls, v):
        return SupabaseConverter.parse_dict_field(v, {})
    
    @field_validator('created_date', 'last_modified', 'last_contacted', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.parse_datetime(v)
    
    @field_validator('id', 'business_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.parse_uuid(v)
    
    @classmethod
    def from_supabase_dict(cls, data: Dict[str, Any]) -> "ContactResponse":
        """Create ContactResponse from Supabase dictionary with safe conversion."""
        # Compute display fields
        display_name = cls._compute_display_name(data)
        primary_contact_method = cls._compute_primary_contact_method(data)
        
        # Add computed fields to data
        computed_data = {
            **data,
            'display_name': display_name,
            'primary_contact_method': primary_contact_method,
            'type_display': EnumConverter.safe_contact_type(data.get('contact_type')).get_display(),
            'status_display': EnumConverter.safe_contact_status(data.get('status')).get_display(),
            'priority_display': EnumConverter.safe_contact_priority(data.get('priority')).get_display(),
            'source_display': EnumConverter.safe_contact_source(data.get('source')).get_display() if data.get('source') else 'Unknown',
            'relationship_status_display': EnumConverter.safe_relationship_status(data.get('relationship_status')).get_display(),
            'lifecycle_stage_display': EnumConverter.safe_lifecycle_stage(data.get('lifecycle_stage')).get_display(),
        }
        
        return cls.model_validate(computed_data)
    
    @staticmethod
    def _compute_display_name(data: Dict[str, Any]) -> str:
        """Compute display name from contact data."""
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        company_name = data.get('company_name', '').strip()
        
        if first_name and last_name:
            return f"{first_name} {last_name}"
        elif first_name:
            return first_name
        elif last_name:
            return last_name
        elif company_name:
            return company_name
        else:
            return "Unknown Contact"
    
    @staticmethod
    def _compute_primary_contact_method(data: Dict[str, Any]) -> str:
        """Compute primary contact method from contact data."""
        if data.get('email'):
            return 'email'
        elif data.get('mobile_phone'):
            return 'mobile_phone'
        elif data.get('phone'):
            return 'phone'
        else:
            return 'none'
    
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