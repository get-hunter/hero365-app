-- Business Management System Migration
-- This migration creates tables for businesses, memberships, and invitations

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create businesses table
CREATE TABLE IF NOT EXISTS businesses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(255) NOT NULL,
    custom_industry VARCHAR(255),
    company_size VARCHAR(50) NOT NULL CHECK (company_size IN ('just_me', 'small', 'medium', 'large', 'enterprise')),
    owner_id TEXT NOT NULL,
    
    -- Business Profile
    description TEXT,
    phone_number VARCHAR(20),
    business_address TEXT,
    website VARCHAR(500),
    logo_url VARCHAR(500),
    business_email VARCHAR(320),
    
    -- Business Identity
    business_registration_number VARCHAR(100),
    tax_id VARCHAR(100),
    business_license VARCHAR(100),
    insurance_number VARCHAR(100),
    
    -- Onboarding & Setup
    selected_features JSONB DEFAULT '[]'::jsonb,
    primary_goals JSONB DEFAULT '[]'::jsonb,
    referral_source VARCHAR(50) CHECK (referral_source IN ('tiktok', 'tv', 'online_ad', 'web_search', 'podcast_radio', 'reddit', 'review_sites', 'youtube', 'facebook_instagram', 'referral', 'other')),
    onboarding_completed BOOLEAN DEFAULT false,
    onboarding_completed_date TIMESTAMPTZ,
    
    -- Business Settings
    timezone VARCHAR(100),
    currency VARCHAR(3) DEFAULT 'USD',
    business_hours JSONB,
    is_active BOOLEAN DEFAULT true,
    
    -- Team Management
    max_team_members INTEGER,
    
    -- Subscription & Features
    subscription_tier VARCHAR(50),
    enabled_features JSONB DEFAULT '[]'::jsonb,
    
    -- Metadata
    created_date TIMESTAMPTZ DEFAULT now(),
    last_modified TIMESTAMPTZ DEFAULT now(),
    
    -- Constraints
    CONSTRAINT businesses_name_owner_unique UNIQUE (name, owner_id),
    CONSTRAINT businesses_website_format CHECK (website IS NULL OR website ~ '^https?://'),
    CONSTRAINT businesses_email_format CHECK (business_email IS NULL OR business_email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Create business_memberships table
CREATE TABLE IF NOT EXISTS business_memberships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'admin', 'manager', 'employee', 'contractor', 'viewer')),
    permissions JSONB NOT NULL DEFAULT '[]'::jsonb,
    joined_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    invited_date TIMESTAMPTZ,
    invited_by TEXT,
    is_active BOOLEAN DEFAULT true,
    department_id UUID,
    job_title VARCHAR(100),
    
    -- Constraints
    CONSTRAINT business_memberships_unique UNIQUE (business_id, user_id),
    CONSTRAINT business_memberships_permissions_not_empty CHECK (jsonb_array_length(permissions) > 0)
);

-- Create business_invitations table
CREATE TABLE IF NOT EXISTS business_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    business_name VARCHAR(255) NOT NULL,
    invited_email VARCHAR(320),
    invited_phone VARCHAR(20),
    invited_by TEXT NOT NULL,
    invited_by_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'admin', 'manager', 'employee', 'contractor', 'viewer')),
    permissions JSONB NOT NULL DEFAULT '[]'::jsonb,
    invitation_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    expiry_date TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined', 'expired', 'cancelled')),
    message TEXT,
    accepted_date TIMESTAMPTZ,
    declined_date TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT business_invitations_contact_required CHECK (
        (invited_email IS NOT NULL AND invited_email != '') OR 
        (invited_phone IS NOT NULL AND invited_phone != '')
    ),
    CONSTRAINT business_invitations_email_format CHECK (
        invited_email IS NULL OR 
        invited_email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),
    CONSTRAINT business_invitations_phone_format CHECK (
        invited_phone IS NULL OR 
        length(regexp_replace(invited_phone, '[^0-9]', '', 'g')) >= 10
    ),
    CONSTRAINT business_invitations_expiry_future CHECK (expiry_date > invitation_date),
    CONSTRAINT business_invitations_permissions_not_empty CHECK (jsonb_array_length(permissions) > 0),
    CONSTRAINT business_invitations_accepted_date_check CHECK (
        (status = 'accepted' AND accepted_date IS NOT NULL) OR 
        (status != 'accepted' AND accepted_date IS NULL)
    ),
    CONSTRAINT business_invitations_declined_date_check CHECK (
        (status = 'declined' AND declined_date IS NOT NULL) OR 
        (status != 'declined' AND declined_date IS NULL)
    )
);

-- Create departments table (optional for now, but good to have)
CREATE TABLE IF NOT EXISTS departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    manager_id TEXT,
    is_active BOOLEAN DEFAULT true,
    created_date TIMESTAMPTZ DEFAULT now(),
    last_modified TIMESTAMPTZ DEFAULT now(),
    
    -- Constraints
    CONSTRAINT departments_name_business_unique UNIQUE (business_id, name)
);

-- Create indexes for performance

-- Businesses indexes
CREATE INDEX IF NOT EXISTS idx_businesses_owner_id ON businesses(owner_id);
CREATE INDEX IF NOT EXISTS idx_businesses_is_active ON businesses(is_active);
CREATE INDEX IF NOT EXISTS idx_businesses_industry ON businesses(industry);
CREATE INDEX IF NOT EXISTS idx_businesses_created_date ON businesses(created_date);
CREATE INDEX IF NOT EXISTS idx_businesses_name_gin ON businesses USING gin(name gin_trgm_ops);

-- Business memberships indexes
CREATE INDEX IF NOT EXISTS idx_business_memberships_business_id ON business_memberships(business_id);
CREATE INDEX IF NOT EXISTS idx_business_memberships_user_id ON business_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_business_memberships_role ON business_memberships(role);
CREATE INDEX IF NOT EXISTS idx_business_memberships_is_active ON business_memberships(is_active);
CREATE INDEX IF NOT EXISTS idx_business_memberships_joined_date ON business_memberships(joined_date);

-- Business invitations indexes
CREATE INDEX IF NOT EXISTS idx_business_invitations_business_id ON business_invitations(business_id);
CREATE INDEX IF NOT EXISTS idx_business_invitations_invited_email ON business_invitations(invited_email);
CREATE INDEX IF NOT EXISTS idx_business_invitations_invited_phone ON business_invitations(invited_phone);
CREATE INDEX IF NOT EXISTS idx_business_invitations_status ON business_invitations(status);
CREATE INDEX IF NOT EXISTS idx_business_invitations_expiry_date ON business_invitations(expiry_date);
CREATE INDEX IF NOT EXISTS idx_business_invitations_invited_by ON business_invitations(invited_by);

-- Departments indexes
CREATE INDEX IF NOT EXISTS idx_departments_business_id ON departments(business_id);
CREATE INDEX IF NOT EXISTS idx_departments_manager_id ON departments(manager_id);
CREATE INDEX IF NOT EXISTS idx_departments_is_active ON departments(is_active);

-- Create triggers for updating last_modified timestamp

-- Businesses trigger
CREATE OR REPLACE FUNCTION update_businesses_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER businesses_update_last_modified
    BEFORE UPDATE ON businesses
    FOR EACH ROW
    EXECUTE FUNCTION update_businesses_last_modified();

-- Departments trigger
CREATE OR REPLACE FUNCTION update_departments_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER departments_update_last_modified
    BEFORE UPDATE ON departments
    FOR EACH ROW
    EXECUTE FUNCTION update_departments_last_modified();

-- Create function to automatically expire invitations
CREATE OR REPLACE FUNCTION mark_expired_invitations()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE business_invitations 
    SET status = 'expired'
    WHERE status = 'pending' 
    AND expiry_date < now();
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to clean up old expired invitations
CREATE OR REPLACE FUNCTION cleanup_expired_invitations(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM business_invitations 
    WHERE status IN ('expired', 'declined', 'cancelled')
    AND invitation_date < now() - INTERVAL '1 day' * days_old;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Insert default permissions data (as JSONB for reference)
-- This is just documentation - actual permissions are managed in the application layer

COMMENT ON TABLE businesses IS 'Core business entities with profile, settings, and subscription information';
COMMENT ON TABLE business_memberships IS 'User memberships in businesses with roles and permissions';
COMMENT ON TABLE business_invitations IS 'Invitations for users to join business teams';
COMMENT ON TABLE departments IS 'Organizational departments within businesses';

COMMENT ON COLUMN businesses.selected_features IS 'Array of feature names selected during onboarding';
COMMENT ON COLUMN businesses.primary_goals IS 'Array of primary business goals';
COMMENT ON COLUMN businesses.enabled_features IS 'Array of currently enabled feature names';
COMMENT ON COLUMN business_memberships.permissions IS 'Array of permission strings for this membership';
COMMENT ON COLUMN business_invitations.permissions IS 'Array of permission strings for the invited role';

-- Grant permissions (adjust based on your RLS policies)
-- Note: In Supabase, you'll typically want to set up Row Level Security (RLS) policies
-- These are just basic table permissions

-- Example RLS policies (uncomment and adjust as needed):
-- ALTER TABLE businesses ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE business_memberships ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE business_invitations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE departments ENABLE ROW LEVEL SECURITY;

-- Policy examples:
-- CREATE POLICY "Users can view businesses they're members of" ON businesses FOR SELECT
--     USING (id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()::text));

-- CREATE POLICY "Business owners can update their businesses" ON businesses FOR UPDATE
--     USING (owner_id = auth.uid()::text);

-- CREATE POLICY "Users can view their own memberships" ON business_memberships FOR SELECT
--     USING (user_id = auth.uid()::text);

-- CREATE POLICY "Users can view invitations sent to them" ON business_invitations FOR SELECT
--     USING (invited_email = auth.email() OR invited_phone = auth.phone());

-- Remember to:
-- 1. Set up proper RLS policies based on your authentication system
-- 2. Configure appropriate grants for your application user
-- 3. Set up scheduled jobs for invitation cleanup if needed
-- 4. Consider adding audit logging if required 