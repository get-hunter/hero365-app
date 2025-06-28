-- Unify Address Storage with JSONB
-- Standardizes address storage across all entities to use JSONB for consistency, 
-- flexibility, and support for geocoding/access information

-- ===============================================
-- PART 1: Migrate Contacts back to JSONB address
-- ===============================================

-- Add the JSONB address column to contacts
ALTER TABLE "public"."contacts" 
ADD COLUMN IF NOT EXISTS "address" JSONB DEFAULT '{}';

-- Migrate existing individual address fields to JSONB
UPDATE "public"."contacts" 
SET address = jsonb_build_object(
    'street_address', COALESCE(street_address, ''),
    'city', COALESCE(city, ''),
    'state', COALESCE(state, ''),
    'postal_code', COALESCE(postal_code, ''),
    'country', COALESCE(country, 'US')
)
WHERE address = '{}' OR address IS NULL;

-- Only keep address data if at least one field has meaningful content
UPDATE "public"."contacts" 
SET address = '{}'
WHERE 
    (address->>'street_address' = '' OR address->>'street_address' IS NULL) AND
    (address->>'city' = '' OR address->>'city' IS NULL) AND
    (address->>'state' = '' OR address->>'state' IS NULL) AND
    (address->>'postal_code' = '' OR address->>'postal_code' IS NULL);

-- Drop the individual address columns now that data is migrated
ALTER TABLE "public"."contacts" 
DROP COLUMN IF EXISTS "street_address",
DROP COLUMN IF EXISTS "city",
DROP COLUMN IF EXISTS "state", 
DROP COLUMN IF EXISTS "postal_code",
DROP COLUMN IF EXISTS "country";

-- Add GIN index for efficient JSONB queries on contacts
CREATE INDEX IF NOT EXISTS "idx_contacts_address" ON "public"."contacts" USING GIN ("address");

-- ===============================================
-- PART 2: Ensure Jobs have proper JSONB structure
-- ===============================================

-- Ensure all job addresses have the complete structure
UPDATE "public"."jobs" 
SET job_address = jsonb_build_object(
    'street_address', COALESCE(job_address->>'street_address', ''),
    'city', COALESCE(job_address->>'city', ''),
    'state', COALESCE(job_address->>'state', ''),
    'postal_code', COALESCE(job_address->>'postal_code', ''),
    'country', COALESCE(job_address->>'country', 'US'),
    'latitude', (job_address->>'latitude')::float,
    'longitude', (job_address->>'longitude')::float,
    'access_notes', job_address->>'access_notes'
)
WHERE job_address IS NOT NULL AND job_address != '{}';

-- ===============================================
-- PART 3: Add any other entities that need addresses
-- ===============================================

-- If we need to add addresses to other entities in the future, 
-- this migration establishes the pattern:
-- ALTER TABLE "public"."entity_name" 
-- ADD COLUMN IF NOT EXISTS "address" JSONB DEFAULT '{}';
-- CREATE INDEX IF NOT EXISTS "idx_entity_name_address" ON "public"."entity_name" USING GIN ("address");

-- ===============================================
-- PART 4: Update comments for documentation
-- ===============================================

COMMENT ON COLUMN "public"."contacts"."address" IS 'JSONB address object: {street_address, city, state, postal_code, country, latitude?, longitude?, access_notes?, place_id?, formatted_address?, address_type?}';
COMMENT ON COLUMN "public"."jobs"."job_address" IS 'JSONB address object: {street_address, city, state, postal_code, country, latitude?, longitude?, access_notes?, place_id?, formatted_address?, address_type?}';

-- Add constraints to ensure address data integrity
-- Contacts can have empty addresses, jobs require addresses
ALTER TABLE "public"."jobs" 
ADD CONSTRAINT "jobs_address_required" 
CHECK (job_address IS NOT NULL AND job_address != '{}');

-- ===============================================
-- PART 5: Clean up old indexes
-- ===============================================

-- Remove old individual field indexes from contacts migration
DROP INDEX IF EXISTS "idx_contacts_street_address";
DROP INDEX IF EXISTS "idx_contacts_city";
DROP INDEX IF EXISTS "idx_contacts_state";
DROP INDEX IF EXISTS "idx_contacts_country";
DROP INDEX IF EXISTS "idx_contacts_postal_code"; 