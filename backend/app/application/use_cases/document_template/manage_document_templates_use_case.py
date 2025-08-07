"""
Manage Document Templates Use Case

Unified use case for managing all document templates (estimates, invoices, contracts, etc.)
"""

from typing import List, Optional
from uuid import UUID

from app.domain.entities.document_template import DocumentTemplate, DocumentType, DocumentTemplateFactory
from app.domain.repositories.document_template_repository import DocumentTemplateRepository
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, DomainValidationError


class ManageDocumentTemplatesUseCase:
    """Use case for managing document templates."""

    def __init__(self, template_repository: DocumentTemplateRepository):
        self.template_repository = template_repository

    async def create_template(
        self,
        business_id: UUID,
        name: str,
        document_type: DocumentType,
        branding_id: Optional[UUID] = None,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
        **template_kwargs
    ) -> DocumentTemplate:
        """Create a new document template."""
        
        # Use factory method for document-specific defaults
        if document_type == DocumentType.ESTIMATE:
            template = DocumentTemplateFactory.create_estimate_template(
                business_id=business_id,
                name=name,
                branding_id=branding_id,
                created_by=created_by
            )
        elif document_type == DocumentType.INVOICE:
            template = DocumentTemplateFactory.create_invoice_template(
                business_id=business_id,
                name=name,
                branding_id=branding_id,
                created_by=created_by
            )
        else:
            # Generic template for other document types
            template = DocumentTemplate(
                business_id=business_id,
                branding_id=branding_id,
                name=name,
                document_type=document_type,
                description=description,
                created_by=created_by,
                **template_kwargs
            )

        if description:
            template = template.model_copy(update={'description': description})

        return await self.template_repository.create(template)

    async def get_template(self, template_id: UUID) -> DocumentTemplate:
        """Get a template by ID."""
        template = await self.template_repository.get_by_id(template_id)
        if not template:
            raise EntityNotFoundError(f"Document template not found: {template_id}")
        return template

    async def get_business_templates(
        self,
        business_id: UUID,
        document_type: Optional[DocumentType] = None,
        is_active: Optional[bool] = None
    ) -> List[DocumentTemplate]:
        """Get all templates for a business."""
        return await self.template_repository.get_by_business_id(
            business_id=business_id,
            document_type=document_type,
            is_active=is_active
        )

    async def get_system_templates(
        self,
        document_type: Optional[DocumentType] = None,
        is_active: Optional[bool] = None
    ) -> List[DocumentTemplate]:
        """Get all system templates."""
        return await self.template_repository.get_system_templates(
            document_type=document_type,
            is_active=is_active
        )

    async def get_default_template(
        self,
        business_id: UUID,
        document_type: DocumentType
    ) -> Optional[DocumentTemplate]:
        """Get the default template for a business and document type."""
        return await self.template_repository.get_default_template(
            business_id=business_id,
            document_type=document_type
        )

    async def update_template(
        self,
        template_id: UUID,
        updates: dict,
        updated_by: Optional[str] = None
    ) -> DocumentTemplate:
        """Update a template."""
        template = await self.get_template(template_id)
        
        # Add audit info
        if updated_by:
            updates['last_modified_by'] = updated_by
        
        updated_template = template.model_copy(update=updates)
        return await self.template_repository.update(updated_template)

    async def activate_template(
        self,
        template_id: UUID,
        activated_by: Optional[str] = None
    ) -> DocumentTemplate:
        """Activate a template."""
        template = await self.get_template(template_id)
        activated_template = template.activate()
        
        if activated_by:
            activated_template = activated_template.model_copy(update={'last_modified_by': activated_by})
        
        return await self.template_repository.update(activated_template)

    async def deactivate_template(
        self,
        template_id: UUID,
        deactivated_by: Optional[str] = None
    ) -> DocumentTemplate:
        """Deactivate a template."""
        template = await self.get_template(template_id)
        deactivated_template = template.deactivate()
        
        if deactivated_by:
            deactivated_template = deactivated_template.model_copy(update={'last_modified_by': deactivated_by})
        
        return await self.template_repository.update(deactivated_template)

    async def set_default_template(
        self,
        template_id: UUID,
        business_id: UUID,
        document_type: DocumentType,
        set_by: Optional[str] = None
    ) -> DocumentTemplate:
        """Set a template as the default for a business and document type."""
        template = await self.get_template(template_id)
        
        # Validate that template belongs to the business and is the correct type
        if template.business_id != business_id:
            raise DomainValidationError("Template does not belong to the specified business")
        
        if template.document_type != document_type:
            raise DomainValidationError("Template document type does not match")
        
        if not template.is_active:
            raise DomainValidationError("Cannot set inactive template as default")
        
        # Set as default in repository (handles unsetting other defaults)
        success = await self.template_repository.set_as_default(
            template_id=template_id,
            business_id=business_id,
            document_type=document_type
        )
        
        if not success:
            raise DomainValidationError("Failed to set template as default")
        
        # Update the template instance
        default_template = template.set_as_default(set_by)
        return await self.template_repository.update(default_template)

    async def clone_template(
        self,
        template_id: UUID,
        new_name: str,
        business_id: Optional[UUID] = None,
        document_type: Optional[DocumentType] = None,
        cloned_by: Optional[str] = None
    ) -> DocumentTemplate:
        """Clone a template."""
        original_template = await self.get_template(template_id)
        
        cloned_template = original_template.clone(
            new_name=new_name,
            document_type=document_type,
            business_id=business_id,
            cloned_by=cloned_by
        )
        
        return await self.template_repository.create(cloned_template)

    async def increment_template_usage(
        self,
        template_id: UUID
    ) -> DocumentTemplate:
        """Increment the usage count for a template."""
        template = await self.get_template(template_id)
        updated_template = template.increment_usage()
        return await self.template_repository.update(updated_template)

    async def delete_template(
        self,
        template_id: UUID
    ) -> bool:
        """Delete a template."""
        template = await self.get_template(template_id)
        
        # Prevent deletion of default templates
        if template.is_default:
            raise DomainValidationError("Cannot delete default template")
        
        return await self.template_repository.delete(template_id)

    async def search_templates(
        self,
        business_id: UUID,
        query: str,
        document_type: Optional[DocumentType] = None,
        tags: Optional[List[str]] = None
    ) -> List[DocumentTemplate]:
        """Search templates."""
        return await self.template_repository.search_templates(
            business_id=business_id,
            query=query,
            document_type=document_type,
            tags=tags
        )

    async def get_popular_templates(
        self,
        business_id: UUID,
        document_type: Optional[DocumentType] = None,
        limit: int = 10
    ) -> List[DocumentTemplate]:
        """Get the most used templates."""
        return await self.template_repository.get_templates_by_usage(
            business_id=business_id,
            document_type=document_type,
            limit=limit
        )

    async def get_templates_with_branding(
        self,
        branding_id: UUID
    ) -> List[DocumentTemplate]:
        """Get all templates using a specific branding configuration."""
        return await self.template_repository.get_templates_with_branding(branding_id)

    async def update_template_sections(
        self,
        template_id: UUID,
        section_updates: dict,
        updated_by: Optional[str] = None
    ) -> DocumentTemplate:
        """Update template section settings."""
        template = await self.get_template(template_id)
        updated_template = template.update_sections(**section_updates)
        
        if updated_by:
            updated_template = updated_template.model_copy(update={'last_modified_by': updated_by})
        
        return await self.template_repository.update(updated_template)

    async def update_template_content(
        self,
        template_id: UUID,
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None,
        terms_text: Optional[str] = None,
        payment_instructions: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> DocumentTemplate:
        """Update template content."""
        template = await self.get_template(template_id)
        
        updates = {}
        if header_text is not None:
            template = template.set_header_text(header_text)
        if footer_text is not None:
            template = template.set_footer_text(footer_text)
        if terms_text is not None:
            template = template.set_terms_text(terms_text)
        if payment_instructions is not None:
            template = template.set_payment_instructions(payment_instructions)
        
        if updated_by:
            template = template.model_copy(update={'last_modified_by': updated_by})
        
        return await self.template_repository.update(template)
