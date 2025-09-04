"""
Trade Taxonomy Domain Entities

Represents the canonical trade profiles and activities system.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class MarketSegment(Enum):
    """Market segments a trade can serve."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    BOTH = "both"


class TradeProfile(BaseModel):
    """
    Canonical trade profile representing a specific trade/profession.
    
    This is the single source of truth for trade categorization.
    """
    
    slug: str = Field(..., description="Unique slug identifier")
    name: str = Field(..., description="Display name")
    synonyms: List[str] = Field(default_factory=list, description="Alternative names and search terms")
    segments: MarketSegment = Field(default=MarketSegment.BOTH, description="Market segments served")
    icon: Optional[str] = Field(None, description="Icon identifier")
    description: Optional[str] = Field(None, description="Trade description")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    def serves_residential(self) -> bool:
        """Check if this trade serves residential customers."""
        return self.segments in [MarketSegment.RESIDENTIAL, MarketSegment.BOTH]

    def serves_commercial(self) -> bool:
        """Check if this trade serves commercial customers."""
        return self.segments in [MarketSegment.COMMERCIAL, MarketSegment.BOTH]

    def matches_search(self, query: str) -> bool:
        """Check if this profile matches a search query."""
        query_lower = query.lower()
        return (
            query_lower in self.name.lower() or
            query_lower in self.slug.lower() or
            any(query_lower in synonym.lower() for synonym in self.synonyms)
        )


class BookingFieldType(Enum):
    """Types of booking form fields."""
    TEXT = "text"
    TEXTAREA = "textarea"
    SELECT = "select"
    MULTISELECT = "multiselect"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    FILE = "file"


class BookingField(BaseModel):
    """Booking form field definition."""
    
    key: str = Field(..., description="Field identifier")
    type: BookingFieldType = Field(..., description="Field type")
    label: str = Field(..., description="Display label")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    options: Optional[List[str]] = Field(None, description="Options for select fields")
    required: bool = Field(False, description="Whether field is required")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
    help_text: Optional[str] = Field(None, description="Help text")

    class Config:
        from_attributes = True


class TradeActivity(BaseModel):
    """
    Specific activity/service within a trade.
    
    Activities drive service templates, booking forms, and technician skills.
    """
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    trade_slug: str = Field(..., description="Parent trade profile slug")
    slug: str = Field(..., description="Unique activity slug")
    name: str = Field(..., description="Activity name")
    synonyms: List[str] = Field(default_factory=list, description="Alternative names")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    default_booking_fields: List[BookingField] = Field(default_factory=list, description="Default booking form fields")
    required_booking_fields: List[BookingField] = Field(default_factory=list, description="Required booking fields")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    def matches_search(self, query: str) -> bool:
        """Check if this activity matches a search query."""
        query_lower = query.lower()
        return (
            query_lower in self.name.lower() or
            query_lower in self.slug.lower() or
            any(query_lower in synonym.lower() for synonym in self.synonyms) or
            any(query_lower in tag.lower() for tag in self.tags)
        )

    def has_tag(self, tag: str) -> bool:
        """Check if activity has a specific tag."""
        return tag.lower() in [t.lower() for t in self.tags]

    def is_emergency(self) -> bool:
        """Check if this is an emergency activity."""
        return self.has_tag("emergency")

    def get_booking_form_schema(self) -> Dict[str, Any]:
        """Generate JSON schema for booking form."""
        schema = {
            "type": "object",
            "properties": {},
            "required": self.required_booking_fields
        }
        
        for field in self.default_booking_fields:
            field_schema = {
                "type": self._get_json_schema_type(field.type),
                "title": field.label
            }
            
            if field.placeholder:
                field_schema["description"] = field.placeholder
            
            if field.options:
                field_schema["enum"] = field.options
            
            if field.validation:
                field_schema.update(field.validation)
            
            schema["properties"][field.key] = field_schema
        
        return schema

    def _get_json_schema_type(self, field_type: BookingFieldType) -> str:
        """Convert booking field type to JSON schema type."""
        mapping = {
            BookingFieldType.TEXT: "string",
            BookingFieldType.TEXTAREA: "string",
            BookingFieldType.SELECT: "string",
            BookingFieldType.MULTISELECT: "array",
            BookingFieldType.NUMBER: "number",
            BookingFieldType.DATE: "string",
            BookingFieldType.DATETIME: "string",
            BookingFieldType.BOOLEAN: "boolean",
            BookingFieldType.FILE: "string"
        }
        return mapping.get(field_type, "string")


class ActivityServiceTemplate(BaseModel):
    """Mapping between activities and service templates."""
    
    activity_id: uuid.UUID = Field(..., description="Activity ID")
    template_slug: str = Field(..., description="Service template slug")
    is_primary: bool = Field(False, description="Primary template for this activity")
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Request/Response Models for API

class TradeProfileListRequest(BaseModel):
    """Request for listing trade profiles."""
    
    search: Optional[str] = Field(None, description="Search query")
    segments: Optional[List[MarketSegment]] = Field(None, description="Filter by market segments")
    limit: int = Field(50, ge=1, le=200, description="Maximum results")
    offset: int = Field(0, ge=0, description="Results offset")
    order_by: Optional[str] = Field("name", description="Field to order by")
    order_desc: bool = Field(False, description="Order in descending order")


class TradeActivityListRequest(BaseModel):
    """Request for listing trade activities."""
    
    trade_slug: Optional[str] = Field(None, description="Filter by trade")
    search: Optional[str] = Field(None, description="Search query")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    emergency_only: bool = Field(False, description="Only emergency activities")
    limit: int = Field(50, ge=1, le=200, description="Maximum results")
    offset: int = Field(0, ge=0, description="Results offset")
    order_by: Optional[str] = Field("name", description="Field to order by")
    order_desc: bool = Field(False, description="Order in descending order")


class TradeProfileWithActivities(TradeProfile):
    """Trade profile with its activities."""
    
    activities: List[TradeActivity] = Field(default_factory=list, description="Associated activities")
    activity_count: int = Field(0, description="Total activity count")


class ActivityWithTemplates(TradeActivity):
    """Trade activity with associated service templates."""
    
    template_slugs: List[str] = Field(default_factory=list, description="Associated template slugs")
    template_count: int = Field(0, description="Total template count")
