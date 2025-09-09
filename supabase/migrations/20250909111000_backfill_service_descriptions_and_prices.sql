-- Backfill service descriptions and pricing for commonly used services
-- Safe to re-run: uses COALESCE and only fills missing values

-- 1) Normalize empty strings to NULL
UPDATE business_services
SET description = NULL
WHERE description IS NOT NULL AND btrim(description) = '';

-- 2) Backfill per canonical_slug when values are missing
-- HVAC
UPDATE business_services SET
  description = COALESCE(description, 'Professional AC installation with load sizing, quality equipment, permits, and warranty.'),
  price_type = COALESCE(price_type, 'range'),
  price_min = COALESCE(price_min, 3500),
  price_max = COALESCE(price_max, 12000),
  price_unit = COALESCE(price_unit, 'system')
WHERE canonical_slug = 'ac-installation';

UPDATE business_services SET
  description = COALESCE(description, 'Fast diagnostics and repair for cooling issues, refrigerant leaks, and electrical faults.'),
  price_type = COALESCE(price_type, 'range'),
  price_min = COALESCE(price_min, 150),
  price_max = COALESCE(price_max, 1200),
  price_unit = COALESCE(price_unit, 'job')
WHERE canonical_slug = 'ac-repair';

UPDATE business_services SET
  description = COALESCE(description, 'Trusted furnace repair for ignition, blower, and heat exchanger issues with safety checks.'),
  price_type = COALESCE(price_type, 'range'),
  price_min = COALESCE(price_min, 200),
  price_max = COALESCE(price_max, 1500),
  price_unit = COALESCE(price_unit, 'job')
WHERE canonical_slug = 'furnace-repair';

UPDATE business_services SET
  description = COALESCE(description, 'Seasonal HVAC tune-ups including coil cleaning, filter change, and performance testing.'),
  price_type = COALESCE(price_type, 'fixed'),
  price_min = COALESCE(price_min, 129),
  price_unit = COALESCE(price_unit, 'visit')
WHERE canonical_slug = 'hvac-maintenance';

-- Plumbing
UPDATE business_services SET
  description = COALESCE(description, 'Clearing clogs and slow drains using auger or hydro-jet, with camera inspection on request.'),
  price_type = COALESCE(price_type, 'range'),
  price_min = COALESCE(price_min, 99),
  price_max = COALESCE(price_max, 350),
  price_unit = COALESCE(price_unit, 'job')
WHERE canonical_slug = 'drain-cleaning';

UPDATE business_services SET
  description = COALESCE(description, 'Leak fixes and pipe section replacements in copper, PEX, or PVC with code-compliant repairs.'),
  price_type = COALESCE(price_type, 'range'),
  price_min = COALESCE(price_min, 150),
  price_max = COALESCE(price_max, 1200),
  price_unit = COALESCE(price_unit, 'job')
WHERE canonical_slug = 'pipe-repair';

UPDATE business_services SET
  description = COALESCE(description, 'Diagnosis and service of gas, electric, or tankless water heaters including parts and labor.'),
  price_type = COALESCE(price_type, 'range'),
  price_min = COALESCE(price_min, 200),
  price_max = COALESCE(price_max, 1200),
  price_unit = COALESCE(price_unit, 'job')
WHERE canonical_slug = 'water-heater-service';

-- Electrical
UPDATE business_services SET
  description = COALESCE(description, 'Troubleshooting and repair of outlets, switches, lighting, and circuits by licensed electricians.'),
  price_type = COALESCE(price_type, 'range'),
  price_min = COALESCE(price_min, 120),
  price_max = COALESCE(price_max, 900),
  price_unit = COALESCE(price_unit, 'job')
WHERE canonical_slug = 'electrical-repair';

UPDATE business_services SET
  description = COALESCE(description, 'Upgrade to 200A+ panels with new breakers, grounding, labeling, and permit management.'),
  price_type = COALESCE(price_type, 'range'),
  price_min = COALESCE(price_min, 1500),
  price_max = COALESCE(price_max, 3500),
  price_unit = COALESCE(price_unit, 'job')
WHERE canonical_slug = 'panel-upgrade';

-- 3) Default fallbacks where description is still NULL
UPDATE business_services
SET description = 'Professional ' || service_name || ' services by certified technicians.'
WHERE description IS NULL;

-- 4) Ensure price_unit defaults for non-hourly priced items
UPDATE business_services
SET price_unit = 'job'
WHERE price_unit IS NULL AND price_type IN ('range', 'fixed');


