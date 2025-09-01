-- =============================================
-- CORE PROJECT TABLES
-- =============================================
-- Jobs, projects, and activities
-- Depends on: businesses, contacts tables

-- =============================================
-- PROJECTS TABLE
-- =============================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id),
    
    -- Project Info
    project_number VARCHAR(50) UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    project_type VARCHAR(50) DEFAULT 'service', -- 'service', 'installation', 'maintenance', 'repair'
    
    -- Status & Priority
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'active', 'completed', 'cancelled', 'on_hold'
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    
    -- Dates
    start_date DATE,
    end_date DATE,
    estimated_completion DATE,
    actual_completion DATE,
    
    -- Financial
    estimated_cost DECIMAL(12,2) DEFAULT 0,
    actual_cost DECIMAL(12,2) DEFAULT 0,
    
    -- Assignment
    assigned_to UUID REFERENCES users(id),
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- JOBS TABLE (WORK ITEMS WITHIN PROJECTS)
-- =============================================

CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id),
    
    -- Job Info
    job_number VARCHAR(50) UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    job_type VARCHAR(50), -- 'repair', 'installation', 'maintenance', 'inspection'
    
    -- Status & Priority
    status VARCHAR(50) DEFAULT 'scheduled', -- 'scheduled', 'in_progress', 'completed', 'cancelled'
    priority VARCHAR(20) DEFAULT 'medium',
    
    -- Scheduling
    scheduled_date DATE,
    scheduled_start_time TIME,
    scheduled_end_time TIME,
    actual_start_time TIMESTAMPTZ,
    actual_end_time TIMESTAMPTZ,
    
    -- Location
    job_address TEXT,
    job_city VARCHAR(100),
    job_state VARCHAR(2),
    job_zip_code VARCHAR(10),
    
    -- Assignment
    assigned_to UUID REFERENCES users(id),
    
    -- Financial
    estimated_cost DECIMAL(10,2) DEFAULT 0,
    actual_cost DECIMAL(10,2) DEFAULT 0,
    
    -- Metadata
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- ACTIVITIES TABLE (TIME TRACKING)
-- =============================================

CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    
    -- Activity Info
    title VARCHAR(255) NOT NULL,
    description TEXT,
    activity_type VARCHAR(50) DEFAULT 'work', -- 'work', 'travel', 'break', 'meeting'
    
    -- Time Tracking
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    duration_minutes INTEGER, -- Calculated field
    
    -- Assignment
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'paused', 'completed'
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- BASIC INDEXES
-- =============================================

CREATE INDEX idx_projects_business ON projects(business_id);
CREATE INDEX idx_projects_contact ON projects(contact_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_assigned_to ON projects(assigned_to);
CREATE INDEX idx_projects_number ON projects(project_number);

CREATE INDEX idx_jobs_business ON jobs(business_id);
CREATE INDEX idx_jobs_project ON jobs(project_id);
CREATE INDEX idx_jobs_contact ON jobs(contact_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_assigned_to ON jobs(assigned_to);
CREATE INDEX idx_jobs_scheduled_date ON jobs(scheduled_date);

CREATE INDEX idx_activities_business ON activities(business_id);
CREATE INDEX idx_activities_project ON activities(project_id);
CREATE INDEX idx_activities_job ON activities(job_id);
CREATE INDEX idx_activities_user ON activities(user_id);
CREATE INDEX idx_activities_start_time ON activities(start_time);

COMMIT;
