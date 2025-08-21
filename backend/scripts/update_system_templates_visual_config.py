#!/usr/bin/env python3
"""
Update System Templates with Enhanced Visual Configuration

This script updates existing system templates with the new visual_config
structure to support mobile app template differentiation.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.domain.entities.template import TemplateType, TemplateCategory, LayoutStyle
from app.infrastructure.config.dependency_injection import get_manage_templates_use_case
from app.core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced visual configurations for different template styles
VISUAL_CONFIGURATIONS = {
    LayoutStyle.EMERGENCY_SERVICE: {
        "layout_style": "creative_split",
        "enhanced_colors": {
            "header_background": "#DC2626",
            "header_text": "#FFFFFF",
            "table_header": "#FEF3C7",
            "accent": "#FEF3C7"
        },
        "header_style": {
            "type": "split",
            "height": "medium",
            "show_logo": True,
            "logo_position": "left",
            "show_border": True,
            "border_style": "solid"
        },
        "layout_elements": {
            "side_panel": {
                "enabled": True,
                "position": "left",
                "width": "narrow"
            },
            "accent_bars": {
                "enabled": True,
                "position": "left",
                "thickness": "medium"
            },
            "spacing": {
                "sections": "normal",
                "elements": "normal"
            }
        },
        "visual_theme": {
            "border_radius": 4,
            "shadow_style": "subtle",
            "line_style": "solid",
            "table_style": "modern"
        }
    },
    
    LayoutStyle.CORPORATE_BOLD: {
        "layout_style": "corporate_bold",
        "enhanced_colors": {
            "header_background": "#1E40AF",
            "header_text": "#FFFFFF",
            "table_header": "#DBEAFE",
            "accent": "#DBEAFE"
        },
        "header_style": {
            "type": "bold",
            "height": "large",
            "show_logo": True,
            "logo_position": "left",
            "show_border": True,
            "border_style": "solid"
        },
        "layout_elements": {
            "side_panel": {
                "enabled": False
            },
            "accent_bars": {
                "enabled": True,
                "position": "left",
                "thickness": "medium"
            },
            "spacing": {
                "sections": "normal",
                "elements": "normal"
            }
        },
        "visual_theme": {
            "border_radius": 2,
            "shadow_style": "prominent",
            "line_style": "solid",
            "table_style": "bordered"
        }
    },
    
    LayoutStyle.ELEGANT_SIMPLE: {
        "layout_style": "elegant_simple",
        "enhanced_colors": {
            "header_background": "#374151",
            "header_text": "#FFFFFF",
            "table_header": "#F9FAFB",
            "accent": "#F3F4F6"
        },
        "header_style": {
            "type": "centered",
            "height": "medium",
            "show_logo": True,
            "logo_position": "center",
            "show_border": True,
            "border_style": "solid"
        },
        "layout_elements": {
            "side_panel": {
                "enabled": False
            },
            "accent_bars": {
                "enabled": False
            },
            "spacing": {
                "sections": "spacious",
                "elements": "loose"
            }
        },
        "visual_theme": {
            "border_radius": 8,
            "shadow_style": "none",
            "line_style": "solid",
            "table_style": "minimal"
        }
    },
    
    LayoutStyle.MODERN_MINIMAL: {
        "layout_style": "modern_minimal",
        "enhanced_colors": {
            "header_background": "#F8FAFC",
            "header_text": "#1F2937",
            "table_header": "#F1F5F9",
            "accent": "#E2E8F0"
        },
        "header_style": {
            "type": "minimal",
            "height": "small",
            "show_logo": True,
            "logo_position": "left",
            "show_border": False,
            "border_style": "none"
        },
        "layout_elements": {
            "side_panel": {
                "enabled": False
            },
            "accent_bars": {
                "enabled": True,
                "position": "top",
                "thickness": "thin"
            },
            "spacing": {
                "sections": "compact",
                "elements": "tight"
            }
        },
        "visual_theme": {
            "border_radius": 0,
            "shadow_style": "none",
            "line_style": "solid",
            "table_style": "minimal"
        }
    },
    
    LayoutStyle.PROFESSIONAL: {
        "layout_style": "professional",
        "enhanced_colors": {
            "header_background": "#2563EB",
            "header_text": "#FFFFFF",
            "table_header": "#F1F5F9",
            "accent": "#F1F5F9"
        },
        "header_style": {
            "type": "standard",
            "height": "medium",
            "show_logo": True,
            "logo_position": "left",
            "show_border": True,
            "border_style": "solid"
        },
        "layout_elements": {
            "side_panel": {
                "enabled": False
            },
            "accent_bars": {
                "enabled": False
            },
            "spacing": {
                "sections": "normal",
                "elements": "normal"
            }
        },
        "visual_theme": {
            "border_radius": 4,
            "shadow_style": "subtle",
            "line_style": "solid",
            "table_style": "striped"
        }
    }
}

# Template name to layout style mapping
TEMPLATE_NAME_MAPPINGS = {
    # Emergency/Service templates
    "emergency": LayoutStyle.CREATIVE_SPLIT,
    "urgent": LayoutStyle.CREATIVE_SPLIT,
    "24/7": LayoutStyle.CREATIVE_SPLIT,
    "service": LayoutStyle.CREATIVE_SPLIT,
    
    # Corporate templates
    "professional": LayoutStyle.CORPORATE_BOLD,
    "plumbing": LayoutStyle.CORPORATE_BOLD,
    "corporate": LayoutStyle.CORPORATE_BOLD,
    "business": LayoutStyle.CORPORATE_BOLD,
    
    # Classic templates
    "classic": LayoutStyle.ELEGANT_SIMPLE,
    "traditional": LayoutStyle.ELEGANT_SIMPLE,
    "elegant": LayoutStyle.ELEGANT_SIMPLE,
    
    # Modern templates
    "modern": LayoutStyle.MODERN_MINIMAL,
    "minimal": LayoutStyle.MODERN_MINIMAL,
    "clean": LayoutStyle.MODERN_MINIMAL,
    "simple": LayoutStyle.MODERN_MINIMAL,
}


def detect_layout_style_from_name(template_name: str) -> LayoutStyle:
    """Detect layout style from template name."""
    name_lower = template_name.lower()
    
    for keyword, layout_style in TEMPLATE_NAME_MAPPINGS.items():
        if keyword in name_lower:
            return layout_style
    
    return LayoutStyle.PROFESSIONAL


async def update_template_visual_config(use_case, template, layout_style: LayoutStyle):
    """Update a template with enhanced visual configuration."""
    
    # Get the visual configuration for this layout style
    visual_config = VISUAL_CONFIGURATIONS.get(layout_style, VISUAL_CONFIGURATIONS[LayoutStyle.PROFESSIONAL])
    
    # Update the template config with visual_config
    updated_config = template.config.copy()
    updated_config["visual_config"] = visual_config
    
    # Update the template
    updated_template = await use_case.update_template(
        template_id=template.id,
        config=updated_config,
        updated_by="system_visual_config_update"
    )
    
    logger.info(f"Updated template '{template.name}' with layout_style: {layout_style.value}")
    return updated_template


async def main():
    """Main function to update all system templates."""
    logger.info("Starting system templates visual configuration update...")
    
    try:
        # Get the use case
        use_case = get_manage_templates_use_case()
        
        # Get all system templates
        system_templates = await use_case.get_system_templates()
        logger.info(f"Found {len(system_templates)} system templates")
        
        updated_count = 0
        
        for template in system_templates:
            # Skip if already has visual_config
            if template.config.get("visual_config"):
                logger.info(f"Template '{template.name}' already has visual_config, skipping")
                continue
            
            # Detect layout style from name
            layout_style = detect_layout_style_from_name(template.name)
            
            # Update template
            try:
                await update_template_visual_config(use_case, template, layout_style)
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to update template '{template.name}': {str(e)}")
        
        logger.info(f"Successfully updated {updated_count} templates with visual configuration")
        
    except Exception as e:
        logger.error(f"Error updating system templates: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
