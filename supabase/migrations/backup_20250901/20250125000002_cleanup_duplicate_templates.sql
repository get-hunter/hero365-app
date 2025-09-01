-- =====================================
-- Clean Up Duplicate System Templates
-- =====================================
-- This migration removes duplicate system templates created by multiple seeding migrations
-- Keeps only the templates from the latest seeding (mobile app specifications)

-- =====================================
-- REMOVE OLDER SYSTEM TEMPLATES
-- =====================================

-- Delete templates created by the earlier seeding migration (20250818131000)
-- Keep only templates created by the latest migration (20250125000001) with mobile app specs
DELETE FROM public.templates 
WHERE is_system = true 
AND created_by = 'system'
AND created_at < '2025-01-25 00:00:01'::timestamp;

-- =====================================
-- VERIFICATION
-- =====================================
DO $$
DECLARE
    v_template_count INTEGER;
    v_invoice_count INTEGER;
    v_estimate_count INTEGER;
BEGIN
    -- Count total system templates (should be 22)
    SELECT COUNT(*) INTO v_template_count
    FROM public.templates
    WHERE is_system = true;
    
    -- Count by type
    SELECT COUNT(*) INTO v_invoice_count
    FROM public.templates
    WHERE is_system = true AND template_type = 'invoice';
    
    SELECT COUNT(*) INTO v_estimate_count
    FROM public.templates
    WHERE is_system = true AND template_type = 'estimate';
    
    RAISE NOTICE 'System templates after cleanup: % total (% invoices, % estimates)', 
                 v_template_count, v_invoice_count, v_estimate_count;
    
    -- Verify we have exactly 22 templates
    IF v_template_count != 22 THEN
        RAISE WARNING 'Expected 22 system templates, found %', v_template_count;
    END IF;
    
    -- Verify defaults exist
    IF NOT EXISTS (
        SELECT 1 FROM public.templates 
        WHERE name = 'Classic Professional' 
        AND template_type = 'invoice'
        AND is_default = true 
        AND is_system = true
    ) THEN
        RAISE WARNING 'Classic Professional invoice template should be default';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM public.templates 
        WHERE name = 'Classic Professional (Estimate)' 
        AND template_type = 'estimate'
        AND is_default = true 
        AND is_system = true
    ) THEN
        RAISE WARNING 'Classic Professional estimate template should be default';
    END IF;
END $$;

COMMENT ON TABLE public.templates IS 'System templates cleaned up - contains 11 unique templates for both invoice and estimate types from mobile app specifications';
