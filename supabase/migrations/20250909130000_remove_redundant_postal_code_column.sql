-- Remove redundant postal_code column, keep postal_codes array
-- This migration cleans up the service_areas table to avoid confusion
-- between postal_code (singular) and postal_codes (array)

-- Drop the redundant postal_code column
ALTER TABLE service_areas DROP COLUMN IF EXISTS postal_code;

-- Add comment to clarify the postal_codes column usage
COMMENT ON COLUMN service_areas.postal_codes IS 'Array of postal codes covered by this service area. Supports international postal code formats.';
