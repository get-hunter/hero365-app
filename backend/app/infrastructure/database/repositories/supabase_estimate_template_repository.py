"""
Supabase Estimate Template Repository Implementation
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from supabase import Client

from app.domain.repositories.estimate_template_repository import EstimateTemplateRepository
from app.domain.entities.estimate_template import EstimateTemplate
from app.domain.shared.enums import TemplateType
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, DuplicateEntityError, DatabaseError

logger = logging.getLogger(__name__)

class SupabaseEstimateTemplateRepository(EstimateTemplateRepository):
    """Supabase implementation of EstimateTemplateRepository."""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "estimate_templates"
    
    async def create(self, template: EstimateTemplate) -> EstimateTemplate:
        """Create a new estimate template."""
        try:
            template_data = {
                "id": str(template.id),
                "business_id": str(template.business_id) if template.business_id else None,
                "name": template.name,
                "description": template.description,
                "template_type": template.template_type.value,
                "is_active": template.is_active,
                "is_default": template.is_default,
                "is_system_template": template.is_system_template,
                "usage_count": template.usage_count,
                "tags": template.tags,
                "category": template.category,
                "version": template.version,
                "created_by": template.created_by,
                "created_date": template.created_date.isoformat(),
                "last_modified": template.last_modified.isoformat()
            }
            
            response = self.client.table(self.table_name).insert(template_data).execute()
            
            if response.data:
                return self._dict_to_template(response.data[0])
            else:
                raise DatabaseError("Failed to create template")
                
        except Exception as e:
            if "duplicate key" in str(e).lower():
                raise DuplicateEntityError(f"Template with name '{template.name}' already exists")
            raise DatabaseError(f"Failed to create template: {str(e)}")
    
    async def get_by_id(self, template_id: uuid.UUID) -> Optional[EstimateTemplate]:
        """Get template by ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq("id", str(template_id)).execute()
            
            if response.data:
                return self._dict_to_template(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get template by ID: {str(e)}")
    
    def _dict_to_template(self, data: dict) -> EstimateTemplate:
        """Convert dictionary to EstimateTemplate."""
        def safe_uuid_parse(value):
            if value is None:
                return None
            try:
                return uuid.UUID(value)
            except (ValueError, TypeError):
                return None
        
        def safe_datetime_parse(value):
            if value is None:
                return None
            try:
                if isinstance(value, str):
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                return value
            except (ValueError, TypeError):
                return None
        
        return EstimateTemplate(
            id=uuid.UUID(data["id"]),
            business_id=safe_uuid_parse(data.get("business_id")),
            name=data.get("name", ""),
            description=data.get("description"),
            template_type=TemplateType(data.get("template_type", "professional")),
            is_active=data.get("is_active", True),
            is_default=data.get("is_default", False),
            is_system_template=data.get("is_system_template", False),
            usage_count=data.get("usage_count", 0),
            tags=data.get("tags", []),
            category=data.get("category"),
            version=data.get("version", "1.0"),
            created_by=data.get("created_by"),
            created_date=safe_datetime_parse(data["created_date"]) or datetime.now(),
            last_modified=safe_datetime_parse(data["last_modified"]) or datetime.now()
        )

    # Basic implementations for remaining methods
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[EstimateTemplate]:
        return []

    async def get_by_name(self, business_id: uuid.UUID, name: str) -> Optional[EstimateTemplate]:
        return None

    async def get_by_type(self, business_id: uuid.UUID, template_type: TemplateType, skip: int = 0, limit: int = 100) -> List[EstimateTemplate]:
        return []

    async def get_active_templates(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[EstimateTemplate]:
        return []

    async def get_default_template(self, business_id: uuid.UUID) -> Optional[EstimateTemplate]:
        return None

    async def get_most_used_templates(self, business_id: uuid.UUID, limit: int = 10) -> List[EstimateTemplate]:
        return []

    async def search_templates(self, business_id: uuid.UUID, search_term: str, skip: int = 0, limit: int = 100) -> List[EstimateTemplate]:
        return []

    async def get_by_created_user(self, business_id: uuid.UUID, user_id: str, skip: int = 0, limit: int = 100) -> List[EstimateTemplate]:
        return []

    async def update(self, template: EstimateTemplate) -> EstimateTemplate:
        return template

    async def delete(self, template_id: uuid.UUID) -> bool:
        return True

    async def clone_template(self, template_id: uuid.UUID, new_name: str, business_id: uuid.UUID) -> EstimateTemplate:
        template = await self.get_by_id(template_id)
        if not template:
            raise EntityNotFoundError(f"Template with ID {template_id} not found")
        return template.clone(new_name, business_id)

    async def set_default_template(self, business_id: uuid.UUID, template_id: uuid.UUID) -> bool:
        return True

    async def activate_template(self, template_id: uuid.UUID) -> bool:
        return True

    async def deactivate_template(self, template_id: uuid.UUID) -> bool:
        return True

    async def increment_usage_count(self, template_id: uuid.UUID) -> bool:
        return True

    async def count_by_business(self, business_id: uuid.UUID) -> int:
        return 0

    async def count_by_type(self, business_id: uuid.UUID, template_type: TemplateType) -> int:
        return 0

    async def count_active_templates(self, business_id: uuid.UUID) -> int:
        return 0

    async def get_template_statistics(self, business_id: uuid.UUID) -> Dict[str, Any]:
        return {}

    async def get_usage_analytics(self, template_id: uuid.UUID) -> Dict[str, Any]:
        return {}

    async def exists(self, template_id: uuid.UUID) -> bool:
        return False

    async def has_duplicate_name(self, business_id: uuid.UUID, name: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
        return False

    async def is_in_use(self, template_id: uuid.UUID) -> bool:
        return False

    async def get_estimates_using_template(self, template_id: uuid.UUID) -> int:
        return 0
