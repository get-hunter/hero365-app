"""
Business Management API Schemas

Pydantic schemas for business management API endpoints.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator, field_serializer
from pydantic import ConfigDict

from ...domain.entities.business import CompanySize, ReferralSource
from ...domain.entities.business_membership import BusinessRole
from ...domain.entities.business_invitation import InvitationStatus
from ...utils import format_datetime_utc


# Enum schemas for API responses
class CompanySizeSchema(str, Enum):
    """Company size options for API."""
    JUST_ME = "just_me"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class BusinessRoleSchema(str, Enum):
    """Business role options for API."""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    CONTRACTOR = "contractor"
    VIEWER = "viewer"


class InvitationStatusSchema(str, Enum):
    """Invitation status options for API."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ReferralSourceSchema(str, Enum):
    """Referral source options for API."""
    SEARCH_ENGINE = "search_engine"
    SOCIAL_MEDIA = "social_media"
    FRIEND_REFERRAL = "friend_referral"
    ADVERTISEMENT = "advertisement"
    APP_STORE = "app_store"
    OTHER = "other"


# Business schemas
class BusinessCreateRequest(BaseModel):
    """Request schema for creating a business."""
    name: str = Field(..., min_length=1, max_length=100, description="Business name")
    industry: str = Field(..., min_length=1, max_length=50, description="Industry category")
    company_size: CompanySizeSchema = Field(..., description="Company size category")
    custom_industry: Optional[str] = Field(None, max_length=100, description="Custom industry if not in predefined list")
    description: Optional[str] = Field(None, max_length=500, description="Business description")
    phone_number: Optional[str] = Field(None, max_length=20, description="Business phone number")
    business_address: Optional[str] = Field(None, max_length=200, description="Business address")
    website: Optional[str] = Field(None, max_length=100, description="Business website URL")
    business_email: Optional[str] = Field(None, max_length=100, description="Business email address")
    selected_features: List[str] = Field(default_factory=list, description="Selected platform features")
    primary_goals: List[str] = Field(default_factory=list, description="Primary business goals")
    referral_source: Optional[ReferralSourceSchema] = Field(None, description="How did you hear about us")
    timezone: Optional[str] = Field(None, max_length=50, description="Business timezone")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Business name cannot be empty')
        return v.strip()
    
    @field_validator('website')
    @classmethod
    def validate_website(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Website must be a valid URL starting with http:// or https://')
        return v
    
    @field_validator('business_email')
    @classmethod
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Business email must be a valid email address')
        return v


class BusinessUpdateRequest(BaseModel):
    """Request schema for updating a business."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    industry: Optional[str] = Field(None, min_length=1, max_length=50)
    custom_industry: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    phone_number: Optional[str] = Field(None, max_length=20)
    business_address: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=200)
    business_email: Optional[str] = Field(None, max_length=100)
    business_registration_number: Optional[str] = Field(None, max_length=50)
    tax_id: Optional[str] = Field(None, max_length=50)
    business_license: Optional[str] = Field(None, max_length=50)
    insurance_number: Optional[str] = Field(None, max_length=50)
    timezone: Optional[str] = Field(None, max_length=50)
    currency: Optional[str] = Field(None, max_length=3)
    business_hours: Optional[dict] = Field(None, description="Business operating hours")
    max_team_members: Optional[int] = Field(None, ge=1, le=1000)
    subscription_tier: Optional[str] = Field(None, max_length=20)
    enabled_features: Optional[List[str]] = Field(None)


class BusinessResponse(BaseModel):
    """Response schema for business information."""
    model_config = ConfigDict(json_encoders={datetime: format_datetime_utc})
    
    id: uuid.UUID
    name: str
    industry: str
    company_size: CompanySizeSchema
    owner_id: str
    custom_industry: Optional[str]
    description: Optional[str]
    phone_number: Optional[str]
    business_address: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    business_email: Optional[str]
    business_registration_number: Optional[str]
    tax_id: Optional[str]
    business_license: Optional[str]
    insurance_number: Optional[str]
    selected_features: List[str]
    primary_goals: List[str]
    referral_source: Optional[ReferralSourceSchema]
    onboarding_completed: bool
    onboarding_completed_date: Optional[datetime]
    timezone: Optional[str]
    currency: str
    business_hours: Optional[dict]
    is_active: bool
    max_team_members: Optional[int]
    subscription_tier: Optional[str]
    enabled_features: List[str]
    created_date: Optional[datetime]
    last_modified: Optional[datetime]
    
    @field_serializer('created_date', 'last_modified', 'onboarding_completed_date')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to standardized UTC format."""
        return format_datetime_utc(dt)


class BusinessSummaryResponse(BaseModel):
    """Response schema for business summary information."""
    model_config = ConfigDict(json_encoders={datetime: format_datetime_utc})
    
    id: uuid.UUID
    name: str
    industry: str
    company_size: CompanySizeSchema
    is_active: bool
    created_date: Optional[datetime]
    team_member_count: Optional[int]
    onboarding_completed: bool
    
    @field_serializer('created_date')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to standardized UTC format."""
        return format_datetime_utc(dt)


# Business membership schemas
class BusinessMembershipResponse(BaseModel):
    """Response schema for business membership."""
    model_config = ConfigDict(json_encoders={datetime: format_datetime_utc})
    
    id: uuid.UUID
    business_id: uuid.UUID
    user_id: str
    role: BusinessRoleSchema
    permissions: List[str]
    joined_date: datetime
    invited_date: Optional[datetime]
    invited_by: Optional[str]
    is_active: bool
    department_id: Optional[uuid.UUID]
    job_title: Optional[str]
    role_display: str
    
    @field_serializer('joined_date', 'invited_date')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to standardized UTC format."""
        return format_datetime_utc(dt)


class BusinessMembershipUpdateRequest(BaseModel):
    """Request schema for updating business membership."""
    role: Optional[BusinessRoleSchema] = Field(None, description="New role for the member")
    permissions: Optional[List[str]] = Field(None, description="Custom permissions list")
    department_id: Optional[uuid.UUID] = Field(None, description="Department assignment")
    job_title: Optional[str] = Field(None, max_length=100, description="Job title")
    is_active: Optional[bool] = Field(None, description="Active status")


# Business invitation schemas
class BusinessInvitationCreateRequest(BaseModel):
    """Request schema for creating business invitations."""
    invited_email: Optional[str] = Field(None, max_length=100, description="Email address to invite")
    invited_phone: Optional[str] = Field(None, max_length=20, description="Phone number to invite")
    role: BusinessRoleSchema = Field(..., description="Role to assign to the invitee")
    message: Optional[str] = Field(None, max_length=500, description="Personal message for the invitation")
    permissions: Optional[List[str]] = Field(None, description="Custom permissions for the role")
    department_id: Optional[uuid.UUID] = Field(None, description="Department to assign")
    expiry_days: int = Field(7, ge=1, le=30, description="Days until invitation expires")
    
    @model_validator(mode='after')
    def validate_contact_method(self):
        # At least one contact method must be provided
        if not self.invited_email and not self.invited_phone:
            raise ValueError('Either email or phone number is required')
        
        # Validate email format if provided
        if self.invited_email and '@' not in self.invited_email:
            raise ValueError('Invalid email format')
        
        return self


class BusinessInvitationResponse(BaseModel):
    """Response schema for business invitations."""
    model_config = ConfigDict(json_encoders={datetime: format_datetime_utc})
    
    id: uuid.UUID
    business_id: uuid.UUID
    business_name: str
    invited_email: Optional[str]
    invited_phone: Optional[str]
    invited_by: str
    invited_by_name: str
    role: BusinessRoleSchema
    permissions: List[str]
    invitation_date: datetime
    expiry_date: datetime
    status: InvitationStatusSchema
    message: Optional[str]
    accepted_date: Optional[datetime]
    declined_date: Optional[datetime]
    role_display: str
    status_display: str
    expiry_summary: str
    
    @field_serializer('invitation_date', 'expiry_date', 'accepted_date', 'declined_date')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to standardized UTC format."""
        return format_datetime_utc(dt)


class BusinessInvitationAcceptRequest(BaseModel):
    """Request schema for accepting business invitations."""
    invitation_id: uuid.UUID = Field(..., description="ID of the invitation to accept")


class BusinessInvitationDeclineRequest(BaseModel):
    """Request schema for declining business invitations."""
    invitation_id: uuid.UUID = Field(..., description="ID of the invitation to decline")


# Combined response schemas
class UserBusinessSummaryResponse(BaseModel):
    """Response schema for user's business summary."""
    business: BusinessSummaryResponse
    membership: BusinessMembershipResponse
    is_owner: bool
    pending_invitations_count: Optional[int]


class BusinessDetailResponse(BaseModel):
    """Response schema for detailed business information."""
    business: BusinessResponse
    user_membership: BusinessMembershipResponse
    team_members: List[BusinessMembershipResponse]
    pending_invitations: List[BusinessInvitationResponse]
    total_members: int
    owner_membership: BusinessMembershipResponse


# Business onboarding schemas
class BusinessOnboardingUpdateRequest(BaseModel):
    """Request schema for updating business onboarding."""
    selected_features: Optional[List[str]] = Field(None, description="Selected platform features")
    primary_goals: Optional[List[str]] = Field(None, description="Primary business goals")
    complete_onboarding: bool = Field(False, description="Mark onboarding as complete")


# Business statistics schemas
class BusinessStatsResponse(BaseModel):
    """Response schema for business statistics."""
    total_businesses: int
    active_businesses: int
    total_memberships: int
    total_invitations: int
    pending_invitations: int
    expired_invitations: int


# Permission checking schemas
class BusinessPermissionCheckRequest(BaseModel):
    """Request schema for checking business permissions."""
    business_id: uuid.UUID = Field(..., description="Business ID to check permissions for")
    permission: str = Field(..., min_length=1, description="Permission to check")


class BusinessPermissionCheckResponse(BaseModel):
    """Response schema for business permission checks."""
    business_id: uuid.UUID
    user_id: str
    permission: str
    has_permission: bool
    user_role: Optional[BusinessRoleSchema]


# Search and filter schemas
class BusinessSearchRequest(BaseModel):
    """Request schema for business search."""
    query: Optional[str] = Field(None, max_length=100, description="Search query")
    industry: Optional[str] = Field(None, max_length=50, description="Filter by industry")
    company_size: Optional[CompanySizeSchema] = Field(None, description="Filter by company size")
    is_active: Optional[bool] = Field(True, description="Filter by active status")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of records to return")


# Bulk operations schemas
class BusinessTeamInviteRequest(BaseModel):
    """Request schema for bulk team invitations."""
    invitations: List[BusinessInvitationCreateRequest] = Field(
        ..., min_items=1, max_items=10, description="List of invitations to send"
    )


class BulkOperationResponse(BaseModel):
    """Response schema for bulk operations."""
    success_count: int
    failure_count: int
    errors: List[str] = Field(default_factory=list)
    results: List[dict] = Field(default_factory=list) 