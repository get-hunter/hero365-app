"""
Document Template Repository Interface

Repository interface for managing document templates (estimates, invoices, contracts, etc.)
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.document_template import DocumentTemplate, DocumentType


class DocumentTemplateRepository(ABC):
    """Repository interface for document template operations."""

    @abstractmethod
    async def create(self, template: DocumentTemplate) -> DocumentTemplate:
        """Create a new document template."""
        pass

    @abstractmethod
    async def get_by_id(self, template_id: UUID) -> Optional[DocumentTemplate]:
        """Get a document template by ID."""
        pass

    @abstractmethod
    async def get_by_business_id(
        self, 
        business_id: UUID, 
        document_type: Optional[DocumentType] = None,
        is_active: Optional[bool] = None
    ) -> List[DocumentTemplate]:
        """Get all document templates for a business, optionally filtered by document type and active status."""
        pass

    @abstractmethod
    async def get_system_templates(
        self, 
        document_type: Optional[DocumentType] = None,
        is_active: Optional[bool] = None
    ) -> List[DocumentTemplate]:
        """Get all system templates, optionally filtered by document type and active status."""
        pass

    @abstractmethod
    async def get_default_template(
        self, 
        business_id: UUID, 
        document_type: DocumentType
    ) -> Optional[DocumentTemplate]:
        """Get the default template for a business and document type."""
        pass

    @abstractmethod
    async def update(self, template: DocumentTemplate) -> DocumentTemplate:
        """Update an existing document template."""
        pass

    @abstractmethod
    async def delete(self, template_id: UUID) -> bool:
        """Delete a document template."""
        pass

    @abstractmethod
    async def set_as_default(
        self, 
        template_id: UUID, 
        business_id: UUID, 
        document_type: DocumentType
    ) -> bool:
        """Set a template as the default for a business and document type."""
        pass

    @abstractmethod
    async def get_templates_by_usage(
        self, 
        business_id: UUID, 
        document_type: Optional[DocumentType] = None,
        limit: int = 10
    ) -> List[DocumentTemplate]:
        """Get templates ordered by usage count (most used first)."""
        pass

    @abstractmethod
    async def search_templates(
        self, 
        business_id: UUID,
        query: str,
        document_type: Optional[DocumentType] = None,
        tags: Optional[List[str]] = None
    ) -> List[DocumentTemplate]:
        """Search templates by name, description, or tags."""
        pass

    @abstractmethod
    async def get_templates_with_branding(
        self, 
        branding_id: UUID
    ) -> List[DocumentTemplate]:
        """Get all templates that use a specific branding configuration."""
        pass
