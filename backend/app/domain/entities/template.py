"""
Template Domain Entity

A single, flexible template system for all document types (invoices, estimates, 
websites, contracts, etc.) using JSONB for configuration storage.
"""

import uuid
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum

from ..exceptions.domain_exceptions import DomainValidationError


class TemplateType(str, Enum):
    """Types of templates supported by the system."""
    INVOICE = "invoice"
    ESTIMATE = "estimate"
    CONTRACT = "contract"
    PROPOSAL = "proposal"
    QUOTE = "quote"
    WORK_ORDER = "work_order"
    RECEIPT = "receipt"
    WEBSITE = "website"
    EMAIL = "email"
    PROJECT = "project"
    JOB = "job"
    ACTIVITY = "activity"
    WORKING_HOURS = "working_hours"
    CUSTOM = "custom"


class TemplateCategory(str, Enum):
    """Template style categories."""
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    MINIMAL = "minimal"
    CORPORATE = "corporate"
    MODERN = "modern"
    CLASSIC = "classic"
    INDUSTRIAL = "industrial"
    SERVICE_FOCUSED = "service_focused"
    CONSULTING = "consulting"
    CUSTOM = "custom"


class Template(BaseModel):
    """
    Unified template entity that supports all document types with flexible
    JSONB configuration for maximum extensibility.
    
    The config field structure varies by template_type but follows consistent
    patterns for similar document types.
    """
    
    # Core identification
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: Optional[uuid.UUID] = Field(None, description="None for system templates")
    branding_id: Optional[uuid.UUID] = Field(None, description="Reference to BusinessBranding")
    
    # Template classification
    template_type: TemplateType
    category: Optional[TemplateCategory] = None
    
    # Basic metadata
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    version: int = Field(default=1, ge=1)
    
    # Status flags
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)
    is_system: bool = Field(default=False)
    
    # Flexible configuration stored as dict (becomes JSONB in database)
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # Usage tracking
    usage_count: int = Field(default=0, ge=0)
    last_used_at: Optional[datetime] = Field(None)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Audit fields
    created_by: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = Field(None)
    
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
    
    @field_validator('config')
    @classmethod
    def validate_config(cls, v, values):
        """Validate config structure based on template type."""
        # Basic validation - ensure config is not None
        if v is None:
            return {}
        
        # We could add template-type specific validation here if needed
        # For now, we'll keep it flexible
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Clean and validate tags."""
        if v:
            # Remove duplicates and empty strings, convert to lowercase
            v = list(set(tag.strip().lower() for tag in v if tag and tag.strip()))
        return v
    
    @model_validator(mode='after')
    def validate_template_rules(self):
        """Validate complex template rules."""
        # System templates cannot belong to a business
        if self.is_system and self.business_id:
            raise ValueError("System templates cannot belong to a business")
        
        # Business templates must belong to a business
        if not self.is_system and not self.business_id:
            raise ValueError("Business templates must belong to a business")
        
        return self
    
    # Template management methods
    def activate(self) -> 'Template':
        """Activate the template."""
        return self.model_copy(update={'is_active': True})
    
    def deactivate(self) -> 'Template':
        """Deactivate the template."""
        return self.model_copy(update={'is_active': False, 'is_default': False})
    
    def set_as_default(self, set_by: Optional[str] = None) -> 'Template':
        """Mark template as default."""
        if not self.is_active:
            raise DomainValidationError("Cannot set inactive template as default")
        
        updates = {'is_default': True}
        if set_by:
            updates['updated_by'] = set_by
            updates['updated_at'] = datetime.now(timezone.utc)
        
        return self.model_copy(update=updates)
    
    def unset_default(self) -> 'Template':
        """Remove default status."""
        return self.model_copy(update={'is_default': False})
    
    def increment_usage(self) -> 'Template':
        """Increment usage count and update last used date."""
        return self.model_copy(update={
            'usage_count': self.usage_count + 1,
            'last_used_at': datetime.now(timezone.utc)
        })
    
    def update_config(self, config_updates: Dict[str, Any], merge: bool = True) -> 'Template':
        """
        Update template configuration.
        
        Args:
            config_updates: New configuration values
            merge: If True, merge with existing config. If False, replace entirely.
        """
        if merge:
            new_config = {**self.config, **config_updates}
        else:
            new_config = config_updates
        
        return self.model_copy(update={
            'config': new_config,
            'updated_at': datetime.now(timezone.utc)
        })
    
    def get_config_value(self, path: str, default: Any = None) -> Any:
        """
        Get a value from the config using dot notation.
        
        Args:
            path: Dot-separated path (e.g., "colors.primary")
            default: Default value if path not found
        """
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set_config_value(self, path: str, value: Any) -> 'Template':
        """
        Set a value in the config using dot notation.
        
        Args:
            path: Dot-separated path (e.g., "colors.primary")
            value: Value to set
        """
        keys = path.split('.')
        new_config = {**self.config}
        
        # Navigate to the parent of the target key
        current = new_config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
        
        return self.model_copy(update={
            'config': new_config,
            'updated_at': datetime.now(timezone.utc)
        })
    
    def clone(
        self, 
        new_name: str,
        business_id: Optional[uuid.UUID] = None,
        cloned_by: Optional[str] = None
    ) -> 'Template':
        """
        Clone this template.
        
        Args:
            new_name: Name for the cloned template
            business_id: Optional business ID for the clone
            cloned_by: User who is cloning
        """
        return Template(
            business_id=business_id or self.business_id,
            branding_id=self.branding_id,
            template_type=self.template_type,
            category=self.category,
            name=new_name,
            description=f"Cloned from {self.name}",
            version=1,
            is_active=True,
            is_default=False,
            is_system=False,
            config={**self.config},  # Deep copy of config
            tags=list(self.tags),
            metadata={
                **self.metadata,
                'cloned_from': str(self.id),
                'cloned_at': datetime.now(timezone.utc).isoformat()
            },
            created_by=cloned_by,
            created_at=datetime.now(timezone.utc)
        )
    
    def to_version_snapshot(self) -> Dict[str, Any]:
        """Create a snapshot of current state for versioning."""
        return {
            'template_id': str(self.id),
            'version': self.version,
            'config': {**self.config},
            'metadata': {**self.metadata},
            'snapshot_at': datetime.now(timezone.utc).isoformat()
        }
    
    def apply_branding(self, branding: Any) -> 'Template':
        """
        Apply business branding to template configuration.
        
        This method would merge branding colors, fonts, etc. into the template
        config while preserving template-specific overrides.
        """
        if not branding:
            return self
        
        # Get current config
        new_config = {**self.config}
        
        # Apply branding colors if not overridden
        if 'colors' not in new_config:
            new_config['colors'] = {}
        
        if hasattr(branding, 'color_scheme') and branding.color_scheme:
            # Only apply branding colors that aren't already set
            for key, value in branding.color_scheme.items():
                if key not in new_config['colors']:
                    new_config['colors'][key] = value
        
        # Apply branding typography if not overridden
        if 'typography' not in new_config:
            new_config['typography'] = {}
        
        if hasattr(branding, 'typography') and branding.typography:
            for key, value in branding.typography.items():
                if key not in new_config['typography']:
                    new_config['typography'][key] = value
        
        return self.model_copy(update={
            'config': new_config,
            'branding_id': branding.id if hasattr(branding, 'id') else None
        })
    
    def is_document_template(self) -> bool:
        """Check if this is a document template (invoice, estimate, etc.)."""
        document_types = {
            TemplateType.INVOICE, TemplateType.ESTIMATE, TemplateType.CONTRACT,
            TemplateType.PROPOSAL, TemplateType.QUOTE, TemplateType.WORK_ORDER,
            TemplateType.RECEIPT
        }
        return self.template_type in document_types
    
    def is_website_template(self) -> bool:
        """Check if this is a website template."""
        return self.template_type == TemplateType.WEBSITE
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get display information for UI."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'type': self.template_type,
            'category': self.category,
            'is_default': self.is_default,
            'is_system': self.is_system,
            'usage_count': self.usage_count,
            'last_used': self.last_used_at.isoformat() if self.last_used_at else None,
            'preview': self._generate_preview()
        }
    
    def _generate_preview(self) -> Dict[str, Any]:
        """Generate a preview of the template for UI display."""
        preview = {
            'colors': self.get_config_value('colors', {}),
            'typography': self.get_config_value('typography', {})
        }
        
        if self.is_document_template():
            preview['layout'] = self.get_config_value('layout', {})
            preview['sections'] = list(self.get_config_value('sections', {}).keys())
        elif self.is_website_template():
            preview['pages'] = len(self.get_config_value('pages', []))
            preview['navigation'] = self.get_config_value('navigation.style', 'standard')
        
        return preview


class TemplateFactory:
    """Factory for creating templates with appropriate defaults."""
    
    @staticmethod
    def create_invoice_template(
        business_id: uuid.UUID,
        name: str,
        branding_id: Optional[uuid.UUID] = None,
        created_by: Optional[str] = None
    ) -> Template:
        """Create an invoice template with invoice-specific defaults."""
        
        default_config = {
            "layout": {
                "header_style": "standard",
                "items_table_style": "detailed",
                "footer_style": "detailed",
                "logo_position": "top_left",
                "page_size": "letter",
                "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
            },
            "sections": {
                "header": {"visible": True},
                "business_info": {"visible": True},
                "client_info": {"visible": True},
                "line_items": {"visible": True},
                "totals": {"visible": True, "show_tax": True},
                "payment_terms": {"visible": True},
                "footer": {"visible": True}
            },
            "business_rules": {
                "payment_terms": "net_30",
                "show_due_date": True,
                "tax_calculation": "exclusive"
            }
        }
        
        return Template(
            business_id=business_id,
            branding_id=branding_id,
            template_type=TemplateType.INVOICE,
            category=TemplateCategory.PROFESSIONAL,
            name=name,
            config=default_config,
            created_by=created_by
        )
    
    @staticmethod
    def create_estimate_template(
        business_id: uuid.UUID,
        name: str,
        branding_id: Optional[uuid.UUID] = None,
        created_by: Optional[str] = None
    ) -> Template:
        """Create an estimate template with estimate-specific defaults."""
        
        default_config = {
            "layout": {
                "header_style": "standard",
                "items_table_style": "detailed",
                "footer_style": "detailed",
                "logo_position": "top_left",
                "page_size": "letter",
                "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
            },
            "sections": {
                "header": {"visible": True},
                "business_info": {"visible": True},
                "client_info": {"visible": True},
                "line_items": {"visible": True},
                "totals": {"visible": True, "show_tax": True},
                "validity_period": {"visible": True},
                "terms_conditions": {"visible": True},
                "footer": {"visible": True}
            },
            "business_rules": {
                "validity_days": 30,
                "show_expiry_date": True,
                "tax_calculation": "exclusive"
            }
        }
        
        return Template(
            business_id=business_id,
            branding_id=branding_id,
            template_type=TemplateType.ESTIMATE,
            category=TemplateCategory.PROFESSIONAL,
            name=name,
            config=default_config,
            created_by=created_by
        )
    
    @staticmethod
    def create_website_template(
        business_id: Optional[uuid.UUID],
        name: str,
        pages: List[Dict[str, Any]],
        created_by: Optional[str] = None
    ) -> Template:
        """Create a website template."""
        
        default_config = {
            "pages": pages,
            "navigation": {
                "style": "standard",
                "items": [{"label": p.get("name", "Page"), "path": p.get("path", "/")} for p in pages]
            },
            "seo": {
                "defaults": {},
                "schemas": ["LocalBusiness"]
            },
            "theme": {
                "extends_branding": True,
                "overrides": {}
            }
        }
        
        return Template(
            business_id=business_id,
            template_type=TemplateType.WEBSITE,
            category=TemplateCategory.PROFESSIONAL,
            name=name,
            config=default_config,
            created_by=created_by,
            is_system=business_id is None
        )
