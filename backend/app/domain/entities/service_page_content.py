"""
Service page content entities for LLM-generated SEO pages.
Defines structured content blocks and schema markup for rich service pages.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ContentSource(str, Enum):
    """Source of content generation."""
    TEMPLATE = "template"
    LLM = "llm"
    MIXED = "mixed"
    MANUAL = "manual"


class ContentBlockType(str, Enum):
    """Types of content blocks for service pages."""
    HERO = "hero"
    OVERVIEW = "overview"
    BENEFITS = "benefits"
    PROCESS_STEPS = "process_steps"
    PRICING = "pricing"
    BRANDS = "brands"
    FINANCING = "financing"
    CASE_STUDIES = "case_studies"
    MEMBERSHIP = "membership"
    FAQ = "faq"
    RELATED_SERVICES = "related_services"
    SERVICE_AREAS = "service_areas"
    LOCAL_TRUST = "local_trust"
    MEDIA = "media"
    CTA = "cta"
    RICH_TEXT = "rich_text"


class SchemaType(str, Enum):
    """JSON-LD schema types."""
    SERVICE = "Service"
    LOCAL_BUSINESS = "LocalBusiness"
    FAQ_PAGE = "FAQPage"
    HOW_TO = "HowTo"
    BREADCRUMB_LIST = "BreadcrumbList"
    AGGREGATE_RATING = "AggregateRating"
    OFFER = "Offer"
    PRODUCT = "Product"


class ContentBlock(BaseModel):
    """Base content block with type and payload."""
    type: ContentBlockType
    title: Optional[str] = None
    content: Dict[str, Any] = Field(default_factory=dict)
    order: int = Field(default=0, description="Display order on page")
    visible: bool = Field(default=True)
    source: ContentSource = ContentSource.TEMPLATE
    
    class Config:
        use_enum_values = True


class HeroBlock(ContentBlock):
    """Hero section content."""
    type: ContentBlockType = ContentBlockType.HERO
    content: Dict[str, Any] = Field(default_factory=lambda: {
        "h1": "",
        "subheading": "",
        "description": "",
        "primary_cta": {"text": "Get Free Quote", "action": "quote"},
        "secondary_cta": {"text": "Call Now", "action": "phone"},
        "trust_badges": [],
        "quick_facts": []
    })


class BenefitsBlock(ContentBlock):
    """Benefits grid content."""
    type: ContentBlockType = ContentBlockType.BENEFITS
    content: Dict[str, Any] = Field(default_factory=lambda: {
        "title": "Why Choose Us",
        "benefits": [
            # {"title": "Licensed & Insured", "description": "...", "icon": "shield"}
        ]
    })


class ProcessStepsBlock(ContentBlock):
    """Process steps (maps to HowTo schema)."""
    type: ContentBlockType = ContentBlockType.PROCESS_STEPS
    content: Dict[str, Any] = Field(default_factory=lambda: {
        "title": "How It Works",
        "description": "",
        "steps": [
            # {"name": "Assessment", "text": "...", "image": "...", "url": "..."}
        ]
    })


class PricingBlock(ContentBlock):
    """Pricing and packages."""
    type: ContentBlockType = ContentBlockType.PRICING
    content: Dict[str, Any] = Field(default_factory=lambda: {
        "title": "Pricing & Packages",
        "description": "",
        "starting_price": None,
        "packages": [],
        "financing_available": False,
        "rebates": [],
        "warranty_info": ""
    })


class FAQBlock(ContentBlock):
    """FAQ section (maps to FAQPage schema)."""
    type: ContentBlockType = ContentBlockType.FAQ
    content: Dict[str, Any] = Field(default_factory=lambda: {
        "title": "Frequently Asked Questions",
        "faqs": [
            # {"question": "...", "answer": "..."}
        ]
    })


class CaseStudiesBlock(ContentBlock):
    """Local case studies and projects."""
    type: ContentBlockType = ContentBlockType.CASE_STUDIES
    content: Dict[str, Any] = Field(default_factory=lambda: {
        "title": "Recent Projects",
        "description": "",
        "studies": [
            # {"title": "...", "location": "...", "before": "...", "after": "...", "metrics": {}}
        ]
    })


class RelatedServicesBlock(ContentBlock):
    """Related services for internal linking."""
    type: ContentBlockType = ContentBlockType.RELATED_SERVICES
    content: Dict[str, Any] = Field(default_factory=lambda: {
        "title": "Related Services",
        "services": [
            # {"name": "...", "slug": "...", "description": "...", "url": "..."}
        ]
    })


class ServiceAreasBlock(ContentBlock):
    """Service areas and locations."""
    type: ContentBlockType = ContentBlockType.SERVICE_AREAS
    content: Dict[str, Any] = Field(default_factory=lambda: {
        "title": "Service Areas",
        "description": "",
        "primary_areas": [],
        "nearby_cities": [],
        "neighborhoods": []
    })


class SchemaBlock(BaseModel):
    """JSON-LD schema markup block."""
    type: SchemaType
    data: Dict[str, Any]
    priority: int = Field(default=0, description="Injection priority")
    
    class Config:
        use_enum_values = True


class ContentMetrics(BaseModel):
    """Content quality metrics."""
    word_count: int = 0
    heading_count: int = 0
    internal_link_count: int = 0
    external_link_count: int = 0
    image_count: int = 0
    faq_count: int = 0
    readability_score: Optional[float] = None
    keyword_density: Dict[str, float] = Field(default_factory=dict)


class ServicePageContent(BaseModel):
    """Complete service page content structure."""
    business_id: str
    service_slug: str
    location_slug: Optional[str] = None
    
    # Content structure
    content_blocks: List[ContentBlock] = Field(default_factory=list)
    schema_blocks: List[SchemaBlock] = Field(default_factory=list)
    
    # Metadata
    title: str = ""
    meta_description: str = ""
    canonical_url: str = ""
    target_keywords: List[str] = Field(default_factory=list)
    
    # Generation info
    content_source: ContentSource = ContentSource.TEMPLATE
    revision: int = 1
    content_hash: Optional[str] = None
    
    # Quality metrics
    metrics: ContentMetrics = Field(default_factory=ContentMetrics)
    
    # Status
    status: str = Field(default="draft", description="draft, published, archived")
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True
    
    def get_block_by_type(self, block_type: ContentBlockType) -> Optional[ContentBlock]:
        """Get first content block of specified type."""
        for block in self.content_blocks:
            if block.type == block_type:
                return block
        return None
    
    def get_blocks_by_type(self, block_type: ContentBlockType) -> List[ContentBlock]:
        """Get all content blocks of specified type."""
        return [block for block in self.content_blocks if block.type == block_type]
    
    def add_block(self, block: ContentBlock) -> None:
        """Add content block with auto-ordering."""
        if not block.order:
            block.order = len(self.content_blocks)
        self.content_blocks.append(block)
    
    def get_schema_by_type(self, schema_type: SchemaType) -> Optional[SchemaBlock]:
        """Get first schema block of specified type."""
        for schema in self.schema_blocks:
            if schema.type == schema_type:
                return schema
        return None
    
    def calculate_metrics(self) -> ContentMetrics:
        """Calculate content quality metrics."""
        metrics = ContentMetrics()
        
        # Count words across all text content
        total_words = 0
        headings = 0
        internal_links = 0
        
        for block in self.content_blocks:
            if isinstance(block.content, dict):
                # Count words in text fields
                for key, value in block.content.items():
                    if isinstance(value, str):
                        total_words += len(value.split())
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict) and 'text' in item:
                                total_words += len(str(item['text']).split())
                            elif isinstance(item, str):
                                total_words += len(item.split())
                
                # Count headings
                if 'title' in block.content and block.content['title']:
                    headings += 1
                
                # Count FAQ questions as headings
                if block.type == ContentBlockType.FAQ and 'faqs' in block.content:
                    headings += len(block.content['faqs'])
        
        metrics.word_count = total_words
        metrics.heading_count = headings
        metrics.faq_count = len(self.get_blocks_by_type(ContentBlockType.FAQ))
        
        self.metrics = metrics
        return metrics
    
    @property
    def is_location_specific(self) -> bool:
        """Check if this is a location-specific page."""
        return self.location_slug is not None
    
    @property
    def page_url(self) -> str:
        """Generate page URL path."""
        if self.location_slug:
            return f"/services/{self.service_slug}/{self.location_slug}"
        return f"/services/{self.service_slug}"
