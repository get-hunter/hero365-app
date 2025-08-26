"""
Service Areas Domain Entities
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import re


class ServiceAreaBase(BaseModel):
    """Base service area model"""
    postal_code: str = Field(..., min_length=3, max_length=10, description="Postal/ZIP code")
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    city: Optional[str] = Field(None, max_length=100, description="City name")
    region: Optional[str] = Field(None, max_length=100, description="State/Province")
    timezone: str = Field(default="America/New_York", description="IANA timezone identifier")
    is_active: bool = Field(default=True, description="Whether this service area is active")
    dispatch_fee_cents: int = Field(default=0, ge=0, description="Dispatch fee in cents")
    min_response_time_hours: int = Field(default=2, ge=0, le=168, description="Minimum response time in hours")
    max_response_time_hours: int = Field(default=24, ge=0, le=168, description="Maximum response time in hours")
    emergency_services_available: bool = Field(default=True, description="Emergency services available")
    regular_services_available: bool = Field(default=True, description="Regular services available")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")

    @validator('country_code')
    def validate_country_code(cls, v):
        if v and not re.match(r'^[A-Z]{2}$', v.upper()):
            raise ValueError('Country code must be 2 uppercase letters')
        return v.upper()

    @validator('postal_code')
    def validate_postal_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Postal code is required')
        # Basic validation - can be enhanced per country
        cleaned = re.sub(r'[^A-Za-z0-9]', '', v.upper())
        if len(cleaned) < 3:
            raise ValueError('Postal code too short')
        return cleaned

    @validator('timezone')
    def validate_timezone(cls, v):
        # Basic timezone validation - could use pytz for full validation
        if not v or '/' not in v:
            raise ValueError('Invalid timezone format')
        return v


class ServiceAreaCreate(ServiceAreaBase):
    """Service area creation model"""
    business_id: str = Field(..., description="Business UUID")


class ServiceAreaUpdate(BaseModel):
    """Service area update model"""
    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = None
    is_active: Optional[bool] = None
    dispatch_fee_cents: Optional[int] = Field(None, ge=0)
    min_response_time_hours: Optional[int] = Field(None, ge=0, le=168)
    max_response_time_hours: Optional[int] = Field(None, ge=0, le=168)
    emergency_services_available: Optional[bool] = None
    regular_services_available: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)


class ServiceArea(ServiceAreaBase):
    """Complete service area model with database fields"""
    id: str = Field(..., description="Service area UUID")
    business_id: str = Field(..., description="Business UUID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ServiceAreaBulkUpsert(BaseModel):
    """Bulk upsert request for service areas"""
    business_id: str = Field(..., description="Business UUID")
    areas: List[ServiceAreaBase] = Field(..., min_items=1, max_items=1000, description="Service areas to upsert")


class ServiceAreaCheckRequest(BaseModel):
    """Request to check if a postal code is supported"""
    business_id: str = Field(..., description="Business UUID")
    postal_code: str = Field(..., min_length=3, max_length=10, description="Postal/ZIP code to check")
    country_code: str = Field(default="US", min_length=2, max_length=2, description="Country code")

    @validator('country_code')
    def validate_country_code(cls, v):
        return v.upper()

    @validator('postal_code')
    def validate_postal_code(cls, v):
        return re.sub(r'[^A-Za-z0-9]', '', v.upper())


class ServiceAreaCheckResponse(BaseModel):
    """Response for service area check"""
    supported: bool = Field(..., description="Whether the postal code is supported")
    normalized: Optional['NormalizedLocation'] = Field(None, description="Normalized location data")
    suggestions: Optional[List['ServiceAreaSuggestion']] = Field(None, description="Nearby service areas")
    message: Optional[str] = Field(None, description="Human-readable message")


class NormalizedLocation(BaseModel):
    """Normalized location information"""
    postal_code: str = Field(..., description="Normalized postal code")
    country_code: str = Field(..., description="Country code")
    city: Optional[str] = Field(None, description="City name")
    region: Optional[str] = Field(None, description="State/Province")
    timezone: str = Field(..., description="IANA timezone")
    dispatch_fee_cents: int = Field(default=0, description="Dispatch fee in cents")
    min_response_time_hours: int = Field(..., description="Minimum response time")
    max_response_time_hours: int = Field(..., description="Maximum response time")
    emergency_available: bool = Field(..., description="Emergency services available")
    regular_available: bool = Field(..., description="Regular services available")


class ServiceAreaSuggestion(BaseModel):
    """Suggested nearby service area"""
    postal_code: str = Field(..., description="Postal code")
    city: Optional[str] = Field(None, description="City name")
    region: Optional[str] = Field(None, description="State/Province")
    distance_estimate: str = Field(..., description="Distance estimate (e.g., 'nearby', '10 miles')")


class AvailabilityRequestBase(BaseModel):
    """Base availability request model"""
    contact_name: str = Field(..., min_length=1, max_length=100, description="Contact person name")
    phone_e164: Optional[str] = Field(None, description="Phone in E.164 format (+1234567890)")
    email: Optional[str] = Field(None, description="Email address")
    postal_code: str = Field(..., min_length=3, max_length=10, description="Requested postal code")
    country_code: str = Field(default="US", min_length=2, max_length=2, description="Country code")
    city: Optional[str] = Field(None, max_length=100, description="City name")
    region: Optional[str] = Field(None, max_length=100, description="State/Province")
    service_category: Optional[str] = Field(None, max_length=50, description="Service category (HVAC, Plumbing, etc.)")
    service_type: Optional[str] = Field(None, max_length=100, description="Specific service type")
    urgency_level: str = Field(default="normal", description="Urgency level")
    preferred_contact_method: str = Field(default="phone", description="Preferred contact method")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional details")

    @validator('urgency_level')
    def validate_urgency_level(cls, v):
        allowed = ['emergency', 'urgent', 'normal', 'flexible']
        if v not in allowed:
            raise ValueError(f'Urgency level must be one of: {allowed}')
        return v

    @validator('preferred_contact_method')
    def validate_contact_method(cls, v):
        allowed = ['phone', 'email', 'sms']
        if v not in allowed:
            raise ValueError(f'Contact method must be one of: {allowed}')
        return v

    @validator('phone_e164')
    def validate_phone_e164(cls, v):
        if v and not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Phone must be in E.164 format (+1234567890)')
        return v

    @validator('email')
    def validate_email(cls, v):
        if v and not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v.lower() if v else v

    @validator('country_code')
    def validate_country_code(cls, v):
        return v.upper()

    @validator('postal_code')
    def validate_postal_code(cls, v):
        return re.sub(r'[^A-Za-z0-9]', '', v.upper())


class AvailabilityRequestCreate(AvailabilityRequestBase):
    """Availability request creation model"""
    business_id: str = Field(..., description="Business UUID")
    source: str = Field(default="booking_widget", description="Request source")
    referrer_url: Optional[str] = Field(None, max_length=500, description="Referrer URL")
    user_agent: Optional[str] = Field(None, max_length=500, description="User agent string")


class AvailabilityRequest(AvailabilityRequestBase):
    """Complete availability request model"""
    id: str = Field(..., description="Request UUID")
    business_id: str = Field(..., description="Business UUID")
    status: str = Field(..., description="Request status")
    source: str = Field(..., description="Request source")
    referrer_url: Optional[str] = Field(None, description="Referrer URL")
    user_agent: Optional[str] = Field(None, description="User agent string")
    contacted_at: Optional[datetime] = Field(None, description="When contact was attempted")
    converted_at: Optional[datetime] = Field(None, description="When converted to booking")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class AvailabilityRequestResponse(BaseModel):
    """Response for availability request creation"""
    created: bool = Field(..., description="Whether request was created")
    id: str = Field(..., description="Request UUID")
    message: str = Field(default="Request submitted successfully", description="Success message")


# Update forward references
ServiceAreaCheckResponse.model_rebuild()
