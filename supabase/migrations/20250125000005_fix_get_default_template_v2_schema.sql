-- =====================================
-- Fix get_default_template_v2 Function Schema Mismatch
-- =====================================
-- The function was created with wrong column names (template_id instead of id)
-- This causes the error: 'structure of query does not match function result type'

-- Drop the existing function
DROP FUNCTION IF EXISTS get_default_template_v2(UUID, VARCHAR);

-- Recreate with correct column names matching the templates table schema
CREATE OR REPLACE FUNCTION get_default_template_v2(
    p_business_id UUID,
    p_template_type VARCHAR
)
RETURNS TABLE (
    id UUID,
    business_id UUID,
    branding_id UUID,
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
    SELECT t.id, t.business_id, t.branding_id, t.template_type, t.category, 
           t.name, t.description, t.version, t.is_active, t.is_default, t.is_system,
           t.config, t.usage_count, t.last_used_at, t.tags, t.metadata,
           t.created_by, t.created_at, t.updated_at, t.updated_by
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
    SELECT t.id, t.business_id, t.branding_id, t.template_type, t.category, 
           t.name, t.description, t.version, t.is_active, t.is_default, t.is_system,
           t.config, t.usage_count, t.last_used_at, t.tags, t.metadata,
           t.created_by, t.created_at, t.updated_at, t.updated_by
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
    SELECT t.id, t.business_id, t.branding_id, t.template_type, t.category, 
           t.name, t.description, t.version, t.is_active, t.is_default, t.is_system,
           t.config, t.usage_count, t.last_used_at, t.tags, t.metadata,
           t.created_by, t.created_at, t.updated_at, t.updated_by
    FROM public.templates t
    WHERE t.is_system = TRUE
    AND t.template_type = p_template_type
    AND t.is_default = TRUE
    AND t.is_active = TRUE
    LIMIT 1;
    
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Also fix the get_or_create_default_template function to use the correct column name
DROP FUNCTION IF EXISTS get_or_create_default_template(UUID, VARCHAR);

CREATE OR REPLACE FUNCTION get_or_create_default_template(
    p_business_id UUID,
    p_template_type VARCHAR
)
RETURNS UUID AS $$
DECLARE
    v_template_id UUID;
BEGIN
    -- Try to get existing default for this business
    SELECT id INTO v_template_id
    FROM get_default_template_v2(p_business_id, p_template_type);
    
    IF v_template_id IS NOT NULL THEN
        RETURN v_template_id;
    END IF;
    
    -- If no default found, get system default
    SELECT id INTO v_template_id
    FROM public.templates
    WHERE is_system = true
    AND template_type = p_template_type
    AND is_default = true
    AND is_active = true
    LIMIT 1;
    
    IF v_template_id IS NULL THEN
        RAISE EXCEPTION 'No default % template found in system', p_template_type;
    END IF;
    
    RETURN v_template_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- VERIFICATION
-- =====================================
DO $$
DECLARE
    v_result UUID;
    v_test_business_id UUID := '660e8400-e29b-41d4-a716-446655440000'; -- Test business ID from logs
BEGIN
    -- Test the function with a known business ID
    SELECT id INTO v_result
    FROM get_default_template_v2(v_test_business_id, 'invoice')
    LIMIT 1;
    
    IF v_result IS NOT NULL THEN
        RAISE NOTICE '✓ get_default_template_v2 function working correctly, returned template: %', v_result;
    ELSE
        RAISE NOTICE '⚠ get_default_template_v2 returned no results for business % and type invoice', v_test_business_id;
    END IF;
    
    -- Test the helper function
    BEGIN
        v_result := get_or_create_default_template(v_test_business_id, 'invoice');
        RAISE NOTICE '✓ get_or_create_default_template function working correctly, returned: %', v_result;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE '⚠ get_or_create_default_template failed: %', SQLERRM;
    END;
END $$;

-- =====================================
-- COMMENTS
-- =====================================
COMMENT ON FUNCTION get_default_template_v2 IS 'Fixed version that matches the templates table schema exactly';
COMMENT ON FUNCTION get_or_create_default_template IS 'Helper function updated to use correct column names from get_default_template_v2';
