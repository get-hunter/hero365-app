-- Normalize contact address fields for production
-- Drop JSON address field and use individual fields for better query performance

-- Add the street_address field if it doesn't exist
ALTER TABLE "public"."contacts" 
ADD COLUMN IF NOT EXISTS "street_address" VARCHAR(200);

-- Drop the JSON address field since we're using individual fields
ALTER TABLE "public"."contacts" 
DROP COLUMN IF EXISTS "address";

-- Add indexes for better query performance on location fields
CREATE INDEX IF NOT EXISTS "idx_contacts_street_address" ON "public"."contacts"("street_address");
CREATE INDEX IF NOT EXISTS "idx_contacts_city" ON "public"."contacts"("city");
CREATE INDEX IF NOT EXISTS "idx_contacts_state" ON "public"."contacts"("state");
CREATE INDEX IF NOT EXISTS "idx_contacts_country" ON "public"."contacts"("country");
CREATE INDEX IF NOT EXISTS "idx_contacts_postal_code" ON "public"."contacts"("postal_code");

-- Add comments for documentation
COMMENT ON COLUMN "public"."contacts"."street_address" IS 'Street address line (e.g., 123 Main St, Apt 4B)';
COMMENT ON COLUMN "public"."contacts"."city" IS 'City name';
COMMENT ON COLUMN "public"."contacts"."state" IS 'State, province, or region';
COMMENT ON COLUMN "public"."contacts"."postal_code" IS 'Postal code, ZIP code, or equivalent';
COMMENT ON COLUMN "public"."contacts"."country" IS 'Country name or ISO country code'; 