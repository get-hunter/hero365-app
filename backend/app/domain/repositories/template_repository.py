"""
Template Repository Interface

Abstract repository interface for the template system.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from ..entities.template import Template, TemplateType, TemplateCategory


class TemplateRepository(ABC):
    """Abstract repository for template operations."""
    
    @abstractmethod
    async def create(self, template: Template) -> Template:
        """Create a new template."""
        pass
    
    @abstractmethod
    async def get_by_id(self, template_id: UUID) -> Optional[Template]:
        """Get a template by ID."""
        pass
    
    @abstractmethod
    async def get_by_business_id(
        self,
        business_id: UUID,
        template_type: Optional[TemplateType] = None,
        is_active: Optional[bool] = None
    ) -> List[Template]:
        """Get all templates for a business, optionally filtered."""
        pass
    
    @abstractmethod
    async def get_system_templates(
        self,
        template_type: Optional[TemplateType] = None,
        category: Optional[TemplateCategory] = None,
        is_active: Optional[bool] = None
    ) -> List[Template]:
        """Get system templates, optionally filtered."""
        pass
    
    @abstractmethod
    async def get_default_template(
        self,
        business_id: UUID,
        template_type: TemplateType
    ) -> Optional[Template]:
        """Get the default template for a business and type."""
        pass
    
    @abstractmethod
    async def update(self, template: Template) -> Template:
        """Update an existing template."""
        pass
    
    @abstractmethod
    async def delete(self, template_id: UUID) -> bool:
        """Delete a template by ID."""
        pass
    
    @abstractmethod
    async def set_as_default(
        self,
        template_id: UUID,
        business_id: UUID,
        template_type: TemplateType
    ) -> bool:
        """Set a template as default for its type and business."""
        pass
    
    @abstractmethod
    async def increment_usage(self, template_id: UUID) -> bool:
        """Increment the usage count for a template."""
        pass
    
    @abstractmethod
    async def search_templates(
        self,
        query: str,
        business_id: Optional[UUID] = None,
        template_type: Optional[TemplateType] = None,
        tags: Optional[List[str]] = None
    ) -> List[Template]:
        """Search templates by query, tags, or other criteria."""
        pass
    
    @abstractmethod
    async def get_templates_by_usage(
        self,
        business_id: Optional[UUID] = None,
        template_type: Optional[TemplateType] = None,
        limit: int = 10
    ) -> List[Template]:
        """Get templates ordered by usage count."""
        pass
    
    @abstractmethod
    async def get_templates_with_branding(
        self,
        branding_id: UUID
    ) -> List[Template]:
        """Get all templates using a specific branding configuration."""
        pass
    
    @abstractmethod
    async def create_version(
        self,
        template_id: UUID,
        change_notes: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> int:
        """Create a version snapshot of the template."""
        pass
    
    @abstractmethod
    async def get_version_history(
        self,
        template_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get version history for a template."""
        pass
    
    @abstractmethod
    async def restore_version(
        self,
        template_id: UUID,
        version: int
    ) -> Template:
        """Restore a template to a specific version."""
        pass
    
    @abstractmethod
    async def cache_template(
        self,
        template_id: UUID,
        cache_key: str,
        cache_data: Dict[str, Any],
        expires_at: Optional[datetime] = None
    ) -> bool:
        """Cache processed template data."""
        pass
    
    @abstractmethod
    async def get_cached_template(
        self,
        template_id: UUID,
        cache_key: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached template data."""
        pass
    
    @abstractmethod
    async def clear_template_cache(
        self,
        template_id: UUID,
        cache_key: Optional[str] = None
    ) -> bool:
        """Clear template cache."""
        pass
    
    @abstractmethod
    async def bulk_create(
        self,
        templates: List[Template]
    ) -> List[Template]:
        """Create multiple templates in a single operation."""
        pass
    
    @abstractmethod
    async def bulk_update(
        self,
        template_updates: List[Dict[str, Any]]
    ) -> List[Template]:
        """Update multiple templates in a single operation."""
        pass
    
    @abstractmethod
    async def get_template_analytics(
        self,
        template_id: Optional[UUID] = None,
        business_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get analytics data for templates."""
        pass
