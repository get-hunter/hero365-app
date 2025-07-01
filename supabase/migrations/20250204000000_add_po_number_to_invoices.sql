-- =====================================
-- ADD PO_NUMBER FIELD TO INVOICES
-- =====================================

-- Add po_number field to invoices table
ALTER TABLE "public"."invoices" 
ADD COLUMN "po_number" VARCHAR(100) DEFAULT NULL;

-- Add comment to document the field
COMMENT ON COLUMN "public"."invoices"."po_number" IS 'Purchase Order number from the client';

-- Create index for po_number searches
CREATE INDEX "idx_invoices_po_number" ON "public"."invoices" ("business_id", "po_number") WHERE "po_number" IS NOT NULL;

-- Update full-text search index to include po_number
DROP INDEX IF EXISTS "idx_invoices_search";
CREATE INDEX "idx_invoices_search" ON "public"."invoices" USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '') || ' ' || invoice_number || ' ' || COALESCE(po_number, ''))); 