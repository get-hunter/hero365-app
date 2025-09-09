-- Drop redundant category_slug from business_services (we use category_id FK)
BEGIN;

-- Drop FK if it exists
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE table_name = 'business_services' 
      AND constraint_name = 'business_services_category_slug_fkey'
  ) THEN
    ALTER TABLE business_services DROP CONSTRAINT business_services_category_slug_fkey;
  END IF;
END$$;

-- Drop index if it exists
DROP INDEX IF EXISTS idx_business_services_category_slug;

-- Drop the column
ALTER TABLE business_services DROP COLUMN IF EXISTS category_slug;

COMMIT;


