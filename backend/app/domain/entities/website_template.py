"""
Website Template Domain Entities

Entities for the website template generation system matching the Supabase schema
and designed for template-driven static site generation.
"""

import uuid
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from decimal import Decimal

from ..exceptions.domain_exceptions import DomainValidationError


class OfferType(Enum):
    """Types of promotional offers."""
    PERCENTAGE_DISCOUNT = "percentage_discount"
    FIXED_AMOUNT = "fixed_amount"
    BUY_ONE_GET_ONE = "buy_one_get_one"
    FREE_SERVICE = "free_service"
    SEASONAL_SPECIAL = "seasonal_special"
    NEW_CUSTOMER = "new_customer"
    REFERRAL = "referral"


class PromoPlacement(Enum):
    """Website placement locations for promotional content."""
    HERO_BANNER = "hero_banner"
    PROMO_CAROUSEL = "promo_carousel"
    SIDEBAR = "sidebar"
    FOOTER = "footer"
    POPUP = "popup"
    INLINE = "inline"


class RatingPlatform(Enum):
    """Review platforms for ratings snapshots."""
    GOOGLE = "google"
    YELP = "yelp"
    BBB = "bbb"
    ANGIE = "angie"
    FACEBOOK = "facebook"
    TRUSTPILOT = "trustpilot"
    HOMEADVISOR = "homeadvisor"
    THUMBTACK = "thumbtack"


class CertificateType(Enum):
    """Types of awards and certifications."""
    INDUSTRY_AWARD = "industry_award"
    CERTIFICATION = "certification"
    LICENSE = "license"
    ACCREDITATION = "accreditation"
    SAFETY_CERTIFICATION = "safety_certification"
    TRAINING_COMPLETION = "training_completion"
    QUALITY_ASSURANCE = "quality_assurance"


class PartnerType(Enum):
    """Types of business partnerships."""
    MANUFACTURER = "manufacturer"
    DISTRIBUTOR = "distributor"
    SUPPLIER = "supplier"
    TECHNOLOGY_PARTNER = "technology_partner"
    CERTIFICATION_BODY = "certification_body"
    TRADE_ASSOCIATION = "trade_association"
    DEALER_NETWORK = "dealer_network"


class TestimonialSource(Enum):
    """Sources of customer testimonials."""
    GOOGLE_REVIEW = "google_review"
    YELP_REVIEW = "yelp_review"
    FACEBOOK_REVIEW = "facebook_review"
    DIRECT_FEEDBACK = "direct_feedback"
    SURVEY_RESPONSE = "survey_response"
    CASE_STUDY = "case_study"
    REFERRAL_FEEDBACK = "referral_feedback"
    MANUAL_ENTRY = "manual_entry"


class ModerationStatus(Enum):
    """Content moderation statuses."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class DeploymentType(Enum):
    """Website deployment types."""
    PRODUCTION = "production"
    STAGING = "staging"
    PREVIEW = "preview"
    DEVELOPMENT = "development"


class BuildStatus(Enum):
    """Website build statuses."""
    PENDING = "pending"
    BUILDING = "building"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LocationType(Enum):
    """Business location types."""
    HEADQUARTERS = "headquarters"
    BRANCH_OFFICE = "branch_office"
    SERVICE_AREA = "service_area"
    COVERAGE_ZONE = "coverage_zone"
    WAREHOUSE = "warehouse"


# =====================================
# PROMOTIONAL OFFERS
# =====================================

class PromoOffer(BaseModel):
    """Promotional offer entity for website display."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    
    # Offer details
    title: str = Field(..., min_length=1, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    offer_type: OfferType
    
    # Display settings
    price_label: Optional[str] = Field(None, max_length=100)  # e.g., "Starting at $99"
    badge_text: Optional[str] = Field(None, max_length=50)  # e.g., "Limited Time"
    cta_text: str = Field(default="Learn More", max_length=100)
    cta_link: Optional[str] = Field(None, max_length=500)
    
    # Placement and priority
    placement: PromoPlacement
    priority: int = Field(default=0, description="Higher numbers = higher priority")
    
    # Targeting and validity
    target_services: List[str] = Field(default_factory=list)
    target_trades: List[str] = Field(default_factory=list)
    service_areas: List[str] = Field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Status and tracking
    is_active: bool = True
    is_featured: bool = False
    view_count: int = Field(default=0, ge=0)
    click_count: int = Field(default=0, ge=0)
    conversion_count: int = Field(default=0, ge=0)
    
    # Audit fields
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Validate date logic."""
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValueError("End date must be after start date")
        return self
    
    def is_currently_active(self) -> bool:
        """Check if offer is currently active based on dates."""
        if not self.is_active:
            return False
        
        now = datetime.utcnow()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        
        return True


# =====================================
# RATINGS SNAPSHOT
# =====================================

class RatingSnapshot(BaseModel):
    """Rating snapshot from review platforms."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    
    # Rating platform
    platform: RatingPlatform
    
    # Rating data
    rating: Decimal = Field(..., ge=0, le=5, decimal_places=2)
    review_count: int = Field(..., ge=0)
    total_reviews: Optional[int] = Field(None, ge=0)
    
    # Display settings
    display_name: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    profile_url: Optional[str] = Field(None, max_length=500)
    is_featured: bool = False
    sort_order: int = 0
    
    # Data freshness
    last_synced_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    sync_frequency_hours: int = Field(default=24, ge=1)
    is_active: bool = True
    
    # Audit fields
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    def is_stale(self) -> bool:
        """Check if rating data is stale based on sync frequency."""
        if not self.last_synced_at:
            return True
        
        hours_since_sync = (datetime.utcnow() - self.last_synced_at).total_seconds() / 3600
        return hours_since_sync > self.sync_frequency_hours
    
    def get_display_name(self) -> str:
        """Get display name, fallback to platform name."""
        return self.display_name or self.platform.value.title()


# =====================================
# AWARDS AND CERTIFICATIONS
# =====================================

class AwardCertification(BaseModel):
    """Awards and certifications entity."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    
    # Award/Certification details
    name: str = Field(..., min_length=1, max_length=200)
    issuing_organization: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    certificate_type: Optional[CertificateType] = None
    
    # Display assets
    logo_url: Optional[str] = Field(None, max_length=500)
    certificate_url: Optional[str] = Field(None, max_length=500)
    verification_url: Optional[str] = Field(None, max_length=500)
    
    # Validity
    issued_date: Optional[date] = None
    expiry_date: Optional[date] = None
    is_current: bool = True
    
    # Display settings
    is_featured: bool = False
    sort_order: int = 0
    display_on_website: bool = True
    
    # Categories for filtering
    trade_relevance: List[str] = Field(default_factory=list)
    service_categories: List[str] = Field(default_factory=list)
    
    # Status
    is_active: bool = True
    
    # Audit fields
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    def is_expired(self) -> bool:
        """Check if certification is expired."""
        if not self.expiry_date:
            return False
        return date.today() > self.expiry_date
    
    def days_until_expiry(self) -> Optional[int]:
        """Get days until expiry, None if no expiry date."""
        if not self.expiry_date:
            return None
        delta = self.expiry_date - date.today()
        return delta.days


# =====================================
# OEM PARTNERSHIPS
# =====================================

class OEMPartnership(BaseModel):
    """OEM and business partnerships entity."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    
    # Partner details
    partner_name: str = Field(..., min_length=1, max_length=200)
    partner_type: PartnerType
    
    # Partnership details
    partnership_level: Optional[str] = Field(None, max_length=50)  # e.g., "Authorized Dealer"
    description: Optional[str] = None
    partnership_benefits: List[str] = Field(default_factory=list)
    
    # Display assets
    logo_url: str = Field(..., max_length=500)
    partner_url: Optional[str] = Field(None, max_length=500)
    verification_url: Optional[str] = Field(None, max_length=500)
    
    # Relevance and targeting
    trade_relevance: List[str] = Field(..., min_items=1)
    service_categories: List[str] = Field(default_factory=list)
    product_lines: List[str] = Field(default_factory=list)
    
    # Display settings
    is_featured: bool = False
    sort_order: int = 0
    display_on_website: bool = True
    
    # Partnership status
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True
    is_current: bool = True
    
    # Audit fields
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    def is_partnership_active(self) -> bool:
        """Check if partnership is currently active based on dates."""
        if not self.is_active or not self.is_current:
            return False
        
        today = date.today()
        if self.start_date and today < self.start_date:
            return False
        if self.end_date and today > self.end_date:
            return False
        
        return True


# =====================================
# TESTIMONIALS
# =====================================

class Testimonial(BaseModel):
    """Customer testimonials entity."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    
    # Source and attribution
    source_type: TestimonialSource
    source_id: Optional[str] = Field(None, max_length=200)
    source_url: Optional[str] = Field(None, max_length=500)
    
    # Testimonial content
    quote: str = Field(..., min_length=1)
    full_review: Optional[str] = None
    rating: Optional[Decimal] = Field(None, ge=0, le=5, decimal_places=2)
    
    # Customer information
    customer_name: Optional[str] = Field(None, max_length=200)
    customer_initial: Optional[str] = Field(None, max_length=10)  # e.g., "J.S."
    customer_location: Optional[str] = Field(None, max_length=100)
    customer_avatar_url: Optional[str] = Field(None, max_length=500)
    
    # Service context
    service_performed: Optional[str] = Field(None, max_length=200)
    service_date: Optional[date] = None
    project_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    trade_category: Optional[str] = Field(None, max_length=50)
    
    # Display settings
    is_featured: bool = False
    is_verified: bool = False
    display_on_website: bool = True
    sort_order: int = 0
    
    # Content moderation
    moderation_status: ModerationStatus = ModerationStatus.PENDING
    moderated_by: Optional[str] = Field(None, max_length=255)
    moderated_at: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    
    # Audit fields
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    def get_customer_display_name(self) -> str:
        """Get customer display name, preferring initials for privacy."""
        if self.customer_initial:
            return self.customer_initial
        if self.customer_name:
            # Generate initials from full name
            parts = self.customer_name.split()
            if len(parts) >= 2:
                return f"{parts[0][0]}.{parts[-1][0]}."
            return f"{parts[0][0]}."
        return "Anonymous Customer"
    
    def is_ready_for_display(self) -> bool:
        """Check if testimonial is ready for website display."""
        return (
            self.is_active and
            self.display_on_website and
            self.moderation_status == ModerationStatus.APPROVED
        )


# =====================================
# WEBSITE DEPLOYMENTS
# =====================================

class WebsiteDeployment(BaseModel):
    """Website deployment tracking entity."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    
    # Template and deployment details
    template_name: str = Field(..., min_length=1, max_length=100)
    template_version: Optional[str] = Field(None, max_length=50)
    deployment_type: DeploymentType
    
    # Cloudflare project details
    project_name: str = Field(..., min_length=1, max_length=200)
    deploy_url: str = Field(..., min_length=1, max_length=500)
    custom_domain: Optional[str] = Field(None, max_length=200)
    
    # Build information
    build_id: Optional[str] = Field(None, max_length=200)
    build_status: BuildStatus = BuildStatus.PENDING
    build_log: Optional[str] = None
    build_duration_seconds: Optional[int] = Field(None, ge=0)
    
    # Performance metrics
    lighthouse_json: Optional[Dict[str, Any]] = None
    performance_score: Optional[int] = Field(None, ge=0, le=100)
    accessibility_score: Optional[int] = Field(None, ge=0, le=100)
    seo_score: Optional[int] = Field(None, ge=0, le=100)
    best_practices_score: Optional[int] = Field(None, ge=0, le=100)
    
    # Content generation details
    content_generated_at: Optional[datetime] = None
    content_generation_model: Optional[str] = Field(None, max_length=100)
    content_generation_tokens_used: Optional[int] = Field(None, ge=0)
    
    # Status and metadata
    is_current: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Audit fields
    deployed_by: Optional[str] = Field(None, max_length=255)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    def is_successful_deployment(self) -> bool:
        """Check if deployment was successful."""
        return self.build_status == BuildStatus.SUCCESS
    
    def get_lighthouse_overall_score(self) -> Optional[float]:
        """Calculate overall Lighthouse score."""
        scores = [
            self.performance_score,
            self.accessibility_score,
            self.seo_score,
            self.best_practices_score
        ]
        valid_scores = [s for s in scores if s is not None]
        if not valid_scores:
            return None
        return sum(valid_scores) / len(valid_scores)


# =====================================
# BUSINESS LOCATIONS
# =====================================

class BusinessLocation(BaseModel):
    """Business locations and service areas entity."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    
    # Location details
    name: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = None
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    county: Optional[str] = Field(None, max_length=100)
    
    # Geographic data
    latitude: Optional[Decimal] = Field(None, decimal_places=8)
    longitude: Optional[Decimal] = Field(None, decimal_places=8)
    service_radius_miles: Optional[int] = Field(None, ge=0)
    
    # Location type and status
    location_type: LocationType
    is_primary: bool = False
    is_active: bool = True
    
    # Service details
    services_offered: List[str] = Field(default_factory=list)
    trades_covered: List[str] = Field(default_factory=list)
    operating_hours: Optional[Dict[str, Any]] = None
    
    # SEO and website display
    display_on_website: bool = True
    seo_description: Optional[str] = None
    page_slug: Optional[str] = Field(None, max_length=100)
    
    # Audit fields
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    def get_full_address(self) -> str:
        """Get formatted full address."""
        parts = []
        if self.address:
            parts.append(self.address)
        parts.append(f"{self.city}, {self.state}")
        if self.zip_code:
            parts.append(self.zip_code)
        return ", ".join(parts)
    
    def has_coordinates(self) -> bool:
        """Check if location has geographic coordinates."""
        return self.latitude is not None and self.longitude is not None
    
    def get_display_name(self) -> str:
        """Get display name for the location."""
        if self.name:
            return self.name
        return f"{self.city}, {self.state}"


# =====================================
# COMPOSITE DTOs FOR TEMPLATE GENERATION
# =====================================

class ServiceCategoryProps(BaseModel):
    """Service category properties for template rendering."""
    
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    icon_name: Optional[str] = None  # Icon identifier for UI
    slug: str
    services_count: int = 0
    is_featured: bool = False
    sort_order: int = 0


class BusinessProps(BaseModel):
    """Comprehensive business properties for template rendering."""
    
    # Core business info
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    phone_number: Optional[str] = None
    business_email: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    
    # Address and location
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    
    # Business details
    trades: List[str] = Field(default_factory=list)
    service_areas: List[str] = Field(default_factory=list)
    business_hours: Optional[Dict[str, Any]] = None
    
    # SEO helpers
    primary_trade: Optional[str] = None
    seo_keywords: List[str] = Field(default_factory=list)


class TemplateProps(BaseModel):
    """Complete template properties for website generation."""
    
    # Business information
    business: BusinessProps
    
    # Content sections
    service_categories: List[ServiceCategoryProps] = Field(default_factory=list)
    promos: List[PromoOffer] = Field(default_factory=list)
    ratings: List[RatingSnapshot] = Field(default_factory=list)
    awards: List[AwardCertification] = Field(default_factory=list)
    partnerships: List[OEMPartnership] = Field(default_factory=list)
    testimonials: List[Testimonial] = Field(default_factory=list)
    locations: List[BusinessLocation] = Field(default_factory=list)
    
    # Template metadata
    template_name: str = "professional"
    template_version: str = "1.0"
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # SEO and meta
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    canonical_url: Optional[str] = None
    
    def get_featured_promos(self, placement: Optional[PromoPlacement] = None) -> List[PromoOffer]:
        """Get featured promos, optionally filtered by placement."""
        promos = [p for p in self.promos if p.is_featured and p.is_currently_active()]
        if placement:
            promos = [p for p in promos if p.placement == placement]
        return sorted(promos, key=lambda x: (x.priority, x.created_at), reverse=True)
    
    def get_featured_ratings(self) -> List[RatingSnapshot]:
        """Get featured ratings for trust indicators."""
        return sorted(
            [r for r in self.ratings if r.is_featured and r.is_active],
            key=lambda x: (x.sort_order, x.rating),
            reverse=True
        )
    
    def get_approved_testimonials(self, limit: Optional[int] = None) -> List[Testimonial]:
        """Get approved testimonials for display."""
        testimonials = [
            t for t in self.testimonials 
            if t.is_ready_for_display()
        ]
        testimonials.sort(key=lambda x: (x.is_featured, x.rating or 0, x.sort_order), reverse=True)
        return testimonials[:limit] if limit else testimonials


# =====================================
# REQUEST/RESPONSE DTOS
# =====================================

class DynamicWebsiteRequest(BaseModel):
    """Request DTO for dynamic website generation."""
    
    business_id: uuid.UUID
    template_name: str = "professional"
    deployment_type: DeploymentType = DeploymentType.PRODUCTION
    custom_domain: Optional[str] = None
    
    # Override settings
    include_promos: bool = True
    include_testimonials: bool = True
    include_ratings: bool = True
    include_awards: bool = True
    include_partnerships: bool = True
    
    # SEO overrides
    meta_title_override: Optional[str] = None
    meta_description_override: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_id": "123e4567-e89b-12d3-a456-426614174000",
                "template_name": "professional",
                "deployment_type": "production",
                "include_promos": True,
                "include_testimonials": True,
                "include_ratings": True,
                "include_awards": True,
                "include_partnerships": True
            }
        }


class WebsiteGenerationResponse(BaseModel):
    """Response DTO for website generation."""
    
    job_id: uuid.UUID
    business_id: uuid.UUID
    template_props: TemplateProps
    deployment: Optional[WebsiteDeployment] = None
    
    # Generation metadata
    content_tokens_used: Optional[int] = None
    generation_time_seconds: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "business_id": "123e4567-e89b-12d3-a456-426614174000",
                "template_props": {
                    "business": {"name": "ABC Plumbing", "city": "Austin"},
                    "template_name": "professional"
                }
            }
        }


class WebsiteDeploymentResponse(BaseModel):
    """Response DTO for website deployment."""
    
    deployment_id: uuid.UUID
    deploy_url: str
    build_status: BuildStatus
    lighthouse_scores: Optional[Dict[str, int]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
                "deploy_url": "https://abc-plumbing.pages.dev",
                "build_status": "success",
                "lighthouse_scores": {
                    "performance": 95,
                    "accessibility": 98,
                    "seo": 100,
                    "best_practices": 92
                }
            }
        }
