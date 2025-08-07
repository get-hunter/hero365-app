"""
Document Template API Schemas

Pydantic models for document template API requests and responses.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DocumentTemplateResponse(BaseModel):
    """Response schema for document template."""
    
    id: uuid.UUID
    business_id: Optional[uuid.UUID] = None
    branding_id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    document_type: str
    template_type: str
    is_active: bool
    is_default: bool
    is_system_template: bool
    usage_count: int
    last_used_date: Optional[datetime] = None
    created_by: Optional[str] = None
    created_date: datetime
    last_modified: datetime
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    version: str


class CreateDocumentTemplateRequest(BaseModel):
    """Request schema for creating a document template."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    document_type: str = Field(..., description="Type of document (estimate, invoice, contract, etc.)")
    branding_id: Optional[uuid.UUID] = Field(None, description="Reference to business branding")


class UpdateDocumentTemplateRequest(BaseModel):
    """Request schema for updating a document template."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None
    branding_id: Optional[uuid.UUID] = None


class DocumentTemplateSectionsResponse(BaseModel):
    """Response schema for template sections configuration."""
    
    show_header: bool = True
    show_footer: bool = True
    show_business_info: bool = True
    show_client_info: bool = True
    show_line_items: bool = True
    show_totals: bool = True
    show_notes: bool = True
    show_signature: bool = True
    show_terms_conditions: bool = True
    show_payment_terms: bool = True
    show_tax_breakdown: bool = True
    show_validity_period: bool = True
    show_estimate_notes: bool = True
    show_payment_instructions: bool = True
    show_due_date: bool = True
    show_payment_methods: bool = True
    section_order: List[str] = Field(default_factory=list)


class UpdateTemplateSectionsRequest(BaseModel):
    """Request schema for updating template sections."""
    
    show_header: Optional[bool] = None
    show_footer: Optional[bool] = None
    show_business_info: Optional[bool] = None
    show_client_info: Optional[bool] = None
    show_line_items: Optional[bool] = None
    show_totals: Optional[bool] = None
    show_notes: Optional[bool] = None
    show_signature: Optional[bool] = None
    show_terms_conditions: Optional[bool] = None
    show_payment_terms: Optional[bool] = None
    show_tax_breakdown: Optional[bool] = None
    show_validity_period: Optional[bool] = None
    show_estimate_notes: Optional[bool] = None
    show_payment_instructions: Optional[bool] = None
    show_due_date: Optional[bool] = None
    show_payment_methods: Optional[bool] = None
    section_order: Optional[List[str]] = None


class UpdateTemplateContentRequest(BaseModel):
    """Request schema for updating template content."""
    
    header_text: Optional[str] = None
    footer_text: Optional[str] = None
    terms_text: Optional[str] = None
    payment_instructions: Optional[str] = None


class CloneTemplateRequest(BaseModel):
    """Request schema for cloning a template."""
    
    new_name: str = Field(..., min_length=1, max_length=200)
    document_type: Optional[str] = Field(None, description="New document type for cloned template")
    business_id: Optional[uuid.UUID] = Field(None, description="Target business ID for clone")


class DocumentTemplateSearchRequest(BaseModel):
    """Request schema for searching templates."""
    
    query: str = Field(..., min_length=1, description="Search query")
    document_type: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentTemplateListResponse(BaseModel):
    """Response schema for paginated template list."""
    
    templates: List[DocumentTemplateResponse]
    total_count: int
    has_more: bool = False
