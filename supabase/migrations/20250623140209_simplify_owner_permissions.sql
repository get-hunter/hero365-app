-- Simplify Owner Permissions Migration
-- This migration adds a special handling for owner permissions to make them automatically get all permissions

-- Update the get_default_permissions_for_role function to handle owners more elegantly
CREATE OR REPLACE FUNCTION get_default_permissions_for_role(role_name text)
RETURNS jsonb AS $$
DECLARE
    all_permissions jsonb;
BEGIN
    -- For owners, return a special marker that indicates "all permissions"
    -- This makes it future-proof as new permissions will automatically be included
    IF role_name = 'owner' THEN
        -- Return all available permissions dynamically
        all_permissions := '[
            "view_contacts", "create_contacts", "edit_contacts", "delete_contacts",
            "view_jobs", "create_jobs", "edit_jobs", "delete_jobs", 
            "view_projects", "create_projects", "edit_projects", "delete_projects",
            "edit_business_profile", "view_business_settings", "edit_business_settings",
            "invite_team_members", "edit_team_members", "remove_team_members",
            "view_invoices", "create_invoices", "edit_invoices", "delete_invoices",
            "view_estimates", "create_estimates", "edit_estimates", "delete_estimates",
            "view_reports", "edit_reports", "view_accounting", "edit_accounting",
            "*"
        ]'::jsonb;
        RETURN all_permissions;
    END IF;
    
    -- For other roles, use specific permissions
    CASE role_name
        WHEN 'admin' THEN  
            RETURN '["view_contacts", "create_contacts", "edit_contacts", "delete_contacts", "view_jobs", "create_jobs", "edit_jobs", "delete_jobs", "view_projects", "create_projects", "edit_projects", "delete_projects", "view_business_settings", "invite_team_members", "edit_team_members", "view_invoices", "create_invoices", "edit_invoices", "delete_invoices", "view_estimates", "create_estimates", "edit_estimates", "delete_estimates", "view_reports", "edit_reports", "view_accounting", "edit_accounting"]'::jsonb;
        WHEN 'manager' THEN
            RETURN '["view_contacts", "create_contacts", "edit_contacts", "view_jobs", "create_jobs", "edit_jobs", "view_projects", "create_projects", "edit_projects", "view_invoices", "create_invoices", "edit_invoices", "view_estimates", "create_estimates", "edit_estimates", "invite_team_members", "view_reports"]'::jsonb;
        WHEN 'employee' THEN
            RETURN '["view_contacts", "create_contacts", "edit_contacts", "view_jobs", "create_jobs", "edit_jobs", "view_projects", "create_projects", "edit_projects", "view_invoices", "view_estimates"]'::jsonb;
        WHEN 'contractor' THEN
            RETURN '["view_contacts", "view_jobs", "view_projects"]'::jsonb;
        WHEN 'viewer' THEN
            RETURN '["view_contacts", "view_jobs", "view_projects"]'::jsonb;
        ELSE
            RETURN '["view_contacts"]'::jsonb; -- Fallback to minimum permissions
    END CASE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create a helper function to check if a user has permission (handles the "*" wildcard for owners)
CREATE OR REPLACE FUNCTION user_has_permission(user_permissions jsonb, required_permission text)
RETURNS boolean AS $$
BEGIN
    -- If user has "*" permission (owner), they have all permissions
    IF user_permissions ? '*' THEN
        RETURN true;
    END IF;
    
    -- Otherwise check for specific permission
    RETURN user_permissions ? required_permission;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Update existing owner memberships to use the new system
UPDATE business_memberships 
SET permissions = get_default_permissions_for_role('owner')
WHERE role = 'owner';

-- Create a view that shows effective permissions for business memberships
CREATE OR REPLACE VIEW business_membership_permissions AS
SELECT 
    bm.id,
    bm.business_id,
    bm.user_id,
    bm.role,
    bm.is_active,
    CASE 
        WHEN bm.role = 'owner' THEN 'ALL_PERMISSIONS'::text
        ELSE jsonb_array_length(bm.permissions)::text || ' specific permissions'
    END as permission_summary,
    bm.permissions as raw_permissions,
    CASE 
        WHEN bm.permissions ? '*' THEN true
        ELSE false
    END as has_all_permissions
FROM business_memberships bm;

-- Add helpful comment
COMMENT ON VIEW business_membership_permissions IS 'View showing business membership permissions with special handling for owners who have all permissions';

-- Verify the update
DO $$
DECLARE
    owner_count integer;
    owners_with_wildcard integer;
BEGIN
    SELECT COUNT(*) INTO owner_count 
    FROM business_memberships 
    WHERE role = 'owner';
    
    SELECT COUNT(*) INTO owners_with_wildcard 
    FROM business_memberships 
    WHERE role = 'owner' AND permissions ? '*';
    
    RAISE NOTICE 'Found % owner memberships, % now have wildcard permissions', owner_count, owners_with_wildcard;
END $$;
