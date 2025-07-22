"""
Estimate Template Repository Interface

Defines the contract for estimate template data access operations.
Follows the Repository pattern for clean architecture.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from ..entities.estimate_template import EstimateTemplate
from ..shared.enums import TemplateType


class EstimateTemplateRepository(ABC):
    """
    Abstract repository interface for estimate template data access operations.
    
    Defines all methods needed for template management without
    specifying implementation details.
    """
    
    @abstractmethod
    async def create(self, template: EstimateTemplate) -> EstimateTemplate:
        """Create a new estimate template."""
        pass
    
    @abstractmethod
    async def get_by_id(self, template_id: uuid.UUID) -> Optional[EstimateTemplate]:
        """Get template by ID."""
        pass
    
    @abstractmethod
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[EstimateTemplate]:
        """Get templates by business ID with pagination."""
        pass
    
    @abstractmethod
    async def get_by_name(self, business_id: uuid.UUID, name: str) -> Optional[EstimateTemplate]:
        """Get template by name within a business."""
        pass
    
    @abstractmethod
    async def get_by_type(self, business_id: uuid.UUID, template_type: TemplateType,
                         skip: int = 0, limit: int = 100) -> List[EstimateTemplate]:
        """Get templates by type within a business."""
        pass
    
    @abstractmethod
    async def get_active_templates(self, business_id: uuid.UUID,
                                  skip: int = 0, limit: int = 100) -> List[EstimateTemplate]:
        """Get active templates within a business."""
        pass
    
    @abstractmethod
    async def get_default_template(self, business_id: uuid.UUID) -> Optional[EstimateTemplate]:
        """Get the default template for a business."""
        pass
    
    @abstractmethod
    async def get_most_used_templates(self, business_id: uuid.UUID, limit: int = 10) -> List[EstimateTemplate]:
        """Get most frequently used templates within a business."""
        pass
    
    @abstractmethod
    async def search_templates(self, business_id: uuid.UUID, search_term: str,
                              skip: int = 0, limit: int = 100) -> List[EstimateTemplate]:
        """Search templates within a business by name or description."""
        pass
    
    @abstractmethod
    async def get_by_created_user(self, business_id: uuid.UUID, user_id: str,
                                 skip: int = 0, limit: int = 100) -> List[EstimateTemplate]:
        """Get templates created by a specific user within a business."""
        pass
    
    @abstractmethod
    async def update(self, template: EstimateTemplate) -> EstimateTemplate:
        """Update an existing template."""
        pass
    
    @abstractmethod
    async def delete(self, template_id: uuid.UUID) -> bool:
        """Delete a template by ID."""
        pass
    
    @abstractmethod
    async def clone_template(self, template_id: uuid.UUID, new_name: str, business_id: uuid.UUID) -> EstimateTemplate:
        """Clone an existing template with a new name."""
        pass
    
    @abstractmethod
    async def set_default_template(self, business_id: uuid.UUID, template_id: uuid.UUID) -> bool:
        """Set a template as the default for a business."""
        pass
    
    @abstractmethod
    async def activate_template(self, template_id: uuid.UUID) -> bool:
        """Activate a template."""
        pass
    
    @abstractmethod
    async def deactivate_template(self, template_id: uuid.UUID) -> bool:
        """Deactivate a template."""
        pass
    
    @abstractmethod
    async def increment_usage_count(self, template_id: uuid.UUID) -> bool:
        """Increment the usage count for a template."""
        pass
    
    @abstractmethod
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """Count total templates for a business."""
        pass
    
    @abstractmethod
    async def count_by_type(self, business_id: uuid.UUID, template_type: TemplateType) -> int:
        """Count templates by type within a business."""
        pass
    
    @abstractmethod
    async def count_active_templates(self, business_id: uuid.UUID) -> int:
        """Count active templates within a business."""
        pass
    
    @abstractmethod
    async def get_template_statistics(self, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive template statistics for a business."""
        pass
    
    @abstractmethod
    async def get_usage_analytics(self, template_id: uuid.UUID) -> Dict[str, Any]:
        """Get usage analytics for a specific template."""
        pass
    
    @abstractmethod
    async def exists(self, template_id: uuid.UUID) -> bool:
        """Check if a template exists."""
        pass
    
    @abstractmethod
    async def has_duplicate_name(self, business_id: uuid.UUID, name: str,
                                exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if template name already exists within business."""
        pass
    
    @abstractmethod
    async def is_in_use(self, template_id: uuid.UUID) -> bool:
        """Check if a template is currently being used by estimates."""
        pass
    
    @abstractmethod
    async def get_estimates_using_template(self, template_id: uuid.UUID) -> int:
        """Get count of estimates using a specific template."""
        pass 