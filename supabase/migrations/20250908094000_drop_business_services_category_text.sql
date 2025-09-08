-- Remove legacy free-text category column from business_services
-- We now use category_id (FK -> service_categories.id) and category_slug

BEGIN;

-- Safety: only drop after the FK-backed columns exist
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'business_services' AND column_name = 'category'
  ) THEN
    ALTER TABLE business_services DROP COLUMN category;
  END IF;
END$$;

COMMIT;


