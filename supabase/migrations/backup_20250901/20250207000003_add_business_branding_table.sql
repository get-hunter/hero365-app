-- Create business_branding table for centralized brand management
CREATE TABLE IF NOT EXISTS public.business_branding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    color_scheme JSONB DEFAULT '{}'::jsonb,
    typography JSONB DEFAULT '{}'::jsonb,
    assets JSONB DEFAULT '{}'::jsonb,
    trade_customizations JSONB DEFAULT '[]'::jsonb,
    website_settings JSONB DEFAULT '{}'::jsonb,
    document_settings JSONB DEFAULT '{}'::jsonb,
    email_settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (business_id) -- Each business has one branding configuration
);

COMMENT ON TABLE public.business_branding IS 'Centralized branding configuration for businesses.';
COMMENT ON COLUMN public.business_branding.color_scheme IS 'JSONB for primary, secondary, accent colors etc.';
COMMENT ON COLUMN public.business_branding.typography IS 'JSONB for font families, sizes, line heights etc.';
COMMENT ON COLUMN public.business_branding.assets IS 'JSONB for logo_url, favicon_url, watermark_url, signature_image_url.';
COMMENT ON COLUMN public.business_branding.trade_customizations IS 'JSONB array of trade-specific theme overrides.';
COMMENT ON COLUMN public.business_branding.website_settings IS 'JSONB for website-specific branding settings.';
COMMENT ON COLUMN public.business_branding.document_settings IS 'JSONB for document (estimate, invoice) branding settings.';
COMMENT ON COLUMN public.business_branding.email_settings IS 'JSONB for email branding settings.';

-- Optional: Add RLS policies if needed for this table
ALTER TABLE public.business_branding ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON public.business_branding
FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users" ON public.business_branding
FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Enable update for users based on business_id" ON public.business_branding
FOR UPDATE USING (auth.uid() IN (SELECT user_id FROM public.business_memberships WHERE business_id = public.business_branding.business_id));

CREATE POLICY "Enable delete for users based on business_id" ON public.business_branding
FOR DELETE USING (auth.uid() IN (SELECT user_id FROM public.business_memberships WHERE business_id = public.business_branding.business_id));