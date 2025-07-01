-- Add Client Fields to Estimates Table
-- This migration adds denormalized client fields to estimates for performance and historical accuracy
-- Date: 2025-02-03
-- Version: Add Client Fields for Hybrid Approach

-- =====================================
-- ADD CLIENT FIELDS TO ESTIMATES TABLE
-- =====================================

-- Add client fields to estimates table
ALTER TABLE "public"."estimates" 
ADD COLUMN "client_name" VARCHAR(300),
ADD COLUMN "client_email" VARCHAR(255),
ADD COLUMN "client_phone" VARCHAR(50),
ADD COLUMN "client_address" JSONB DEFAULT '{}';

-- Add client fields to invoices table (for consistency)
ALTER TABLE "public"."invoices" 
ADD COLUMN "client_name" VARCHAR(300),
ADD COLUMN "client_email" VARCHAR(255), 
ADD COLUMN "client_phone" VARCHAR(50),
ADD COLUMN "client_address" JSONB DEFAULT '{}';

-- =====================================
-- UPDATE EXISTING DATA
-- =====================================

-- Populate client fields for existing estimates from contacts table
UPDATE "public"."estimates" 
SET 
    "client_name" = COALESCE(c.first_name || ' ' || c.last_name, c.company_name, 'Unknown Client'),
    "client_email" = c.email,
    "client_phone" = COALESCE(c.phone, c.mobile_phone),
    "client_address" = COALESCE(c.address, '{}')
FROM "public"."contacts" c
WHERE "estimates"."contact_id" = c.id;

-- Populate client fields for existing invoices from contacts table  
UPDATE "public"."invoices"
SET 
    "client_name" = COALESCE(c.first_name || ' ' || c.last_name, c.company_name, 'Unknown Client'),
    "client_email" = c.email,
    "client_phone" = COALESCE(c.phone, c.mobile_phone),
    "client_address" = COALESCE(c.address, '{}')
FROM "public"."contacts" c
WHERE "invoices"."contact_id" = c.id;

-- =====================================
-- ADD CONSTRAINTS
-- =====================================

-- Make client_name required for non-draft estimates
ALTER TABLE "public"."estimates" 
ADD CONSTRAINT "estimates_client_name_required" 
CHECK (status = 'draft' OR client_name IS NOT NULL);

-- Make client_name required for invoices
ALTER TABLE "public"."invoices" 
ADD CONSTRAINT "invoices_client_name_required" 
CHECK (client_name IS NOT NULL);

-- =====================================
-- ADD INDEXES FOR PERFORMANCE
-- =====================================

-- Add indexes for client search and filtering
CREATE INDEX "idx_estimates_client_name" ON "public"."estimates" USING GIN (to_tsvector('english', client_name));
CREATE INDEX "idx_estimates_client_email" ON "public"."estimates" (client_email);
CREATE INDEX "idx_estimates_business_client" ON "public"."estimates" (business_id, client_name);

CREATE INDEX "idx_invoices_client_name" ON "public"."invoices" USING GIN (to_tsvector('english', client_name));
CREATE INDEX "idx_invoices_client_email" ON "public"."invoices" (client_email);
CREATE INDEX "idx_invoices_business_client" ON "public"."invoices" (business_id, client_name);

-- =====================================
-- ADD COMMENTS FOR DOCUMENTATION
-- =====================================

COMMENT ON COLUMN "public"."estimates"."client_name" IS 'Denormalized client name for performance and historical accuracy';
COMMENT ON COLUMN "public"."estimates"."client_email" IS 'Denormalized client email for sending estimates';
COMMENT ON COLUMN "public"."estimates"."client_phone" IS 'Denormalized client phone for contact purposes';
COMMENT ON COLUMN "public"."estimates"."client_address" IS 'Denormalized client address as JSONB for estimate display';

COMMENT ON COLUMN "public"."invoices"."client_name" IS 'Denormalized client name for performance and historical accuracy';
COMMENT ON COLUMN "public"."invoices"."client_email" IS 'Denormalized client email for sending invoices';
COMMENT ON COLUMN "public"."invoices"."client_phone" IS 'Denormalized client phone for contact purposes';
COMMENT ON COLUMN "public"."invoices"."client_address" IS 'Denormalized client address as JSONB for invoice display'; 