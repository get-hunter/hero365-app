-- =====================================
-- Built-in System Templates Migration
-- =====================================
-- This migration inserts the 11 built-in templates that are currently
-- hardcoded in the mobile app, making them available system-wide.
-- Templates include: Professional (2), Minimal (2), Creative (2),
-- Corporate (1), Service (1), Consulting (1), Modern (1), Classic (1)

-- Helper function to create a complete template with all configurations
CREATE OR REPLACE FUNCTION create_builtin_template(
    p_name VARCHAR,
    p_description TEXT,
    p_category VARCHAR,
    p_primary_color VARCHAR,
    p_secondary_color VARCHAR,
    p_accent_color VARCHAR,
    p_header_style VARCHAR,
    p_items_style VARCHAR,
    p_footer_style VARCHAR,
    p_logo_position VARCHAR,
    p_is_default BOOLEAN DEFAULT FALSE,
    p_title_font_size INTEGER DEFAULT 28,
    p_title_font_weight VARCHAR DEFAULT 'bold',
    p_header_font_size INTEGER DEFAULT 14,
    p_header_font_weight VARCHAR DEFAULT 'semibold',
    p_body_font_size INTEGER DEFAULT 11,
    p_body_font_weight VARCHAR DEFAULT 'regular',
    p_font_family VARCHAR DEFAULT 'System',
    p_section_spacing DECIMAL DEFAULT 16,
    p_margins INTEGER DEFAULT 20
)
RETURNS UUID AS $$
DECLARE
    v_template_id UUID;
    v_document_type VARCHAR;
BEGIN
    -- Create templates for both invoice and estimate document types
    FOR v_document_type IN SELECT unnest(ARRAY['invoice', 'estimate'])
    LOOP
        -- Create the main template
        INSERT INTO public.document_templates (
            business_id,
            name,
            description,
            document_type,
            template_type,
            category,
            is_active,
            is_default,
            is_system_template,
            created_by,
            created_date,
            last_modified
        ) VALUES (
            NULL, -- System template
            p_name,
            p_description,
            v_document_type,
            CASE 
                WHEN p_category = 'consulting' THEN 'professional'
                WHEN p_category = 'service' THEN 'service_focused'
                WHEN p_category = 'service_focused' THEN 'service_focused'
                ELSE p_category
            END, -- Map category to valid template_type
            p_category,
            TRUE,
            CASE 
                WHEN p_is_default AND p_name = 'Classic Professional' THEN TRUE
                ELSE FALSE
            END,
            TRUE, -- System template
            'system',
            NOW(),
            NOW()
        ) RETURNING id INTO v_template_id;
        
        -- Create layout configuration
        INSERT INTO public.template_layouts (
            template_id,
            header_style,
            items_table_style,
            footer_style,
            logo_position,
            page_size,
            section_spacing,
            margins
        ) VALUES (
            v_template_id,
            p_header_style,
            p_items_style,
            p_footer_style,
            p_logo_position,
            'letter',
            p_section_spacing,
            jsonb_build_object('top', p_margins, 'left', p_margins, 'right', p_margins, 'bottom', p_margins)
        );
        
        -- Create color scheme
        INSERT INTO public.template_color_schemes (
            template_id,
            name,
            primary_color,
            secondary_color,
            accent_color,
            background_color,
            text_primary_color,
            text_secondary_color,
            border_color
        ) VALUES (
            v_template_id,
            p_name || ' Color Scheme',
            p_primary_color,
            p_secondary_color,
            p_accent_color,
            '#FFFFFF',
            CASE 
                WHEN p_name IN ('Modern Minimal', 'Classic Monospace') THEN '#1F2937'
                WHEN p_name = 'Clean Simple' THEN '#374151'
                ELSE '#000000'
            END,
            CASE 
                WHEN p_name = 'Classic Monospace' THEN '#4A5568'
                ELSE '#6B7280'
            END,
            CASE 
                WHEN p_name IN ('Modern Minimal', 'Classic Monospace', 'Clean Simple') THEN '#E5E7EB'
                ELSE '#E2E8F0'
            END
        );
        
        -- Create typography configuration
        INSERT INTO public.template_typography (
            template_id,
            title_font,
            header_font,
            body_font,
            caption_font,
            font_family_primary
        ) VALUES (
            v_template_id,
            jsonb_build_object('name', p_font_family, 'size', p_title_font_size, 'weight', p_title_font_weight),
            jsonb_build_object('name', p_font_family, 'size', p_header_font_size, 'weight', p_header_font_weight),
            jsonb_build_object('name', p_font_family, 'size', p_body_font_size, 'weight', p_body_font_weight),
            jsonb_build_object('name', p_font_family, 'size', 9, 'weight', 'regular'),
            CASE 
                WHEN p_font_family = 'Menlo' THEN 'Menlo, Monaco, Consolas, "Courier New", monospace'
                ELSE 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
            END
        );
        
        -- Create business rules (will be customized per template later)
        INSERT INTO public.template_business_rules (
            template_id,
            show_invoice_number,
            show_due_date,
            show_tax_breakdown,
            show_payment_terms,
            default_payment_terms,
            currency_format,
            date_format
        ) VALUES (
            v_template_id,
            TRUE,
            v_document_type = 'invoice', -- Only show due date for invoices
            TRUE,
            TRUE,
            'net_30',
            'usd',
            'mm_dd_yyyy'
        );
    END LOOP;
    
    RETURN v_template_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- INSERT THE 11 BUILT-IN TEMPLATES
-- =====================================

DO $$
BEGIN

-- 1. Classic Professional (DEFAULT for both invoice and estimate)
PERFORM create_builtin_template(
    'Classic Professional',
    'A timeless, professional template with clean lines and traditional layout. Features company logo placement, complete business information, detailed client information, line items with descriptions, tax calculations, and payment terms.',
    'professional',
    '#2563EB', -- Professional blue
    '#64748B', -- Slate gray
    '#F1F5F9', -- Light blue-gray
    'standard',
    'detailed',
    'detailed',
    'top_left',
    TRUE, -- Set as default
    28, 'bold',     -- Title font
    14, 'semibold', -- Header font
    11, 'regular'   -- Body font
);

-- 2. Modern Minimal
PERFORM create_builtin_template(
    'Modern Minimal',
    'Clean and contemporary design with minimal visual elements. Features centered logo, minimal business details, clean typography, essential invoice elements only, and subtle gray tones.',
    'minimal',
    '#1F2937', -- Dark gray
    '#6B7280', -- Medium gray
    '#F9FAFB', -- Very light gray
    'minimal',
    'simple',
    'simple',
    'top_center',
    FALSE,
    24, 'regular',  -- Title font (light style requested, using regular)
    12, 'medium',   -- Header font
    10, 'regular'   -- Body font
);

-- 3. Corporate Bold  
PERFORM create_builtin_template(
    'Corporate Bold',
    'Professional corporate template with formal structure. Features bold typography, right-aligned logo, complete contact information, discount calculations, project context, and corporate green theme.',
    'corporate',
    '#059669', -- Emerald green
    '#047857', -- Dark emerald
    '#D1FAE5', -- Light emerald
    'bold',
    'detailed',
    'detailed',
    'top_right',
    FALSE,
    32, 'bold',     -- Title font (heavy style requested, using bold)
    15, 'bold',     -- Header font
    11, 'medium'    -- Body font
);

-- 4. Creative Split
PERFORM create_builtin_template(
    'Creative Split',
    'Eye-catching template with vibrant colors for creative professionals. Features split header layout, creative table styling, project-based billing, custom headlines, and modern purple theme.',
    'creative',
    '#7C3AED', -- Purple
    '#A855F7', -- Light purple
    '#F3E8FF', -- Very light purple
    'split',
    'creative',
    'detailed',
    'header_left',
    FALSE,
    26, 'semibold', -- Title font
    13, 'semibold', -- Header font
    10, 'regular'   -- Body font
);

-- 5. Service Professional
PERFORM create_builtin_template(
    'Service Professional',
    'Optimized for service-based businesses with detailed line items. Features service-oriented layout, license number display, job reference tracking, professional red theme, and trade-focused details.',
    'service_focused',
    '#DC2626', -- Red
    '#991B1B', -- Dark red
    '#FEE2E2', -- Light red
    'standard',
    'service',
    'detailed',
    'top_left',
    FALSE,
    28, 'bold',     -- Title font
    14, 'semibold', -- Header font
    11, 'regular'   -- Body font
);

-- 6. Consulting Elite
PERFORM create_builtin_template(
    'Consulting Elite',  
    'Premium template for consulting and professional services. Features centered header layout, hourly rate display, project context, executive blue theme, and premium presentation.',
    'consulting', -- Will be mapped to 'professional' template_type in the function
    '#1E40AF', -- Blue
    '#3B82F6', -- Light blue
    '#DBEAFE', -- Very light blue
    'centered',
    'consulting',
    'detailed',
    'top_center',
    FALSE,
    30, 'bold',     -- Title font
    14, 'bold',     -- Header font
    11, 'regular'   -- Body font
);

-- 7. Modern Centered
PERFORM create_builtin_template(
    'Modern Centered',
    'Centered minimalist layout with ultra-light typography. Features simplified information display, modern indigo accent, clean and contemporary design.',
    'modern',
    '#6366F1', -- Indigo
    '#8B5CF6', -- Purple
    '#F0F9FF', -- Very light blue
    'centered',
    'simple',
    'none',
    'top_center',
    FALSE,
    36, 'regular',  -- Title font (light style requested, using regular)
    12, 'regular',  -- Header font (light style requested, using regular)
    10, 'regular',  -- Body font
    'System',
    24,             -- Section spacing
    30              -- Margins
);

-- 8. Classic Monospace
PERFORM create_builtin_template(
    'Classic Monospace',
    'Classic business layout with monospace typography. Features traditional invoice format, charcoal and gray theme, and timeless professional look.',
    'classic',
    '#2D3748', -- Charcoal
    '#4A5568', -- Dark gray
    '#F7FAFC', -- Off-white
    'minimal',
    'simple',
    'simple',
    'top_left',
    FALSE,
    20, 'bold',     -- Title font
    11, 'regular',  -- Header font
    9, 'regular',   -- Body font
    'Menlo',        -- Monospace font
    20,             -- Section spacing
    40              -- Margins
);

-- 9. Bold Creative
PERFORM create_builtin_template(
    'Bold Creative',
    'Eye-catching template with vibrant colors. Features bold creative typography, split header design, vibrant pink and amber colors, eye-catching layout, and modern creative style.',
    'creative',
    '#EC4899', -- Pink
    '#F59E0B', -- Amber (using as secondary)
    '#FDF2F8', -- Very light pink
    'split',
    'creative',
    'detailed',
    'header_right',
    FALSE,
    32, 'bold',     -- Title font (heavy style requested, using bold)
    13, 'medium',   -- Header font
    10, 'regular',  -- Body font
    'System',
    32,             -- Section spacing
    20              -- Margins
);

-- 10. Executive Bold
PERFORM create_builtin_template(
    'Executive Bold',
    'Bold professional layout for executive presentation. Features comprehensive information, professional teal theme, detailed formatting, and executive presentation style.',
    'professional',
    '#0F766E', -- Teal
    '#134E4A', -- Dark teal
    '#F0FDFA', -- Very light teal
    'bold',
    'detailed',
    'detailed',
    'top_left',
    FALSE,
    24, 'semibold', -- Title font
    13, 'semibold', -- Header font
    11, 'regular',  -- Body font
    'System',
    18,             -- Section spacing
    25              -- Margins
);

-- 11. Clean Simple
PERFORM create_builtin_template(
    'Clean Simple',
    'Minimal information display with clean gray monochrome. Features essential details only, compact layout, and streamlined design.',
    'minimal',
    '#374151', -- Gray-700
    '#6B7280', -- Gray-500
    '#F9FAFB', -- Gray-50
    'minimal',
    'simple',
    'none',
    'top_right',
    FALSE,
    22, 'medium',   -- Title font
    11, 'regular',  -- Header font
    10, 'regular',  -- Body font
    'System',
    16,             -- Section spacing
    16              -- Margins
);

END $$;

-- =====================================
-- UPDATE TEMPLATE SECTIONS BASED ON SPECIFICATIONS
-- =====================================
DO $$
DECLARE
    template_record RECORD;
    v_template_name TEXT;
    v_show_sections JSONB;
BEGIN
    -- Define section visibility for each template
    FOR template_record IN 
        SELECT id, name, document_type 
        FROM public.document_templates 
        WHERE is_system_template = TRUE
    LOOP
        -- Set section visibility based on template specifications
        v_show_sections := CASE template_record.name
            -- Classic Professional: All standard sections
            WHEN 'Classic Professional' THEN jsonb_build_object(
                'show_header', true,
                'show_business_info', true,
                'show_client_info', true,
                'show_line_items', true,
                'show_totals', true,
                'show_subtotal', true,
                'show_tax_breakdown', true,
                'show_payment_terms', true,
                'show_notes', true,
                'show_footer', true,
                'show_invoice_number', true,
                'show_dates', true,
                'show_po_number', true,
                'show_project_name', true,
                'show_discount', false,
                'show_job_reference', false,
                'show_license_number', false,
                'show_hourly_rates', false,
                'show_custom_headline', false
            )
            -- Modern Minimal: Minimal sections
            WHEN 'Modern Minimal' THEN jsonb_build_object(
                'show_header', true,
                'show_business_info', false,
                'show_client_info', true,
                'show_line_items', true,
                'show_totals', true,
                'show_subtotal', true,
                'show_tax_breakdown', true,
                'show_payment_terms', false,
                'show_notes', false,
                'show_footer', true,
                'show_invoice_number', true,
                'show_dates', true,
                'show_po_number', false,
                'show_project_name', true,
                'show_custom_headline', true
            )
            -- Corporate Bold: All sections plus extras
            WHEN 'Corporate Bold' THEN jsonb_build_object(
                'show_header', true,
                'show_business_info', true,
                'show_client_info', true,
                'show_line_items', true,
                'show_totals', true,
                'show_subtotal', true,
                'show_tax_breakdown', true,
                'show_payment_terms', true,
                'show_notes', true,
                'show_footer', true,
                'show_invoice_number', true,
                'show_dates', true,
                'show_po_number', true,
                'show_project_name', true,
                'show_discount', true,
                'show_custom_headline', true,
                'show_website', true
            )
            -- Creative Split
            WHEN 'Creative Split' THEN jsonb_build_object(
                'show_header', true,
                'show_business_info', true,
                'show_client_info', true,
                'show_line_items', true,
                'show_totals', true,
                'show_subtotal', true,
                'show_tax_breakdown', true,
                'show_payment_terms', true,
                'show_notes', true,
                'show_footer', true,
                'show_invoice_number', true,
                'show_dates', true,
                'show_po_number', false,
                'show_project_name', true,
                'show_custom_headline', true
            )
            -- Service Professional
            WHEN 'Service Professional' THEN jsonb_build_object(
                'show_header', true,
                'show_business_info', true,
                'show_client_info', true,
                'show_line_items', true,
                'show_totals', true,
                'show_subtotal', true,
                'show_tax_breakdown', true,
                'show_payment_terms', true,
                'show_notes', true,
                'show_footer', true,
                'show_invoice_number', true,
                'show_dates', true,
                'show_job_reference', true,
                'show_license_number', true
            )
            -- Consulting Elite
            WHEN 'Consulting Elite' THEN jsonb_build_object(
                'show_header', true,
                'show_business_info', true,
                'show_client_info', true,
                'show_line_items', true,
                'show_totals', true,
                'show_subtotal', true,
                'show_tax_breakdown', true,
                'show_payment_terms', true,
                'show_notes', true,
                'show_footer', true,
                'show_invoice_number', true,
                'show_dates', true,
                'show_project_name', true,
                'show_custom_headline', true,
                'show_hourly_rates', true
            )
            -- Modern Centered: Ultra minimal
            WHEN 'Modern Centered' THEN jsonb_build_object(
                'show_header', true,
                'show_business_info', false,
                'show_client_info', true,
                'show_line_items', true,
                'show_totals', true,
                'show_subtotal', false,
                'show_tax_breakdown', false,
                'show_payment_terms', false,
                'show_notes', false,
                'show_footer', false,
                'show_invoice_number', true,
                'show_dates', true,
                'show_project_name', true,
                'show_custom_headline', true
            )
            -- Classic Monospace
            WHEN 'Classic Monospace' THEN jsonb_build_object(
                'show_header', true,
                'show_business_info', true,
                'show_client_info', true,
                'show_line_items', true,
                'show_totals', true,
                'show_subtotal', true,
                'show_tax_breakdown', true,
                'show_payment_terms', true,
                'show_notes', true,
                'show_footer', true,
                'show_invoice_number', true,
                'show_dates', true,
                'show_logo', false
            )
            -- Bold Creative
            WHEN 'Bold Creative' THEN jsonb_build_object(
                'show_header', true,
                'show_business_info', true,
                'show_client_info', true,
                'show_line_items', true,
                'show_totals', true,
                'show_subtotal', true,
                'show_tax_breakdown', true,
                'show_payment_terms', false,
                'show_notes', true,
                'show_footer', true,
                'show_invoice_number', true,
                'show_dates', true,
                'show_project_name', true,
                'show_custom_headline', true,
                'show_website', true,
                'show_address', false,
                'show_phone', false
            )
            -- Executive Bold
            WHEN 'Executive Bold' THEN jsonb_build_object(
                'show_header', true,
                'show_business_info', true,
                'show_client_info', true,
                'show_line_items', true,
                'show_totals', true,
                'show_subtotal', true,
                'show_tax_breakdown', true,
                'show_payment_terms', true,
                'show_notes', true,
                'show_footer', true,
                'show_invoice_number', true,
                'show_dates', true
            )
            -- Clean Simple: Ultra minimal
            WHEN 'Clean Simple' THEN jsonb_build_object(
                'show_header', true,
                'show_business_info', false,
                'show_client_info', true,
                'show_line_items', true,
                'show_totals', true,
                'show_subtotal', false,
                'show_tax_breakdown', false,
                'show_payment_terms', false,
                'show_notes', false,
                'show_footer', false,
                'show_invoice_number', true,
                'show_dates', true,
                'show_project_name', true,
                'show_logo', false,
                'show_business_name', true,
                'show_business_email', true
            )
            ELSE jsonb_build_object() -- Default empty
        END;
        
        -- Update the sections field
        UPDATE public.document_templates
        SET sections = v_show_sections
        WHERE id = template_record.id;
        
        -- Create template sections entries
        INSERT INTO public.template_sections (
            template_id,
            section_key,
            section_name,
            is_visible,
            display_order
        )
        SELECT 
            template_record.id,
            key,
            REPLACE(INITCAP(REPLACE(key, '_', ' ')), ' ', ' '),
            (value::boolean),
            row_number() OVER (ORDER BY 
                CASE key
                    WHEN 'show_header' THEN 1
                    WHEN 'show_business_info' THEN 2
                    WHEN 'show_client_info' THEN 3
                    WHEN 'show_invoice_number' THEN 4
                    WHEN 'show_dates' THEN 5
                    WHEN 'show_line_items' THEN 6
                    WHEN 'show_subtotal' THEN 7
                    WHEN 'show_discount' THEN 8
                    WHEN 'show_tax_breakdown' THEN 9
                    WHEN 'show_totals' THEN 10
                    WHEN 'show_payment_terms' THEN 11
                    WHEN 'show_notes' THEN 12
                    WHEN 'show_footer' THEN 13
                    ELSE 14
                END
            ) * 10
        FROM jsonb_each(v_show_sections)
        WHERE key LIKE 'show_%';
    END LOOP;
END $$;

-- =====================================
-- ADD CUSTOM FIELDS FOR SPECIFIC TEMPLATES
-- =====================================
DO $$
DECLARE
    template_record RECORD;
BEGIN
    -- Add PO Number field to templates that show it
    FOR template_record IN 
        SELECT id 
        FROM public.document_templates 
        WHERE is_system_template = TRUE 
        AND name IN ('Classic Professional', 'Corporate Bold')
    LOOP
        INSERT INTO public.template_custom_fields (
            template_id,
            field_name,
            field_label,
            field_key,
            field_type,
            placeholder,
            display_section,
            display_order
        ) VALUES (
            template_record.id,
            'Purchase Order',
            'PO Number',
            'po_number',
            'text',
            'Enter PO number if applicable',
            'header',
            10
        );
    END LOOP;
    
    -- Add Job Reference field to Service Professional template
    FOR template_record IN 
        SELECT id 
        FROM public.document_templates 
        WHERE is_system_template = TRUE 
        AND name = 'Service Professional'
    LOOP
        INSERT INTO public.template_custom_fields (
            template_id,
            field_name,
            field_label,
            field_key,
            field_type,
            placeholder,
            display_section,
            display_order
        ) VALUES (
            template_record.id,
            'Job Reference',
            'Job Ref #',
            'job_reference',
            'text',
            'Job reference number',
            'header',
            10
        );
        
        INSERT INTO public.template_custom_fields (
            template_id,
            field_name,
            field_label,
            field_key,
            field_type,
            placeholder,
            display_section,
            display_order
        ) VALUES (
            template_record.id,
            'License Number',
            'License #',
            'license_number',
            'text',
            'Professional license number',
            'header',
            20
        );
    END LOOP;
    
    -- Add Hourly Rate field to Consulting Elite template
    FOR template_record IN 
        SELECT id 
        FROM public.document_templates 
        WHERE is_system_template = TRUE 
        AND name = 'Consulting Elite'
    LOOP
        INSERT INTO public.template_custom_fields (
            template_id,
            field_name,
            field_label,
            field_key,
            field_type,
            placeholder,
            display_section,
            display_order
        ) VALUES (
            template_record.id,
            'Hourly Rate',
            'Rate/Hour',
            'hourly_rate',
            'currency',
            'Hourly rate',
            'header',
            10
        );
    END LOOP;
END $$;

-- =====================================
-- CLEANUP
-- =====================================
-- Drop the helper function as it's no longer needed
DROP FUNCTION IF EXISTS create_builtin_template;

-- =====================================
-- VERIFICATION
-- =====================================
-- This query can be used to verify the templates were created correctly
DO $$
DECLARE
    v_template_count INTEGER;
    v_unique_templates INTEGER;
BEGIN
    -- Count total templates (should be 22 = 11 templates × 2 document types)
    SELECT COUNT(*) INTO v_template_count
    FROM public.document_templates
    WHERE is_system_template = TRUE;
    
    -- Count unique template names (should be 11)
    SELECT COUNT(DISTINCT name) INTO v_unique_templates
    FROM public.document_templates
    WHERE is_system_template = TRUE;
    
    IF v_unique_templates != 11 THEN
        RAISE EXCEPTION 'Expected 11 unique built-in templates, but found %', v_unique_templates;
    END IF;
    
    IF v_template_count != 22 THEN
        RAISE EXCEPTION 'Expected 22 total templates (11 × 2 document types), but found %', v_template_count;
    END IF;
    
    -- Verify Classic Professional is set as default
    IF NOT EXISTS (
        SELECT 1 FROM public.document_templates 
        WHERE name = 'Classic Professional' 
        AND is_default = TRUE 
        AND is_system_template = TRUE
    ) THEN
        RAISE EXCEPTION 'Classic Professional should be set as default template';
    END IF;
    
    RAISE NOTICE 'Successfully created % built-in templates with % unique designs', 
                 v_template_count, v_unique_templates;
END $$;
