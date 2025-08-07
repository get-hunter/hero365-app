"""
Document Template Domain Entity

Unified template system for all business documents (estimates, invoices, contracts, etc.)
that leverages the centralized BusinessBranding system.
"""

import uuid
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum

from ..exceptions.domain_exceptions import DomainValidationError
from ..shared.enums import TemplateType


class DocumentType(str, Enum):
    """Types of documents that can use templates."""
    ESTIMATE = "estimate"
    INVOICE = "invoice"
    CONTRACT = "contract"
    PROPOSAL = "proposal"
    WORK_ORDER = "work_order"
    RECEIPT = "receipt"
    QUOTE = "quote"


class DocumentSections(BaseModel):
    """Configurable sections for different document types."""
    
    # Common sections
    show_header: bool = Field(default=True)
    show_footer: bool = Field(default=True)
    show_business_info: bool = Field(default=True)
    show_client_info: bool = Field(default=True)
    show_line_items: bool = Field(default=True)
    show_totals: bool = Field(default=True)
    show_notes: bool = Field(default=True)
    show_signature: bool = Field(default=True)
    
    # Document-specific sections
    show_terms_conditions: bool = Field(default=True)
    show_payment_terms: bool = Field(default=True)
    show_tax_breakdown: bool = Field(default=True)
    
    # Estimate-specific
    show_validity_period: bool = Field(default=True)
    show_estimate_notes: bool = Field(default=True)
    
    # Invoice-specific  
    show_payment_instructions: bool = Field(default=True)
    show_due_date: bool = Field(default=True)
    show_payment_methods: bool = Field(default=True)
    
    # Contract-specific
    show_scope_of_work: bool = Field(default=False)
    show_timeline: bool = Field(default=False)
    show_change_orders: bool = Field(default=False)
    
    # Section ordering
    section_order: List[str] = Field(default_factory=lambda: [
        "header", "business_info", "client_info", "document_details",
        "line_items", "totals", "payment_terms", "terms_conditions",
        "notes", "signature", "footer"
    ])


class DocumentTemplate(BaseModel):
    """
    Unified document template for all business documents.
    
    Uses the centralized BusinessBranding system for consistent styling
    while allowing document-specific customizations.
    """
    
    # Core identification
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: Optional[uuid.UUID] = Field(None, description="None for system templates")
    branding_id: Optional[uuid.UUID] = Field(None, description="Reference to BusinessBranding")
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    
    # Document type and template type
    document_type: DocumentType
    template_type: TemplateType = Field(default=TemplateType.PROFESSIONAL)
    
    # Template status
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)
    is_system_template: bool = Field(default=False)
    
    # Document configuration
    sections: DocumentSections = Field(default_factory=DocumentSections)
    
    # Content customization (overrides BusinessBranding if needed)
    header_text: Optional[str] = Field(None)
    footer_text: Optional[str] = Field(None)
    
    # Document-specific content
    terms_text: Optional[str] = Field(None)
    payment_instructions: Optional[str] = Field(None)
    thank_you_message: str = Field(default="Thank you for your business!")
    
    # Document-specific overrides (if different from BusinessBranding)
    logo_override_url: Optional[str] = Field(None)
    color_overrides: Dict[str, str] = Field(default_factory=dict)
    font_overrides: Dict[str, str] = Field(default_factory=dict)
    
    # Custom styling and data
    custom_css: Optional[str] = Field(None)
    template_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Usage statistics
    usage_count: int = Field(default=0, ge=0)
    last_used_date: Optional[datetime] = Field(None)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = Field(None)
    version: str = Field(default="1.0")
    
    # Audit fields
    created_by: Optional[str] = Field(None)
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified_by: Optional[str] = Field(None)
    
    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate template name."""
        if not v or not v.strip():
            raise ValueError("Template name is required")
        return v.strip()
    
    @field_validator('logo_override_url')
    @classmethod
    def validate_logo_url(cls, v):
        """Validate logo override URL."""
        if v and not cls._is_valid_url(v):
            raise ValueError(f"Invalid logo URL: {v}")
        return v
    
    @model_validator(mode='after')
    def validate_template_rules(self):
        """Validate complex template rules."""
        # System templates cannot belong to a business
        if self.is_system_template and self.business_id:
            raise ValueError("System templates cannot belong to a business")
        
        # Business templates must belong to a business
        if not self.is_system_template and not self.business_id:
            raise ValueError("Business templates must belong to a business")
        
        # Business templates should have branding reference
        if self.business_id and not self.branding_id:
            # This is a warning, not an error - can be set later
            pass
        
        return self
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Basic URL validation."""
        return url.startswith(('http://', 'https://')) or url.startswith('data:')
    
    # Template management methods
    def activate(self) -> 'DocumentTemplate':
        """Activate the template."""
        return self.model_copy(update={
            'is_active': True,
            'last_modified': datetime.now(timezone.utc)
        })
    
    def deactivate(self) -> 'DocumentTemplate':
        """Deactivate the template."""
        if self.is_default:
            raise DomainValidationError("Cannot deactivate default template")
        
        return self.model_copy(update={
            'is_active': False,
            'last_modified': datetime.now(timezone.utc)
        })
    
    def set_as_default(self, set_by: Optional[str] = None) -> 'DocumentTemplate':
        """Set this template as the default for its document type."""
        return self.model_copy(update={
            'is_default': True,
            'last_modified': datetime.now(timezone.utc),
            'last_modified_by': set_by
        })
    
    def increment_usage(self) -> 'DocumentTemplate':
        """Increment usage counter."""
        return self.model_copy(update={
            'usage_count': self.usage_count + 1,
            'last_used_date': datetime.now(timezone.utc)
        })
    
    # Content management methods
    def update_sections(self, **section_settings) -> 'DocumentTemplate':
        """Update section visibility settings."""
        updated_sections = self.sections.model_copy(update=section_settings)
        
        return self.model_copy(update={
            'sections': updated_sections,
            'last_modified': datetime.now(timezone.utc)
        })
    
    def set_header_text(self, text: str) -> 'DocumentTemplate':
        """Set custom header text."""
        return self.model_copy(update={
            'header_text': text,
            'last_modified': datetime.now(timezone.utc)
        })
    
    def set_footer_text(self, text: str) -> 'DocumentTemplate':
        """Set custom footer text."""
        return self.model_copy(update={
            'footer_text': text,
            'last_modified': datetime.now(timezone.utc)
        })
    
    def set_terms_text(self, terms: str) -> 'DocumentTemplate':
        """Set terms and conditions text."""
        return self.model_copy(update={
            'terms_text': terms,
            'last_modified': datetime.now(timezone.utc)
        })
    
    def set_payment_instructions(self, instructions: str) -> 'DocumentTemplate':
        """Set payment instructions."""
        return self.model_copy(update={
            'payment_instructions': instructions,
            'last_modified': datetime.now(timezone.utc)
        })
    
    def add_color_override(self, color_name: str, color_value: str) -> 'DocumentTemplate':
        """Add color override for this template."""
        new_overrides = self.color_overrides.copy()
        new_overrides[color_name] = color_value
        
        return self.model_copy(update={
            'color_overrides': new_overrides,
            'last_modified': datetime.now(timezone.utc)
        })
    
    def add_font_override(self, font_property: str, font_value: str) -> 'DocumentTemplate':
        """Add font override for this template."""
        new_overrides = self.font_overrides.copy()
        new_overrides[font_property] = font_value
        
        return self.model_copy(update={
            'font_overrides': new_overrides,
            'last_modified': datetime.now(timezone.utc)
        })
    
    # Utility methods
    def clone(
        self, 
        new_name: str, 
        document_type: Optional[DocumentType] = None,
        business_id: Optional[uuid.UUID] = None,
        cloned_by: Optional[str] = None
    ) -> 'DocumentTemplate':
        """Create a copy of this template, optionally for different document type."""
        return self.model_copy(update={
            'id': uuid.uuid4(),
            'business_id': business_id or self.business_id,
            'name': new_name,
            'description': f"Copy of {self.name}",
            'document_type': document_type or self.document_type,
            'is_active': True,
            'is_default': False,
            'is_system_template': False,
            'template_data': self.template_data.copy(),
            'tags': self.tags.copy(),
            'color_overrides': self.color_overrides.copy(),
            'font_overrides': self.font_overrides.copy(),
            'usage_count': 0,
            'last_used_date': None,
            'created_by': cloned_by,
            'created_date': datetime.now(timezone.utc),
            'last_modified': datetime.now(timezone.utc),
            'last_modified_by': cloned_by
        })
    
    def get_effective_branding(self, business_branding: Optional['BusinessBranding'] = None) -> Dict[str, Any]:
        """
        Get effective branding configuration by merging BusinessBranding with template overrides.
        
        Args:
            business_branding: BusinessBranding instance to merge with
            
        Returns:
            Merged branding configuration
        """
        if not business_branding:
            # Return only template-specific overrides
            return {
                'color_overrides': self.color_overrides,
                'font_overrides': self.font_overrides,
                'logo_override_url': self.logo_override_url
            }
        
        # Get base branding config
        base_config = business_branding.get_template_config(
            component="estimate" if self.document_type == DocumentType.ESTIMATE else "invoice"
        )
        
        # Apply template overrides
        if self.color_overrides:
            base_config['color_scheme'].update(self.color_overrides)
        
        if self.font_overrides:
            base_config['typography'].update(self.font_overrides)
        
        if self.logo_override_url:
            base_config['assets']['logo_url'] = self.logo_override_url
        
        return base_config
    
    def is_suitable_for_document_type(self, document_type: DocumentType) -> bool:
        """Check if template is suitable for a specific document type."""
        return self.document_type == document_type
    
    def get_document_type_display(self) -> str:
        """Get human-readable document type."""
        # Handle both enum and string values (due to use_enum_values=True)
        value = self.document_type.value if hasattr(self.document_type, 'value') else self.document_type
        return value.replace('_', ' ').title()
    
    def get_status_display(self) -> str:
        """Get human-readable status."""
        if not self.is_active:
            return "Inactive"
        elif self.is_default:
            return f"Default {self.get_document_type_display()}"
        else:
            return "Active"
    
    def __str__(self) -> str:
        return f"DocumentTemplate({self.name} - {self.get_document_type_display()} - {self.get_status_display()})"
    
    def __repr__(self) -> str:
        return (f"DocumentTemplate(id={self.id}, name='{self.name}', "
                f"document_type={self.document_type}, active={self.is_active}, "
                f"default={self.is_default})")


# Factory methods for creating specific document templates
class DocumentTemplateFactory:
    """Factory for creating document templates with appropriate defaults."""
    
    @staticmethod
    def create_estimate_template(
        business_id: uuid.UUID,
        name: str,
        branding_id: Optional[uuid.UUID] = None,
        created_by: Optional[str] = None
    ) -> DocumentTemplate:
        """Create an estimate template with estimate-specific defaults."""
        sections = DocumentSections(
            show_validity_period=True,
            show_estimate_notes=True,
            show_payment_instructions=False,  # Not needed for estimates
            show_due_date=False
        )
        
        return DocumentTemplate(
            business_id=business_id,
            branding_id=branding_id,
            name=name,
            document_type=DocumentType.ESTIMATE,
            sections=sections,
            thank_you_message="Thank you for considering our services!",
            created_by=created_by
        )
    
    @staticmethod
    def create_invoice_template(
        business_id: uuid.UUID,
        name: str,
        branding_id: Optional[uuid.UUID] = None,
        created_by: Optional[str] = None
    ) -> DocumentTemplate:
        """Create an invoice template with invoice-specific defaults."""
        sections = DocumentSections(
            show_validity_period=False,  # Not needed for invoices
            show_estimate_notes=False,
            show_payment_instructions=True,
            show_due_date=True,
            show_payment_methods=True
        )
        
        return DocumentTemplate(
            business_id=business_id,
            branding_id=branding_id,
            name=name,
            document_type=DocumentType.INVOICE,
            sections=sections,
            thank_you_message="Thank you for your business!",
            payment_instructions="Payment is due within 30 days of invoice date.",
            created_by=created_by
        )
