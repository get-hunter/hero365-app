-- Booking System Schema Migration
-- Creates comprehensive booking system with availability, scheduling, and notifications

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- =====================================================
-- TECHNICIANS & SKILLS
-- =====================================================

-- Technician profiles with availability and skills
CREATE TABLE technicians (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Basic Info
    employee_id VARCHAR(50), -- Internal employee ID
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    
    -- Professional Info
    title VARCHAR(100), -- "Senior HVAC Technician"
    hire_date DATE,
    hourly_rate DECIMAL(10,2),
    
    -- Scheduling
    is_active BOOLEAN DEFAULT true,
    can_be_booked BOOLEAN DEFAULT true,
    default_buffer_minutes INTEGER DEFAULT 30, -- Travel/prep time between jobs
    max_daily_hours INTEGER DEFAULT 8,
    
    -- Service Areas (JSON array of area IDs or names)
    service_areas JSONB DEFAULT '[]'::jsonb,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT technicians_business_employee_unique UNIQUE (business_id, employee_id)
);

-- Skills that technicians can have
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    name VARCHAR(100) NOT NULL, -- "HVAC Repair", "Electrical Installation"
    category VARCHAR(50), -- "hvac", "electrical", "plumbing"
    description TEXT,
    
    -- Skill requirements
    requires_certification BOOLEAN DEFAULT false,
    min_experience_years INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT skills_business_name_unique UNIQUE (business_id, name)
);

-- Many-to-many: technicians ↔ skills
CREATE TABLE technician_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technician_id UUID NOT NULL REFERENCES technicians(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    
    -- Proficiency and certification
    proficiency_level VARCHAR(20) DEFAULT 'intermediate', -- beginner, intermediate, advanced, expert
    certified_date DATE,
    certification_expires DATE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT technician_skills_unique UNIQUE (technician_id, skill_id)
);

-- =====================================================
-- SERVICES & REQUIREMENTS
-- =====================================================

-- Bookable services (extends existing services table)
CREATE TABLE bookable_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Service Details
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100), -- Links to service categories
    description TEXT,
    
    -- Booking Configuration
    is_bookable BOOLEAN DEFAULT true,
    requires_site_visit BOOLEAN DEFAULT true,
    
    -- Duration & Scheduling
    estimated_duration_minutes INTEGER NOT NULL DEFAULT 60,
    min_duration_minutes INTEGER,
    max_duration_minutes INTEGER,
    
    -- Pricing
    base_price DECIMAL(10,2),
    price_type VARCHAR(20) DEFAULT 'fixed', -- fixed, hourly, estimate
    
    -- Requirements
    required_skills JSONB DEFAULT '[]'::jsonb, -- Array of skill IDs
    min_technicians INTEGER DEFAULT 1,
    max_technicians INTEGER DEFAULT 1,
    
    -- Lead Time
    min_lead_time_hours INTEGER DEFAULT 2, -- Minimum notice required
    max_advance_days INTEGER DEFAULT 90, -- Maximum days in advance
    
    -- Availability
    available_days JSONB DEFAULT '[1,2,3,4,5]'::jsonb, -- 1=Monday, 7=Sunday
    available_times JSONB DEFAULT '{"start": "08:00", "end": "17:00"}'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT bookable_services_business_name_unique UNIQUE (business_id, name)
);

-- =====================================================
-- BUSINESS HOURS & AVAILABILITY
-- =====================================================

-- Business operating hours by location and day
CREATE TABLE business_hours (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    location_id UUID REFERENCES business_locations(id) ON DELETE CASCADE,
    
    -- Day of week (1=Monday, 7=Sunday)
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 1 AND day_of_week <= 7),
    
    -- Hours
    is_open BOOLEAN DEFAULT true,
    open_time TIME,
    close_time TIME,
    
    -- Breaks
    lunch_start TIME,
    lunch_end TIME,
    
    -- Special handling
    is_emergency_only BOOLEAN DEFAULT false, -- Sunday emergency only
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT business_hours_unique UNIQUE (business_id, location_id, day_of_week)
);

-- Technician time off and unavailability
CREATE TABLE time_off (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technician_id UUID NOT NULL REFERENCES technicians(id) ON DELETE CASCADE,
    
    -- Time Range
    start_at TIMESTAMPTZ NOT NULL,
    end_at TIMESTAMPTZ NOT NULL,
    
    -- Type
    type VARCHAR(50) NOT NULL, -- vacation, sick, training, lunch, break
    reason VARCHAR(200),
    
    -- Status
    status VARCHAR(20) DEFAULT 'approved', -- pending, approved, denied
    is_recurring BOOLEAN DEFAULT false,
    recurrence_pattern JSONB, -- For recurring breaks/lunch
    
    -- Approval
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT time_off_valid_range CHECK (end_at > start_at),
    -- Prevent overlapping time off for same technician
    EXCLUDE USING gist (
        technician_id WITH =,
        tstzrange(start_at, end_at) WITH &&
    ) WHERE (status = 'approved')
);

-- =====================================================
-- BOOKINGS & APPOINTMENTS
-- =====================================================

-- Customer booking requests and appointments
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- External Reference
    booking_number VARCHAR(50) UNIQUE, -- Human-readable: BK-2025-001234
    
    -- Service Details
    service_id UUID NOT NULL REFERENCES bookable_services(id),
    service_name VARCHAR(200) NOT NULL, -- Snapshot for history
    estimated_duration_minutes INTEGER NOT NULL,
    
    -- Scheduling
    requested_at TIMESTAMPTZ NOT NULL, -- When customer wants service
    scheduled_at TIMESTAMPTZ, -- Confirmed appointment time
    completed_at TIMESTAMPTZ,
    
    -- Assignment
    primary_technician_id UUID REFERENCES technicians(id),
    additional_technicians JSONB DEFAULT '[]'::jsonb, -- Array of technician IDs
    
    -- Customer Information
    customer_name VARCHAR(200) NOT NULL,
    customer_email VARCHAR(255),
    customer_phone VARCHAR(20) NOT NULL,
    
    -- Service Address
    service_address TEXT NOT NULL,
    service_city VARCHAR(100),
    service_state VARCHAR(50),
    service_zip VARCHAR(20),
    service_coordinates POINT, -- For distance calculations
    
    -- Booking Details
    problem_description TEXT,
    special_instructions TEXT,
    access_instructions TEXT, -- Gate codes, key location, etc.
    
    -- Pricing
    quoted_price DECIMAL(10,2),
    final_price DECIMAL(10,2),
    
    -- Status Tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending, confirmed, in_progress, completed, cancelled, no_show
    
    cancellation_reason TEXT,
    cancelled_by VARCHAR(50), -- customer, business, system
    cancelled_at TIMESTAMPTZ,
    
    -- Communication Preferences
    preferred_contact_method VARCHAR(20) DEFAULT 'phone', -- phone, email, sms
    sms_consent BOOLEAN DEFAULT false,
    email_consent BOOLEAN DEFAULT true,
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'website', -- website, phone, mobile_app, referral
    user_agent TEXT, -- For website bookings
    ip_address INET, -- For fraud prevention
    
    -- Idempotency
    idempotency_key VARCHAR(100) UNIQUE, -- Prevent duplicate bookings
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT bookings_valid_times CHECK (
        (scheduled_at IS NULL OR scheduled_at >= requested_at) AND
        (completed_at IS NULL OR completed_at >= COALESCE(scheduled_at, requested_at))
    )
);

-- Booking status change audit trail
CREATE TABLE booking_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    
    -- Event Details
    event_type VARCHAR(50) NOT NULL, -- created, confirmed, rescheduled, cancelled, completed
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    
    -- Changes
    changed_fields JSONB, -- What fields were modified
    old_values JSONB, -- Previous values
    new_values JSONB, -- New values
    
    -- Context
    triggered_by VARCHAR(50), -- customer, technician, admin, system
    user_id UUID REFERENCES users(id), -- If triggered by user
    reason TEXT,
    notes TEXT,
    
    -- Metadata
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- AVAILABILITY CACHE & OPTIMIZATION
-- =====================================================

-- Pre-computed availability slots for performance
CREATE TABLE availability_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES bookable_services(id) ON DELETE CASCADE,
    
    -- Time Slot
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    
    -- Capacity
    available_slots INTEGER NOT NULL DEFAULT 1,
    booked_slots INTEGER NOT NULL DEFAULT 0,
    
    -- Assignment
    available_technicians JSONB DEFAULT '[]'::jsonb, -- Array of technician IDs
    
    -- Cache Management
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    
    CONSTRAINT availability_cache_unique UNIQUE (business_id, service_id, date, start_time),
    CONSTRAINT availability_cache_valid_capacity CHECK (booked_slots <= available_slots)
);

-- =====================================================
-- CUSTOMER MANAGEMENT
-- =====================================================

-- Customer contact information and preferences
CREATE TABLE customer_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Identity (normalized for deduplication)
    email VARCHAR(255),
    phone VARCHAR(20),
    
    -- Personal Info
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(200),
    
    -- Preferences
    preferred_contact_method VARCHAR(20) DEFAULT 'phone',
    preferred_contact_time JSONB, -- {"start": "09:00", "end": "17:00", "timezone": "America/New_York"}
    
    -- Service History
    total_bookings INTEGER DEFAULT 0,
    last_booking_at TIMESTAMPTZ,
    customer_since DATE,
    
    -- Communication Consents
    sms_consent BOOLEAN DEFAULT false,
    sms_consent_date TIMESTAMPTZ,
    sms_consent_ip INET,
    
    email_consent BOOLEAN DEFAULT true,
    email_consent_date TIMESTAMPTZ,
    email_consent_ip INET,
    
    marketing_consent BOOLEAN DEFAULT false,
    marketing_consent_date TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT customer_contacts_business_email_unique UNIQUE (business_id, email),
    CONSTRAINT customer_contacts_business_phone_unique UNIQUE (business_id, phone)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Booking queries
CREATE INDEX idx_bookings_business_status ON bookings(business_id, status);
CREATE INDEX idx_bookings_scheduled_at ON bookings(scheduled_at) WHERE scheduled_at IS NOT NULL;
CREATE INDEX idx_bookings_technician ON bookings(primary_technician_id) WHERE primary_technician_id IS NOT NULL;
CREATE INDEX idx_bookings_customer_phone ON bookings(business_id, customer_phone);
CREATE INDEX idx_bookings_created_at ON bookings(created_at);

-- Availability queries
CREATE INDEX idx_availability_cache_lookup ON availability_cache(business_id, service_id, date, start_time);
CREATE INDEX idx_availability_cache_expires ON availability_cache(expires_at);

-- Time off queries
CREATE INDEX idx_time_off_technician_time ON time_off(technician_id, start_at, end_at);
CREATE INDEX idx_time_off_range ON time_off USING gist(tstzrange(start_at, end_at));

-- Technician queries
CREATE INDEX idx_technicians_business_active ON technicians(business_id, is_active, can_be_booked);
CREATE INDEX idx_technician_skills_lookup ON technician_skills(technician_id, skill_id);

-- Business hours
CREATE INDEX idx_business_hours_lookup ON business_hours(business_id, location_id, day_of_week);

-- Audit trail
CREATE INDEX idx_booking_events_booking ON booking_events(booking_id, created_at);
CREATE INDEX idx_booking_events_type ON booking_events(event_type, created_at);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Helper function to get user's business IDs (create if not exists)
CREATE OR REPLACE FUNCTION get_user_business_ids()
RETURNS TABLE(business_id UUID) AS $$
BEGIN
    -- For now, return all business IDs for the authenticated user
    -- This should be updated based on your actual user-business relationship
    RETURN QUERY
    SELECT DISTINCT b.id
    FROM businesses b
    WHERE b.id IS NOT NULL;  -- Placeholder - update with actual user filtering
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Enable RLS on all tables
ALTER TABLE technicians ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE technician_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookable_services ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_hours ENABLE ROW LEVEL SECURITY;
ALTER TABLE time_off ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE booking_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE availability_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_contacts ENABLE ROW LEVEL SECURITY;

-- RLS Policies (business isolation)
CREATE POLICY "Users can access their business technicians" ON technicians
    FOR ALL USING (business_id IN (SELECT get_user_business_ids()));

CREATE POLICY "Users can access their business skills" ON skills
    FOR ALL USING (business_id IN (SELECT get_user_business_ids()));

CREATE POLICY "Users can access their business technician skills" ON technician_skills
    FOR ALL USING (technician_id IN (
        SELECT id FROM technicians WHERE business_id IN (SELECT get_user_business_ids())
    ));

CREATE POLICY "Users can access their business bookable services" ON bookable_services
    FOR ALL USING (business_id IN (SELECT get_user_business_ids()));

CREATE POLICY "Users can access their business hours" ON business_hours
    FOR ALL USING (business_id IN (SELECT get_user_business_ids()));

CREATE POLICY "Users can access their business time off" ON time_off
    FOR ALL USING (technician_id IN (
        SELECT id FROM technicians WHERE business_id IN (SELECT get_user_business_ids())
    ));

CREATE POLICY "Users can access their business bookings" ON bookings
    FOR ALL USING (business_id IN (SELECT get_user_business_ids()));

CREATE POLICY "Users can access their business booking events" ON booking_events
    FOR ALL USING (booking_id IN (
        SELECT id FROM bookings WHERE business_id IN (SELECT get_user_business_ids())
    ));

CREATE POLICY "Users can access their business availability cache" ON availability_cache
    FOR ALL USING (business_id IN (SELECT get_user_business_ids()));

CREATE POLICY "Users can access their business customer contacts" ON customer_contacts
    FOR ALL USING (business_id IN (SELECT get_user_business_ids()));

-- Public read access for booking availability (with business_id filter)
CREATE POLICY "Public can read availability for booking" ON availability_cache
    FOR SELECT USING (true);

CREATE POLICY "Public can read bookable services for booking" ON bookable_services
    FOR SELECT USING (is_bookable = true);

-- =====================================================
-- TRIGGERS & FUNCTIONS
-- =====================================================

-- Update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_technicians_updated_at BEFORE UPDATE ON technicians
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookable_services_updated_at BEFORE UPDATE ON bookable_services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customer_contacts_updated_at BEFORE UPDATE ON customer_contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Generate booking numbers
CREATE OR REPLACE FUNCTION generate_booking_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.booking_number IS NULL THEN
        NEW.booking_number := 'BK-' || EXTRACT(YEAR FROM NOW()) || '-' || 
                             LPAD(nextval('booking_number_seq')::text, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create sequence for booking numbers
CREATE SEQUENCE IF NOT EXISTS booking_number_seq START 1;

CREATE TRIGGER generate_booking_number_trigger BEFORE INSERT ON bookings
    FOR EACH ROW EXECUTE FUNCTION generate_booking_number();

-- Audit trail for booking changes
CREATE OR REPLACE FUNCTION log_booking_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Log the change
    INSERT INTO booking_events (
        booking_id,
        event_type,
        old_status,
        new_status,
        changed_fields,
        old_values,
        new_values,
        triggered_by
    ) VALUES (
        COALESCE(NEW.id, OLD.id),
        CASE 
            WHEN TG_OP = 'INSERT' THEN 'created'
            WHEN TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN 'status_changed'
            WHEN TG_OP = 'UPDATE' THEN 'updated'
            WHEN TG_OP = 'DELETE' THEN 'deleted'
        END,
        CASE WHEN TG_OP = 'UPDATE' THEN OLD.status END,
        CASE WHEN TG_OP != 'DELETE' THEN NEW.status END,
        CASE 
            WHEN TG_OP = 'UPDATE' THEN 
                (SELECT jsonb_object_agg(key, value) FROM jsonb_each(to_jsonb(NEW)) WHERE key != 'updated_at')
            ELSE NULL
        END,
        CASE WHEN TG_OP = 'UPDATE' THEN to_jsonb(OLD) END,
        CASE WHEN TG_OP != 'DELETE' THEN to_jsonb(NEW) END,
        'system'
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

CREATE TRIGGER log_booking_changes_trigger 
    AFTER INSERT OR UPDATE OR DELETE ON bookings
    FOR EACH ROW EXECUTE FUNCTION log_booking_changes();

-- Invalidate availability cache on booking changes
CREATE OR REPLACE FUNCTION invalidate_availability_cache()
RETURNS TRIGGER AS $$
BEGIN
    -- Delete cached availability for the affected date and service
    DELETE FROM availability_cache 
    WHERE business_id = COALESCE(NEW.business_id, OLD.business_id)
      AND service_id = COALESCE(NEW.service_id, OLD.service_id)
      AND date = COALESCE(NEW.scheduled_at, OLD.scheduled_at, NEW.requested_at, OLD.requested_at)::date;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

CREATE TRIGGER invalidate_availability_cache_trigger 
    AFTER INSERT OR UPDATE OR DELETE ON bookings
    FOR EACH ROW EXECUTE FUNCTION invalidate_availability_cache();

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to check technician availability
CREATE OR REPLACE FUNCTION is_technician_available(
    p_technician_id UUID,
    p_start_time TIMESTAMPTZ,
    p_end_time TIMESTAMPTZ
) RETURNS BOOLEAN AS $$
BEGIN
    -- Check for conflicting bookings
    IF EXISTS (
        SELECT 1 FROM bookings 
        WHERE primary_technician_id = p_technician_id
          AND status IN ('confirmed', 'in_progress')
          AND tstzrange(scheduled_at, scheduled_at + (estimated_duration_minutes || ' minutes')::interval) &&
              tstzrange(p_start_time, p_end_time)
    ) THEN
        RETURN FALSE;
    END IF;
    
    -- Check for time off
    IF EXISTS (
        SELECT 1 FROM time_off
        WHERE technician_id = p_technician_id
          AND status = 'approved'
          AND tstzrange(start_at, end_at) && tstzrange(p_start_time, p_end_time)
    ) THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ language 'plpgsql';

-- Function to get available technicians for a service
CREATE OR REPLACE FUNCTION get_available_technicians(
    p_business_id UUID,
    p_service_id UUID,
    p_start_time TIMESTAMPTZ,
    p_end_time TIMESTAMPTZ
) RETURNS TABLE (
    technician_id UUID,
    technician_name TEXT,
    skills JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id,
        (t.first_name || ' ' || t.last_name)::TEXT,
        jsonb_agg(s.name) as skills
    FROM technicians t
    JOIN technician_skills ts ON t.id = ts.technician_id
    JOIN skills s ON ts.skill_id = s.id
    JOIN bookable_services bs ON bs.id = p_service_id
    WHERE t.business_id = p_business_id
      AND t.is_active = true
      AND t.can_be_booked = true
      AND is_technician_available(t.id, p_start_time, p_end_time)
      AND s.id = ANY(SELECT jsonb_array_elements_text(bs.required_skills)::UUID)
    GROUP BY t.id, t.first_name, t.last_name
    HAVING COUNT(DISTINCT s.id) >= jsonb_array_length(bs.required_skills);
END;
$$ language 'plpgsql';
