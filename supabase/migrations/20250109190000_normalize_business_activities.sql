-- =============================================
-- BUSINESS ACTIVITIES NORMALIZATION MIGRATION
-- Phase 1: Create normalized table and backfill data
-- =============================================

-- =============================================
-- 1. CREATE BUSINESS_ACTIVITY_SELECTIONS TABLE
-- =============================================

CREATE TABLE IF NOT EXISTS business_activity_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    activity_slug TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure unique business-activity combinations
    UNIQUE (business_id, activity_slug)
);

-- Add foreign key constraint to trade_activities if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'trade_activities') THEN
        ALTER TABLE business_activity_selections 
        ADD CONSTRAINT fk_business_activity_selections_activity 
        FOREIGN KEY (activity_slug) REFERENCES trade_activities(slug) ON DELETE RESTRICT;
        
        RAISE NOTICE 'Added foreign key constraint to trade_activities';
    ELSE
        RAISE NOTICE 'trade_activities table not found, skipping FK constraint';
    END IF;
END $$;

-- =============================================
-- 2. CREATE INDEXES FOR PERFORMANCE
-- =============================================

CREATE INDEX IF NOT EXISTS idx_business_activity_selections_business_id 
    ON business_activity_selections(business_id);

CREATE INDEX IF NOT EXISTS idx_business_activity_selections_activity_slug 
    ON business_activity_selections(activity_slug);

CREATE INDEX IF NOT EXISTS idx_business_activity_selections_active 
    ON business_activity_selections(business_id, is_active) 
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_business_activity_selections_display_order 
    ON business_activity_selections(business_id, display_order, activity_slug);

-- =============================================
-- 3. BACKFILL FROM SELECTED_ACTIVITY_SLUGS
-- =============================================

-- Backfill business_activity_selections from businesses.selected_activity_slugs
INSERT INTO business_activity_selections (business_id, activity_slug, display_order, created_at, updated_at)
SELECT 
    b.id as business_id,
    activity_slug,
    row_number() OVER (PARTITION BY b.id ORDER BY ordinality) - 1 as display_order,
    COALESCE(b.created_date, NOW()) as created_at,
    COALESCE(b.last_modified, NOW()) as updated_at
FROM businesses b,
     unnest(COALESCE(b.selected_activity_slugs, '{}')) WITH ORDINALITY AS t(activity_slug, ordinality)
WHERE b.selected_activity_slugs IS NOT NULL 
  AND array_length(b.selected_activity_slugs, 1) > 0
  AND activity_slug IS NOT NULL 
  AND trim(activity_slug) != ''
ON CONFLICT (business_id, activity_slug) DO UPDATE SET
    display_order = EXCLUDED.display_order,
    updated_at = EXCLUDED.updated_at;

-- =============================================
-- 4. CREATE V_BUSINESS_PROFILE VIEW
-- =============================================

-- Create a view that provides business profile with derived primary_trade_slug
CREATE OR REPLACE VIEW v_business_profile AS
SELECT 
    b.*,
    -- Derive primary_trade_slug from business_trades
    pt.slug as primary_trade_slug,
    pt.display_name as primary_trade_display_name,
    pt.market_type as primary_trade_market_type
FROM businesses b
LEFT JOIN business_trades bt ON bt.business_id = b.id AND bt.is_primary = TRUE
LEFT JOIN trades pt ON bt.trade_id = pt.id;

-- =============================================
-- 5. CREATE HELPER FUNCTIONS
-- =============================================

-- Function to get business activity slugs (replacement for array column)
CREATE OR REPLACE FUNCTION get_business_activity_slugs(business_uuid UUID)
RETURNS TEXT[] AS $$
BEGIN
    RETURN ARRAY(
        SELECT activity_slug 
        FROM business_activity_selections 
        WHERE business_id = business_uuid 
          AND is_active = TRUE 
        ORDER BY display_order, activity_slug
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to add activity to business
CREATE OR REPLACE FUNCTION add_business_activity(
    business_uuid UUID, 
    activity_slug_param TEXT,
    display_order_param INTEGER DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    next_order INTEGER;
BEGIN
    -- Get next display order if not provided
    IF display_order_param IS NULL THEN
        SELECT COALESCE(MAX(display_order), -1) + 1 
        INTO next_order
        FROM business_activity_selections 
        WHERE business_id = business_uuid;
    ELSE
        next_order := display_order_param;
    END IF;
    
    -- Insert or update
    INSERT INTO business_activity_selections (business_id, activity_slug, display_order)
    VALUES (business_uuid, activity_slug_param, next_order)
    ON CONFLICT (business_id, activity_slug) DO UPDATE SET
        is_active = TRUE,
        display_order = EXCLUDED.display_order,
        updated_at = NOW();
    
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Function to remove activity from business
CREATE OR REPLACE FUNCTION remove_business_activity(
    business_uuid UUID, 
    activity_slug_param TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE business_activity_selections 
    SET is_active = FALSE, updated_at = NOW()
    WHERE business_id = business_uuid 
      AND activity_slug = activity_slug_param;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 6. VALIDATION AND SUMMARY
-- =============================================

-- Validation query to check backfill success
DO $$
DECLARE
    original_count INTEGER;
    backfilled_count INTEGER;
    businesses_with_activities INTEGER;
    summary_record RECORD;
BEGIN
    -- Count original activity selections
    SELECT COUNT(*) INTO original_count
    FROM (
        SELECT DISTINCT b.id, unnest(b.selected_activity_slugs) as activity_slug
        FROM businesses b
        WHERE b.selected_activity_slugs IS NOT NULL 
          AND array_length(b.selected_activity_slugs, 1) > 0
    ) original;
    
    -- Count backfilled selections
    SELECT COUNT(*) INTO backfilled_count
    FROM business_activity_selections;
    
    -- Count businesses with activities
    SELECT COUNT(DISTINCT business_id) INTO businesses_with_activities
    FROM business_activity_selections;
    
    RAISE NOTICE '=== BUSINESS ACTIVITIES NORMALIZATION SUMMARY ===';
    RAISE NOTICE 'Original activity selections: %', original_count;
    RAISE NOTICE 'Backfilled activity selections: %', backfilled_count;
    RAISE NOTICE 'Businesses with activities: %', businesses_with_activities;
    
    -- Show per-business breakdown
    FOR summary_record IN 
        SELECT 
            b.name as business_name,
            array_length(b.selected_activity_slugs, 1) as original_count,
            COUNT(bas.id) as backfilled_count,
            array_agg(bas.activity_slug ORDER BY bas.display_order) as activities
        FROM businesses b
        LEFT JOIN business_activity_selections bas ON bas.business_id = b.id
        WHERE b.selected_activity_slugs IS NOT NULL 
          AND array_length(b.selected_activity_slugs, 1) > 0
        GROUP BY b.id, b.name, b.selected_activity_slugs
        ORDER BY b.name
    LOOP
        RAISE NOTICE 'Business: % | Original: % | Backfilled: % | Activities: %', 
            summary_record.business_name, 
            summary_record.original_count, 
            summary_record.backfilled_count,
            summary_record.activities;
    END LOOP;
    
    -- Validation check
    IF original_count != backfilled_count THEN
        RAISE WARNING 'Backfill count mismatch! Original: %, Backfilled: %', original_count, backfilled_count;
    ELSE
        RAISE NOTICE '✅ Backfill validation passed: all activity selections migrated successfully';
    END IF;
    
    RAISE NOTICE '=== MIGRATION PHASE 1 COMPLETED ===';
END $$;
