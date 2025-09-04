"""
SEO Artifact DTOs

Data Transfer Objects for the new SEO artifact system that powers
programmatic SEO at scale with activity-first content generation.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime


class ActivityType(str, Enum):
    """Activity types for specialized UI modules."""
    HVAC = "hvac"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    ROOFING = "roofing"
    GENERAL_CONTRACTOR = "general_contractor"
    LANDSCAPING = "landscaping"
    SECURITY_SYSTEMS = "security_systems"
    POOL_SPA = "pool_spa"
    GARAGE_DOOR = "garage_door"
    CHIMNEY = "chimney"
    SEPTIC = "septic"
    PEST_CONTROL = "pest_control"
    IRRIGATION = "irrigation"
    PAINTING = "painting"


class ContentSource(str, Enum):
    """Source of content generation."""
    TEMPLATE = "template"
    LLM = "llm"
    RAG_ENHANCED = "rag_enhanced"
    HYBRID = "hybrid"
    MANUAL = "manual"


class ArtifactStatus(str, Enum):
    """Status of SEO artifacts."""
    DRAFT = "draft"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class QualityLevel(str, Enum):
    """Content quality levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


class ActivityModuleConfig(BaseModel):
    """Configuration for activity-specific UI modules."""
    module_type: str = Field(..., description="Module identifier (e.g., 'hvac_tune_up_checklist')")
    enabled: bool = Field(default=True)
    config: Dict[str, Any] = Field(default_factory=dict, description="Module-specific configuration")
    order: int = Field(default=0, description="Display order in page")


class ContentVariant(BaseModel):
    """A/B test variant for content sections."""
    variant_key: str = Field(..., description="Unique variant identifier")
    content: Dict[str, Any] = Field(..., description="Variant content")
    weight: float = Field(default=1.0, description="Traffic allocation weight")
    performance_metrics: Dict[str, float] = Field(default_factory=dict)


class QualityMetrics(BaseModel):
    """Content quality assessment metrics."""
    overall_score: float = Field(ge=0, le=100, description="Overall quality score 0-100")
    overall_level: QualityLevel
    word_count: int = Field(ge=0)
    heading_count: int = Field(ge=0)
    internal_link_count: int = Field(ge=0)
    external_link_count: int = Field(ge=0)
    faq_count: int = Field(ge=0)
    readability_score: Optional[float] = Field(None, ge=0, le=100)
    keyword_density: Dict[str, float] = Field(default_factory=dict)
    local_intent_density: float = Field(default=0.0, ge=0, le=1)
    eat_score: float = Field(default=0.0, ge=0, le=100, description="E-E-A-T score")
    uniqueness_score: float = Field(default=0.0, ge=0, le=100)
    coverage_score: float = Field(default=0.0, ge=0, le=100)
    passed_quality_gate: bool = Field(default=False)


class InternalLink(BaseModel):
    """Internal link for topical authority."""
    anchor_text: str
    target_url: str
    context: str = Field(description="Surrounding text context")
    link_type: str = Field(default="contextual", description="Type: contextual, navigational, footer")


class ActivityPageArtifact(BaseModel):
    """Complete activity page content artifact."""
    # Identifiers
    business_id: str
    activity_slug: str
    location_slug: Optional[str] = None
    artifact_id: Optional[str] = None
    
    # Activity context
    activity_type: ActivityType
    activity_name: str
    
    # SEO metadata
    title: str = Field(..., max_length=60, description="Page title (SEO optimized)")
    meta_description: str = Field(..., max_length=160, description="Meta description")
    h1_heading: str = Field(..., description="Main H1 heading")
    canonical_url: str
    target_keywords: List[str] = Field(default_factory=list)
    
    # Content sections
    hero: Dict[str, Any] = Field(default_factory=dict, description="Hero section content")
    benefits: Dict[str, Any] = Field(default_factory=dict, description="Benefits/value props")
    process: Dict[str, Any] = Field(default_factory=dict, description="How it works steps")
    offers: Dict[str, Any] = Field(default_factory=dict, description="Pricing/packages")
    guarantees: Dict[str, Any] = Field(default_factory=dict, description="Warranties/guarantees")
    faqs: List[Dict[str, str]] = Field(default_factory=list, description="FAQ items")
    cta_sections: List[Dict[str, Any]] = Field(default_factory=list, description="Call-to-action blocks")
    
    # Activity-specific modules
    activity_modules: List[ActivityModuleConfig] = Field(default_factory=list)
    
    # Structured data
    json_ld_schemas: List[Dict[str, Any]] = Field(default_factory=list, description="JSON-LD schemas")
    
    # Internal linking
    internal_links: List[InternalLink] = Field(default_factory=list)
    
    # A/B testing
    content_variants: Dict[str, List[ContentVariant]] = Field(default_factory=dict)
    active_experiment_keys: List[str] = Field(default_factory=list)
    
    # Quality and versioning
    quality_metrics: QualityMetrics
    content_source: ContentSource
    content_hash: Optional[str] = None
    revision: int = Field(default=1)
    
    # Status and lifecycle
    status: ArtifactStatus = ArtifactStatus.DRAFT
    approved_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('title')
    def validate_title_length(cls, v):
        if len(v) > 60:
            raise ValueError('Title must be 60 characters or less for SEO')
        return v
    
    @validator('meta_description')
    def validate_meta_description_length(cls, v):
        if len(v) > 160:
            raise ValueError('Meta description must be 160 characters or less')
        return v
    
    @property
    def page_url(self) -> str:
        """Generate page URL path."""
        if self.location_slug:
            return f"/locations/{self.location_slug}/{self.activity_slug}"
        return f"/services/{self.activity_slug}"
    
    @property
    def is_location_specific(self) -> bool:
        """Check if this is a location-specific page."""
        return self.location_slug is not None


class SitemapEntry(BaseModel):
    """Individual sitemap entry."""
    loc: str = Field(..., description="Page URL")
    lastmod: datetime
    changefreq: str = Field(default="weekly", description="Change frequency")
    priority: float = Field(default=0.5, ge=0, le=1.0)
    page_type: str = Field(description="Type: service, location, project, etc.")


class SitemapManifest(BaseModel):
    """Sitemap manifest for segmented sitemaps."""
    business_id: str
    sitemap_index_url: str
    sitemaps: List[Dict[str, Any]] = Field(default_factory=list, description="Individual sitemap files")
    total_urls: int = Field(default=0)
    generated_at: datetime
    
    # Segmented sitemap data
    service_pages: List[SitemapEntry] = Field(default_factory=list)
    location_pages: List[SitemapEntry] = Field(default_factory=list)
    project_pages: List[SitemapEntry] = Field(default_factory=list)
    static_pages: List[SitemapEntry] = Field(default_factory=list)


class GenerateArtifactsRequest(BaseModel):
    """Request to generate SEO artifacts."""
    business_id: str
    activity_slugs: Optional[List[str]] = None
    location_slugs: Optional[List[str]] = None
    force_regenerate: bool = Field(default=False)
    enable_experiments: bool = Field(default=False)
    quality_threshold: float = Field(default=70.0, ge=0, le=100)


class GenerateArtifactsResponse(BaseModel):
    """Response from artifact generation."""
    business_id: str
    job_id: str
    status: str = Field(description="queued, processing, completed, failed")
    artifacts_generated: int = Field(default=0)
    artifacts_approved: int = Field(default=0)
    quality_gate_failures: int = Field(default=0)
    estimated_completion: Optional[datetime] = None
    generated_at: datetime


class ArtifactListResponse(BaseModel):
    """Response for listing artifacts."""
    business_id: str
    artifacts: List[ActivityPageArtifact]
    total_count: int
    approved_count: int
    published_count: int
    last_updated: Optional[datetime] = None


class SitemapGenerationRequest(BaseModel):
    """Request to generate sitemaps."""
    business_id: str
    base_url: str
    include_drafts: bool = Field(default=False)
    max_urls_per_sitemap: int = Field(default=50000, le=50000)


class SitemapGenerationResponse(BaseModel):
    """Response from sitemap generation."""
    business_id: str
    sitemap_index_url: str
    sitemaps_generated: List[str]
    total_urls: int
    generated_at: datetime


class ExperimentResult(BaseModel):
    """A/B test experiment result."""
    experiment_key: str
    winning_variant: str
    confidence_level: float = Field(ge=0, le=1)
    improvement_percentage: float
    sample_size: int
    test_duration_days: int
    metrics: Dict[str, float] = Field(default_factory=dict)


class PromoteVariantRequest(BaseModel):
    """Request to promote winning variant."""
    business_id: str
    artifact_id: str
    experiment_key: str
    winning_variant_key: str
    experiment_result: ExperimentResult


class QualityGateResult(BaseModel):
    """Quality gate validation result."""
    passed: bool
    overall_score: float
    overall_level: QualityLevel
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    metrics: QualityMetrics
