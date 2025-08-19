-- =====================================
-- Fix System Template Default Handling
-- =====================================
-- This migration fixes the issue where setting a system template as default
-- incorrectly modifies the system template itself, affecting all businesses.

-- =====================================
-- CREATE BUSINESS TEMPLATE PREFERENCES TABLE
-- =====================================
CREATE TABLE public.business_template_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES public.templates(id) ON DELETE CASCADE,
    template_type VARCHAR(50) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Only one default per business per template type
    UNIQUE(business_id, template_type, is_default) DEFERRABLE INITIALLY DEFERRED
);

-- Create indexes for performance
CREATE INDEX idx_business_template_preferences_business_id ON public.business_template_preferences(business_id);
CREATE INDEX idx_business_template_preferences_template_id ON public.business_template_preferences(template_id);
CREATE INDEX idx_business_template_preferences_default ON public.business_template_preferences(business_id, template_type, is_default) WHERE is_default = TRUE;

-- =====================================
-- CREATE IMPROVED SET DEFAULT FUNCTION
-- =====================================
CREATE OR REPLACE FUNCTION set_default_template_v2(
    p_template_id UUID,
    p_business_id UUID,
    p_template_type VARCHAR
)
RETURNS BOOLEAN AS $$
DECLARE
    v_template_business_id UUID;
    v_is_system BOOLEAN;
BEGIN
    -- Get template info
    SELECT business_id, is_system INTO v_template_business_id, v_is_system
    FROM public.templates
    WHERE id = p_template_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Template not found: %', p_template_id;
    END IF;
    
    -- Clear existing defaults for this business and template type
    DELETE FROM public.business_template_preferences
    WHERE business_id = p_business_id 
    AND template_type = p_template_type 
    AND is_default = TRUE;
    
    -- If it's a business template, also clear the template's is_default flag
    IF v_template_business_id = p_business_id THEN
        UPDATE public.templates
        SET is_default = FALSE
        WHERE business_id = p_business_id 
        AND template_type = p_template_type 
        AND is_default = TRUE
        AND id != p_template_id;
        
        -- Set the business template as default
        UPDATE public.templates
        SET is_default = TRUE
        WHERE id = p_template_id;
    ELSE
        -- It's a system template or another business's template
        -- Create a preference record
        INSERT INTO public.business_template_preferences (
            business_id, template_id, template_type, is_default
        ) VALUES (
            p_business_id, p_template_id, p_template_type, TRUE
        );
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- CREATE IMPROVED GET DEFAULT FUNCTION
-- =====================================
CREATE OR REPLACE FUNCTION get_default_template_v2(
    p_business_id UUID,
    p_template_type VARCHAR
)
RETURNS TABLE (
    template_id UUID,
    business_id UUID,
    template_type VARCHAR,
    category VARCHAR,
    name VARCHAR,
    description TEXT,
    version INTEGER,
    is_active BOOLEAN,
    is_default BOOLEAN,
    is_system BOOLEAN,
    config JSONB,
    usage_count INTEGER,
    last_used_at TIMESTAMP WITH TIME ZONE,
    tags TEXT[],
    metadata JSONB,
    created_by VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    updated_by VARCHAR
) AS $$
BEGIN
    -- First, check for business template preferences
    RETURN QUERY
    SELECT t.*
    FROM public.templates t
    INNER JOIN public.business_template_preferences btp ON t.id = btp.template_id
    WHERE btp.business_id = p_business_id
    AND btp.template_type = p_template_type
    AND btp.is_default = TRUE
    AND t.is_active = TRUE
    LIMIT 1;
    
    -- If found, return
    IF FOUND THEN
        RETURN;
    END IF;
    
    -- Second, check for business-owned default templates
    RETURN QUERY
    SELECT t.*
    FROM public.templates t
    WHERE t.business_id = p_business_id
    AND t.template_type = p_template_type
    AND t.is_default = TRUE
    AND t.is_active = TRUE
    LIMIT 1;
    
    -- If found, return
    IF FOUND THEN
        RETURN;
    END IF;
    
    -- Finally, fall back to system default
    RETURN QUERY
    SELECT t.*
    FROM public.templates t
    WHERE t.is_system = TRUE
    AND t.template_type = p_template_type
    AND t.is_default = TRUE
    AND t.is_active = TRUE
    LIMIT 1;
    
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- MIGRATE EXISTING DATA
-- =====================================
DO $$
DECLARE
    template_record RECORD;
BEGIN
    -- Find any system templates that have been incorrectly marked as default
    -- and reset them to their original state
    FOR template_record IN 
        SELECT id, template_type 
        FROM public.templates 
        WHERE is_system = TRUE 
        AND is_default = TRUE
        AND template_type IN ('invoice', 'estimate')
        AND name != 'Classic Professional'
        AND name != 'Classic Professional (Estimate)'
    LOOP
        -- Reset the system template
        UPDATE public.templates
        SET is_default = FALSE
        WHERE id = template_record.id;
        
        RAISE NOTICE 'Reset system template % to non-default', template_record.id;
    END LOOP;
    
    -- Ensure Classic Professional templates are the only system defaults
    UPDATE public.templates
    SET is_default = TRUE
    WHERE is_system = TRUE
    AND (name = 'Classic Professional' OR name = 'Classic Professional (Estimate)')
    AND is_default = FALSE;
    
END $$;

-- =====================================
-- UPDATE TRIGGER FOR PREFERENCES
-- =====================================
CREATE OR REPLACE FUNCTION update_business_template_preferences_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_business_template_preferences_updated_at
    BEFORE UPDATE ON public.business_template_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_business_template_preferences_updated_at();

-- =====================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================
COMMENT ON TABLE public.business_template_preferences IS 'Stores business preferences for system templates, allowing businesses to set system templates as their defaults without modifying the system templates themselves';
COMMENT ON COLUMN public.business_template_preferences.template_id IS 'References either system templates or business templates';
COMMENT ON COLUMN public.business_template_preferences.is_default IS 'Whether this template is the default for this business and template type';

COMMENT ON FUNCTION set_default_template_v2 IS 'Improved function that properly handles setting system templates as business defaults without modifying system templates';
COMMENT ON FUNCTION get_default_template_v2 IS 'Improved function that checks business preferences first, then business templates, then system defaults';

-- =====================================
-- VERIFICATION
-- =====================================
DO $$
DECLARE
    v_system_defaults INTEGER;
BEGIN
    -- Verify only Classic Professional templates are system defaults
    SELECT COUNT(*) INTO v_system_defaults
    FROM public.templates
    WHERE is_system = TRUE 
    AND is_default = TRUE;
    
    RAISE NOTICE 'System default templates: % (should be 2: Classic Professional invoice and estimate)', v_system_defaults;
    
    -- Verify the preference table exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'business_template_preferences') THEN
        RAISE EXCEPTION 'business_template_preferences table was not created';
    END IF;
    
    RAISE NOTICE 'System template default handling has been fixed';
END $$;
