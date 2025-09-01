-- =============================================
-- CORE BOOKING SYSTEM TABLES
-- =============================================
-- Essential booking and scheduling functionality
-- Depends on: businesses, contacts tables

-- =============================================
-- BOOKABLE SERVICES
-- =============================================

CREATE TABLE bookable_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Service Details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    service_category VARCHAR(100),
    
    -- Booking Configuration
    duration_minutes INTEGER NOT NULL DEFAULT 60,
    buffer_minutes INTEGER DEFAULT 15, -- Time between bookings
    advance_booking_days INTEGER DEFAULT 30, -- How far in advance can book
    
    -- Pricing
    base_price DECIMAL(10,2),
    price_type VARCHAR(20) DEFAULT 'fixed', -- 'fixed', 'hourly', 'quote'
    
    -- Availability
    is_active BOOLEAN DEFAULT true,
    requires_approval BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- BUSINESS HOURS
-- =============================================

CREATE TABLE business_hours (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Schedule
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6), -- 0=Sunday
    is_open BOOLEAN DEFAULT true,
    
    -- Times
    open_time TIME,
    close_time TIME,
    break_start TIME,
    break_end TIME,
    
    -- Special Hours
    is_emergency_available BOOLEAN DEFAULT false,
    emergency_rate_multiplier DECIMAL(3,2) DEFAULT 1.5,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, day_of_week)
);

-- =============================================
-- BOOKINGS
-- =============================================

CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES bookable_services(id),
    contact_id UUID REFERENCES contacts(id),
    
    -- Booking Details
    booking_number VARCHAR(50) UNIQUE,
    title VARCHAR(255),
    description TEXT,
    
    -- Customer Info (denormalized for quick access)
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    customer_phone VARCHAR(20),
    
    -- Scheduling
    scheduled_at TIMESTAMPTZ NOT NULL,
    estimated_duration_minutes INTEGER NOT NULL,
    actual_start_time TIMESTAMPTZ,
    actual_end_time TIMESTAMPTZ,
    
    -- Location
    service_address TEXT,
    service_city VARCHAR(100),
    service_state VARCHAR(2),
    service_zip_code VARCHAR(10),
    
    -- Status
    status VARCHAR(50) DEFAULT 'scheduled', -- 'scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show'
    
    -- Assignment
    primary_technician_id UUID REFERENCES users(id),
    
    -- Pricing
    quoted_price DECIMAL(10,2),
    final_price DECIMAL(10,2),
    
    -- Special Requirements
    special_instructions TEXT,
    requires_ladder BOOLEAN DEFAULT false,
    requires_permits BOOLEAN DEFAULT false,
    
    -- Tracking
    idempotency_key VARCHAR(255) UNIQUE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- BOOKING EVENTS (AUDIT LOG)
-- =============================================

CREATE TABLE booking_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    
    -- Event Details
    event_type VARCHAR(50) NOT NULL, -- 'created', 'confirmed', 'rescheduled', 'cancelled', 'completed'
    event_description TEXT,
    
    -- Actor
    created_by UUID REFERENCES users(id),
    
    -- Metadata
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- CALENDAR EVENTS
-- =============================================

CREATE TABLE calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    booking_id UUID REFERENCES bookings(id),
    
    -- Event Details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) DEFAULT 'booking', -- 'booking', 'block', 'meeting', 'personal'
    
    -- Timing
    start_datetime TIMESTAMPTZ NOT NULL,
    end_datetime TIMESTAMPTZ NOT NULL,
    is_all_day BOOLEAN DEFAULT false,
    
    -- Assignment
    assigned_to UUID REFERENCES users(id),
    
    -- Status
    status VARCHAR(20) DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled'
    
    -- Customer Reference
    customer_id UUID REFERENCES contacts(id),
    service_id UUID REFERENCES bookable_services(id),
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- SERVICE AREAS
-- =============================================

CREATE TABLE service_areas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Geographic Details
    area_name VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    postal_code VARCHAR(10),
    country_code VARCHAR(2) DEFAULT 'US',
    
    -- Service Configuration
    service_radius_miles INTEGER DEFAULT 25,
    travel_fee DECIMAL(10,2) DEFAULT 0,
    minimum_job_amount DECIMAL(10,2) DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    priority_level INTEGER DEFAULT 1, -- 1=highest priority
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, postal_code, country_code)
);

-- =============================================
-- AVAILABILITY REQUESTS
-- =============================================

CREATE TABLE availability_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Contact Info
    contact_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    
    -- Service Request
    service_type VARCHAR(255),
    service_description TEXT,
    preferred_date DATE,
    preferred_time_range VARCHAR(50), -- 'morning', 'afternoon', 'evening', 'anytime'
    
    -- Location
    service_address TEXT,
    service_city VARCHAR(100),
    service_state VARCHAR(2),
    service_zip_code VARCHAR(10),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'contacted', 'scheduled', 'declined'
    
    -- Response
    response_notes TEXT,
    responded_at TIMESTAMPTZ,
    responded_by UUID REFERENCES users(id),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- INDEXES
-- =============================================

CREATE INDEX idx_bookable_services_business ON bookable_services(business_id);
CREATE INDEX idx_bookable_services_active ON bookable_services(is_active);

CREATE INDEX idx_business_hours_business ON business_hours(business_id);
CREATE INDEX idx_business_hours_day ON business_hours(day_of_week);

CREATE INDEX idx_bookings_business ON bookings(business_id);
CREATE INDEX idx_bookings_service ON bookings(service_id);
CREATE INDEX idx_bookings_contact ON bookings(contact_id);
CREATE INDEX idx_bookings_scheduled ON bookings(scheduled_at);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_technician ON bookings(primary_technician_id);

CREATE INDEX idx_booking_events_booking ON booking_events(booking_id);
CREATE INDEX idx_booking_events_type ON booking_events(event_type);

CREATE INDEX idx_calendar_events_business ON calendar_events(business_id);
CREATE INDEX idx_calendar_events_booking ON calendar_events(booking_id);
CREATE INDEX idx_calendar_events_start ON calendar_events(start_datetime);
CREATE INDEX idx_calendar_events_assigned ON calendar_events(assigned_to);

CREATE INDEX idx_service_areas_business ON service_areas(business_id);
CREATE INDEX idx_service_areas_location ON service_areas(city, state);
CREATE INDEX idx_service_areas_postal ON service_areas(postal_code);
CREATE INDEX idx_service_areas_active ON service_areas(is_active);

CREATE INDEX idx_availability_requests_business ON availability_requests(business_id);
CREATE INDEX idx_availability_requests_status ON availability_requests(status);
CREATE INDEX idx_availability_requests_date ON availability_requests(preferred_date);

COMMIT;
