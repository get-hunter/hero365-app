-- =====================================
-- ADD PO_NUMBER AND ISSUE_DATE FIELDS TO ESTIMATES
-- =====================================

-- Add po_number field to estimates table
ALTER TABLE "public"."estimates" 
ADD COLUMN "po_number" VARCHAR(100) DEFAULT NULL;

-- Add issue_date field to estimates table
ALTER TABLE "public"."estimates" 
ADD COLUMN "issue_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add comments to document the fields
COMMENT ON COLUMN "public"."estimates"."po_number" IS 'Purchase Order number from the client';
COMMENT ON COLUMN "public"."estimates"."issue_date" IS 'Date when the estimate was issued';

-- Create index for po_number searches
CREATE INDEX "idx_estimates_po_number" ON "public"."estimates" ("business_id", "po_number") WHERE "po_number" IS NOT NULL;

-- Create index for issue_date
CREATE INDEX "idx_estimates_issue_date" ON "public"."estimates" ("issue_date");

-- Update full-text search index to include po_number
DROP INDEX IF EXISTS "idx_estimates_search";
CREATE INDEX "idx_estimates_search" ON "public"."estimates" USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '') || ' ' || COALESCE(po_number, '')));

-- Update existing estimates to have issue_date = created_date if issue_date is NULL
UPDATE "public"."estimates" 
SET "issue_date" = "created_date" 
WHERE "issue_date" IS NULL; 