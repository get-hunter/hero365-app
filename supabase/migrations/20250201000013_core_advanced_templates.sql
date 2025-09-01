-- =============================================
-- CORE ADVANCED TEMPLATE SYSTEM
-- =============================================
-- Advanced template configuration and customization
-- Depends on: templates table from core_document_tables

-- =============================================
-- TEMPLATE LAYOUTS
-- =============================================

CREATE TABLE template_layouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    
    -- Layout Styles
    header_style VARCHAR(50) DEFAULT 'standard' CHECK (header_style IN (
        'standard', 'bold', 'minimal', 'centered', 'split'
    )),
    items_table_style VARCHAR(50) DEFAULT 'standard' CHECK (items_table_style IN (
        'standard', 'detailed', 'simple', 'creative', 'service', 'consulting'
    )),
    footer_style VARCHAR(50) DEFAULT 'detailed' CHECK (footer_style IN (
        'simple', 'detailed', 'none'
    )),
    
    -- Logo Configuration
    logo_position VARCHAR(50) DEFAULT 'top_left' CHECK (logo_position IN (
        'top_left', 'top_center', 'top_right', 'header_left', 'header_right', 'none'
    )),
    logo_size VARCHAR(20) DEFAULT 'medium' CHECK (logo_size IN (
        'small', 'medium', 'large', 'custom'
    )),
    
    -- Page Configuration
    page_size VARCHAR(20) DEFAULT 'letter' CHECK (page_size IN (
        'a4', 'letter', 'legal', 'a3', 'tabloid'
    )),
    page_orientation VARCHAR(20) DEFAULT 'portrait' CHECK (page_orientation IN (
        'portrait', 'landscape'
    )),
    
    -- Spacing and Margins
    section_spacing DECIMAL(5,2) DEFAULT 1.5 CHECK (section_spacing >= 0),
    margins JSONB DEFAULT '{"top": 20, "left": 20, "right": 20, "bottom": 20}',
    column_widths JSONB DEFAULT '{"description": 0.4, "quantity": 0.15, "rate": 0.15, "amount": 0.15, "tax": 0.15}',
    
    -- Additional Layout Settings
    show_page_numbers BOOLEAN DEFAULT TRUE,
    show_watermark BOOLEAN DEFAULT FALSE,
    watermark_text VARCHAR(100),
    watermark_opacity DECIMAL(3,2) DEFAULT 0.1 CHECK (watermark_opacity >= 0 AND watermark_opacity <= 1),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure one layout per template
    UNIQUE (template_id)
);

-- =============================================
-- TEMPLATE COLOR SCHEMES
-- =============================================

CREATE TABLE template_color_schemes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    
    -- Scheme Identification
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Primary Colors
    primary_color VARCHAR(7) NOT NULL DEFAULT '#2563EB' CHECK (primary_color ~ '^#[0-9A-Fa-f]{6}$'),
    secondary_color VARCHAR(7) NOT NULL DEFAULT '#64748B' CHECK (secondary_color ~ '^#[0-9A-Fa-f]{6}$'),
    accent_color VARCHAR(7) NOT NULL DEFAULT '#F1F5F9' CHECK (accent_color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Background Colors
    background_color VARCHAR(7) DEFAULT '#FFFFFF' CHECK (background_color ~ '^#[0-9A-Fa-f]{6}$'),
    surface_color VARCHAR(7) DEFAULT '#F8FAFC' CHECK (surface_color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Text Colors
    text_primary_color VARCHAR(7) DEFAULT '#000000' CHECK (text_primary_color ~ '^#[0-9A-Fa-f]{6}$'),
    text_secondary_color VARCHAR(7) DEFAULT '#6B7280' CHECK (text_secondary_color ~ '^#[0-9A-Fa-f]{6}$'),
    text_muted_color VARCHAR(7) DEFAULT '#9CA3AF' CHECK (text_muted_color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Border and Divider Colors
    border_color VARCHAR(7) DEFAULT '#E5E7EB' CHECK (border_color ~ '^#[0-9A-Fa-f]{6}$'),
    divider_color VARCHAR(7) DEFAULT '#D1D5DB' CHECK (divider_color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Status Colors
    success_color VARCHAR(7) DEFAULT '#10B981' CHECK (success_color ~ '^#[0-9A-Fa-f]{6}$'),
    warning_color VARCHAR(7) DEFAULT '#F59E0B' CHECK (warning_color ~ '^#[0-9A-Fa-f]{6}$'),
    error_color VARCHAR(7) DEFAULT '#EF4444' CHECK (error_color ~ '^#[0-9A-Fa-f]{6}$'),
    info_color VARCHAR(7) DEFAULT '#3B82F6' CHECK (info_color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Additional Colors
    link_color VARCHAR(7) DEFAULT '#2563EB' CHECK (link_color ~ '^#[0-9A-Fa-f]{6}$'),
    highlight_color VARCHAR(7) DEFAULT '#FEF3C7' CHECK (highlight_color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Status
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- TEMPLATE TYPOGRAPHY
-- =============================================

CREATE TABLE template_typography (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    
    -- Font Families
    heading_font_family VARCHAR(100) DEFAULT 'Inter, system-ui, sans-serif',
    body_font_family VARCHAR(100) DEFAULT 'Inter, system-ui, sans-serif',
    monospace_font_family VARCHAR(100) DEFAULT 'JetBrains Mono, Consolas, monospace',
    
    -- Font Sizes (in points for print, pixels for web)
    h1_font_size DECIMAL(4,1) DEFAULT 24.0,
    h2_font_size DECIMAL(4,1) DEFAULT 20.0,
    h3_font_size DECIMAL(4,1) DEFAULT 18.0,
    h4_font_size DECIMAL(4,1) DEFAULT 16.0,
    body_font_size DECIMAL(4,1) DEFAULT 12.0,
    small_font_size DECIMAL(4,1) DEFAULT 10.0,
    
    -- Font Weights
    heading_font_weight INTEGER DEFAULT 600 CHECK (heading_font_weight >= 100 AND heading_font_weight <= 900),
    body_font_weight INTEGER DEFAULT 400 CHECK (body_font_weight >= 100 AND body_font_weight <= 900),
    bold_font_weight INTEGER DEFAULT 700 CHECK (bold_font_weight >= 100 AND bold_font_weight <= 900),
    
    -- Line Heights
    heading_line_height DECIMAL(3,2) DEFAULT 1.2,
    body_line_height DECIMAL(3,2) DEFAULT 1.5,
    
    -- Letter Spacing
    heading_letter_spacing DECIMAL(4,3) DEFAULT 0.0,
    body_letter_spacing DECIMAL(4,3) DEFAULT 0.0,
    
    -- Text Styles
    heading_text_transform VARCHAR(20) DEFAULT 'none' CHECK (heading_text_transform IN (
        'none', 'uppercase', 'lowercase', 'capitalize'
    )),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure one typography per template
    UNIQUE (template_id)
);

-- =============================================
-- TEMPLATE CUSTOM FIELDS
-- =============================================

CREATE TABLE template_custom_fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    
    -- Field Definition
    field_name VARCHAR(100) NOT NULL,
    field_label VARCHAR(200) NOT NULL,
    field_type VARCHAR(50) NOT NULL CHECK (field_type IN (
        'text', 'textarea', 'number', 'date', 'boolean', 'select', 'multiselect', 'file', 'image'
    )),
    
    -- Field Configuration
    field_options JSONB DEFAULT '{}', -- For select/multiselect options, validation rules, etc.
    default_value TEXT,
    placeholder_text VARCHAR(200),
    
    -- Validation
    is_required BOOLEAN DEFAULT FALSE,
    validation_rules JSONB DEFAULT '{}', -- min/max length, regex patterns, etc.
    
    -- Display Configuration
    display_order INTEGER DEFAULT 0,
    field_group VARCHAR(100), -- Group related fields together
    help_text TEXT,
    
    -- Conditional Logic
    conditional_logic JSONB DEFAULT '{}', -- Show/hide based on other field values
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(template_id, field_name)
);

-- =============================================
-- TEMPLATE SECTIONS
-- =============================================

CREATE TABLE template_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    
    -- Section Definition
    section_name VARCHAR(100) NOT NULL,
    section_label VARCHAR(200) NOT NULL,
    section_type VARCHAR(50) NOT NULL CHECK (section_type IN (
        'header', 'footer', 'items', 'totals', 'terms', 'notes', 'custom'
    )),
    
    -- Content Configuration
    content_template TEXT, -- Template with placeholders
    default_content TEXT,
    
    -- Display Configuration
    display_order INTEGER DEFAULT 0,
    is_required BOOLEAN DEFAULT FALSE,
    is_repeatable BOOLEAN DEFAULT FALSE, -- Can this section be repeated?
    
    -- Styling
    section_styles JSONB DEFAULT '{}', -- CSS-like styling configuration
    
    -- Conditional Display
    display_conditions JSONB DEFAULT '{}', -- When to show this section
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(template_id, section_name)
);

-- =============================================
-- BUSINESS TEMPLATE PREFERENCES
-- =============================================

CREATE TABLE business_template_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    
    -- Preference Configuration
    is_default BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    
    -- Customizations
    custom_color_scheme_id UUID REFERENCES template_color_schemes(id),
    custom_layout_overrides JSONB DEFAULT '{}',
    custom_field_values JSONB DEFAULT '{}',
    
    -- Metadata
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, template_id)
);

-- =============================================
-- INDEXES
-- =============================================

CREATE INDEX idx_template_layouts_template ON template_layouts(template_id);

CREATE INDEX idx_template_color_schemes_template ON template_color_schemes(template_id);
CREATE INDEX idx_template_color_schemes_default ON template_color_schemes(is_default);
CREATE INDEX idx_template_color_schemes_active ON template_color_schemes(is_active);

CREATE INDEX idx_template_typography_template ON template_typography(template_id);

CREATE INDEX idx_template_custom_fields_template ON template_custom_fields(template_id);
CREATE INDEX idx_template_custom_fields_group ON template_custom_fields(field_group);
CREATE INDEX idx_template_custom_fields_order ON template_custom_fields(display_order);
CREATE INDEX idx_template_custom_fields_active ON template_custom_fields(is_active);

CREATE INDEX idx_template_sections_template ON template_sections(template_id);
CREATE INDEX idx_template_sections_type ON template_sections(section_type);
CREATE INDEX idx_template_sections_order ON template_sections(display_order);
CREATE INDEX idx_template_sections_active ON template_sections(is_active);

CREATE INDEX idx_business_template_preferences_business ON business_template_preferences(business_id);
CREATE INDEX idx_business_template_preferences_template ON business_template_preferences(template_id);
CREATE INDEX idx_business_template_preferences_default ON business_template_preferences(is_default);
CREATE INDEX idx_business_template_preferences_favorite ON business_template_preferences(is_favorite);

COMMIT;
