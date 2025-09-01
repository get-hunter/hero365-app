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
    phone VARCHAR(20),
    
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