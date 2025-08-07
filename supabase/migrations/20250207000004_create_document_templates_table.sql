-- Create unified document templates table
-- This replaces the estimate_templates table with a more flexible system

-- Create document templates table
CREATE TABLE IF NOT EXISTS public.document_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES public.businesses(id) ON DELETE CASCADE,
    branding_id UUID REFERENCES public.business_branding(id) ON DELETE SET NULL,
    
    -- Template identification
    name VARCHAR(200) NOT NULL,
    description TEXT,
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN (
        'estimate', 'invoice', 'contract', 'proposal', 'work_order', 'receipt', 'quote'
    )),
    template_type VARCHAR(50) NOT NULL DEFAULT 'professional' CHECK (template_type IN (
        'professional', 'creative', 'minimal', 'corporate', 'modern', 'classic', 'industrial', 'service_focused'
    )),
    
    -- Template status
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    is_system_template BOOLEAN DEFAULT FALSE,
    
    -- Document configuration
    sections JSONB NOT NULL DEFAULT '{
        "show_header": true,
        "show_footer": true,
        "show_business_info": true,
        "show_client_info": true,
        "show_line_items": true,
        "show_totals": true,
        "show_notes": true,
        "show_signature": true,
        "show_terms_conditions": true,
        "show_payment_terms": true,
        "show_tax_breakdown": true,
        "show_validity_period": true,
        "show_estimate_notes": true,
        "show_payment_instructions": true,
        "show_due_date": true,
        "show_payment_methods": true,
        "section_order": [
            "header", "business_info", "client_info", "document_details",
            "line_items", "totals", "payment_terms", "terms_conditions",
            "notes", "signature", "footer"
        ]
    }'::JSONB,
    
    -- Content customization
    header_text TEXT,
    footer_text TEXT,
    terms_text TEXT,
    payment_instructions TEXT,
    thank_you_message TEXT DEFAULT 'Thank you for your business!',
    
    -- Template-specific overrides (overrides BusinessBranding if needed)
    logo_override_url TEXT,
    color_overrides JSONB DEFAULT '{}'::JSONB,
    font_overrides JSONB DEFAULT '{}'::JSONB,
    
    -- Custom styling and data
    custom_css TEXT,
    template_data JSONB DEFAULT '{}'::JSONB,
    
    -- Usage statistics
    usage_count INTEGER DEFAULT 0 CHECK (usage_count >= 0),
    last_used_date TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    tags TEXT[],
    category VARCHAR(100),
    version VARCHAR(20) DEFAULT '1.0',
    
    -- Audit fields
    created_by VARCHAR(255),
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified_by VARCHAR(255),
    
    -- Constraints
    CONSTRAINT document_templates_business_or_system CHECK (
        (business_id IS NOT NULL AND is_system_template = FALSE) OR 
        (business_id IS NULL AND is_system_template = TRUE AND branding_id IS NULL)
    ),
    CONSTRAINT document_templates_unique_default_per_type UNIQUE (business_id, document_type, is_default)
);

-- Create indexes for performance
CREATE INDEX idx_document_templates_business_id ON public.document_templates(business_id);
CREATE INDEX idx_document_templates_branding_id ON public.document_templates(branding_id);
CREATE INDEX idx_document_templates_document_type ON public.document_templates(document_type);
CREATE INDEX idx_document_templates_is_active ON public.document_templates(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_document_templates_is_default ON public.document_templates(is_default) WHERE is_default = TRUE;
CREATE INDEX idx_document_templates_template_type ON public.document_templates(template_type);
CREATE INDEX idx_document_templates_tags ON public.document_templates USING GIN(tags);
CREATE INDEX idx_document_templates_usage ON public.document_templates(usage_count DESC);

-- Add trigger to update last_modified
CREATE OR REPLACE FUNCTION update_document_templates_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_document_templates_last_modified_trigger
    BEFORE UPDATE ON public.document_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_document_templates_last_modified();

-- Note: Data migration will be handled separately if needed
-- The table is now ready for the unified DocumentTemplate system

-- Update invoices table to reference document_templates instead of estimate_templates
ALTER TABLE public.invoices 
DROP CONSTRAINT IF EXISTS invoices_template_id_fkey;

ALTER TABLE public.invoices 
ADD CONSTRAINT invoices_template_id_fkey 
FOREIGN KEY (template_id) REFERENCES public.document_templates(id) ON DELETE SET NULL;

-- Update estimates table to reference document_templates instead of estimate_templates  
ALTER TABLE public.estimates 
DROP CONSTRAINT IF EXISTS estimates_template_id_fkey;

ALTER TABLE public.estimates 
ADD CONSTRAINT estimates_template_id_fkey 
FOREIGN KEY (template_id) REFERENCES public.document_templates(id) ON DELETE SET NULL;

-- Add comment for documentation
COMMENT ON TABLE public.document_templates IS 'Unified template system for all business documents (estimates, invoices, contracts, etc.) with centralized branding support';
COMMENT ON COLUMN public.document_templates.branding_id IS 'Reference to centralized BusinessBranding configuration';
COMMENT ON COLUMN public.document_templates.document_type IS 'Type of document this template is designed for';
COMMENT ON COLUMN public.document_templates.color_overrides IS 'Document-specific color overrides that override BusinessBranding colors';
COMMENT ON COLUMN public.document_templates.font_overrides IS 'Document-specific font overrides that override BusinessBranding typography';
