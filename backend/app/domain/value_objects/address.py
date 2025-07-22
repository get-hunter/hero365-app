"""
Address Value Object

Unified address representation for Hero365 domain entities.
Supports rich address data including geocoding and access information.
"""

from typing import Optional, Dict, Any
import json
from pydantic import BaseModel, Field, validator
from ..exceptions.domain_exceptions import DomainValidationError


class Address(BaseModel):
    """
    Unified address value object for all Hero365 entities.
    
    Designed to support:
    - Basic address components
    - Geocoding results (latitude/longitude)
    - Access information for field service
    - International address formats
    - Google Places integration
    """
    
    # Core address components
    street_address: str = Field(..., min_length=1, description="Street address")
    city: str = Field(..., min_length=1, description="City")
    state: str = Field(..., min_length=1, description="State/Province")
    postal_code: str = Field(..., min_length=1, description="Postal/ZIP code")
    country: str = Field(default="US", description="Country code")
    
    # Geocoding and location data
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    
    # Field service specific
    access_notes: Optional[str] = Field(None, description="Access instructions")
    
    # External service integration
    place_id: Optional[str] = Field(None, description="Google Places ID")
    formatted_address: Optional[str] = Field(None, description="Full formatted address")
    
    # Additional metadata
    address_type: Optional[str] = Field(None, description="Address type (residential, commercial, etc.)")

    @validator('street_address', 'city', 'state', 'postal_code')
    def validate_required_fields(cls, v):
        """Validate required fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Address field cannot be empty")
        return v.strip()

    def get_full_address(self) -> str:
        """Get formatted full address."""
        if self.formatted_address:
            return self.formatted_address
        
        parts = [self.street_address, self.city, f"{self.state} {self.postal_code}"]
        if self.country != "US":
            parts.append(self.country)
        
        return ", ".join(parts)
    
    def get_short_address(self) -> str:
        """Get short address for display."""
        return f"{self.city}, {self.state}"
    
    def has_coordinates(self) -> bool:
        """Check if address has geocoding coordinates."""
        return self.latitude is not None and self.longitude is not None
    
    def is_complete(self) -> bool:
        """Check if address has minimum required information."""
        return bool(
            self.street_address and 
            self.city and 
            self.state and 
            self.postal_code
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return self.model_dump(exclude_none=True)
    
    def to_json(self) -> str:
        """Convert to JSON string for database storage."""
        return self.model_dump_json(exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Address':
        """Create Address from dictionary."""
        if not data:
            raise ValueError("Address data cannot be empty")
        
        return cls.model_validate(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Address':
        """Create Address from JSON string."""
        try:
            if isinstance(json_str, str):
                return cls.model_validate_json(json_str)
            else:
                return cls.model_validate(json_str)
        except Exception as e:
            raise ValueError(f"Invalid address JSON: {e}")
    
    @classmethod
    def create_minimal(cls, street_address: str, city: str, state: str, postal_code: str, country: str = "US") -> 'Address':
        """Create a minimal address with just the required fields."""
        return cls(
            street_address=street_address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country
        )
    
    def __str__(self) -> str:
        """String representation of the address."""
        return self.get_full_address()
    
    def __repr__(self) -> str:
        """Developer representation of the address."""
        return f"Address(street_address='{self.street_address}', city='{self.city}', state='{self.state}')"

    model_config = {
        "frozen": True,  # Equivalent to dataclass(frozen=True)
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "json_encoders": {
            float: lambda v: round(v, 6) if v else None
        }
    } 