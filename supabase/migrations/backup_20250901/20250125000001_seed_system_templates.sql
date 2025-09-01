-- =====================================
-- Seed System Templates Migration
-- =====================================
-- This migration populates the database with the 11 hardcoded templates 
-- from the mobile app as system templates available to all businesses.
-- Date: 2025-01-25
-- Version: System Template Seeding

-- =====================================
-- SEED SYSTEM TEMPLATES
-- =====================================

-- Template 1: Classic Professional (Default for Invoice & Estimate)
INSERT INTO public.templates (
    id, business_id, template_type, category, name, description, version,
    is_active, is_default, is_system, config, tags, metadata,
    created_by, created_at, updated_at
) VALUES (
    gen_random_uuid(), NULL, 'invoice', 'professional',
    'Classic Professional', 
    'Professional template with complete business information and detailed client data',
    1, true, true, true,
    '{
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
            "primary": "#2563EB", "secondary": "#64748B", "accent": "#F1F5F9",
            "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#6B7280", "border": "#E5E7EB"
        },
        "typography": {
            "title": {"font": "System", "size": 28, "weight": "bold"},
            "header": {"font": "System", "size": 14, "weight": "semibold"},
            "body": {"font": "System", "size": 11, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "sections": {
            "invoice_number": {"visible": true}, "dates": {"visible": true}, "client_info": {"visible": true},
            "business_info": {"visible": true}, "line_items": {"visible": true}, "subtotal": {"visible": true},
            "tax": {"visible": true}, "total": {"visible": true}, "payment_terms": {"visible": true},
            "notes": {"visible": true}, "custom_headline": {"visible": false}, "po_number": {"visible": true},
            "project_name": {"visible": true}, "discount": {"visible": false}, "job_reference": {"visible": false},
            "license_number": {"visible": false}, "hourly_rates": {"visible": false}
        },
        "branding": {
            "show_logo": true, "show_business_name": true, "show_address": true,
            "show_phone": true, "show_email": true, "show_website": false, "show_license": false
        },
        "business_rules": {
            "payment_terms": "net_30", "show_due_date": true, "tax_calculation": "exclusive",
            "currency": "usd", "date_format": "mm_dd_yyyy",
            "number_format": {"decimal_places": 2, "thousand_separator": ","}
        }
    }'::jsonb,
    ARRAY['professional', 'detailed', 'business', 'standard'],
    '{"features": ["Company logo placement", "Complete business information", "Detailed client information", "Line items with descriptions", "Tax calculations", "Payment terms", "Professional blue color scheme"], "seeded_at": "2025-01-25", "source": "mobile_app_hardcoded"}'::jsonb,
    'system_migration', NOW(), NOW()
);

-- Template 1 Estimate version
INSERT INTO public.templates (
    id, business_id, template_type, category, name, description, version,
    is_active, is_default, is_system, config, tags, metadata,
    created_by, created_at, updated_at
) VALUES (
    gen_random_uuid(), NULL, 'estimate', 'professional',
    'Classic Professional (Estimate)', 
    'Professional template with complete business information and detailed client data - Estimate version',
    1, true, true, true,
    '{
        "layout": {
            "header_style": "standard", "items_table_style": "detailed", "footer_style": "detailed",
            "logo_position": "top_left", "page_size": "letter", "section_spacing": 16,
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20},
            "column_widths": {"description": 0.5, "quantity": 0.15, "price": 0.2, "total": 0.15}
        },
        "colors": {
            "primary": "#2563EB", "secondary": "#64748B", "accent": "#F1F5F9",
            "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#6B7280", "border": "#E5E7EB"
        },
        "typography": {
            "title": {"font": "System", "size": 28, "weight": "bold"},
            "header": {"font": "System", "size": 14, "weight": "semibold"},
            "body": {"font": "System", "size": 11, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "sections": {
            "invoice_number": {"visible": true}, "dates": {"visible": true}, "client_info": {"visible": true},
            "business_info": {"visible": true}, "line_items": {"visible": true}, "subtotal": {"visible": true},
            "tax": {"visible": true}, "total": {"visible": true}, "payment_terms": {"visible": true},
            "notes": {"visible": true}, "custom_headline": {"visible": false}, "po_number": {"visible": true},
            "project_name": {"visible": true}, "discount": {"visible": false}, "job_reference": {"visible": false},
            "license_number": {"visible": false}, "hourly_rates": {"visible": false}
        },
        "branding": {
            "show_logo": true, "show_business_name": true, "show_address": true,
            "show_phone": true, "show_email": true, "show_website": false, "show_license": false
        },
        "business_rules": {
            "payment_terms": "net_30", "show_due_date": true, "tax_calculation": "exclusive",
            "currency": "usd", "date_format": "mm_dd_yyyy",
            "number_format": {"decimal_places": 2, "thousand_separator": ","}
        }
    }'::jsonb,
    ARRAY['professional', 'detailed', 'business', 'standard'],
    '{"features": ["Company logo placement", "Complete business information", "Detailed client information", "Line items with descriptions", "Tax calculations", "Payment terms", "Professional blue color scheme"], "seeded_at": "2025-01-25", "source": "mobile_app_hardcoded"}'::jsonb,
    'system_migration', NOW(), NOW()
);

-- Template 2: Modern Minimal
INSERT INTO public.templates (
    id, business_id, template_type, category, name, description, version,
    is_active, is_default, is_system, config, tags, metadata,
    created_by, created_at, updated_at
) VALUES (
    gen_random_uuid(), NULL, 'invoice', 'minimal',
    'Modern Minimal', 
    'Clean minimal design with centered logo and essential information only',
    1, true, false, true,
    '{
        "layout": {
            "header_style": "minimal", "items_table_style": "simple", "footer_style": "simple",
            "logo_position": "top_center", "page_size": "letter", "section_spacing": 16,
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
        },
        "colors": {
            "primary": "#1F2937", "secondary": "#6B7280", "accent": "#F9FAFB",
            "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#6B7280", "border": "#E5E7EB"
        },
        "typography": {
            "title": {"font": "System", "size": 24, "weight": "light"},
            "header": {"font": "System", "size": 12, "weight": "medium"},
            "body": {"font": "System", "size": 10, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "sections": {
            "invoice_number": {"visible": true}, "dates": {"visible": true}, "client_info": {"visible": true},
            "business_info": {"visible": false}, "line_items": {"visible": true}, "subtotal": {"visible": true},
            "tax": {"visible": true}, "total": {"visible": true}, "payment_terms": {"visible": false},
            "notes": {"visible": false}, "custom_headline": {"visible": true}, "po_number": {"visible": false},
            "project_name": {"visible": true}
        },
        "branding": {
            "show_logo": true, "show_business_name": true, "show_address": false,
            "show_phone": false, "show_email": true, "show_website": false, "show_license": false
        },
        "business_rules": {
            "payment_terms": "net_30", "show_due_date": true, "tax_calculation": "exclusive",
            "currency": "usd", "date_format": "mm_dd_yyyy"
        }
    }'::jsonb,
    ARRAY['minimal', 'modern', 'clean', 'centered'],
    '{"features": ["Centered logo", "Minimal business details", "Clean typography", "Essential invoice elements only", "Subtle gray tones"], "seeded_at": "2025-01-25", "source": "mobile_app_hardcoded"}'::jsonb,
    'system_migration', NOW(), NOW()
);

-- Template 3: Corporate Bold
INSERT INTO public.templates (
    id, business_id, template_type, category, name, description, version,
    is_active, is_default, is_system, config, tags, metadata,
    created_by, created_at, updated_at
) VALUES (
    gen_random_uuid(), NULL, 'invoice', 'corporate',
    'Corporate Bold', 
    'Bold corporate template with comprehensive information and green theme',
    1, true, false, true,
    '{
        "layout": {
            "header_style": "bold", "items_table_style": "detailed", "footer_style": "detailed",
            "logo_position": "top_right", "page_size": "letter", "section_spacing": 16,
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
        },
        "colors": {
            "primary": "#059669", "secondary": "#047857", "accent": "#D1FAE5",
            "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#6B7280", "border": "#E5E7EB"
        },
        "typography": {
            "title": {"font": "System", "size": 32, "weight": "heavy"},
            "header": {"font": "System", "size": 15, "weight": "bold"},
            "body": {"font": "System", "size": 11, "weight": "medium"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "sections": {
            "invoice_number": {"visible": true}, "dates": {"visible": true}, "client_info": {"visible": true},
            "business_info": {"visible": true}, "line_items": {"visible": true}, "subtotal": {"visible": true},
            "tax": {"visible": true}, "total": {"visible": true}, "payment_terms": {"visible": true},
            "notes": {"visible": true}, "custom_headline": {"visible": true}, "po_number": {"visible": true},
            "project_name": {"visible": true}, "discount": {"visible": true}
        },
        "branding": {
            "show_logo": true, "show_business_name": true, "show_address": true,
            "show_phone": true, "show_email": true, "show_website": true, "show_license": false
        },
        "business_rules": {
            "payment_terms": "net_30", "show_due_date": true, "tax_calculation": "exclusive",
            "currency": "usd", "date_format": "mm_dd_yyyy"
        }
    }'::jsonb,
    ARRAY['corporate', 'bold', 'comprehensive', 'green'],
    '{"features": ["Bold typography", "Right-aligned logo", "Complete contact information", "Discount calculations", "Project context", "Corporate green theme"], "seeded_at": "2025-01-25", "source": "mobile_app_hardcoded"}'::jsonb,
    'system_migration', NOW(), NOW()
);

-- Template 4: Creative Split
INSERT INTO public.templates (
    id, business_id, template_type, category, name, description, version,
    is_active, is_default, is_system, config, tags, metadata,
    created_by, created_at, updated_at
) VALUES (
    gen_random_uuid(), NULL, 'invoice', 'creative',
    'Creative Split', 
    'Creative template with split header layout and modern purple theme',
    1, true, false, true,
    '{
        "layout": {
            "header_style": "split", "items_table_style": "creative", "footer_style": "detailed",
            "logo_position": "header_left", "page_size": "letter", "section_spacing": 16,
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
        },
        "colors": {
            "primary": "#7C3AED", "secondary": "#A855F7", "accent": "#F3E8FF",
            "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#6B7280", "border": "#E5E7EB"
        },
        "typography": {
            "title": {"font": "System", "size": 26, "weight": "semibold"},
            "header": {"font": "System", "size": 13, "weight": "semibold"},
            "body": {"font": "System", "size": 10, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "sections": {
            "invoice_number": {"visible": true}, "dates": {"visible": true}, "client_info": {"visible": true},
            "business_info": {"visible": true}, "line_items": {"visible": true}, "subtotal": {"visible": true},
            "tax": {"visible": true}, "total": {"visible": true}, "payment_terms": {"visible": true},
            "notes": {"visible": true}, "custom_headline": {"visible": true}, "po_number": {"visible": false},
            "project_name": {"visible": true}
        },
        "branding": {
            "show_logo": true, "show_business_name": true, "show_address": true,
            "show_phone": true, "show_email": true, "show_website": false, "show_license": false
        },
        "business_rules": {
            "payment_terms": "net_30", "show_due_date": true, "tax_calculation": "exclusive",
            "currency": "usd", "date_format": "mm_dd_yyyy"
        }
    }'::jsonb,
    ARRAY['creative', 'split', 'modern', 'purple'],
    '{"features": ["Split header layout", "Creative table styling", "Project-based billing", "Custom headlines", "Modern purple theme"], "seeded_at": "2025-01-25", "source": "mobile_app_hardcoded"}'::jsonb,
    'system_migration', NOW(), NOW()
);

-- Template 5: Service Professional
INSERT INTO public.templates (
    id, business_id, template_type, category, name, description, version,
    is_active, is_default, is_system, config, tags, metadata,
    created_by, created_at, updated_at
) VALUES (
    gen_random_uuid(), NULL, 'invoice', 'service_focused',
    'Service Professional', 
    'Service-oriented template with license number display and trade-focused details',
    1, true, false, true,
    '{
        "layout": {
            "header_style": "standard", "items_table_style": "service", "footer_style": "detailed",
            "logo_position": "top_left", "page_size": "letter", "section_spacing": 16,
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
        },
        "colors": {
            "primary": "#DC2626", "secondary": "#991B1B", "accent": "#FEE2E2",
            "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#6B7280", "border": "#E5E7EB"
        },
        "typography": {
            "title": {"font": "System", "size": 28, "weight": "bold"},
            "header": {"font": "System", "size": 14, "weight": "semibold"},
            "body": {"font": "System", "size": 11, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "sections": {
            "invoice_number": {"visible": true}, "dates": {"visible": true}, "client_info": {"visible": true},
            "business_info": {"visible": true}, "line_items": {"visible": true}, "subtotal": {"visible": true},
            "tax": {"visible": true}, "total": {"visible": true}, "payment_terms": {"visible": true},
            "notes": {"visible": true}, "custom_headline": {"visible": false}, "po_number": {"visible": true},
            "project_name": {"visible": true}, "job_reference": {"visible": true}, "license_number": {"visible": true}
        },
        "branding": {
            "show_logo": true, "show_business_name": true, "show_address": true,
            "show_phone": true, "show_email": true, "show_website": true, "show_license": true
        },
        "business_rules": {
            "payment_terms": "net_30", "show_due_date": true, "tax_calculation": "exclusive",
            "currency": "usd", "date_format": "mm_dd_yyyy"
        }
    }'::jsonb,
    ARRAY['service', 'trades', 'license', 'professional'],
    '{"features": ["Service-oriented layout", "License number display", "Job reference tracking", "Professional red theme", "Trade-focused details"], "seeded_at": "2025-01-25", "source": "mobile_app_hardcoded"}'::jsonb,
    'system_migration', NOW(), NOW()
);

-- Template 6: Consulting Elite
INSERT INTO public.templates (
    id, business_id, template_type, category, name, description, version,
    is_active, is_default, is_system, config, tags, metadata,
    created_by, created_at, updated_at
) VALUES (
    gen_random_uuid(), NULL, 'invoice', 'consulting',
    'Consulting Elite', 
    'Premium consulting template with hourly rate display and executive presentation',
    1, true, false, true,
    '{
        "layout": {
            "header_style": "centered", "items_table_style": "consulting", "footer_style": "detailed",
            "logo_position": "top_center", "page_size": "letter", "section_spacing": 16,
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
        },
        "colors": {
            "primary": "#1E40AF", "secondary": "#3B82F6", "accent": "#DBEAFE",
            "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#6B7280", "border": "#E5E7EB"
        },
        "typography": {
            "title": {"font": "System", "size": 30, "weight": "bold"},
            "header": {"font": "System", "size": 14, "weight": "bold"},
            "body": {"font": "System", "size": 11, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "sections": {
            "invoice_number": {"visible": true}, "dates": {"visible": true}, "client_info": {"visible": true},
            "business_info": {"visible": true}, "line_items": {"visible": true}, "subtotal": {"visible": true},
            "tax": {"visible": true}, "total": {"visible": true}, "payment_terms": {"visible": true},
            "notes": {"visible": true}, "custom_headline": {"visible": true}, "po_number": {"visible": true},
            "project_name": {"visible": true}, "hourly_rates": {"visible": true}
        },
        "branding": {
            "show_logo": true, "show_business_name": true, "show_address": true,
            "show_phone": true, "show_email": true, "show_website": true, "show_license": false
        },
        "business_rules": {
            "payment_terms": "net_30", "show_due_date": true, "tax_calculation": "exclusive",
            "currency": "usd", "date_format": "mm_dd_yyyy"
        }
    }'::jsonb,
    ARRAY['consulting', 'premium', 'hourly', 'executive'],
    '{"features": ["Centered header layout", "Hourly rate display", "Project context", "Executive blue theme", "Premium presentation"], "seeded_at": "2025-01-25", "source": "mobile_app_hardcoded"}'::jsonb,
    'system_migration', NOW(), NOW()
);

-- Template 7: Modern Centered
INSERT INTO public.templates (
    id, business_id, template_type, category, name, description, version,
    is_active, is_default, is_system, config, tags, metadata,
    created_by, created_at, updated_at
) VALUES (
    gen_random_uuid(), NULL, 'invoice', 'modern',
    'Modern Centered', 
    'Ultra-modern centered template with simplified information display',
    1, true, false, true,
    '{
        "layout": {
            "header_style": "centered", "items_table_style": "simple", "footer_style": "none",
            "logo_position": "top_center", "page_size": "letter", "section_spacing": 24,
            "margins": {"top": 30, "left": 30, "right": 30, "bottom": 30}
        },
        "colors": {
            "primary": "#6366F1", "secondary": "#8B5CF6", "accent": "#F0F9FF",
            "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#6B7280", "border": "#E5E7EB"
        },
        "typography": {
            "title": {"font": "System", "size": 36, "weight": "light"},
            "header": {"font": "System", "size": 12, "weight": "light"},
            "body": {"font": "System", "size": 10, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "sections": {
            "invoice_number": {"visible": true}, "dates": {"visible": true}, "client_info": {"visible": true},
            "business_info": {"visible": false}, "line_items": {"visible": true}, "subtotal": {"visible": false},
            "tax": {"visible": false}, "total": {"visible": true}, "payment_terms": {"visible": false},
            "notes": {"visible": false}, "custom_headline": {"visible": true}, "project_name": {"visible": true}
        },
        "branding": {
            "show_logo": true, "show_business_name": true, "show_address": false,
            "show_phone": false, "show_email": true, "show_website": false, "show_license": false
        },
        "business_rules": {
            "payment_terms": "net_30", "show_due_date": true, "tax_calculation": "exclusive",
            "currency": "usd", "date_format": "mm_dd_yyyy"
        }
    }'::jsonb,
    ARRAY['modern', 'centered', 'minimal', 'contemporary'],
    '{"features": ["Centered minimalist layout", "Ultra-light typography", "Simplified information display", "Modern indigo accent", "Clean and contemporary"], "seeded_at": "2025-01-25", "source": "mobile_app_hardcoded"}'::jsonb,
    'system_migration', NOW(), NOW()
);

-- Template 8: Classic Monospace  
INSERT INTO public.templates (
    id, business_id, template_type, category, name, description, version,
    is_active, is_default, is_system, config, tags, metadata,
    created_by, created_at, updated_at
) VALUES (
    gen_random_uuid(), NULL, 'invoice', 'classic',
    'Classic Monospace', 
    'Traditional invoice format with monospace typography and classic business layout',
    1, true, false, true,
    '{
        "layout": {
            "header_style": "minimal", "items_table_style": "simple", "footer_style": "simple",
            "logo_position": "top_left", "page_size": "letter", "section_spacing": 20,
            "margins": {"top": 40, "left": 40, "right": 40, "bottom": 40}
        },
        "colors": {
            "primary": "#2D3748", "secondary": "#4A5568", "accent": "#F7FAFC",
            "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#6B7280", "border": "#E5E7EB"
        },
        "typography": {
            "title": {"font": "Menlo", "size": 20, "weight": "bold"},
            "header": {"font": "Menlo", "size": 11, "weight": "regular"},
            "body": {"font": "Menlo", "size": 9, "weight": "regular"},
            "caption": {"font": "Menlo", "size": 9, "weight": "regular"}
        },
        "sections": {
            "invoice_number": {"visible": true}, "dates": {"visible": true}, "client_info": {"visible": true},
            "business_info": {"visible": true}, "line_items": {"visible": true}, "subtotal": {"visible": true},
            "tax": {"visible": true}, "total": {"visible": true}, "payment_terms": {"visible": true},
            "notes": {"visible": true}, "custom_headline": {"visible": false}, "project_name": {"visible": false}
        },
        "branding": {
            "show_logo": false, "show_business_name": true, "show_address": true,
            "show_phone": true, "show_email": true, "show_website": false, "show_license": false
        },
        "business_rules": {
            "payment_terms": "net_30", "show_due_date": true, "tax_calculation": "exclusive",
            "currency": "usd", "date_format": "mm_dd_yyyy"
        }
    }'::jsonb,
    ARRAY['classic', 'monospace', 'traditional', 'charcoal'],
    '{"features": ["Monospace typography", "Classic business layout", "Traditional invoice format", "Charcoal and gray theme", "Timeless professional look"], "seeded_at": "2025-01-25", "source": "mobile_app_hardcoded"}'::jsonb,
    'system_migration', NOW(), NOW()
);

-- Template 9: Bold Creative
INSERT INTO public.templates (
    id, business_id, template_type, category, name, description, version,
    is_active, is_default, is_system, config, tags, metadata,
    created_by, created_at, updated_at
) VALUES (
    gen_random_uuid(), NULL, 'invoice', 'creative',
    'Bold Creative', 
    'Eye-catching creative template with vibrant colors and bold design',
    1, true, false, true,
    '{
        "layout": {
            "header_style": "split", "items_table_style": "creative", "footer_style": "detailed",
            "logo_position": "header_right", "page_size": "letter", "section_spacing": 32,
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20}
        },
        "colors": {
            "primary": "#EC4899", "secondary": "#F59E0B", "accent": "#FDF2F8",
            "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#6B7280", "border": "#E5E7EB"
        },
        "typography": {
            "title": {"font": "System", "size": 32, "weight": "heavy"},
            "header": {"font": "System", "size": 13, "weight": "medium"},
            "body": {"font": "System", "size": 10, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "sections": {
            "invoice_number": {"visible": true}, "dates": {"visible": true}, "client_info": {"visible": true},
            "business_info": {"visible": true}, "line_items": {"visible": true}, "subtotal": {"visible": true},
            "tax": {"visible": true}, "total": {"visible": true}, "payment_terms": {"visible": false},
            "notes": {"visible": true}, "custom_headline": {"visible": true}, "po_number": {"visible": false},
            "project_name": {"visible": true}
        },
        "branding": {
            "show_logo": true, "show_business_name": true, "show_address": false,
            "show_phone": false, "show_email": true, "show_website": true, "show_license": false
        },
        "business_rules": {
            "payment_terms": "net_30", "show_due_date": true, "tax_calculation": "exclusive",
            "currency": "usd", "date_format": "mm_dd_yyyy"
        }
    }'::jsonb,
    ARRAY['creative', 'bold', 'vibrant', 'pink'],
    '{"features": ["Bold creative typography", "Split header design", "Vibrant pink and amber colors", "Eye-catching layout", "Modern creative style"], "seeded_at": "2025-01-25", "source": "mobile_app_hardcoded"}'::jsonb,
    'system_migration', NOW(), NOW()
);

-- Template 10: Executive Bold
INSERT INTO public.templates (
    id, business_id, template_type, category, name, description, version,
    is_active, is_default, is_system, config, tags, metadata,
    created_by, created_at, updated_at
) VALUES (
    gen_random_uuid(), NULL, 'invoice', 'professional',
    'Executive Bold', 
    'Executive-level professional template with comprehensive information and teal theme',
    1, true, false, true,
    '{
        "layout": {
            "header_style": "bold", "items_table_style": "detailed", "footer_style": "detailed",
            "logo_position": "top_left", "page_size": "letter", "section_spacing": 18,
            "margins": {"top": 25, "left": 25, "right": 25, "bottom": 25}
        },
        "colors": {
            "primary": "#0F766E", "secondary": "#134E4A", "accent": "#F0FDFA",
            "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#6B7280", "border": "#E5E7EB"
        },
        "typography": {
            "title": {"font": "System", "size": 24, "weight": "semibold"},
            "header": {"font": "System", "size": 13, "weight": "semibold"},
            "body": {"font": "System", "size": 11, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "sections": {
            "invoice_number": {"visible": true}, "dates": {"visible": true}, "client_info": {"visible": true},
            "business_info": {"visible": true}, "line_items": {"visible": true}, "subtotal": {"visible": true},
            "tax": {"visible": true}, "total": {"visible": true}, "payment_terms": {"visible": true},
            "notes": {"visible": true}, "custom_headline": {"visible": false}, "po_number": {"visible": true},
            "project_name": {"visible": false}, "license_number": {"visible": false}
        },
        "branding": {
            "show_logo": true, "show_business_name": true, "show_address": true,
            "show_phone": true, "show_email": true, "show_website": true, "show_license": false
        },
        "business_rules": {
            "payment_terms": "net_30", "show_due_date": true, "tax_calculation": "exclusive",
            "currency": "usd", "date_format": "mm_dd_yyyy"
        }
    }'::jsonb,
    ARRAY['executive', 'professional', 'comprehensive', 'teal'],
    '{"features": ["Bold professional layout", "Comprehensive information", "Professional teal theme", "Detailed formatting", "Executive presentation"], "seeded_at": "2025-01-25", "source": "mobile_app_hardcoded"}'::jsonb,
    'system_migration', NOW(), NOW()
);

-- Template 11: Clean Simple
INSERT INTO public.templates (
    id, business_id, template_type, category, name, description, version,
    is_active, is_default, is_system, config, tags, metadata,
    created_by, created_at, updated_at
) VALUES (
    gen_random_uuid(), NULL, 'invoice', 'minimal',
    'Clean Simple', 
    'Streamlined minimal template with essential details only and compact layout',
    1, true, false, true,
    '{
        "layout": {
            "header_style": "minimal", "items_table_style": "simple", "footer_style": "none",
            "logo_position": "top_right", "page_size": "letter", "section_spacing": 16,
            "margins": {"top": 16, "left": 16, "right": 16, "bottom": 16}
        },
        "colors": {
            "primary": "#374151", "secondary": "#6B7280", "accent": "#F9FAFB",
            "background": "#FFFFFF", "text_primary": "#000000", "text_secondary": "#6B7280", "border": "#E5E7EB"
        },
        "typography": {
            "title": {"font": "System", "size": 22, "weight": "medium"},
            "header": {"font": "System", "size": 11, "weight": "regular"},
            "body": {"font": "System", "size": 10, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "sections": {
            "invoice_number": {"visible": true}, "dates": {"visible": true}, "client_info": {"visible": true},
            "business_info": {"visible": false}, "line_items": {"visible": true}, "subtotal": {"visible": false},
            "tax": {"visible": false}, "total": {"visible": true}, "payment_terms": {"visible": false},
            "notes": {"visible": false}, "custom_headline": {"visible": false}, "po_number": {"visible": false},
            "project_name": {"visible": true}
        },
        "branding": {
            "show_logo": false, "show_business_name": true, "show_address": false,
            "show_phone": false, "show_email": true, "show_website": false, "show_license": false
        },
        "business_rules": {
            "payment_terms": "net_30", "show_due_date": true, "tax_calculation": "exclusive",
            "currency": "usd", "date_format": "mm_dd_yyyy"
        }
    }'::jsonb,
    ARRAY['minimal', 'simple', 'streamlined', 'compact'],
    '{"features": ["Minimal information display", "Clean gray monochrome", "Essential details only", "Compact layout", "Streamlined design"], "seeded_at": "2025-01-25", "source": "mobile_app_hardcoded"}'::jsonb,
    'system_migration', NOW(), NOW()
);

-- =====================================
-- CREATE ESTIMATE VERSIONS OF TEMPLATES 2-11
-- =====================================
-- Create estimate versions for all templates (2-11) except Classic Professional which is already done

-- Modern Minimal (Estimate)
INSERT INTO public.templates (id, business_id, template_type, category, name, description, version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by)
SELECT gen_random_uuid(), business_id, 'estimate', category, name || ' (Estimate)', description || ' - Estimate version', version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by 
FROM public.templates WHERE name = 'Modern Minimal' AND template_type = 'invoice';

-- Corporate Bold (Estimate)
INSERT INTO public.templates (id, business_id, template_type, category, name, description, version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by)
SELECT gen_random_uuid(), business_id, 'estimate', category, name || ' (Estimate)', description || ' - Estimate version', version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by 
FROM public.templates WHERE name = 'Corporate Bold' AND template_type = 'invoice';

-- Creative Split (Estimate)
INSERT INTO public.templates (id, business_id, template_type, category, name, description, version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by)
SELECT gen_random_uuid(), business_id, 'estimate', category, name || ' (Estimate)', description || ' - Estimate version', version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by 
FROM public.templates WHERE name = 'Creative Split' AND template_type = 'invoice';

-- Service Professional (Estimate)
INSERT INTO public.templates (id, business_id, template_type, category, name, description, version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by)
SELECT gen_random_uuid(), business_id, 'estimate', category, name || ' (Estimate)', description || ' - Estimate version', version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by 
FROM public.templates WHERE name = 'Service Professional' AND template_type = 'invoice';

-- Consulting Elite (Estimate)
INSERT INTO public.templates (id, business_id, template_type, category, name, description, version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by)
SELECT gen_random_uuid(), business_id, 'estimate', category, name || ' (Estimate)', description || ' - Estimate version', version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by 
FROM public.templates WHERE name = 'Consulting Elite' AND template_type = 'invoice';

-- Modern Centered (Estimate)
INSERT INTO public.templates (id, business_id, template_type, category, name, description, version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by)
SELECT gen_random_uuid(), business_id, 'estimate', category, name || ' (Estimate)', description || ' - Estimate version', version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by 
FROM public.templates WHERE name = 'Modern Centered' AND template_type = 'invoice';

-- Classic Monospace (Estimate)
INSERT INTO public.templates (id, business_id, template_type, category, name, description, version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by)
SELECT gen_random_uuid(), business_id, 'estimate', category, name || ' (Estimate)', description || ' - Estimate version', version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by 
FROM public.templates WHERE name = 'Classic Monospace' AND template_type = 'invoice';

-- Bold Creative (Estimate)
INSERT INTO public.templates (id, business_id, template_type, category, name, description, version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by)
SELECT gen_random_uuid(), business_id, 'estimate', category, name || ' (Estimate)', description || ' - Estimate version', version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by 
FROM public.templates WHERE name = 'Bold Creative' AND template_type = 'invoice';

-- Executive Bold (Estimate)
INSERT INTO public.templates (id, business_id, template_type, category, name, description, version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by)
SELECT gen_random_uuid(), business_id, 'estimate', category, name || ' (Estimate)', description || ' - Estimate version', version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by 
FROM public.templates WHERE name = 'Executive Bold' AND template_type = 'invoice';

-- Clean Simple (Estimate)
INSERT INTO public.templates (id, business_id, template_type, category, name, description, version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by)
SELECT gen_random_uuid(), business_id, 'estimate', category, name || ' (Estimate)', description || ' - Estimate version', version, is_active, is_default, is_system, config, usage_count, last_used_at, tags, metadata, created_by, created_at, updated_at, updated_by 
FROM public.templates WHERE name = 'Clean Simple' AND template_type = 'invoice';

-- =====================================
-- COMMENTS AND DOCUMENTATION
-- =====================================
COMMENT ON COLUMN public.templates.config IS 'System templates seeded from mobile app hardcoded templates - contains complete layout, colors, typography, sections, branding, and business rules configuration';

-- =====================================
-- VERIFICATION QUERIES
-- =====================================
-- View all seeded system templates
-- SELECT name, template_type, category, is_system, is_default, 
--        jsonb_pretty(config->'colors') as colors,
--        array_to_string(tags, ', ') as tags
-- FROM public.templates 
-- WHERE is_system = true 
-- ORDER BY template_type, name;
