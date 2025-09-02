-- Fix content_source_enum to include RAG_ENHANCED value
-- This migration adds the missing RAG_ENHANCED enum value

-- Add the new enum value to content_source_enum
ALTER TYPE content_source_enum ADD VALUE IF NOT EXISTS 'rag_enhanced';

-- Update the service_page_contents table comment to reflect new enum values
COMMENT ON COLUMN service_page_contents.content_source IS 'Source of content generation: template, llm, rag_enhanced, mixed, manual';
