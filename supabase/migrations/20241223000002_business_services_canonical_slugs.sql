-- Standardize business_services with canonical slugs
-- This creates a single source of truth for business service offerings

-- Add canonical_slug column if it doesn't exist
ALTER TABLE business_services 
ADD COLUMN IF NOT EXISTS canonical_slug text;

-- Backfill canonical_slug from existing service_slug, normalizing to lowercase with hyphens
UPDATE business_services 
SET canonical_slug = lower(regexp_replace(
    COALESCE(service_slug, regexp_replace(service_name, '[^a-zA-Z0-9\s]', '', 'g')), 
    '[^a-zA-Z0-9-]', '-', 'g'
))
WHERE canonical_slug IS NULL OR canonical_slug = '';

-- Make canonical_slug NOT NULL after backfill
ALTER TABLE business_services 
ALTER COLUMN canonical_slug SET NOT NULL;

-- Add unique constraint on canonical_slug per business
ALTER TABLE business_services 
ADD CONSTRAINT business_services_business_canonical_slug_unique 
UNIQUE (business_id, canonical_slug);

-- Add trade_slug column for categorization
ALTER TABLE business_services 
ADD COLUMN IF NOT EXISTS trade_slug text;

-- Backfill trade_slug from business primary_trade_slug
UPDATE business_services bs
SET trade_slug = b.primary_trade_slug
FROM businesses b 
WHERE bs.business_id = b.id 
AND (bs.trade_slug IS NULL OR bs.trade_slug = '');

-- Add sort_order for consistent ordering
ALTER TABLE business_services 
ADD COLUMN IF NOT EXISTS sort_order integer DEFAULT 0;

-- Add is_featured for navigation prominence
ALTER TABLE business_services 
ADD COLUMN IF NOT EXISTS is_featured boolean DEFAULT false;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_business_services_canonical_slug 
ON business_services (canonical_slug);

CREATE INDEX IF NOT EXISTS idx_business_services_business_active_featured 
ON business_services (business_id, is_active, is_featured, sort_order);

CREATE INDEX IF NOT EXISTS idx_business_services_trade_slug 
ON business_services (trade_slug);

-- Add comments for documentation
COMMENT ON COLUMN business_services.canonical_slug IS 'URL-safe canonical slug, unique per business, used for /services/{slug} routes';
COMMENT ON COLUMN business_services.trade_slug IS 'Trade category slug for grouping services (hvac, plumbing, electrical, etc.)';
COMMENT ON COLUMN business_services.sort_order IS 'Display order for navigation menus (lower = higher priority)';
COMMENT ON COLUMN business_services.is_featured IS 'Featured services shown prominently in navigation';

-- Migrate any existing service_template_adoptions to business_services
INSERT INTO business_services (
    business_id,
    canonical_slug,
    service_name,
    trade_slug,
    category,
    is_active,
    adopted_from_slug,
    created_at,
    updated_at
)
SELECT DISTINCT
    sta.business_id,
    COALESCE(st.activity_slug, st.template_slug) as canonical_slug,
    st.name as service_name,
    ta.trade_slug,
    'service' as category,
    true as is_active,
    sta.template_slug as adopted_from_slug,
    sta.adopted_at as created_at,
    NOW() as updated_at
FROM service_template_adoptions sta
JOIN service_templates st ON st.template_slug = sta.template_slug
LEFT JOIN trade_activities ta ON ta.slug = st.activity_slug
WHERE NOT EXISTS (
    SELECT 1 FROM business_services bs 
    WHERE bs.business_id = sta.business_id 
    AND bs.canonical_slug = COALESCE(st.activity_slug, st.template_slug)
);
