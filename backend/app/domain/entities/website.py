"""
Website Domain Entities

Pydantic models for the SEO Website Builder system, including website templates,
business websites, domain registrations, and SEO tracking.
"""

import uuid
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, Dict, List, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, validator, model_validator

# from .business import TradeCategory, CommercialTrade, ResidentialTrade  # TODO: Define trade entities

class TradeCategory(str, Enum):
    """Trade category classification."""
    COMMERCIAL = "commercial"
    RESIDENTIAL = "residential"
    BOTH = "both"


class WebsiteStatus(str, Enum):
    """Website build and deployment status."""
    DRAFT = "draft"
    BUILDING = "building"
    BUILT = "built"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    ERROR = "error"


class DomainStatus(str, Enum):
    """Domain registration status."""
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    TRANSFERRED = "transferred"
    CANCELLED = "cancelled"
    FAILED = "failed"


class BuildJobType(str, Enum):
    """Website build job types."""
    INITIAL_BUILD = "initial_build"
    CONTENT_UPDATE = "content_update"
    THEME_UPDATE = "theme_update"
    DEPLOYMENT = "deployment"
    SEO_OPTIMIZATION = "seo_optimization"


class BuildJobStatus(str, Enum):
    """Build job execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CompetitionLevel(str, Enum):
    """SEO keyword competition levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class SyncStatus(str, Enum):
    """Google Business Profile sync status."""
    PENDING = "pending"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


# =====================================
# WEBSITE TEMPLATE ENTITIES
# =====================================

class WebsiteTemplate(BaseModel):
    """
    Website template entity for trade-specific site generation.
    
    Templates are designed around specific trades and can support
    single-trade or multi-trade businesses.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    
    # Trade classification
    trade_type: str = Field(..., description="Specific trade from CommercialTrade or ResidentialTrade")
    trade_category: TradeCategory = Field(..., description="COMMERCIAL, RESIDENTIAL, or BOTH")
    
    # Template metadata
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    preview_url: Optional[HttpUrl] = None
    
    # Template configuration
    structure: Dict[str, Any] = Field(default_factory=dict, description="Page hierarchy and components")
    default_content: Dict[str, Any] = Field(default_factory=dict, description="AI prompts and seed content")
    seo_config: Dict[str, Any] = Field(default_factory=dict, description="Meta tags and schema templates")
    
    # Multi-trade support
    is_multi_trade: bool = Field(default=False, description="Supports multi-trade businesses")
    supported_trades: List[str] = Field(default_factory=list, description="Supported trade combinations")
    
    # Template status
    is_active: bool = Field(default=True)
    is_system_template: bool = Field(default=False)
    
    # Usage tracking
    usage_count: int = Field(default=0, ge=0)
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('trade_category')
    def validate_trade_category(cls, v):
        """Validate trade category is valid."""
        if v not in [TradeCategory.COMMERCIAL, TradeCategory.RESIDENTIAL]:
            raise ValueError(f"Invalid trade category: {v}")
        return v
    
    @validator('supported_trades')
    def validate_supported_trades(cls, v, values):
        """Validate supported trades when is_multi_trade is True."""
        if values.get('is_multi_trade') and not v:
            raise ValueError("Multi-trade templates must specify supported_trades")
        return v
    
    def supports_business(self, business: 'Business') -> bool:
        """Check if template supports a business's trades."""
        business_trades = business.get_all_trades()
        
        if self.is_multi_trade:
            return any(trade in self.supported_trades for trade in business_trades)
        
        return self.trade_type in business_trades
    
    def get_seo_keywords(self, business_name: str, location: str) -> List[str]:
        """Generate SEO keywords for this template and business."""
        keywords = []
        
        # Base trade keywords
        keywords.extend([
            f"{self.trade_type} services",
            f"{self.trade_type} contractor",
            f"professional {self.trade_type}"
        ])
        
        # Location-based keywords
        if location:
            keywords.extend([
                f"{self.trade_type} {location}",
                f"{self.trade_type} services {location}",
                f"{location} {self.trade_type} contractor"
            ])
        
        # Business name keywords
        if business_name:
            keywords.extend([
                f"{business_name} {self.trade_type}",
                f"{business_name} services"
            ])
        
        return keywords[:20]  # Return top 20 keywords


# =====================================
# BUSINESS WEBSITE ENTITIES
# =====================================

class CoreWebVitals(BaseModel):
    """Core Web Vitals performance metrics."""
    
    lcp: Optional[float] = Field(None, description="Largest Contentful Paint (seconds)")
    fid: Optional[float] = Field(None, description="First Input Delay (milliseconds)")
    cls: Optional[float] = Field(None, description="Cumulative Layout Shift")
    fcp: Optional[float] = Field(None, description="First Contentful Paint (seconds)")
    ttfb: Optional[float] = Field(None, description="Time to First Byte (milliseconds)")
    
    @validator('lcp')
    def validate_lcp(cls, v):
        """LCP should be under 2.5 seconds for good performance."""
        if v is not None and v < 0:
            raise ValueError("LCP cannot be negative")
        return v
    
    @validator('fid')
    def validate_fid(cls, v):
        """FID should be under 100ms for good performance."""
        if v is not None and v < 0:
            raise ValueError("FID cannot be negative")
        return v
    
    @validator('cls')
    def validate_cls(cls, v):
        """CLS should be under 0.1 for good performance."""
        if v is not None and v < 0:
            raise ValueError("CLS cannot be negative")
        return v


class DeploymentConfig(BaseModel):
    """Website deployment configuration."""
    
    # AWS S3 configuration
    s3_bucket: Optional[str] = None
    s3_region: str = Field(default="us-east-1")
    
    # CloudFront configuration
    cloudfront_distribution_id: Optional[str] = None
    cloudfront_domain: Optional[str] = None
    
    # SSL certificate
    certificate_arn: Optional[str] = None
    
    # Custom domain configuration
    custom_domain: Optional[str] = None
    dns_configured: bool = Field(default=False)
    
    # CDN settings
    cache_ttl: int = Field(default=86400, description="Cache TTL in seconds")
    enable_compression: bool = Field(default=True)
    
    # Security settings
    enable_https_redirect: bool = Field(default=True)
    enable_security_headers: bool = Field(default=True)


class BusinessWebsite(BaseModel):
    """
    Business website entity with trade-specific SEO optimization.
    
    Each business can have one website that showcases their trades
    and services with AI-generated, SEO-optimized content.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    branding_id: Optional[uuid.UUID] = None
    template_id: Optional[uuid.UUID] = None
    
    # Domain configuration
    domain: Optional[str] = Field(None, max_length=255)
    subdomain: Optional[str] = Field(None, max_length=100, description="For hero365.ai subdomains")
    
    # Website status
    status: WebsiteStatus = Field(default=WebsiteStatus.DRAFT)
    
    # Trade-specific configuration
    primary_trade: Optional[str] = Field(None, description="Primary trade for SEO focus")
    secondary_trades: List[str] = Field(default_factory=list, description="Additional trades")
    service_areas: List[str] = Field(default_factory=list, description="Geographic service areas")
    
    # Customization
    theme_overrides: Dict[str, Any] = Field(default_factory=dict, description="Theme customizations")
    content_overrides: Dict[str, Any] = Field(default_factory=dict, description="Content edits")
    pages: Dict[str, Any] = Field(default_factory=dict, description="Generated page structure")
    
    # Deployment
    deployment_config: DeploymentConfig = Field(default_factory=DeploymentConfig)
    build_config: Dict[str, Any] = Field(default_factory=dict, description="Build-time settings")
    website_url: Optional[str] = Field(None, max_length=500, description="Full website URL after deployment")
    
    # Build tracking
    build_path: Optional[str] = Field(None, max_length=500)
    last_build_at: Optional[datetime] = None
    last_deploy_at: Optional[datetime] = None
    build_duration_seconds: Optional[int] = Field(None, ge=0)
    
    # SEO configuration
    seo_keywords: List[str] = Field(default_factory=list, description="Target keywords")
    target_locations: List[str] = Field(default_factory=list, description="Target locations")
    google_site_verification: Optional[str] = None
    
    # Performance metrics
    lighthouse_score: Optional[int] = Field(None, ge=0, le=100)
    core_web_vitals: CoreWebVitals = Field(default_factory=CoreWebVitals)
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @model_validator(mode='after')
    def validate_domain_or_subdomain(self):
        """Ensure either domain or subdomain is provided."""
        if not self.domain and not self.subdomain:
            raise ValueError("Either domain or subdomain must be provided")
        
        return self
    
    @validator('seo_keywords')
    def validate_seo_keywords(cls, v):
        """Limit SEO keywords to reasonable number."""
        if len(v) > 50:
            raise ValueError("Maximum 50 SEO keywords allowed")
        return v
    
    def get_full_domain(self) -> str:
        """Get the full domain (custom or subdomain)."""
        if self.domain:
            return self.domain
        elif self.subdomain:
            return f"{self.subdomain}.hero365.ai"
        else:
            raise ValueError("No domain configured")
    
    def get_website_url(self) -> str:
        """Get the full website URL."""
        return f"https://{self.get_full_domain()}"
    
    def is_deployed(self) -> bool:
        """Check if website is deployed."""
        return self.status == WebsiteStatus.DEPLOYED
    
    def get_seo_focus_keywords(self) -> List[str]:
        """Generate primary SEO keywords based on trades."""
        keywords = []
        
        if self.primary_trade:
            keywords.extend([
                f"{self.primary_trade} services",
                f"{self.primary_trade} contractor",
                f"professional {self.primary_trade}"
            ])
        
        # Add location-based keywords
        for area in self.service_areas[:3]:  # Top 3 service areas
            if self.primary_trade:
                keywords.append(f"{self.primary_trade} {area}")
        
        return keywords


# =====================================
# DOMAIN REGISTRATION ENTITIES
# =====================================

class SEOFactors(BaseModel):
    """Detailed SEO scoring factors for domain evaluation."""
    
    tld_score: int = Field(default=0, ge=0, le=100)
    length_score: int = Field(default=0, ge=0, le=100)
    keyword_score: int = Field(default=0, ge=0, le=100)
    brandability_score: int = Field(default=0, ge=0, le=100)
    memorability_score: int = Field(default=0, ge=0, le=100)
    
    # Detailed factors
    contains_primary_trade: bool = Field(default=False)
    contains_any_trade: bool = Field(default=False)
    exact_match_trade: bool = Field(default=False)
    has_hyphens: bool = Field(default=False)
    is_alphabetic_only: bool = Field(default=False)
    
    def calculate_total_score(self) -> int:
        """Calculate total SEO score from individual factors."""
        return min(
            (self.tld_score + self.length_score + self.keyword_score + 
             self.brandability_score + self.memorability_score) // 5,
            100
        )


class DomainRegistration(BaseModel):
    """
    Domain registration tracking with SEO scoring.
    
    Manages domain purchases, renewals, and SEO value assessment
    based on trade relevance and other factors.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    website_id: Optional[uuid.UUID] = None
    
    # Domain details
    domain: str = Field(..., max_length=255)
    provider: str = Field(default="cloudflare", max_length=50)
    
    # Registration status
    status: DomainStatus = Field(default=DomainStatus.ACTIVE)
    
    # Registration details
    registered_at: datetime
    expires_at: datetime
    auto_renew: bool = Field(default=True)
    privacy_protection: bool = Field(default=True)
    
    # Provider details
    provider_order_id: Optional[str] = None
    nameservers: List[str] = Field(default_factory=list)
    dns_configured: bool = Field(default=False)
    
    # Pricing
    purchase_price: Optional[Decimal] = Field(None, decimal_places=2)
    renewal_price: Optional[Decimal] = Field(None, decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    
    # SEO scoring
    seo_score: Optional[int] = Field(None, ge=0, le=100)
    seo_factors: SEOFactors = Field(default_factory=SEOFactors)
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('domain')
    def validate_domain_format(cls, v):
        """Validate domain format."""
        if not v or '.' not in v:
            raise ValueError("Invalid domain format")
        
        # Basic domain validation
        parts = v.split('.')
        if len(parts) < 2:
            raise ValueError("Domain must have at least one dot")
        
        return v.lower()
    
    @validator('expires_at')
    def validate_expiration(cls, v, values):
        """Ensure expiration is after registration."""
        registered_at = values.get('registered_at')
        if registered_at and v <= registered_at:
            raise ValueError("Expiration date must be after registration date")
        return v
    
    def is_expired(self) -> bool:
        """Check if domain is expired."""
        return datetime.utcnow() > self.expires_at
    
    def days_until_expiry(self) -> int:
        """Get days until domain expires."""
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)
    
    def needs_renewal_warning(self, warning_days: int = 30) -> bool:
        """Check if domain needs renewal warning."""
        return self.days_until_expiry() <= warning_days
    
    def get_tld(self) -> str:
        """Get the top-level domain."""
        return '.' + self.domain.split('.', 1)[1]
    
    def get_domain_name(self) -> str:
        """Get domain name without TLD."""
        return self.domain.split('.', 1)[0]


# =====================================
# SEO TRACKING ENTITIES
# =====================================

class SEOKeywordTracking(BaseModel):
    """
    SEO keyword ranking tracking for local search optimization.
    
    Tracks keyword performance across different locations and
    provides insights for SEO strategy optimization.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    website_id: uuid.UUID
    
    # Keyword details
    keyword: str = Field(..., max_length=255)
    search_volume: int = Field(default=0, ge=0)
    competition_level: CompetitionLevel = Field(default=CompetitionLevel.UNKNOWN)
    
    # Ranking data
    current_rank: Optional[int] = Field(None, ge=1)
    previous_rank: Optional[int] = Field(None, ge=1)
    best_rank: Optional[int] = Field(None, ge=1)
    worst_rank: Optional[int] = Field(None, ge=1)
    
    # Geographic targeting
    target_location: Optional[str] = Field(None, max_length=255)
    location_coordinates: Optional[str] = None  # "lat,lng" format
    
    # Tracking metadata
    first_tracked_at: datetime = Field(default_factory=datetime.utcnow)
    last_checked_at: datetime = Field(default_factory=datetime.utcnow)
    check_frequency_hours: int = Field(default=24, ge=1)
    
    # Trade relevance
    trade_relevance_score: Optional[int] = Field(None, ge=0, le=100)
    is_primary_keyword: bool = Field(default=False)
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('keyword')
    def validate_keyword(cls, v):
        """Validate keyword format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Keyword cannot be empty")
        return v.strip().lower()
    
    def update_rank(self, new_rank: Optional[int]) -> None:
        """Update ranking with history tracking."""
        if new_rank is not None:
            self.previous_rank = self.current_rank
            self.current_rank = new_rank
            
            # Update best/worst ranks
            if self.best_rank is None or new_rank < self.best_rank:
                self.best_rank = new_rank
            
            if self.worst_rank is None or new_rank > self.worst_rank:
                self.worst_rank = new_rank
        
        self.last_checked_at = datetime.utcnow()
    
    def get_rank_change(self) -> Optional[int]:
        """Get rank change from previous check."""
        if self.current_rank is not None and self.previous_rank is not None:
            return self.previous_rank - self.current_rank  # Positive = improvement
        return None
    
    def is_improving(self) -> bool:
        """Check if keyword ranking is improving."""
        change = self.get_rank_change()
        return change is not None and change > 0
    
    def needs_check(self) -> bool:
        """Check if keyword needs ranking update."""
        hours_since_check = (datetime.utcnow() - self.last_checked_at).total_seconds() / 3600
        return hours_since_check >= self.check_frequency_hours


# =====================================
# ANALYTICS ENTITIES
# =====================================

class WebsiteAnalytics(BaseModel):
    """
    Website performance and SEO analytics.
    
    Tracks traffic, performance, and conversion metrics
    for website optimization insights.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    website_id: uuid.UUID
    
    # Time dimension
    date: date
    hour: Optional[int] = Field(None, ge=0, le=23)
    
    # Traffic metrics
    page_views: int = Field(default=0, ge=0)
    unique_visitors: int = Field(default=0, ge=0)
    sessions: int = Field(default=0, ge=0)
    avg_session_duration: int = Field(default=0, ge=0, description="Average session duration in seconds")
    bounce_rate: Decimal = Field(default=Decimal('0.0'), ge=0, le=100, decimal_places=2)
    
    # Performance metrics
    core_web_vitals: CoreWebVitals = Field(default_factory=CoreWebVitals)
    lighthouse_score: Optional[int] = Field(None, ge=0, le=100)
    
    # SEO metrics
    search_impressions: int = Field(default=0, ge=0)
    search_clicks: int = Field(default=0, ge=0)
    avg_search_position: Optional[Decimal] = Field(None, ge=1, decimal_places=2)
    
    # Conversion metrics
    contact_form_submissions: int = Field(default=0, ge=0)
    phone_clicks: int = Field(default=0, ge=0)
    email_clicks: int = Field(default=0, ge=0)
    
    # Geographic data
    top_countries: List[Dict[str, Any]] = Field(default_factory=list)
    top_cities: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Device breakdown
    desktop_percentage: Decimal = Field(default=Decimal('0.0'), ge=0, le=100, decimal_places=2)
    mobile_percentage: Decimal = Field(default=Decimal('0.0'), ge=0, le=100, decimal_places=2)
    tablet_percentage: Decimal = Field(default=Decimal('0.0'), ge=0, le=100, decimal_places=2)
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @model_validator(mode='after')
    def validate_device_percentages(self):
        """Ensure device percentages add up to 100%."""
        desktop = self.desktop_percentage or Decimal('0')
        mobile = self.mobile_percentage or Decimal('0')
        tablet = self.tablet_percentage or Decimal('0')
        
        total = desktop + mobile + tablet
        if total > 0 and abs(total - Decimal('100')) > Decimal('0.1'):
            raise ValueError("Device percentages must add up to 100%")
        
        return self
    
    def get_ctr(self) -> Optional[Decimal]:
        """Calculate click-through rate from search."""
        if self.search_impressions > 0:
            return Decimal(self.search_clicks) / Decimal(self.search_impressions) * 100
        return None
    
    def get_conversion_rate(self) -> Optional[Decimal]:
        """Calculate conversion rate (forms + calls + emails / visitors)."""
        if self.unique_visitors > 0:
            conversions = self.contact_form_submissions + self.phone_clicks + self.email_clicks
            return Decimal(conversions) / Decimal(self.unique_visitors) * 100
        return None


# =====================================
# BUILD JOB ENTITIES
# =====================================

class WebsiteBuildJob(BaseModel):
    """
    Website build job for async processing.
    
    Manages the queue and execution of website builds,
    deployments, and optimization tasks.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    website_id: uuid.UUID
    
    # Job details
    job_type: BuildJobType
    status: BuildJobStatus = Field(default=BuildJobStatus.QUEUED)
    
    # Job configuration
    job_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    
    # Results and logs
    result_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    build_logs: Optional[str] = None
    
    # Priority and retry
    priority: int = Field(default=5, ge=1, le=10, description="1 = highest priority")
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0)
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def start_job(self) -> None:
        """Mark job as started."""
        self.status = BuildJobStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete_job(self, result_data: Dict[str, Any] = None) -> None:
        """Mark job as completed."""
        self.status = BuildJobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        
        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        
        if result_data:
            self.result_data = result_data
    
    def fail_job(self, error_message: str) -> None:
        """Mark job as failed."""
        self.status = BuildJobStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        
        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
    
    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return self.retry_count < self.max_retries and self.status == BuildJobStatus.FAILED
    
    def retry_job(self) -> None:
        """Reset job for retry."""
        if self.can_retry():
            self.retry_count += 1
            self.status = BuildJobStatus.QUEUED
            self.started_at = None
            self.completed_at = None
            self.duration_seconds = None
            self.error_message = None


# =====================================
# GOOGLE BUSINESS PROFILE ENTITIES
# =====================================

class FormFieldType(str, Enum):
    """Form field types for intake forms."""
    TEXT = "text"
    EMAIL = "email"
    TEL = "tel"
    TEXTAREA = "textarea"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    DATE = "date"
    TIME = "time"
    NUMBER = "number"
    FILE = "file"


class FormType(str, Enum):
    """Types of intake forms."""
    CONTACT = "contact"
    QUOTE = "quote"
    BOOKING = "booking"
    EMERGENCY = "emergency"
    CONSULTATION = "consultation"
    MAINTENANCE = "maintenance"


class LeadType(str, Enum):
    """Types of leads from form submissions."""
    QUOTE_REQUEST = "quote_request"
    SERVICE_BOOKING = "service_booking"
    EMERGENCY = "emergency"
    CONSULTATION = "consultation"
    MAINTENANCE = "maintenance"
    GENERAL_INQUIRY = "general_inquiry"
    CALLBACK_REQUEST = "callback_request"


class PriorityLevel(str, Enum):
    """Priority levels for leads and submissions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"


class SubmissionStatus(str, Enum):
    """Status of form submissions."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    CLOSED = "closed"
    SPAM = "spam"


class BookingStatus(str, Enum):
    """Status of booking appointments."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class ConversionEventType(str, Enum):
    """Types of conversion events."""
    FORM_SUBMISSION = "form_submission"
    PHONE_CALL = "phone_call"
    EMAIL_CLICK = "email_click"
    BOOKING_COMPLETED = "booking_completed"
    QUOTE_REQUESTED = "quote_requested"
    EMERGENCY_CALL = "emergency_call"
    CHAT_STARTED = "chat_started"
    DOWNLOAD = "download"


# =====================================
# INTAKE FORM ENTITIES
# =====================================

class FormField(BaseModel):
    """Individual form field configuration."""
    
    name: str = Field(..., description="Field name/identifier")
    type: FormFieldType = Field(..., description="Field input type")
    label: str = Field(..., description="Display label")
    placeholder: Optional[str] = None
    required: bool = Field(default=False)
    options: Optional[List[str]] = Field(None, description="Options for select/radio fields")
    validation: Optional[Dict[str, Any]] = Field(default_factory=dict)
    conditional_logic: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('options')
    def validate_options_for_select_fields(cls, v, values):
        """Validate options are provided for select/radio fields."""
        field_type = values.get('type')
        if field_type in [FormFieldType.SELECT, FormFieldType.RADIO] and not v:
            raise ValueError(f"Options required for {field_type} fields")
        return v


class IntegrationConfig(BaseModel):
    """Integration configuration for form submissions."""
    
    hero365_api: bool = Field(default=True, description="Submit to Hero365 backend")
    email_notifications: bool = Field(default=True)
    sms_notifications: bool = Field(default=False)
    auto_responder: bool = Field(default=True)
    
    # Lead routing configuration
    create_contact: bool = Field(default=True)
    create_estimate: bool = Field(default=False)
    create_job: bool = Field(default=False)
    add_to_calendar: bool = Field(default=False)
    
    # Priority handling
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    auto_call_back: bool = Field(default=False)
    callback_delay_minutes: int = Field(default=15, ge=1)


class WebsiteIntakeForm(BaseModel):
    """
    Website intake form configuration.
    
    Defines the structure and behavior of forms embedded
    in websites for lead capture and booking.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    website_id: uuid.UUID
    
    # Form identification
    form_type: FormType
    form_name: str = Field(..., max_length=100)
    
    # Form structure
    fields: List[FormField] = Field(..., min_items=1)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    styling_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Integration settings
    integration_config: IntegrationConfig = Field(default_factory=IntegrationConfig)
    auto_response_config: Dict[str, str] = Field(default_factory=dict)
    lead_routing_config: Dict[str, str] = Field(default_factory=dict)
    
    # Form status
    is_active: bool = Field(default=True)
    is_embedded: bool = Field(default=False)
    
    # Usage tracking
    submission_count: int = Field(default=0, ge=0)
    conversion_rate: Decimal = Field(default=Decimal('0.0'), ge=0, le=100)
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_field_by_name(self, field_name: str) -> Optional[FormField]:
        """Get a form field by name."""
        return next((field for field in self.fields if field.name == field_name), None)
    
    def get_required_fields(self) -> List[FormField]:
        """Get all required fields."""
        return [field for field in self.fields if field.required]
    
    def validate_submission_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate form submission data and return list of errors."""
        errors = []
        
        # Check required fields
        for field in self.get_required_fields():
            if field.name not in data or not data[field.name]:
                errors.append(f"{field.label} is required")
        
        # Validate field types and formats
        for field in self.fields:
            if field.name in data and data[field.name]:
                value = data[field.name]
                
                if field.type == FormFieldType.EMAIL:
                    # Basic email validation
                    if '@' not in str(value):
                        errors.append(f"{field.label} must be a valid email address")
                
                elif field.type == FormFieldType.TEL:
                    # Basic phone validation
                    phone_digits = ''.join(filter(str.isdigit, str(value)))
                    if len(phone_digits) < 10:
                        errors.append(f"{field.label} must be a valid phone number")
        
        return errors


class WebsiteFormSubmission(BaseModel):
    """
    Website form submission with lead processing.
    
    Represents a submitted form with all data and
    processing status for lead management.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    website_id: uuid.UUID
    form_id: uuid.UUID
    business_id: uuid.UUID
    
    # Submission data
    form_data: Dict[str, Any] = Field(..., description="All form field values")
    visitor_info: Dict[str, Any] = Field(default_factory=dict)
    
    # Lead classification
    lead_type: LeadType
    priority_level: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    
    # Extracted contact information
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    service_address: Optional[str] = None
    
    # Processing status
    status: SubmissionStatus = Field(default=SubmissionStatus.NEW)
    
    # Integration results
    contact_created_id: Optional[uuid.UUID] = None
    estimate_created_id: Optional[uuid.UUID] = None
    job_created_id: Optional[uuid.UUID] = None
    
    # Response tracking
    auto_response_sent: bool = Field(default=False)
    follow_up_scheduled: bool = Field(default=False)
    first_response_at: Optional[datetime] = None
    
    # Conversion tracking
    converted_at: Optional[datetime] = None
    conversion_value: Optional[Decimal] = Field(None, decimal_places=2)
    
    # Audit fields
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def extract_contact_info(self) -> None:
        """Extract contact information from form data."""
        if 'name' in self.form_data:
            self.contact_name = str(self.form_data['name'])
        
        if 'email' in self.form_data:
            self.contact_email = str(self.form_data['email'])
        
        if 'phone' in self.form_data:
            self.contact_phone = str(self.form_data['phone'])
        
        if 'address' in self.form_data:
            self.service_address = str(self.form_data['address'])
        elif 'service_address' in self.form_data:
            self.service_address = str(self.form_data['service_address'])
    
    def mark_processed(self) -> None:
        """Mark submission as processed."""
        self.processed_at = datetime.utcnow()
        if self.status == SubmissionStatus.NEW:
            self.status = SubmissionStatus.CONTACTED
    
    def mark_converted(self, value: Optional[Decimal] = None) -> None:
        """Mark submission as converted."""
        self.status = SubmissionStatus.CONVERTED
        self.converted_at = datetime.utcnow()
        if value:
            self.conversion_value = value
    
    def get_estimated_value(self) -> Decimal:
        """Get estimated lead value based on lead type."""
        value_map = {
            LeadType.EMERGENCY: Decimal('500.00'),
            LeadType.SERVICE_BOOKING: Decimal('300.00'),
            LeadType.QUOTE_REQUEST: Decimal('250.00'),
            LeadType.CONSULTATION: Decimal('150.00'),
            LeadType.MAINTENANCE: Decimal('200.00'),
            LeadType.GENERAL_INQUIRY: Decimal('100.00'),
            LeadType.CALLBACK_REQUEST: Decimal('75.00')
        }
        return value_map.get(self.lead_type, Decimal('100.00'))


class WebsiteBookingSlot(BaseModel):
    """
    Website booking appointment slot.
    
    Represents a scheduled service appointment
    booked through the website booking system.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    website_id: uuid.UUID
    business_id: uuid.UUID
    
    # Booking details
    service_type: str = Field(..., max_length=100)
    appointment_date: date
    start_time: time
    end_time: time
    duration_minutes: int = Field(..., gt=0)
    
    # Customer information
    customer_name: str = Field(..., max_length=255)
    customer_email: Optional[str] = Field(None, max_length=320)
    customer_phone: str = Field(..., max_length=20)
    service_address: str
    
    # Booking details
    booking_notes: Optional[str] = None
    special_requirements: Optional[str] = None
    access_instructions: Optional[str] = None
    
    # Booking status
    status: BookingStatus = Field(default=BookingStatus.PENDING)
    
    # Integration
    calendar_event_id: Optional[uuid.UUID] = None
    technician_assigned_id: Optional[uuid.UUID] = None
    
    # Payment information
    requires_deposit: bool = Field(default=False)
    deposit_amount: Optional[Decimal] = Field(None, decimal_places=2)
    deposit_paid: bool = Field(default=False)
    
    # Confirmation and reminders
    confirmation_sent: bool = Field(default=False)
    reminder_24h_sent: bool = Field(default=False)
    reminder_2h_sent: bool = Field(default=False)
    
    # Audit fields
    booked_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('end_time')
    def validate_end_time_after_start(cls, v, values):
        """Ensure end time is after start time."""
        start_time = values.get('start_time')
        if start_time and v <= start_time:
            raise ValueError("End time must be after start time")
        return v
    
    def get_appointment_datetime(self) -> datetime:
        """Get full appointment datetime."""
        return datetime.combine(self.appointment_date, self.start_time)
    
    def is_upcoming(self) -> bool:
        """Check if appointment is in the future."""
        return self.get_appointment_datetime() > datetime.utcnow()
    
    def confirm_booking(self) -> None:
        """Confirm the booking."""
        self.status = BookingStatus.CONFIRMED
        self.confirmed_at = datetime.utcnow()
    
    def needs_reminder(self, hours_before: int) -> bool:
        """Check if booking needs a reminder."""
        appointment_time = self.get_appointment_datetime()
        reminder_time = appointment_time - timedelta(hours=hours_before)
        return datetime.utcnow() >= reminder_time and self.status == BookingStatus.CONFIRMED


class WebsiteConversionTracking(BaseModel):
    """
    Website conversion event tracking.
    
    Tracks visitor actions and conversions for
    analytics and optimization insights.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    website_id: uuid.UUID
    
    # Conversion event
    event_type: ConversionEventType
    event_value: Decimal = Field(default=Decimal('0.0'), decimal_places=2)
    
    # Visitor tracking
    visitor_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Attribution
    traffic_source: Optional[str] = None  # organic, paid, direct, referral, social
    campaign_name: Optional[str] = None
    referrer_url: Optional[str] = None
    landing_page: Optional[str] = None
    
    # Event details
    event_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Geographic data
    visitor_country: Optional[str] = None
    visitor_region: Optional[str] = None
    visitor_city: Optional[str] = None
    
    # Device information
    device_type: Optional[str] = None  # desktop, mobile, tablet
    browser: Optional[str] = None
    operating_system: Optional[str] = None
    
    # Audit fields
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def is_high_value_conversion(self) -> bool:
        """Check if this is a high-value conversion."""
        high_value_events = [
            ConversionEventType.BOOKING_COMPLETED,
            ConversionEventType.QUOTE_REQUESTED,
            ConversionEventType.EMERGENCY_CALL
        ]
        return self.event_type in high_value_events or self.event_value >= Decimal('100.00')


# =====================================
# GOOGLE BUSINESS PROFILE ENTITIES
# =====================================

class GoogleBusinessProfile(BaseModel):
    """
    Google Business Profile integration and sync management.
    
    Manages the connection to Google Business Profile API
    and synchronizes business information for SEO benefits.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    website_id: Optional[uuid.UUID] = None
    
    # Google API identifiers
    google_account_id: Optional[str] = None
    location_id: Optional[str] = None
    place_id: Optional[str] = None
    
    # Sync configuration
    auto_sync_enabled: bool = Field(default=True)
    sync_frequency_hours: int = Field(default=24, ge=1)
    last_sync_at: Optional[datetime] = None
    
    # Cached data
    profile_data: Dict[str, Any] = Field(default_factory=dict)
    insights_data: Dict[str, Any] = Field(default_factory=dict)
    reviews_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Sync status
    sync_status: SyncStatus = Field(default=SyncStatus.PENDING)
    last_error: Optional[str] = None
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def needs_sync(self) -> bool:
        """Check if profile needs synchronization."""
        if not self.auto_sync_enabled or not self.last_sync_at:
            return True
        
        hours_since_sync = (datetime.utcnow() - self.last_sync_at).total_seconds() / 3600
        return hours_since_sync >= self.sync_frequency_hours
    
    def mark_sync_success(self, profile_data: Dict[str, Any] = None) -> None:
        """Mark successful sync."""
        self.sync_status = SyncStatus.ACTIVE
        self.last_sync_at = datetime.utcnow()
        self.last_error = None
        
        if profile_data:
            self.profile_data = profile_data
    
    def mark_sync_error(self, error_message: str) -> None:
        """Mark sync error."""
        self.sync_status = SyncStatus.ERROR
        self.last_error = error_message
    
    def is_connected(self) -> bool:
        """Check if profile is properly connected."""
        return (
            self.google_account_id is not None and 
            self.location_id is not None and 
            self.sync_status == SyncStatus.ACTIVE
        )


class ReviewData(BaseModel):
    """Google Business Profile review data."""
    
    google_review_id: str
    reviewer_name: str
    reviewer_profile_photo: Optional[str] = None
    rating: int = Field(ge=1, le=5)
    review_text: str
    review_date: datetime
    business_response: Optional[str] = None
    response_date: Optional[datetime] = None
    is_responded: bool = Field(default=False)
    sentiment_score: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    review_url: Optional[str] = None


class InsightData(BaseModel):
    """Google Business Profile insights data."""
    
    profile_id: uuid.UUID
    date_range_start: date
    date_range_end: date
    
    # Search metrics
    search_queries_direct: int = Field(default=0, ge=0)
    search_queries_indirect: int = Field(default=0, ge=0)
    search_queries_chain: int = Field(default=0, ge=0)
    
    # View metrics
    views_search: int = Field(default=0, ge=0)
    views_maps: int = Field(default=0, ge=0)
    
    # Action metrics
    actions_website: int = Field(default=0, ge=0)
    actions_phone: int = Field(default=0, ge=0)
    actions_directions: int = Field(default=0, ge=0)
    
    # Calculated metrics
    total_searches: int = Field(default=0, ge=0)
    total_views: int = Field(default=0, ge=0)
    total_actions: int = Field(default=0, ge=0)
    
    collected_at: datetime = Field(default_factory=datetime.utcnow)
