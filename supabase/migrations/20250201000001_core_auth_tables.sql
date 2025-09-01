-- =============================================
-- CORE AUTH TABLES
-- =============================================
-- Multi-user system for contractors, clients, and suppliers
-- Foundation tables - no dependencies

-- =============================================
-- USERS TABLE
-- =============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(320) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    display_name VARCHAR(255),
    avatar_url TEXT,
    phone VARCHAR(20), -- E.164
    phone_country_code VARCHAR(3),
    phone_display VARCHAR(30),
    
    -- User Type Management
    user_type VARCHAR(20) NOT NULL DEFAULT 'contractor', -- 'contractor', 'client', 'supplier', 'admin'
    primary_role VARCHAR(50), -- 'business_owner', 'technician', 'customer', 'supplier_rep'
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    verification_method VARCHAR(20), -- 'email', 'phone', 'manual'
    
    -- Authentication
    last_login_at TIMESTAMPTZ,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT users_user_type_check CHECK (user_type IN ('contractor', 'client', 'supplier', 'admin'))
);

-- =============================================
-- INTERNATIONAL PHONE HELPERS (COMMON)
-- =============================================

-- Function to validate E.164 phone number format
CREATE OR REPLACE FUNCTION is_valid_e164_phone(phone_number TEXT)
RETURNS BOOLEAN AS $$
BEGIN
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
    RETURN SUBSTRING(phone_number FROM 2 FOR 3);
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
        RETURN phone_number;
    END IF;
    cc := extract_country_code(phone_number);
    national_number := SUBSTRING(phone_number FROM LENGTH(cc) + 2);
    RETURN '+' || cc || ' ' || national_number;
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
    cleaned := REGEXP_REPLACE(phone_input, '[^\d+]', '', 'g');
    IF cleaned ~ '^\+' THEN
        IF is_valid_e164_phone(cleaned) THEN
            RETURN cleaned;
        ELSE
            RETURN NULL;
        END IF;
    END IF;
    IF LENGTH(cleaned) > 10 THEN
        result := '+' || cleaned;
        IF is_valid_e164_phone(result) THEN
            RETURN result;
        END IF;
    END IF;
    IF LENGTH(cleaned) >= 7 THEN
        result := '+' || default_country_code || cleaned;
        IF is_valid_e164_phone(result) THEN
            RETURN result;
        END IF;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- International phone support for users
ALTER TABLE users 
ADD CONSTRAINT users_phone_valid 
CHECK (phone IS NULL OR is_valid_e164_phone(phone));

CREATE OR REPLACE FUNCTION auto_normalize_user_phone()
RETURNS TRIGGER AS $$
DECLARE
    normalized_phone TEXT;
    country_code TEXT;
    display_phone TEXT;
    original_phone TEXT;
BEGIN
    original_phone := NEW.phone;
    IF NEW.phone IS NOT NULL THEN
        IF is_valid_e164_phone(NEW.phone) THEN
            normalized_phone := NEW.phone;
        ELSE
            normalized_phone := normalize_phone_to_e164(NEW.phone, '1');
        END IF;

        IF normalized_phone IS NOT NULL THEN
            country_code := extract_country_code(normalized_phone);
            display_phone := format_phone_display(normalized_phone);

            NEW.phone := normalized_phone;
            NEW.phone_country_code := country_code;
            NEW.phone_display := display_phone;
        ELSE
            RAISE EXCEPTION 'Invalid phone number format: %. Please provide a valid phone number.', original_phone;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_phone_normalize
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    WHEN (NEW.phone IS NOT NULL)
    EXECUTE FUNCTION auto_normalize_user_phone();

-- =============================================
-- USER PROFILES (EXTENDED INFO)
-- =============================================

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Extended Profile Information
    bio TEXT,
    timezone VARCHAR(50) DEFAULT 'America/Chicago',
    language VARCHAR(10) DEFAULT 'en',
    
    -- Contact Preferences
    preferred_contact_method VARCHAR(20) DEFAULT 'email', -- 'email', 'phone', 'sms'
    notification_preferences JSONB DEFAULT '{}',
    email_notifications BOOLEAN DEFAULT true,
    sms_notifications BOOLEAN DEFAULT false,
    marketing_emails BOOLEAN DEFAULT true,
    
    -- Professional Information (for contractors/suppliers)
    job_title VARCHAR(100),
    company_name VARCHAR(255),
    license_number VARCHAR(100),
    years_experience INTEGER,
    
    -- Address Information
    address JSONB,
    
    -- Emergency Contact (for technicians)
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_phone_country_code VARCHAR(3),
    emergency_contact_phone_display VARCHAR(30),
    emergency_contact_relationship VARCHAR(50),
    
    -- Onboarding & Status
    onboarding_completed BOOLEAN DEFAULT false,
    onboarding_step VARCHAR(50), -- 'profile', 'business', 'services', 'payment', 'complete'
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- Note: user_relationships table moved to core_contact_tables.sql 
-- to resolve dependency on businesses table

-- =============================================
-- BASIC INDEXES
-- =============================================

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_type ON users(user_type);
CREATE INDEX idx_users_role ON users(primary_role);
CREATE INDEX idx_users_verified ON users(is_verified);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_onboarding ON user_profiles(onboarding_completed);

-- user_relationships indexes moved to core_contact_tables.sql

COMMIT;