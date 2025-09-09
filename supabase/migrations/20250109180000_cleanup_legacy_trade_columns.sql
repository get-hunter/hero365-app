-- =============================================
-- LEGACY TRADE COLUMNS CLEANUP MIGRATION
-- Phase 3: Remove deprecated columns and optimize schema
-- =============================================

-- =============================================
-- 1. VERIFY DATA INTEGRITY BEFORE CLEANUP
-- =============================================

-- Ensure all business_services have proper trade relationships
DO $$
DECLARE
  missing_trades INTEGER;
  missing_service_types INTEGER;
BEGIN
  -- Check for services without trade_id
  SELECT COUNT(*) INTO missing_trades
  FROM business_services 
  WHERE is_active = true AND trade_id IS NULL;
  
  -- Check for services without service_type_id
  SELECT COUNT(*) INTO missing_service_types
  FROM business_services 
  WHERE is_active = true AND service_type_id IS NULL;
  
  IF missing_trades > 0 THEN
    RAISE EXCEPTION 'Cannot proceed with cleanup: % active services missing trade_id', missing_trades;
  END IF;
  
  IF missing_service_types > 0 THEN
    RAISE EXCEPTION 'Cannot proceed with cleanup: % active services missing service_type_id', missing_service_types;
  END IF;
  
  RAISE NOTICE 'Data integrity check passed: All active services have proper trade and service type relationships';
END $$;

-- =============================================
-- 2. PREPARE FOR LEGACY COLUMN REMOVAL
-- =============================================

-- We'll create the legacy compatibility view after removing the deprecated columns

-- =============================================
-- 3. REMOVE DEPRECATED COLUMNS FROM BUSINESSES TABLE
-- =============================================

-- These columns are now replaced by business_trades table
ALTER TABLE businesses 
  DROP COLUMN IF EXISTS secondary_trades,
  DROP COLUMN IF EXISTS primary_trade,
  DROP COLUMN IF EXISTS primary_trade_slug;

-- =============================================
-- 4. UPDATE VIEWS TO REMOVE CATEGORY_ID DEPENDENCY
-- =============================================

-- Update v_service_catalog to remove legacy_category_id reference
DROP VIEW IF EXISTS v_service_catalog;

CREATE VIEW v_service_catalog AS
SELECT
  bs.id,
  bs.business_id,
  bs.service_name,
  bs.service_slug,
  bs.canonical_slug,
  bs.description,
  
  -- Trade information (standardized naming)
  t.id as trade_id,
  t.slug as trade_slug,
  t.display_name as trade_display_name,
  t.icon as trade_icon,
  t.color as trade_color,
  t.market_type as trade_market_type,
  
  -- Service Type information
  st.id as service_type_id,
  st.code as service_type_code,
  st.display_name as service_type_display_name,
  st.is_emergency as service_type_is_emergency,
  st.typical_duration_hours,
  
  -- Pricing and booking
  bs.base_price,
  bs.price_type,
  bs.price_min,
  bs.price_max,
  bs.price_unit,
  bs.estimated_duration_minutes,
  bs.is_bookable,
  bs.is_emergency,
  
  -- Service characteristics
  bs.is_commercial,
  bs.is_residential,
  bs.is_active,
  bs.is_featured,
  bs.display_order,
  
  -- Metadata
  bs.created_at,
  bs.updated_at
FROM business_services bs
LEFT JOIN trades t ON bs.trade_id = t.id
LEFT JOIN service_types st ON bs.service_type_id = st.id;

-- =============================================
-- 5. REMOVE DEPRECATED CATEGORY_ID FROM BUSINESS_SERVICES
-- =============================================

-- Drop the legacy view that depends on category_id
DROP VIEW IF EXISTS v_business_services_legacy;

-- category_id is replaced by trade_id + service_type_id
ALTER TABLE business_services 
  DROP COLUMN IF EXISTS category_id;

-- Recreate the legacy compatibility view without category_id dependency
CREATE OR REPLACE VIEW v_business_services_legacy AS
SELECT
  bs.*,
  t.slug as trade_slug_computed,
  t.display_name as category_computed,
  st.code as service_type_code_computed
FROM business_services bs
LEFT JOIN trades t ON bs.trade_id = t.id
LEFT JOIN service_types st ON bs.service_type_id = st.id;

-- =============================================
-- 6. ADD NOT NULL CONSTRAINTS FOR CANONICAL FIELDS
-- =============================================

-- Ensure trade_id and service_type_id are required for active services
-- (We already verified data integrity above)

-- Add NOT NULL constraint for trade_id on active services
ALTER TABLE business_services 
  ADD CONSTRAINT chk_active_services_have_trade 
  CHECK (is_active = false OR trade_id IS NOT NULL);

-- Add NOT NULL constraint for service_type_id on active services  
ALTER TABLE business_services 
  ADD CONSTRAINT chk_active_services_have_service_type 
  CHECK (is_active = false OR service_type_id IS NOT NULL);

-- =============================================
-- 7. OPTIMIZE FEATURED_PROJECTS TABLE
-- =============================================

-- Remove the free-text trade column since we now have proper references
ALTER TABLE featured_projects 
  DROP COLUMN IF EXISTS trade;

-- Make trade_id NOT NULL for new projects (existing can be NULL during transition)
-- This will be enforced at the application level for new inserts

-- =============================================
-- 8. CREATE OPTIMIZED INDEXES
-- =============================================

-- Remove old indexes that are no longer needed
DROP INDEX IF EXISTS idx_business_services_category_id;
DROP INDEX IF EXISTS idx_businesses_primary_trade;
DROP INDEX IF EXISTS idx_businesses_secondary_trades;

-- Add optimized indexes for the new structure
CREATE INDEX IF NOT EXISTS idx_business_services_active_trade 
  ON business_services(business_id, trade_id) 
  WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_business_services_active_service_type 
  ON business_services(business_id, service_type_id) 
  WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_business_services_bookable_trade 
  ON business_services(trade_id, is_bookable) 
  WHERE is_active = true AND is_bookable = true;

-- =============================================
-- 9. UPDATE BUSINESS_BRANDING TRADE CUSTOMIZATIONS
-- =============================================

-- Update trade_customizations JSONB to use new trade slugs
-- This is a complex operation that would need to be done carefully in production
-- For now, we'll add a comment for manual review

-- TODO: Review and update trade_customizations JSONB in business_branding table
-- to use canonical trade slugs from the trades table instead of legacy references

-- =============================================
-- 10. CREATE MIGRATION SUMMARY FUNCTION
-- =============================================

CREATE OR REPLACE FUNCTION get_trade_consolidation_summary()
RETURNS TABLE (
  metric text,
  count bigint,
  details text
) AS $$
BEGIN
  RETURN QUERY
  SELECT 'Total Trades'::text, COUNT(*)::bigint, 'Canonical trade taxonomy'::text FROM trades WHERE is_active = true
  UNION ALL
  SELECT 'Trade Profiles'::text, COUNT(*)::bigint, 'SEO/website taxonomy (kept for content)'::text FROM trade_profiles
  UNION ALL
  SELECT 'Bridge Mappings'::text, COUNT(*)::bigint, 'trade_profiles -> trades mappings'::text FROM trade_profile_to_trade
  UNION ALL
  SELECT 'Business-Trade Relationships'::text, COUNT(*)::bigint, 'Primary and secondary trade relationships'::text FROM business_trades
  UNION ALL
  SELECT 'Services with Trade ID'::text, COUNT(*)::bigint, 'Active services with proper trade classification'::text 
    FROM business_services WHERE is_active = true AND trade_id IS NOT NULL
  UNION ALL
  SELECT 'Services with Service Type'::text, COUNT(*)::bigint, 'Active services with proper service type classification'::text 
    FROM business_services WHERE is_active = true AND service_type_id IS NOT NULL
  UNION ALL
  SELECT 'Featured Projects with Trade'::text, COUNT(*)::bigint, 'Projects with proper trade classification'::text 
    FROM featured_projects WHERE trade_id IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 11. FINAL VERIFICATION AND SUMMARY
-- =============================================

-- Run the summary to verify everything is working
DO $$
DECLARE
  summary_record RECORD;
BEGIN
  RAISE NOTICE '=== TRADE CONSOLIDATION MIGRATION SUMMARY ===';
  
  FOR summary_record IN 
    SELECT * FROM get_trade_consolidation_summary() ORDER BY metric
  LOOP
    RAISE NOTICE '% : % (%)', summary_record.metric, summary_record.count, summary_record.details;
  END LOOP;
  
  RAISE NOTICE '=== MIGRATION COMPLETED SUCCESSFULLY ===';
  RAISE NOTICE 'Legacy columns removed, constraints added, indexes optimized';
  RAISE NOTICE 'All active services now use canonical trade and service type relationships';
  RAISE NOTICE 'Business trade relationships managed via business_trades table';
  RAISE NOTICE 'SEO taxonomy preserved in trade_profiles for website content';
END $$;

-- =============================================
-- CLEANUP TEMPORARY FUNCTIONS
-- =============================================

-- Keep the summary function for future reference, but clean up migration helpers
DROP FUNCTION IF EXISTS map_category_to_trade_slug(TEXT, TEXT);
DROP FUNCTION IF EXISTS map_service_to_type_code(TEXT, BOOLEAN);
