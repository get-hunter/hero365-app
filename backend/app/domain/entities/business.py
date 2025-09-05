"""
Business Domain Entity

Represents a business in the domain with associated business rules and behaviors.
"""

import uuid
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator

from ..exceptions.domain_exceptions import DomainValidationError


class CompanySize(Enum):
    """Enumeration for company sizes."""
    JUST_ME = "just_me"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class MarketFocus(Enum):
    """Enumeration for market focus - which customer segments the business serves."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial" 
    BOTH = "both"


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


class Business(BaseModel):
    """
    Business entity representing the core business concept.
    
    This entity contains business logic and rules that apply to businesses
    regardless of how they are stored or presented.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = Field(..., min_length=1, max_length=255)
    primary_trade_slug: str = Field(..., description="Primary trade profile slug")
    company_size: CompanySize
    
    # Business Profile
    description: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    phone_country_code: Optional[str] = Field(None, max_length=5)
    phone_display: Optional[str] = Field(None, max_length=25)
    years_in_business: Optional[int] = Field(None, ge=0)
    emergency_available: Optional[bool] = False
    business_address: Optional[str] = None
    
    # Address components (for SEO and local business features)
    address: Optional[str] = Field(None, max_length=200, description="Street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=50, description="State")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal/ZIP code")
    
    website: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    business_email: Optional[str] = Field(None, max_length=320)
    
    # Trade Information (clean profile-activity model)
    market_focus: MarketFocus = Field(default=MarketFocus.BOTH, description="Which customer segments the business serves")
    selected_activity_slugs: List[str] = Field(default_factory=list, description="Selected trade activities for this business")
    
    # Business Identity
    business_registration_number: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    business_license: Optional[str] = Field(None, max_length=100)
    insurance_number: Optional[str] = Field(None, max_length=100)
    
    # Onboarding & Setup
    selected_features: List[str] = Field(default_factory=list)
    primary_goals: List[str] = Field(default_factory=list)
    referral_source: Optional[ReferralSource] = None
    onboarding_completed: bool = False
    onboarding_completed_date: Optional[datetime] = None
    
    # Business Settings
    timezone: Optional[str] = Field(None, max_length=100)
    currency: str = Field(default="USD", max_length=3)
    business_hours: Optional[dict] = None
    is_active: bool = True
    
    # Team Management
    max_team_members: Optional[int] = Field(None, ge=1)
    
    # Subscription & Features
    subscription_tier: Optional[str] = Field(None, max_length=50)
    enabled_features: List[str] = Field(default_factory=list)
    
    # Metadata
    created_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_modified: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Business name cannot be empty")
        return v.strip()
    
    @field_validator('primary_trade_slug')
    @classmethod
    def validate_primary_trade_slug(cls, v):
        if not v or not v.strip():
            raise ValueError("Primary trade slug cannot be empty")
        return v.strip()
    
    @field_validator('website')
    @classmethod
    def validate_website(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError("Invalid website URL format")
        return v
    
    @model_validator(mode='after')
    def validate_business_rules(self):
        """Validate complex business rules that require multiple fields."""
        
        # Primary trade slug is required
        if not self.primary_trade_slug:
            raise ValueError("Primary trade slug is required")
        
        # At least one activity should be selected for a complete business profile
        # (This is not enforced at entity level but can be checked during onboarding)
        
        return self
    
    def update_profile(self, **kwargs) -> 'Business':
        """
        Update business profile information.
        
        Args:
            **kwargs: Profile fields to update
            
        Returns:
            Business: Updated business instance
            
        Raises:
            ValueError: If the update violates business rules
        """
        # Update last modified timestamp
        kwargs['last_modified'] = datetime.utcnow()
        
        # Create new instance with updated values (Pydantic validation happens automatically)
        return self.copy(update=kwargs)
    
    def complete_onboarding(self) -> 'Business':
        """Mark business onboarding as completed."""
        if self.onboarding_completed:
            raise ValueError("Onboarding already completed")
        
        return self.copy(update={
            'onboarding_completed': True,
            'onboarding_completed_date': datetime.utcnow(),
            'last_modified': datetime.utcnow()
        })
    
    def activate(self) -> 'Business':
        """Activate the business."""
        return self.copy(update={
            'is_active': True,
            'last_modified': datetime.utcnow()
        })
    
    def deactivate(self) -> 'Business':
        """Deactivate the business."""
        return self.copy(update={
            'is_active': False,
            'last_modified': datetime.utcnow()
        })
    
    def add_feature(self, feature: str) -> 'Business':
        """Add a feature to the business."""
        if feature not in self.enabled_features:
            new_features = self.enabled_features.copy()
            new_features.append(feature)
            return self.copy(update={
                'enabled_features': new_features,
                'last_modified': datetime.utcnow()
            })
        return self
    
    def remove_feature(self, feature: str) -> 'Business':
        """Remove a feature from the business."""
        if feature in self.enabled_features:
            new_features = self.enabled_features.copy()
            new_features.remove(feature)
            return self.copy(update={
                'enabled_features': new_features,
                'last_modified': datetime.utcnow()
            })
        return self
    
    def has_feature(self, feature: str) -> bool:
        """Check if business has a specific feature enabled."""
        return feature in self.enabled_features
    
    def add_activity(self, activity_slug: str) -> 'Business':
        """Add an activity to the business."""
        if activity_slug not in self.selected_activity_slugs:
            new_activities = self.selected_activity_slugs.copy()
            new_activities.append(activity_slug)
            return self.model_copy(update={
                'selected_activity_slugs': new_activities,
                'last_modified': datetime.utcnow()
            })
        return self
    
    def remove_activity(self, activity_slug: str) -> 'Business':
        """Remove an activity from the business."""
        if activity_slug in self.selected_activity_slugs:
            new_activities = self.selected_activity_slugs.copy()
            new_activities.remove(activity_slug)
            return self.model_copy(update={
                'selected_activity_slugs': new_activities,
                'last_modified': datetime.utcnow()
            })
        return self
    
    def get_all_activities(self) -> List[str]:
        """Get all selected activity slugs for the business."""
        return self.selected_activity_slugs.copy()
    
    def get_primary_trade_slug(self) -> str:
        """Get the primary trade slug for SEO and template selection."""
        return self.primary_trade_slug
    
    def is_multi_activity_business(self) -> bool:
        """Check if business offers multiple activities."""
        return len(self.selected_activity_slugs) > 1
    
    def get_activity_count(self) -> int:
        """Get total number of activities offered."""
        return len(self.selected_activity_slugs)
    
    def has_activity(self, activity_slug: str) -> bool:
        """Check if business offers a specific activity."""
        return activity_slug in self.selected_activity_slugs
    
    # Note: Service area management moved to dedicated ServiceAreasService
    # Use ServiceAreasService.bulk_upsert_service_areas() and related methods
    
    def get_seo_keywords(self) -> List[str]:
        """Generate SEO keywords based on primary trade and business location."""
        keywords = []
        
        # Add primary trade-based keywords
        primary_trade = self.primary_trade_slug.replace('-', ' ')
        keywords.append(primary_trade)
        keywords.append(f"{primary_trade} services")
        keywords.append(f"{primary_trade} contractor")
        
        # Add location-based keywords using business city/state
        # Note: For service areas, use ServiceAreasService to get areas and generate keywords separately
        if self.city:
            keywords.append(f"{primary_trade} {self.city}")
            keywords.append(f"{primary_trade} services {self.city}")
        
        # Add business name combinations
        if self.name:
            keywords.append(f"{self.name} {primary_trade}")
        
        return list(set(keywords))  # Remove duplicates
    
    def get_website_template_category(self) -> str:
        """Determine the best website template category for this business."""
        if self.is_multi_activity_business():
            # For multi-activity businesses, use the primary trade
            return self.primary_trade_slug
        else:
            # Single activity business
            return self.primary_trade_slug
    
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
        activities = self.get_all_activities()
        return (f"Business(id={self.id}, name='{self.name}', primary_trade='{self.primary_trade_slug}', "
                f"activities={activities}, is_active={self.is_active})")
    
    # Market focus methods
    
    def serves_residential_market(self) -> bool:
        """Check if business serves residential customers."""
        return self.market_focus in [MarketFocus.RESIDENTIAL, MarketFocus.BOTH]
    
    def serves_commercial_market(self) -> bool:
        """Check if business serves commercial customers."""
        return self.market_focus in [MarketFocus.COMMERCIAL, MarketFocus.BOTH]
    
    def set_market_focus(self, focus: MarketFocus) -> 'Business':
        """Set the market focus for the business."""
        return self.model_copy(update={'market_focus': focus})
    
    @classmethod
    def create_with_activities(
        cls,
        name: str,
        primary_trade_slug: str,
        market_focus: MarketFocus,
        selected_activity_slugs: List[str] = None,
        **kwargs
    ) -> 'Business':
        """
        Create a new business with selected activities.
        This is the recommended way to create businesses.
        """
        from datetime import datetime
        
        # Set default values for required fields
        defaults = {
            'id': uuid.uuid4(),
            'name': name,
            'primary_trade_slug': primary_trade_slug,
            'market_focus': market_focus,
            'selected_activity_slugs': selected_activity_slugs or [],
            'company_size': CompanySize.SMALL,  # Default company size
            'created_date': datetime.utcnow(),
            'last_modified': datetime.utcnow()
        }
        
        # Override with any provided kwargs
        defaults.update(kwargs)
        
        # Create business
        return cls(**defaults) 