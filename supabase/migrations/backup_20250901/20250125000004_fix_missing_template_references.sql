-- =====================================
-- Fix Missing Template References in Invoices
-- =====================================
-- This migration handles invoices that reference non-existent templates
-- and ensures all invoices have valid template references

-- =====================================
-- CHECK FOR ORPHANED TEMPLATE REFERENCES
-- =====================================
DO $$
DECLARE
    v_orphaned_count INTEGER;
    v_default_invoice_template_id UUID;
    v_default_estimate_template_id UUID;
BEGIN
    -- Count invoices with missing template references
    SELECT COUNT(*) INTO v_orphaned_count
    FROM public.invoices i
    WHERE i.template_id IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM public.templates t WHERE t.id = i.template_id
    );
    
    IF v_orphaned_count > 0 THEN
        RAISE NOTICE 'Found % invoices with missing template references', v_orphaned_count;
        
        -- Get the default invoice template (Classic Professional)
        SELECT id INTO v_default_invoice_template_id
        FROM public.templates
        WHERE name = 'Classic Professional'
        AND template_type = 'invoice'
        AND is_system = true
        AND is_default = true
        LIMIT 1;
        
        IF v_default_invoice_template_id IS NULL THEN
            RAISE EXCEPTION 'Default invoice template not found';
        END IF;
        
        -- Update invoices with missing templates to use the default
        UPDATE public.invoices
        SET template_id = v_default_invoice_template_id
        WHERE template_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM public.templates t WHERE t.id = invoices.template_id
        );
        
        RAISE NOTICE 'Updated % invoices to use default template', v_orphaned_count;
    END IF;
    
    -- Do the same for estimates
    SELECT COUNT(*) INTO v_orphaned_count
    FROM public.estimates e
    WHERE e.template_id IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM public.templates t WHERE t.id = e.template_id
    );
    
    IF v_orphaned_count > 0 THEN
        RAISE NOTICE 'Found % estimates with missing template references', v_orphaned_count;
        
        -- Get the default estimate template
        SELECT id INTO v_default_estimate_template_id
        FROM public.templates
        WHERE name = 'Classic Professional (Estimate)'
        AND template_type = 'estimate'
        AND is_system = true
        AND is_default = true
        LIMIT 1;
        
        IF v_default_estimate_template_id IS NULL THEN
            RAISE EXCEPTION 'Default estimate template not found';
        END IF;
        
        -- Update estimates with missing templates to use the default
        UPDATE public.estimates
        SET template_id = v_default_estimate_template_id
        WHERE template_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM public.templates t WHERE t.id = estimates.template_id
        );
        
        RAISE NOTICE 'Updated % estimates to use default template', v_orphaned_count;
    END IF;
END $$;

-- =====================================
-- ADD TRIGGER TO VALIDATE TEMPLATE REFERENCES
-- =====================================
CREATE OR REPLACE FUNCTION validate_template_reference()
RETURNS TRIGGER AS $$
DECLARE
    v_template_exists BOOLEAN;
    v_template_type VARCHAR;
    v_default_template_id UUID;
BEGIN
    -- If template_id is NULL, allow it
    IF NEW.template_id IS NULL THEN
        RETURN NEW;
    END IF;
    
    -- Check if the template exists and get its type
    SELECT EXISTS(
        SELECT 1 FROM public.templates 
        WHERE id = NEW.template_id
    ), template_type INTO v_template_exists, v_template_type
    FROM public.templates
    WHERE id = NEW.template_id;
    
    -- If template doesn't exist, use the default
    IF NOT v_template_exists THEN
        -- Determine document type based on table name
        IF TG_TABLE_NAME = 'invoices' THEN
            SELECT id INTO v_default_template_id
            FROM public.templates
            WHERE template_type = 'invoice'
            AND is_system = true
            AND is_default = true
            LIMIT 1;
        ELSIF TG_TABLE_NAME = 'estimates' THEN
            SELECT id INTO v_default_template_id
            FROM public.templates
            WHERE template_type = 'estimate'
            AND is_system = true
            AND is_default = true
            LIMIT 1;
        END IF;
        
        IF v_default_template_id IS NOT NULL THEN
            NEW.template_id := v_default_template_id;
            RAISE NOTICE 'Template % not found, using default template %', NEW.template_id, v_default_template_id;
        ELSE
            -- If no default found, set to NULL
            NEW.template_id := NULL;
            RAISE NOTICE 'Template % not found and no default available, setting to NULL', NEW.template_id;
        END IF;
    ELSE
        -- Validate template type matches document type
        IF TG_TABLE_NAME = 'invoices' AND v_template_type != 'invoice' THEN
            RAISE EXCEPTION 'Cannot use % template for invoice', v_template_type;
        ELSIF TG_TABLE_NAME = 'estimates' AND v_template_type != 'estimate' THEN
            RAISE EXCEPTION 'Cannot use % template for estimate', v_template_type;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for invoices and estimates
DROP TRIGGER IF EXISTS validate_invoice_template ON public.invoices;
CREATE TRIGGER validate_invoice_template
    BEFORE INSERT OR UPDATE OF template_id ON public.invoices
    FOR EACH ROW
    EXECUTE FUNCTION validate_template_reference();

DROP TRIGGER IF EXISTS validate_estimate_template ON public.estimates;
CREATE TRIGGER validate_estimate_template
    BEFORE INSERT OR UPDATE OF template_id ON public.estimates
    FOR EACH ROW
    EXECUTE FUNCTION validate_template_reference();

-- =====================================
-- CREATE HELPER FUNCTION FOR API
-- =====================================
CREATE OR REPLACE FUNCTION get_or_create_default_template(
    p_business_id UUID,
    p_template_type VARCHAR
)
RETURNS UUID AS $$
DECLARE
    v_template_id UUID;
BEGIN
    -- Try to get existing default for this business
    SELECT template_id INTO v_template_id
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
    v_orphaned_invoices INTEGER;
    v_orphaned_estimates INTEGER;
BEGIN
    -- Check if any orphaned references remain
    SELECT COUNT(*) INTO v_orphaned_invoices
    FROM public.invoices i
    WHERE i.template_id IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM public.templates t WHERE t.id = i.template_id
    );
    
    SELECT COUNT(*) INTO v_orphaned_estimates
    FROM public.estimates e
    WHERE e.template_id IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM public.templates t WHERE t.id = e.template_id
    );
    
    IF v_orphaned_invoices > 0 OR v_orphaned_estimates > 0 THEN
        RAISE WARNING 'Still have orphaned template references: % invoices, % estimates', 
                      v_orphaned_invoices, v_orphaned_estimates;
    ELSE
        RAISE NOTICE 'All template references are now valid';
    END IF;
END $$;

-- =====================================
-- COMMENTS
-- =====================================
COMMENT ON FUNCTION validate_template_reference() IS 'Ensures all template references are valid, falls back to default if template not found';
COMMENT ON FUNCTION get_or_create_default_template IS 'Helper function to get or create a default template for a business';
