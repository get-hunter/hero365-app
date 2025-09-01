-- Add Document Type to Estimates Table
-- This migration adds the document_type field to distinguish between estimates and quotes
-- Date: 2025-02-02
-- Version: Document Type Enhancement

-- Add document_type column to estimates table
ALTER TABLE "public"."estimates" 
ADD COLUMN "document_type" VARCHAR(10) NOT NULL DEFAULT 'estimate' 
CHECK (document_type IN ('estimate', 'quote'));

-- Create index for document_type for better query performance
CREATE INDEX "idx_estimates_document_type" ON "public"."estimates" ("document_type");

-- Create composite index for business_id and document_type
CREATE INDEX "idx_estimates_business_document_type" ON "public"."estimates" ("business_id", "document_type");

-- Update the estimate number generation function to support different prefixes based on document type
CREATE OR REPLACE FUNCTION get_next_document_number(business_uuid UUID, doc_type TEXT DEFAULT 'estimate')
RETURNS TEXT AS $$
DECLARE
    next_number INTEGER;
    formatted_number TEXT;
    prefix TEXT;
BEGIN
    -- Set prefix based on document type
    prefix := CASE 
        WHEN LOWER(doc_type) = 'quote' THEN 'QUO'
        ELSE 'EST'
    END;
    
    -- Get the next number by finding the highest existing number for this document type
    SELECT COALESCE(MAX(CAST(RIGHT(estimate_number, -LENGTH(prefix || '-')) AS INTEGER)), 0) + 1
    INTO next_number
    FROM public.estimates
    WHERE business_id = business_uuid
    AND document_type = doc_type
    AND estimate_number ~ ('^' || prefix || '-\d+$');
    
    -- Format the number with leading zeros
    formatted_number := prefix || '-' || LPAD(next_number::TEXT, 6, '0');
    
    RETURN formatted_number;
END;
$$ LANGUAGE plpgsql;

-- Add comment to the estimates table documenting the new field
COMMENT ON COLUMN "public"."estimates"."document_type" IS 'Type of document: estimate (preliminary pricing) or quote (firm offer)';

-- Migration completed successfully 