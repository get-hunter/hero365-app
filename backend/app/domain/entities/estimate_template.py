"""
Estimate Template Domain Entity

Represents a template for generating estimate documents with customizable
branding, layout, and business-specific configurations.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from ..exceptions.domain_exceptions import DomainValidationError
from ..enums import TemplateType, CurrencyCode


@dataclass
class TemplateColorScheme:
    """Value object for template color scheme."""
    primary_color: str = "#2563eb"  # Blue
    secondary_color: str = "#64748b"  # Slate
    accent_color: str = "#10b981"  # Emerald
    text_color: str = "#1f2937"  # Gray-800
    background_color: str = "#ffffff"  # White
    border_color: str = "#e5e7eb"  # Gray-200
    
    def __post_init__(self):
        """Validate color codes."""
        colors = [
            self.primary_color, self.secondary_color, self.accent_color,
            self.text_color, self.background_color, self.border_color
        ]
        
        for color in colors:
            if not self._is_valid_color(color):
                raise DomainValidationError(f"Invalid color code: {color}")
    
    def _is_valid_color(self, color: str) -> bool:
        """Validate hex color code."""
        if not color.startswith('#'):
            return False
        
        hex_part = color[1:]
        if len(hex_part) not in [3, 6]:
            return False
        
        try:
            int(hex_part, 16)
            return True
        except ValueError:
            return False


@dataclass
class TemplateTypography:
    """Value object for template typography settings."""
    heading_font: str = "Inter"
    body_font: str = "Inter"
    heading_size: str = "24px"
    subheading_size: str = "18px"
    body_size: str = "14px"
    small_size: str = "12px"
    line_height: str = "1.5"
    
    def __post_init__(self):
        """Validate typography settings."""
        if not self.heading_font or not self.body_font:
            raise DomainValidationError("Font names cannot be empty")


@dataclass
class TemplateLayout:
    """Value object for template layout configuration."""
    page_size: str = "A4"  # A4, Letter, Legal, etc.
    margin_top: str = "20mm"
    margin_bottom: str = "20mm"
    margin_left: str = "20mm"
    margin_right: str = "20mm"
    header_height: str = "60mm"
    footer_height: str = "30mm"
    show_logo: bool = True
    logo_position: str = "left"  # left, center, right
    show_watermark: bool = False
    
    def __post_init__(self):
        """Validate layout settings."""
        valid_page_sizes = ["A4", "Letter", "Legal", "A3", "A5"]
        if self.page_size not in valid_page_sizes:
            raise DomainValidationError(f"Invalid page size: {self.page_size}")
        
        valid_positions = ["left", "center", "right"]
        if self.logo_position not in valid_positions:
            raise DomainValidationError(f"Invalid logo position: {self.logo_position}")


@dataclass
class TemplateSections:
    """Value object for controlling template section visibility."""
    show_header: bool = True
    show_footer: bool = True
    show_client_address: bool = True
    show_estimate_details: bool = True
    show_line_items: bool = True
    show_subtotals: bool = True
    show_tax_breakdown: bool = True
    show_terms: bool = True
    show_advance_payment: bool = True
    show_signature_section: bool = True
    show_notes: bool = True
    show_thank_you_message: bool = True
    
    # Custom section ordering
    section_order: List[str] = field(default_factory=lambda: [
        "header", "client_info", "estimate_details", "line_items",
        "subtotals", "advance_payment", "terms", "signature", "footer"
    ])


@dataclass
class TemplateBusinessInfo:
    """Value object for business information in templates."""
    show_business_name: bool = True
    show_business_address: bool = True
    show_business_phone: bool = True
    show_business_email: bool = True
    show_business_website: bool = True
    show_tax_id: bool = False
    show_license_number: bool = False
    custom_fields: Dict[str, str] = field(default_factory=dict)


@dataclass
class EstimateTemplate:
    """
    Estimate template entity for customizable document generation.
    
    Defines the appearance, layout, and content structure for estimate documents
    with business-specific branding and customization options.
    """
    
    # Core identification
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    business_id: Optional[uuid.UUID] = None  # None for system templates
    name: str = ""
    description: Optional[str] = None
    template_type: TemplateType = TemplateType.PROFESSIONAL
    
    # Template status
    is_active: bool = True
    is_default: bool = False
    is_system_template: bool = False
    
    # Design configuration
    color_scheme: TemplateColorScheme = field(default_factory=TemplateColorScheme)
    typography: TemplateTypography = field(default_factory=TemplateTypography)
    layout: TemplateLayout = field(default_factory=TemplateLayout)
    sections: TemplateSections = field(default_factory=TemplateSections)
    business_info: TemplateBusinessInfo = field(default_factory=TemplateBusinessInfo)
    
    # Content customization
    header_text: Optional[str] = None
    footer_text: Optional[str] = None
    thank_you_message: str = "Thank you for considering our services!"
    terms_text: Optional[str] = None
    payment_instructions: Optional[str] = None
    
    # Branding assets
    logo_url: Optional[str] = None
    watermark_url: Optional[str] = None
    signature_image_url: Optional[str] = None
    
    # Template data and styling
    custom_css: Optional[str] = None
    template_data: Dict[str, Any] = field(default_factory=dict)
    
    # Usage statistics
    usage_count: int = 0
    last_used_date: Optional[datetime] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    version: str = "1.0"
    
    # Audit fields
    created_by: Optional[str] = None
    created_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified_by: Optional[str] = None
    
    def __post_init__(self):
        """Initialize and validate template."""
        if not self.name or not self.name.strip():
            raise DomainValidationError("Template name is required")
        
        # System templates cannot belong to a business
        if self.is_system_template and self.business_id:
            raise DomainValidationError("System templates cannot belong to a business")
        
        # Business templates must belong to a business
        if not self.is_system_template and not self.business_id:
            raise DomainValidationError("Business templates must belong to a business")
        
        self._validate_business_rules()
    
    def _validate_business_rules(self) -> None:
        """Validate business rules."""
        # Validate URLs if provided
        if self.logo_url and not self._is_valid_url(self.logo_url):
            raise DomainValidationError("Invalid logo URL")
        
        if self.watermark_url and not self._is_valid_url(self.watermark_url):
            raise DomainValidationError("Invalid watermark URL")
        
        if self.signature_image_url and not self._is_valid_url(self.signature_image_url):
            raise DomainValidationError("Invalid signature image URL")
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation."""
        return url.startswith(('http://', 'https://')) or url.startswith('data:')
    
    # Template management methods
    def activate(self) -> None:
        """Activate the template."""
        self.is_active = True
        self.last_modified = datetime.now(timezone.utc)
    
    def deactivate(self) -> None:
        """Deactivate the template."""
        if self.is_default:
            raise DomainValidationError("Cannot deactivate default template")
        
        self.is_active = False
        self.last_modified = datetime.now(timezone.utc)
    
    def set_as_default(self, set_by: Optional[str] = None) -> None:
        """Set this template as the default."""
        self.is_default = True
        self.last_modified = datetime.now(timezone.utc)
        self.last_modified_by = set_by
    
    def unset_as_default(self, unset_by: Optional[str] = None) -> None:
        """Remove default status from this template."""
        self.is_default = False
        self.last_modified = datetime.now(timezone.utc)
        self.last_modified_by = unset_by
    
    def increment_usage(self) -> None:
        """Increment usage counter."""
        self.usage_count += 1
        self.last_used_date = datetime.now(timezone.utc)
    
    # Content management methods
    def update_color_scheme(self, **colors) -> None:
        """Update color scheme."""
        for key, value in colors.items():
            if hasattr(self.color_scheme, key):
                setattr(self.color_scheme, key, value)
        
        self.last_modified = datetime.now(timezone.utc)
    
    def update_typography(self, **typography_settings) -> None:
        """Update typography settings."""
        for key, value in typography_settings.items():
            if hasattr(self.typography, key):
                setattr(self.typography, key, value)
        
        self.last_modified = datetime.now(timezone.utc)
    
    def update_layout(self, **layout_settings) -> None:
        """Update layout settings."""
        for key, value in layout_settings.items():
            if hasattr(self.layout, key):
                setattr(self.layout, key, value)
        
        self.last_modified = datetime.now(timezone.utc)
    
    def update_sections(self, **section_settings) -> None:
        """Update section visibility settings."""
        for key, value in section_settings.items():
            if hasattr(self.sections, key):
                setattr(self.sections, key, value)
        
        self.last_modified = datetime.now(timezone.utc)
    
    def update_business_info(self, **business_settings) -> None:
        """Update business information settings."""
        for key, value in business_settings.items():
            if hasattr(self.business_info, key):
                setattr(self.business_info, key, value)
        
        self.last_modified = datetime.now(timezone.utc)
    
    # Content methods
    def set_header_text(self, text: str) -> None:
        """Set custom header text."""
        self.header_text = text
        self.last_modified = datetime.now(timezone.utc)
    
    def set_footer_text(self, text: str) -> None:
        """Set custom footer text."""
        self.footer_text = text
        self.last_modified = datetime.now(timezone.utc)
    
    def set_thank_you_message(self, message: str) -> None:
        """Set thank you message."""
        self.thank_you_message = message
        self.last_modified = datetime.now(timezone.utc)
    
    def set_terms_text(self, terms: str) -> None:
        """Set terms and conditions text."""
        self.terms_text = terms
        self.last_modified = datetime.now(timezone.utc)
    
    def set_payment_instructions(self, instructions: str) -> None:
        """Set payment instructions."""
        self.payment_instructions = instructions
        self.last_modified = datetime.now(timezone.utc)
    
    # Asset management
    def set_logo_url(self, url: str) -> None:
        """Set logo URL."""
        if not self._is_valid_url(url):
            raise DomainValidationError("Invalid logo URL")
        
        self.logo_url = url
        self.last_modified = datetime.now(timezone.utc)
    
    def set_watermark_url(self, url: str) -> None:
        """Set watermark URL."""
        if not self._is_valid_url(url):
            raise DomainValidationError("Invalid watermark URL")
        
        self.watermark_url = url
        self.last_modified = datetime.now(timezone.utc)
    
    def set_signature_image_url(self, url: str) -> None:
        """Set signature image URL."""
        if not self._is_valid_url(url):
            raise DomainValidationError("Invalid signature image URL")
        
        self.signature_image_url = url
        self.last_modified = datetime.now(timezone.utc)
    
    # Tag management
    def add_tag(self, tag: str) -> None:
        """Add a tag to the template."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.last_modified = datetime.now(timezone.utc)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the template."""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.last_modified = datetime.now(timezone.utc)
    
    def set_custom_data(self, key: str, value: Any) -> None:
        """Set custom template data."""
        self.template_data[key] = value
        self.last_modified = datetime.now(timezone.utc)
    
    def get_custom_data(self, key: str, default: Any = None) -> Any:
        """Get custom template data."""
        return self.template_data.get(key, default)
    
    # Utility methods
    def clone(self, new_name: str, business_id: Optional[uuid.UUID] = None,
             cloned_by: Optional[str] = None) -> 'EstimateTemplate':
        """Create a copy of this template."""
        return EstimateTemplate(
            business_id=business_id or self.business_id,
            name=new_name,
            description=f"Copy of {self.name}",
            template_type=self.template_type,
            is_active=True,
            is_default=False,
            is_system_template=False,
            color_scheme=self.color_scheme,
            typography=self.typography,
            layout=self.layout,
            sections=self.sections,
            business_info=self.business_info,
            header_text=self.header_text,
            footer_text=self.footer_text,
            thank_you_message=self.thank_you_message,
            terms_text=self.terms_text,
            payment_instructions=self.payment_instructions,
            logo_url=self.logo_url,
            watermark_url=self.watermark_url,
            signature_image_url=self.signature_image_url,
            custom_css=self.custom_css,
            template_data=self.template_data.copy(),
            tags=self.tags.copy(),
            category=self.category,
            created_by=cloned_by
        )
    
    def is_compatible_with_currency(self, currency: CurrencyCode) -> bool:
        """Check if template is compatible with currency."""
        # All templates are compatible with all currencies by default
        # This can be extended for currency-specific formatting
        return True
    
    def get_preview_data(self) -> Dict[str, Any]:
        """Get data for template preview."""
        return {
            "color_scheme": {
                "primary_color": self.color_scheme.primary_color,
                "secondary_color": self.color_scheme.secondary_color,
                "accent_color": self.color_scheme.accent_color,
                "text_color": self.color_scheme.text_color,
                "background_color": self.color_scheme.background_color,
                "border_color": self.color_scheme.border_color
            },
            "typography": {
                "heading_font": self.typography.heading_font,
                "body_font": self.typography.body_font,
                "heading_size": self.typography.heading_size,
                "body_size": self.typography.body_size
            },
            "layout": {
                "page_size": self.layout.page_size,
                "logo_position": self.layout.logo_position,
                "show_logo": self.layout.show_logo,
                "show_watermark": self.layout.show_watermark
            },
            "branding": {
                "logo_url": self.logo_url,
                "watermark_url": self.watermark_url
            }
        }
    
    # Display methods
    def get_type_display(self) -> str:
        """Get human-readable template type."""
        return self.template_type.get_display()
    
    def get_status_display(self) -> str:
        """Get human-readable status."""
        if not self.is_active:
            return "Inactive"
        elif self.is_default:
            return "Default"
        else:
            return "Active"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id) if self.business_id else None,
            "name": self.name,
            "description": self.description,
            "template_type": self.template_type.value,
            "template_type_display": self.get_type_display(),
            "is_active": self.is_active,
            "is_default": self.is_default,
            "is_system_template": self.is_system_template,
            "status_display": self.get_status_display(),
            "color_scheme": {
                "primary_color": self.color_scheme.primary_color,
                "secondary_color": self.color_scheme.secondary_color,
                "accent_color": self.color_scheme.accent_color,
                "text_color": self.color_scheme.text_color,
                "background_color": self.color_scheme.background_color,
                "border_color": self.color_scheme.border_color
            },
            "typography": {
                "heading_font": self.typography.heading_font,
                "body_font": self.typography.body_font,
                "heading_size": self.typography.heading_size,
                "subheading_size": self.typography.subheading_size,
                "body_size": self.typography.body_size,
                "small_size": self.typography.small_size,
                "line_height": self.typography.line_height
            },
            "layout": {
                "page_size": self.layout.page_size,
                "margin_top": self.layout.margin_top,
                "margin_bottom": self.layout.margin_bottom,
                "margin_left": self.layout.margin_left,
                "margin_right": self.layout.margin_right,
                "header_height": self.layout.header_height,
                "footer_height": self.layout.footer_height,
                "show_logo": self.layout.show_logo,
                "logo_position": self.layout.logo_position,
                "show_watermark": self.layout.show_watermark
            },
            "sections": {
                "show_header": self.sections.show_header,
                "show_footer": self.sections.show_footer,
                "show_client_address": self.sections.show_client_address,
                "show_estimate_details": self.sections.show_estimate_details,
                "show_line_items": self.sections.show_line_items,
                "show_subtotals": self.sections.show_subtotals,
                "show_tax_breakdown": self.sections.show_tax_breakdown,
                "show_terms": self.sections.show_terms,
                "show_advance_payment": self.sections.show_advance_payment,
                "show_signature_section": self.sections.show_signature_section,
                "show_notes": self.sections.show_notes,
                "show_thank_you_message": self.sections.show_thank_you_message,
                "section_order": self.sections.section_order
            },
            "business_info": {
                "show_business_name": self.business_info.show_business_name,
                "show_business_address": self.business_info.show_business_address,
                "show_business_phone": self.business_info.show_business_phone,
                "show_business_email": self.business_info.show_business_email,
                "show_business_website": self.business_info.show_business_website,
                "show_tax_id": self.business_info.show_tax_id,
                "show_license_number": self.business_info.show_license_number,
                "custom_fields": self.business_info.custom_fields
            },
            "content": {
                "header_text": self.header_text,
                "footer_text": self.footer_text,
                "thank_you_message": self.thank_you_message,
                "terms_text": self.terms_text,
                "payment_instructions": self.payment_instructions
            },
            "branding": {
                "logo_url": self.logo_url,
                "watermark_url": self.watermark_url,
                "signature_image_url": self.signature_image_url
            },
            "custom_css": self.custom_css,
            "template_data": self.template_data,
            "usage_count": self.usage_count,
            "last_used_date": self.last_used_date.isoformat() if self.last_used_date else None,
            "tags": self.tags,
            "category": self.category,
            "version": self.version,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "last_modified_by": self.last_modified_by,
            "preview_data": self.get_preview_data()
        }
    
    def __str__(self) -> str:
        return f"EstimateTemplate({self.name} - {self.get_type_display()} - {self.get_status_display()})"
    
    def __repr__(self) -> str:
        return (f"EstimateTemplate(id={self.id}, name='{self.name}', "
                f"type={self.template_type}, active={self.is_active}, "
                f"default={self.is_default})") 