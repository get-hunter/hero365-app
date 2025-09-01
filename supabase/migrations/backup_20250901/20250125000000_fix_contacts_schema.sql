-- Fix contacts table schema to match entity model
-- Add missing fields and fix field types

-- Add missing columns
ALTER TABLE "public"."contacts" 
ADD COLUMN "custom_fields" JSONB DEFAULT '{}',
ADD COLUMN "estimated_value" NUMERIC(10,2),
ADD COLUMN "currency" VARCHAR(3) DEFAULT 'USD',
ADD COLUMN "job_title" VARCHAR(255),
ADD COLUMN "website" VARCHAR(500);

-- Change tags from TEXT[] to JSONB to match entity model
-- First, create a temporary column
ALTER TABLE "public"."contacts" ADD COLUMN "tags_new" JSONB DEFAULT '[]';

-- Copy data from old tags array to new JSONB column
UPDATE "public"."contacts" 
SET "tags_new" = CASE 
    WHEN "tags" IS NULL THEN '[]'::jsonb
    ELSE array_to_json("tags")::jsonb
END;

-- Drop the old column and rename the new one
ALTER TABLE "public"."contacts" DROP COLUMN "tags";
ALTER TABLE "public"."contacts" RENAME COLUMN "tags_new" TO "tags";

-- Add comments for documentation
COMMENT ON COLUMN "public"."contacts"."custom_fields" IS 'JSON object for storing custom contact fields';
COMMENT ON COLUMN "public"."contacts"."estimated_value" IS 'Estimated value of the contact in the specified currency';
COMMENT ON COLUMN "public"."contacts"."currency" IS 'Currency code for estimated_value (ISO 4217)';
COMMENT ON COLUMN "public"."contacts"."job_title" IS 'Job title or position of the contact';
COMMENT ON COLUMN "public"."contacts"."website" IS 'Contact or company website URL';
COMMENT ON COLUMN "public"."contacts"."tags" IS 'JSON array of tags for categorizing contacts'; 