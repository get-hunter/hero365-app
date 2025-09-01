-- =============================================
-- CORE BUSINESS TABLES
-- =============================================
-- Business entities and relationships
-- Depends on: users table

-- =============================================
-- BUSINESSES TABLE
-- =============================================

CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Basic Info
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    website VARCHAR(255),
    
    -- Address
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    country VARCHAR(2) DEFAULT 'US',
    
    -- Business Details
    primary_trade VARCHAR(100),
    secondary_trades TEXT[],
    business_type VARCHAR(50) DEFAULT 'contractor', -- 'contractor', 'supplier', 'service_provider'
    company_size VARCHAR(20) DEFAULT 'small', -- 'small', 'medium', 'large'
    
    -- Experience & Credentials
    years_in_business INTEGER DEFAULT 0,
    year_established INTEGER,
    license_number VARCHAR(100),
    insurance_number VARCHAR(100),
    certifications TEXT[],
    
    -- Service Area
    service_radius INTEGER DEFAULT 25, -- miles
    service_areas JSONB DEFAULT '[]', -- Array of service area objects
    
    -- Operational
    emergency_available BOOLEAN DEFAULT false,
    business_hours JSONB DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- BUSINESS MEMBERSHIPS
-- =============================================

CREATE TABLE business_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Role & Permissions
    role VARCHAR(50) NOT NULL DEFAULT 'member', -- 'owner', 'admin', 'manager', 'member', 'viewer'
    permissions JSONB DEFAULT '[]',
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'pending', 'suspended'
    invited_by UUID REFERENCES users(id),
    invited_at TIMESTAMPTZ,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, user_id)
);

-- =============================================
-- BUSINESS SERVICES
-- =============================================

CREATE TABLE business_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Service Details
    service_name VARCHAR(100) NOT NULL,
    service_slug VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    
    -- Pricing
    price_type VARCHAR(20) DEFAULT 'range', -- 'fixed', 'range', 'hourly', 'quote'
    price_min DECIMAL(10,2),
    price_max DECIMAL(10,2),
    price_unit VARCHAR(20), -- 'hour', 'job', 'sqft', etc.
    
    -- Service Options
    is_emergency BOOLEAN DEFAULT false,
    is_commercial BOOLEAN DEFAULT false,
    is_residential BOOLEAN DEFAULT true,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, service_slug)
);

-- =============================================
-- BUSINESS LOCATIONS (SERVICE AREAS)
-- =============================================

CREATE TABLE business_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Location Details
    name VARCHAR(255), -- "Main Office", "Austin Service Area"
    address TEXT,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip_code VARCHAR(10),
    county VARCHAR(100),
    
    -- Service Area
    is_primary BOOLEAN DEFAULT false,
    service_radius INTEGER DEFAULT 25,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- BASIC INDEXES
-- =============================================

CREATE INDEX idx_businesses_owner ON businesses(owner_id);
CREATE INDEX idx_businesses_active ON businesses(is_active);
CREATE INDEX idx_businesses_trade ON businesses(primary_trade);
CREATE INDEX idx_businesses_city_state ON businesses(city, state);

CREATE INDEX idx_business_memberships_business ON business_memberships(business_id);
CREATE INDEX idx_business_memberships_user ON business_memberships(user_id);
CREATE INDEX idx_business_memberships_role ON business_memberships(role);

CREATE INDEX idx_business_services_business ON business_services(business_id);
CREATE INDEX idx_business_services_active ON business_services(is_active);
CREATE INDEX idx_business_services_slug ON business_services(service_slug);

CREATE INDEX idx_business_locations_business ON business_locations(business_id);
CREATE INDEX idx_business_locations_city_state ON business_locations(city, state);
CREATE INDEX idx_business_locations_primary ON business_locations(is_primary);

COMMIT;
