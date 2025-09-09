-- Add image fields to business_services and backfill sensible placeholders

-- 1) Add columns if not exist
ALTER TABLE business_services
  ADD COLUMN IF NOT EXISTS image_url text,
  ADD COLUMN IF NOT EXISTS image_alt text,
  ADD COLUMN IF NOT EXISTS image_gallery jsonb NOT NULL DEFAULT '[]'::jsonb;

-- 2) Normalize empty strings to NULL
UPDATE business_services SET image_url = NULL WHERE image_url IS NOT NULL AND btrim(image_url) = '';
UPDATE business_services SET image_alt = NULL WHERE image_alt IS NOT NULL AND btrim(image_alt) = '';

-- 3) Backfill placeholders for known services (dev-friendly)
UPDATE business_services SET
  image_url = COALESCE(image_url, 'https://placehold.co/800x500?text=AC+Installation'),
  image_alt = COALESCE(image_alt, 'AC Installation')
WHERE canonical_slug = 'ac-installation';

UPDATE business_services SET
  image_url = COALESCE(image_url, 'https://placehold.co/800x500?text=AC+Repair'),
  image_alt = COALESCE(image_alt, 'AC Repair')
WHERE canonical_slug = 'ac-repair';

UPDATE business_services SET
  image_url = COALESCE(image_url, 'https://placehold.co/800x500?text=Furnace+Repair'),
  image_alt = COALESCE(image_alt, 'Furnace Repair')
WHERE canonical_slug = 'furnace-repair';

UPDATE business_services SET
  image_url = COALESCE(image_url, 'https://placehold.co/800x500?text=HVAC+Maintenance'),
  image_alt = COALESCE(image_alt, 'HVAC Maintenance')
WHERE canonical_slug = 'hvac-maintenance';

UPDATE business_services SET
  image_url = COALESCE(image_url, 'https://placehold.co/800x500?text=Drain+Cleaning'),
  image_alt = COALESCE(image_alt, 'Drain Cleaning')
WHERE canonical_slug = 'drain-cleaning';

UPDATE business_services SET
  image_url = COALESCE(image_url, 'https://placehold.co/800x500?text=Pipe+Repair'),
  image_alt = COALESCE(image_alt, 'Pipe Repair')
WHERE canonical_slug = 'pipe-repair';

UPDATE business_services SET
  image_url = COALESCE(image_url, 'https://placehold.co/800x500?text=Water+Heater+Service'),
  image_alt = COALESCE(image_alt, 'Water Heater Service')
WHERE canonical_slug = 'water-heater-service';

UPDATE business_services SET
  image_url = COALESCE(image_url, 'https://placehold.co/800x500?text=Electrical+Repair'),
  image_alt = COALESCE(image_alt, 'Electrical Repair')
WHERE canonical_slug = 'electrical-repair';

UPDATE business_services SET
  image_url = COALESCE(image_url, 'https://placehold.co/800x500?text=Panel+Upgrade'),
  image_alt = COALESCE(image_alt, 'Panel Upgrade')
WHERE canonical_slug = 'panel-upgrade';


