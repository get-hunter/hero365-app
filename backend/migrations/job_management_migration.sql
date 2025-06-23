-- Job Management System Migration
-- Hero365 - Comprehensive job/project management for home services

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
    job_number VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    job_type VARCHAR(20) NOT NULL CHECK (job_type IN (
        'service', 'installation', 'maintenance', 'repair', 
        'inspection', 'consultation', 'emergency', 'project', 'other'
    )),
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN (
        'draft', 'quoted', 'scheduled', 'in_progress', 'on_hold', 
        'completed', 'cancelled', 'invoiced', 'paid'
    )),
    priority VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (priority IN (
        'low', 'medium', 'high', 'urgent', 'emergency'
    )),
    source VARCHAR(20) NOT NULL DEFAULT 'other' CHECK (source IN (
        'website', 'referral', 'repeat_customer', 'marketing', 
        'cold_call', 'emergency_call', 'partner', 'walk_in', 'other'
    )),
    
    -- Location information (JSONB for flexibility)
    job_address JSONB NOT NULL,
    
    -- Scheduling
    scheduled_start TIMESTAMP WITH TIME ZONE,
    scheduled_end TIMESTAMP WITH TIME ZONE,
    actual_start TIMESTAMP WITH TIME ZONE,
    actual_end TIMESTAMP WITH TIME ZONE,
    
    -- Assignment (array of user IDs)
    assigned_to TEXT[] DEFAULT '{}',
    created_by TEXT NOT NULL,
    
    -- Time tracking (JSONB for flexibility)
    time_tracking JSONB DEFAULT '{}',
    
    -- Cost estimation (JSONB for flexibility)
    cost_estimate JSONB DEFAULT '{}',
    
    -- Metadata
    tags TEXT[] DEFAULT '{}',
    notes TEXT,
    internal_notes TEXT,
    customer_requirements TEXT,
    completion_notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    
    -- Audit fields
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_date TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    UNIQUE(business_id, job_number),
    CHECK (scheduled_end IS NULL OR scheduled_start IS NULL OR scheduled_end > scheduled_start),
    CHECK (actual_end IS NULL OR actual_start IS NULL OR actual_end > actual_start)
);

-- Create job activities table for tracking job history
CREATE TABLE IF NOT EXISTS job_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN (
        'created', 'updated', 'status_changed', 'assigned', 'unassigned',
        'started', 'paused', 'resumed', 'completed', 'cancelled',
        'note_added', 'file_attached', 'time_logged', 'cost_updated'
    )),
    description TEXT NOT NULL,
    old_values JSONB DEFAULT '{}',
    new_values JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create job notes table for detailed notes tracking
CREATE TABLE IF NOT EXISTS job_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    note_type VARCHAR(20) NOT NULL DEFAULT 'general' CHECK (note_type IN (
        'general', 'customer', 'internal', 'technical', 'follow_up'
    )),
    title VARCHAR(255),
    content TEXT NOT NULL,
    is_private BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create job attachments table for file management
CREATE TABLE IF NOT EXISTS job_attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    mime_type VARCHAR(100),
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create job templates table for recurring job types
CREATE TABLE IF NOT EXISTS job_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    job_type VARCHAR(20) NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    estimated_duration_hours DECIMAL(10,2),
    default_cost_estimate JSONB DEFAULT '{}',
    default_tags TEXT[] DEFAULT '{}',
    template_data JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_by TEXT NOT NULL,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(business_id, name)
);

-- Create indexes for performance optimization

-- Primary lookup indexes
CREATE INDEX IF NOT EXISTS idx_jobs_business_id ON jobs(business_id);
CREATE INDEX IF NOT EXISTS idx_jobs_contact_id ON jobs(contact_id);
CREATE INDEX IF NOT EXISTS idx_jobs_job_number ON jobs(business_id, job_number);
CREATE INDEX IF NOT EXISTS idx_jobs_created_by ON jobs(created_by);

-- Status and type indexes
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(business_id, status);
CREATE INDEX IF NOT EXISTS idx_jobs_job_type ON jobs(business_id, job_type);
CREATE INDEX IF NOT EXISTS idx_jobs_priority ON jobs(business_id, priority);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(business_id, source);

-- Assignment and scheduling indexes
CREATE INDEX IF NOT EXISTS idx_jobs_assigned_to ON jobs USING GIN(assigned_to);
CREATE INDEX IF NOT EXISTS idx_jobs_scheduled_start ON jobs(business_id, scheduled_start);
CREATE INDEX IF NOT EXISTS idx_jobs_scheduled_end ON jobs(business_id, scheduled_end);
CREATE INDEX IF NOT EXISTS idx_jobs_actual_start ON jobs(business_id, actual_start);
CREATE INDEX IF NOT EXISTS idx_jobs_actual_end ON jobs(business_id, actual_end);

-- Date-based indexes
CREATE INDEX IF NOT EXISTS idx_jobs_created_date ON jobs(business_id, created_date);
CREATE INDEX IF NOT EXISTS idx_jobs_last_modified ON jobs(business_id, last_modified);
CREATE INDEX IF NOT EXISTS idx_jobs_completed_date ON jobs(business_id, completed_date);

-- Tag and search indexes
CREATE INDEX IF NOT EXISTS idx_jobs_tags ON jobs USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_jobs_title_search ON jobs USING GIN(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_jobs_description_search ON jobs USING GIN(to_tsvector('english', description));

-- JSONB indexes for flexible queries
CREATE INDEX IF NOT EXISTS idx_jobs_job_address ON jobs USING GIN(job_address);
CREATE INDEX IF NOT EXISTS idx_jobs_time_tracking ON jobs USING GIN(time_tracking);
CREATE INDEX IF NOT EXISTS idx_jobs_cost_estimate ON jobs USING GIN(cost_estimate);
CREATE INDEX IF NOT EXISTS idx_jobs_custom_fields ON jobs USING GIN(custom_fields);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_jobs_status_priority ON jobs(business_id, status, priority);
CREATE INDEX IF NOT EXISTS idx_jobs_type_status ON jobs(business_id, job_type, status);
CREATE INDEX IF NOT EXISTS idx_jobs_assigned_status ON jobs USING GIN(assigned_to) WHERE status IN ('scheduled', 'in_progress');
-- Index for overdue job queries (without NOW() function)
CREATE INDEX IF NOT EXISTS idx_jobs_scheduled_end_active ON jobs(business_id, scheduled_end) WHERE status IN ('scheduled', 'in_progress');

-- Activity table indexes
CREATE INDEX IF NOT EXISTS idx_job_activities_job_id ON job_activities(job_id);
CREATE INDEX IF NOT EXISTS idx_job_activities_business_id ON job_activities(business_id);
CREATE INDEX IF NOT EXISTS idx_job_activities_user_id ON job_activities(user_id);
CREATE INDEX IF NOT EXISTS idx_job_activities_type ON job_activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_job_activities_created_date ON job_activities(created_date);

-- Notes table indexes
CREATE INDEX IF NOT EXISTS idx_job_notes_job_id ON job_notes(job_id);
CREATE INDEX IF NOT EXISTS idx_job_notes_business_id ON job_notes(business_id);
CREATE INDEX IF NOT EXISTS idx_job_notes_user_id ON job_notes(user_id);
CREATE INDEX IF NOT EXISTS idx_job_notes_note_type ON job_notes(note_type);
CREATE INDEX IF NOT EXISTS idx_job_notes_created_date ON job_notes(created_date);

-- Attachments table indexes
CREATE INDEX IF NOT EXISTS idx_job_attachments_job_id ON job_attachments(job_id);
CREATE INDEX IF NOT EXISTS idx_job_attachments_business_id ON job_attachments(business_id);
CREATE INDEX IF NOT EXISTS idx_job_attachments_user_id ON job_attachments(user_id);
CREATE INDEX IF NOT EXISTS idx_job_attachments_file_type ON job_attachments(file_type);

-- Templates table indexes
CREATE INDEX IF NOT EXISTS idx_job_templates_business_id ON job_templates(business_id);
CREATE INDEX IF NOT EXISTS idx_job_templates_job_type ON job_templates(business_id, job_type);
CREATE INDEX IF NOT EXISTS idx_job_templates_active ON job_templates(business_id, is_active);

-- Create triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_job_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_job_last_modified
    BEFORE UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_job_last_modified();

CREATE TRIGGER trigger_update_job_notes_last_modified
    BEFORE UPDATE ON job_notes
    FOR EACH ROW
    EXECUTE FUNCTION update_job_last_modified();

CREATE TRIGGER trigger_update_job_templates_last_modified
    BEFORE UPDATE ON job_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_job_last_modified();

-- Create trigger for automatic job activity logging
CREATE OR REPLACE FUNCTION log_job_activity()
RETURNS TRIGGER AS $$
BEGIN
    -- Log job creation
    IF TG_OP = 'INSERT' THEN
        INSERT INTO job_activities (job_id, business_id, user_id, activity_type, description, new_values)
        VALUES (NEW.id, NEW.business_id, NEW.created_by, 'created', 
                'Job created: ' || NEW.title, to_jsonb(NEW));
        RETURN NEW;
    END IF;
    
    -- Log job updates
    IF TG_OP = 'UPDATE' THEN
        -- Log status changes
        IF OLD.status != NEW.status THEN
            INSERT INTO job_activities (job_id, business_id, user_id, activity_type, description, old_values, new_values)
            VALUES (NEW.id, NEW.business_id, NEW.created_by, 'status_changed',
                    'Status changed from ' || OLD.status || ' to ' || NEW.status,
                    jsonb_build_object('status', OLD.status),
                    jsonb_build_object('status', NEW.status));
        END IF;
        
        -- Log assignment changes
        IF OLD.assigned_to != NEW.assigned_to THEN
            INSERT INTO job_activities (job_id, business_id, user_id, activity_type, description, old_values, new_values)
            VALUES (NEW.id, NEW.business_id, NEW.created_by, 'assigned',
                    'Assignment changed',
                    jsonb_build_object('assigned_to', OLD.assigned_to),
                    jsonb_build_object('assigned_to', NEW.assigned_to));
        END IF;
        
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_job_activity
    AFTER INSERT OR UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION log_job_activity();

-- Create function for generating next job number
CREATE OR REPLACE FUNCTION get_next_job_number(p_business_id UUID, p_prefix TEXT DEFAULT 'JOB')
RETURNS TEXT AS $$
DECLARE
    next_number INTEGER;
    job_number TEXT;
BEGIN
    -- Get the highest existing job number for this business
    SELECT COALESCE(
        MAX(
            CAST(
                SUBSTRING(job_number FROM LENGTH(p_prefix || '-') + 1) AS INTEGER
            )
        ), 0
    ) + 1
    INTO next_number
    FROM jobs
    WHERE business_id = p_business_id
    AND job_number ~ ('^' || p_prefix || '-[0-9]+$');
    
    -- Format the job number
    job_number := p_prefix || '-' || LPAD(next_number::TEXT, 6, '0');
    
    RETURN job_number;
END;
$$ LANGUAGE plpgsql;

-- Create function for job statistics
CREATE OR REPLACE FUNCTION get_job_statistics(p_business_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    total_jobs INTEGER;
    jobs_by_status JSONB;
    jobs_by_type JSONB;
    jobs_by_priority JSONB;
    overdue_jobs INTEGER;
    emergency_jobs INTEGER;
    jobs_in_progress INTEGER;
    completed_this_month INTEGER;
    revenue_this_month DECIMAL;
    average_job_value DECIMAL;
BEGIN
    -- Total jobs
    SELECT COUNT(*) INTO total_jobs
    FROM jobs WHERE business_id = p_business_id;
    
    -- Jobs by status
    SELECT jsonb_object_agg(status, count)
    INTO jobs_by_status
    FROM (
        SELECT status, COUNT(*) as count
        FROM jobs
        WHERE business_id = p_business_id
        GROUP BY status
    ) s;
    
    -- Jobs by type
    SELECT jsonb_object_agg(job_type, count)
    INTO jobs_by_type
    FROM (
        SELECT job_type, COUNT(*) as count
        FROM jobs
        WHERE business_id = p_business_id
        GROUP BY job_type
    ) t;
    
    -- Jobs by priority
    SELECT jsonb_object_agg(priority, count)
    INTO jobs_by_priority
    FROM (
        SELECT priority, COUNT(*) as count
        FROM jobs
        WHERE business_id = p_business_id
        GROUP BY priority
    ) p;
    
    -- Overdue jobs
    SELECT COUNT(*) INTO overdue_jobs
    FROM jobs
    WHERE business_id = p_business_id
    AND status IN ('scheduled', 'in_progress')
    AND scheduled_end < NOW();
    
    -- Emergency jobs
    SELECT COUNT(*) INTO emergency_jobs
    FROM jobs
    WHERE business_id = p_business_id
    AND priority = 'emergency';
    
    -- Jobs in progress
    SELECT COUNT(*) INTO jobs_in_progress
    FROM jobs
    WHERE business_id = p_business_id
    AND status = 'in_progress';
    
    -- Completed this month
    SELECT COUNT(*) INTO completed_this_month
    FROM jobs
    WHERE business_id = p_business_id
    AND status = 'completed'
    AND completed_date >= DATE_TRUNC('month', NOW());
    
    -- Revenue this month (from cost estimates)
    SELECT COALESCE(SUM(
        COALESCE((cost_estimate->>'labor_cost')::DECIMAL, 0) +
        COALESCE((cost_estimate->>'material_cost')::DECIMAL, 0) +
        COALESCE((cost_estimate->>'equipment_cost')::DECIMAL, 0) +
        COALESCE((cost_estimate->>'overhead_cost')::DECIMAL, 0)
    ), 0) INTO revenue_this_month
    FROM jobs
    WHERE business_id = p_business_id
    AND status IN ('completed', 'invoiced', 'paid')
    AND completed_date >= DATE_TRUNC('month', NOW());
    
    -- Average job value
    SELECT COALESCE(AVG(
        COALESCE((cost_estimate->>'labor_cost')::DECIMAL, 0) +
        COALESCE((cost_estimate->>'material_cost')::DECIMAL, 0) +
        COALESCE((cost_estimate->>'equipment_cost')::DECIMAL, 0) +
        COALESCE((cost_estimate->>'overhead_cost')::DECIMAL, 0)
    ), 0) INTO average_job_value
    FROM jobs
    WHERE business_id = p_business_id
    AND status IN ('completed', 'invoiced', 'paid');
    
    -- Build result
    result := jsonb_build_object(
        'total_jobs', total_jobs,
        'jobs_by_status', COALESCE(jobs_by_status, '{}'::jsonb),
        'jobs_by_type', COALESCE(jobs_by_type, '{}'::jsonb),
        'jobs_by_priority', COALESCE(jobs_by_priority, '{}'::jsonb),
        'overdue_jobs', overdue_jobs,
        'emergency_jobs', emergency_jobs,
        'jobs_in_progress', jobs_in_progress,
        'completed_this_month', completed_this_month,
        'revenue_this_month', revenue_this_month,
        'average_job_value', average_job_value,
        'completion_rate', CASE WHEN total_jobs > 0 THEN 
            (SELECT COUNT(*)::DECIMAL / total_jobs * 100 
             FROM jobs 
             WHERE business_id = p_business_id AND status IN ('completed', 'invoiced', 'paid'))
            ELSE 0 END,
        'on_time_completion_rate', CASE WHEN completed_this_month > 0 THEN
            (SELECT COUNT(*)::DECIMAL / completed_this_month * 100
             FROM jobs
             WHERE business_id = p_business_id
             AND status = 'completed'
             AND completed_date >= DATE_TRUNC('month', NOW())
             AND (actual_end IS NULL OR scheduled_end IS NULL OR actual_end <= scheduled_end))
            ELSE 0 END
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Create sample job templates for common home service jobs
INSERT INTO job_templates (business_id, name, description, job_type, priority, estimated_duration_hours, default_cost_estimate, default_tags, template_data, created_by)
SELECT 
    b.id,
    template.name,
    template.description,
    template.job_type,
    template.priority,
    template.estimated_duration_hours,
    template.default_cost_estimate,
    template.default_tags,
    template.template_data,
    'system'
FROM businesses b
CROSS JOIN (
    VALUES
    ('HVAC Maintenance', 'Regular HVAC system maintenance and inspection', 'maintenance', 'medium', 2.0, 
     '{"labor_cost": 150, "material_cost": 50, "equipment_cost": 0, "overhead_cost": 25}'::jsonb,
     ARRAY['hvac', 'maintenance', 'routine'],
     '{"checklist": ["Check filters", "Inspect ductwork", "Test thermostat", "Clean coils"]}'::jsonb),
    
    ('Plumbing Repair', 'General plumbing repair service', 'repair', 'high', 1.5,
     '{"labor_cost": 120, "material_cost": 75, "equipment_cost": 0, "overhead_cost": 20}'::jsonb,
     ARRAY['plumbing', 'repair', 'emergency'],
     '{"common_issues": ["Leaky faucet", "Clogged drain", "Running toilet", "Low water pressure"]}'::jsonb),
    
    ('Electrical Installation', 'Electrical fixture or outlet installation', 'installation', 'high', 3.0,
     '{"labor_cost": 200, "material_cost": 100, "equipment_cost": 25, "overhead_cost": 35}'::jsonb,
     ARRAY['electrical', 'installation', 'safety'],
     '{"safety_requirements": ["Turn off breaker", "Test circuits", "Use proper PPE"]}'::jsonb),
    
    ('Home Inspection', 'Comprehensive home inspection service', 'inspection', 'medium', 4.0,
     '{"labor_cost": 300, "material_cost": 25, "equipment_cost": 50, "overhead_cost": 40}'::jsonb,
     ARRAY['inspection', 'assessment', 'report'],
     '{"inspection_areas": ["Electrical", "Plumbing", "HVAC", "Structural", "Roofing"]}'::jsonb),
    
    ('Emergency Service Call', 'Emergency service response', 'emergency', 'emergency', 1.0,
     '{"labor_cost": 150, "material_cost": 0, "equipment_cost": 0, "overhead_cost": 25}'::jsonb,
     ARRAY['emergency', 'urgent', '24/7'],
     '{"response_time": "Within 2 hours", "availability": "24/7"}'::jsonb)
) AS template(name, description, job_type, priority, estimated_duration_hours, default_cost_estimate, default_tags, template_data)
ON CONFLICT (business_id, name) DO NOTHING;

-- Add comments for documentation
COMMENT ON TABLE jobs IS 'Core jobs table for Hero365 job management system';
COMMENT ON TABLE job_activities IS 'Activity log for job changes and updates';
COMMENT ON TABLE job_notes IS 'Detailed notes and comments for jobs';
COMMENT ON TABLE job_attachments IS 'File attachments associated with jobs';
COMMENT ON TABLE job_templates IS 'Reusable job templates for common service types';

COMMENT ON COLUMN jobs.job_address IS 'JSONB containing address details: street_address, city, state, postal_code, country, latitude, longitude, access_notes';
COMMENT ON COLUMN jobs.time_tracking IS 'JSONB containing time tracking: estimated_hours, actual_hours, billable_hours, start_time, end_time, break_time_minutes';
COMMENT ON COLUMN jobs.cost_estimate IS 'JSONB containing cost breakdown: labor_cost, material_cost, equipment_cost, overhead_cost, markup_percentage, tax_percentage, discount_amount';
COMMENT ON COLUMN jobs.assigned_to IS 'Array of user IDs assigned to this job';
COMMENT ON COLUMN jobs.tags IS 'Array of tags for categorization and search';
COMMENT ON COLUMN jobs.custom_fields IS 'JSONB for business-specific custom fields'; 