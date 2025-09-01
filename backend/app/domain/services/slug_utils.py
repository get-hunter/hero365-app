"""
Slug Utilities
Standardized slug generation and normalization
"""

import re
from typing import List


class SlugUtils:
    """Utilities for slug generation and normalization."""
    
    @staticmethod
    def normalize_service_slug(service_key: str) -> str:
        """
        Normalize a service key to kebab-case slug.
        
        Args:
            service_key: Service key (e.g., 'hvac_repair', 'emergency_plumbing')
            
        Returns:
            Kebab-case slug (e.g., 'hvac-repair', 'emergency-plumbing')
        """
        if not service_key:
            return ""
        
        # Convert underscores to hyphens
        slug = service_key.replace('_', '-')
        
        # Convert to lowercase
        slug = slug.lower()
        
        # Remove any non-alphanumeric characters except hyphens
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        return slug
    
    @staticmethod
    def normalize_business_slug(business_name: str) -> str:
        """
        Generate a slug from business name.
        
        Args:
            business_name: Business name (e.g., 'Elite HVAC Austin')
            
        Returns:
            Kebab-case slug (e.g., 'elite-hvac-austin')
        """
        if not business_name:
            return ""
        
        # Convert to lowercase
        slug = business_name.lower()
        
        # Replace spaces and special characters with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        return slug
    
    @staticmethod
    def batch_normalize_service_slugs(service_keys: List[str]) -> List[str]:
        """
        Normalize a batch of service keys to kebab-case slugs.
        
        Args:
            service_keys: List of service keys
            
        Returns:
            List of normalized kebab-case slugs
        """
        return [SlugUtils.normalize_service_slug(key) for key in service_keys]
    
    @staticmethod
    def service_key_to_display_name(service_key: str) -> str:
        """
        Convert service key to display name.
        
        Args:
            service_key: Service key (e.g., 'hvac_repair', 'emergency_plumbing')
            
        Returns:
            Display name (e.g., 'HVAC Repair', 'Emergency Plumbing')
        """
        if not service_key:
            return ""
        
        # Split on underscores and capitalize each word
        words = service_key.split('_')
        display_words = []
        
        for word in words:
            # Handle special cases
            if word.lower() == 'hvac':
                display_words.append('HVAC')
            elif word.lower() == 'ac':
                display_words.append('AC')
            elif word.lower() == 'iaq':
                display_words.append('IAQ')
            else:
                display_words.append(word.capitalize())
        
        return ' '.join(display_words)
    
    @staticmethod
    def normalize_location_slug(location_text: str) -> str:
        """
        Normalize location text to slug format.
        
        Args:
            location_text: Location text (e.g., 'Austin, TX', 'New York City')
            
        Returns:
            Location slug (e.g., 'austin-tx', 'new-york-city')
        """
        if not location_text:
            return ""
        
        # Remove common separators and normalize
        slug = location_text.lower()
        slug = re.sub(r'[,\s]+', '-', slug)  # Replace commas and spaces with hyphens
        slug = re.sub(r'[^a-z0-9\-]', '', slug)  # Remove non-alphanumeric except hyphens
        slug = re.sub(r'-+', '-', slug)  # Collapse multiple hyphens
        slug = slug.strip('-')  # Remove leading/trailing hyphens
        
        return slug
