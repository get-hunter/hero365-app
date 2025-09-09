-- Rename zip_codes to postal_codes for international support

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'service_areas' AND column_name = 'zip_codes'
  ) THEN
    ALTER TABLE service_areas RENAME COLUMN zip_codes TO postal_codes;
  END IF;
END $$;


