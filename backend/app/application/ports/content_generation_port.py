"""
Content Generation Port

Interface/contract for content generation services.
Defines what the application layer expects from content generators.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass

from ...domain.entities.business import Business
from ...domain.entities.business_branding import BusinessBranding
from ...domain.entities.website import BusinessWebsite, WebsiteTemplate


@dataclass
class ContentGenerationResult:
    """Result of content generation operation."""
    
    success: bool
    content_data: Dict[str, Any]
    pages_generated: List[str]
    generation_time_seconds: float
    error_message: str = None
    warnings: List[str] = None


class ContentGenerationPort(ABC):
    """
    Port (interface) for content generation services.
    
    This defines the contract that any content generation implementation
    must follow. The application layer depends on this interface, not
    on specific implementations.
    """
    
    @abstractmethod
    async def generate_website_content(
        self,
        business: Business,
        branding: BusinessBranding,
        template: WebsiteTemplate,
        required_pages: List[str]
    ) -> ContentGenerationResult:
        """
        Generate complete website content for all required pages.
        
        Args:
            business: Business entity with trade and location info
            branding: Business branding preferences
            template: Website template to use
            required_pages: List of pages that need content
            
        Returns:
            ContentGenerationResult with generated content
        """
        pass
    
    @abstractmethod
    async def generate_page_content(
        self,
        business: Business,
        branding: BusinessBranding,
        page_type: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate content for a specific page type.
        
        Args:
            business: Business entity
            branding: Branding preferences
            page_type: Type of page (home, services, contact, etc.)
            context: Additional context for generation
            
        Returns:
            Dictionary with page content
        """
        pass
    
    @abstractmethod
    async def update_website_content(
        self,
        website: BusinessWebsite,
        business: Business,
        branding: BusinessBranding,
        content_updates: Dict[str, Any]
    ) -> ContentGenerationResult:
        """
        Update existing website content with new information.
        
        Args:
            website: Existing website entity
            business: Updated business information
            branding: Updated branding preferences
            content_updates: Specific content changes
            
        Returns:
            ContentGenerationResult with updated content
        """
        pass
    
    @abstractmethod
    async def generate_seo_content(
        self,
        business: Business,
        target_keywords: List[str],
        page_type: str
    ) -> Dict[str, Any]:
        """
        Generate SEO-optimized content for specific keywords.
        
        Args:
            business: Business entity
            target_keywords: Keywords to optimize for
            page_type: Type of page for SEO content
            
        Returns:
            Dictionary with SEO content (titles, descriptions, etc.)
        """
        pass
    
    @abstractmethod
    async def validate_content_quality(
        self,
        content: Dict[str, Any],
        business: Business
    ) -> Dict[str, Any]:
        """
        Validate the quality of generated content.
        
        Args:
            content: Generated content to validate
            business: Business context for validation
            
        Returns:
            Validation result with quality scores and issues
        """
        pass
