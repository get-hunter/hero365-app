-- Add normalized category reference to service_categories
BEGIN;

-- 1) Add column if not exists
ALTER TABLE business_services
ADD COLUMN IF NOT EXISTS category_slug TEXT,
ADD COLUMN IF NOT EXISTS category_id UUID;

-- 2) Ensure a slugify helper (inline expression used below)

-- 3) Insert missing service_categories per business for distinct text categories
--    We create a category row for any text category not present yet for the business.
WITH distinct_cats AS (
  SELECT DISTINCT bs.business_id, trim(bs.category) AS category
  FROM business_services bs
  WHERE bs.category IS NOT NULL AND trim(bs.category) <> ''
)
INSERT INTO service_categories (id, business_id, name, slug, description, display_order, is_active)
SELECT gen_random_uuid(), dc.business_id,
       INITCAP(dc.category) AS name,
       lower(regexp_replace(regexp_replace(dc.category, '[^a-zA-Z0-9\s-]', '', 'g'), '\s+', '-', 'g')) AS slug,
       NULL, 0, TRUE
FROM distinct_cats dc
LEFT JOIN service_categories sc
  ON sc.business_id = dc.business_id
 AND sc.slug = lower(regexp_replace(regexp_replace(dc.category, '[^a-zA-Z0-9\s-]', '', 'g'), '\s+', '-', 'g'))
WHERE sc.id IS NULL;

-- 4) Backfill category_slug and category_id from existing matches by slug or name
UPDATE business_services bs
SET category_slug = sc.slug,
    category_id = sc.id
FROM service_categories sc
WHERE sc.business_id = bs.business_id
  AND (
        sc.slug = lower(regexp_replace(regexp_replace(coalesce(bs.category, ''), '[^a-zA-Z0-9\s-]', '', 'g'), '\s+', '-', 'g'))
     OR lower(sc.name) = lower(trim(coalesce(bs.category, '')))
  )
  AND (bs.category_id IS NULL);

-- 5) Add FK and indexes
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'business_services_category_id_fkey' 
      AND table_name = 'business_services'
  ) THEN
    ALTER TABLE business_services
    ADD CONSTRAINT business_services_category_id_fkey
    FOREIGN KEY (category_id) REFERENCES service_categories(id)
    ON UPDATE CASCADE ON DELETE SET NULL;
  END IF;
END$$;

CREATE INDEX IF NOT EXISTS idx_business_services_category_slug
ON business_services (category_slug);

CREATE INDEX IF NOT EXISTS idx_business_services_category_id
ON business_services (category_id);

COMMIT;

-- Down migration (manual): remove FK/column if necessary.

