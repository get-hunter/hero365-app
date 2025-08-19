#!/usr/bin/env python3
"""
Seed System Templates Script

Populates the database with the 11 hardcoded templates from the mobile app.
These templates are available to all businesses by default.

Run with: python -m scripts.seed_system_templates
"""

import asyncio
import logging
import sys
import uuid
from typing import Dict, Any, List

# Add the backend directory to Python path
sys.path.append('.')

from app.core.config import settings
from app.domain.entities.template import Template, TemplateType, TemplateCategory
from app.infrastructure.config.dependency_injection import get_supabase_client
from app.infrastructure.database.repositories.supabase_template_repository import SupabaseTemplateRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# System template configurations based on mobile app hardcoded templates
SYSTEM_TEMPLATES = [
    {
        "name": "Classic Professional",
        "template_type": TemplateType.INVOICE,
        "category": TemplateCategory.PROFESSIONAL,
        "description": "Professional template with complete business information and detailed client data",
        "is_default": True,  # Default for both invoice and estimate
        "tags": ["professional", "detailed", "business", "standard"],
        "features": [
            "Company logo placement", "Complete business information", "Detailed client information", 
            "Line items with descriptions", "Tax calculations", "Payment terms", "Professional blue color scheme"
        ],
        "config": {
            "layout": {
                "header_style": "standard",
                "items_table_style": "detailed",
                "footer_style": "detailed",
                "logo_position": "top_left",
                "page_size": "letter",
                "section_spacing": 16,
                "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20},
                "column_widths": {"description": 0.5, "quantity": 0.15, "price": 0.2, "total": 0.15}
            },
            "colors": {
                "primary": "#2563EB",
                "secondary": "#64748B", 
                "accent": "#F1F5F9",
                "background": "#FFFFFF",
                "text_primary": "#000000",
                "text_secondary": "#6B7280",
                "border": "#E5E7EB"
            },
            "typography": {
                "title": {"font": "System", "size": 28, "weight": "bold"},
                "header": {"font": "System", "size": 14, "weight": "semibold"},
                "body": {"font": "System", "size": 11, "weight": "regular"},
                "caption": {"font": "System", "size": 9, "weight": "regular"}
            },
            "sections": {
                "invoice_number": {"visible": True},
                "dates": {"visible": True},
                "client_info": {"visible": True},
                "business_info": {"visible": True},
                "line_items": {"visible": True},
                "subtotal": {"visible": True},
                "tax": {"visible": True},
                "total": {"visible": True},
                "payment_terms": {"visible": True},
                "notes": {"visible": True},
                "custom_headline": {"visible": False},
                "po_number": {"visible": True},
                "project_name": {"visible": True},
                "discount": {"visible": False},
                "job_reference": {"visible": False},
                "license_number": {"visible": False},
                "hourly_rates": {"visible": False}
            },
            "branding": {
                "show_logo": True,
                "show_business_name": True,
                "show_address": True,
                "show_phone": True,
                "show_email": True,
                "show_website": False,
                "show_license": False
            },
            "business_rules": {
                "payment_terms": "net_30",
                "show_due_date": True,
                "tax_calculation": "exclusive",
                "currency": "usd",
                "date_format": "mm_dd_yyyy",
                "number_format": {"decimal_places": 2, "thousand_separator": ","}
            }
        }
    },
    {
        "name": "Modern Minimal", 
        "template_type": TemplateType.INVOICE,
        "category": TemplateCategory.MINIMAL,
        "description": "Clean minimal design with centered logo and essential information only",
        "tags": ["minimal", "modern", "clean", "centered"],
        "features": [
            "Centered logo", "Minimal business details", "Clean typography", 
            "Essential invoice elements only", "Subtle gray tones"
        ],
        "config": {
            "layout": {
                "header_style": "minimal",
                "items_table_style": "simple",
                "footer_style": "simple", 
                "logo_position": "top_center",
                "page_size": "letter",
                "section_spacing": 16,
                "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
            },
            "colors": {
                "primary": "#1F2937",
                "secondary": "#6B7280",
                "accent": "#F9FAFB",
                "background": "#FFFFFF",
                "text_primary": "#000000",
                "text_secondary": "#6B7280",
                "border": "#E5E7EB"
            },
            "typography": {
                "title": {"font": "System", "size": 24, "weight": "light"},
                "header": {"font": "System", "size": 12, "weight": "medium"},
                "body": {"font": "System", "size": 10, "weight": "regular"},
                "caption": {"font": "System", "size": 9, "weight": "regular"}
            },
            "sections": {
                "invoice_number": {"visible": True},
                "dates": {"visible": True},
                "client_info": {"visible": True},
                "business_info": {"visible": False},
                "line_items": {"visible": True},
                "subtotal": {"visible": True},
                "tax": {"visible": True},
                "total": {"visible": True},
                "payment_terms": {"visible": False},
                "notes": {"visible": False},
                "custom_headline": {"visible": True},
                "po_number": {"visible": False},
                "project_name": {"visible": True}
            },
            "branding": {
                "show_logo": True,
                "show_business_name": True,
                "show_address": False,
                "show_phone": False,
                "show_email": True,
                "show_website": False,
                "show_license": False
            },
            "business_rules": {
                "payment_terms": "net_30",
                "show_due_date": True,
                "tax_calculation": "exclusive",
                "currency": "usd",
                "date_format": "mm_dd_yyyy"
            }
        }
    },
    {
        "name": "Corporate Bold",
        "template_type": TemplateType.INVOICE,
        "category": TemplateCategory.CORPORATE,
        "description": "Bold corporate template with comprehensive information and green theme",
        "tags": ["corporate", "bold", "comprehensive", "green"],
        "features": [
            "Bold typography", "Right-aligned logo", "Complete contact information",
            "Discount calculations", "Project context", "Corporate green theme"
        ],
        "config": {
            "layout": {
                "header_style": "bold",
                "items_table_style": "detailed",
                "footer_style": "detailed",
                "logo_position": "top_right",
                "page_size": "letter",
                "section_spacing": 16,
                "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
            },
            "colors": {
                "primary": "#059669",
                "secondary": "#047857", 
                "accent": "#D1FAE5",
                "background": "#FFFFFF",
                "text_primary": "#000000",
                "text_secondary": "#6B7280",
                "border": "#E5E7EB"
            },
            "typography": {
                "title": {"font": "System", "size": 32, "weight": "heavy"},
                "header": {"font": "System", "size": 15, "weight": "bold"},
                "body": {"font": "System", "size": 11, "weight": "medium"},
                "caption": {"font": "System", "size": 9, "weight": "regular"}
            },
            "sections": {
                "invoice_number": {"visible": True},
                "dates": {"visible": True},
                "client_info": {"visible": True},
                "business_info": {"visible": True},
                "line_items": {"visible": True},
                "subtotal": {"visible": True},
                "tax": {"visible": True},
                "total": {"visible": True},
                "payment_terms": {"visible": True},
                "notes": {"visible": True},
                "custom_headline": {"visible": True},
                "po_number": {"visible": True},
                "project_name": {"visible": True},
                "discount": {"visible": True}
            },
            "branding": {
                "show_logo": True,
                "show_business_name": True,
                "show_address": True,
                "show_phone": True,
                "show_email": True,
                "show_website": True,
                "show_license": False
            },
            "business_rules": {
                "payment_terms": "net_30",
                "show_due_date": True,
                "tax_calculation": "exclusive",
                "currency": "usd",
                "date_format": "mm_dd_yyyy"
            }
        }
    },
    {
        "name": "Creative Split",
        "template_type": TemplateType.INVOICE,
        "category": TemplateCategory.CREATIVE,
        "description": "Creative template with split header layout and modern purple theme",
        "tags": ["creative", "split", "modern", "purple"],
        "features": [
            "Split header layout", "Creative table styling", "Project-based billing",
            "Custom headlines", "Modern purple theme"
        ],
        "config": {
            "layout": {
                "header_style": "split",
                "items_table_style": "creative",
                "footer_style": "detailed",
                "logo_position": "header_left",
                "page_size": "letter",
                "section_spacing": 16,
                "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
            },
            "colors": {
                "primary": "#7C3AED",
                "secondary": "#A855F7",
                "accent": "#F3E8FF",
                "background": "#FFFFFF",
                "text_primary": "#000000",
                "text_secondary": "#6B7280",
                "border": "#E5E7EB"
            },
            "typography": {
                "title": {"font": "System", "size": 26, "weight": "semibold"},
                "header": {"font": "System", "size": 13, "weight": "semibold"},
                "body": {"font": "System", "size": 10, "weight": "regular"},
                "caption": {"font": "System", "size": 9, "weight": "regular"}
            },
            "sections": {
                "invoice_number": {"visible": True},
                "dates": {"visible": True},
                "client_info": {"visible": True},
                "business_info": {"visible": True},
                "line_items": {"visible": True},
                "subtotal": {"visible": True},
                "tax": {"visible": True},
                "total": {"visible": True},
                "payment_terms": {"visible": True},
                "notes": {"visible": True},
                "custom_headline": {"visible": True},
                "po_number": {"visible": False},
                "project_name": {"visible": True}
            },
            "branding": {
                "show_logo": True,
                "show_business_name": True,
                "show_address": True,
                "show_phone": True,
                "show_email": True,
                "show_website": False,
                "show_license": False
            },
            "business_rules": {
                "payment_terms": "net_30",
                "show_due_date": True,
                "tax_calculation": "exclusive",
                "currency": "usd",
                "date_format": "mm_dd_yyyy"
            }
        }
    },
    {
        "name": "Service Professional",
        "template_type": TemplateType.INVOICE,
        "category": TemplateCategory.SERVICE_FOCUSED,
        "description": "Service-oriented template with license number display and trade-focused details",
        "tags": ["service", "trades", "license", "professional"],
        "features": [
            "Service-oriented layout", "License number display", "Job reference tracking",
            "Professional red theme", "Trade-focused details"
        ],
        "config": {
            "layout": {
                "header_style": "standard",
                "items_table_style": "service",
                "footer_style": "detailed",
                "logo_position": "top_left",
                "page_size": "letter",
                "section_spacing": 16,
                "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
            },
            "colors": {
                "primary": "#DC2626",
                "secondary": "#991B1B",
                "accent": "#FEE2E2",
                "background": "#FFFFFF",
                "text_primary": "#000000",
                "text_secondary": "#6B7280",
                "border": "#E5E7EB"
            },
            "typography": {
                "title": {"font": "System", "size": 28, "weight": "bold"},
                "header": {"font": "System", "size": 14, "weight": "semibold"},
                "body": {"font": "System", "size": 11, "weight": "regular"},
                "caption": {"font": "System", "size": 9, "weight": "regular"}
            },
            "sections": {
                "invoice_number": {"visible": True},
                "dates": {"visible": True},
                "client_info": {"visible": True},
                "business_info": {"visible": True},
                "line_items": {"visible": True},
                "subtotal": {"visible": True},
                "tax": {"visible": True},
                "total": {"visible": True},
                "payment_terms": {"visible": True},
                "notes": {"visible": True},
                "custom_headline": {"visible": False},
                "po_number": {"visible": True},
                "project_name": {"visible": True},
                "job_reference": {"visible": True},
                "license_number": {"visible": True}
            },
            "branding": {
                "show_logo": True,
                "show_business_name": True,
                "show_address": True,
                "show_phone": True,
                "show_email": True,
                "show_website": True,
                "show_license": True
            },
            "business_rules": {
                "payment_terms": "net_30",
                "show_due_date": True,
                "tax_calculation": "exclusive",
                "currency": "usd",
                "date_format": "mm_dd_yyyy"
            }
        }
    },
    {
        "name": "Consulting Elite",
        "template_type": TemplateType.INVOICE,
        "category": TemplateCategory.CONSULTING,
        "description": "Premium consulting template with hourly rate display and executive presentation",
        "tags": ["consulting", "premium", "hourly", "executive"],
        "features": [
            "Centered header layout", "Hourly rate display", "Project context",
            "Executive blue theme", "Premium presentation"
        ],
        "config": {
            "layout": {
                "header_style": "centered",
                "items_table_style": "consulting",
                "footer_style": "detailed",
                "logo_position": "top_center",
                "page_size": "letter",
                "section_spacing": 16,
                "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
            },
            "colors": {
                "primary": "#1E40AF",
                "secondary": "#3B82F6",
                "accent": "#DBEAFE",
                "background": "#FFFFFF",
                "text_primary": "#000000",
                "text_secondary": "#6B7280",
                "border": "#E5E7EB"
            },
            "typography": {
                "title": {"font": "System", "size": 30, "weight": "bold"},
                "header": {"font": "System", "size": 14, "weight": "bold"},
                "body": {"font": "System", "size": 11, "weight": "regular"},
                "caption": {"font": "System", "size": 9, "weight": "regular"}
            },
            "sections": {
                "invoice_number": {"visible": True},
                "dates": {"visible": True},
                "client_info": {"visible": True},
                "business_info": {"visible": True},
                "line_items": {"visible": True},
                "subtotal": {"visible": True},
                "tax": {"visible": True},
                "total": {"visible": True},
                "payment_terms": {"visible": True},
                "notes": {"visible": True},
                "custom_headline": {"visible": True},
                "po_number": {"visible": True},
                "project_name": {"visible": True},
                "hourly_rates": {"visible": True}
            },
            "branding": {
                "show_logo": True,
                "show_business_name": True,
                "show_address": True,
                "show_phone": True,
                "show_email": True,
                "show_website": True,
                "show_license": False
            },
            "business_rules": {
                "payment_terms": "net_30",
                "show_due_date": True,
                "tax_calculation": "exclusive",
                "currency": "usd",
                "date_format": "mm_dd_yyyy"
            }
        }
    },
    {
        "name": "Modern Centered",
        "template_type": TemplateType.INVOICE,
        "category": TemplateCategory.MODERN,
        "description": "Ultra-modern centered template with simplified information display",
        "tags": ["modern", "centered", "minimal", "contemporary"],
        "features": [
            "Centered minimalist layout", "Ultra-light typography", "Simplified information display",
            "Modern indigo accent", "Clean and contemporary"
        ],
        "config": {
            "layout": {
                "header_style": "centered",
                "items_table_style": "simple",
                "footer_style": "none",
                "logo_position": "top_center",
                "page_size": "letter",
                "section_spacing": 24,
                "margins": {"top": 30, "left": 30, "right": 30, "bottom": 30}
            },
            "colors": {
                "primary": "#6366F1",
                "secondary": "#8B5CF6",
                "accent": "#F0F9FF",
                "background": "#FFFFFF",
                "text_primary": "#000000",
                "text_secondary": "#6B7280",
                "border": "#E5E7EB"
            },
            "typography": {
                "title": {"font": "System", "size": 36, "weight": "light"},
                "header": {"font": "System", "size": 12, "weight": "light"},
                "body": {"font": "System", "size": 10, "weight": "regular"},
                "caption": {"font": "System", "size": 9, "weight": "regular"}
            },
            "sections": {
                "invoice_number": {"visible": True},
                "dates": {"visible": True},
                "client_info": {"visible": True},
                "business_info": {"visible": False},
                "line_items": {"visible": True},
                "subtotal": {"visible": False},
                "tax": {"visible": False},
                "total": {"visible": True},
                "payment_terms": {"visible": False},
                "notes": {"visible": False},
                "custom_headline": {"visible": True},
                "project_name": {"visible": True}
            },
            "branding": {
                "show_logo": True,
                "show_business_name": True,
                "show_address": False,
                "show_phone": False,
                "show_email": True,
                "show_website": False,
                "show_license": False
            },
            "business_rules": {
                "payment_terms": "net_30",
                "show_due_date": True,
                "tax_calculation": "exclusive",
                "currency": "usd",
                "date_format": "mm_dd_yyyy"
            }
        }
    },
    {
        "name": "Classic Monospace",
        "template_type": TemplateType.INVOICE,
        "category": TemplateCategory.CLASSIC,
        "description": "Traditional invoice format with monospace typography and classic business layout",
        "tags": ["classic", "monospace", "traditional", "charcoal"],
        "features": [
            "Monospace typography", "Classic business layout", "Traditional invoice format",
            "Charcoal and gray theme", "Timeless professional look"
        ],
        "config": {
            "layout": {
                "header_style": "minimal",
                "items_table_style": "simple",
                "footer_style": "simple",
                "logo_position": "top_left",
                "page_size": "letter",
                "section_spacing": 20,
                "margins": {"top": 40, "left": 40, "right": 40, "bottom": 40}
            },
            "colors": {
                "primary": "#2D3748",
                "secondary": "#4A5568",
                "accent": "#F7FAFC",
                "background": "#FFFFFF",
                "text_primary": "#000000",
                "text_secondary": "#6B7280",
                "border": "#E5E7EB"
            },
            "typography": {
                "title": {"font": "Menlo", "size": 20, "weight": "bold"},
                "header": {"font": "Menlo", "size": 11, "weight": "regular"},
                "body": {"font": "Menlo", "size": 9, "weight": "regular"},
                "caption": {"font": "Menlo", "size": 9, "weight": "regular"}
            },
            "sections": {
                "invoice_number": {"visible": True},
                "dates": {"visible": True},
                "client_info": {"visible": True},
                "business_info": {"visible": True},
                "line_items": {"visible": True},
                "subtotal": {"visible": True},
                "tax": {"visible": True},
                "total": {"visible": True},
                "payment_terms": {"visible": True},
                "notes": {"visible": True},
                "custom_headline": {"visible": False},
                "project_name": {"visible": False}
            },
            "branding": {
                "show_logo": False,
                "show_business_name": True,
                "show_address": True,
                "show_phone": True,
                "show_email": True,
                "show_website": False,
                "show_license": False
            },
            "business_rules": {
                "payment_terms": "net_30",
                "show_due_date": True,
                "tax_calculation": "exclusive",
                "currency": "usd",
                "date_format": "mm_dd_yyyy"
            }
        }
    },
    {
        "name": "Bold Creative",
        "template_type": TemplateType.INVOICE,
        "category": TemplateCategory.CREATIVE,
        "description": "Eye-catching creative template with vibrant colors and bold design",
        "tags": ["creative", "bold", "vibrant", "pink"],
        "features": [
            "Bold creative typography", "Split header design", "Vibrant pink and amber colors",
            "Eye-catching layout", "Modern creative style"
        ],
        "config": {
            "layout": {
                "header_style": "split",
                "items_table_style": "creative",
                "footer_style": "detailed",
                "logo_position": "header_right",
                "page_size": "letter",
                "section_spacing": 32,
                "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
            },
            "colors": {
                "primary": "#EC4899",
                "secondary": "#F59E0B",
                "accent": "#FDF2F8",
                "background": "#FFFFFF",
                "text_primary": "#000000",
                "text_secondary": "#6B7280",
                "border": "#E5E7EB"
            },
            "typography": {
                "title": {"font": "System", "size": 32, "weight": "heavy"},
                "header": {"font": "System", "size": 13, "weight": "medium"},
                "body": {"font": "System", "size": 10, "weight": "regular"},
                "caption": {"font": "System", "size": 9, "weight": "regular"}
            },
            "sections": {
                "invoice_number": {"visible": True},
                "dates": {"visible": True},
                "client_info": {"visible": True},
                "business_info": {"visible": True},
                "line_items": {"visible": True},
                "subtotal": {"visible": True},
                "tax": {"visible": True},
                "total": {"visible": True},
                "payment_terms": {"visible": False},
                "notes": {"visible": True},
                "custom_headline": {"visible": True},
                "po_number": {"visible": False},
                "project_name": {"visible": True}
            },
            "branding": {
                "show_logo": True,
                "show_business_name": True,
                "show_address": False,
                "show_phone": False,
                "show_email": True,
                "show_website": True,
                "show_license": False
            },
            "business_rules": {
                "payment_terms": "net_30",
                "show_due_date": True,
                "tax_calculation": "exclusive",
                "currency": "usd",
                "date_format": "mm_dd_yyyy"
            }
        }
    },
    {
        "name": "Executive Bold",
        "template_type": TemplateType.INVOICE,
        "category": TemplateCategory.PROFESSIONAL,
        "description": "Executive-level professional template with comprehensive information and teal theme",
        "tags": ["executive", "professional", "comprehensive", "teal"],
        "features": [
            "Bold professional layout", "Comprehensive information", "Professional teal theme",
            "Detailed formatting", "Executive presentation"
        ],
        "config": {
            "layout": {
                "header_style": "bold",
                "items_table_style": "detailed",
                "footer_style": "detailed",
                "logo_position": "top_left",
                "page_size": "letter",
                "section_spacing": 18,
                "margins": {"top": 25, "left": 25, "right": 25, "bottom": 25}
            },
            "colors": {
                "primary": "#0F766E",
                "secondary": "#134E4A",
                "accent": "#F0FDFA",
                "background": "#FFFFFF",
                "text_primary": "#000000",
                "text_secondary": "#6B7280",
                "border": "#E5E7EB"
            },
            "typography": {
                "title": {"font": "System", "size": 24, "weight": "semibold"},
                "header": {"font": "System", "size": 13, "weight": "semibold"},
                "body": {"font": "System", "size": 11, "weight": "regular"},
                "caption": {"font": "System", "size": 9, "weight": "regular"}
            },
            "sections": {
                "invoice_number": {"visible": True},
                "dates": {"visible": True},
                "client_info": {"visible": True},
                "business_info": {"visible": True},
                "line_items": {"visible": True},
                "subtotal": {"visible": True},
                "tax": {"visible": True},
                "total": {"visible": True},
                "payment_terms": {"visible": True},
                "notes": {"visible": True},
                "custom_headline": {"visible": False},
                "po_number": {"visible": True},
                "project_name": {"visible": False},
                "license_number": {"visible": False}
            },
            "branding": {
                "show_logo": True,
                "show_business_name": True,
                "show_address": True,
                "show_phone": True,
                "show_email": True,
                "show_website": True,
                "show_license": False
            },
            "business_rules": {
                "payment_terms": "net_30",
                "show_due_date": True,
                "tax_calculation": "exclusive",
                "currency": "usd",
                "date_format": "mm_dd_yyyy"
            }
        }
    },
    {
        "name": "Clean Simple",
        "template_type": TemplateType.INVOICE,
        "category": TemplateCategory.MINIMAL,
        "description": "Streamlined minimal template with essential details only and compact layout",
        "tags": ["minimal", "simple", "streamlined", "compact"],
        "features": [
            "Minimal information display", "Clean gray monochrome", "Essential details only",
            "Compact layout", "Streamlined design"
        ],
        "config": {
            "layout": {
                "header_style": "minimal",
                "items_table_style": "simple",
                "footer_style": "none",
                "logo_position": "top_right",
                "page_size": "letter",
                "section_spacing": 16,
                "margins": {"top": 16, "left": 16, "right": 16, "bottom": 16}
            },
            "colors": {
                "primary": "#374151",
                "secondary": "#6B7280",
                "accent": "#F9FAFB",
                "background": "#FFFFFF",
                "text_primary": "#000000",
                "text_secondary": "#6B7280",
                "border": "#E5E7EB"
            },
            "typography": {
                "title": {"font": "System", "size": 22, "weight": "medium"},
                "header": {"font": "System", "size": 11, "weight": "regular"},
                "body": {"font": "System", "size": 10, "weight": "regular"},
                "caption": {"font": "System", "size": 9, "weight": "regular"}
            },
            "sections": {
                "invoice_number": {"visible": True},
                "dates": {"visible": True},
                "client_info": {"visible": True},
                "business_info": {"visible": False},
                "line_items": {"visible": True},
                "subtotal": {"visible": False},
                "tax": {"visible": False},
                "total": {"visible": True},
                "payment_terms": {"visible": False},
                "notes": {"visible": False},
                "custom_headline": {"visible": False},
                "po_number": {"visible": False},
                "project_name": {"visible": True}
            },
            "branding": {
                "show_logo": False,
                "show_business_name": True,
                "show_address": False,
                "show_phone": False,
                "show_email": True,
                "show_website": False,
                "show_license": False
            },
            "business_rules": {
                "payment_terms": "net_30",
                "show_due_date": True,
                "tax_calculation": "exclusive",
                "currency": "usd",
                "date_format": "mm_dd_yyyy"
            }
        }
    }
]


class SystemTemplateSeeder:
    """Service for seeding system templates."""
    
    def __init__(self):
        self.supabase_client = get_supabase_client()
        self.template_repository = SupabaseTemplateRepository(self.supabase_client)
    
    async def check_existing_templates(self) -> Dict[str, bool]:
        """Check which system templates already exist."""
        existing_templates = {}
        
        for template_data in SYSTEM_TEMPLATES:
            try:
                # Search for existing template by name and system flag
                result = self.supabase_client.table("templates").select("id, name").eq("name", template_data["name"]).eq("is_system", True).execute()
                existing_templates[template_data["name"]] = len(result.data) > 0
            except Exception as e:
                logger.warning(f"Error checking template {template_data['name']}: {e}")
                existing_templates[template_data["name"]] = False
                
        return existing_templates
    
    async def seed_template(self, template_data: Dict[str, Any]) -> bool:
        """Seed a single template."""
        try:
            # Add features to metadata
            metadata = {
                "features": template_data.get("features", []),
                "seeded_at": "2025-01-25",
                "source": "mobile_app_hardcoded"
            }
            
            # Create template entity
            template = Template(
                business_id=None,  # System template
                template_type=template_data["template_type"],
                category=template_data["category"],
                name=template_data["name"],
                description=template_data["description"],
                is_system=True,
                is_active=True,
                is_default=template_data.get("is_default", False),
                config=template_data["config"],
                tags=template_data.get("tags", []),
                metadata=metadata,
                created_by="system_seeder"
            )
            
            # Save to database
            created_template = await self.template_repository.create(template)
            logger.info(f"✅ Created system template: {created_template.name}")
            
            # Set as default for both invoice and estimate if specified
            if template_data.get("is_default", False):
                # Set as default for invoice
                await self.template_repository.set_as_default(
                    template_id=created_template.id,
                    business_id=None,  # System default
                    template_type=TemplateType.INVOICE
                )
                
                # Also create estimate version and set as default
                estimate_template = template.model_copy(update={
                    'id': uuid.uuid4(),
                    'template_type': TemplateType.ESTIMATE,
                    'name': template_data["name"] + " (Estimate)",
                    'description': template_data["description"] + " - Estimate version"
                })
                
                created_estimate_template = await self.template_repository.create(estimate_template)
                await self.template_repository.set_as_default(
                    template_id=created_estimate_template.id,
                    business_id=None,  # System default
                    template_type=TemplateType.ESTIMATE
                )
                
                logger.info(f"✅ Set as default: {created_template.name} (Invoice & Estimate)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create template {template_data['name']}: {e}")
            return False
    
    async def seed_all_templates(self, force: bool = False) -> Dict[str, Any]:
        """Seed all system templates."""
        logger.info("🚀 Starting system template seeding...")
        
        # Check existing templates
        existing_templates = await self.check_existing_templates()
        
        results = {
            "total": len(SYSTEM_TEMPLATES),
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "templates": []
        }
        
        for template_data in SYSTEM_TEMPLATES:
            template_name = template_data["name"]
            
            # Skip if already exists (unless force)
            if existing_templates.get(template_name, False) and not force:
                logger.info(f"⏭️  Skipped existing template: {template_name}")
                results["skipped"] += 1
                results["templates"].append({"name": template_name, "status": "skipped"})
                continue
            
            # Seed template
            success = await self.seed_template(template_data)
            
            if success:
                results["created"] += 1
                results["templates"].append({"name": template_name, "status": "created"})
            else:
                results["failed"] += 1
                results["templates"].append({"name": template_name, "status": "failed"})
        
        logger.info(f"✅ Seeding completed: {results['created']} created, {results['skipped']} skipped, {results['failed']} failed")
        return results


async def main():
    """Main seeding function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed system templates")
    parser.add_argument("--force", action="store_true", help="Force recreate existing templates")
    args = parser.parse_args()
    
    seeder = SystemTemplateSeeder()
    results = await seeder.seed_all_templates(force=args.force)
    
    print("\n" + "="*50)
    print("SYSTEM TEMPLATE SEEDING RESULTS")
    print("="*50)
    print(f"Total templates: {results['total']}")
    print(f"Created: {results['created']}")
    print(f"Skipped: {results['skipped']}")
    print(f"Failed: {results['failed']}")
    print("\nTemplate Details:")
    for template in results['templates']:
        status_emoji = {"created": "✅", "skipped": "⏭️", "failed": "❌"}
        print(f"{status_emoji[template['status']]} {template['name']}: {template['status']}")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
