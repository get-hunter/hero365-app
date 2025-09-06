-- Unify location model: merge business_locations into service_areas
-- This creates a single source of truth for both physical locations and service coverage areas

-- Add new columns to service_areas
ALTER TABLE service_areas 
ADD COLUMN IF NOT EXISTS kind text CHECK (kind IN ('physical', 'coverage')) DEFAULT 'coverage',
ADD COLUMN IF NOT EXISTS location_slug text DEFAULT '',
ADD COLUMN IF NOT EXISTS address text,
ADD COLUMN IF NOT EXISTS county text,
ADD COLUMN IF NOT EXISTS is_primary boolean DEFAULT false;

-- Backfill location_slug for existing service_areas (coverage areas)
-- Handle cases where city or state might be null
UPDATE service_areas 
SET location_slug = lower(regexp_replace(
    COALESCE(city, 'unknown') || '-' || COALESCE(state, 'xx'), 
    '[^a-zA-Z0-9-]', '-', 'g'
))
WHERE location_slug = '' OR location_slug IS NULL;

-- Remove duplicates by keeping only the first record for each business_id + location_slug combination
DELETE FROM service_areas 
WHERE id NOT IN (
    SELECT DISTINCT ON (business_id, location_slug) id
    FROM service_areas
    ORDER BY business_id, location_slug, created_at ASC
);

-- Remove any remaining empty location_slugs to avoid constraint violations
DELETE FROM service_areas 
WHERE location_slug = '' OR location_slug IS NULL;

-- Now make location_slug NOT NULL and add unique constraint
ALTER TABLE service_areas 
ALTER COLUMN location_slug SET NOT NULL;

ALTER TABLE service_areas 
ADD CONSTRAINT service_areas_business_location_slug_unique 
UNIQUE (business_id, location_slug);

-- Migrate data from business_locations to service_areas as physical locations
INSERT INTO service_areas (
    business_id, 
    kind, 
    location_slug,
    area_name, 
    city, 
    state, 
    postal_code,
    address,
    county,
    service_radius_miles, 
    is_active, 
    is_primary,
    created_at, 
    updated_at
)
SELECT 
    bl.business_id,
    'physical' as kind,
    lower(regexp_replace(bl.city || '-' || bl.state, '[^a-zA-Z0-9-]', '-', 'g')) as location_slug,
    bl.name as area_name,
    bl.city,
    bl.state,
    bl.postal_code,
    bl.address,
    bl.county,
    COALESCE(bl.service_radius, 25) as service_radius_miles,
    bl.is_active,
    bl.is_primary,
    bl.created_at,
    bl.updated_at
FROM business_locations bl
WHERE NOT EXISTS (
    SELECT 1 FROM service_areas sa 
    WHERE sa.business_id = bl.business_id 
    AND sa.location_slug = lower(regexp_replace(bl.city || '-' || bl.state, '[^a-zA-Z0-9-]', '-', 'g'))
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_service_areas_business_kind_active 
ON service_areas (business_id, kind, is_active);

CREATE INDEX IF NOT EXISTS idx_service_areas_location_slug 
ON service_areas (location_slug);

-- Add comment for documentation
COMMENT ON COLUMN service_areas.kind IS 'Type of location: physical (business address) or coverage (service area)';
COMMENT ON COLUMN service_areas.location_slug IS 'URL-safe slug derived from city-state, unique per business';
COMMENT ON COLUMN service_areas.is_primary IS 'True for the primary physical location (used for NAP, schema)';
