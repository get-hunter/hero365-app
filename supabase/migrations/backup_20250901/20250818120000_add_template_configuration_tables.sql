-- =====================================
-- Template Management System Enhancement
-- =====================================
-- This migration adds comprehensive template configuration tables
-- to support detailed template customization for invoices, estimates,
-- and other document types.

-- =====================================
-- TEMPLATE LAYOUTS TABLE
-- =====================================
-- Stores layout configuration for templates
CREATE TABLE public.template_layouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.document_templates(id) ON DELETE CASCADE,
    
    -- Layout styles
    header_style VARCHAR(50) DEFAULT 'standard' CHECK (header_style IN (
        'standard', 'bold', 'minimal', 'centered', 'split'
    )),
    items_table_style VARCHAR(50) DEFAULT 'standard' CHECK (items_table_style IN (
        'standard', 'detailed', 'simple', 'creative', 'service', 'consulting'
    )),
    footer_style VARCHAR(50) DEFAULT 'detailed' CHECK (footer_style IN (
        'simple', 'detailed', 'none'
    )),
    
    -- Logo configuration
    logo_position VARCHAR(50) DEFAULT 'top_left' CHECK (logo_position IN (
        'top_left', 'top_center', 'top_right', 'header_left', 'header_right', 'none'
    )),
    logo_size VARCHAR(20) DEFAULT 'medium' CHECK (logo_size IN (
        'small', 'medium', 'large', 'custom'
    )),
    
    -- Page configuration
    page_size VARCHAR(20) DEFAULT 'letter' CHECK (page_size IN (
        'a4', 'letter', 'legal', 'a3', 'tabloid'
    )),
    page_orientation VARCHAR(20) DEFAULT 'portrait' CHECK (page_orientation IN (
        'portrait', 'landscape'
    )),
    
    -- Spacing and margins
    section_spacing DECIMAL(5,2) DEFAULT 1.5 CHECK (section_spacing >= 0),
    margins JSONB DEFAULT '{"top": 20, "left": 20, "right": 20, "bottom": 20}'::JSONB,
    column_widths JSONB DEFAULT '{"description": 0.4, "quantity": 0.15, "rate": 0.15, "amount": 0.15, "tax": 0.15}'::JSONB,
    
    -- Additional layout settings
    show_page_numbers BOOLEAN DEFAULT TRUE,
    show_watermark BOOLEAN DEFAULT FALSE,
    watermark_text VARCHAR(100),
    watermark_opacity DECIMAL(3,2) DEFAULT 0.1 CHECK (watermark_opacity >= 0 AND watermark_opacity <= 1),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one layout per template
    CONSTRAINT template_layouts_template_unique UNIQUE (template_id)
);

-- =====================================
-- TEMPLATE COLOR SCHEMES TABLE
-- =====================================
-- Stores color configuration for templates
CREATE TABLE public.template_color_schemes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.document_templates(id) ON DELETE CASCADE,
    
    -- Scheme identification
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Primary colors
    primary_color VARCHAR(7) NOT NULL DEFAULT '#2563EB' CHECK (primary_color ~ '^#[0-9A-Fa-f]{6}$'),
    secondary_color VARCHAR(7) NOT NULL DEFAULT '#64748B' CHECK (secondary_color ~ '^#[0-9A-Fa-f]{6}$'),
    accent_color VARCHAR(7) NOT NULL DEFAULT '#F1F5F9' CHECK (accent_color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Background colors
    background_color VARCHAR(7) DEFAULT '#FFFFFF' CHECK (background_color ~ '^#[0-9A-Fa-f]{6}$'),
    surface_color VARCHAR(7) DEFAULT '#F8FAFC' CHECK (surface_color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Text colors
    text_primary_color VARCHAR(7) DEFAULT '#000000' CHECK (text_primary_color ~ '^#[0-9A-Fa-f]{6}$'),
    text_secondary_color VARCHAR(7) DEFAULT '#6B7280' CHECK (text_secondary_color ~ '^#[0-9A-Fa-f]{6}$'),
    text_muted_color VARCHAR(7) DEFAULT '#9CA3AF' CHECK (text_muted_color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Border and divider colors
    border_color VARCHAR(7) DEFAULT '#E5E7EB' CHECK (border_color ~ '^#[0-9A-Fa-f]{6}$'),
    divider_color VARCHAR(7) DEFAULT '#D1D5DB' CHECK (divider_color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Status colors (for invoices/estimates)
    success_color VARCHAR(7) DEFAULT '#10B981' CHECK (success_color ~ '^#[0-9A-Fa-f]{6}$'),
    warning_color VARCHAR(7) DEFAULT '#F59E0B' CHECK (warning_color ~ '^#[0-9A-Fa-f]{6}$'),
    error_color VARCHAR(7) DEFAULT '#EF4444' CHECK (error_color ~ '^#[0-9A-Fa-f]{6}$'),
    info_color VARCHAR(7) DEFAULT '#3B82F6' CHECK (info_color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Additional color settings
    link_color VARCHAR(7) DEFAULT '#2563EB' CHECK (link_color ~ '^#[0-9A-Fa-f]{6}$'),
    highlight_color VARCHAR(7) DEFAULT '#FEF3C7' CHECK (highlight_color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one color scheme per template
    CONSTRAINT template_color_schemes_template_unique UNIQUE (template_id)
);

-- =====================================
-- TEMPLATE TYPOGRAPHY TABLE
-- =====================================
-- Stores typography settings for templates
CREATE TABLE public.template_typography (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.document_templates(id) ON DELETE CASCADE,
    
    -- Font configurations (stored as JSONB for flexibility)
    title_font JSONB NOT NULL DEFAULT '{"name": "System", "size": 28, "weight": "bold", "style": "normal", "letterSpacing": 0}'::JSONB,
    header_font JSONB NOT NULL DEFAULT '{"name": "System", "size": 14, "weight": "semibold", "style": "normal", "letterSpacing": 0}'::JSONB,
    subheader_font JSONB NOT NULL DEFAULT '{"name": "System", "size": 12, "weight": "medium", "style": "normal", "letterSpacing": 0}'::JSONB,
    body_font JSONB NOT NULL DEFAULT '{"name": "System", "size": 11, "weight": "regular", "style": "normal", "letterSpacing": 0}'::JSONB,
    caption_font JSONB NOT NULL DEFAULT '{"name": "System", "size": 9, "weight": "regular", "style": "normal", "letterSpacing": 0}'::JSONB,
    label_font JSONB NOT NULL DEFAULT '{"name": "System", "size": 10, "weight": "medium", "style": "normal", "letterSpacing": 0.5}'::JSONB,
    
    -- Line heights
    line_height_tight DECIMAL(3,2) DEFAULT 1.25,
    line_height_normal DECIMAL(3,2) DEFAULT 1.5,
    line_height_relaxed DECIMAL(3,2) DEFAULT 1.75,
    
    -- Text transformations
    uppercase_headers BOOLEAN DEFAULT FALSE,
    uppercase_labels BOOLEAN DEFAULT FALSE,
    
    -- Font families (fallback options)
    font_family_primary VARCHAR(200) DEFAULT 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
    font_family_secondary VARCHAR(200) DEFAULT 'Georgia, Cambria, "Times New Roman", serif',
    font_family_monospace VARCHAR(200) DEFAULT 'Consolas, Monaco, "Courier New", monospace',
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one typography config per template
    CONSTRAINT template_typography_template_unique UNIQUE (template_id)
);

-- =====================================
-- TEMPLATE BUSINESS RULES TABLE
-- =====================================
-- Stores business logic and formatting rules for templates
CREATE TABLE public.template_business_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.document_templates(id) ON DELETE CASCADE,
    
    -- Display settings for invoices/estimates
    show_invoice_number BOOLEAN DEFAULT TRUE,
    show_estimate_number BOOLEAN DEFAULT TRUE,
    show_issue_date BOOLEAN DEFAULT TRUE,
    show_due_date BOOLEAN DEFAULT TRUE,
    show_valid_until BOOLEAN DEFAULT TRUE,
    show_project_name BOOLEAN DEFAULT FALSE,
    show_job_reference BOOLEAN DEFAULT FALSE,
    
    -- Financial display settings
    show_subtotal BOOLEAN DEFAULT TRUE,
    show_tax_breakdown BOOLEAN DEFAULT TRUE,
    show_discount_breakdown BOOLEAN DEFAULT TRUE,
    show_payment_terms BOOLEAN DEFAULT TRUE,
    show_late_fees BOOLEAN DEFAULT FALSE,
    show_deposit_required BOOLEAN DEFAULT FALSE,
    show_balance_due BOOLEAN DEFAULT TRUE,
    show_amount_paid BOOLEAN DEFAULT TRUE,
    
    -- Content display settings
    show_notes BOOLEAN DEFAULT TRUE,
    show_terms_conditions BOOLEAN DEFAULT TRUE,
    show_payment_instructions BOOLEAN DEFAULT TRUE,
    show_thank_you_message BOOLEAN DEFAULT TRUE,
    show_signature_line BOOLEAN DEFAULT FALSE,
    
    -- Default values
    default_payment_terms VARCHAR(50) DEFAULT 'net_30' CHECK (default_payment_terms IN (
        'immediate', 'net_15', 'net_30', 'net_45', 'net_60', 'net_90', 'custom'
    )),
    default_late_fee_percentage DECIMAL(5,2) DEFAULT 0 CHECK (default_late_fee_percentage >= 0 AND default_late_fee_percentage <= 100),
    default_deposit_percentage DECIMAL(5,2) DEFAULT 0 CHECK (default_deposit_percentage >= 0 AND default_deposit_percentage <= 100),
    
    -- Formatting rules
    currency_format VARCHAR(10) DEFAULT 'usd' CHECK (currency_format IN (
        'usd', 'eur', 'gbp', 'cad', 'aud', 'jpy', 'cny', 'inr', 'mxn', 'brl'
    )),
    currency_position VARCHAR(10) DEFAULT 'before' CHECK (currency_position IN ('before', 'after')),
    thousand_separator VARCHAR(1) DEFAULT ',' CHECK (thousand_separator IN (',', '.', ' ', '')),
    decimal_separator VARCHAR(1) DEFAULT '.' CHECK (decimal_separator IN ('.', ',')),
    decimal_places INTEGER DEFAULT 2 CHECK (decimal_places >= 0 AND decimal_places <= 4),
    
    -- Date formatting
    date_format VARCHAR(20) DEFAULT 'mm_dd_yyyy' CHECK (date_format IN (
        'mm_dd_yyyy', 'dd_mm_yyyy', 'yyyy_mm_dd', 'month_day_year', 'day_month_year'
    )),
    time_format VARCHAR(10) DEFAULT '12h' CHECK (time_format IN ('12h', '24h')),
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    
    -- Tax and calculation rules
    tax_calculation VARCHAR(20) DEFAULT 'exclusive' CHECK (tax_calculation IN ('inclusive', 'exclusive')),
    tax_label VARCHAR(50) DEFAULT 'Tax',
    discount_calculation VARCHAR(20) DEFAULT 'before_tax' CHECK (discount_calculation IN ('before_tax', 'after_tax')),
    
    -- Rounding rules
    rounding_mode VARCHAR(20) DEFAULT 'half_up' CHECK (rounding_mode IN (
        'half_up', 'half_down', 'half_even', 'up', 'down'
    )),
    
    -- Number formatting
    negative_format VARCHAR(20) DEFAULT 'minus' CHECK (negative_format IN (
        'minus', 'parentheses', 'red'
    )),
    zero_format VARCHAR(20) DEFAULT 'show' CHECK (zero_format IN (
        'show', 'hide', 'dash'
    )),
    
    -- Custom text labels
    invoice_label VARCHAR(50) DEFAULT 'Invoice',
    estimate_label VARCHAR(50) DEFAULT 'Estimate',
    quote_label VARCHAR(50) DEFAULT 'Quote',
    subtotal_label VARCHAR(50) DEFAULT 'Subtotal',
    total_label VARCHAR(50) DEFAULT 'Total',
    balance_due_label VARCHAR(50) DEFAULT 'Balance Due',
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one business rules config per template
    CONSTRAINT template_business_rules_template_unique UNIQUE (template_id)
);

-- =====================================
-- TEMPLATE CUSTOM FIELDS TABLE
-- =====================================
-- Stores custom fields that can be added to templates
CREATE TABLE public.template_custom_fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.document_templates(id) ON DELETE CASCADE,
    
    -- Field identification
    field_name VARCHAR(100) NOT NULL,
    field_label VARCHAR(100) NOT NULL,
    field_key VARCHAR(100) NOT NULL, -- Unique key for API/data access
    
    -- Field configuration
    field_type VARCHAR(20) NOT NULL CHECK (field_type IN (
        'text', 'number', 'currency', 'percentage', 'date', 'datetime',
        'email', 'phone', 'url', 'address', 'multiline', 'dropdown',
        'checkbox', 'radio', 'file', 'signature', 'image'
    )),
    
    -- Field properties
    default_value TEXT,
    placeholder TEXT,
    help_text TEXT,
    
    -- Validation
    is_required BOOLEAN DEFAULT FALSE,
    is_visible BOOLEAN DEFAULT TRUE,
    is_editable BOOLEAN DEFAULT TRUE,
    is_printable BOOLEAN DEFAULT TRUE,
    
    -- Validation rules (stored as JSONB for flexibility)
    validation_rules JSONB DEFAULT '{}'::JSONB,
    -- Example: {"min": 0, "max": 100, "pattern": "^[A-Z]+$", "options": ["Option1", "Option2"]}
    
    -- Display configuration
    display_order INTEGER NOT NULL DEFAULT 0,
    display_section VARCHAR(50) DEFAULT 'additional' CHECK (display_section IN (
        'header', 'customer', 'items', 'totals', 'footer', 'additional', 'custom'
    )),
    display_width VARCHAR(20) DEFAULT 'full' CHECK (display_width IN (
        'full', 'half', 'third', 'quarter', 'auto'
    )),
    
    -- Conditional display
    conditional_display JSONB DEFAULT NULL,
    -- Example: {"field": "invoice_status", "operator": "equals", "value": "sent"}
    
    -- Data source (for dropdowns, etc.)
    data_source VARCHAR(50) CHECK (data_source IN (
        'static', 'contacts', 'products', 'projects', 'custom_list', 'api'
    )),
    data_source_config JSONB DEFAULT NULL,
    
    -- Permissions
    visible_to_customer BOOLEAN DEFAULT TRUE,
    editable_by_customer BOOLEAN DEFAULT FALSE,
    
    -- Global field flag
    is_global BOOLEAN DEFAULT FALSE, -- Available across all templates
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255),
    
    -- Constraints
    CONSTRAINT template_custom_fields_unique_key UNIQUE (template_id, field_key)
);

-- =====================================
-- TEMPLATE SECTIONS CONFIGURATION TABLE
-- =====================================
-- Enhanced section configuration for templates
CREATE TABLE public.template_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.document_templates(id) ON DELETE CASCADE,
    
    -- Section identification
    section_key VARCHAR(50) NOT NULL,
    section_name VARCHAR(100) NOT NULL,
    
    -- Section properties
    is_visible BOOLEAN DEFAULT TRUE,
    is_collapsible BOOLEAN DEFAULT FALSE,
    is_collapsed_default BOOLEAN DEFAULT FALSE,
    
    -- Display configuration
    display_order INTEGER NOT NULL DEFAULT 0,
    custom_title VARCHAR(200),
    custom_subtitle VARCHAR(200),
    
    -- Section styling
    background_color VARCHAR(7) CHECK (background_color ~ '^#[0-9A-Fa-f]{6}$'),
    border_style VARCHAR(20) CHECK (border_style IN (
        'none', 'solid', 'dashed', 'dotted', 'double'
    )),
    padding JSONB DEFAULT '{"top": 10, "left": 10, "right": 10, "bottom": 10}'::JSONB,
    
    -- Section-specific configuration
    configuration JSONB DEFAULT '{}'::JSONB,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT template_sections_unique_key UNIQUE (template_id, section_key)
);

-- =====================================
-- INDEXES FOR PERFORMANCE
-- =====================================
CREATE INDEX idx_template_layouts_template_id ON public.template_layouts(template_id);
CREATE INDEX idx_template_color_schemes_template_id ON public.template_color_schemes(template_id);
CREATE INDEX idx_template_typography_template_id ON public.template_typography(template_id);
CREATE INDEX idx_template_business_rules_template_id ON public.template_business_rules(template_id);
CREATE INDEX idx_template_custom_fields_template_id ON public.template_custom_fields(template_id);
CREATE INDEX idx_template_custom_fields_is_global ON public.template_custom_fields(is_global) WHERE is_global = TRUE;
CREATE INDEX idx_template_sections_template_id ON public.template_sections(template_id);
CREATE INDEX idx_template_sections_display_order ON public.template_sections(template_id, display_order);

-- =====================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================
CREATE OR REPLACE FUNCTION update_template_configs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all new tables
CREATE TRIGGER update_template_layouts_updated_at
    BEFORE UPDATE ON public.template_layouts
    FOR EACH ROW
    EXECUTE FUNCTION update_template_configs_updated_at();

CREATE TRIGGER update_template_color_schemes_updated_at
    BEFORE UPDATE ON public.template_color_schemes
    FOR EACH ROW
    EXECUTE FUNCTION update_template_configs_updated_at();

CREATE TRIGGER update_template_typography_updated_at
    BEFORE UPDATE ON public.template_typography
    FOR EACH ROW
    EXECUTE FUNCTION update_template_configs_updated_at();

CREATE TRIGGER update_template_business_rules_updated_at
    BEFORE UPDATE ON public.template_business_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_template_configs_updated_at();

CREATE TRIGGER update_template_custom_fields_updated_at
    BEFORE UPDATE ON public.template_custom_fields
    FOR EACH ROW
    EXECUTE FUNCTION update_template_configs_updated_at();

CREATE TRIGGER update_template_sections_updated_at
    BEFORE UPDATE ON public.template_sections
    FOR EACH ROW
    EXECUTE FUNCTION update_template_configs_updated_at();

-- =====================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================
COMMENT ON TABLE public.template_layouts IS 'Layout configuration for document templates including header styles, margins, and page settings';
COMMENT ON TABLE public.template_color_schemes IS 'Color scheme configuration for document templates';
COMMENT ON TABLE public.template_typography IS 'Typography and font settings for document templates';
COMMENT ON TABLE public.template_business_rules IS 'Business logic and formatting rules for document templates';
COMMENT ON TABLE public.template_custom_fields IS 'Custom fields that can be added to document templates';
COMMENT ON TABLE public.template_sections IS 'Section-specific configuration for document templates';

COMMENT ON COLUMN public.template_layouts.template_id IS 'Reference to the parent document template';
COMMENT ON COLUMN public.template_color_schemes.template_id IS 'Reference to the parent document template';
COMMENT ON COLUMN public.template_typography.template_id IS 'Reference to the parent document template';
COMMENT ON COLUMN public.template_business_rules.template_id IS 'Reference to the parent document template';
COMMENT ON COLUMN public.template_custom_fields.template_id IS 'Reference to the parent document template';
COMMENT ON COLUMN public.template_custom_fields.field_key IS 'Unique key for programmatic access to the field';
COMMENT ON COLUMN public.template_custom_fields.is_global IS 'If true, field is available across all templates in the business';
COMMENT ON COLUMN public.template_sections.section_key IS 'Unique key identifying the section type (header, items, footer, etc.)';

-- =====================================
-- SAMPLE DATA FUNCTION (Optional - for testing)
-- =====================================
-- This function can be used to create sample template configurations
CREATE OR REPLACE FUNCTION create_sample_template_config(p_template_id UUID)
RETURNS VOID AS $$
BEGIN
    -- Create layout
    INSERT INTO public.template_layouts (template_id, header_style, items_table_style, footer_style)
    VALUES (p_template_id, 'standard', 'standard', 'detailed')
    ON CONFLICT (template_id) DO NOTHING;
    
    -- Create color scheme
    INSERT INTO public.template_color_schemes (template_id, name, primary_color, secondary_color)
    VALUES (p_template_id, 'Default Professional', '#2563EB', '#64748B')
    ON CONFLICT (template_id) DO NOTHING;
    
    -- Create typography
    INSERT INTO public.template_typography (template_id)
    VALUES (p_template_id)
    ON CONFLICT (template_id) DO NOTHING;
    
    -- Create business rules
    INSERT INTO public.template_business_rules (template_id)
    VALUES (p_template_id)
    ON CONFLICT (template_id) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION create_sample_template_config IS 'Helper function to create default template configurations for testing';
