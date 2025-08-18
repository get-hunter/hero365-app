"""
Supabase Template Repository Implementation

Implementation of TemplateRepository using Supabase as the data store.
"""

import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from supabase import Client

from app.domain.repositories.template_repository import TemplateRepository
from app.domain.entities.template import Template, TemplateType, TemplateCategory
from app.domain.exceptions.domain_exceptions import RepositoryError


class SupabaseTemplateRepository(TemplateRepository):
    """Supabase implementation of the template repository."""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "templates"
        self.versions_table = "template_versions"
        self.cache_table = "template_cache"
    
    async def create(self, template: Template) -> Template:
        """Create a new template."""
        try:
            template_data = self._template_to_dict(template)
            
            result = self.client.table(self.table_name).insert(template_data).execute()
            
            if not result.data:
                raise RepositoryError("Failed to create template")
            
            return self._dict_to_template(result.data[0])
            
        except Exception as e:
            raise RepositoryError(f"Failed to create template: {str(e)}")
    
    async def get_by_id(self, template_id: UUID) -> Optional[Template]:
        """Get a template by ID."""
        try:
            result = self.client.table(self.table_name).select("*").eq("id", str(template_id)).execute()
            
            if not result.data:
                return None
            
            return self._dict_to_template(result.data[0])
            
        except Exception as e:
            raise RepositoryError(f"Failed to get template by ID: {str(e)}")
    
    async def get_by_business_id(
        self,
        business_id: UUID,
        template_type: Optional[TemplateType] = None,
        is_active: Optional[bool] = None
    ) -> List[Template]:
        """Get all templates for a business, optionally filtered."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if template_type:
                query = query.eq("template_type", template_type.value if hasattr(template_type, 'value') else template_type)
            
            if is_active is not None:
                query = query.eq("is_active", is_active)
            
            # Also include system templates
            system_query = self.client.table(self.table_name).select("*").eq("is_system", True)
            
            if template_type:
                system_query = system_query.eq("template_type", template_type.value if hasattr(template_type, 'value') else template_type)
            
            if is_active is not None:
                system_query = system_query.eq("is_active", is_active)
            
            # Execute both queries
            business_result = query.execute()
            system_result = system_query.execute()
            
            # Combine results
            all_templates = business_result.data + system_result.data
            
            # Remove duplicates based on ID
            seen_ids = set()
            unique_templates = []
            for template_data in all_templates:
                if template_data['id'] not in seen_ids:
                    seen_ids.add(template_data['id'])
                    unique_templates.append(template_data)
            
            return [self._dict_to_template(data) for data in unique_templates]
            
        except Exception as e:
            raise RepositoryError(f"Failed to get templates for business: {str(e)}")
    
    async def get_system_templates(
        self,
        template_type: Optional[TemplateType] = None,
        category: Optional[TemplateCategory] = None,
        is_active: Optional[bool] = None
    ) -> List[Template]:
        """Get system templates, optionally filtered."""
        try:
            query = self.client.table(self.table_name).select("*").eq("is_system", True)
            
            if template_type:
                query = query.eq("template_type", template_type.value if hasattr(template_type, 'value') else template_type)
            
            if category:
                query = query.eq("category", category.value if hasattr(category, 'value') else category)
            
            if is_active is not None:
                query = query.eq("is_active", is_active)
            
            result = query.execute()
            
            return [self._dict_to_template(data) for data in result.data]
            
        except Exception as e:
            raise RepositoryError(f"Failed to get system templates: {str(e)}")
    
    async def get_default_template(
        self,
        business_id: UUID,
        template_type: TemplateType
    ) -> Optional[Template]:
        """Get the default template for a business and type."""
        try:
            # First try to get business-specific default
            result = self.client.table(self.table_name).select("*") \
                .eq("business_id", str(business_id)) \
                .eq("template_type", template_type.value if hasattr(template_type, 'value') else template_type) \
                .eq("is_default", True) \
                .eq("is_active", True) \
                .execute()
            
            if result.data:
                return self._dict_to_template(result.data[0])
            
            # Fall back to system default
            system_result = self.client.table(self.table_name).select("*") \
                .eq("is_system", True) \
                .eq("template_type", template_type.value if hasattr(template_type, 'value') else template_type) \
                .eq("is_default", True) \
                .eq("is_active", True) \
                .execute()
            
            if system_result.data:
                return self._dict_to_template(system_result.data[0])
            
            return None
            
        except Exception as e:
            raise RepositoryError(f"Failed to get default template: {str(e)}")
    
    async def update(self, template: Template) -> Template:
        """Update an existing template."""
        try:
            template_data = self._template_to_dict(template)
            
            # Remove id from update data
            template_id = template_data.pop('id')
            
            result = self.client.table(self.table_name) \
                .update(template_data) \
                .eq("id", template_id) \
                .execute()
            
            if not result.data:
                raise RepositoryError("Failed to update template")
            
            return self._dict_to_template(result.data[0])
            
        except Exception as e:
            raise RepositoryError(f"Failed to update template: {str(e)}")
    
    async def delete(self, template_id: UUID) -> bool:
        """Delete a template by ID."""
        try:
            result = self.client.table(self.table_name) \
                .delete() \
                .eq("id", str(template_id)) \
                .execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            raise RepositoryError(f"Failed to delete template: {str(e)}")
    
    async def set_as_default(
        self,
        template_id: UUID,
        business_id: UUID,
        template_type: TemplateType
    ) -> bool:
        """Set a template as default for its type and business."""
        try:
            # Use the database function
            result = self.client.rpc(
                'set_default_template',
                {
                    'p_template_id': str(template_id),
                    'p_business_id': str(business_id),
                    'p_template_type': template_type.value if hasattr(template_type, 'value') else template_type
                }
            ).execute()
            
            return True
            
        except Exception as e:
            raise RepositoryError(f"Failed to set template as default: {str(e)}")
    
    async def increment_usage(self, template_id: UUID) -> bool:
        """Increment the usage count for a template."""
        try:
            result = self.client.rpc(
                'increment_template_usage',
                {'p_template_id': str(template_id)}
            ).execute()
            
            return True
            
        except Exception as e:
            raise RepositoryError(f"Failed to increment template usage: {str(e)}")
    
    async def search_templates(
        self,
        query: str,
        business_id: Optional[UUID] = None,
        template_type: Optional[TemplateType] = None,
        tags: Optional[List[str]] = None
    ) -> List[Template]:
        """Search templates by query, tags, or other criteria."""
        try:
            # Build search query
            search = self.client.table(self.table_name).select("*")
            
            # Add text search on name and description
            if query:
                search = search.or_(f"name.ilike.%{query}%,description.ilike.%{query}%")
            
            # Filter by business or system templates
            if business_id:
                search = search.or_(f"business_id.eq.{business_id},is_system.eq.true")
            
            # Filter by template type
            if template_type:
                search = search.eq("template_type", template_type.value if hasattr(template_type, 'value') else template_type)
            
            # Filter by tags using JSONB containment
            if tags:
                for tag in tags:
                    search = search.contains("tags", [tag])
            
            result = search.execute()
            
            return [self._dict_to_template(data) for data in result.data]
            
        except Exception as e:
            raise RepositoryError(f"Failed to search templates: {str(e)}")
    
    async def get_templates_by_usage(
        self,
        business_id: Optional[UUID] = None,
        template_type: Optional[TemplateType] = None,
        limit: int = 10
    ) -> List[Template]:
        """Get templates ordered by usage count."""
        try:
            query = self.client.table(self.table_name).select("*")
            
            if business_id:
                query = query.or_(f"business_id.eq.{business_id},is_system.eq.true")
            
            if template_type:
                query = query.eq("template_type", template_type.value if hasattr(template_type, 'value') else template_type)
            
            result = query.order("usage_count", desc=True).limit(limit).execute()
            
            return [self._dict_to_template(data) for data in result.data]
            
        except Exception as e:
            raise RepositoryError(f"Failed to get templates by usage: {str(e)}")
    
    async def get_templates_with_branding(
        self,
        branding_id: UUID
    ) -> List[Template]:
        """Get all templates using a specific branding configuration."""
        try:
            result = self.client.table(self.table_name).select("*") \
                .eq("branding_id", str(branding_id)) \
                .execute()
            
            return [self._dict_to_template(data) for data in result.data]
            
        except Exception as e:
            raise RepositoryError(f"Failed to get templates with branding: {str(e)}")
    
    async def create_version(
        self,
        template_id: UUID,
        change_notes: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> int:
        """Create a version snapshot of the template."""
        try:
            result = self.client.rpc(
                'create_template_version',
                {
                    'p_template_id': str(template_id),
                    'p_change_notes': change_notes,
                    'p_created_by': created_by
                }
            ).execute()
            
            return result.data if result.data else 1
            
        except Exception as e:
            raise RepositoryError(f"Failed to create template version: {str(e)}")
    
    async def get_version_history(
        self,
        template_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get version history for a template."""
        try:
            result = self.client.table(self.versions_table).select("*") \
                .eq("template_id", str(template_id)) \
                .order("version", desc=True) \
                .limit(limit) \
                .execute()
            
            return result.data
            
        except Exception as e:
            raise RepositoryError(f"Failed to get template version history: {str(e)}")
    
    async def restore_version(
        self,
        template_id: UUID,
        version: int
    ) -> Template:
        """Restore a template to a specific version."""
        try:
            # Get the version data
            version_result = self.client.table(self.versions_table).select("*") \
                .eq("template_id", str(template_id)) \
                .eq("version", version) \
                .execute()
            
            if not version_result.data:
                raise RepositoryError(f"Version {version} not found for template {template_id}")
            
            version_data = version_result.data[0]
            
            # Update the template with the version's config
            update_result = self.client.table(self.table_name) \
                .update({
                    "config": version_data['config'],
                    "version": version,
                    "updated_at": datetime.utcnow().isoformat()
                }) \
                .eq("id", str(template_id)) \
                .execute()
            
            if not update_result.data:
                raise RepositoryError("Failed to restore template version")
            
            return self._dict_to_template(update_result.data[0])
            
        except Exception as e:
            raise RepositoryError(f"Failed to restore template version: {str(e)}")
    
    async def cache_template(
        self,
        template_id: UUID,
        cache_key: str,
        cache_data: Dict[str, Any],
        expires_at: Optional[datetime] = None
    ) -> bool:
        """Cache processed template data."""
        try:
            cache_entry = {
                "template_id": str(template_id),
                "cache_key": cache_key,
                "cache_data": cache_data,
                "expires_at": expires_at.isoformat() if expires_at else None
            }
            
            # Upsert cache entry
            result = self.client.table(self.cache_table) \
                .upsert(cache_entry) \
                .execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            raise RepositoryError(f"Failed to cache template: {str(e)}")
    
    async def get_cached_template(
        self,
        template_id: UUID,
        cache_key: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached template data."""
        try:
            result = self.client.table(self.cache_table).select("*") \
                .eq("template_id", str(template_id)) \
                .eq("cache_key", cache_key) \
                .execute()
            
            if not result.data:
                return None
            
            cache_entry = result.data[0]
            
            # Check if expired
            if cache_entry.get('expires_at'):
                expires_at = datetime.fromisoformat(cache_entry['expires_at'])
                if expires_at < datetime.utcnow():
                    # Cache expired, delete it
                    self.client.table(self.cache_table) \
                        .delete() \
                        .eq("id", cache_entry['id']) \
                        .execute()
                    return None
            
            return cache_entry.get('cache_data')
            
        except Exception as e:
            raise RepositoryError(f"Failed to get cached template: {str(e)}")
    
    async def clear_template_cache(
        self,
        template_id: UUID,
        cache_key: Optional[str] = None
    ) -> bool:
        """Clear template cache."""
        try:
            query = self.client.table(self.cache_table).delete() \
                .eq("template_id", str(template_id))
            
            if cache_key:
                query = query.eq("cache_key", cache_key)
            
            result = query.execute()
            
            return True
            
        except Exception as e:
            raise RepositoryError(f"Failed to clear template cache: {str(e)}")
    
    async def bulk_create(
        self,
        templates: List[Template]
    ) -> List[Template]:
        """Create multiple templates in a single operation."""
        try:
            templates_data = [self._template_to_dict(t) for t in templates]
            
            result = self.client.table(self.table_name).insert(templates_data).execute()
            
            if not result.data:
                raise RepositoryError("Failed to bulk create templates")
            
            return [self._dict_to_template(data) for data in result.data]
            
        except Exception as e:
            raise RepositoryError(f"Failed to bulk create templates: {str(e)}")
    
    async def bulk_update(
        self,
        template_updates: List[Dict[str, Any]]
    ) -> List[Template]:
        """Update multiple templates in a single operation."""
        try:
            # Supabase doesn't support bulk updates directly,
            # so we need to do them one by one (could be optimized with a stored procedure)
            updated_templates = []
            
            for update in template_updates:
                template_id = update.pop('id')
                result = self.client.table(self.table_name) \
                    .update(update) \
                    .eq("id", template_id) \
                    .execute()
                
                if result.data:
                    updated_templates.append(self._dict_to_template(result.data[0]))
            
            return updated_templates
            
        except Exception as e:
            raise RepositoryError(f"Failed to bulk update templates: {str(e)}")
    
    async def get_template_analytics(
        self,
        template_id: Optional[UUID] = None,
        business_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get analytics data for templates."""
        try:
            # This would typically query the materialized view
            # For now, return basic analytics
            query = self.client.table(self.table_name).select("id, name, template_type, usage_count, last_used_at")
            
            if template_id:
                query = query.eq("id", str(template_id))
            
            if business_id:
                query = query.or_(f"business_id.eq.{business_id},is_system.eq.true")
            
            result = query.execute()
            
            analytics = {
                "total_templates": len(result.data),
                "total_usage": sum(t['usage_count'] for t in result.data),
                "templates": result.data,
                "most_used": max(result.data, key=lambda t: t['usage_count']) if result.data else None
            }
            
            return analytics
            
        except Exception as e:
            raise RepositoryError(f"Failed to get template analytics: {str(e)}")
    
    def _template_to_dict(self, template: Template) -> Dict[str, Any]:
        """Convert Template entity to database dictionary."""
        return {
            "id": str(template.id),
            "business_id": str(template.business_id) if template.business_id else None,
            "branding_id": str(template.branding_id) if template.branding_id else None,
            "template_type": template.template_type.value if hasattr(template.template_type, 'value') else template.template_type,
            "category": template.category.value if template.category and hasattr(template.category, 'value') else template.category,
            "name": template.name,
            "description": template.description,
            "version": template.version,
            "is_active": template.is_active,
            "is_default": template.is_default,
            "is_system": template.is_system,
            "config": template.config,  # JSONB field
            "usage_count": template.usage_count,
            "last_used_at": template.last_used_at.isoformat() if template.last_used_at else None,
            "tags": template.tags,
            "metadata": template.metadata,  # JSONB field
            "created_by": template.created_by,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat(),
            "updated_by": template.updated_by
        }
    
    def _dict_to_template(self, data: Dict[str, Any]) -> Template:
        """Convert database dictionary to Template entity."""
        return Template(
            id=UUID(data['id']),
            business_id=UUID(data['business_id']) if data.get('business_id') else None,
            branding_id=UUID(data['branding_id']) if data.get('branding_id') else None,
            template_type=TemplateType(data['template_type']),
            category=TemplateCategory(data['category']) if data.get('category') else None,
            name=data['name'],
            description=data.get('description'),
            version=data.get('version', 1),
            is_active=data.get('is_active', True),
            is_default=data.get('is_default', False),
            is_system=data.get('is_system', False),
            config=data.get('config', {}),
            usage_count=data.get('usage_count', 0),
            last_used_at=datetime.fromisoformat(data['last_used_at']) if data.get('last_used_at') else None,
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
            created_by=data.get('created_by'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.utcnow(),
            updated_by=data.get('updated_by')
        )
