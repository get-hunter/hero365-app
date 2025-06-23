-- Calendar Management Migration
-- Creates tables for comprehensive calendar and availability management

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
    user_id VARCHAR(255) NOT NULL,
    business_id UUID NOT NULL,
    
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
    user_id VARCHAR(255) NOT NULL,
    business_id UUID NOT NULL,
    
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
    requested_by VARCHAR(255) NOT NULL,
    approved_by VARCHAR(255),
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
    user_id VARCHAR(255) NOT NULL,
    business_id UUID NOT NULL,
    
    -- Time zone and locale
    timezone VARCHAR(100) DEFAULT 'UTC',
    date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
    time_format VARCHAR(5) DEFAULT '24h' CHECK (time_format IN ('12h', '24h')),
    week_start_day INTEGER DEFAULT 0 CHECK (week_start_day >= 0 AND week_start_day <= 6),
    
    -- Scheduling preferences
    preferred_working_hours_template_id UUID,
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
    
    PRIMARY KEY (user_id, business_id),
    FOREIGN KEY (preferred_working_hours_template_id) REFERENCES working_hours_templates(id) ON DELETE SET NULL
);

-- Note: user_capabilities table and working hours template link 
-- are now created in intelligent_scheduling_migration.sql

-- Indexes for performance
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
    thursday_start, thursday_end, friday_start, friday_end,
    break_duration_minutes, lunch_start_time, lunch_duration_minutes,
    allows_flexible_start, flexible_start_window_minutes) 
VALUES 
    ('Standard Business Hours', 'Monday to Friday, 9 AM to 5 PM',
     '09:00:00', '17:00:00', '09:00:00', '17:00:00', '09:00:00', '17:00:00',
     '09:00:00', '17:00:00', '09:00:00', '17:00:00',
     30, '12:00:00', 60, TRUE, 30),
    
    ('Extended Hours', 'Monday to Friday, 8 AM to 6 PM',
     '08:00:00', '18:00:00', '08:00:00', '18:00:00', '08:00:00', '18:00:00',
     '08:00:00', '18:00:00', '08:00:00', '18:00:00',
     30, '12:00:00', 60, TRUE, 30),
    
    ('Part-time Morning', 'Monday to Friday, 9 AM to 1 PM',
     '09:00:00', '13:00:00', '09:00:00', '13:00:00', '09:00:00', '13:00:00',
     '09:00:00', '13:00:00', '09:00:00', '13:00:00',
     15, NULL, 0, FALSE, 0),
    
    ('Part-time Afternoon', 'Monday to Friday, 1 PM to 5 PM',
     '13:00:00', '17:00:00', '13:00:00', '17:00:00', '13:00:00', '17:00:00',
     '13:00:00', '17:00:00', '13:00:00', '17:00:00',
     15, NULL, 0, FALSE, 0),
    
    ('Weekend Service', 'Saturday and Sunday, 10 AM to 4 PM',
     NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
     '10:00:00', '16:00:00', '10:00:00', '16:00:00',
     30, '13:00:00', 60, FALSE, 0),
    
    ('Flexible Schedule', 'Monday to Friday, flexible 8-hour shifts',
     '08:00:00', '18:00:00', '08:00:00', '18:00:00', '08:00:00', '18:00:00',
     '08:00:00', '18:00:00', '08:00:00', '18:00:00',
     30, '12:00:00', 60, TRUE, 120)
ON CONFLICT DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE working_hours_templates IS 'Templates for defining working hour patterns that can be reused across team members';
COMMENT ON TABLE calendar_events IS 'Calendar events that can block scheduling or provide additional context';
COMMENT ON TABLE time_off_requests IS 'Time off requests with approval workflow and scheduling impact';
COMMENT ON TABLE calendar_preferences IS 'User preferences for calendar behavior, notifications, and scheduling';

COMMENT ON COLUMN calendar_events.recurrence_days_of_week IS 'Array of integers 0-6 representing days of week (0=Monday, 6=Sunday)';
COMMENT ON COLUMN calendar_preferences.job_reminder_minutes_before IS 'Array of minutes before job start to send reminders';
COMMENT ON COLUMN calendar_preferences.travel_buffer_percentage IS 'Multiplier for travel time estimates (e.g., 1.2 = 20% buffer)'; 