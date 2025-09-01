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


class TradeCategory(Enum):
    """Enumeration for trade categories."""
    COMMERCIAL = "commercial"
    RESIDENTIAL = "residential"


class MarketFocus(Enum):
    """Enumeration for market focus - which customer segments the business serves."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial" 
    BOTH = "both"


class CommercialTrade(Enum):
    """Enumeration for commercial trades."""
    MECHANICAL = "mechanical"
    REFRIGERATION = "refrigeration"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    SECURITY_SYSTEMS = "security_systems"
    LANDSCAPING = "landscaping"
    ROOFING = "roofing"
    KITCHEN_EQUIPMENT = "kitchen_equipment"
    WATER_TREATMENT = "water_treatment"
    POOL_SPA = "pool_spa"


class ResidentialTrade(Enum):
    """Enumeration for residential trades."""
    HVAC = "hvac"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    CHIMNEY = "chimney"
    ROOFING = "roofing"
    GARAGE_DOOR = "garage_door"
    SEPTIC = "septic"
    PEST_CONTROL = "pest_control"
    IRRIGATION = "irrigation"
    PAINTING = "painting"


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
    industry: str = Field(..., min_length=1, max_length=100)
    company_size: CompanySize
    # owner_id removed - use business_memberships with role='owner' instead
    
    # Business Profile
    custom_industry: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    business_address: Optional[str] = None
    
    # Address components (for SEO and local business features)
    address: Optional[str] = Field(None, max_length=200, description="Street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=50, description="State")
    zip_code: Optional[str] = Field(None, max_length=20, description="ZIP/Postal code")
    
    website: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    business_email: Optional[str] = Field(None, max_length=320)
    
    # Trade Information
    trade_category: Optional[TradeCategory] = None
    market_focus: MarketFocus = Field(default=MarketFocus.BOTH, description="Which customer segments the business serves")
    commercial_trades: List[CommercialTrade] = Field(default_factory=list)
    residential_trades: List[ResidentialTrade] = Field(default_factory=list)
    # New service-based approach (will replace trades eventually)
    residential_services: List[ResidentialTrade] = Field(default_factory=list, description="Residential services offered")
    commercial_services: List[CommercialTrade] = Field(default_factory=list, description="Commercial services offered")
    service_areas: List[str] = Field(default_factory=list)  # Geographic areas served
    
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
    
    @field_validator('industry')
    @classmethod
    def validate_industry(cls, v):
        if not v or not v.strip():
            raise ValueError("Industry cannot be empty")
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
        
        # Custom industry validation
        if self.industry and self.industry.lower() == 'custom' and not self.custom_industry:
            raise ValueError("Custom industry must be specified when industry is 'custom'")
        
        # At least one trade/service must be specified
        if not (self.commercial_trades or self.residential_trades or 
                self.commercial_services or self.residential_services or 
                self.industry):
            raise ValueError("Business must have at least one trade or service specified")
        
        # Trade category consistency validation
        if self.trade_category == TradeCategory.COMMERCIAL:
            if self.residential_trades and not self.commercial_trades:
                raise ValueError("Commercial-only businesses cannot have residential trades without commercial trades")
        
        if self.trade_category == TradeCategory.RESIDENTIAL:
            if self.commercial_trades and not self.residential_trades:
                raise ValueError("Residential-only businesses cannot have commercial trades without residential trades")
        
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
    
    def add_trade(self, trade) -> 'Business':
        """Add a trade to the business based on trade category."""
        if isinstance(trade, CommercialTrade) and trade not in self.commercial_trades:
            new_commercial_trades = self.commercial_trades.copy()
            new_commercial_trades.append(trade)
            return self.copy(update={
                'commercial_trades': new_commercial_trades,
                'last_modified': datetime.utcnow()
            })
        elif isinstance(trade, ResidentialTrade) and trade not in self.residential_trades:
            new_residential_trades = self.residential_trades.copy()
            new_residential_trades.append(trade)
            return self.copy(update={
                'residential_trades': new_residential_trades,
                'last_modified': datetime.utcnow()
            })
        return self
    
    def remove_trade(self, trade) -> 'Business':
        """Remove a trade from the business."""
        if isinstance(trade, CommercialTrade) and trade in self.commercial_trades:
            new_commercial_trades = self.commercial_trades.copy()
            new_commercial_trades.remove(trade)
            return self.copy(update={
                'commercial_trades': new_commercial_trades,
                'last_modified': datetime.utcnow()
            })
        elif isinstance(trade, ResidentialTrade) and trade in self.residential_trades:
            new_residential_trades = self.residential_trades.copy()
            new_residential_trades.remove(trade)
            return self.copy(update={
                'residential_trades': new_residential_trades,
                'last_modified': datetime.utcnow()
            })
        return self
    
    def get_all_trades(self) -> List[str]:
        """Get all trades as string values for the business."""
        trades = []
        if self.commercial_trades:
            # Handle both enum objects and string values (due to use_enum_values=True)
            trades.extend([trade.value if hasattr(trade, 'value') else trade for trade in self.commercial_trades])
        if self.residential_trades:
            # Handle both enum objects and string values (due to use_enum_values=True)
            trades.extend([trade.value if hasattr(trade, 'value') else trade for trade in self.residential_trades])
        return trades
    
    def get_primary_trade(self) -> Optional[str]:
        """Get the primary trade for SEO and template selection."""
        all_trades = self.get_all_trades()
        return all_trades[0] if all_trades else None
    
    def is_multi_trade_business(self) -> bool:
        """Check if business offers multiple trades."""
        return len(self.get_all_trades()) > 1
    
    def get_trade_count(self) -> int:
        """Get total number of trades offered."""
        return len(self.get_all_trades())
    
    def has_trade(self, trade_name: str) -> bool:
        """Check if business offers a specific trade."""
        return trade_name.lower() in [trade.lower() for trade in self.get_all_trades()]
    
    def get_trades_for_category(self, category: TradeCategory) -> List[str]:
        """Get trades for a specific category."""
        if category == TradeCategory.COMMERCIAL:
            return [trade.value for trade in self.commercial_trades] if self.commercial_trades else []
        elif category == TradeCategory.RESIDENTIAL:
            return [trade.value for trade in self.residential_trades] if self.residential_trades else []
        return []
    
    def can_serve_both_markets(self) -> bool:
        """Check if business can serve both commercial and residential markets."""
        # This would be true for trades like plumbing, electrical that exist in both categories
        commercial_trades = set(self.get_trades_for_category(TradeCategory.COMMERCIAL))
        residential_trades = set(self.get_trades_for_category(TradeCategory.RESIDENTIAL))
        
        # Check for overlapping trade types (plumbing, electrical, roofing exist in both)
        overlapping_trades = {'plumbing', 'electrical', 'roofing'}
        return bool(commercial_trades.intersection(overlapping_trades) and 
                   residential_trades.intersection(overlapping_trades))
    
    def add_service_area(self, area: str) -> 'Business':
        """Add a service area to the business."""
        if area and area not in self.service_areas:
            new_service_areas = self.service_areas.copy()
            new_service_areas.append(area)
            return self.copy(update={
                'service_areas': new_service_areas,
                'last_modified': datetime.utcnow()
            })
        return self
    
    def remove_service_area(self, area: str) -> 'Business':
        """Remove a service area from the business."""
        if area in self.service_areas:
            new_service_areas = self.service_areas.copy()
            new_service_areas.remove(area)
            return self.copy(update={
                'service_areas': new_service_areas,
                'last_modified': datetime.utcnow()
            })
        return self
    
    def get_seo_keywords(self) -> List[str]:
        """Generate SEO keywords based on trades and service areas."""
        keywords = []
        trades = self.get_all_trades()
        
        # Add trade-based keywords
        for trade in trades:
            keywords.append(trade.replace('_', ' '))
            keywords.append(f"{trade.replace('_', ' ')} services")
            keywords.append(f"{trade.replace('_', ' ')} contractor")
        
        # Add location-based keywords
        if self.service_areas:
            for area in self.service_areas:
                for trade in trades:
                    keywords.append(f"{trade.replace('_', ' ')} {area}")
                    keywords.append(f"{trade.replace('_', ' ')} services {area}")
        
        # Add business name combinations
        if self.name:
            for trade in trades:
                keywords.append(f"{self.name} {trade.replace('_', ' ')}")
        
        return list(set(keywords))  # Remove duplicates
    
    def get_website_template_category(self) -> str:
        """Determine the best website template category for this business."""
        if self.is_multi_trade_business():
            # For multi-trade businesses, use the primary trade or 'multi-service'
            primary_trade = self.get_primary_trade()
            if primary_trade:
                return primary_trade
            return "multi-service"
        else:
            # Single trade business
            return self.get_primary_trade() or "general-contractor"
    
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
        trades = self.get_all_trades()
        return (f"Business(id={self.id}, name='{self.name}', industry='{self.industry}', "
                f"trades={trades}, is_active={self.is_active})")
    
    # New methods for market focus and service-based approach
    
    def get_all_services(self) -> List[str]:
        """Get all services as string values (new service-based approach)."""
        services = []
        if self.residential_services:
            services.extend([service.value if hasattr(service, 'value') else service for service in self.residential_services])
        if self.commercial_services:
            services.extend([service.value if hasattr(service, 'value') else service for service in self.commercial_services])
        return services
    
    def get_residential_services(self) -> List[str]:
        """Get residential services as string values."""
        if not self.residential_services:
            return []
        return [service.value if hasattr(service, 'value') else service for service in self.residential_services]
    
    def get_commercial_services(self) -> List[str]:
        """Get commercial services as string values."""
        if not self.commercial_services:
            return []
        return [service.value if hasattr(service, 'value') else service for service in self.commercial_services]
    
    def serves_residential_market(self) -> bool:
        """Check if business serves residential customers."""
        return self.market_focus in [MarketFocus.RESIDENTIAL, MarketFocus.BOTH]
    
    def serves_commercial_market(self) -> bool:
        """Check if business serves commercial customers."""
        return self.market_focus in [MarketFocus.COMMERCIAL, MarketFocus.BOTH]
    
    def has_service(self, service_name: str) -> bool:
        """Check if business offers a specific service."""
        all_services = self.get_all_services()
        return service_name.lower() in [service.lower() for service in all_services]
    
    def add_residential_service(self, service: ResidentialTrade) -> 'Business':
        """Add a residential service to the business."""
        if service not in self.residential_services:
            return self.model_copy(update={
                'residential_services': self.residential_services + [service]
            })
        return self
    
    def add_commercial_service(self, service: CommercialTrade) -> 'Business':
        """Add a commercial service to the business."""
        if service not in self.commercial_services:
            return self.model_copy(update={
                'commercial_services': self.commercial_services + [service]
            })
        return self
    
    def remove_residential_service(self, service: ResidentialTrade) -> 'Business':
        """Remove a residential service from the business."""
        if service in self.residential_services:
            new_services = [s for s in self.residential_services if s != service]
            return self.model_copy(update={'residential_services': new_services})
        return self
    
    def remove_commercial_service(self, service: CommercialTrade) -> 'Business':
        """Remove a commercial service from the business."""
        if service in self.commercial_services:
            new_services = [s for s in self.commercial_services if s != service]
            return self.model_copy(update={'commercial_services': new_services})
        return self
    
    def set_market_focus(self, focus: MarketFocus) -> 'Business':
        """Set the market focus for the business."""
        return self.model_copy(update={'market_focus': focus})
    
    def auto_assign_default_services(self) -> 'Business':
        """
        Auto-assign default services based on primary_trade and secondary_trades.
        This provides a better onboarding experience - users get pre-selected services
        and can unselect what they don't offer.
        """
        from ..services.default_services_mapping import DefaultServicesMapping
        
        # Get all existing trades (combine commercial and residential)
        all_trades = []
        if self.industry:
            all_trades.append(self.industry)
        
        # Add existing trades as secondary trades
        for trade in self.commercial_trades:
            if trade.value not in all_trades:
                all_trades.append(trade.value)
        for trade in self.residential_trades:
            if trade.value not in all_trades:
                all_trades.append(trade.value)
        
        # Get default services for all trades
        default_services = DefaultServicesMapping.get_default_services_for_business(
            primary_trade=self.industry or "",
            secondary_trades=all_trades[1:] if len(all_trades) > 1 else [],  # Skip primary trade
            market_focus=self.market_focus
        )
        
        # Auto-assign based on primary and secondary trades
        residential_services = []
        commercial_services = []
        
        # Map primary trade to services
        if self.industry:
            if self.market_focus in [MarketFocus.RESIDENTIAL, MarketFocus.BOTH]:
                try:
                    residential_trade = ResidentialTrade(self.industry.lower())
                    residential_services.append(residential_trade)
                except ValueError:
                    pass
            
            if self.market_focus in [MarketFocus.COMMERCIAL, MarketFocus.BOTH]:
                try:
                    commercial_trade = CommercialTrade(self.industry.lower())
                    commercial_services.append(commercial_trade)
                except ValueError:
                    pass
        
        # Map existing trades to services (skip primary trade since it's already handled)
        existing_trades = all_trades[1:] if len(all_trades) > 1 else []
        for trade in existing_trades:
                if self.market_focus in [MarketFocus.RESIDENTIAL, MarketFocus.BOTH]:
                    try:
                        residential_trade = ResidentialTrade(trade.lower())
                        if residential_trade not in residential_services:
                            residential_services.append(residential_trade)
                    except ValueError:
                        pass
                
                if self.market_focus in [MarketFocus.COMMERCIAL, MarketFocus.BOTH]:
                    try:
                        commercial_trade = CommercialTrade(trade.lower())
                        if commercial_trade not in commercial_services:
                            commercial_services.append(commercial_trade)
                    except ValueError:
                        pass
        
        return self.model_copy(update={
            'residential_services': residential_services,
            'commercial_services': commercial_services
        })
    
    @classmethod
    def create_with_default_services(
        cls,
        owner_id: uuid.UUID,
        name: str,
        primary_trade: str,
        market_focus: MarketFocus,
        **kwargs
    ) -> 'Business':
        """
        Create a new business with auto-assigned default services.
        This is the recommended way to create businesses for better UX.
        """
        from datetime import datetime
        
        # Set default values for required fields
        defaults = {
            'id': uuid.uuid4(),
            'owner_id': owner_id,
            'name': name,
            'industry': primary_trade,
            'market_focus': market_focus,
            'residential_services': [],
            'commercial_services': [],
            'company_size': CompanySize.SMALL,  # Default company size
            'created_date': datetime.utcnow(),
            'last_modified': datetime.utcnow()
        }
        
        # Override with any provided kwargs
        defaults.update(kwargs)
        
        # Create business with basic info
        business = cls(**defaults)
        
        # Auto-assign default services
        return business.auto_assign_default_services() 