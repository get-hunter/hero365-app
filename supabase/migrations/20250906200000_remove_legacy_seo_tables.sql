-- Remove Legacy SEO Tables Migration
-- This migration removes legacy SEO tables that have been replaced by the new dynamic architecture
-- Note: Using IF EXISTS to safely handle cases where tables don't exist yet

-- Drop legacy SEO tables that are no longer needed
-- These have been replaced by the unified content orchestrator and dynamic data fetching

-- 1. Drop generated_seo_pages (replaced by dynamic content generation)
DROP TABLE IF EXISTS generated_seo_pages CASCADE;

-- 2. Drop service_page_contents (replaced by unified content orchestrator)  
DROP TABLE IF EXISTS service_page_contents CASCADE;

-- 3. Drop service_location_pages (replaced by dynamic location-aware routing)
DROP TABLE IF EXISTS service_location_pages CASCADE;

-- 4. Drop service_seo_config (replaced by dynamic configuration)
DROP TABLE IF EXISTS service_seo_config CASCADE;

-- 5. Drop location_pages (replaced by dynamic location data)
DROP TABLE IF EXISTS location_pages CASCADE;

-- 6. Drop seo_templates (replaced by unified content templates)
DROP TABLE IF EXISTS seo_templates CASCADE;

-- Drop related enums that are no longer needed
DROP TYPE IF EXISTS content_source_enum CASCADE;
DROP TYPE IF EXISTS page_status_enum CASCADE;

-- Add comment explaining the migration (only if schema exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'public') THEN
        COMMENT ON SCHEMA public IS 'Legacy SEO tables removed - system now uses dynamic content generation and unified orchestrator';
    END IF;
END $$;
