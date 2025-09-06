-- Remove redundant seo_slug column from featured_projects table
-- This migration consolidates to using only the 'slug' column for URL routing and API responses

-- Remove the seo_slug column from featured_projects table
ALTER TABLE featured_projects DROP COLUMN IF EXISTS seo_slug;

-- Drop the index on seo_slug if it exists
DROP INDEX IF EXISTS idx_featured_projects_seo_slug;
