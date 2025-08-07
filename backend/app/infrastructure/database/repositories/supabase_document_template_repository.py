"""
Supabase Document Template Repository Implementation

Implementation of DocumentTemplateRepository using Supabase as the data store.
"""

import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from supabase import Client

from app.domain.repositories.document_template_repository import DocumentTemplateRepository
from app.domain.entities.document_template import DocumentTemplate, DocumentType, DocumentSections
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, RepositoryError


class SupabaseDocumentTemplateRepository(DocumentTemplateRepository):
    """Supabase implementation of DocumentTemplateRepository."""

    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "document_templates"

    async def create(self, template: DocumentTemplate) -> DocumentTemplate:
        """Create a new document template."""
        try:
            template_data = self._template_to_dict(template)
            
            result = self.client.table(self.table_name).insert(template_data).execute()
            
            if not result.data:
                raise RepositoryError("Failed to create document template")
            
            return self._dict_to_template(result.data[0])
            
        except Exception as e:
            raise RepositoryError(f"Failed to create document template: {str(e)}")

    async def get_by_id(self, template_id: UUID) -> Optional[DocumentTemplate]:
        """Get a document template by ID."""
        try:
            result = self.client.table(self.table_name).select("*").eq("id", str(template_id)).execute()
            
            if not result.data:
                return None
            
            return self._dict_to_template(result.data[0])
            
        except Exception as e:
            raise RepositoryError(f"Failed to get document template by ID: {str(e)}")

    async def get_by_business_id(
        self, 
        business_id: UUID, 
        document_type: Optional[DocumentType] = None,
        is_active: Optional[bool] = None
    ) -> List[DocumentTemplate]:
        """Get all document templates for a business."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if document_type:
                query = query.eq("document_type", document_type.value)
            
            if is_active is not None:
                query = query.eq("is_active", is_active)
            
            query = query.order("created_date", desc=True)
            
            result = query.execute()
            
            return [self._dict_to_template(row) for row in result.data]
            
        except Exception as e:
            raise RepositoryError(f"Failed to get document templates by business ID: {str(e)}")

    async def get_system_templates(
        self, 
        document_type: Optional[DocumentType] = None,
        is_active: Optional[bool] = None
    ) -> List[DocumentTemplate]:
        """Get all system templates."""
        try:
            query = self.client.table(self.table_name).select("*").eq("is_system_template", True)
            
            if document_type:
                query = query.eq("document_type", document_type.value)
            
            if is_active is not None:
                query = query.eq("is_active", is_active)
            
            query = query.order("created_date", desc=True)
            
            result = query.execute()
            
            return [self._dict_to_template(row) for row in result.data]
            
        except Exception as e:
            raise RepositoryError(f"Failed to get system templates: {str(e)}")

    async def get_default_template(
        self, 
        business_id: UUID, 
        document_type: DocumentType
    ) -> Optional[DocumentTemplate]:
        """Get the default template for a business and document type."""
        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .eq("business_id", str(business_id))
                .eq("document_type", document_type.value)
                .eq("is_default", True)
                .eq("is_active", True)
                .execute()
            )
            
            if not result.data:
                return None
            
            return self._dict_to_template(result.data[0])
            
        except Exception as e:
            raise RepositoryError(f"Failed to get default template: {str(e)}")

    async def update(self, template: DocumentTemplate) -> DocumentTemplate:
        """Update an existing document template."""
        try:
            template_data = self._template_to_dict(template)
            template_data['last_modified'] = datetime.utcnow().isoformat()
            
            result = (
                self.client.table(self.table_name)
                .update(template_data)
                .eq("id", str(template.id))
                .execute()
            )
            
            if not result.data:
                raise EntityNotFoundError(f"Document template not found: {template.id}")
            
            return self._dict_to_template(result.data[0])
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            raise RepositoryError(f"Failed to update document template: {str(e)}")

    async def delete(self, template_id: UUID) -> bool:
        """Delete a document template."""
        try:
            result = (
                self.client.table(self.table_name)
                .delete()
                .eq("id", str(template_id))
                .execute()
            )
            
            return len(result.data) > 0
            
        except Exception as e:
            raise RepositoryError(f"Failed to delete document template: {str(e)}")

    async def set_as_default(
        self, 
        template_id: UUID, 
        business_id: UUID, 
        document_type: DocumentType
    ) -> bool:
        """Set a template as the default for a business and document type."""
        try:
            # First, unset any existing default for this business and document type
            self.client.table(self.table_name).update({"is_default": False}).eq(
                "business_id", str(business_id)
            ).eq("document_type", document_type.value).eq("is_default", True).execute()
            
            # Then set the new default
            result = (
                self.client.table(self.table_name)
                .update({"is_default": True, "last_modified": datetime.utcnow().isoformat()})
                .eq("id", str(template_id))
                .eq("business_id", str(business_id))
                .eq("document_type", document_type.value)
                .execute()
            )
            
            return len(result.data) > 0
            
        except Exception as e:
            raise RepositoryError(f"Failed to set template as default: {str(e)}")

    async def get_templates_by_usage(
        self, 
        business_id: UUID, 
        document_type: Optional[DocumentType] = None,
        limit: int = 10
    ) -> List[DocumentTemplate]:
        """Get templates ordered by usage count (most used first)."""
        try:
            query = (
                self.client.table(self.table_name)
                .select("*")
                .eq("business_id", str(business_id))
                .eq("is_active", True)
            )
            
            if document_type:
                query = query.eq("document_type", document_type.value)
            
            query = query.order("usage_count", desc=True).limit(limit)
            
            result = query.execute()
            
            return [self._dict_to_template(row) for row in result.data]
            
        except Exception as e:
            raise RepositoryError(f"Failed to get templates by usage: {str(e)}")

    async def search_templates(
        self, 
        business_id: UUID,
        query: str,
        document_type: Optional[DocumentType] = None,
        tags: Optional[List[str]] = None
    ) -> List[DocumentTemplate]:
        """Search templates by name, description, or tags."""
        try:
            # Build search query
            search_query = (
                self.client.table(self.table_name)
                .select("*")
                .eq("business_id", str(business_id))
                .eq("is_active", True)
            )
            
            if document_type:
                search_query = search_query.eq("document_type", document_type.value)
            
            # Use text search on name and description
            search_query = search_query.or_(f"name.ilike.%{query}%,description.ilike.%{query}%")
            
            if tags:
                # Search for templates that contain any of the specified tags
                for tag in tags:
                    search_query = search_query.contains("tags", [tag])
            
            result = search_query.order("name").execute()
            
            return [self._dict_to_template(row) for row in result.data]
            
        except Exception as e:
            raise RepositoryError(f"Failed to search templates: {str(e)}")

    async def get_templates_with_branding(
        self, 
        branding_id: UUID
    ) -> List[DocumentTemplate]:
        """Get all templates that use a specific branding configuration."""
        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .eq("branding_id", str(branding_id))
                .execute()
            )
            
            return [self._dict_to_template(row) for row in result.data]
            
        except Exception as e:
            raise RepositoryError(f"Failed to get templates with branding: {str(e)}")

    def _template_to_dict(self, template: DocumentTemplate) -> Dict[str, Any]:
        """Convert DocumentTemplate entity to database dictionary."""
        return {
            "id": str(template.id),
            "business_id": str(template.business_id) if template.business_id else None,
            "branding_id": str(template.branding_id) if template.branding_id else None,
            "name": template.name,
            "description": template.description,
            "document_type": template.document_type.value if hasattr(template.document_type, 'value') else template.document_type,
            "template_type": template.template_type.value if hasattr(template.template_type, 'value') else template.template_type,
            "is_active": template.is_active,
            "is_default": template.is_default,
            "is_system_template": template.is_system_template,
            "sections": template.sections.model_dump(),
            "header_text": template.header_text,
            "footer_text": template.footer_text,
            "terms_text": template.terms_text,
            "payment_instructions": template.payment_instructions,
            "thank_you_message": template.thank_you_message,
            "logo_override_url": template.logo_override_url,
            "color_overrides": template.color_overrides,
            "font_overrides": template.font_overrides,
            "custom_css": template.custom_css,
            "template_data": template.template_data,
            "usage_count": template.usage_count,
            "last_used_date": template.last_used_date.isoformat() if template.last_used_date else None,
            "tags": template.tags,
            "category": template.category,
            "version": template.version,
            "created_by": template.created_by,
            "created_date": template.created_date.isoformat(),
            "last_modified": template.last_modified.isoformat(),
            "last_modified_by": template.last_modified_by,
        }

    def _dict_to_template(self, data: Dict[str, Any]) -> DocumentTemplate:
        """Convert database dictionary to DocumentTemplate entity."""
        # Parse sections JSON to DocumentSections
        sections_data = data.get("sections", {})
        sections = DocumentSections(**sections_data) if sections_data else DocumentSections()
        
        # Parse datetime fields
        created_date = datetime.fromisoformat(data["created_date"].replace("Z", "+00:00"))
        last_modified = datetime.fromisoformat(data["last_modified"].replace("Z", "+00:00"))
        last_used_date = None
        if data.get("last_used_date"):
            last_used_date = datetime.fromisoformat(data["last_used_date"].replace("Z", "+00:00"))
        
        return DocumentTemplate(
            id=UUID(data["id"]),
            business_id=UUID(data["business_id"]) if data["business_id"] else None,
            branding_id=UUID(data["branding_id"]) if data["branding_id"] else None,
            name=data["name"],
            description=data.get("description"),
            document_type=DocumentType(data["document_type"]),
            template_type=data["template_type"],
            is_active=data["is_active"],
            is_default=data["is_default"],
            is_system_template=data["is_system_template"],
            sections=sections,
            header_text=data.get("header_text"),
            footer_text=data.get("footer_text"),
            terms_text=data.get("terms_text"),
            payment_instructions=data.get("payment_instructions"),
            thank_you_message=data.get("thank_you_message", "Thank you for your business!"),
            logo_override_url=data.get("logo_override_url"),
            color_overrides=data.get("color_overrides", {}),
            font_overrides=data.get("font_overrides", {}),
            custom_css=data.get("custom_css"),
            template_data=data.get("template_data", {}),
            usage_count=data.get("usage_count", 0),
            last_used_date=last_used_date,
            tags=data.get("tags", []),
            category=data.get("category"),
            version=data.get("version", "1.0"),
            created_by=data.get("created_by"),
            created_date=created_date,
            last_modified=last_modified,
            last_modified_by=data.get("last_modified_by"),
        )
