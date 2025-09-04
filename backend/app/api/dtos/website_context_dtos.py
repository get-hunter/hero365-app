"""DTOs for website context endpoint."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class WebsiteBusinessInfo(BaseModel):
    """Business information for website context."""
    id: str = Field(..., description="Business ID")
    name: str = Field(..., description="Business name")
    description: Optional[str] = Field(None, description="Business description")
    phone: Optional[str] = Field(None, description="Business phone number")
    email: Optional[str] = Field(None, description="Business email")
    address: Optional[str] = Field(None, description="Business address")
    city: Optional[str] = Field(None, description="Business city")
    state: Optional[str] = Field(None, description="Business state")
    postal_code: Optional[str] = Field(None, description="Business postal code")
    website: Optional[str] = Field(None, description="Business website URL")
    primary_trade_slug: Optional[str] = Field(None, description="Primary trade slug")
    service_areas: List[str] = Field(default_factory=list, description="Service areas")


class WebsiteBookingField(BaseModel):
    """Booking field for website forms."""
    key: str = Field(..., description="Field key")
    type: str = Field(..., description="Field type (text, select, textarea, etc.)")
    label: str = Field(..., description="Field label")
    options: Optional[List[str]] = Field(None, description="Field options for select/radio")
    required: bool = Field(False, description="Whether field is required")
    placeholder: Optional[str] = Field(None, description="Field placeholder text")
    help_text: Optional[str] = Field(None, description="Help text for field")


class WebsiteActivityInfo(BaseModel):
    """Activity information for website context."""
    slug: str = Field(..., description="Activity slug")
    name: str = Field(..., description="Activity name")
    trade_slug: str = Field(..., description="Trade slug")
    trade_name: str = Field(..., description="Trade name")
    synonyms: List[str] = Field(default_factory=list, description="Activity synonyms")
    tags: List[str] = Field(default_factory=list, description="Activity tags")
    default_booking_fields: List[WebsiteBookingField] = Field(default_factory=list)
    required_booking_fields: List[WebsiteBookingField] = Field(default_factory=list)


class WebsiteServiceTemplate(BaseModel):
    """Service template information for website context."""
    template_slug: str = Field(..., description="Template slug")
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    pricing_model: str = Field(..., description="Pricing model (fixed, hourly, per_unit, etc.)")
    pricing_config: Dict[str, Any] = Field(default_factory=dict, description="Pricing configuration")
    unit_of_measure: Optional[str] = Field(None, description="Unit of measure")
    is_emergency: bool = Field(False, description="Whether this is an emergency service")
    activity_slug: Optional[str] = Field(None, description="Associated activity slug")


class WebsiteTradeInfo(BaseModel):
    """Trade information for website context."""
    slug: str = Field(..., description="Trade slug")
    name: str = Field(..., description="Trade name")
    description: Optional[str] = Field(None, description="Trade description")
    segments: str = Field(..., description="Market segments (residential, commercial, both)")
    icon: Optional[str] = Field(None, description="Trade icon")


class WebsiteContextResponse(BaseModel):
    """Complete website context response."""
    business: WebsiteBusinessInfo
    activities: List[WebsiteActivityInfo] = Field(default_factory=list)
    service_templates: List[WebsiteServiceTemplate] = Field(default_factory=list)
    trades: List[WebsiteTradeInfo] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class WebsiteContextRequest(BaseModel):
    """Request parameters for website context."""
    include_templates: bool = Field(True, description="Include service templates")
    include_trades: bool = Field(True, description="Include trade information")
    activity_limit: Optional[int] = Field(None, description="Limit number of activities returned")
    template_limit: Optional[int] = Field(None, description="Limit number of templates returned")
