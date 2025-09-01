-- Fix Permissions Schema to Match Application Code
-- This migration updates the permission system to use the new permission names that match the application code

-- Update the get_default_permissions_for_role function to use new permission names
CREATE OR REPLACE FUNCTION get_default_permissions_for_role(role_name text)
RETURNS jsonb AS $$
BEGIN
    RETURN CASE role_name
        WHEN 'owner' THEN '["*"]'::jsonb
        WHEN 'admin' THEN '[
            "view_contacts", "create_contacts", "edit_contacts", "delete_contacts",
            "view_jobs", "create_jobs", "edit_jobs", "delete_jobs",
            "view_projects", "create_projects", "edit_projects", "delete_projects",
            "view_invoices", "create_invoices", "edit_invoices", "delete_invoices",
            "view_estimates", "create_estimates", "edit_estimates", "delete_estimates",
            "view_business_settings", "invite_team_members", "edit_team_members",
            "view_reports", "edit_reports", "view_accounting", "edit_accounting"
        ]'::jsonb
        WHEN 'manager' THEN '[
            "view_contacts", "create_contacts", "edit_contacts",
            "view_jobs", "create_jobs", "edit_jobs",
            "view_projects", "create_projects", "edit_projects",
            "view_invoices", "create_invoices", "edit_invoices",
            "view_estimates", "create_estimates", "edit_estimates",
            "invite_team_members", "view_reports"
        ]'::jsonb
        WHEN 'employee' THEN '[
            "view_contacts", "create_contacts", "edit_contacts",
            "view_jobs", "create_jobs", "edit_jobs",
            "view_projects", "create_projects", "edit_projects",
            "view_invoices", "view_estimates"
        ]'::jsonb
        WHEN 'contractor' THEN '[
            "view_contacts", "view_jobs", "view_projects"
        ]'::jsonb
        WHEN 'viewer' THEN '[
            "view_contacts", "view_jobs", "view_projects"
        ]'::jsonb
        ELSE '[]'::jsonb
    END;
END;
$$ LANGUAGE plpgsql;

-- Update existing business memberships to use new permission names
UPDATE "public"."business_memberships" 
SET permissions = get_default_permissions_for_role(role)
WHERE permissions IS NOT NULL;

-- Update any specific permission mappings
UPDATE "public"."business_memberships" 
SET permissions = jsonb_set(
    jsonb_set(
        jsonb_set(
            jsonb_set(permissions, '{0}', '"view_jobs"'),
            '{1}', '"create_jobs"'
        ),
        '{2}', '"edit_jobs"'
    ),
    '{3}', '"delete_jobs"'
)
WHERE permissions @> '["manage_jobs"]'::jsonb;

-- Remove old permission names that are no longer used
UPDATE "public"."business_memberships" 
SET permissions = permissions - 'manage_jobs' - 'manage_contacts' - 'manage_activities'
WHERE permissions @> '["manage_jobs"]'::jsonb 
   OR permissions @> '["manage_contacts"]'::jsonb 
   OR permissions @> '["manage_activities"]'::jsonb;

-- Add helpful comment
COMMENT ON FUNCTION get_default_permissions_for_role(text) IS 'Returns default permissions for a business role using the new permission naming convention that matches the application code'; 