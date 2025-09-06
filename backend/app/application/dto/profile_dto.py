"""
Profile Data Transfer Objects

DTOs for profile-related data transfer between application layers.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class BusinessProfileDTO(BaseModel):
    """DTO for business profile information."""
    
    id: str = Field(..., description="Business ID")
    name: str = Field(..., description="Business name")
    industry: Optional[str] = Field(None, description="Business industry")
    description: Optional[str] = Field(None, description="Business description")
    
    # Contact information
    phone_number: Optional[str] = Field(None, description="Business phone")
    business_email: Optional[str] = Field(None, description="Business email")
    business_address: Optional[str] = Field(None, description="Business address")
    city: Optional[str] = Field(None, description="Business city")
    state: Optional[str] = Field(None, description="Business state")
    postal_code: Optional[str] = Field(None, description="Business postal code")
    website: Optional[str] = Field(None, description="Business website")
    
    # Service information
    service_areas: List[str] = Field(default_factory=list, description="Service areas")
    trades: List[str] = Field(default_factory=list, description="Business trades")
    
    # Business details
    business_license: Optional[str] = Field(None, description="License number")
    years_in_business: Optional[int] = Field(None, description="Years in business")
    
    # Status
    is_active: bool = Field(True, description="Business is active")
    is_verified: bool = Field(False, description="Business is verified")


class ProfileSummaryDTO(BaseModel):
    """DTO for profile summary information."""
    
    business_id: str = Field(..., description="Business ID")
    business_name: str = Field(..., description="Business name")
    primary_trade: Optional[str] = Field(None, description="Primary trade")
    service_area_count: int = Field(0, description="Number of service areas")
    is_emergency_available: bool = Field(False, description="Emergency service available")
