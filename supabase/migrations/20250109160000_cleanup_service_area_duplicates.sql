-- =============================================
-- CLEANUP SERVICE AREA DUPLICATES
-- =============================================

-- Remove duplicate service areas, keeping the oldest record for each (business_id, country_code, postal_code)
WITH duplicates_to_remove AS (
  SELECT 
    id,
    ROW_NUMBER() OVER (
      PARTITION BY business_id, country_code, postal_code 
      ORDER BY created_at ASC
    ) as rn
  FROM service_areas 
  WHERE postal_code IS NOT NULL 
    AND is_active = TRUE
)
DELETE FROM service_areas 
WHERE id IN (
  SELECT id FROM duplicates_to_remove WHERE rn > 1
);

-- Add the unique constraint that was commented out during initial migration
CREATE UNIQUE INDEX IF NOT EXISTS idx_service_areas_unique_postal 
ON service_areas(business_id, country_code, postal_code) 
WHERE is_active = TRUE AND postal_code IS NOT NULL;

-- Add some additional useful indexes for performance
CREATE INDEX IF NOT EXISTS idx_service_areas_business_postal ON service_areas(business_id, postal_code) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_service_areas_country_postal ON service_areas(country_code, postal_code) WHERE is_active = TRUE;
