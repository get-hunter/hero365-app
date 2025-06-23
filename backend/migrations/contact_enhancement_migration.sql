-- Contact Enhancement Migration
-- Adds relationship_status, lifecycle_stage, status_history, interaction_history fields
-- and display_name computed column as specified in Hero365 API Integration Plan Task 1.1

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Add missing fields to contacts table
ALTER TABLE contacts 
ADD COLUMN IF NOT EXISTS relationship_status VARCHAR(20) DEFAULT 'prospect' 
CHECK (relationship_status IN ('prospect', 'qualified_lead', 'opportunity', 'active_client', 'past_client', 'lost_lead', 'inactive'));

ALTER TABLE contacts 
ADD COLUMN IF NOT EXISTS lifecycle_stage VARCHAR(20) DEFAULT 'awareness' 
CHECK (lifecycle_stage IN ('awareness', 'interest', 'consideration', 'decision', 'retention', 'customer'));

ALTER TABLE contacts 
ADD COLUMN IF NOT EXISTS status_history JSONB DEFAULT '[]'::jsonb;

ALTER TABLE contacts 
ADD COLUMN IF NOT EXISTS interaction_history JSONB DEFAULT '[]'::jsonb;

-- 2. Add display_name as generated column
ALTER TABLE contacts 
ADD COLUMN IF NOT EXISTS display_name VARCHAR(200) 
GENERATED ALWAYS AS (
    CASE 
        WHEN company_name IS NOT NULL AND company_name != '' THEN
            CASE
                WHEN first_name IS NOT NULL AND last_name IS NOT NULL THEN
                    first_name || ' ' || last_name || ' (' || company_name || ')'
                WHEN first_name IS NOT NULL THEN
                    first_name || ' (' || company_name || ')'
                WHEN last_name IS NOT NULL THEN
                    last_name || ' (' || company_name || ')'
                ELSE
                    company_name
            END
        WHEN first_name IS NOT NULL AND last_name IS NOT NULL THEN
            first_name || ' ' || last_name
        WHEN first_name IS NOT NULL THEN
            first_name
        WHEN last_name IS NOT NULL THEN
            last_name
        ELSE
            'Unknown Contact'
    END
) STORED;

-- 3. Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_contacts_display_name ON contacts(display_name);
CREATE INDEX IF NOT EXISTS idx_contacts_status_history ON contacts USING gin(status_history);
CREATE INDEX IF NOT EXISTS idx_contacts_interaction_history ON contacts USING gin(interaction_history);
CREATE INDEX IF NOT EXISTS idx_contacts_relationship_status ON contacts(relationship_status);
CREATE INDEX IF NOT EXISTS idx_contacts_lifecycle_stage ON contacts(lifecycle_stage);

-- 4. Create function to automatically update status_history when relationship_status changes
CREATE OR REPLACE FUNCTION update_contact_status_history()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update status_history if relationship_status actually changed
    IF OLD.relationship_status IS DISTINCT FROM NEW.relationship_status THEN
        NEW.status_history = status_history || jsonb_build_object(
            'id', gen_random_uuid(),
            'from_status', OLD.relationship_status,
            'to_status', NEW.relationship_status,
            'timestamp', now(),
            'changed_by', COALESCE(NEW.assigned_to, NEW.created_by, 'system'),
            'reason', COALESCE(NEW.notes, 'Status updated')
        );
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 5. Create trigger for status_history updates
DROP TRIGGER IF EXISTS update_contact_status_history_trigger ON contacts;
CREATE TRIGGER update_contact_status_history_trigger
    BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION update_contact_status_history();

-- 6. Create function to add interaction to interaction_history
CREATE OR REPLACE FUNCTION add_contact_interaction_to_history()
RETURNS TRIGGER AS $$
BEGIN
    -- Add the new activity to the contact's interaction_history
    UPDATE contacts 
    SET interaction_history = interaction_history || jsonb_build_object(
        'id', NEW.id,
        'type', NEW.activity_type,
        'description', NEW.description,
        'timestamp', NEW.activity_date,
        'performed_by', NEW.performed_by,
        'outcome', NEW.outcome
    )
    WHERE id = NEW.contact_id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 7. Create trigger for interaction_history updates
DROP TRIGGER IF EXISTS add_contact_interaction_to_history_trigger ON contact_activities;
CREATE TRIGGER add_contact_interaction_to_history_trigger
    AFTER INSERT ON contact_activities
    FOR EACH ROW EXECUTE FUNCTION add_contact_interaction_to_history();

-- 8. Migrate existing contacts to have proper relationship_status based on contact_type
UPDATE contacts 
SET relationship_status = CASE 
    WHEN contact_type = 'customer' THEN 'active_client'
    WHEN contact_type = 'lead' THEN 'qualified_lead'
    WHEN contact_type = 'prospect' THEN 'prospect'
    WHEN contact_type = 'vendor' THEN 'active_client'
    WHEN contact_type = 'partner' THEN 'active_client'
    WHEN contact_type = 'contractor' THEN 'active_client'
    ELSE 'prospect'
END
WHERE relationship_status = 'prospect'; -- Only update default values

-- 9. Migrate existing contacts to have proper lifecycle_stage based on relationship_status
UPDATE contacts 
SET lifecycle_stage = CASE 
    WHEN relationship_status = 'prospect' THEN 'awareness'
    WHEN relationship_status = 'qualified_lead' THEN 'interest'
    WHEN relationship_status = 'opportunity' THEN 'consideration'
    WHEN relationship_status = 'active_client' THEN 'customer'
    WHEN relationship_status = 'past_client' THEN 'retention'
    WHEN relationship_status = 'lost_lead' THEN 'consideration'
    WHEN relationship_status = 'inactive' THEN 'retention'
    ELSE 'awareness'
END
WHERE lifecycle_stage = 'awareness'; -- Only update default values

-- 10. Initialize status_history for existing contacts
UPDATE contacts 
SET status_history = jsonb_build_array(
    jsonb_build_object(
        'id', gen_random_uuid(),
        'from_status', null,
        'to_status', relationship_status,
        'timestamp', created_date,
        'changed_by', COALESCE(created_by, 'system'),
        'reason', 'Initial status set during migration'
    )
)
WHERE jsonb_array_length(status_history) = 0;

-- 11. Add comments for documentation
COMMENT ON COLUMN contacts.relationship_status IS 'Current relationship status in the sales/client lifecycle';
COMMENT ON COLUMN contacts.lifecycle_stage IS 'Stage in the customer lifecycle journey';
COMMENT ON COLUMN contacts.status_history IS 'JSONB array tracking all relationship status changes over time';
COMMENT ON COLUMN contacts.interaction_history IS 'JSONB array with recent interaction summaries for quick access';
COMMENT ON COLUMN contacts.display_name IS 'Computed display name combining first_name, last_name, and company_name';

-- 12. Create view for enhanced contact information
CREATE OR REPLACE VIEW contact_enhanced_summary AS
SELECT 
    c.*,
    CASE 
        WHEN c.relationship_status = 'active_client' THEN 'Active Client'
        WHEN c.relationship_status = 'qualified_lead' THEN 'Qualified Lead'
        WHEN c.relationship_status = 'opportunity' THEN 'Opportunity'
        WHEN c.relationship_status = 'prospect' THEN 'Prospect'
        WHEN c.relationship_status = 'past_client' THEN 'Past Client'
        WHEN c.relationship_status = 'lost_lead' THEN 'Lost Lead'
        WHEN c.relationship_status = 'inactive' THEN 'Inactive'
        ELSE 'Unknown'
    END as relationship_status_display,
    CASE 
        WHEN c.lifecycle_stage = 'awareness' THEN 'Awareness'
        WHEN c.lifecycle_stage = 'interest' THEN 'Interest'
        WHEN c.lifecycle_stage = 'consideration' THEN 'Consideration'
        WHEN c.lifecycle_stage = 'decision' THEN 'Decision'
        WHEN c.lifecycle_stage = 'retention' THEN 'Retention'
        WHEN c.lifecycle_stage = 'customer' THEN 'Customer'
        ELSE 'Unknown'
    END as lifecycle_stage_display,
    (SELECT COUNT(*) FROM contact_activities ca WHERE ca.contact_id = c.id) as total_interactions,
    (SELECT COUNT(*) FROM contact_notes cn WHERE cn.contact_id = c.id) as total_notes,
    jsonb_array_length(c.status_history) as status_changes_count,
    jsonb_array_length(c.interaction_history) as interaction_summary_count
FROM contacts c
WHERE c.status != 'archived';

-- Grant appropriate permissions
-- GRANT SELECT, INSERT, UPDATE, DELETE ON contacts TO your_app_role;
-- GRANT SELECT ON contact_enhanced_summary TO your_app_role;

-- Migration completed successfully
SELECT 'Contact enhancement migration completed successfully' as status; 