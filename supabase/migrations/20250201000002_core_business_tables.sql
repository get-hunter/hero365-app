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
    display_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20) NOT NULL, -- E.164 format: +1234567890
    phone_country_code VARCHAR(3), -- Country code: 1, 44, 49, etc.
    phone_display VARCHAR(30), -- Formatted for display: +1 (555) 123-4567
    website VARCHAR(255),
    
    -- Address
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'US',
    timezone VARCHAR(100) DEFAULT 'UTC',
    
    -- Business Details
    primary_trade VARCHAR(100),
    secondary_trades TEXT[],
    business_type VARCHAR(50) DEFAULT 'contractor', -- 'contractor', 'supplier', 'service_provider'
    company_size VARCHAR(20) DEFAULT 'small', -- 'small', 'medium', 'large'
    
    -- Market Focus & Services (New Structure)
    market_focus VARCHAR(20) DEFAULT 'both' CHECK (market_focus IN ('residential', 'commercial', 'both')),
    residential_services JSONB DEFAULT '[]', -- Array of residential services
    commercial_services JSONB DEFAULT '[]', -- Array of commercial services
    
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
    onboarding_completed BOOLEAN DEFAULT false,
    referral_source VARCHAR(100),
    
    -- Metadata
    created_date TIMESTAMPTZ DEFAULT NOW(),
    last_modified TIMESTAMPTZ DEFAULT NOW()
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
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
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
-- INTERNATIONAL PHONE NUMBER SUPPORT
-- =============================================

-- Function to validate E.164 phone number format
CREATE OR REPLACE FUNCTION is_valid_e164_phone(phone_number TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- E.164 format: +[country code][national number]
    -- Length: 7-15 digits (including country code)
    -- Must start with +
    RETURN phone_number ~ '^\+[1-9]\d{6,14}$';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to extract country code from E.164 phone number
CREATE OR REPLACE FUNCTION extract_country_code(phone_number TEXT)
RETURNS TEXT AS $$
BEGIN
    IF NOT is_valid_e164_phone(phone_number) THEN
        RETURN NULL;
    END IF;
    
    -- Extract country code (1-3 digits after +)
    RETURN CASE
        WHEN phone_number ~ '^\+1[2-9]' THEN '1'  -- US/Canada
        WHEN phone_number ~ '^\+44' THEN '44'     -- UK
        WHEN phone_number ~ '^\+49' THEN '49'     -- Germany
        WHEN phone_number ~ '^\+33' THEN '33'     -- France
        WHEN phone_number ~ '^\+34' THEN '34'     -- Spain
        WHEN phone_number ~ '^\+39' THEN '39'     -- Italy
        WHEN phone_number ~ '^\+52' THEN '52'     -- Mexico
        WHEN phone_number ~ '^\+55' THEN '55'     -- Brazil
        WHEN phone_number ~ '^\+86' THEN '86'     -- China
        WHEN phone_number ~ '^\+91' THEN '91'     -- India
        ELSE SUBSTRING(phone_number FROM 2 FOR 3)  -- Fallback: first 3 digits
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to format phone number for display
CREATE OR REPLACE FUNCTION format_phone_display(phone_number TEXT)
RETURNS TEXT AS $$
DECLARE
    cc TEXT;
    national_number TEXT;
BEGIN
    IF NOT is_valid_e164_phone(phone_number) THEN
        RETURN phone_number; -- Return as-is if invalid
    END IF;
    
    cc := extract_country_code(phone_number);
    national_number := SUBSTRING(phone_number FROM LENGTH(cc) + 2);
    
    -- Format based on country code
    RETURN CASE cc
        WHEN '1' THEN -- US/Canada: +1 (XXX) XXX-XXXX
            '+1 (' || SUBSTRING(national_number FROM 1 FOR 3) || ') ' ||
            SUBSTRING(national_number FROM 4 FOR 3) || '-' ||
            SUBSTRING(national_number FROM 7)
        WHEN '44' THEN -- UK: +44 XXXX XXX XXX
            '+44 ' || SUBSTRING(national_number FROM 1 FOR 4) || ' ' ||
            SUBSTRING(national_number FROM 5 FOR 3) || ' ' ||
            SUBSTRING(national_number FROM 8)
        ELSE -- Default: +CC XXXXXXXXX
            '+' || cc || ' ' || national_number
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to normalize phone number to E.164 format
CREATE OR REPLACE FUNCTION normalize_phone_to_e164(
    phone_input TEXT, 
    default_country_code TEXT DEFAULT '1'
)
RETURNS TEXT AS $$
DECLARE
    cleaned TEXT;
    result TEXT;
BEGIN
    -- Remove all non-digit characters except +
    cleaned := REGEXP_REPLACE(phone_input, '[^\d+]', '', 'g');
    
    -- If already in E.164 format, validate and return
    IF cleaned ~ '^\+' THEN
        IF is_valid_e164_phone(cleaned) THEN
            RETURN cleaned;
        ELSE
            RETURN NULL;
        END IF;
    END IF;
    
    -- If starts with country code without +, add +
    IF LENGTH(cleaned) > 10 THEN
        result := '+' || cleaned;
        IF is_valid_e164_phone(result) THEN
            RETURN result;
        END IF;
    END IF;
    
    -- Assume national number, add default country code
    IF LENGTH(cleaned) >= 7 THEN
        result := '+' || default_country_code || cleaned;
        IF is_valid_e164_phone(result) THEN
            RETURN result;
        END IF;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Trigger function for automatic phone normalization
CREATE OR REPLACE FUNCTION auto_normalize_business_phone()
RETURNS TRIGGER AS $$
DECLARE
    normalized_phone TEXT;
    country_code TEXT;
    display_phone TEXT;
    original_phone TEXT;
BEGIN
    -- Store original input for normalization
    original_phone := NEW.phone;
    
    -- Only process if phone field is provided
    IF NEW.phone IS NOT NULL THEN
        -- If phone is already in E.164 format, use it directly
        IF is_valid_e164_phone(NEW.phone) THEN
            normalized_phone := NEW.phone;
        ELSE
            -- Normalize to E.164 format
            normalized_phone := normalize_phone_to_e164(NEW.phone, '1'); -- Default to US
        END IF;
        
        IF normalized_phone IS NOT NULL THEN
            country_code := extract_country_code(normalized_phone);
            display_phone := format_phone_display(normalized_phone);
            
            -- Store E.164 format in phone field
            NEW.phone := normalized_phone;
            NEW.phone_country_code := country_code;
            NEW.phone_display := display_phone;
        ELSE
            -- If normalization failed, reject the insert/update
            RAISE EXCEPTION 'Invalid phone number format: %. Please provide a valid phone number.', original_phone;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add constraints for E.164 validation
ALTER TABLE businesses 
ADD CONSTRAINT businesses_phone_valid 
CHECK (phone IS NULL OR is_valid_e164_phone(phone));

-- Create trigger for automatic phone normalization
CREATE TRIGGER businesses_phone_normalize
    BEFORE INSERT OR UPDATE ON businesses
    FOR EACH ROW
    WHEN (NEW.phone IS NOT NULL)
    EXECUTE FUNCTION auto_normalize_business_phone();

-- =============================================
-- BASIC INDEXES
-- =============================================

CREATE INDEX idx_businesses_owner ON businesses(owner_id);
CREATE INDEX idx_businesses_active ON businesses(is_active);
CREATE INDEX idx_businesses_trade ON businesses(primary_trade);
CREATE INDEX idx_businesses_city_state ON businesses(city, state);
CREATE INDEX idx_businesses_market_focus ON businesses(market_focus);
CREATE INDEX idx_businesses_residential_services ON businesses USING GIN(residential_services);
CREATE INDEX idx_businesses_commercial_services ON businesses USING GIN(commercial_services);
CREATE INDEX idx_businesses_phone ON businesses(phone);
CREATE INDEX idx_businesses_phone_country ON businesses(phone_country_code);

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
