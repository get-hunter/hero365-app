-- =====================================
-- Seed Built-in Templates for Template System
-- =====================================
-- This migration seeds the 11 built-in templates using the new template structure.
-- Each template is created for both invoice and estimate types where applicable.

-- Helper function to create built-in templates
CREATE OR REPLACE FUNCTION seed_builtin_template(
    p_name VARCHAR,
    p_template_type VARCHAR,
    p_category VARCHAR,
    p_config JSONB,
    p_is_default BOOLEAN DEFAULT FALSE
)
RETURNS UUID AS $$
DECLARE
    v_template_id UUID;
BEGIN
    INSERT INTO public.templates (
        business_id,
        template_type,
        category,
        name,
        description,
        is_active,
        is_default,
        is_system,
        config,
        created_by,
        created_at,
        updated_at
    ) VALUES (
        NULL, -- System template
        p_template_type,
        p_category,
        p_name,
        p_name || ' - ' || p_category || ' template for ' || p_template_type,
        TRUE,
        p_is_default,
        TRUE, -- System template
        p_config,
        'system',
        NOW(),
        NOW()
    ) RETURNING id INTO v_template_id;
    
    RETURN v_template_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- CREATE INVOICE AND ESTIMATE TEMPLATES
-- =====================================

DO $$
DECLARE
    v_template_config JSONB;
    v_template_types TEXT[] := ARRAY['invoice', 'estimate'];
    v_template_type TEXT;
BEGIN
    -- 1. Classic Professional (DEFAULT)
    v_template_config := '{
        "layout": {
            "header_style": "standard",
            "items_table_style": "detailed",
            "footer_style": "detailed",
            "logo_position": "top_left",
            "page_size": "letter",
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20},
            "section_spacing": 16
        },
        "sections": {
            "header": {"visible": true, "style": "standard"},
            "business_info": {"visible": true, "fields": ["name", "address", "phone", "email"]},
            "client_info": {"visible": true, "fields": ["name", "address", "phone", "email"]},
            "line_items": {"visible": true, "columns": ["description", "quantity", "rate", "amount"]},
            "totals": {"visible": true, "show_subtotal": true, "show_tax": true, "show_discount": false},
            "payment_terms": {"visible": true},
            "notes": {"visible": true},
            "footer": {"visible": true, "content": "Thank you for your business!"}
        },
        "colors": {
            "primary": "#2563EB",
            "secondary": "#64748B",
            "accent": "#F1F5F9",
            "text_primary": "#000000",
            "text_secondary": "#6B7280",
            "border": "#E2E8F0",
            "background": "#FFFFFF"
        },
        "typography": {
            "title": {"font": "System", "size": 28, "weight": "bold"},
            "header": {"font": "System", "size": 14, "weight": "semibold"},
            "body": {"font": "System", "size": 11, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "business_rules": {
            "payment_terms": "net_30",
            "late_fees": {"enabled": false, "percentage": 0},
            "tax_calculation": "exclusive",
            "currency": "usd",
            "date_format": "mm_dd_yyyy"
        },
        "custom_fields": [
            {"key": "po_number", "label": "PO Number", "type": "text", "required": false}
        ]
    }'::JSONB;
    
    FOREACH v_template_type IN ARRAY v_template_types LOOP
        PERFORM seed_builtin_template(
            'Classic Professional',
            v_template_type,
            'professional',
            v_template_config,
            TRUE -- Set as default
        );
    END LOOP;

    -- 2. Modern Minimal
    v_template_config := '{
        "layout": {
            "header_style": "minimal",
            "items_table_style": "simple",
            "footer_style": "simple",
            "logo_position": "top_center",
            "page_size": "letter",
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20},
            "section_spacing": 16
        },
        "sections": {
            "header": {"visible": true, "style": "minimal"},
            "business_info": {"visible": false},
            "client_info": {"visible": true, "fields": ["name", "email"]},
            "line_items": {"visible": true, "columns": ["description", "amount"]},
            "totals": {"visible": true, "show_subtotal": true, "show_tax": true},
            "payment_terms": {"visible": false},
            "notes": {"visible": false},
            "footer": {"visible": true, "content": ""}
        },
        "colors": {
            "primary": "#1F2937",
            "secondary": "#6B7280",
            "accent": "#F9FAFB",
            "text_primary": "#1F2937",
            "text_secondary": "#6B7280",
            "border": "#E5E7EB",
            "background": "#FFFFFF"
        },
        "typography": {
            "title": {"font": "System", "size": 24, "weight": "light"},
            "header": {"font": "System", "size": 12, "weight": "medium"},
            "body": {"font": "System", "size": 10, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "business_rules": {
            "payment_terms": "immediate",
            "tax_calculation": "exclusive",
            "currency": "usd",
            "date_format": "mm_dd_yyyy"
        }
    }'::JSONB;
    
    FOREACH v_template_type IN ARRAY v_template_types LOOP
        PERFORM seed_builtin_template(
            'Modern Minimal',
            v_template_type,
            'minimal',
            v_template_config,
            FALSE
        );
    END LOOP;

    -- 3. Corporate Bold
    v_template_config := '{
        "layout": {
            "header_style": "bold",
            "items_table_style": "detailed",
            "footer_style": "detailed",
            "logo_position": "top_right",
            "page_size": "letter",
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20},
            "section_spacing": 16
        },
        "sections": {
            "header": {"visible": true, "style": "bold"},
            "business_info": {"visible": true, "fields": ["name", "address", "phone", "email", "website"]},
            "client_info": {"visible": true, "fields": ["name", "address", "phone", "email"]},
            "line_items": {"visible": true, "columns": ["description", "quantity", "rate", "discount", "amount"]},
            "totals": {"visible": true, "show_subtotal": true, "show_tax": true, "show_discount": true},
            "payment_terms": {"visible": true},
            "notes": {"visible": true},
            "footer": {"visible": true}
        },
        "colors": {
            "primary": "#059669",
            "secondary": "#047857",
            "accent": "#D1FAE5",
            "text_primary": "#000000",
            "text_secondary": "#6B7280",
            "border": "#E2E8F0",
            "background": "#FFFFFF"
        },
        "typography": {
            "title": {"font": "System", "size": 32, "weight": "bold"},
            "header": {"font": "System", "size": 15, "weight": "bold"},
            "body": {"font": "System", "size": 11, "weight": "medium"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "business_rules": {
            "payment_terms": "net_30",
            "late_fees": {"enabled": true, "percentage": 1.5},
            "tax_calculation": "exclusive",
            "currency": "usd",
            "date_format": "mm_dd_yyyy"
        },
        "custom_fields": [
            {"key": "po_number", "label": "PO Number", "type": "text", "required": false},
            {"key": "project_name", "label": "Project", "type": "text", "required": false}
        ]
    }'::JSONB;
    
    FOREACH v_template_type IN ARRAY v_template_types LOOP
        PERFORM seed_builtin_template(
            'Corporate Bold',
            v_template_type,
            'corporate',
            v_template_config,
            FALSE
        );
    END LOOP;

    -- 4. Creative Split
    v_template_config := '{
        "layout": {
            "header_style": "split",
            "items_table_style": "creative",
            "footer_style": "detailed",
            "logo_position": "header_left",
            "page_size": "letter",
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20},
            "section_spacing": 16
        },
        "sections": {
            "header": {"visible": true, "style": "split"},
            "business_info": {"visible": true},
            "client_info": {"visible": true},
            "line_items": {"visible": true, "columns": ["description", "quantity", "rate", "amount"]},
            "totals": {"visible": true, "show_subtotal": true, "show_tax": true},
            "payment_terms": {"visible": true},
            "notes": {"visible": true},
            "footer": {"visible": true}
        },
        "colors": {
            "primary": "#7C3AED",
            "secondary": "#A855F7",
            "accent": "#F3E8FF",
            "text_primary": "#000000",
            "text_secondary": "#6B7280",
            "border": "#E2E8F0",
            "background": "#FFFFFF"
        },
        "typography": {
            "title": {"font": "System", "size": 26, "weight": "semibold"},
            "header": {"font": "System", "size": 13, "weight": "semibold"},
            "body": {"font": "System", "size": 10, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "business_rules": {
            "payment_terms": "net_15",
            "tax_calculation": "exclusive",
            "currency": "usd",
            "date_format": "mm_dd_yyyy"
        }
    }'::JSONB;
    
    FOREACH v_template_type IN ARRAY v_template_types LOOP
        PERFORM seed_builtin_template(
            'Creative Split',
            v_template_type,
            'creative',
            v_template_config,
            FALSE
        );
    END LOOP;

    -- 5. Service Professional
    v_template_config := '{
        "layout": {
            "header_style": "standard",
            "items_table_style": "service",
            "footer_style": "detailed",
            "logo_position": "top_left",
            "page_size": "letter",
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20},
            "section_spacing": 16
        },
        "sections": {
            "header": {"visible": true},
            "business_info": {"visible": true, "fields": ["name", "address", "phone", "email", "license"]},
            "client_info": {"visible": true},
            "line_items": {"visible": true, "columns": ["description", "hours", "rate", "amount"]},
            "totals": {"visible": true, "show_subtotal": true, "show_tax": true},
            "payment_terms": {"visible": true},
            "notes": {"visible": true},
            "footer": {"visible": true}
        },
        "colors": {
            "primary": "#DC2626",
            "secondary": "#991B1B",
            "accent": "#FEE2E2",
            "text_primary": "#000000",
            "text_secondary": "#6B7280",
            "border": "#E2E8F0",
            "background": "#FFFFFF"
        },
        "typography": {
            "title": {"font": "System", "size": 28, "weight": "bold"},
            "header": {"font": "System", "size": 14, "weight": "semibold"},
            "body": {"font": "System", "size": 11, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "business_rules": {
            "payment_terms": "net_30",
            "tax_calculation": "exclusive",
            "currency": "usd",
            "date_format": "mm_dd_yyyy"
        },
        "custom_fields": [
            {"key": "job_reference", "label": "Job Ref #", "type": "text", "required": false},
            {"key": "license_number", "label": "License #", "type": "text", "required": false}
        ]
    }'::JSONB;
    
    FOREACH v_template_type IN ARRAY v_template_types LOOP
        PERFORM seed_builtin_template(
            'Service Professional',
            v_template_type,
            'service_focused',
            v_template_config,
            FALSE
        );
    END LOOP;

    -- 6. Consulting Elite
    v_template_config := '{
        "layout": {
            "header_style": "centered",
            "items_table_style": "consulting",
            "footer_style": "detailed",
            "logo_position": "top_center",
            "page_size": "letter",
            "margins": {"top": 25, "left": 25, "right": 25, "bottom": 25},
            "section_spacing": 18
        },
        "sections": {
            "header": {"visible": true, "style": "centered"},
            "business_info": {"visible": true},
            "client_info": {"visible": true},
            "line_items": {"visible": true, "columns": ["description", "hours", "rate", "amount"]},
            "totals": {"visible": true, "show_subtotal": true, "show_tax": true},
            "payment_terms": {"visible": true},
            "notes": {"visible": true},
            "footer": {"visible": true}
        },
        "colors": {
            "primary": "#1E40AF",
            "secondary": "#3B82F6",
            "accent": "#DBEAFE",
            "text_primary": "#000000",
            "text_secondary": "#6B7280",
            "border": "#E2E8F0",
            "background": "#FFFFFF"
        },
        "typography": {
            "title": {"font": "System", "size": 30, "weight": "bold"},
            "header": {"font": "System", "size": 14, "weight": "bold"},
            "body": {"font": "System", "size": 11, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "business_rules": {
            "payment_terms": "net_15",
            "tax_calculation": "exclusive",
            "currency": "usd",
            "date_format": "mm_dd_yyyy"
        },
        "custom_fields": [
            {"key": "hourly_rate", "label": "Rate/Hour", "type": "currency", "required": false}
        ]
    }'::JSONB;
    
    FOREACH v_template_type IN ARRAY v_template_types LOOP
        PERFORM seed_builtin_template(
            'Consulting Elite',
            v_template_type,
            'consulting',
            v_template_config,
            FALSE
        );
    END LOOP;

    -- 7. Modern Centered
    v_template_config := '{
        "layout": {
            "header_style": "centered",
            "items_table_style": "simple",
            "footer_style": "none",
            "logo_position": "top_center",
            "page_size": "letter",
            "margins": {"top": 30, "left": 30, "right": 30, "bottom": 30},
            "section_spacing": 24
        },
        "sections": {
            "header": {"visible": true, "style": "centered"},
            "business_info": {"visible": false},
            "client_info": {"visible": true, "fields": ["name"]},
            "line_items": {"visible": true, "columns": ["description", "amount"]},
            "totals": {"visible": true, "show_subtotal": false, "show_tax": false},
            "payment_terms": {"visible": false},
            "notes": {"visible": false},
            "footer": {"visible": false}
        },
        "colors": {
            "primary": "#6366F1",
            "secondary": "#8B5CF6",
            "accent": "#F0F9FF",
            "text_primary": "#000000",
            "text_secondary": "#6B7280",
            "border": "#E2E8F0",
            "background": "#FFFFFF"
        },
        "typography": {
            "title": {"font": "System", "size": 36, "weight": "light"},
            "header": {"font": "System", "size": 12, "weight": "light"},
            "body": {"font": "System", "size": 10, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "business_rules": {
            "payment_terms": "immediate",
            "tax_calculation": "inclusive",
            "currency": "usd",
            "date_format": "mm_dd_yyyy"
        }
    }'::JSONB;
    
    FOREACH v_template_type IN ARRAY v_template_types LOOP
        PERFORM seed_builtin_template(
            'Modern Centered',
            v_template_type,
            'modern',
            v_template_config,
            FALSE
        );
    END LOOP;

    -- 8. Classic Monospace
    v_template_config := '{
        "layout": {
            "header_style": "minimal",
            "items_table_style": "simple",
            "footer_style": "simple",
            "logo_position": "top_left",
            "page_size": "letter",
            "margins": {"top": 40, "left": 40, "right": 40, "bottom": 40},
            "section_spacing": 20
        },
        "sections": {
            "header": {"visible": true},
            "business_info": {"visible": true},
            "client_info": {"visible": true},
            "line_items": {"visible": true},
            "totals": {"visible": true, "show_subtotal": true, "show_tax": true},
            "payment_terms": {"visible": true},
            "notes": {"visible": true},
            "footer": {"visible": true}
        },
        "colors": {
            "primary": "#2D3748",
            "secondary": "#4A5568",
            "accent": "#F7FAFC",
            "text_primary": "#2D3748",
            "text_secondary": "#4A5568",
            "border": "#E5E7EB",
            "background": "#FFFFFF"
        },
        "typography": {
            "title": {"font": "Menlo", "size": 20, "weight": "bold"},
            "header": {"font": "Menlo", "size": 11, "weight": "regular"},
            "body": {"font": "Menlo", "size": 9, "weight": "regular"},
            "caption": {"font": "Menlo", "size": 8, "weight": "regular"}
        },
        "business_rules": {
            "payment_terms": "net_30",
            "tax_calculation": "exclusive",
            "currency": "usd",
            "date_format": "yyyy_mm_dd"
        }
    }'::JSONB;
    
    FOREACH v_template_type IN ARRAY v_template_types LOOP
        PERFORM seed_builtin_template(
            'Classic Monospace',
            v_template_type,
            'classic',
            v_template_config,
            FALSE
        );
    END LOOP;

    -- 9. Bold Creative
    v_template_config := '{
        "layout": {
            "header_style": "split",
            "items_table_style": "creative",
            "footer_style": "detailed",
            "logo_position": "header_right",
            "page_size": "letter",
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20},
            "section_spacing": 32
        },
        "sections": {
            "header": {"visible": true, "style": "split"},
            "business_info": {"visible": true, "fields": ["name", "email", "website"]},
            "client_info": {"visible": true},
            "line_items": {"visible": true},
            "totals": {"visible": true, "show_subtotal": true, "show_tax": true},
            "payment_terms": {"visible": false},
            "notes": {"visible": true},
            "footer": {"visible": true}
        },
        "colors": {
            "primary": "#EC4899",
            "secondary": "#F59E0B",
            "accent": "#FDF2F8",
            "text_primary": "#000000",
            "text_secondary": "#6B7280",
            "border": "#E2E8F0",
            "background": "#FFFFFF"
        },
        "typography": {
            "title": {"font": "System", "size": 32, "weight": "bold"},
            "header": {"font": "System", "size": 13, "weight": "medium"},
            "body": {"font": "System", "size": 10, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "business_rules": {
            "payment_terms": "immediate",
            "tax_calculation": "exclusive",
            "currency": "usd",
            "date_format": "mm_dd_yyyy"
        }
    }'::JSONB;
    
    FOREACH v_template_type IN ARRAY v_template_types LOOP
        PERFORM seed_builtin_template(
            'Bold Creative',
            v_template_type,
            'creative',
            v_template_config,
            FALSE
        );
    END LOOP;

    -- 10. Executive Bold
    v_template_config := '{
        "layout": {
            "header_style": "bold",
            "items_table_style": "detailed",
            "footer_style": "detailed",
            "logo_position": "top_left",
            "page_size": "letter",
            "margins": {"top": 25, "left": 25, "right": 25, "bottom": 25},
            "section_spacing": 18
        },
        "sections": {
            "header": {"visible": true, "style": "bold"},
            "business_info": {"visible": true},
            "client_info": {"visible": true},
            "line_items": {"visible": true},
            "totals": {"visible": true, "show_subtotal": true, "show_tax": true},
            "payment_terms": {"visible": true},
            "notes": {"visible": true},
            "footer": {"visible": true}
        },
        "colors": {
            "primary": "#0F766E",
            "secondary": "#134E4A",
            "accent": "#F0FDFA",
            "text_primary": "#000000",
            "text_secondary": "#6B7280",
            "border": "#E2E8F0",
            "background": "#FFFFFF"
        },
        "typography": {
            "title": {"font": "System", "size": 24, "weight": "semibold"},
            "header": {"font": "System", "size": 13, "weight": "semibold"},
            "body": {"font": "System", "size": 11, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "business_rules": {
            "payment_terms": "net_30",
            "tax_calculation": "exclusive",
            "currency": "usd",
            "date_format": "mm_dd_yyyy"
        }
    }'::JSONB;
    
    FOREACH v_template_type IN ARRAY v_template_types LOOP
        PERFORM seed_builtin_template(
            'Executive Bold',
            v_template_type,
            'professional',
            v_template_config,
            FALSE
        );
    END LOOP;

    -- 11. Clean Simple
    v_template_config := '{
        "layout": {
            "header_style": "minimal",
            "items_table_style": "simple",
            "footer_style": "none",
            "logo_position": "top_right",
            "page_size": "letter",
            "margins": {"top": 16, "left": 16, "right": 16, "bottom": 16},
            "section_spacing": 16
        },
        "sections": {
            "header": {"visible": true},
            "business_info": {"visible": false},
            "client_info": {"visible": true, "fields": ["name", "email"]},
            "line_items": {"visible": true, "columns": ["description", "amount"]},
            "totals": {"visible": true, "show_subtotal": false, "show_tax": false},
            "payment_terms": {"visible": false},
            "notes": {"visible": false},
            "footer": {"visible": false}
        },
        "colors": {
            "primary": "#374151",
            "secondary": "#6B7280",
            "accent": "#F9FAFB",
            "text_primary": "#374151",
            "text_secondary": "#6B7280",
            "border": "#E5E7EB",
            "background": "#FFFFFF"
        },
        "typography": {
            "title": {"font": "System", "size": 22, "weight": "medium"},
            "header": {"font": "System", "size": 11, "weight": "regular"},
            "body": {"font": "System", "size": 10, "weight": "regular"},
            "caption": {"font": "System", "size": 9, "weight": "regular"}
        },
        "business_rules": {
            "payment_terms": "immediate",
            "tax_calculation": "inclusive",
            "currency": "usd",
            "date_format": "mm_dd_yyyy"
        }
    }'::JSONB;
    
    FOREACH v_template_type IN ARRAY v_template_types LOOP
        PERFORM seed_builtin_template(
            'Clean Simple',
            v_template_type,
            'minimal',
            v_template_config,
            FALSE
        );
    END LOOP;

END $$;

-- =====================================
-- CREATE SAMPLE WEBSITE TEMPLATE
-- =====================================
INSERT INTO public.templates (
    business_id,
    template_type,
    category,
    name,
    description,
    is_active,
    is_default,
    is_system,
    config,
    created_by
) VALUES (
    NULL,
    'website',
    'professional',
    'Professional Service Website',
    'Professional website template for service businesses',
    TRUE,
    TRUE,
    TRUE,
    '{
        "pages": [
            {
                "path": "/",
                "name": "Home",
                "title": "Welcome to Our Services",
                "sections": [
                    {
                        "type": "hero",
                        "props": {
                            "headline": "Professional Services You Can Trust",
                            "subheadline": "Quality work, competitive prices, exceptional service"
                        }
                    },
                    {
                        "type": "services",
                        "props": {
                            "featured": true,
                            "columns": 3
                        }
                    },
                    {
                        "type": "testimonials",
                        "props": {
                            "count": 3
                        }
                    },
                    {
                        "type": "cta",
                        "props": {
                            "action": "Get Free Quote",
                            "style": "primary"
                        }
                    }
                ]
            },
            {
                "path": "/services",
                "name": "Services",
                "title": "Our Services",
                "sections": [
                    {
                        "type": "service-grid",
                        "props": {
                            "layout": "cards"
                        }
                    }
                ]
            },
            {
                "path": "/contact",
                "name": "Contact",
                "title": "Contact Us",
                "sections": [
                    {
                        "type": "contact-form",
                        "props": {
                            "fields": ["name", "email", "phone", "message"]
                        }
                    },
                    {
                        "type": "contact-info",
                        "props": {
                            "show_map": true
                        }
                    }
                ]
            }
        ],
        "navigation": {
            "style": "standard",
            "items": [
                {"label": "Home", "path": "/"},
                {"label": "Services", "path": "/services"},
                {"label": "About", "path": "/about"},
                {"label": "Contact", "path": "/contact"}
            ]
        },
        "seo": {
            "defaults": {
                "title_suffix": " | Professional Services",
                "meta_description": "Professional service provider offering quality work at competitive prices"
            },
            "schemas": ["LocalBusiness", "Service"]
        },
        "theme": {
            "extends_branding": true,
            "overrides": {}
        }
    }'::JSONB,
    'system'
);

-- =====================================
-- CLEANUP
-- =====================================
DROP FUNCTION IF EXISTS seed_builtin_template;

-- =====================================
-- VERIFICATION
-- =====================================
DO $$
DECLARE
    v_template_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_template_count
    FROM public.templates
    WHERE is_system = TRUE;
    
    -- Should have 22 document templates (11 × 2) + 1 website template = 23
    IF v_template_count < 23 THEN
        RAISE WARNING 'Expected at least 23 system templates, but found %', v_template_count;
    ELSE
        RAISE NOTICE 'Successfully created % system templates', v_template_count;
    END IF;
    
    -- Verify defaults are set
    IF NOT EXISTS (
        SELECT 1 FROM public.templates 
        WHERE name = 'Classic Professional' 
        AND is_default = TRUE 
        AND is_system = TRUE
    ) THEN
        RAISE WARNING 'Classic Professional should be set as default template';
    END IF;
END $$;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW template_usage_analytics;
