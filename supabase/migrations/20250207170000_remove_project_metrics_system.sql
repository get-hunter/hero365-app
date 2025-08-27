-- Remove project metrics system since we're using Tinybird for analytics
-- This removes the project_metrics table, functions, and triggers

-- Drop the trigger first
DROP TRIGGER IF EXISTS trigger_update_project_metrics ON featured_projects;

-- Drop the function
DROP FUNCTION IF EXISTS update_project_metrics(UUID);

-- Drop the project_metrics table
DROP TABLE IF EXISTS project_metrics;

-- Note: We keep the featured_projects table as it's still needed for the website showcase
