-- Add project_number column to projects table
-- This migration adds the missing project_number field that the application code expects
-- Date: 2025-02-01
-- Version: Add missing project_number column

-- Add project_number column to projects table
ALTER TABLE "public"."projects" 
ADD COLUMN IF NOT EXISTS "project_number" VARCHAR(50);

-- Create a unique constraint for project_number within each business
ALTER TABLE "public"."projects" 
ADD CONSTRAINT "projects_business_project_number_unique" 
UNIQUE ("business_id", "project_number");

-- Create an index for project_number lookups
CREATE INDEX IF NOT EXISTS "idx_projects_project_number" 
ON "public"."projects" ("project_number");

-- Update existing projects with auto-generated project numbers
-- Generate project numbers in format PROJ-YYYY-001, PROJ-YYYY-002, etc.
DO $$
DECLARE
    project_record RECORD;
    project_counter INTEGER;
    current_year TEXT;
    new_project_number VARCHAR(50);
BEGIN
    current_year := EXTRACT(YEAR FROM NOW())::TEXT;
    project_counter := 1;
    
    -- Loop through existing projects ordered by created_date
    FOR project_record IN 
        SELECT id, business_id, created_date 
        FROM "public"."projects" 
        WHERE project_number IS NULL
        ORDER BY business_id, created_date
    LOOP
        -- Reset counter for each business
        IF project_counter = 1 OR 
           (SELECT business_id FROM "public"."projects" WHERE id = project_record.id) != 
           (SELECT business_id FROM "public"."projects" 
            WHERE id = (SELECT id FROM "public"."projects" 
                       WHERE created_date < project_record.created_date 
                       AND project_number IS NOT NULL
                       ORDER BY created_date DESC LIMIT 1)) THEN
            -- Get the next number for this business
            SELECT COALESCE(MAX(CAST(SUBSTRING(project_number FROM 'PROJ-\d{4}-(\d+)') AS INTEGER)), 0) + 1
            INTO project_counter
            FROM "public"."projects" 
            WHERE business_id = project_record.business_id 
            AND project_number IS NOT NULL;
            
            IF project_counter IS NULL THEN
                project_counter := 1;
            END IF;
        END IF;
        
        -- Generate the project number
        new_project_number := 'PROJ-' || current_year || '-' || LPAD(project_counter::TEXT, 3, '0');
        
        -- Update the project with the generated number
        UPDATE "public"."projects" 
        SET project_number = new_project_number
        WHERE id = project_record.id;
        
        project_counter := project_counter + 1;
    END LOOP;
END $$;

-- Make project_number NOT NULL after populating existing records
ALTER TABLE "public"."projects" 
ALTER COLUMN "project_number" SET NOT NULL;

-- ===============================================
-- PART 2: Unified Address System for Projects
-- ===============================================

-- Add JSONB address column for structured address storage
ALTER TABLE "public"."projects" 
ADD COLUMN IF NOT EXISTS "address" JSONB DEFAULT '{}';

-- Migrate existing client_address (TEXT) to structured address (JSONB)
-- This will attempt to parse simple address strings into structured format
UPDATE "public"."projects" 
SET address = jsonb_build_object(
    'street_address', COALESCE(client_address, ''),
    'city', '',
    'state', '',
    'postal_code', '',
    'country', 'US'
)
WHERE address = '{}' OR address IS NULL;

-- Only keep address data if client_address has meaningful content
UPDATE "public"."projects" 
SET address = '{}'
WHERE 
    (client_address IS NULL OR client_address = '' OR TRIM(client_address) = '');

-- Create GIN index for efficient JSONB queries on project addresses
CREATE INDEX IF NOT EXISTS "idx_projects_address" 
ON "public"."projects" USING GIN ("address");

-- Add comment for documentation
COMMENT ON COLUMN "public"."projects"."address" IS 'JSONB address object: {street_address, city, state, postal_code, country, latitude?, longitude?, access_notes?, place_id?, formatted_address?, address_type?}';

-- Drop the old client_address column after migration
-- Note: This removes the old TEXT column in favor of the structured JSONB address
ALTER TABLE "public"."projects" 
DROP COLUMN IF EXISTS "client_address";

-- Add comment for documentation
COMMENT ON COLUMN "public"."projects"."project_number" IS 'Unique project number within each business, auto-generated if not provided'; 