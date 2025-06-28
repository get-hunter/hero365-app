"""
Address Utilities

Shared utilities for address handling across Hero365 application.
Provides common address operations, validation, and conversion helpers.
"""

from typing import Optional, Dict, Any, Union
import json
import logging
from ..dto.contact_dto import ContactAddressDTO
from ..dto.job_dto import JobAddressDTO
from ...domain.value_objects.address import Address

logger = logging.getLogger(__name__)


class AddressUtils:
    """Shared utilities for address handling across Hero365."""
    
    @staticmethod
    def parse_address_from_jsonb(address_data: Union[str, Dict[str, Any], None]) -> Optional[Address]:
        """
        Parse address from JSONB database field into Address value object.
        
        Args:
            address_data: JSONB data from database (string or dict)
            
        Returns:
            Address value object or None if parsing fails
        """
        if not address_data:
            return None
            
        try:
            # Handle string JSON
            if isinstance(address_data, str):
                if address_data.strip() in ['{}', '']:
                    return None
                parsed_data = json.loads(address_data)
            else:
                parsed_data = address_data
            
            # Check if we have meaningful address data
            if not parsed_data or not any(
                parsed_data.get(field) for field in ['street_address', 'city', 'state', 'postal_code']
            ):
                return None
            
            return Address.from_dict(parsed_data)
            
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.warning(f"Failed to parse address JSONB: {str(e)}")
            return None
    
    @staticmethod
    def parse_address_to_contact_dto(address_data: Union[str, Dict[str, Any], None]) -> Optional[ContactAddressDTO]:
        """
        Parse address from JSONB into ContactAddressDTO.
        
        Args:
            address_data: JSONB data from database
            
        Returns:
            ContactAddressDTO or None if parsing fails
        """
        address = AddressUtils.parse_address_from_jsonb(address_data)
        if not address:
            return None
            
        return ContactAddressDTO(
            street_address=address.street_address,
            city=address.city,
            state=address.state,
            postal_code=address.postal_code,
            country=address.country,
            latitude=address.latitude,
            longitude=address.longitude,
            access_notes=address.access_notes,
            place_id=address.place_id,
            formatted_address=address.formatted_address,
            address_type=address.address_type
        )
    
    @staticmethod
    def parse_address_to_job_dto(address_data: Union[str, Dict[str, Any], None]) -> Optional[JobAddressDTO]:
        """
        Parse address from JSONB into JobAddressDTO.
        
        Args:
            address_data: JSONB data from database
            
        Returns:
            JobAddressDTO or None if parsing fails
        """
        address = AddressUtils.parse_address_from_jsonb(address_data)
        if not address:
            return None
            
        return JobAddressDTO(
            street_address=address.street_address,
            city=address.city,
            state=address.state,
            postal_code=address.postal_code,
            country=address.country,
            latitude=address.latitude,
            longitude=address.longitude,
            access_notes=address.access_notes,
            place_id=address.place_id,
            formatted_address=address.formatted_address,
            address_type=address.address_type
        )
    
    @staticmethod
    def address_to_dict(address: Address) -> Dict[str, Any]:
        """
        Convert Address value object to dictionary for database storage.
        
        Args:
            address: Address value object
            
        Returns:
            Dictionary ready for JSONB storage
        """
        return address.to_dict()
    
    @staticmethod
    def address_to_json(address: Address) -> str:
        """
        Convert Address value object to JSON string for database storage.
        
        Args:
            address: Address value object
            
        Returns:
            JSON string ready for JSONB storage
        """
        return address.to_json()
    
    @staticmethod
    def create_minimal_address(street_address: str, city: str, state: str, 
                              postal_code: str, country: str = "US") -> Address:
        """
        Create a minimal address with just the required fields.
        
        Args:
            street_address: Street address
            city: City name
            state: State/province
            postal_code: Postal/ZIP code
            country: Country code (default: US)
            
        Returns:
            Address value object
        """
        return Address.create_minimal(
            street_address=street_address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country
        )
    
    @staticmethod
    def create_geocoded_address(street_address: str, city: str, state: str, 
                               postal_code: str, latitude: float, longitude: float,
                               country: str = "US", access_notes: Optional[str] = None,
                               place_id: Optional[str] = None,
                               formatted_address: Optional[str] = None) -> Address:
        """
        Create an address with geocoding information.
        
        Args:
            street_address: Street address
            city: City name
            state: State/province
            postal_code: Postal/ZIP code
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            country: Country code (default: US)
            access_notes: Optional access notes for field service
            place_id: Optional Google Places ID
            formatted_address: Optional formatted address from geocoding service
            
        Returns:
            Address value object with geocoding data
        """
        return Address(
            street_address=street_address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            latitude=latitude,
            longitude=longitude,
            access_notes=access_notes,
            place_id=place_id,
            formatted_address=formatted_address
        )
    
    @staticmethod
    def validate_address_completeness(address: Address) -> bool:
        """
        Validate if address has minimum required information.
        
        Args:
            address: Address value object
            
        Returns:
            True if address is complete
        """
        return address.is_complete()
    
    @staticmethod
    def validate_address_geocoding(address: Address) -> bool:
        """
        Validate if address has geocoding coordinates.
        
        Args:
            address: Address value object
            
        Returns:
            True if address has coordinates
        """
        return address.has_coordinates()
    
    @staticmethod
    def get_address_display_formats(address: Address) -> Dict[str, str]:
        """
        Get various display formats for an address.
        
        Args:
            address: Address value object
            
        Returns:
            Dictionary with different address formats
        """
        return {
            "full": address.get_full_address(),
            "short": address.get_short_address(),
            "street_city": f"{address.street_address}, {address.city}",
            "city_state": f"{address.city}, {address.state}",
            "state_zip": f"{address.state} {address.postal_code}"
        }
    
    @staticmethod
    def merge_address_data(existing_address: Optional[Address], 
                          update_data: Dict[str, Any]) -> Address:
        """
        Merge existing address with update data.
        
        Args:
            existing_address: Current address value object
            update_data: Dictionary with updated address fields
            
        Returns:
            New Address value object with merged data
        """
        # Start with existing data or empty dict
        merged_data = existing_address.to_dict() if existing_address else {}
        
        # Update with new data (only non-None values)
        for key, value in update_data.items():
            if value is not None:
                merged_data[key] = value
        
        return Address.from_dict(merged_data) 