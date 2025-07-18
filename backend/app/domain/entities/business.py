"""
Business Domain Entity

Represents a business in the domain with associated business rules and behaviors.
"""

import uuid
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from enum import Enum

from ..exceptions.domain_exceptions import DomainValidationError


class CompanySize(Enum):
    """Enumeration for company sizes."""
    JUST_ME = "just_me"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class BusinessType(Enum):
    """Enumeration for business types."""
    CONTRACTOR = "contractor"
    CONSULTING = "consulting"
    SERVICES = "services"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    CONSTRUCTION = "construction"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    HVAC = "hvac"
    LANDSCAPING = "landscaping"
    CLEANING = "cleaning"
    HANDYMAN = "handyman"
    OTHER = "other"


class ReferralSource(Enum):
    """Enumeration for referral sources."""
    TIKTOK = "tiktok"
    TV = "tv"
    ONLINE_AD = "online_ad"
    WEB_SEARCH = "web_search"
    PODCAST_RADIO = "podcast_radio"
    REDDIT = "reddit"
    REVIEW_SITES = "review_sites"
    YOUTUBE = "youtube"
    FACEBOOK_INSTAGRAM = "facebook_instagram"
    REFERRAL = "referral"
    OTHER = "other"


@dataclass
class Business:
    """
    Business entity representing the core business concept.
    
    This entity contains business logic and rules that apply to businesses
    regardless of how they are stored or presented.
    """
    
    id: uuid.UUID
    name: str
    industry: str
    business_type: BusinessType
    company_size: CompanySize
    owner_id: str
    
    # Business Profile
    custom_industry: Optional[str] = None
    description: Optional[str] = None
    phone_number: Optional[str] = None
    business_address: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    business_email: Optional[str] = None
    
    # Business Identity
    business_registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    business_license: Optional[str] = None
    insurance_number: Optional[str] = None
    
    # Onboarding & Setup
    selected_features: List[str] = None
    primary_goals: List[str] = None
    referral_source: Optional[ReferralSource] = None
    onboarding_completed: bool = False
    onboarding_completed_date: Optional[datetime] = None
    
    # Business Settings
    timezone: Optional[str] = None
    currency: str = "USD"
    business_hours: Optional[dict] = None
    is_active: bool = True
    
    # Team Management
    max_team_members: Optional[int] = None
    
    # Subscription & Features
    subscription_tier: Optional[str] = None
    enabled_features: List[str] = None
    
    # Metadata
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values and validate business rules."""
        if self.selected_features is None:
            self.selected_features = []
        if self.primary_goals is None:
            self.primary_goals = []
        if self.enabled_features is None:
            self.enabled_features = []
        self._validate_business_rules()
    
    def _validate_business_rules(self) -> None:
        """Validate core business rules."""
        if not self.name or len(self.name.strip()) == 0:
            raise DomainValidationError("Business name cannot be empty")
        
        if not self.industry or len(self.industry.strip()) == 0:
            raise DomainValidationError("Industry cannot be empty")
        
        if not self.owner_id:
            raise DomainValidationError("Business must have an owner")
        
        if self.industry.lower() == "custom" and not self.custom_industry:
            raise DomainValidationError("Custom industry must be specified when industry is 'custom'")
        
        if self.website and not self._is_valid_url(self.website):
            raise DomainValidationError("Invalid website URL format")
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation."""
        return url.startswith(('http://', 'https://'))
    
    def update_profile(self, **kwargs) -> None:
        """
        Update business profile information.
        
        Args:
            **kwargs: Profile fields to update
            
        Raises:
            DomainValidationError: If the update violates business rules
        """
        # Store original values for rollback
        original_values = {}
        
        try:
            for field, value in kwargs.items():
                if hasattr(self, field):
                    original_values[field] = getattr(self, field)
                    setattr(self, field, value)
            
            # Update last modified timestamp
            self.last_modified = datetime.utcnow()
            
            # Validate after changes
            self._validate_business_rules()
            
        except DomainValidationError:
            # Rollback changes
            for field, value in original_values.items():
                setattr(self, field, value)
            raise
    
    def complete_onboarding(self) -> None:
        """Mark business onboarding as completed."""
        if self.onboarding_completed:
            raise DomainValidationError("Onboarding already completed")
        
        self.onboarding_completed = True
        self.onboarding_completed_date = datetime.utcnow()
        self.last_modified = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate the business."""
        self.is_active = True
        self.last_modified = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate the business."""
        self.is_active = False
        self.last_modified = datetime.utcnow()
    
    def add_feature(self, feature: str) -> None:
        """Add a feature to the business."""
        if feature not in self.enabled_features:
            self.enabled_features.append(feature)
            self.last_modified = datetime.utcnow()
    
    def remove_feature(self, feature: str) -> None:
        """Remove a feature from the business."""
        if feature in self.enabled_features:
            self.enabled_features.remove(feature)
            self.last_modified = datetime.utcnow()
    
    def has_feature(self, feature: str) -> bool:
        """Check if business has a specific feature enabled."""
        return feature in self.enabled_features
    
    def can_add_team_member(self) -> bool:
        """Check if business can add more team members."""
        if self.max_team_members is None:
            return True
        # This would need to check current team member count
        # Implementation depends on team member repository
        return True
    
    def get_display_name(self) -> str:
        """Get the display name for the business."""
        return self.name
    
    def __str__(self) -> str:
        return f"Business({self.name})"
    
    def __repr__(self) -> str:
        return (f"Business(id={self.id}, name='{self.name}', industry='{self.industry}', "
                f"business_type='{self.business_type}', owner_id='{self.owner_id}', is_active={self.is_active})") 