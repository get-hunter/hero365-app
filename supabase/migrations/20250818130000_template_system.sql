-- =====================================
-- Unified Template System Migration
-- =====================================
-- This migration replaces the complex multi-table template system
-- with a single unified template table using JSONB for flexible configuration.
-- This approach combines the flexibility of NoSQL with PostgreSQL's reliability.

-- =====================================
-- DROP EXISTING TEMPLATE TABLES
-- =====================================

-- Drop the recently created template configuration tables
DROP TABLE IF EXISTS public.template_custom_fields CASCADE;
DROP TABLE IF EXISTS public.template_sections CASCADE;
DROP TABLE IF EXISTS public.template_business_rules CASCADE;
DROP TABLE IF EXISTS public.template_typography CASCADE;
DROP TABLE IF EXISTS public.template_color_schemes CASCADE;
DROP TABLE IF EXISTS public.template_layouts CASCADE;

-- Drop the old document_templates table
DROP TABLE IF EXISTS public.document_templates CASCADE;

-- Drop other template tables if they exist
DROP TABLE IF EXISTS public.estimate_templates CASCADE;
DROP TABLE IF EXISTS public.project_templates CASCADE;
DROP TABLE IF EXISTS public.job_templates CASCADE;
DROP TABLE IF EXISTS public.activity_templates CASCADE;
DROP TABLE IF EXISTS public.working_hours_templates CASCADE;

-- =====================================
-- CREATE TEMPLATES TABLE
-- =====================================
CREATE TABLE public.templates (
    -- Core identification
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES public.businesses(id) ON DELETE CASCADE,
    branding_id UUID REFERENCES public.business_branding(id) ON DELETE SET NULL,
    
    -- Template classification
    template_type VARCHAR(50) NOT NULL CHECK (template_type IN (
        'invoice', 'estimate', 'contract', 'proposal', 'quote',
        'work_order', 'receipt', 'website', 'email', 'project',
        'job', 'activity', 'working_hours', 'custom'
    )),
    category VARCHAR(50) CHECK (category IN (
        'professional', 'creative', 'minimal', 'corporate', 'modern', 
        'classic', 'industrial', 'service_focused', 'consulting', 'custom'
    )),
    
    -- Basic metadata
    name VARCHAR(200) NOT NULL,
    description TEXT,
    version INTEGER DEFAULT 1,
    
    -- Status flags
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    is_system BOOLEAN DEFAULT FALSE,
    
    -- Complete configuration in JSONB
    config JSONB NOT NULL DEFAULT '{}'::JSONB,
    /*
    Config structure varies by template_type:
    
    For document templates (invoice, estimate, contract):
    {
        "layout": {
            "header_style": "standard|bold|minimal|centered|split",
            "items_table_style": "standard|detailed|simple|creative|service|consulting",
            "footer_style": "simple|detailed|none",
            "logo_position": "top_left|top_center|top_right|header_left|header_right",
            "page_size": "a4|letter|legal",
            "margins": {"top": 20, "left": 20, "right": 20, "bottom": 20},
            "section_spacing": 16,
            "column_widths": {"description": 0.4, "quantity": 0.15, "rate": 0.15, "amount": 0.15}
        },
        "sections": {
            "header": {"visible": true, "style": "bold", "content": null},
            "business_info": {"visible": true, "fields": ["name", "address", "phone", "email"]},
            "client_info": {"visible": true, "fields": ["name", "address", "phone", "email"]},
            "line_items": {"visible": true, "columns": ["description", "quantity", "rate", "amount"]},
            "totals": {"visible": true, "show_subtotal": true, "show_tax": true, "show_discount": true},
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
            "late_fees": {"enabled": true, "percentage": 1.5},
            "tax_calculation": "exclusive",
            "currency": "usd",
            "date_format": "mm_dd_yyyy",
            "number_format": {"decimal_places": 2, "thousand_separator": ","}
        },
        "custom_fields": [
            {"key": "po_number", "label": "PO Number", "type": "text", "required": false},
            {"key": "project_name", "label": "Project", "type": "text", "required": false}
        ]
    }
    
    For website templates:
    {
        "pages": [
            {
                "path": "/",
                "name": "Home",
                "title": "Welcome",
                "sections": [
                    {
                        "type": "hero",
                        "props": {"headline": "...", "subheadline": "..."},
                        "content": {"text": "...", "images": [...]}
                    }
                ]
            }
        ],
        "navigation": {
            "style": "standard|minimal|centered",
            "items": [{"label": "Home", "path": "/"}]
        },
        "seo": {
            "defaults": {"title_suffix": " | Company Name"},
            "schemas": ["LocalBusiness", "Service"]
        },
        "theme": {
            "extends_branding": true,
            "overrides": {"primary_color": "#..."}
        },
        "components": {
            "header": {...},
            "footer": {...}
        }
    }
    */
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}'::JSONB, -- Additional flexible metadata
    
    -- Audit fields
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by VARCHAR(255),
    
    -- Constraints
    CONSTRAINT templates_business_or_system CHECK (
        (business_id IS NOT NULL AND is_system = FALSE) OR 
        (business_id IS NULL AND is_system = TRUE)
    ),
    CONSTRAINT templates_unique_default UNIQUE (business_id, template_type, is_default)
);

-- =====================================
-- CREATE TEMPLATE VERSIONS TABLE
-- =====================================
CREATE TABLE public.template_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.templates(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    config JSONB NOT NULL,
    change_notes TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(template_id, version)
);

-- =====================================
-- CREATE TEMPLATE CACHE TABLE
-- =====================================
-- For storing pre-rendered or processed templates
CREATE TABLE public.template_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.templates(id) ON DELETE CASCADE,
    cache_key VARCHAR(255) NOT NULL, -- e.g., "rendered_html", "pdf_layout", etc.
    cache_data JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(template_id, cache_key)
);

-- =====================================
-- INDEXES FOR PERFORMANCE
-- =====================================

-- Primary access patterns
CREATE INDEX idx_templates_business_id ON public.templates(business_id);
CREATE INDEX idx_templates_type ON public.templates(template_type);
CREATE INDEX idx_templates_category ON public.templates(category);
CREATE INDEX idx_templates_active ON public.templates(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_templates_default ON public.templates(is_default) WHERE is_default = TRUE;
CREATE INDEX idx_templates_system ON public.templates(is_system) WHERE is_system = TRUE;

-- JSONB GIN indexes for config queries
CREATE INDEX idx_templates_config ON public.templates USING gin(config);
CREATE INDEX idx_templates_config_layout ON public.templates USING gin((config->'layout'));
CREATE INDEX idx_templates_config_colors ON public.templates USING gin((config->'colors'));
CREATE INDEX idx_templates_config_sections ON public.templates USING gin((config->'sections'));

-- For website templates specifically
CREATE INDEX idx_templates_website_pages ON public.templates USING gin((config->'pages')) 
    WHERE template_type = 'website';

-- Tags and metadata
CREATE INDEX idx_templates_tags ON public.templates USING gin(tags);
CREATE INDEX idx_templates_metadata ON public.templates USING gin(metadata);

-- Composite indexes for common queries
CREATE INDEX idx_templates_business_type_default 
    ON public.templates(business_id, template_type, is_default);
CREATE INDEX idx_templates_type_category_active 
    ON public.templates(template_type, category, is_active);

-- Template versions
CREATE INDEX idx_template_versions_template_id ON public.template_versions(template_id);
CREATE INDEX idx_template_versions_created_at ON public.template_versions(created_at DESC);

-- Template cache
CREATE INDEX idx_template_cache_template_id ON public.template_cache(template_id);
CREATE INDEX idx_template_cache_expires_at ON public.template_cache(expires_at) WHERE expires_at IS NOT NULL;

-- =====================================
-- UPDATE TRIGGER FOR updated_at
-- =====================================
CREATE OR REPLACE FUNCTION update_templates_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_templates_updated_at
    BEFORE UPDATE ON public.templates
    FOR EACH ROW
    EXECUTE FUNCTION update_templates_updated_at();

-- =====================================
-- HELPER FUNCTIONS
-- =====================================

-- Function to set a template as default (unsets others)
CREATE OR REPLACE FUNCTION set_default_template(
    p_template_id UUID,
    p_business_id UUID,
    p_template_type VARCHAR
)
RETURNS BOOLEAN AS $$
BEGIN
    -- Unset current default
    UPDATE public.templates
    SET is_default = FALSE
    WHERE business_id = p_business_id 
    AND template_type = p_template_type 
    AND is_default = TRUE
    AND id != p_template_id;
    
    -- Set new default
    UPDATE public.templates
    SET is_default = TRUE
    WHERE id = p_template_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to increment usage count
CREATE OR REPLACE FUNCTION increment_template_usage(p_template_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE public.templates
    SET 
        usage_count = usage_count + 1,
        last_used_at = NOW()
    WHERE id = p_template_id;
END;
$$ LANGUAGE plpgsql;

-- Function to create a template version snapshot
CREATE OR REPLACE FUNCTION create_template_version(
    p_template_id UUID,
    p_change_notes TEXT,
    p_created_by VARCHAR
)
RETURNS INTEGER AS $$
DECLARE
    v_new_version INTEGER;
    v_config JSONB;
BEGIN
    -- Get current config
    SELECT config INTO v_config
    FROM public.templates
    WHERE id = p_template_id;
    
    -- Get next version number
    SELECT COALESCE(MAX(version), 0) + 1 INTO v_new_version
    FROM public.template_versions
    WHERE template_id = p_template_id;
    
    -- Create version record
    INSERT INTO public.template_versions (template_id, version, config, change_notes, created_by)
    VALUES (p_template_id, v_new_version, v_config, p_change_notes, p_created_by);
    
    -- Update template version
    UPDATE public.templates
    SET version = v_new_version
    WHERE id = p_template_id;
    
    RETURN v_new_version;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- MATERIALIZED VIEW FOR ANALYTICS
-- =====================================
CREATE MATERIALIZED VIEW template_usage_analytics AS
SELECT 
    t.id,
    t.name,
    t.template_type,
    t.category,
    t.is_system,
    t.usage_count,
    t.last_used_at,
    b.name as business_name,
    COUNT(DISTINCT iv.id) as invoice_uses,
    COUNT(DISTINCT es.id) as estimate_uses,
    AVG(EXTRACT(EPOCH FROM (NOW() - t.last_used_at))/86400)::INTEGER as days_since_last_use
FROM public.templates t
LEFT JOIN public.businesses b ON t.business_id = b.id
LEFT JOIN public.invoices iv ON iv.template_id = t.id
LEFT JOIN public.estimates es ON es.template_id = t.id
GROUP BY t.id, t.name, t.template_type, t.category, t.is_system, t.usage_count, t.last_used_at, b.name;

CREATE INDEX idx_template_usage_analytics_type ON template_usage_analytics(template_type);
CREATE INDEX idx_template_usage_analytics_usage ON template_usage_analytics(usage_count DESC);

-- =====================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================
COMMENT ON TABLE public.templates IS 'Unified template system for all document types using flexible JSONB configuration';
COMMENT ON COLUMN public.templates.config IS 'Complete template configuration as JSONB - structure varies by template_type';
COMMENT ON COLUMN public.templates.template_type IS 'Type of template: invoice, estimate, website, etc.';
COMMENT ON COLUMN public.templates.is_default IS 'Only one template per type per business can be default';
COMMENT ON COLUMN public.templates.is_system IS 'System templates are available to all businesses';

COMMENT ON TABLE public.template_versions IS 'Version history for templates, enabling rollback and change tracking';
COMMENT ON TABLE public.template_cache IS 'Cache for pre-processed template data to improve performance';

COMMENT ON FUNCTION set_default_template IS 'Sets a template as default for its type and business, unsetting others';
COMMENT ON FUNCTION increment_template_usage IS 'Increments usage count and updates last used timestamp';
COMMENT ON FUNCTION create_template_version IS 'Creates a snapshot of current template configuration for version history';

-- =====================================
-- UPDATE FOREIGN KEY REFERENCES
-- =====================================
-- Update invoices table to reference templates
ALTER TABLE public.invoices 
    DROP CONSTRAINT IF EXISTS invoices_template_id_fkey,
    ADD CONSTRAINT invoices_template_id_fkey 
    FOREIGN KEY (template_id) REFERENCES public.templates(id) ON DELETE SET NULL;

-- Update estimates table to reference templates
ALTER TABLE public.estimates 
    DROP CONSTRAINT IF EXISTS estimates_template_id_fkey,
    ADD CONSTRAINT estimates_template_id_fkey 
    FOREIGN KEY (template_id) REFERENCES public.templates(id) ON DELETE SET NULL;
