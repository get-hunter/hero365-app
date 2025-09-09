-- =============================================
-- COMPLETE LEGACY CLEANUP MIGRATION
-- Fix view dependencies and remove legacy columns
-- =============================================

-- =============================================
-- 1. VALIDATION BEFORE CLEANUP
-- =============================================

DO $$
DECLARE
    activity_selections_count INTEGER;
    business_trades_count INTEGER;
    businesses_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO activity_selections_count FROM business_activity_selections;
    SELECT COUNT(*) INTO business_trades_count FROM business_trades;
    SELECT COUNT(*) INTO businesses_count FROM businesses;
    
    RAISE NOTICE '=== PRE-CLEANUP VALIDATION ===';
    RAISE NOTICE 'Businesses: %', businesses_count;
    RAISE NOTICE 'Activity selections: %', activity_selections_count;
    RAISE NOTICE 'Business trades: %', business_trades_count;
    
    IF activity_selections_count = 0 AND businesses_count > 0 THEN
        RAISE EXCEPTION 'Cannot proceed: No activity selections found but businesses exist';
    END IF;
    
    IF business_trades_count = 0 AND businesses_count > 0 THEN
        RAISE EXCEPTION 'Cannot proceed: No business trades found but businesses exist';
    END IF;
    
    RAISE NOTICE '✅ Validation passed: Normalized data is in place';
END $$;

-- =============================================
-- 2. FIX VIEW DEPENDENCIES
-- =============================================

-- Drop and recreate v_business_profile without legacy column dependencies
DROP VIEW IF EXISTS v_business_profile;

CREATE OR REPLACE VIEW v_business_profile AS
SELECT 
    -- Core business fields (explicitly listed to avoid legacy columns)
    b.id,
    b.owner_id,
    b.name,
    b.display_name,
    b.email,
    b.phone,
    b.phone_country_code,
    b.phone_display,
    b.website,
    b.address,
    b.city,
    b.state,
    b.postal_code,
    b.country,
    b.timezone,
    b.business_type,
    b.company_size,
    b.market_focus,
    b.years_in_business,
    b.year_established,
    b.license_number,
    b.insurance_number,
    b.certifications,
    b.service_radius,
    b.emergency_available,
    b.business_hours,
    b.is_active,
    b.is_verified,
    b.onboarding_completed,
    b.referral_source,
    b.created_date,
    b.last_modified,
    b.subdomain,
    
    -- Derived trade information from normalized business_trades
    pt.slug as primary_trade_slug,
    pt.display_name as primary_trade_display_name,
    pt.market_type as primary_trade_market_type
FROM businesses b
LEFT JOIN business_trades bt ON bt.business_id = b.id AND bt.is_primary = TRUE
LEFT JOIN trades pt ON bt.trade_id = pt.id;

-- =============================================
-- 3. REMOVE LEGACY COLUMNS
-- =============================================

-- Now safe to drop legacy columns
ALTER TABLE businesses 
  DROP COLUMN IF EXISTS selected_activity_slugs,
  DROP COLUMN IF EXISTS residential_services,
  DROP COLUMN IF EXISTS commercial_services,
  DROP COLUMN IF EXISTS selected_residential_service_keys,
  DROP COLUMN IF EXISTS selected_commercial_service_keys;

-- =============================================
-- 4. REMOVE LEGACY INDEXES
-- =============================================

DROP INDEX IF EXISTS idx_businesses_selected_activity_slugs;
DROP INDEX IF EXISTS idx_businesses_residential_services;
DROP INDEX IF EXISTS idx_businesses_commercial_services;

-- =============================================
-- 5. CREATE COMPATIBILITY VIEWS
-- =============================================

-- Create a compatibility view that mimics the old selected_activity_slugs column
CREATE OR REPLACE VIEW v_business_activities_compat AS
SELECT 
    b.id as business_id,
    b.name as business_name,
    COALESCE(
        array_agg(bas.activity_slug ORDER BY bas.display_order) 
        FILTER (WHERE bas.activity_slug IS NOT NULL), 
        '{}'::text[]
    ) as selected_activity_slugs,
    COUNT(bas.id) as activity_count
FROM businesses b
LEFT JOIN business_activity_selections bas ON bas.business_id = b.id AND bas.is_active = TRUE
GROUP BY b.id, b.name;

-- =============================================
-- 6. ADD DOCUMENTATION
-- =============================================

COMMENT ON VIEW v_business_profile IS 'Business profile view with derived primary trade information from normalized business_trades table. Excludes legacy activity and service columns.';
COMMENT ON VIEW v_business_activities_compat IS 'Compatibility view that provides selected_activity_slugs array for backward compatibility with legacy code.';
COMMENT ON TABLE businesses IS 'Core business entity. Trade relationships managed via business_trades table. Activity selections managed via business_activity_selections table.';

-- Add comments to helper functions
COMMENT ON FUNCTION get_business_activity_slugs(UUID) IS 'Returns active activity slugs for a business - replacement for businesses.selected_activity_slugs column';
COMMENT ON FUNCTION add_business_activity(UUID, TEXT, INTEGER) IS 'Add an activity to a business - replacement for array manipulation on selected_activity_slugs';
COMMENT ON FUNCTION remove_business_activity(UUID, TEXT) IS 'Remove an activity from a business - replacement for array manipulation on selected_activity_slugs';

-- =============================================
-- 7. FINAL VALIDATION AND SUMMARY
-- =============================================

DO $$
DECLARE
    summary_record RECORD;
    total_activities INTEGER;
    total_trades INTEGER;
BEGIN
    RAISE NOTICE '=== LEGACY CLEANUP COMPLETED SUCCESSFULLY ===';
    
    -- Count normalized data
    SELECT COUNT(*) INTO total_activities FROM business_activity_selections WHERE is_active = TRUE;
    SELECT COUNT(*) INTO total_trades FROM business_trades;
    
    RAISE NOTICE 'Active business activity selections: %', total_activities;
    RAISE NOTICE 'Business trade relationships: %', total_trades;
    
    -- Show per-business summary
    RAISE NOTICE '=== PER-BUSINESS SUMMARY ===';
    FOR summary_record IN 
        SELECT 
            b.name as business_name,
            vbp.primary_trade_slug,
            vbp.primary_trade_display_name,
            vbp.market_focus,
            COUNT(bas.id) as activity_count,
            COUNT(bt.id) as trade_count,
            array_agg(bas.activity_slug ORDER BY bas.display_order) FILTER (WHERE bas.activity_slug IS NOT NULL) as activities
        FROM businesses b
        LEFT JOIN v_business_profile vbp ON vbp.id = b.id
        LEFT JOIN business_activity_selections bas ON bas.business_id = b.id AND bas.is_active = TRUE
        LEFT JOIN business_trades bt ON bt.business_id = b.id
        GROUP BY b.id, b.name, vbp.primary_trade_slug, vbp.primary_trade_display_name, vbp.market_focus
        ORDER BY b.name
    LOOP
        RAISE NOTICE 'Business: % | Primary Trade: % (%) | Market: % | Activities: % | Trades: % | Activity List: %', 
            summary_record.business_name,
            COALESCE(summary_record.primary_trade_display_name, 'None'),
            COALESCE(summary_record.primary_trade_slug, 'none'),
            summary_record.market_focus,
            summary_record.activity_count,
            summary_record.trade_count,
            COALESCE(summary_record.activities::text, '{}');
    END LOOP;
    
    RAISE NOTICE '=== MIGRATION SUMMARY ===';
    RAISE NOTICE 'Legacy columns removed: selected_activity_slugs, residential_services, commercial_services, selected_residential_service_keys, selected_commercial_service_keys';
    RAISE NOTICE 'Data preserved in normalized tables: business_activity_selections, business_trades';
    RAISE NOTICE 'Views available: v_business_profile (normalized), v_business_activities_compat (compatibility)';
    RAISE NOTICE 'Helper functions: get_business_activity_slugs(), add_business_activity(), remove_business_activity()';
END $$;
