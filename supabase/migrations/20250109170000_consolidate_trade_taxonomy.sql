-- =============================================
-- TRADE TAXONOMY CONSOLIDATION MIGRATION
-- Phase 1: Bridge Tables, Sync Triggers, and Data Normalization
-- =============================================

-- =============================================
-- 1. EXTEND TRADES TABLE WITH MISSING ENTRIES
-- =============================================

-- Add missing trades from trade_profiles to make trades the canonical source
INSERT INTO trades (slug, name, display_name, description, icon, color, market_type, display_order) VALUES
-- Missing from trade_profiles that should be in canonical trades
('carpentry-joinery', 'carpentry-joinery', 'Carpentry & Joinery', 'Carpentry and joinery services including custom woodwork', 'carpentry-icon', '#8b4513', 'both', 19),
('commercial-kitchen-equipment', 'commercial-kitchen-equipment', 'Commercial Kitchen Equipment', 'Commercial kitchen equipment installation and maintenance', 'kitchen-equipment-icon', '#be123c', 'commercial', 20),
('commercial-refrigeration', 'commercial-refrigeration', 'Commercial Refrigeration', 'Commercial refrigeration systems and walk-in coolers', 'refrigeration-icon', '#0ea5e9', 'commercial', 21),
('drywall-interior-finishing', 'drywall-interior-finishing', 'Drywall & Interior Finishing', 'Drywall installation, taping, texturing, and interior finishing', 'drywall-icon', '#6b7280', 'both', 22),
('flooring-tiling', 'flooring-tiling', 'Flooring & Tiling', 'Flooring installation and tile work', 'flooring-icon', '#92400e', 'both', 23),
('landscaping-gardening', 'landscaping-gardening', 'Landscaping & Gardening', 'Landscaping design, installation, and garden maintenance', 'landscaping-icon', '#059669', 'both', 24),
('metal-fabrication', 'metal-fabrication', 'Metal Fabrication', 'Custom metal fabrication including railings and frames', 'metal-icon', '#374151', 'both', 25),
('metal-roofing', 'metal-roofing', 'Metal Roofing', 'Standing seam and sheet metal roofing systems', 'metal-roofing-icon', '#10b981', 'both', 26),
('painting-decorating', 'painting-decorating', 'Painting & Decorating', 'Interior and exterior painting and decorating services', 'painting-icon', '#d97706', 'both', 27),
('plastering-stucco', 'plastering-stucco', 'Plastering & Stucco', 'Plastering and stucco application services', 'plaster-icon', '#a3a3a3', 'both', 28),
('solar-pv', 'solar-pv', 'Solar PV', 'Solar photovoltaic system design, installation, and maintenance', 'solar-icon', '#fbbf24', 'both', 29)
ON CONFLICT (slug) DO UPDATE SET
  display_name = EXCLUDED.display_name,
  description = EXCLUDED.description,
  market_type = EXCLUDED.market_type,
  updated_at = now();

-- Update existing trades with proper display names and market types
UPDATE trades SET 
  display_name = 'HVAC',
  market_type = 'both',
  updated_at = now()
WHERE slug = 'hvac';

UPDATE trades SET 
  display_name = 'General Contractor',
  updated_at = now()
WHERE slug = 'general-contractor';

-- Standardize naming inconsistencies between tables
UPDATE trades SET 
  display_name = 'Garage Doors',
  updated_at = now()
WHERE slug = 'garage-door';

UPDATE trades SET 
  display_name = 'Chimney & Fireplace',
  updated_at = now()
WHERE slug = 'chimney';

UPDATE trades SET 
  display_name = 'Septic Systems',
  updated_at = now()
WHERE slug = 'septic';

UPDATE trades SET 
  display_name = 'Landscaping & Gardening',
  updated_at = now()
WHERE slug = 'landscaping';

UPDATE trades SET 
  display_name = 'Painting & Decorating',
  updated_at = now()
WHERE slug = 'painting';

-- =============================================
-- 2. CREATE BRIDGE TABLE FOR TRADE TAXONOMIES
-- =============================================

CREATE TABLE IF NOT EXISTS trade_profile_to_trade (
  trade_profile_slug text PRIMARY KEY REFERENCES trade_profiles(slug) ON DELETE CASCADE,
  trade_id uuid NOT NULL REFERENCES trades(id) ON DELETE RESTRICT,
  mapping_type text NOT NULL DEFAULT 'equivalent' CHECK (mapping_type IN ('equivalent','broader','narrower','custom')),
  notes text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_trade_profile_to_trade_id ON trade_profile_to_trade(trade_id);

-- Populate bridge table with direct slug matches
INSERT INTO trade_profile_to_trade (trade_profile_slug, trade_id, mapping_type)
SELECT tp.slug, t.id, 'equivalent'
FROM trade_profiles tp
JOIN trades t ON t.slug = tp.slug
ON CONFLICT (trade_profile_slug) DO NOTHING;

-- Add custom mappings for non-exact matches
INSERT INTO trade_profile_to_trade (trade_profile_slug, trade_id, mapping_type, notes) VALUES
('garage-doors', (SELECT id FROM trades WHERE slug = 'garage-door'), 'equivalent', 'Slug normalization: garage-doors -> garage-door'),
('chimney-fireplace', (SELECT id FROM trades WHERE slug = 'chimney'), 'equivalent', 'Slug normalization: chimney-fireplace -> chimney'),
('septic-systems', (SELECT id FROM trades WHERE slug = 'septic'), 'equivalent', 'Slug normalization: septic-systems -> septic'),
('landscaping-gardening', (SELECT id FROM trades WHERE slug = 'landscaping-gardening'), 'equivalent', 'Direct match after trade addition'),
('painting-decorating', (SELECT id FROM trades WHERE slug = 'painting-decorating'), 'equivalent', 'Direct match after trade addition'),
('commercial-kitchen-equipment', (SELECT id FROM trades WHERE slug = 'kitchen-equipment'), 'broader', 'Kitchen equipment is broader category'),
('commercial-refrigeration', (SELECT id FROM trades WHERE slug = 'refrigeration'), 'broader', 'Refrigeration is broader category')
ON CONFLICT (trade_profile_slug) DO NOTHING;

-- =============================================
-- 3. CREATE BUSINESS-TRADE MANY-TO-MANY TABLE
-- =============================================

CREATE TABLE IF NOT EXISTS business_trades (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id uuid NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  trade_id uuid NOT NULL REFERENCES trades(id) ON DELETE RESTRICT,
  is_primary boolean NOT NULL DEFAULT false,
  proficiency_level text DEFAULT 'standard' CHECK (proficiency_level IN ('beginner', 'standard', 'expert', 'master')),
  years_experience integer DEFAULT 0,
  certifications jsonb DEFAULT '[]'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE (business_id, trade_id)
);

CREATE INDEX IF NOT EXISTS idx_business_trades_business_id ON business_trades(business_id);
CREATE INDEX IF NOT EXISTS idx_business_trades_trade_id ON business_trades(trade_id);
CREATE INDEX IF NOT EXISTS idx_business_trades_primary ON business_trades(business_id, is_primary) WHERE is_primary = true;

-- =============================================
-- 4. SYNC TRIGGERS FOR BUSINESS_SERVICES
-- =============================================

-- Function to sync trade_id <-> trade_slug
CREATE OR REPLACE FUNCTION sync_business_services_trade() RETURNS trigger AS $$
BEGIN
  -- If trade_id is set, sync trade_slug
  IF NEW.trade_id IS NOT NULL THEN
    SELECT slug INTO NEW.trade_slug FROM trades WHERE id = NEW.trade_id;
  -- If trade_slug is set but trade_id is null, sync trade_id
  ELSIF NEW.trade_slug IS NOT NULL AND NEW.trade_id IS NULL THEN
    SELECT id INTO NEW.trade_id FROM trades WHERE slug = NEW.trade_slug;
  END IF;
  
  -- Ensure we have both or neither
  IF (NEW.trade_id IS NULL) != (NEW.trade_slug IS NULL) THEN
    RAISE EXCEPTION 'trade_id and trade_slug must be consistent. trade_id: %, trade_slug: %', NEW.trade_id, NEW.trade_slug;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to sync service_type_id <-> service_type_code
CREATE OR REPLACE FUNCTION sync_business_services_service_type() RETURNS trigger AS $$
BEGIN
  -- If service_type_id is set, sync service_type_code
  IF NEW.service_type_id IS NOT NULL THEN
    SELECT code INTO NEW.service_type_code FROM service_types WHERE id = NEW.service_type_id;
  -- If service_type_code is set but service_type_id is null, sync service_type_id
  ELSIF NEW.service_type_code IS NOT NULL AND NEW.service_type_id IS NULL THEN
    SELECT id INTO NEW.service_type_id FROM service_types WHERE code = NEW.service_type_code;
  END IF;
  
  -- Ensure we have both or neither
  IF (NEW.service_type_id IS NULL) != (NEW.service_type_code IS NULL) THEN
    RAISE EXCEPTION 'service_type_id and service_type_code must be consistent. service_type_id: %, service_type_code: %', NEW.service_type_id, NEW.service_type_code;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
DROP TRIGGER IF EXISTS trg_business_services_trade_sync ON business_services;
CREATE TRIGGER trg_business_services_trade_sync
  BEFORE INSERT OR UPDATE ON business_services
  FOR EACH ROW EXECUTE FUNCTION sync_business_services_trade();

DROP TRIGGER IF EXISTS trg_business_services_service_type_sync ON business_services;
CREATE TRIGGER trg_business_services_service_type_sync
  BEFORE INSERT OR UPDATE ON business_services
  FOR EACH ROW EXECUTE FUNCTION sync_business_services_service_type();

-- =============================================
-- 5. BACKFILL BUSINESS_TRADES FROM EXISTING DATA
-- =============================================

-- Backfill primary trades from businesses.primary_trade_slug
INSERT INTO business_trades (business_id, trade_id, is_primary, proficiency_level)
SELECT DISTINCT
  b.id,
  m.trade_id,
  true,
  'standard'
FROM businesses b
JOIN trade_profile_to_trade m ON m.trade_profile_slug = b.primary_trade_slug
WHERE b.primary_trade_slug IS NOT NULL
ON CONFLICT (business_id, trade_id) DO UPDATE SET
  is_primary = true,
  updated_at = now();

-- Backfill secondary trades from businesses.secondary_trades array
INSERT INTO business_trades (business_id, trade_id, is_primary, proficiency_level)
SELECT DISTINCT
  b.id,
  m.trade_id,
  false,
  'standard'
FROM businesses b,
     unnest(COALESCE(b.secondary_trades, '{}')) AS s(slug)
JOIN trade_profile_to_trade m ON m.trade_profile_slug = s.slug
WHERE b.secondary_trades IS NOT NULL AND array_length(b.secondary_trades, 1) > 0
ON CONFLICT (business_id, trade_id) DO UPDATE SET
  updated_at = now();

-- =============================================
-- 6. ENHANCE FEATURED_PROJECTS WITH TRADE REFERENCES
-- =============================================

-- Add trade reference columns to featured_projects
ALTER TABLE featured_projects 
  ADD COLUMN IF NOT EXISTS trade_profile_slug text,
  ADD COLUMN IF NOT EXISTS trade_id uuid REFERENCES trades(id);

-- Backfill trade_profile_slug from free-text trade field
UPDATE featured_projects fp
SET trade_profile_slug = tp.slug
FROM trade_profiles tp
WHERE lower(trim(fp.trade)) = lower(tp.slug) 
  AND fp.trade_profile_slug IS NULL
  AND fp.trade IS NOT NULL;

-- Backfill trade_id via mapping
UPDATE featured_projects fp
SET trade_id = m.trade_id
FROM trade_profile_to_trade m
WHERE fp.trade_profile_slug = m.trade_profile_slug 
  AND fp.trade_id IS NULL;

-- =============================================
-- 7. STANDARDIZE V_SERVICE_CATALOG VIEW
-- =============================================

-- Drop and recreate the view with standardized naming
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
  
  -- Legacy fields (marked for deprecation)
  bs.category_id as legacy_category_id,
  
  -- Metadata
  bs.created_at,
  bs.updated_at
FROM business_services bs
LEFT JOIN trades t ON bs.trade_id = t.id
LEFT JOIN service_types st ON bs.service_type_id = st.id;

-- =============================================
-- 8. ADD PERFORMANCE INDEXES
-- =============================================

-- Business services indexes
CREATE INDEX IF NOT EXISTS idx_business_services_trade_active ON business_services(trade_id, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_business_services_business_trade ON business_services(business_id, trade_id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_business_services_bookable ON business_services(business_id, is_bookable) WHERE is_bookable = true AND is_active = true;

-- Canonical slug uniqueness per business (critical for URL stability)
CREATE UNIQUE INDEX IF NOT EXISTS ux_business_services_business_canonical
ON business_services(business_id, canonical_slug) WHERE is_active = true;

-- Service slug uniqueness per business (if used for public URLs)
CREATE UNIQUE INDEX IF NOT EXISTS ux_business_services_business_service_slug
ON business_services(business_id, service_slug) WHERE is_active = true AND service_slug IS NOT NULL;

-- =============================================
-- 9. ADD HELPFUL CONSTRAINTS
-- =============================================

-- Ensure only one primary trade per business
CREATE OR REPLACE FUNCTION check_single_primary_trade() RETURNS trigger AS $$
BEGIN
  IF NEW.is_primary = true THEN
    -- Remove primary flag from other trades for this business
    UPDATE business_trades 
    SET is_primary = false, updated_at = now()
    WHERE business_id = NEW.business_id 
      AND trade_id != NEW.trade_id 
      AND is_primary = true;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_business_trades_single_primary ON business_trades;
CREATE TRIGGER trg_business_trades_single_primary
  BEFORE INSERT OR UPDATE ON business_trades
  FOR EACH ROW 
  WHEN (NEW.is_primary = true)
  EXECUTE FUNCTION check_single_primary_trade();

-- =============================================
-- 10. UPDATE EXISTING BUSINESS_SERVICES DATA
-- =============================================

-- Fix any business_services that have trade_slug but missing trade_id
UPDATE business_services 
SET trade_id = t.id,
    updated_at = now()
FROM trades t
WHERE business_services.trade_slug = t.slug 
  AND business_services.trade_id IS NULL;

-- Fix any business_services that have service_type_code but missing service_type_id
UPDATE business_services 
SET service_type_id = st.id,
    updated_at = now()
FROM service_types st
WHERE business_services.service_type_code = st.code 
  AND business_services.service_type_id IS NULL;

-- =============================================
-- SUMMARY
-- =============================================

-- Log completion
DO $$
BEGIN
  RAISE NOTICE 'Trade taxonomy consolidation migration completed successfully';
  RAISE NOTICE 'Created bridge table: trade_profile_to_trade';
  RAISE NOTICE 'Created business-trade relationships: business_trades';
  RAISE NOTICE 'Added sync triggers for business_services';
  RAISE NOTICE 'Standardized v_service_catalog view';
  RAISE NOTICE 'Enhanced featured_projects with trade references';
  RAISE NOTICE 'Added performance indexes and constraints';
END $$;
