"""
Manage Templates Use Case

Unified use case for managing all templates using the new Template system.
This replaces the old ManageDocumentTemplatesUseCase.
"""

from typing import List, Optional
from uuid import UUID

from app.domain.entities.template import Template, TemplateType, TemplateCategory, TemplateFactory
from app.domain.repositories.template_repository import TemplateRepository
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, DomainValidationError


class ManageTemplatesUseCase:
    """Use case for managing templates using the new unified template system."""

    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository

    async def create_template(
        self,
        business_id: UUID,
        name: str,
        template_type: TemplateType,
        branding_id: Optional[UUID] = None,
        description: Optional[str] = None,
        category: Optional[TemplateCategory] = None,
        config: Optional[dict] = None,
        created_by: Optional[str] = None,
        **template_kwargs
    ) -> Template:
        """Create a new template."""
        
        # Use factory method for template-specific defaults
        if template_type == TemplateType.ESTIMATE:
            template = TemplateFactory.create_estimate_template(
                business_id=business_id,
                name=name,
                branding_id=branding_id,
                created_by=created_by
            )
        elif template_type == TemplateType.INVOICE:
            template = TemplateFactory.create_invoice_template(
                business_id=business_id,
                name=name,
                branding_id=branding_id,
                created_by=created_by
            )
        elif template_type == TemplateType.WEBSITE:
            pages = config.get('pages', []) if config else []
            template = TemplateFactory.create_website_template(
                business_id=business_id,
                name=name,
                pages=pages,
                created_by=created_by
            )
        else:
            # Generic template for other types
            template = Template(
                business_id=business_id,
                branding_id=branding_id,
                name=name,
                template_type=template_type,
                category=category or TemplateCategory.PROFESSIONAL,
                description=description,
                config=config or {},
                created_by=created_by,
                **template_kwargs
            )

        if description:
            template = template.model_copy(update={'description': description})
        
        if category:
            template = template.model_copy(update={'category': category})
        
        if config:
            template = template.update_config(config, merge=True)

        return await self.template_repository.create(template)

    async def get_template(self, template_id: UUID) -> Template:
        """Get a template by ID."""
        template = await self.template_repository.get_by_id(template_id)
        if not template:
            raise EntityNotFoundError(f"Template not found: {template_id}")
        return template

    async def get_business_templates(
        self,
        business_id: UUID,
        template_type: Optional[TemplateType] = None,
        is_active: Optional[bool] = None
    ) -> List[Template]:
        """Get all templates for a business (including system templates)."""
        return await self.template_repository.get_by_business_id(
            business_id=business_id,
            template_type=template_type,
            is_active=is_active
        )

    async def get_system_templates(
        self,
        template_type: Optional[TemplateType] = None,
        category: Optional[TemplateCategory] = None,
        is_active: Optional[bool] = None
    ) -> List[Template]:
        """Get all system templates."""
        return await self.template_repository.get_system_templates(
            template_type=template_type,
            category=category,
            is_active=is_active
        )

    async def get_default_template(
        self,
        business_id: UUID,
        template_type: TemplateType
    ) -> Optional[Template]:
        """Get the default template for a business and template type."""
        return await self.template_repository.get_default_template(
            business_id=business_id,
            template_type=template_type
        )

    async def update_template(
        self,
        template_id: UUID,
        updates: dict,
        updated_by: Optional[str] = None
    ) -> Template:
        """Update an existing template."""
        template = await self.get_template(template_id)
        
        # Update fields
        if 'name' in updates:
            template = template.model_copy(update={'name': updates['name']})
        if 'description' in updates:
            template = template.model_copy(update={'description': updates['description']})
        if 'is_active' in updates:
            if updates['is_active']:
                template = template.activate()
            else:
                template = template.deactivate()
        if 'category' in updates:
            template = template.model_copy(update={'category': updates['category']})
        if 'tags' in updates:
            template = template.model_copy(update={'tags': updates['tags']})
        if 'config' in updates:
            template = template.update_config(updates['config'], merge=True)
        
        if updated_by:
            template = template.model_copy(update={
                'updated_by': updated_by,
                'updated_at': template.updated_at
            })

        return await self.template_repository.update(template)

    async def set_default_template(
        self,
        template_id: UUID,
        business_id: UUID,
        template_type: TemplateType,
        set_by: Optional[str] = None
    ) -> Template:
        """Set a template as default for its type and business."""
        template = await self.get_template(template_id)
        
        # Validate template belongs to business or is system template
        if template.business_id and template.business_id != business_id:
            raise DomainValidationError("Template does not belong to this business")
        
        # Set as default
        await self.template_repository.set_as_default(
            template_id=template_id,
            business_id=business_id,
            template_type=template_type
        )
        
        # Get updated template
        return await self.get_template(template_id)

    async def clone_template(
        self,
        template_id: UUID,
        new_name: str,
        business_id: UUID,
        cloned_by: Optional[str] = None
    ) -> Template:
        """Clone an existing template."""
        template = await self.get_template(template_id)
        
        # Clone the template
        cloned = template.clone(
            new_name=new_name,
            business_id=business_id,
            cloned_by=cloned_by
        )
        
        return await self.template_repository.create(cloned)

    async def delete_template(self, template_id: UUID) -> bool:
        """Delete a template."""
        template = await self.get_template(template_id)
        
        # Don't allow deletion of system templates
        if template.is_system:
            raise DomainValidationError("Cannot delete system templates")
        
        return await self.template_repository.delete(template_id)

    async def increment_usage(self, template_id: UUID) -> Template:
        """Increment the usage count for a template."""
        await self.template_repository.increment_usage(template_id)
        return await self.get_template(template_id)

    async def search_templates(
        self,
        query: str,
        business_id: Optional[UUID] = None,
        template_type: Optional[TemplateType] = None,
        tags: Optional[List[str]] = None
    ) -> List[Template]:
        """Search templates by query, tags, or other criteria."""
        return await self.template_repository.search_templates(
            query=query,
            business_id=business_id,
            template_type=template_type,
            tags=tags
        )

    async def get_popular_templates(
        self,
        business_id: Optional[UUID] = None,
        template_type: Optional[TemplateType] = None,
        limit: int = 10
    ) -> List[Template]:
        """Get the most used templates."""
        return await self.template_repository.get_templates_by_usage(
            business_id=business_id,
            template_type=template_type,
            limit=limit
        )
