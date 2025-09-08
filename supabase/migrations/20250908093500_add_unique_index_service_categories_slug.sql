-- Ensure service_categories(slug) has a unique constraint to support FK from business_services.category_slug
BEGIN;

-- Add unique constraint across (business_id, slug) if not already present
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE table_name = 'service_categories' AND constraint_name = 'service_categories_business_slug_key'
  ) THEN
    ALTER TABLE service_categories ADD CONSTRAINT service_categories_business_slug_key UNIQUE (business_id, slug);
  END IF;
END$$;

COMMIT;

