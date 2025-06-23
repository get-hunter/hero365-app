-- Link User IDs to auth.users table Migration
-- This migration converts user_id fields from text to uuid and adds foreign key constraints

-- Step 1: Drop views that depend on user_id columns to allow type conversion
DROP VIEW IF EXISTS "contact_enhanced_summary";
DROP VIEW IF EXISTS "contact_summary";
DROP VIEW IF EXISTS "job_enhanced_summary";
DROP VIEW IF EXISTS "activity_enhanced_summary";
DROP VIEW IF EXISTS "user_enhanced_summary";

-- Step 2: Drop RLS policies that depend on user_id columns to allow type conversion
DROP POLICY IF EXISTS "activities_business_isolation" ON activities;
DROP POLICY IF EXISTS "activity_templates_business_isolation" ON activity_templates;
DROP POLICY IF EXISTS "activity_participants_business_isolation" ON activity_participants;
DROP POLICY IF EXISTS "activity_reminders_business_isolation" ON activity_reminders;
DROP POLICY IF EXISTS "calendar_events_business_isolation" ON calendar_events;
DROP POLICY IF EXISTS "calendar_preferences_business_isolation" ON calendar_preferences;
DROP POLICY IF EXISTS "time_off_requests_business_isolation" ON time_off_requests;
DROP POLICY IF EXISTS "user_capabilities_business_isolation" ON user_capabilities;
DROP POLICY IF EXISTS "user_certifications_business_isolation" ON user_certifications;
DROP POLICY IF EXISTS "user_skills_business_isolation" ON user_skills;
DROP POLICY IF EXISTS "workload_capacity_business_isolation" ON workload_capacity;
DROP POLICY IF EXISTS "availability_windows_business_isolation" ON availability_windows;
DROP POLICY IF EXISTS "contacts_business_isolation" ON contacts;
DROP POLICY IF EXISTS "contact_activities_business_isolation" ON contact_activities;
DROP POLICY IF EXISTS "contact_notes_business_isolation" ON contact_notes;
DROP POLICY IF EXISTS "contact_segments_business_isolation" ON contact_segments;
DROP POLICY IF EXISTS "jobs_business_isolation" ON jobs;
DROP POLICY IF EXISTS "job_activities_business_isolation" ON job_activities;
DROP POLICY IF EXISTS "job_notes_business_isolation" ON job_notes;
DROP POLICY IF EXISTS "business_memberships_business_isolation" ON business_memberships;
DROP POLICY IF EXISTS "business_invitations_business_isolation" ON business_invitations;
DROP POLICY IF EXISTS "businesses_business_isolation" ON businesses;

-- Step 3: Convert user_id columns from text to uuid type
-- Note: This assumes existing user_id values are already valid UUIDs in text format

-- Convert calendar_events.user_id from text to uuid
ALTER TABLE calendar_events 
ALTER COLUMN user_id TYPE uuid USING user_id::uuid;

-- Convert calendar_preferences.user_id from text to uuid  
ALTER TABLE calendar_preferences 
ALTER COLUMN user_id TYPE uuid USING user_id::uuid;

-- Convert time_off_requests user_id fields from text to uuid
ALTER TABLE time_off_requests 
ALTER COLUMN user_id TYPE uuid USING user_id::uuid;

ALTER TABLE time_off_requests 
ALTER COLUMN requested_by TYPE uuid USING requested_by::uuid;

-- Convert approved_by (nullable field)
ALTER TABLE time_off_requests 
ALTER COLUMN approved_by TYPE uuid USING CASE 
    WHEN approved_by IS NULL THEN NULL 
    ELSE approved_by::uuid 
END;

-- Convert user_capabilities.user_id from text to uuid
ALTER TABLE user_capabilities 
ALTER COLUMN user_id TYPE uuid USING user_id::uuid;

-- Convert business_memberships.user_id from text to uuid
ALTER TABLE business_memberships 
ALTER COLUMN user_id TYPE uuid USING user_id::uuid;

-- Convert invited_by (nullable field)
ALTER TABLE business_memberships 
ALTER COLUMN invited_by TYPE uuid USING CASE 
    WHEN invited_by IS NULL THEN NULL 
    ELSE invited_by::uuid 
END;

-- Convert business_invitations.invited_by from text to uuid
ALTER TABLE business_invitations 
ALTER COLUMN invited_by TYPE uuid USING invited_by::uuid;

-- Convert contact-related user_id fields from text to uuid
ALTER TABLE contacts 
ALTER COLUMN created_by TYPE uuid USING CASE 
    WHEN created_by IS NULL THEN NULL 
    ELSE created_by::uuid 
END;

ALTER TABLE contacts 
ALTER COLUMN assigned_to TYPE uuid USING CASE 
    WHEN assigned_to IS NULL THEN NULL 
    ELSE assigned_to::uuid 
END;

ALTER TABLE contact_activities 
ALTER COLUMN performed_by TYPE uuid USING performed_by::uuid;

ALTER TABLE contact_notes 
ALTER COLUMN created_by TYPE uuid USING created_by::uuid;

-- Convert job-related user_id fields from text to uuid
ALTER TABLE jobs 
ALTER COLUMN created_by TYPE uuid USING created_by::uuid;

-- Convert jobs.assigned_to array from text[] to uuid[]
ALTER TABLE jobs 
ALTER COLUMN assigned_to DROP DEFAULT;

ALTER TABLE jobs 
ALTER COLUMN assigned_to TYPE uuid[] USING assigned_to::uuid[];

ALTER TABLE jobs 
ALTER COLUMN assigned_to SET DEFAULT '{}'::uuid[];

ALTER TABLE job_activities 
ALTER COLUMN user_id TYPE uuid USING user_id::uuid;

ALTER TABLE job_notes 
ALTER COLUMN user_id TYPE uuid USING user_id::uuid;

-- Convert activity_templates.user_id if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'activity_templates' 
               AND column_name = 'user_id') THEN
        ALTER TABLE activity_templates 
        ALTER COLUMN user_id TYPE uuid USING user_id::uuid;
    END IF;
END $$;

-- Convert activities.user_id if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'activities' 
               AND column_name = 'user_id') THEN
        ALTER TABLE activities 
        ALTER COLUMN user_id TYPE uuid USING user_id::uuid;
    END IF;
END $$;

-- Convert activity_participants.user_id if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'activity_participants' 
               AND column_name = 'user_id') THEN
        ALTER TABLE activity_participants 
        ALTER COLUMN user_id TYPE uuid USING user_id::uuid;
    END IF;
END $$;

-- Convert activity_reminders.user_id if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'activity_reminders' 
               AND column_name = 'user_id') THEN
        ALTER TABLE activity_reminders 
        ALTER COLUMN user_id TYPE uuid USING user_id::uuid;
    END IF;
END $$;

-- Step 4: Add foreign key constraints after type conversion

-- Add foreign key constraints for new tables from intelligent scheduling migration
ALTER TABLE calendar_events 
ADD CONSTRAINT fk_calendar_events_user_id 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

ALTER TABLE calendar_preferences 
ADD CONSTRAINT fk_calendar_preferences_user_id 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

ALTER TABLE time_off_requests 
ADD CONSTRAINT fk_time_off_requests_user_id 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

ALTER TABLE time_off_requests 
ADD CONSTRAINT fk_time_off_requests_requested_by 
FOREIGN KEY (requested_by) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Add constraint for approved_by (nullable, so we need to handle NULL values)
ALTER TABLE time_off_requests 
ADD CONSTRAINT fk_time_off_requests_approved_by 
FOREIGN KEY (approved_by) REFERENCES auth.users(id) ON DELETE SET NULL;

ALTER TABLE user_capabilities 
ADD CONSTRAINT fk_user_capabilities_user_id 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Add foreign key constraints for existing tables that were missing them
ALTER TABLE business_memberships 
ADD CONSTRAINT fk_business_memberships_user_id 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Add constraint for invited_by (nullable, so we need to handle NULL values)  
ALTER TABLE business_memberships 
ADD CONSTRAINT fk_business_memberships_invited_by 
FOREIGN KEY (invited_by) REFERENCES auth.users(id) ON DELETE SET NULL;

ALTER TABLE business_invitations 
ADD CONSTRAINT fk_business_invitations_invited_by 
FOREIGN KEY (invited_by) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Add foreign key constraints for contact-related tables
ALTER TABLE contacts 
ADD CONSTRAINT fk_contacts_created_by 
FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE SET NULL;

ALTER TABLE contacts 
ADD CONSTRAINT fk_contacts_assigned_to 
FOREIGN KEY (assigned_to) REFERENCES auth.users(id) ON DELETE SET NULL;

ALTER TABLE contact_activities 
ADD CONSTRAINT fk_contact_activities_performed_by 
FOREIGN KEY (performed_by) REFERENCES auth.users(id) ON DELETE SET NULL;

ALTER TABLE contact_notes 
ADD CONSTRAINT fk_contact_notes_created_by 
FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE SET NULL;

-- Add foreign key constraints for job-related tables
ALTER TABLE jobs 
ADD CONSTRAINT fk_jobs_created_by 
FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE SET NULL;

-- Handle assigned_to array - we'll create a check constraint instead of FK since it's an array
-- Note: Arrays can't have foreign key constraints, but we can add a check function
CREATE OR REPLACE FUNCTION validate_assigned_to_users(user_ids uuid[])
RETURNS boolean AS $$
BEGIN
    -- Check if all user IDs in the array exist in auth.users
    RETURN NOT EXISTS (
        SELECT 1 
        FROM unnest(user_ids) AS uid
        WHERE uid IS NOT NULL 
        AND NOT EXISTS (SELECT 1 FROM auth.users WHERE id = uid)
    );
END;
$$ LANGUAGE plpgsql;

-- Add check constraint for jobs.assigned_to array
ALTER TABLE jobs 
ADD CONSTRAINT chk_jobs_assigned_to_valid_users 
CHECK (validate_assigned_to_users(assigned_to));

ALTER TABLE job_activities 
ADD CONSTRAINT fk_job_activities_user_id 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE SET NULL;

ALTER TABLE job_notes 
ADD CONSTRAINT fk_job_notes_user_id 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE SET NULL;

-- Step 5: Add indexes to improve performance on foreign key lookups
CREATE INDEX IF NOT EXISTS idx_calendar_events_user_id ON calendar_events(user_id);
CREATE INDEX IF NOT EXISTS idx_calendar_preferences_user_id ON calendar_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_time_off_requests_user_id ON time_off_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_time_off_requests_requested_by ON time_off_requests(requested_by);
CREATE INDEX IF NOT EXISTS idx_time_off_requests_approved_by ON time_off_requests(approved_by) WHERE approved_by IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_capabilities_user_id ON user_capabilities(user_id);
CREATE INDEX IF NOT EXISTS idx_business_memberships_user_id ON business_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_business_memberships_invited_by ON business_memberships(invited_by) WHERE invited_by IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_business_invitations_invited_by ON business_invitations(invited_by);
CREATE INDEX IF NOT EXISTS idx_contacts_created_by ON contacts(created_by) WHERE created_by IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_contacts_assigned_to ON contacts(assigned_to) WHERE assigned_to IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_contact_activities_performed_by ON contact_activities(performed_by) WHERE performed_by IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_contact_notes_created_by ON contact_notes(created_by) WHERE created_by IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_created_by ON jobs(created_by) WHERE created_by IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_job_activities_user_id ON job_activities(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_job_notes_user_id ON job_notes(user_id) WHERE user_id IS NOT NULL;

-- Step 6: Recreate RLS policies with updated uuid types
DROP POLICY IF EXISTS "calendar_events_business_isolation" ON calendar_events;
CREATE POLICY "calendar_events_business_isolation" ON calendar_events
FOR ALL TO PUBLIC
USING (business_id IN (
    SELECT business_memberships.business_id
    FROM business_memberships
    WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
    AND business_memberships.is_active = true
));

DROP POLICY IF EXISTS "calendar_preferences_business_isolation" ON calendar_preferences;
CREATE POLICY "calendar_preferences_business_isolation" ON calendar_preferences
FOR ALL TO PUBLIC
USING (business_id IN (
    SELECT business_memberships.business_id
    FROM business_memberships
    WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
    AND business_memberships.is_active = true
));

DROP POLICY IF EXISTS "time_off_requests_business_isolation" ON time_off_requests;
CREATE POLICY "time_off_requests_business_isolation" ON time_off_requests
FOR ALL TO PUBLIC
USING (business_id IN (
    SELECT business_memberships.business_id
    FROM business_memberships
    WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
    AND business_memberships.is_active = true
));

DROP POLICY IF EXISTS "user_capabilities_business_isolation" ON user_capabilities;
CREATE POLICY "user_capabilities_business_isolation" ON user_capabilities
FOR ALL TO PUBLIC
USING (business_id IN (
    SELECT business_memberships.business_id
    FROM business_memberships
    WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
    AND business_memberships.is_active = true
));

DROP POLICY IF EXISTS "user_certifications_business_isolation" ON user_certifications;
CREATE POLICY "user_certifications_business_isolation" ON user_certifications
FOR ALL TO PUBLIC
USING (user_capabilities_id IN (
    SELECT user_capabilities.id
    FROM user_capabilities
    WHERE user_capabilities.business_id IN (
        SELECT business_memberships.business_id
        FROM business_memberships
        WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
        AND business_memberships.is_active = true
    )
));

DROP POLICY IF EXISTS "user_skills_business_isolation" ON user_skills;
CREATE POLICY "user_skills_business_isolation" ON user_skills
FOR ALL TO PUBLIC
USING (user_capabilities_id IN (
    SELECT user_capabilities.id
    FROM user_capabilities
    WHERE user_capabilities.business_id IN (
        SELECT business_memberships.business_id
        FROM business_memberships
        WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
        AND business_memberships.is_active = true
    )
));

DROP POLICY IF EXISTS "workload_capacity_business_isolation" ON workload_capacity;
CREATE POLICY "workload_capacity_business_isolation" ON workload_capacity
FOR ALL TO PUBLIC
USING (user_capabilities_id IN (
    SELECT user_capabilities.id
    FROM user_capabilities
    WHERE user_capabilities.business_id IN (
        SELECT business_memberships.business_id
        FROM business_memberships
        WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
        AND business_memberships.is_active = true
    )
));

DROP POLICY IF EXISTS "availability_windows_business_isolation" ON availability_windows;
CREATE POLICY "availability_windows_business_isolation" ON availability_windows
FOR ALL TO PUBLIC
USING (user_capabilities_id IN (
    SELECT user_capabilities.id
    FROM user_capabilities
    WHERE user_capabilities.business_id IN (
        SELECT business_memberships.business_id
        FROM business_memberships
        WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
        AND business_memberships.is_active = true
    )
));

-- Recreate activity_templates policy if the table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'activity_templates') THEN
        DROP POLICY IF EXISTS "activity_templates_business_isolation" ON activity_templates;
        CREATE POLICY "activity_templates_business_isolation" ON activity_templates
        FOR ALL TO PUBLIC
        USING (business_id IN (
            SELECT business_memberships.business_id
            FROM business_memberships
            WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
            AND business_memberships.is_active = true
        ));
    END IF;
END $$;

-- Recreate activities policy if the table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'activities') THEN
        DROP POLICY IF EXISTS "activities_business_isolation" ON activities;
        CREATE POLICY "activities_business_isolation" ON activities
        FOR ALL TO PUBLIC
        USING (business_id IN (
            SELECT business_memberships.business_id
            FROM business_memberships
            WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
            AND business_memberships.is_active = true
        ));
    END IF;
END $$;

-- Recreate contacts policy
DROP POLICY IF EXISTS "contacts_business_isolation" ON contacts;
CREATE POLICY "contacts_business_isolation" ON contacts
FOR ALL TO PUBLIC
USING (business_id IN (
    SELECT business_memberships.business_id
    FROM business_memberships
    WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
    AND business_memberships.is_active = true
));

-- Recreate contact_activities policy
DROP POLICY IF EXISTS "contact_activities_business_isolation" ON contact_activities;
CREATE POLICY "contact_activities_business_isolation" ON contact_activities
FOR ALL TO PUBLIC
USING (contact_id IN (
    SELECT contacts.id
    FROM contacts
    WHERE contacts.business_id IN (
        SELECT business_memberships.business_id
        FROM business_memberships
        WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
        AND business_memberships.is_active = true
    )
));

-- Recreate contact_notes policy
DROP POLICY IF EXISTS "contact_notes_business_isolation" ON contact_notes;
CREATE POLICY "contact_notes_business_isolation" ON contact_notes
FOR ALL TO PUBLIC
USING (contact_id IN (
    SELECT contacts.id
    FROM contacts
    WHERE contacts.business_id IN (
        SELECT business_memberships.business_id
        FROM business_memberships
        WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
        AND business_memberships.is_active = true
    )
));

-- Recreate jobs policy
DROP POLICY IF EXISTS "jobs_business_isolation" ON jobs;
CREATE POLICY "jobs_business_isolation" ON jobs
FOR ALL TO PUBLIC
USING (business_id IN (
    SELECT business_memberships.business_id
    FROM business_memberships
    WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
    AND business_memberships.is_active = true
));

-- Recreate job_activities policy
DROP POLICY IF EXISTS "job_activities_business_isolation" ON job_activities;
CREATE POLICY "job_activities_business_isolation" ON job_activities
FOR ALL TO PUBLIC
USING (job_id IN (
    SELECT jobs.id
    FROM jobs
    WHERE jobs.business_id IN (
        SELECT business_memberships.business_id
        FROM business_memberships
        WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
        AND business_memberships.is_active = true
    )
));

-- Recreate job_notes policy
DROP POLICY IF EXISTS "job_notes_business_isolation" ON job_notes;
CREATE POLICY "job_notes_business_isolation" ON job_notes
FOR ALL TO PUBLIC
USING (job_id IN (
    SELECT jobs.id
    FROM jobs
    WHERE jobs.business_id IN (
        SELECT business_memberships.business_id
        FROM business_memberships
        WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
        AND business_memberships.is_active = true
    )
));

-- Recreate business_memberships policy
DROP POLICY IF EXISTS "business_memberships_business_isolation" ON business_memberships;
CREATE POLICY "business_memberships_business_isolation" ON business_memberships
FOR ALL TO PUBLIC
USING (
    user_id = (current_setting('app.current_user_id'::text, true))::uuid
    OR business_id IN (
        SELECT business_memberships.business_id
        FROM business_memberships
        WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
        AND business_memberships.is_active = true
        AND business_memberships.permissions @> '["view_team_members"]'::jsonb
    )
);

-- Recreate business_invitations policy
DROP POLICY IF EXISTS "business_invitations_business_isolation" ON business_invitations;
CREATE POLICY "business_invitations_business_isolation" ON business_invitations
FOR ALL TO PUBLIC
USING (business_id IN (
    SELECT business_memberships.business_id
    FROM business_memberships
    WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
    AND business_memberships.is_active = true
    AND business_memberships.permissions @> '["invite_team_members"]'::jsonb
));

-- Recreate businesses policy if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'businesses') THEN
        DROP POLICY IF EXISTS "businesses_business_isolation" ON businesses;
        CREATE POLICY "businesses_business_isolation" ON businesses
        FOR ALL TO PUBLIC
        USING (id IN (
            SELECT business_memberships.business_id
            FROM business_memberships
            WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
            AND business_memberships.is_active = true
        ));
    END IF;
END $$;

-- Recreate activity_participants policy if the table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'activity_participants') THEN
        DROP POLICY IF EXISTS "activity_participants_business_isolation" ON activity_participants;
        CREATE POLICY "activity_participants_business_isolation" ON activity_participants
        FOR ALL TO PUBLIC
        USING (activity_id IN (
            SELECT activities.id
            FROM activities
            WHERE activities.business_id IN (
                SELECT business_memberships.business_id
                FROM business_memberships
                WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
                AND business_memberships.is_active = true
            )
        ));
    END IF;
END $$;

-- Recreate activity_reminders policy if the table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'activity_reminders') THEN
        DROP POLICY IF EXISTS "activity_reminders_business_isolation" ON activity_reminders;
        CREATE POLICY "activity_reminders_business_isolation" ON activity_reminders
        FOR ALL TO PUBLIC
        USING (activity_id IN (
            SELECT activities.id
            FROM activities
            WHERE activities.business_id IN (
                SELECT business_memberships.business_id
                FROM business_memberships
                WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
                AND business_memberships.is_active = true
            )
        ));
    END IF;
END $$;

-- Recreate contact_segments policy if the table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'contact_segments') THEN
        DROP POLICY IF EXISTS "contact_segments_business_isolation" ON contact_segments;
        CREATE POLICY "contact_segments_business_isolation" ON contact_segments
        FOR ALL TO PUBLIC
        USING (business_id IN (
            SELECT business_memberships.business_id
            FROM business_memberships
            WHERE business_memberships.user_id = (current_setting('app.current_user_id'::text, true))::uuid
            AND business_memberships.is_active = true
        ));
    END IF;
END $$;

-- Step 7: Add comments for documentation
COMMENT ON CONSTRAINT fk_calendar_events_user_id ON calendar_events IS 'Links calendar events to authenticated users';
COMMENT ON CONSTRAINT fk_calendar_preferences_user_id ON calendar_preferences IS 'Links calendar preferences to authenticated users';
COMMENT ON CONSTRAINT fk_time_off_requests_user_id ON time_off_requests IS 'Links time off requests to authenticated users';
COMMENT ON CONSTRAINT fk_user_capabilities_user_id ON user_capabilities IS 'Links user capabilities to authenticated users';
COMMENT ON CONSTRAINT fk_business_memberships_user_id ON business_memberships IS 'Links business memberships to authenticated users';
COMMENT ON CONSTRAINT fk_business_invitations_invited_by ON business_invitations IS 'Links business invitations to the inviting user';

-- Step 8: Recreate views that were dropped with proper uuid handling
-- Recreate contact_summary view
CREATE OR REPLACE VIEW contact_summary AS
SELECT 
    c.id,
    c.business_id,
    c.contact_type,
    c.status,
    c.priority,
    COALESCE(c.company_name, CONCAT(c.first_name, ' ', c.last_name)) as display_name,
    COALESCE(c.email, c.phone, c.mobile_phone) as primary_contact,
    c.estimated_value,
    c.assigned_to,
    c.created_date,
    c.last_contacted,
    (SELECT COUNT(*) FROM contact_activities ca WHERE ca.contact_id = c.id) as activity_count,
    (SELECT COUNT(*) FROM contact_notes cn WHERE cn.contact_id = c.id) as note_count
FROM contacts c
WHERE c.status != 'archived';

-- Recreate contact_enhanced_summary view
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

-- Recreate activity_timeline_view if activities table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'activities') THEN
        CREATE OR REPLACE VIEW activity_timeline_view AS
        SELECT 
            a.id,
            a.business_id,
            a.contact_id,
            c.display_name as contact_name,
            c.email as contact_email,
            c.phone as contact_phone,
            a.activity_type,
            a.title,
            a.description,
            a.status,
            a.priority,
            a.scheduled_date,
            a.due_date,
            a.completed_date,
            a.duration_minutes,
            a.location,
            a.created_by,
            a.assigned_to,
            a.tags,
            a.metadata,
            a.created_date,
            a.last_modified,
            CASE 
                WHEN a.status IN ('pending', 'in_progress') AND 
                     ((a.due_date IS NOT NULL AND a.due_date < NOW()) OR
                      (a.due_date IS NULL AND a.scheduled_date IS NOT NULL AND a.scheduled_date < NOW() - INTERVAL '1 day'))
                THEN true
                ELSE false
            END as is_overdue,
            CASE 
                WHEN a.scheduled_date IS NOT NULL AND a.scheduled_date > NOW() 
                     AND a.scheduled_date <= NOW() + INTERVAL '7 days'
                THEN true
                ELSE false
            END as is_upcoming
        FROM activities a
        JOIN contacts c ON a.contact_id = c.id;
    END IF;
END $$;

-- Recreate user_dashboard_activities if activities table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'activities') THEN
        CREATE OR REPLACE VIEW user_dashboard_activities AS
        SELECT 
            a.id,
            a.business_id,
            a.contact_id,
            c.display_name as contact_name,
            a.activity_type,
            a.title,
            a.status,
            a.priority,
            a.scheduled_date,
            a.due_date,
            a.assigned_to,
            a.created_date,
            CASE 
                WHEN a.status IN ('pending', 'in_progress') AND 
                     ((a.due_date IS NOT NULL AND a.due_date < NOW()) OR
                      (a.due_date IS NULL AND a.scheduled_date IS NOT NULL AND a.scheduled_date < NOW() - INTERVAL '1 day'))
                THEN 'overdue'
                WHEN a.scheduled_date IS NOT NULL AND a.scheduled_date > NOW() 
                     AND a.scheduled_date <= NOW() + INTERVAL '7 days'
                THEN 'upcoming'
                ELSE 'normal'
            END as urgency_status
        FROM activities a
        JOIN contacts c ON a.contact_id = c.id
        WHERE a.status IN ('pending', 'in_progress')
        ORDER BY 
            CASE 
                WHEN a.priority = 'urgent' THEN 1
                WHEN a.priority = 'high' THEN 2
                WHEN a.priority = 'medium' THEN 3
                ELSE 4
            END,
            a.due_date ASC NULLS LAST,
            a.scheduled_date ASC NULLS LAST;
    END IF;
END $$; 