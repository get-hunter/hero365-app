-- Create business_branding table for centralized brand management
CREATE TABLE IF NOT EXISTS public.business_branding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    
    -- Branding theme
    theme VARCHAR(50) DEFAULT 'professional',
    theme_name VARCHAR(100) DEFAULT 'Default Brand',
    
    -- Core branding components (stored as JSONB for flexibility)
    color_scheme JSONB NOT NULL DEFAULT '{
        "primary_color": "#2563eb",
        "secondary_color": "#64748b",
        "accent_color": "#10b981",
        "text_color": "#1f2937",
        "heading_color": "#111827",
        "muted_text_color": "#6b7280",
        "background_color": "#ffffff",
        "surface_color": "#f9fafb",
        "border_color": "#e5e7eb",
        "success_color": "#10b981",
        "warning_color": "#f59e0b",
        "error_color": "#ef4444",
        "info_color": "#3b82f6"
    }'::JSONB,
    
    typography JSONB NOT NULL DEFAULT '{
        "heading_font": "Inter",
        "body_font": "Inter",
        "mono_font": "Courier New",
        "heading_1_size": "2.5rem",
        "heading_2_size": "2rem",
        "heading_3_size": "1.5rem",
        "body_size": "1rem",
        "small_size": "0.875rem",
        "heading_weight": "700",
        "body_weight": "400",
        "bold_weight": "600",
        "heading_line_height": "1.2",
        "body_line_height": "1.6",
        "heading_letter_spacing": "-0.02em",
        "body_letter_spacing": "0"
    }'::JSONB,
    
    assets JSONB DEFAULT '{}'::JSONB,
    
    -- Trade and component customizations
    trade_customizations JSONB DEFAULT '{}'::JSONB,
    website_settings JSONB DEFAULT '{
        "enable_animations": true,
        "enable_dark_mode": false,
        "corner_radius": "8px",
        "shadow_style": "medium"
    }'::JSONB,
    document_settings JSONB DEFAULT '{
        "page_size": "A4",
        "margin": "20mm",
        "show_watermark": false,
        "watermark_opacity": 0.1
    }'::JSONB,
    email_settings JSONB DEFAULT '{
        "header_style": "centered",
        "footer_style": "minimal",
        "include_social_links": true
    }'::JSONB,
    
    -- Custom CSS
    custom_css TEXT,
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    version VARCHAR(20) DEFAULT '1.0',
    tags TEXT[],
    
    -- Audit fields
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255),
    last_modified_by VARCHAR(255),
    
    -- Constraints
    CONSTRAINT unique_active_branding_per_business UNIQUE (business_id, is_active)
);

-- Create indexes for performance
CREATE INDEX idx_business_branding_business_id ON public.business_branding(business_id);
CREATE INDEX idx_business_branding_theme ON public.business_branding(theme);
CREATE INDEX idx_business_branding_active ON public.business_branding(is_active) WHERE is_active = TRUE;

-- Add trigger to update last_modified
CREATE OR REPLACE FUNCTION update_business_branding_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_business_branding_last_modified_trigger
    BEFORE UPDATE ON public.business_branding
    FOR EACH ROW
    EXECUTE FUNCTION update_business_branding_last_modified();

-- Add comment for documentation
COMMENT ON TABLE public.business_branding IS 'Centralized branding configuration for all business components (websites, estimates, invoices, etc.)';

-- Create default branding for existing businesses
INSERT INTO public.business_branding (business_id, theme_name)
SELECT id, name || ' Brand'
FROM public.businesses
WHERE NOT EXISTS (
    SELECT 1 FROM public.business_branding 
    WHERE business_branding.business_id = businesses.id
);

-- Add foreign key reference from estimate_templates to business_branding (optional)
ALTER TABLE public.estimate_templates 
ADD COLUMN IF NOT EXISTS branding_id UUID REFERENCES public.business_branding(id) ON DELETE SET NULL;

-- Add foreign key reference from business_websites to business_branding
ALTER TABLE public.business_websites 
ADD COLUMN IF NOT EXISTS branding_id UUID REFERENCES public.business_branding(id) ON DELETE SET NULL;

-- Add comment for new columns
COMMENT ON COLUMN public.estimate_templates.branding_id IS 'Reference to centralized branding configuration';
COMMENT ON COLUMN public.business_websites.branding_id IS 'Reference to centralized branding configuration';
