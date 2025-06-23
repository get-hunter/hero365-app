-- Fix Business Membership Permissions Migration
-- This migration fixes the issue where business memberships have empty permission arrays

-- Create function to get default permissions for role
CREATE OR REPLACE FUNCTION get_default_permissions_for_role(role_name text)
RETURNS jsonb AS $$
BEGIN
    CASE role_name
        WHEN 'owner' THEN
            RETURN '["view_contacts", "create_contacts", "edit_contacts", "delete_contacts", "view_jobs", "create_jobs", "edit_jobs", "delete_jobs", "view_projects", "create_projects", "edit_projects", "delete_projects", "edit_business_profile", "view_business_settings", "edit_business_settings", "invite_team_members", "edit_team_members", "remove_team_members", "view_invoices", "create_invoices", "edit_invoices", "delete_invoices", "view_estimates", "create_estimates", "edit_estimates", "delete_estimates", "view_reports", "edit_reports", "view_accounting", "edit_accounting"]'::jsonb;
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

-- Create trigger function to auto-assign permissions on insert/update
CREATE OR REPLACE FUNCTION assign_default_permissions()
RETURNS TRIGGER AS $$
BEGIN
    -- If permissions array is empty or null, assign default permissions based on role
    IF NEW.permissions IS NULL OR jsonb_array_length(NEW.permissions) = 0 THEN
        NEW.permissions = get_default_permissions_for_role(NEW.role);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for business_memberships
DROP TRIGGER IF EXISTS trigger_assign_default_permissions ON business_memberships;
CREATE TRIGGER trigger_assign_default_permissions
    BEFORE INSERT OR UPDATE ON business_memberships
    FOR EACH ROW
    EXECUTE FUNCTION assign_default_permissions();

-- Update existing memberships with empty permissions arrays
UPDATE business_memberships 
SET permissions = get_default_permissions_for_role(role)
WHERE permissions = '[]'::jsonb 
   OR permissions IS NULL 
   OR jsonb_array_length(permissions) = 0;

-- Verify the update worked
DO $$
DECLARE
    empty_count integer;
BEGIN
    SELECT COUNT(*) INTO empty_count 
    FROM business_memberships 
    WHERE permissions = '[]'::jsonb 
       OR permissions IS NULL 
       OR jsonb_array_length(permissions) = 0;
    
    IF empty_count > 0 THEN
        RAISE NOTICE 'Warning: % business memberships still have empty permissions arrays', empty_count;
    ELSE
        RAISE NOTICE 'Success: All business memberships now have default permissions assigned';
    END IF;
END $$;
