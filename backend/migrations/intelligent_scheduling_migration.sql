-- Intelligent Scheduling System Migration
-- Creates all tables needed for the intelligent job scheduling system
-- This includes user capabilities, skills, availability, and calendar management

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- User Capabilities table (main aggregate)
CREATE TABLE IF NOT EXISTS user_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL, -- Supabase Auth user ID
    
    -- Location and mobility
    home_base_address TEXT,
    home_base_latitude DECIMAL(10, 8),
    home_base_longitude DECIMAL(11, 8),
    vehicle_type VARCHAR(50),
    has_vehicle BOOLEAN DEFAULT TRUE,
    
    -- Legacy scheduling preferences (maintained for backward compatibility)
    preferred_start_time TIME,
    preferred_end_time TIME,
    min_time_between_jobs_minutes INTEGER DEFAULT 30 CHECK (min_time_between_jobs_minutes >= 0),
    max_commute_time_minutes INTEGER DEFAULT 60 CHECK (max_commute_time_minutes > 0),
    
    -- Performance metrics
    average_job_rating DECIMAL(3,2) CHECK (average_job_rating >= 0 AND average_job_rating <= 5),
    completion_rate DECIMAL(5,2) CHECK (completion_rate >= 0 AND completion_rate <= 100),
    punctuality_score DECIMAL(5,2) CHECK (punctuality_score >= 0 AND punctuality_score <= 100),
    
    -- Link to working hours template
    working_hours_template_id UUID,
    
    -- Metadata
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    UNIQUE(business_id, user_id),
    CHECK ((home_base_latitude IS NULL) = (home_base_longitude IS NULL))
);

-- Skills table
CREATE TABLE IF NOT EXISTS user_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_capabilities_id UUID NOT NULL REFERENCES user_capabilities(id) ON DELETE CASCADE,
    skill_id VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN (
        'technical', 'mechanical', 'electrical', 'plumbing', 'hvac',
        'carpentry', 'painting', 'cleaning', 'security', 'administrative'
    )),
    level VARCHAR(20) NOT NULL CHECK (level IN (
        'beginner', 'intermediate', 'advanced', 'expert', 'master'
    )),
    years_experience DECIMAL(4,2) NOT NULL CHECK (years_experience >= 0),
    last_used TIMESTAMP WITH TIME ZONE,
    proficiency_score DECIMAL(5,2) CHECK (proficiency_score >= 0 AND proficiency_score <= 100),
    certification_required BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_capabilities_id, skill_id)
);

-- Certifications table
CREATE TABLE IF NOT EXISTS user_certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_capabilities_id UUID NOT NULL REFERENCES user_capabilities(id) ON DELETE CASCADE,
    certification_id VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    issuing_authority VARCHAR(200) NOT NULL,
    issue_date TIMESTAMP WITH TIME ZONE NOT NULL,
    expiry_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN (
        'active', 'expired', 'pending', 'suspended'
    )),
    verification_number VARCHAR(100),
    renewal_required BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_capabilities_id, certification_id),
    CHECK (expiry_date IS NULL OR expiry_date > issue_date)
);

-- Availability Windows table
CREATE TABLE IF NOT EXISTS availability_windows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_capabilities_id UUID NOT NULL REFERENCES user_capabilities(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    availability_type VARCHAR(20) DEFAULT 'regular' CHECK (availability_type IN (
        'regular', 'flexible', 'on_call', 'project_based'
    )),
    max_hours_per_day DECIMAL(4,2) CHECK (max_hours_per_day > 0),
    break_duration_minutes INTEGER DEFAULT 30 CHECK (break_duration_minutes >= 0 AND break_duration_minutes <= 120),
    
    -- Metadata
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CHECK (end_time > start_time)
);

-- Workload Capacity table
CREATE TABLE IF NOT EXISTS workload_capacity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_capabilities_id UUID NOT NULL REFERENCES user_capabilities(id) ON DELETE CASCADE,
    max_concurrent_jobs INTEGER DEFAULT 3 CHECK (max_concurrent_jobs > 0),
    max_daily_hours DECIMAL(4,2) DEFAULT 8.0 CHECK (max_daily_hours > 0),
    max_weekly_hours DECIMAL(5,2) DEFAULT 40.0 CHECK (max_weekly_hours > 0),
    preferred_job_types TEXT[] DEFAULT '{}',
    max_travel_distance_km DECIMAL(6,2) DEFAULT 50.0 CHECK (max_travel_distance_km >= 0),
    overtime_willingness BOOLEAN DEFAULT FALSE,
    emergency_availability BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_capabilities_id)
);

-- Working Hours Templates
CREATE TABLE IF NOT EXISTS working_hours_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Weekly schedule
    monday_start TIME,
    monday_end TIME,
    tuesday_start TIME,
    tuesday_end TIME,
    wednesday_start TIME,
    wednesday_end TIME,
    thursday_start TIME,
    thursday_end TIME,
    friday_start TIME,
    friday_end TIME,
    saturday_start TIME,
    saturday_end TIME,
    sunday_start TIME,
    sunday_end TIME,
    
    -- Break configurations
    break_duration_minutes INTEGER DEFAULT 30 CHECK (break_duration_minutes >= 0 AND break_duration_minutes <= 120),
    lunch_start_time TIME,
    lunch_duration_minutes INTEGER DEFAULT 60 CHECK (lunch_duration_minutes >= 0 AND lunch_duration_minutes <= 180),
    
    -- Flexibility settings
    allows_flexible_start BOOLEAN DEFAULT FALSE,
    flexible_start_window_minutes INTEGER DEFAULT 30 CHECK (flexible_start_window_minutes >= 0 AND flexible_start_window_minutes <= 120),
    allows_overtime BOOLEAN DEFAULT FALSE,
    max_overtime_hours_per_day DECIMAL(3,1) DEFAULT 2.0 CHECK (max_overtime_hours_per_day >= 0 AND max_overtime_hours_per_day <= 8),
    
    -- Metadata
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Calendar Events
CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Event details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) DEFAULT 'work_schedule' CHECK (event_type IN (
        'work_schedule', 'time_off', 'break', 'meeting', 'training', 'personal'
    )),
    
    -- Time information
    start_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    end_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    is_all_day BOOLEAN DEFAULT FALSE,
    timezone VARCHAR(100) DEFAULT 'UTC',
    
    -- Recurrence
    recurrence_type VARCHAR(20) DEFAULT 'none' CHECK (recurrence_type IN (
        'none', 'daily', 'weekly', 'biweekly', 'monthly', 'custom'
    )),
    recurrence_end_date DATE,
    recurrence_count INTEGER CHECK (recurrence_count > 0),
    recurrence_interval INTEGER DEFAULT 1 CHECK (recurrence_interval > 0),
    recurrence_days_of_week INTEGER[] DEFAULT '{}',
    
    -- Availability impact
    blocks_scheduling BOOLEAN DEFAULT TRUE,
    allows_emergency_override BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT calendar_events_end_after_start CHECK (end_datetime > start_datetime),
    CONSTRAINT calendar_events_recurrence_days_valid CHECK (
        array_length(recurrence_days_of_week, 1) IS NULL OR 
        (recurrence_days_of_week <@ ARRAY[0,1,2,3,4,5,6])
    )
);

-- Time Off Requests
CREATE TABLE IF NOT EXISTS time_off_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Request details
    time_off_type VARCHAR(20) NOT NULL CHECK (time_off_type IN (
        'vacation', 'sick_leave', 'personal', 'holiday', 'training', 'emergency', 'unpaid'
    )),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,
    notes TEXT,
    
    -- Approval workflow
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'approved', 'denied', 'cancelled'
    )),
    requested_by TEXT NOT NULL,
    approved_by TEXT,
    approval_date TIMESTAMP WITH TIME ZONE,
    denial_reason TEXT,
    
    -- Impact on scheduling
    affects_scheduling BOOLEAN DEFAULT TRUE,
    emergency_contact_allowed BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT time_off_end_after_start CHECK (end_date >= start_date),
    CONSTRAINT time_off_denial_reason_required CHECK (
        (status = 'denied' AND denial_reason IS NOT NULL) OR status != 'denied'
    )
);

-- Calendar Preferences
CREATE TABLE IF NOT EXISTS calendar_preferences (
    user_id TEXT NOT NULL,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Time zone and locale
    timezone VARCHAR(100) DEFAULT 'UTC',
    date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
    time_format VARCHAR(5) DEFAULT '24h' CHECK (time_format IN ('12h', '24h')),
    week_start_day INTEGER DEFAULT 0 CHECK (week_start_day >= 0 AND week_start_day <= 6),
    
    -- Scheduling preferences
    preferred_working_hours_template_id UUID REFERENCES working_hours_templates(id) ON DELETE SET NULL,
    min_time_between_jobs_minutes INTEGER DEFAULT 30 CHECK (min_time_between_jobs_minutes >= 0),
    max_commute_time_minutes INTEGER DEFAULT 60 CHECK (max_commute_time_minutes >= 0),
    allows_back_to_back_jobs BOOLEAN DEFAULT FALSE,
    requires_prep_time_minutes INTEGER DEFAULT 15 CHECK (requires_prep_time_minutes >= 0),
    
    -- Notification preferences
    job_reminder_minutes_before INTEGER[] DEFAULT '{60,15}',
    schedule_change_notifications BOOLEAN DEFAULT TRUE,
    new_job_notifications BOOLEAN DEFAULT TRUE,
    cancellation_notifications BOOLEAN DEFAULT TRUE,
    
    -- Availability preferences
    auto_accept_jobs_in_hours BOOLEAN DEFAULT FALSE,
    auto_decline_outside_hours BOOLEAN DEFAULT TRUE,
    emergency_availability_outside_hours BOOLEAN DEFAULT FALSE,
    weekend_availability BOOLEAN DEFAULT FALSE,
    holiday_availability BOOLEAN DEFAULT FALSE,
    
    -- Buffer times
    travel_buffer_percentage DECIMAL(3,2) DEFAULT 1.20 CHECK (travel_buffer_percentage >= 1.0),
    job_buffer_minutes INTEGER DEFAULT 15 CHECK (job_buffer_minutes >= 0),
    
    -- Metadata
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (user_id, business_id)
);

-- Add foreign key constraint to user_capabilities for working hours template
ALTER TABLE user_capabilities 
ADD CONSTRAINT fk_user_capabilities_working_hours_template 
    FOREIGN KEY (working_hours_template_id) REFERENCES working_hours_templates(id) ON DELETE SET NULL;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_capabilities_business_id ON user_capabilities(business_id);
CREATE INDEX IF NOT EXISTS idx_user_capabilities_user_id ON user_capabilities(user_id);
CREATE INDEX IF NOT EXISTS idx_user_capabilities_active ON user_capabilities(is_active) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_user_skills_capabilities_id ON user_skills(user_capabilities_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_category ON user_skills(category);
CREATE INDEX IF NOT EXISTS idx_user_skills_level ON user_skills(level);
CREATE INDEX IF NOT EXISTS idx_user_skills_skill_id ON user_skills(skill_id);

CREATE INDEX IF NOT EXISTS idx_user_certifications_capabilities_id ON user_certifications(user_capabilities_id);
CREATE INDEX IF NOT EXISTS idx_user_certifications_status ON user_certifications(status);
CREATE INDEX IF NOT EXISTS idx_user_certifications_expiry ON user_certifications(expiry_date) WHERE expiry_date IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_availability_windows_capabilities_id ON availability_windows(user_capabilities_id);
CREATE INDEX IF NOT EXISTS idx_availability_windows_day ON availability_windows(day_of_week);

CREATE INDEX IF NOT EXISTS idx_workload_capacity_capabilities_id ON workload_capacity(user_capabilities_id);

CREATE INDEX IF NOT EXISTS idx_calendar_events_user_business ON calendar_events(user_id, business_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_datetime ON calendar_events(start_datetime, end_datetime);
CREATE INDEX IF NOT EXISTS idx_calendar_events_recurrence ON calendar_events(recurrence_type) WHERE recurrence_type != 'none';
CREATE INDEX IF NOT EXISTS idx_calendar_events_active ON calendar_events(is_active) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_time_off_user_business ON time_off_requests(user_id, business_id);
CREATE INDEX IF NOT EXISTS idx_time_off_dates ON time_off_requests(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_time_off_status ON time_off_requests(status);
CREATE INDEX IF NOT EXISTS idx_time_off_pending ON time_off_requests(business_id, status) WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_working_hours_templates_active ON working_hours_templates(is_active) WHERE is_active = TRUE;

-- Triggers for updating last_modified timestamps
CREATE OR REPLACE FUNCTION update_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_capabilities_last_modified
    BEFORE UPDATE ON user_capabilities
    FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_user_skills_last_modified
    BEFORE UPDATE ON user_skills
    FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_user_certifications_last_modified
    BEFORE UPDATE ON user_certifications
    FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_availability_windows_last_modified
    BEFORE UPDATE ON availability_windows
    FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_workload_capacity_last_modified
    BEFORE UPDATE ON workload_capacity
    FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_working_hours_templates_last_modified
    BEFORE UPDATE ON working_hours_templates
    FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_calendar_events_last_modified
    BEFORE UPDATE ON calendar_events
    FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_time_off_requests_last_modified
    BEFORE UPDATE ON time_off_requests
    FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_calendar_preferences_last_modified
    BEFORE UPDATE ON calendar_preferences
    FOR EACH ROW EXECUTE FUNCTION update_last_modified();

-- Insert default working hours templates
INSERT INTO working_hours_templates (name, description, 
    monday_start, monday_end, tuesday_start, tuesday_end, wednesday_start, wednesday_end,
    thursday_start, thursday_end, friday_start, friday_end, saturday_start, saturday_end,
    sunday_start, sunday_end, break_duration_minutes, lunch_start_time, lunch_duration_minutes,
    allows_flexible_start, flexible_start_window_minutes) 
VALUES 
    ('Standard Business Hours', 'Monday to Friday, 9 AM to 5 PM',
     '09:00:00', '17:00:00', '09:00:00', '17:00:00', '09:00:00', '17:00:00',
     '09:00:00', '17:00:00', '09:00:00', '17:00:00', NULL, NULL,
     NULL, NULL, 30, '12:00:00', 60, TRUE, 30),
    
    ('Extended Hours', 'Monday to Friday, 8 AM to 6 PM',
     '08:00:00', '18:00:00', '08:00:00', '18:00:00', '08:00:00', '18:00:00',
     '08:00:00', '18:00:00', '08:00:00', '18:00:00', NULL, NULL,
     NULL, NULL, 30, '12:00:00', 60, TRUE, 30),
    
    ('Part-time Morning', 'Monday to Friday, 9 AM to 1 PM',
     '09:00:00', '13:00:00', '09:00:00', '13:00:00', '09:00:00', '13:00:00',
     '09:00:00', '13:00:00', '09:00:00', '13:00:00', NULL, NULL,
     NULL, NULL, 15, NULL, 0, FALSE, 0),
    
    ('Part-time Afternoon', 'Monday to Friday, 1 PM to 5 PM',
     '13:00:00', '17:00:00', '13:00:00', '17:00:00', '13:00:00', '17:00:00',
     '13:00:00', '17:00:00', '13:00:00', '17:00:00', NULL, NULL,
     NULL, NULL, 15, NULL, 0, FALSE, 0),
    
    ('Weekend Service', 'Saturday and Sunday, 10 AM to 4 PM',
     NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
     '10:00:00', '16:00:00', '10:00:00', '16:00:00',
     30, '13:00:00', 60, FALSE, 0),
    
    ('Flexible Schedule', 'Monday to Friday, flexible 8-hour shifts',
     '08:00:00', '18:00:00', '08:00:00', '18:00:00', '08:00:00', '18:00:00',
     '08:00:00', '18:00:00', '08:00:00', '18:00:00', NULL, NULL,
     NULL, NULL, 30, '12:00:00', 60, TRUE, 120)
ON CONFLICT DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE user_capabilities IS 'Core user capabilities for intelligent job scheduling including skills, availability, and performance metrics';
COMMENT ON TABLE user_skills IS 'User skills with proficiency levels and experience tracking';
COMMENT ON TABLE user_certifications IS 'Professional certifications with expiry tracking';
COMMENT ON TABLE availability_windows IS 'User availability windows for scheduling';
COMMENT ON TABLE workload_capacity IS 'User workload capacity and preferences';
COMMENT ON TABLE working_hours_templates IS 'Templates for defining working hour patterns that can be reused across team members';
COMMENT ON TABLE calendar_events IS 'Calendar events that can block scheduling or provide additional context';
COMMENT ON TABLE time_off_requests IS 'Time off requests with approval workflow and scheduling impact';
COMMENT ON TABLE calendar_preferences IS 'User preferences for calendar behavior, notifications, and scheduling';

COMMENT ON COLUMN calendar_events.recurrence_days_of_week IS 'Array of integers 0-6 representing days of week (0=Monday, 6=Sunday)';
COMMENT ON COLUMN calendar_preferences.job_reminder_minutes_before IS 'Array of minutes before job start to send reminders';
COMMENT ON COLUMN calendar_preferences.travel_buffer_percentage IS 'Multiplier for travel time estimates (e.g., 1.2 = 20% buffer)';

-- Enable Row Level Security (RLS)
ALTER TABLE user_capabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_certifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE availability_windows ENABLE ROW LEVEL SECURITY;
ALTER TABLE workload_capacity ENABLE ROW LEVEL SECURITY;
ALTER TABLE working_hours_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE time_off_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_preferences ENABLE ROW LEVEL SECURITY;

-- RLS Policies for business isolation
CREATE POLICY "user_capabilities_business_isolation"
ON user_capabilities FOR ALL TO PUBLIC
USING (business_id IN (
    SELECT business_id FROM business_memberships 
    WHERE user_id = current_setting('app.current_user_id', true) 
    AND is_active = true
));

CREATE POLICY "user_skills_business_isolation"
ON user_skills FOR ALL TO PUBLIC
USING (user_capabilities_id IN (
    SELECT id FROM user_capabilities 
    WHERE business_id IN (
        SELECT business_id FROM business_memberships 
        WHERE user_id = current_setting('app.current_user_id', true) 
        AND is_active = true
    )
));

CREATE POLICY "user_certifications_business_isolation"
ON user_certifications FOR ALL TO PUBLIC
USING (user_capabilities_id IN (
    SELECT id FROM user_capabilities 
    WHERE business_id IN (
        SELECT business_id FROM business_memberships 
        WHERE user_id = current_setting('app.current_user_id', true) 
        AND is_active = true
    )
));

CREATE POLICY "availability_windows_business_isolation"
ON availability_windows FOR ALL TO PUBLIC
USING (user_capabilities_id IN (
    SELECT id FROM user_capabilities 
    WHERE business_id IN (
        SELECT business_id FROM business_memberships 
        WHERE user_id = current_setting('app.current_user_id', true) 
        AND is_active = true
    )
));

CREATE POLICY "workload_capacity_business_isolation"
ON workload_capacity FOR ALL TO PUBLIC
USING (user_capabilities_id IN (
    SELECT id FROM user_capabilities 
    WHERE business_id IN (
        SELECT business_id FROM business_memberships 
        WHERE user_id = current_setting('app.current_user_id', true) 
        AND is_active = true
    )
));

CREATE POLICY "working_hours_templates_public_read"
ON working_hours_templates FOR SELECT TO PUBLIC
USING (true);

CREATE POLICY "calendar_events_business_isolation"
ON calendar_events FOR ALL TO PUBLIC
USING (business_id IN (
    SELECT business_id FROM business_memberships 
    WHERE user_id = current_setting('app.current_user_id', true) 
    AND is_active = true
));

CREATE POLICY "time_off_requests_business_isolation"
ON time_off_requests FOR ALL TO PUBLIC
USING (business_id IN (
    SELECT business_id FROM business_memberships 
    WHERE user_id = current_setting('app.current_user_id', true) 
    AND is_active = true
));

CREATE POLICY "calendar_preferences_business_isolation"
ON calendar_preferences FOR ALL TO PUBLIC
USING (business_id IN (
    SELECT business_id FROM business_memberships 
    WHERE user_id = current_setting('app.current_user_id', true) 
    AND is_active = true
)); 