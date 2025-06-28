"""
Address Value Object

Unified address representation for Hero365 domain entities.
Supports rich address data including geocoding and access information.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import json
from ..exceptions.domain_exceptions import DomainValidationError


@dataclass(frozen=True)
class Address:
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
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str = "US"
    
    # Geocoding and location data
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Field service specific
    access_notes: Optional[str] = None
    
    # External service integration
    place_id: Optional[str] = None  # Google Places ID
    formatted_address: Optional[str] = None  # Full formatted address
    
    # Additional metadata
    address_type: Optional[str] = None  # 'residential', 'commercial', etc.
    
    def __post_init__(self):
        """Validate address data."""
        if not self.street_address or not self.street_address.strip():
            raise DomainValidationError("Street address is required")
        if not self.city or not self.city.strip():
            raise DomainValidationError("City is required")
        if not self.state or not self.state.strip():
            raise DomainValidationError("State is required")
        if not self.postal_code or not self.postal_code.strip():
            raise DomainValidationError("Postal code is required")
        
        # Validate coordinates if provided
        if self.latitude is not None:
            if not (-90 <= self.latitude <= 90):
                raise DomainValidationError("Latitude must be between -90 and 90")
        
        if self.longitude is not None:
            if not (-180 <= self.longitude <= 180):
                raise DomainValidationError("Longitude must be between -180 and 180")
    
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
        result = {
            "street_address": self.street_address,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
        }
        
        # Only include optional fields if they have values
        if self.latitude is not None:
            result["latitude"] = self.latitude
        if self.longitude is not None:
            result["longitude"] = self.longitude
        if self.access_notes:
            result["access_notes"] = self.access_notes
        if self.place_id:
            result["place_id"] = self.place_id
        if self.formatted_address:
            result["formatted_address"] = self.formatted_address
        if self.address_type:
            result["address_type"] = self.address_type
        
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string for database storage."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Address':
        """Create Address from dictionary."""
        if not data:
            raise ValueError("Address data cannot be empty")
        
        return cls(
            street_address=data.get("street_address", ""),
            city=data.get("city", ""),
            state=data.get("state", ""),
            postal_code=data.get("postal_code", ""),
            country=data.get("country", "US"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            access_notes=data.get("access_notes"),
            place_id=data.get("place_id"),
            formatted_address=data.get("formatted_address"),
            address_type=data.get("address_type")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Address':
        """Create Address from JSON string."""
        try:
            data = json.loads(json_str) if isinstance(json_str, str) else json_str
            return cls.from_dict(data)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
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