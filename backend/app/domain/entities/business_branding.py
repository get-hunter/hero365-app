"""
Business Branding Domain Entity

Centralized branding configuration for all business components including
websites, estimates, invoices, and other customer-facing materials.
"""

import uuid
from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
from enum import Enum

from ..exceptions.domain_exceptions import DomainValidationError


class BrandingTheme(str, Enum):
    """Predefined branding themes."""
    PROFESSIONAL = "professional"
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMAL = "minimal"
    BOLD = "bold"
    FRIENDLY = "friendly"
    INDUSTRIAL = "industrial"
    RESIDENTIAL = "residential"
    CUSTOM = "custom"


class ColorScheme(BaseModel):
    """Unified color scheme for all business materials."""
    
    # Primary brand colors
    primary_color: str = Field(default="#2563eb", description="Main brand color")
    secondary_color: str = Field(default="#64748b", description="Supporting color")
    accent_color: str = Field(default="#10b981", description="Call-to-action color")
    
    # Text colors
    text_color: str = Field(default="#1f2937", description="Main text color")
    heading_color: str = Field(default="#111827", description="Heading text color")
    muted_text_color: str = Field(default="#6b7280", description="Secondary text color")
    
    # Background colors
    background_color: str = Field(default="#ffffff", description="Main background")
    surface_color: str = Field(default="#f9fafb", description="Card/section background")
    border_color: str = Field(default="#e5e7eb", description="Border color")
    
    # Status colors (shared across all components)
    success_color: str = Field(default="#10b981", description="Success/approved status")
    warning_color: str = Field(default="#f59e0b", description="Warning/pending status")
    error_color: str = Field(default="#ef4444", description="Error/rejected status")
    info_color: str = Field(default="#3b82f6", description="Info/neutral status")
    
    # Trade-specific color hints (optional)
    trade_accent: Optional[str] = Field(None, description="Trade-specific accent color")
    
    @field_validator('*')
    @classmethod
    def validate_color(cls, v, info):
        """Validate hex color codes."""
        if v is None:
            return v
        if not isinstance(v, str):
            return v
        if not v.startswith('#'):
            raise ValueError(f"Color must start with #: {v}")
        
        hex_part = v[1:]
        if len(hex_part) not in [3, 6, 8]:  # Support alpha channel
            raise ValueError(f"Invalid hex color length: {v}")
        
        try:
            int(hex_part, 16)
        except ValueError:
            raise ValueError(f"Invalid hex color code: {v}")
        
        return v.upper()


class Typography(BaseModel):
    """Unified typography settings for all materials."""
    
    # Font families
    heading_font: str = Field(default="Inter", description="Font for headings")
    body_font: str = Field(default="Inter", description="Font for body text")
    mono_font: str = Field(default="Courier New", description="Font for codes/numbers")
    
    # Font sizes (using relative units for responsiveness)
    heading_1_size: str = Field(default="2.5rem", description="H1 size")
    heading_2_size: str = Field(default="2rem", description="H2 size")
    heading_3_size: str = Field(default="1.5rem", description="H3 size")
    body_size: str = Field(default="1rem", description="Body text size")
    small_size: str = Field(default="0.875rem", description="Small text size")
    
    # Font weights
    heading_weight: str = Field(default="700", description="Heading font weight")
    body_weight: str = Field(default="400", description="Body font weight")
    bold_weight: str = Field(default="600", description="Bold text weight")
    
    # Line heights
    heading_line_height: str = Field(default="1.2", description="Heading line height")
    body_line_height: str = Field(default="1.6", description="Body line height")
    
    # Letter spacing
    heading_letter_spacing: str = Field(default="-0.02em", description="Heading letter spacing")
    body_letter_spacing: str = Field(default="0", description="Body letter spacing")
    
    @field_validator('heading_font', 'body_font', 'mono_font')
    @classmethod
    def validate_font(cls, v):
        """Validate font names."""
        if not v or not v.strip():
            raise ValueError("Font name cannot be empty")
        return v.strip()


class BrandAssets(BaseModel):
    """Centralized brand assets used across all materials."""
    
    # Logos
    logo_url: Optional[HttpUrl] = Field(None, description="Primary logo URL")
    logo_dark_url: Optional[HttpUrl] = Field(None, description="Logo for dark backgrounds")
    logo_icon_url: Optional[HttpUrl] = Field(None, description="Icon-only logo")
    favicon_url: Optional[HttpUrl] = Field(None, description="Favicon for websites")
    
    # Additional branding
    watermark_url: Optional[HttpUrl] = Field(None, description="Watermark image")
    signature_image_url: Optional[HttpUrl] = Field(None, description="Digital signature")
    banner_image_url: Optional[HttpUrl] = Field(None, description="Banner/header image")
    
    # Trade-specific imagery
    trade_badge_url: Optional[HttpUrl] = Field(None, description="Trade certification badge")
    trade_hero_image_url: Optional[HttpUrl] = Field(None, description="Trade-specific hero image")
    
    # Social media assets
    social_share_image_url: Optional[HttpUrl] = Field(None, description="OG image for social sharing")
    
    class Config:
        json_encoders = {
            HttpUrl: str
        }


class BusinessBranding(BaseModel):
    """
    Centralized branding configuration for a business.
    
    This entity manages all brand-related settings that are shared across
    websites, estimates, invoices, and other business materials.
    """
    
    # Core identification
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    
    # Branding theme
    theme: BrandingTheme = Field(default=BrandingTheme.PROFESSIONAL)
    theme_name: str = Field(default="Default Brand")
    
    # Core branding components
    color_scheme: ColorScheme = Field(default_factory=ColorScheme)
    typography: Typography = Field(default_factory=Typography)
    assets: BrandAssets = Field(default_factory=BrandAssets)
    
    # Trade-specific customizations
    trade_customizations: Dict[str, Any] = Field(
        default_factory=dict,
        description="Trade-specific branding overrides"
    )
    
    # Component-specific settings
    website_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enable_animations": True,
            "enable_dark_mode": False,
            "corner_radius": "8px",
            "shadow_style": "medium"
        }
    )
    
    document_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "page_size": "A4",
            "margin": "20mm",
            "show_watermark": False,
            "watermark_opacity": 0.1
        }
    )
    
    email_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "header_style": "centered",
            "footer_style": "minimal",
            "include_social_links": True
        }
    )
    
    # Custom CSS overrides
    custom_css: Optional[str] = Field(None, description="Global custom CSS")
    
    # Metadata
    is_active: bool = Field(default=True)
    version: str = Field(default="1.0")
    tags: List[str] = Field(default_factory=list)
    
    # Audit fields
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    last_modified_by: Optional[str] = None
    
    def apply_trade_theme(self, trade_type: str, trade_category: str) -> 'BusinessBranding':
        """
        Apply trade-specific theme adjustments.
        
        Args:
            trade_type: The specific trade (e.g., 'plumbing', 'electrical')
            trade_category: The category ('commercial', 'residential', 'both')
        
        Returns:
            Updated branding instance
        """
        trade_themes = {
            # Commercial trades tend toward professional/industrial
            "commercial": {
                "mechanical": {"primary_color": "#374151", "accent_color": "#ef4444"},
                "electrical": {"primary_color": "#f59e0b", "accent_color": "#3b82f6"},
                "plumbing": {"primary_color": "#3b82f6", "accent_color": "#10b981"},
                "security_systems": {"primary_color": "#dc2626", "accent_color": "#1f2937"},
                "roofing": {"primary_color": "#7c3aed", "accent_color": "#f59e0b"},
            },
            # Residential trades tend toward friendly/approachable
            "residential": {
                "hvac": {"primary_color": "#3b82f6", "accent_color": "#ef4444"},
                "plumbing": {"primary_color": "#06b6d4", "accent_color": "#10b981"},
                "electrical": {"primary_color": "#fbbf24", "accent_color": "#1f2937"},
                "painting": {"primary_color": "#8b5cf6", "accent_color": "#ec4899"},
                "pest_control": {"primary_color": "#10b981", "accent_color": "#f59e0b"},
            }
        }
        
        # Apply trade-specific colors if available
        if trade_category in trade_themes:
            if trade_type in trade_themes[trade_category]:
                trade_colors = trade_themes[trade_category][trade_type]
                for key, value in trade_colors.items():
                    if hasattr(self.color_scheme, key):
                        setattr(self.color_scheme, key, value)
        
        # Store customization
        self.trade_customizations = {
            "trade_type": trade_type,
            "trade_category": trade_category,
            "applied_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.last_modified = datetime.now(timezone.utc)
        return self
    
    def get_css_variables(self) -> str:
        """
        Generate CSS custom properties for web components.
        
        Returns:
            CSS string with custom properties
        """
        css_vars = [":root {"]
        
        # Color variables
        css_vars.append(f"  --color-primary: {self.color_scheme.primary_color};")
        css_vars.append(f"  --color-secondary: {self.color_scheme.secondary_color};")
        css_vars.append(f"  --color-accent: {self.color_scheme.accent_color};")
        css_vars.append(f"  --color-text: {self.color_scheme.text_color};")
        css_vars.append(f"  --color-heading: {self.color_scheme.heading_color};")
        css_vars.append(f"  --color-muted: {self.color_scheme.muted_text_color};")
        css_vars.append(f"  --color-background: {self.color_scheme.background_color};")
        css_vars.append(f"  --color-surface: {self.color_scheme.surface_color};")
        css_vars.append(f"  --color-border: {self.color_scheme.border_color};")
        css_vars.append(f"  --color-success: {self.color_scheme.success_color};")
        css_vars.append(f"  --color-warning: {self.color_scheme.warning_color};")
        css_vars.append(f"  --color-error: {self.color_scheme.error_color};")
        css_vars.append(f"  --color-info: {self.color_scheme.info_color};")
        
        # Typography variables
        css_vars.append(f"  --font-heading: '{self.typography.heading_font}', sans-serif;")
        css_vars.append(f"  --font-body: '{self.typography.body_font}', sans-serif;")
        css_vars.append(f"  --font-mono: '{self.typography.mono_font}', monospace;")
        css_vars.append(f"  --size-h1: {self.typography.heading_1_size};")
        css_vars.append(f"  --size-h2: {self.typography.heading_2_size};")
        css_vars.append(f"  --size-h3: {self.typography.heading_3_size};")
        css_vars.append(f"  --size-body: {self.typography.body_size};")
        css_vars.append(f"  --size-small: {self.typography.small_size};")
        css_vars.append(f"  --weight-heading: {self.typography.heading_weight};")
        css_vars.append(f"  --weight-body: {self.typography.body_weight};")
        css_vars.append(f"  --weight-bold: {self.typography.bold_weight};")
        css_vars.append(f"  --line-height-heading: {self.typography.heading_line_height};")
        css_vars.append(f"  --line-height-body: {self.typography.body_line_height};")
        
        css_vars.append("}")
        
        # Add custom CSS if provided
        if self.custom_css:
            css_vars.append(self.custom_css)
        
        return "\n".join(css_vars)
    
    def get_template_config(self, component: str = "estimate") -> Dict[str, Any]:
        """
        Get branding configuration for specific component templates.
        
        Args:
            component: The component type ('estimate', 'invoice', 'website', 'email')
        
        Returns:
            Configuration dictionary for the component
        """
        base_config = {
            "color_scheme": self.color_scheme.model_dump(),
            "typography": self.typography.model_dump(),
            "assets": self.assets.model_dump(exclude_none=True),
            "theme": self.theme.value
        }
        
        # Add component-specific settings
        if component == "website":
            base_config.update(self.website_settings)
        elif component in ["estimate", "invoice"]:
            base_config.update(self.document_settings)
        elif component == "email":
            base_config.update(self.email_settings)
        
        return base_config
    
    def clone(self, new_name: str) -> 'BusinessBranding':
        """Create a copy of this branding configuration."""
        return BusinessBranding(
            business_id=self.business_id,
            theme=self.theme,
            theme_name=new_name,
            color_scheme=self.color_scheme.model_copy(),
            typography=self.typography.model_copy(),
            assets=self.assets.model_copy(),
            trade_customizations=self.trade_customizations.copy(),
            website_settings=self.website_settings.copy(),
            document_settings=self.document_settings.copy(),
            email_settings=self.email_settings.copy(),
            custom_css=self.custom_css,
            tags=self.tags.copy()
        )
    
    def export_for_figma(self) -> Dict[str, Any]:
        """Export branding as Figma-compatible design tokens."""
        return {
            "colors": {
                "primary": {"value": self.color_scheme.primary_color},
                "secondary": {"value": self.color_scheme.secondary_color},
                "accent": {"value": self.color_scheme.accent_color},
                "text": {
                    "default": {"value": self.color_scheme.text_color},
                    "heading": {"value": self.color_scheme.heading_color},
                    "muted": {"value": self.color_scheme.muted_text_color}
                },
                "background": {
                    "default": {"value": self.color_scheme.background_color},
                    "surface": {"value": self.color_scheme.surface_color}
                },
                "border": {"value": self.color_scheme.border_color},
                "status": {
                    "success": {"value": self.color_scheme.success_color},
                    "warning": {"value": self.color_scheme.warning_color},
                    "error": {"value": self.color_scheme.error_color},
                    "info": {"value": self.color_scheme.info_color}
                }
            },
            "typography": {
                "fontFamilies": {
                    "heading": {"value": self.typography.heading_font},
                    "body": {"value": self.typography.body_font},
                    "mono": {"value": self.typography.mono_font}
                },
                "fontSizes": {
                    "h1": {"value": self.typography.heading_1_size},
                    "h2": {"value": self.typography.heading_2_size},
                    "h3": {"value": self.typography.heading_3_size},
                    "body": {"value": self.typography.body_size},
                    "small": {"value": self.typography.small_size}
                },
                "fontWeights": {
                    "heading": {"value": self.typography.heading_weight},
                    "body": {"value": self.typography.body_weight},
                    "bold": {"value": self.typography.bold_weight}
                },
                "lineHeights": {
                    "heading": {"value": self.typography.heading_line_height},
                    "body": {"value": self.typography.body_line_height}
                }
            }
        }
    
    class Config:
        use_enum_values = True
        validate_assignment = True
