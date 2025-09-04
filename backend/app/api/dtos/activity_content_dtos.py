"""DTOs for activity content pack endpoints."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ActivityContentPackHero(BaseModel):
    """Hero section content for an activity."""
    title: str = Field(..., description="Main hero title")
    subtitle: Optional[str] = Field(None, description="Hero subtitle")
    cta_label: Optional[str] = Field(None, description="Call-to-action button label")
    icon: Optional[str] = Field(None, description="Icon identifier")


class ActivityContentPackBenefits(BaseModel):
    """Benefits section content for an activity."""
    heading: str = Field(..., description="Benefits section heading")
    bullets: List[str] = Field(..., description="List of benefit points")


class ActivityContentPackProcess(BaseModel):
    """Process section content for an activity."""
    heading: str = Field(..., description="Process section heading")
    steps: List[str] = Field(..., description="List of process steps")


class ActivityContentPackFAQ(BaseModel):
    """FAQ item for an activity."""
    q: str = Field(..., description="Question")
    a: str = Field(..., description="Answer")


class ActivityContentPackSEO(BaseModel):
    """SEO content for an activity."""
    title_template: str = Field(..., description="Title template with placeholders")
    description_template: str = Field(..., description="Description template with placeholders")
    keywords: List[str] = Field(..., description="SEO keywords")


class ActivityContentPackSchema(BaseModel):
    """Schema.org content for an activity."""
    service_type: str = Field(..., description="Service type for schema.org")
    description: str = Field(..., description="Service description")
    category: Optional[str] = Field(None, description="Service category")


class ActivityContentPackPricing(BaseModel):
    """Pricing information for an activity."""
    starting_price: Optional[float] = Field(None, description="Starting price")
    price_range: Optional[str] = Field(None, description="Price range display")
    unit: Optional[str] = Field(None, description="Pricing unit")


class ActivityContentPackResponse(BaseModel):
    """Complete activity content pack response."""
    activity_slug: str = Field(..., description="Activity slug identifier")
    hero: ActivityContentPackHero
    benefits: ActivityContentPackBenefits
    process: ActivityContentPackProcess
    faqs: List[ActivityContentPackFAQ]
    seo: ActivityContentPackSEO
    schema: ActivityContentPackSchema
    pricing: Optional[ActivityContentPackPricing] = None


class BusinessActivityServiceTemplate(BaseModel):
    """Service template associated with a business activity."""
    template_slug: str = Field(..., description="Template slug")
    name: str = Field(..., description="Template name")
    pricing_model: str = Field(..., description="Pricing model")
    pricing_config: Dict[str, Any] = Field(default_factory=dict, description="Pricing configuration")


class BusinessActivityBookingField(BaseModel):
    """Booking field for a business activity."""
    key: str = Field(..., description="Field key")
    type: str = Field(..., description="Field type")
    label: str = Field(..., description="Field label")
    options: Optional[List[str]] = Field(None, description="Field options for select/radio")
    required: Optional[bool] = Field(None, description="Whether field is required")


class BusinessActivityDataResponse(BaseModel):
    """Business activity data response."""
    activity_slug: str = Field(..., description="Activity slug")
    activity_name: str = Field(..., description="Activity name")
    trade_slug: str = Field(..., description="Trade slug")
    trade_name: str = Field(..., description="Trade name")
    service_templates: List[BusinessActivityServiceTemplate] = Field(default_factory=list)
    booking_fields: List[BusinessActivityBookingField] = Field(default_factory=list)


class ActivityPageDataRequest(BaseModel):
    """Request for activity page data."""
    business_id: str = Field(..., description="Business ID")
    activity_slug: str = Field(..., description="Activity slug")


class ActivityPageDataResponse(BaseModel):
    """Complete activity page data response."""
    activity: BusinessActivityDataResponse
    content: ActivityContentPackResponse
    business: Dict[str, Any] = Field(..., description="Business information")


class ActivityContentPackListResponse(BaseModel):
    """List of available activity content packs."""
    activity_slugs: List[str] = Field(..., description="Available activity slugs")
    total_count: int = Field(..., description="Total number of content packs")
