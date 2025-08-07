"""
Business Data Transfer Objects

DTOs for business-related data transfer operations.
"""

import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from ...domain.entities.business import CompanySize, ReferralSource
from ...domain.entities.business_membership import BusinessRole, BusinessMembership
from ...domain.entities.business_invitation import InvitationStatus


class BusinessCreateDTO(BaseModel):
    """DTO for creating a new business."""
    name: str
    industry: str
    company_size: CompanySize
    owner_id: str
    custom_industry: Optional[str] = None
    description: Optional[str] = None
    phone_number: Optional[str] = None
    business_address: Optional[str] = None
    website: Optional[str] = None
    business_email: Optional[str] = None
    selected_features: List[str] = Field(default_factory=list)
    primary_goals: List[str] = Field(default_factory=list)
    referral_source: Optional[ReferralSource] = None
    timezone: Optional[str] = None


class BusinessUpdateDTO(BaseModel):
    """DTO for updating business information."""
    business_id: uuid.UUID
    name: Optional[str] = None
    industry: Optional[str] = None
    custom_industry: Optional[str] = None
    description: Optional[str] = None
    phone_number: Optional[str] = None
    business_address: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    business_email: Optional[str] = None
    business_registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    business_license: Optional[str] = None
    insurance_number: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    business_hours: Optional[dict] = None
    max_team_members: Optional[int] = None
    subscription_tier: Optional[str] = None
    enabled_features: Optional[List[str]] = None


class BusinessResponseDTO(BaseModel):
    """DTO for business response data."""
    id: uuid.UUID
    name: str
    industry: str
    company_size: CompanySize
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
    referral_source: Optional[ReferralSource]
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


class BusinessSummaryDTO(BaseModel):
    """DTO for business summary information."""
    id: uuid.UUID
    name: str
    industry: str
    company_size: CompanySize
    is_active: bool
    created_date: Optional[datetime]
    team_member_count: Optional[int] = None
    onboarding_completed: bool = False


class BusinessSearchDTO(BaseModel):
    """DTO for business search parameters."""
    query: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[CompanySize] = None
    is_active: Optional[bool] = True
    owner_id: Optional[str] = None
    skip: int = 0
    limit: int = 100


class BusinessMembershipCreateDTO(BaseModel):
    """DTO for creating a new business membership."""
    business_id: uuid.UUID
    user_id: str
    role: BusinessRole
    permissions: Optional[List[str]] = None
    invited_date: Optional[datetime] = None
    invited_by: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    job_title: Optional[str] = None


class BusinessMembershipUpdateDTO(BaseModel):
    """DTO for updating business membership."""
    membership_id: uuid.UUID
    role: Optional[BusinessRole] = None
    permissions: Optional[List[str]] = None
    department_id: Optional[uuid.UUID] = None
    job_title: Optional[str] = None
    is_active: Optional[bool] = None


class BusinessMembershipResponseDTO(BaseModel):
    """DTO for business membership response data."""
    id: uuid.UUID
    business_id: uuid.UUID
    user_id: str
    role: BusinessRole
    permissions: List[str]
    joined_date: datetime
    invited_date: Optional[datetime]
    invited_by: Optional[str]
    is_active: bool
    department_id: Optional[uuid.UUID]
    job_title: Optional[str]
    role_display: str


class BusinessInvitationCreateDTO(BaseModel):
    """DTO for creating a new business invitation."""
    business_id: uuid.UUID
    business_name: str
    invited_by: str
    invited_by_name: str
    role: BusinessRole
    invited_email: Optional[str] = None
    invited_phone: Optional[str] = None
    message: Optional[str] = None
    permissions: Optional[List[str]] = None
    department_id: Optional[uuid.UUID] = None
    expiry_days: int = 7


class BusinessInvitationResponseDTO(BaseModel):
    """DTO for business invitation response data."""
    id: uuid.UUID
    business_id: uuid.UUID
    business_name: str
    invited_email: Optional[str]
    invited_phone: Optional[str]
    invited_by: str
    invited_by_name: str
    role: BusinessRole
    permissions: List[str]
    invitation_date: datetime
    expiry_date: datetime
    status: InvitationStatus
    message: Optional[str]
    accepted_date: Optional[datetime]
    declined_date: Optional[datetime]
    role_display: str
    status_display: str
    expiry_summary: str


class BusinessInvitationAcceptDTO(BaseModel):
    """DTO for accepting a business invitation."""
    invitation_id: uuid.UUID
    user_id: str


class BusinessInvitationDeclineDTO(BaseModel):
    """DTO for declining a business invitation."""
    invitation_id: uuid.UUID


class UserBusinessSummaryDTO(BaseModel):
    """DTO for user's business summary."""
    business: BusinessSummaryDTO
    membership: BusinessMembershipResponseDTO
    is_owner: bool
    pending_invitations_count: Optional[int] = None


class BusinessDetailResponseDTO(BaseModel):
    """DTO for detailed business information including team members."""
    business: BusinessResponseDTO
    user_membership: BusinessMembershipResponseDTO
    team_members: List[BusinessMembershipResponseDTO]
    pending_invitations: List[BusinessInvitationResponseDTO]
    total_members: int
    owner_membership: BusinessMembershipResponseDTO


class BusinessOnboardingUpdateDTO(BaseModel):
    """DTO for updating business onboarding status."""
    business_id: uuid.UUID
    selected_features: Optional[List[str]] = None
    primary_goals: Optional[List[str]] = None
    complete_onboarding: bool = False


class BusinessTeamInviteDTO(BaseModel):
    """DTO for inviting team members with bulk support."""
    business_id: uuid.UUID
    invitations: List[BusinessInvitationCreateDTO]


class BusinessStatsDTO(BaseModel):
    """DTO for business statistics."""
    total_businesses: int
    active_businesses: int
    total_memberships: int
    total_invitations: int
    pending_invitations: int
    expired_invitations: int


class BusinessPermissionCheckDTO(BaseModel):
    """DTO for checking business permissions."""
    business_id: uuid.UUID
    user_id: str
    permission: str
    has_permission: bool
    user_role: Optional[BusinessRole] = None 