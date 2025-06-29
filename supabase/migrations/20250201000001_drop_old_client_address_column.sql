-- Drop old client_address column after unified address migration
-- This migration removes the legacy client_address TEXT column
-- Date: 2025-02-01
-- Version: Remove legacy client_address column

-- Drop the old client_address column after migration to unified address system
-- The data has been migrated to the new 'address' JSONB column
ALTER TABLE "public"."projects" 
DROP COLUMN IF EXISTS "client_address";

-- Add comment for confirmation
COMMENT ON TABLE "public"."projects" IS 'Projects table updated to use unified address system (address JSONB column)'; 