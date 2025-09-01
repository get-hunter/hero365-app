-- =============================================
-- CORE CONTACT TABLES
-- =============================================
-- Customer and contact management
-- Depends on: businesses table

-- =============================================
-- CONTACTS TABLE
-- =============================================

CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id), -- Link to user account if they have one
    
    -- Personal Info
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20), -- E.164
    phone_country_code VARCHAR(3),
    phone_display VARCHAR(30),
    
    -- Address
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    
    -- Contact Details
    contact_type VARCHAR(50) DEFAULT 'customer', -- 'customer', 'lead', 'vendor', 'partner', 'supplier'
    contact_source VARCHAR(50), -- 'website', 'referral', 'google', 'facebook', 'direct'
    lead_status VARCHAR(50), -- 'new', 'contacted', 'qualified', 'proposal', 'won', 'lost'
    
    -- Customer Info
    customer_since DATE,
    total_jobs INTEGER DEFAULT 0,
    total_revenue DECIMAL(12,2) DEFAULT 0,
    average_job_value DECIMAL(10,2) DEFAULT 0,
    
    -- Communication Preferences
    preferred_contact_method VARCHAR(20) DEFAULT 'phone', -- 'phone', 'email', 'text'
    best_contact_time VARCHAR(50), -- 'morning', 'afternoon', 'evening', 'weekends'
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    do_not_contact BOOLEAN DEFAULT false,
    
    -- Metadata
    notes TEXT,
    tags TEXT[],
    custom_fields JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- International phone support for contacts
ALTER TABLE contacts 
ADD CONSTRAINT contacts_phone_valid 
CHECK (phone IS NULL OR is_valid_e164_phone(phone));

CREATE OR REPLACE FUNCTION auto_normalize_contact_phone()
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

CREATE TRIGGER contacts_phone_normalize
    BEFORE INSERT OR UPDATE ON contacts
    FOR EACH ROW
    WHEN (NEW.phone IS NOT NULL)
    EXECUTE FUNCTION auto_normalize_contact_phone();

-- =============================================
-- CONTACT NOTES
-- =============================================

CREATE TABLE contact_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    
    -- Note Content
    title VARCHAR(255),
    content TEXT NOT NULL,
    note_type VARCHAR(50) DEFAULT 'general', -- 'general', 'call', 'meeting', 'follow_up'
    
    -- Status
    is_important BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- USER RELATIONSHIPS
-- =============================================
-- Manages relationships between different user types (moved from auth tables)

CREATE TABLE user_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationship Participants
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    related_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Relationship Details
    relationship_type VARCHAR(50) NOT NULL, -- 'customer', 'supplier', 'employee', 'partner'
    relationship_status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'pending', 'blocked'
    
    -- Context (optional business context)
    business_id UUID REFERENCES businesses(id),
    
    -- Permissions & Access
    permissions JSONB DEFAULT '[]',
    access_level VARCHAR(20) DEFAULT 'basic', -- 'basic', 'standard', 'full', 'admin'
    
    -- Relationship Metadata
    established_date DATE DEFAULT CURRENT_DATE,
    notes TEXT,
    
    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Prevent duplicate relationships
    UNIQUE(user_id, related_user_id, relationship_type),
    
    -- Prevent self-relationships
    CONSTRAINT user_relationships_no_self CHECK (user_id != related_user_id)
);

-- =============================================
-- BASIC INDEXES
-- =============================================

CREATE INDEX idx_contacts_business ON contacts(business_id);
CREATE INDEX idx_contacts_user ON contacts(user_id);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_phone ON contacts(phone);
CREATE INDEX idx_contacts_type ON contacts(contact_type);
CREATE INDEX idx_contacts_lead_status ON contacts(lead_status);
CREATE INDEX idx_contacts_active ON contacts(is_active);
CREATE INDEX idx_contacts_name ON contacts(full_name);

CREATE INDEX idx_contact_notes_contact ON contact_notes(contact_id);
CREATE INDEX idx_contact_notes_business ON contact_notes(business_id);
CREATE INDEX idx_contact_notes_created_by ON contact_notes(created_by);

-- User relationships indexes
CREATE INDEX idx_user_relationships_user ON user_relationships(user_id);
CREATE INDEX idx_user_relationships_related ON user_relationships(related_user_id);
CREATE INDEX idx_user_relationships_type ON user_relationships(relationship_type);
CREATE INDEX idx_user_relationships_business ON user_relationships(business_id);
CREATE INDEX idx_user_relationships_status ON user_relationships(relationship_status);

COMMIT;
