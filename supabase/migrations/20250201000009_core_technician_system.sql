-- =============================================
-- CORE TECHNICIAN & SKILLS MANAGEMENT SYSTEM
-- =============================================
-- Essential workforce management for service businesses
-- Depends on: businesses, users tables

-- =============================================
-- TECHNICIANS TABLE
-- =============================================

CREATE TABLE technicians (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id), -- Required link to user account
    
    -- Basic Info
    employee_id VARCHAR(50), -- Internal employee ID
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(255) GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,
    email VARCHAR(255),
    phone VARCHAR(20),
    
    -- Professional Info
    title VARCHAR(100), -- "Senior HVAC Technician"
    hire_date DATE,
    hourly_rate DECIMAL(10,2),
    overtime_rate DECIMAL(10,2),
    
    -- Scheduling Configuration
    is_active BOOLEAN DEFAULT true,
    can_be_booked BOOLEAN DEFAULT true,
    default_buffer_minutes INTEGER DEFAULT 30, -- Travel/prep time between jobs
    max_daily_hours INTEGER DEFAULT 8,
    max_weekly_hours INTEGER DEFAULT 40,
    
    -- Service Areas (JSON array of area IDs or names)
    service_areas JSONB DEFAULT '[]'::jsonb,
    
    -- Emergency Services
    emergency_available BOOLEAN DEFAULT false,
    emergency_rate_multiplier DECIMAL(3,2) DEFAULT 1.5,
    
    -- Performance Metrics
    jobs_completed INTEGER DEFAULT 0,
    average_job_rating DECIMAL(3,2) DEFAULT 0,
    on_time_percentage DECIMAL(5,2) DEFAULT 0,
    customer_satisfaction_score DECIMAL(3,2) DEFAULT 0,
    
    -- Contact & Emergency Info
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relationship VARCHAR(50),
    
    -- Employment Details
    employment_type VARCHAR(20) DEFAULT 'full_time', -- 'full_time', 'part_time', 'contractor'
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'on_leave', 'terminated'
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT technicians_business_employee_unique UNIQUE (business_id, employee_id),
    CONSTRAINT technicians_business_email_unique UNIQUE (business_id, email)
);

-- =============================================
-- SKILLS TABLE
-- =============================================

CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Skill Details
    name VARCHAR(100) NOT NULL, -- "HVAC Repair", "Electrical Installation"
    category VARCHAR(50), -- "hvac", "electrical", "plumbing", "general"
    description TEXT,
    
    -- Skill Requirements
    requires_certification BOOLEAN DEFAULT false,
    min_experience_years INTEGER DEFAULT 0,
    complexity_level VARCHAR(20) DEFAULT 'intermediate', -- 'basic', 'intermediate', 'advanced', 'expert'
    
    -- Billing
    skill_rate_multiplier DECIMAL(3,2) DEFAULT 1.0, -- Multiplier for base hourly rate
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT skills_business_name_unique UNIQUE (business_id, name)
);

-- =============================================
-- TECHNICIAN SKILLS (Many-to-Many)
-- =============================================

CREATE TABLE technician_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    technician_id UUID NOT NULL REFERENCES technicians(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    
    -- Proficiency and certification
    proficiency_level VARCHAR(20) DEFAULT 'intermediate', -- 'beginner', 'intermediate', 'advanced', 'expert'
    years_experience INTEGER DEFAULT 0,
    
    -- Certification Details
    is_certified BOOLEAN DEFAULT false,
    certification_name VARCHAR(100),
    certification_number VARCHAR(100),
    certified_date DATE,
    certification_expires DATE,
    certification_authority VARCHAR(100),
    
    -- Performance with this skill
    jobs_completed_with_skill INTEGER DEFAULT 0,
    average_rating_for_skill DECIMAL(3,2) DEFAULT 0,
    
    -- Status
    is_primary_skill BOOLEAN DEFAULT false, -- Is this one of their main skills?
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT technician_skills_unique UNIQUE (technician_id, skill_id)
);

-- =============================================
-- TIME OFF REQUESTS
-- =============================================

CREATE TABLE time_off_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    technician_id UUID NOT NULL REFERENCES technicians(id) ON DELETE CASCADE,
    
    -- Time Off Details
    request_type VARCHAR(20) NOT NULL, -- 'vacation', 'sick', 'personal', 'emergency', 'training'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    start_time TIME, -- For partial day requests
    end_time TIME, -- For partial day requests
    is_full_day BOOLEAN DEFAULT true,
    
    -- Request Information
    reason TEXT,
    notes TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'denied', 'cancelled'
    
    -- Approval
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    approval_notes TEXT,
    
    -- Metadata
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- TECHNICIAN AVAILABILITY CACHE
-- =============================================

CREATE TABLE availability_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    technician_id UUID NOT NULL REFERENCES technicians(id) ON DELETE CASCADE,
    
    -- Availability Window
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    
    -- Availability Status
    is_available BOOLEAN DEFAULT true,
    availability_type VARCHAR(20) DEFAULT 'work', -- 'work', 'break', 'lunch', 'travel', 'blocked'
    
    -- Booking Information
    is_booked BOOLEAN DEFAULT false,
    booking_id UUID, -- Reference to bookings table
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT availability_cache_unique UNIQUE (technician_id, date, start_time, end_time)
);

-- =============================================
-- TECHNICIAN CERTIFICATIONS
-- =============================================

CREATE TABLE technician_certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    technician_id UUID NOT NULL REFERENCES technicians(id) ON DELETE CASCADE,
    
    -- Certification Details
    certification_name VARCHAR(100) NOT NULL,
    certification_type VARCHAR(50), -- 'license', 'certification', 'training'
    issuing_authority VARCHAR(100),
    certification_number VARCHAR(100),
    
    -- Dates
    issue_date DATE,
    expiration_date DATE,
    renewal_date DATE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'expired', 'suspended', 'revoked'
    
    -- Files and Documentation
    certificate_file_url TEXT,
    verification_url TEXT,
    
    -- Reminders
    renewal_reminder_days INTEGER DEFAULT 30, -- Days before expiration to remind
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- INDEXES
-- =============================================

CREATE INDEX idx_technicians_business ON technicians(business_id);
CREATE INDEX idx_technicians_user ON technicians(user_id);
CREATE INDEX idx_technicians_active ON technicians(business_id, is_active);
CREATE INDEX idx_technicians_bookable ON technicians(business_id, can_be_booked);
CREATE INDEX idx_technicians_employee_id ON technicians(business_id, employee_id);
CREATE INDEX idx_technicians_email ON technicians(business_id, email);
CREATE INDEX idx_technicians_status ON technicians(status);

CREATE INDEX idx_skills_business ON skills(business_id);
CREATE INDEX idx_skills_category ON skills(business_id, category);
CREATE INDEX idx_skills_active ON skills(business_id, is_active);

CREATE INDEX idx_technician_skills_technician ON technician_skills(technician_id);
CREATE INDEX idx_technician_skills_skill ON technician_skills(skill_id);
CREATE INDEX idx_technician_skills_primary ON technician_skills(technician_id, is_primary_skill);
CREATE INDEX idx_technician_skills_certified ON technician_skills(technician_id, is_certified);

CREATE INDEX idx_time_off_requests_business ON time_off_requests(business_id);
CREATE INDEX idx_time_off_requests_technician ON time_off_requests(technician_id);
CREATE INDEX idx_time_off_requests_dates ON time_off_requests(start_date, end_date);
CREATE INDEX idx_time_off_requests_status ON time_off_requests(status);

CREATE INDEX idx_availability_cache_business ON availability_cache(business_id);
CREATE INDEX idx_availability_cache_technician ON availability_cache(technician_id);
CREATE INDEX idx_availability_cache_date ON availability_cache(date);
CREATE INDEX idx_availability_cache_available ON availability_cache(technician_id, date, is_available);

CREATE INDEX idx_technician_certifications_technician ON technician_certifications(technician_id);
CREATE INDEX idx_technician_certifications_expiration ON technician_certifications(expiration_date) WHERE status = 'active';
CREATE INDEX idx_technician_certifications_status ON technician_certifications(status);

COMMIT;
