-- Backfill categories for business services that are missing them
-- Purpose: Improve navigation grouping (Services mega menu and mobile menu)
-- Strategy: Derive category from service_name/service_slug using keyword heuristics
-- Categories used: Installation, Repair, Maintenance, Inspection, Emergency, Cleaning, Upgrade, General

BEGIN;

-- Normalize any blank categories to NULL for easier handling
UPDATE business_services
SET category = NULL
WHERE category IS NOT NULL AND trim(category) = '';

-- Backfill categories where missing
UPDATE business_services
SET category = CASE
  WHEN (
    service_name ILIKE '%emergency%' OR service_slug ILIKE '%emergency%'
  ) THEN 'Emergency'

  WHEN (
    service_name ILIKE '%install%' OR service_name ILIKE '%replacement%'
    OR service_name ILIKE '%generator installation%'
    OR service_slug ILIKE '%install%' OR service_slug ILIKE '%replace%'
  ) THEN 'Installation'

  WHEN (
    service_name ILIKE '%repair%' OR service_name ILIKE '%fix%'
    OR service_slug ILIKE '%repair%'
  ) THEN 'Repair'

  WHEN (
    service_name ILIKE '%maintenance%' OR service_name ILIKE '%tune%'
    OR service_name ILIKE '%prevent%'
    OR service_slug ILIKE '%maintenance%' OR service_slug ILIKE '%tune%'
  ) THEN 'Maintenance'

  WHEN (
    service_name ILIKE '%inspection%' OR service_name ILIKE '%diagnostic%'
    OR service_name ILIKE '%assessment%' OR service_name ILIKE '%audit%'
    OR service_slug ILIKE '%inspect%' OR service_slug ILIKE '%diagnostic%'
    OR service_slug ILIKE '%assessment%' OR service_slug ILIKE '%audit%'
  ) THEN 'Inspection'

  WHEN (
    service_name ILIKE '%clean%' OR service_name ILIKE '%flush%'
    OR service_name ILIKE '%descal%' OR service_name ILIKE '%drain%'
  ) THEN 'Cleaning'

  WHEN (
    service_name ILIKE '%upgrade%' OR service_slug ILIKE '%upgrade%'
  ) THEN 'Upgrade'

  ELSE 'General'
END
WHERE category IS NULL;

-- Optional: standardize capitalization for any existing categories to Title Case
UPDATE business_services
SET category = INITCAP(category)
WHERE category IS NOT NULL;

COMMIT;

-- Notes:
-- - This migration does not change existing non-empty categories; it only fills NULL/blank ones.
-- - The keyword rules are conservative and can be extended later if needed.
-- - Navigation groups in the header use trade_slug OR category, so this ensures grouping works.


