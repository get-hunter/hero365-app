-- =============================================
-- REMOVE REDUNDANT SERVICE AREAS COLUMN
-- =============================================
-- Remove the service_areas JSONB column from businesses table
-- since we have a dedicated service_areas table for proper normalization
-- Migration: 20250902160000_remove_redundant_service_areas_column.sql

-- First, let's check if there's any data in the service_areas column that needs to be migrated
-- to the service_areas table before dropping the column

-- Create a function to migrate any existing service_areas data from businesses to service_areas table
CREATE OR REPLACE FUNCTION migrate_business_service_areas()
RETURNS void AS $$
DECLARE
    business_record RECORD;
    service_area_text TEXT;
BEGIN
    -- Loop through businesses that have service_areas data
    FOR business_record IN 
        SELECT id, service_areas 
        FROM businesses 
        WHERE service_areas IS NOT NULL 
        AND jsonb_array_length(service_areas) > 0
    LOOP
        -- Extract each service area from the JSONB array
        FOR service_area_text IN 
            SELECT jsonb_array_elements_text(business_record.service_areas)
        LOOP
            -- Parse the service area text (assuming format like "Austin, TX" or "Austin")
            INSERT INTO service_areas (
                business_id,
                area_name,
                city,
                state,
                is_active,
                created_at,
                updated_at
            )
            VALUES (
                business_record.id,
                service_area_text,
                CASE 
                    WHEN position(',' in service_area_text) > 0 
                    THEN trim(split_part(service_area_text, ',', 1))
                    ELSE service_area_text
                END,
                CASE 
                    WHEN position(',' in service_area_text) > 0 
                    THEN trim(split_part(service_area_text, ',', 2))
                    ELSE 'TX' -- Default to TX if no state specified
                END,
                true,
                NOW(),
                NOW()
            )
            ON CONFLICT (business_id, postal_code, country_code) DO NOTHING; -- Skip if already exists
        END LOOP;
    END LOOP;
    
    RAISE NOTICE 'Migration of service_areas data completed';
END;
$$ LANGUAGE plpgsql;

-- Execute the migration function
SELECT migrate_business_service_areas();

-- Drop the migration function as it's no longer needed
DROP FUNCTION migrate_business_service_areas();

-- Now drop the redundant service_areas column from businesses table
ALTER TABLE businesses DROP COLUMN IF EXISTS service_areas;

-- Drop the associated index if it exists
DROP INDEX IF EXISTS idx_businesses_service_areas;

-- Add a comment to document this change
COMMENT ON TABLE service_areas IS 'Dedicated table for business service areas. Replaces the former service_areas JSONB column in businesses table for better normalization and querying.';

-- Verify the column has been removed
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'businesses' 
        AND column_name = 'service_areas'
    ) THEN
        RAISE NOTICE 'SUCCESS: service_areas column has been removed from businesses table';
    ELSE
        RAISE EXCEPTION 'ERROR: service_areas column still exists in businesses table';
    END IF;
END $$;
