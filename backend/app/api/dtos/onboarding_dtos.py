"""
Onboarding DTOs

Data Transfer Objects for the new profile-first, activity-driven onboarding flow.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from app.domain.entities.business import CompanySize, MarketFocus, ReferralSource
from app.domain.entities.trade_taxonomy import TradeProfile, TradeActivity, MarketSegment


class OnboardingStep(Enum):
    """Enumeration for onboarding steps."""
    PROFILE_SELECTION = "profile_selection"
    ACTIVITY_SELECTION = "activity_selection" 
    BUSINESS_DETAILS = "business_details"
    SERVICE_TEMPLATES = "service_templates"
    COMPLETION = "completion"


class OnboardingProfileResponse(BaseModel):
    """Enhanced trade profile for onboarding with activity count."""
    slug: str
    name: str
    synonyms: List[str] = Field(default_factory=list)
    segments: MarketSegment
    icon: Optional[str] = None
    description: Optional[str] = None
    activity_count: int = Field(0, description="Number of available activities")
    is_popular: bool = Field(False, description="Popular choice indicator")
    estimated_setup_time: Optional[str] = Field(None, description="Estimated setup time")


class OnboardingActivityResponse(BaseModel):
    """Enhanced trade activity for onboarding with template info."""
    id: str
    slug: str
    name: str
    description: Optional[str] = None
    synonyms: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    is_popular: bool = Field(False, description="Popular choice indicator")
    is_emergency: bool = Field(False, description="Emergency service indicator")
    template_count: int = Field(0, description="Number of available templates")
    estimated_revenue: Optional[str] = Field(None, description="Estimated revenue potential")


class ProfileSelectionRequest(BaseModel):
    """Request for profile selection step."""
    search: Optional[str] = Field(None, description="Search query for profiles")
    segments: Optional[List[MarketSegment]] = Field(None, description="Filter by market segments")
    popular_only: bool = Field(False, description="Show only popular profiles")


class ActivitySelectionRequest(BaseModel):
    """Request for activity selection step."""
    trade_slug: str = Field(..., description="Selected trade profile slug")
    search: Optional[str] = Field(None, description="Search query for activities")
    emergency_only: bool = Field(False, description="Show only emergency activities")
    popular_only: bool = Field(False, description="Show only popular activities")


class BusinessDetailsRequest(BaseModel):
    """Request for business details step."""
    name: str = Field(..., min_length=1, max_length=255, description="Business name")
    description: Optional[str] = Field(None, max_length=1000, description="Business description")
    
    # Contact Information
    phone_number: Optional[str] = Field(None, max_length=20, description="Business phone")
    business_email: Optional[str] = Field(None, max_length=320, description="Business email")
    website: Optional[str] = Field(None, max_length=500, description="Business website")
    
    # Address Information
    address: Optional[str] = Field(None, max_length=200, description="Street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=50, description="State")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal/ZIP code")
    
    # Business Profile
    company_size: CompanySize = Field(default=CompanySize.SMALL, description="Company size")
    market_focus: MarketFocus = Field(default=MarketFocus.BOTH, description="Market focus")
    
    # Business Identity
    business_registration_number: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    business_license: Optional[str] = Field(None, max_length=100)
    insurance_number: Optional[str] = Field(None, max_length=100)
    
    # Onboarding Context
    referral_source: Optional[ReferralSource] = Field(None, description="How they found us")
    primary_goals: List[str] = Field(default_factory=list, description="Primary business goals")


class ServiceTemplateSelectionRequest(BaseModel):
    """Request for service template selection step."""
    activity_slugs: List[str] = Field(..., description="Selected activity slugs")
    template_slugs: List[str] = Field(default_factory=list, description="Selected template slugs")
    auto_adopt_popular: bool = Field(True, description="Auto-adopt popular templates")


class CompleteOnboardingRequest(BaseModel):
    """Request to complete the entire onboarding process."""
    # Profile & Activities
    primary_trade_slug: str = Field(..., description="Selected primary trade")
    selected_activity_slugs: List[str] = Field(..., description="Selected activities")
    
    # Business Details
    business_details: BusinessDetailsRequest
    
    # Service Templates
    template_selections: ServiceTemplateSelectionRequest
    
    # Onboarding Metadata
    onboarding_session_id: Optional[str] = Field(None, description="Session tracking ID")
    completion_time_seconds: Optional[int] = Field(None, description="Time to complete onboarding")


class OnboardingProgressResponse(BaseModel):
    """Response showing onboarding progress."""
    session_id: str = Field(..., description="Onboarding session ID")
    current_step: OnboardingStep = Field(..., description="Current onboarding step")
    completed_steps: List[OnboardingStep] = Field(default_factory=list, description="Completed steps")
    progress_percentage: float = Field(..., ge=0, le=100, description="Progress percentage")
    
    # Step-specific data
    selected_profile: Optional[OnboardingProfileResponse] = None
    selected_activities: List[OnboardingActivityResponse] = Field(default_factory=list)
    business_details: Optional[BusinessDetailsRequest] = None
    
    # Validation
    can_proceed: bool = Field(..., description="Can proceed to next step")
    validation_errors: List[str] = Field(default_factory=list, description="Current validation errors")
    
    # Recommendations
    recommended_next_action: Optional[str] = Field(None, description="Recommended next action")
    estimated_time_remaining: Optional[str] = Field(None, description="Estimated time to completion")


class OnboardingValidationResponse(BaseModel):
    """Response for validation requests."""
    is_valid: bool = Field(..., description="Whether the input is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class OnboardingCompletionResponse(BaseModel):
    """Response after successful onboarding completion."""
    business_id: str = Field(..., description="Created business ID")
    business_name: str = Field(..., description="Business name")
    primary_trade: OnboardingProfileResponse = Field(..., description="Primary trade profile")
    selected_activities: List[OnboardingActivityResponse] = Field(..., description="Selected activities")
    
    # Adoption Results
    adopted_templates: List[str] = Field(default_factory=list, description="Auto-adopted template slugs")
    created_services: int = Field(0, description="Number of services created")
    
    # Next Steps
    recommended_next_steps: List[str] = Field(default_factory=list, description="Recommended next actions")
    onboarding_completion_time: Optional[str] = Field(None, description="Total onboarding time")
    
    # Success Metrics
    setup_completion_percentage: float = Field(..., description="Setup completion percentage")
    estimated_revenue_potential: Optional[str] = Field(None, description="Estimated revenue potential")


class OnboardingStatsResponse(BaseModel):
    """Response with onboarding statistics and insights."""
    total_profiles: int = Field(..., description="Total available profiles")
    popular_profiles: List[OnboardingProfileResponse] = Field(..., description="Most popular profiles")
    
    # Activity insights
    total_activities: int = Field(..., description="Total available activities")
    emergency_activities: int = Field(..., description="Emergency activities count")
    
    # Template insights
    total_templates: int = Field(..., description="Total available templates")
    popular_templates: int = Field(..., description="Popular templates count")
    
    # Completion insights
    average_completion_time: Optional[str] = Field(None, description="Average onboarding time")
    completion_rate: Optional[float] = Field(None, description="Onboarding completion rate")


# Response Collections
class OnboardingProfileListResponse(BaseModel):
    """Response for profile listing."""
    profiles: List[OnboardingProfileResponse] = Field(..., description="Available profiles")
    total_count: int = Field(..., description="Total profiles count")
    popular_count: int = Field(0, description="Popular profiles count")
    stats: Optional[OnboardingStatsResponse] = None


class OnboardingActivityListResponse(BaseModel):
    """Response for activity listing."""
    activities: List[OnboardingActivityResponse] = Field(..., description="Available activities")
    total_count: int = Field(..., description="Total activities count")
    emergency_count: int = Field(0, description="Emergency activities count")
    trade_profile: Optional[OnboardingProfileResponse] = None


# Session Management
class OnboardingSessionRequest(BaseModel):
    """Request to start a new onboarding session."""
    user_agent: Optional[str] = Field(None, description="User agent for analytics")
    referral_source: Optional[ReferralSource] = Field(None, description="How they found us")
    utm_parameters: Optional[Dict[str, str]] = Field(None, description="UTM tracking parameters")


class OnboardingSessionResponse(BaseModel):
    """Response when starting an onboarding session."""
    session_id: str = Field(..., description="Unique session ID")
    expires_at: str = Field(..., description="Session expiration time")
    current_step: OnboardingStep = Field(default=OnboardingStep.PROFILE_SELECTION)
    
    # Initial data
    available_profiles_count: int = Field(..., description="Number of available profiles")
    estimated_completion_time: str = Field(..., description="Estimated completion time")
    
    # Tracking
    analytics_enabled: bool = Field(True, description="Whether analytics are enabled")
    session_token: Optional[str] = Field(None, description="Session token for API calls")
