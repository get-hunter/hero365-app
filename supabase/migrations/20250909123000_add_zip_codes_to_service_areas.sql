-- Add zip_codes array to service_areas for postal-code based coverage

ALTER TABLE service_areas
  ADD COLUMN IF NOT EXISTS zip_codes text[];

-- Optional: normalize empty arrays to NULL (no-op if already NULL)
UPDATE service_areas SET zip_codes = NULL WHERE zip_codes IS NOT NULL AND array_length(zip_codes, 1) IS NULL;


