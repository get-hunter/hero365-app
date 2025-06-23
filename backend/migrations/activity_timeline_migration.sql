-- Activity Timeline System Migration
-- Creates tables for comprehensive activity and timeline management
-- Author: AI Assistant
-- Date: 2024-01-10

-- Create activity types enum
CREATE TYPE activity_type AS ENUM (
    'interaction',
    'status_change',
    'task',
    'reminder',
    'note',
    'system_event',
    'service_event',
    'financial_event',
    'document_event'
);

-- Create activity status enum
CREATE TYPE activity_status AS ENUM (
    'pending',
    'in_progress',
    'completed',
    'cancelled',
    'overdue'
);

-- Create activity priority enum
CREATE TYPE activity_priority AS ENUM (
    'low',
    'medium',
    'high',
    'urgent'
);

-- Create activity templates table
CREATE TABLE activity_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    activity_type activity_type NOT NULL,
    default_duration INTEGER, -- in minutes
    default_reminders JSONB DEFAULT '[]',
    default_participants TEXT[] DEFAULT '{}',
    custom_fields JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_by VARCHAR(100) NOT NULL,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create activities table
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    template_id UUID REFERENCES activity_templates(id) ON DELETE SET NULL,
    parent_activity_id UUID REFERENCES activities(id) ON DELETE SET NULL,
    
    -- Activity details
    activity_type activity_type NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status activity_status DEFAULT 'pending',
    priority activity_priority DEFAULT 'medium',
    
    -- Scheduling
    scheduled_date TIMESTAMP WITH TIME ZONE,
    due_date TIMESTAMP WITH TIME ZONE,
    completed_date TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    location VARCHAR(500),
    
    -- Assignment and tracking
    created_by VARCHAR(100) NOT NULL,
    assigned_to VARCHAR(100),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT check_due_after_scheduled CHECK (due_date IS NULL OR scheduled_date IS NULL OR due_date >= scheduled_date),
    CONSTRAINT check_completed_when_status_completed CHECK (
        (status = 'completed' AND completed_date IS NOT NULL) OR 
        (status != 'completed' AND completed_date IS NULL)
    )
);

-- Create activity participants table
CREATE TABLE activity_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_id UUID NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    role VARCHAR(50) DEFAULT 'participant', -- 'organizer', 'participant', 'observer'
    is_primary BOOLEAN DEFAULT false,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint to prevent duplicate participants
    UNIQUE(activity_id, user_id)
);

-- Create activity reminders table
CREATE TABLE activity_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_id UUID NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    reminder_time TIMESTAMP WITH TIME ZONE NOT NULL,
    reminder_type VARCHAR(50) DEFAULT 'notification', -- 'notification', 'email', 'sms'
    message TEXT,
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance

-- Activity templates indexes
CREATE INDEX idx_activity_templates_business_id ON activity_templates(business_id);
CREATE INDEX idx_activity_templates_type ON activity_templates(activity_type);
CREATE INDEX idx_activity_templates_active ON activity_templates(is_active);

-- Activities indexes
CREATE INDEX idx_activities_business_id ON activities(business_id);
CREATE INDEX idx_activities_contact_id ON activities(contact_id);
CREATE INDEX idx_activities_template_id ON activities(template_id);
CREATE INDEX idx_activities_parent_id ON activities(parent_activity_id);
CREATE INDEX idx_activities_type ON activities(activity_type);
CREATE INDEX idx_activities_status ON activities(status);
CREATE INDEX idx_activities_priority ON activities(priority);
CREATE INDEX idx_activities_assigned_to ON activities(assigned_to);
CREATE INDEX idx_activities_created_by ON activities(created_by);
CREATE INDEX idx_activities_scheduled_date ON activities(scheduled_date);
CREATE INDEX idx_activities_due_date ON activities(due_date);
CREATE INDEX idx_activities_created_date ON activities(created_date);
CREATE INDEX idx_activities_last_modified ON activities(last_modified);

-- Composite indexes for common queries
CREATE INDEX idx_activities_contact_timeline ON activities(contact_id, business_id, scheduled_date DESC, created_date DESC);
CREATE INDEX idx_activities_business_timeline ON activities(business_id, scheduled_date DESC, created_date DESC);
CREATE INDEX idx_activities_user_tasks ON activities(business_id, assigned_to, status, due_date);
CREATE INDEX idx_activities_overdue ON activities(business_id, status, due_date) WHERE status IN ('pending', 'in_progress');
CREATE INDEX idx_activities_upcoming ON activities(business_id, scheduled_date) WHERE status IN ('pending', 'in_progress');

-- Activity participants indexes
CREATE INDEX idx_activity_participants_activity_id ON activity_participants(activity_id);
CREATE INDEX idx_activity_participants_user_id ON activity_participants(user_id);

-- Activity reminders indexes
CREATE INDEX idx_activity_reminders_activity_id ON activity_reminders(activity_id);
CREATE INDEX idx_activity_reminders_time ON activity_reminders(reminder_time);
CREATE INDEX idx_activity_reminders_pending ON activity_reminders(is_sent, reminder_time) WHERE is_sent = false;

-- Enable Row Level Security (RLS)
ALTER TABLE activity_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_reminders ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for activity templates
CREATE POLICY activity_templates_business_isolation ON activity_templates
    FOR ALL 
    USING (
        business_id IN (
            SELECT business_id 
            FROM business_memberships 
            WHERE user_id = current_setting('app.current_user_id', true)
            AND is_active = true
        )
    );

-- Create RLS policies for activities
CREATE POLICY activities_business_isolation ON activities
    FOR ALL 
    USING (
        business_id IN (
            SELECT business_id 
            FROM business_memberships 
            WHERE user_id = current_setting('app.current_user_id', true)
            AND is_active = true
        )
    );

-- Create RLS policies for activity participants
CREATE POLICY activity_participants_business_isolation ON activity_participants
    FOR ALL 
    USING (
        activity_id IN (
            SELECT id FROM activities 
            WHERE business_id IN (
                SELECT business_id 
                FROM business_memberships 
                WHERE user_id = current_setting('app.current_user_id', true)
                AND is_active = true
            )
        )
    );

-- Create RLS policies for activity reminders
CREATE POLICY activity_reminders_business_isolation ON activity_reminders
    FOR ALL 
    USING (
        activity_id IN (
            SELECT id FROM activities 
            WHERE business_id IN (
                SELECT business_id 
                FROM business_memberships 
                WHERE user_id = current_setting('app.current_user_id', true)
                AND is_active = true
            )
        )
    );

-- Create functions for automatic updates

-- Function to update last_modified timestamp
CREATE OR REPLACE FUNCTION update_activity_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update activity status to overdue
CREATE OR REPLACE FUNCTION update_overdue_activities()
RETURNS void AS $$
BEGIN
    UPDATE activities 
    SET status = 'overdue',
        last_modified = NOW()
    WHERE status IN ('pending', 'in_progress')
    AND (
        (due_date IS NOT NULL AND due_date < NOW()) OR
        (due_date IS NULL AND scheduled_date IS NOT NULL AND scheduled_date < NOW() - INTERVAL '1 day')
    );
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old completed activities (optional)
CREATE OR REPLACE FUNCTION cleanup_old_activities()
RETURNS void AS $$
BEGIN
    -- Archive activities completed more than 2 years ago
    -- This is optional and can be adjusted based on business needs
    UPDATE activities 
    SET metadata = jsonb_set(
        COALESCE(metadata, '{}'),
        '{archived}',
        'true'
    )
    WHERE status = 'completed'
    AND completed_date < NOW() - INTERVAL '2 years'
    AND NOT (metadata ? 'archived');
END;
$$ LANGUAGE plpgsql;

-- Create triggers

-- Trigger to automatically update last_modified timestamp
CREATE TRIGGER update_activity_templates_modified
    BEFORE UPDATE ON activity_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_activity_modified();

CREATE TRIGGER update_activities_modified
    BEFORE UPDATE ON activities
    FOR EACH ROW
    EXECUTE FUNCTION update_activity_modified();

-- Create views for common queries

-- View for activity timeline with contact information
CREATE VIEW activity_timeline_view AS
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

-- View for user dashboard activities
CREATE VIEW user_dashboard_activities AS
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

-- Grant necessary permissions (adjust based on your user roles)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON activity_templates TO app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON activities TO app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON activity_participants TO app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON activity_reminders TO app_user;
-- GRANT SELECT ON activity_timeline_view TO app_user;
-- GRANT SELECT ON user_dashboard_activities TO app_user;

-- Add helpful comments
COMMENT ON TABLE activity_templates IS 'Templates for creating standardized activities';
COMMENT ON TABLE activities IS 'Main activities table for tracking all customer interactions and tasks';
COMMENT ON TABLE activity_participants IS 'Participants in activities (team members, customers, etc.)';
COMMENT ON TABLE activity_reminders IS 'Reminders and notifications for activities';
COMMENT ON VIEW activity_timeline_view IS 'Comprehensive view of activities with contact information';
COMMENT ON VIEW user_dashboard_activities IS 'User dashboard view showing prioritized activities';

-- Insert some default activity templates
INSERT INTO activity_templates (business_id, name, description, activity_type, default_duration, default_reminders, created_by) 
SELECT 
    b.id,
    'Initial Consultation Call',
    'First call with prospective customer to understand their needs',
    'interaction',
    60,
    '[{"minutes_before": 15, "type": "notification", "message": "Consultation call starting soon"}]',
    'system'
FROM businesses b
WHERE NOT EXISTS (
    SELECT 1 FROM activity_templates 
    WHERE business_id = b.id AND name = 'Initial Consultation Call'
);

INSERT INTO activity_templates (business_id, name, description, activity_type, default_duration, default_reminders, created_by) 
SELECT 
    b.id,
    'Send Proposal',
    'Prepare and send proposal to customer',
    'task',
    120,
    '[{"minutes_before": 60, "type": "notification", "message": "Time to prepare proposal"}]',
    'system'
FROM businesses b
WHERE NOT EXISTS (
    SELECT 1 FROM activity_templates 
    WHERE business_id = b.id AND name = 'Send Proposal'
);

INSERT INTO activity_templates (business_id, name, description, activity_type, default_duration, default_reminders, created_by) 
SELECT 
    b.id,
    'Follow-up Call',
    'Follow up with customer after proposal or service',
    'interaction',
    30,
    '[{"minutes_before": 15, "type": "notification", "message": "Follow-up call reminder"}]',
    'system'
FROM businesses b
WHERE NOT EXISTS (
    SELECT 1 FROM activity_templates 
    WHERE business_id = b.id AND name = 'Follow-up Call'
);

INSERT INTO activity_templates (business_id, name, description, activity_type, default_duration, default_reminders, created_by) 
SELECT 
    b.id,
    'Service Reminder',
    'Remind customer about upcoming service or maintenance',
    'reminder',
    15,
    '[{"minutes_before": 1440, "type": "notification", "message": "Service reminder to be sent"}]',
    'system'
FROM businesses b
WHERE NOT EXISTS (
    SELECT 1 FROM activity_templates 
    WHERE business_id = b.id AND name = 'Service Reminder'
);

-- Create a scheduled job to update overdue activities (requires pg_cron extension)
-- This is optional and requires the pg_cron extension to be installed
-- SELECT cron.schedule('update-overdue-activities', '0 1 * * *', 'SELECT update_overdue_activities();');

COMMIT; 