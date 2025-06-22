-- Contact Management System Migration
-- Creates tables and indexes for comprehensive contact management

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create contacts table
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    contact_type VARCHAR(20) NOT NULL CHECK (contact_type IN ('customer', 'lead', 'prospect', 'vendor', 'partner', 'contractor')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'archived', 'blocked')),
    
    -- Personal Information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(200),
    job_title VARCHAR(100),
    
    -- Contact Information
    email VARCHAR(320),
    phone VARCHAR(20),
    mobile_phone VARCHAR(20),
    website VARCHAR(200),
    
    -- Address Information (stored as JSONB for flexibility)
    address JSONB,
    
    -- Business Information
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    source VARCHAR(20) CHECK (source IN ('website', 'referral', 'social_media', 'advertising', 'cold_outreach', 'event', 'partner', 'existing_customer', 'direct', 'other')),
    tags JSONB DEFAULT '[]'::jsonb,
    notes TEXT,
    
    -- Financial Information
    estimated_value DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Relationship Information
    assigned_to TEXT, -- User ID from Supabase Auth
    created_by TEXT,  -- User ID from Supabase Auth
    
    -- Custom Fields (flexible JSONB storage)
    custom_fields JSONB DEFAULT '{}'::jsonb,
    
    -- Metadata
    created_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_modified TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_contacted TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT contacts_name_required CHECK (
        (first_name IS NOT NULL AND first_name != '') OR 
        (last_name IS NOT NULL AND last_name != '') OR 
        (company_name IS NOT NULL AND company_name != '')
    ),
    CONSTRAINT contacts_contact_method_required CHECK (
        (email IS NOT NULL AND email != '') OR 
        (phone IS NOT NULL AND phone != '') OR 
        (mobile_phone IS NOT NULL AND mobile_phone != '')
    ),
    CONSTRAINT contacts_email_format CHECK (
        email IS NULL OR 
        email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),
    CONSTRAINT contacts_phone_format CHECK (
        phone IS NULL OR 
        length(regexp_replace(phone, '[^0-9]', '', 'g')) >= 10
    ),
    CONSTRAINT contacts_mobile_phone_format CHECK (
        mobile_phone IS NULL OR 
        length(regexp_replace(mobile_phone, '[^0-9]', '', 'g')) >= 10
    ),
    CONSTRAINT contacts_website_format CHECK (
        website IS NULL OR 
        website ~ '^https?://' OR 
        website ~ '\.'
    ),
    CONSTRAINT contacts_estimated_value_positive CHECK (
        estimated_value IS NULL OR estimated_value >= 0
    ),
    CONSTRAINT contacts_currency_format CHECK (
        currency IS NULL OR length(currency) = 3
    ),
    CONSTRAINT contacts_tags_is_array CHECK (
        jsonb_typeof(tags) = 'array'
    ),
    CONSTRAINT contacts_custom_fields_is_object CHECK (
        jsonb_typeof(custom_fields) = 'object'
    )
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_contacts_business_id ON contacts(business_id);
CREATE INDEX IF NOT EXISTS idx_contacts_contact_type ON contacts(contact_type);
CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);
CREATE INDEX IF NOT EXISTS idx_contacts_priority ON contacts(priority);
CREATE INDEX IF NOT EXISTS idx_contacts_source ON contacts(source);
CREATE INDEX IF NOT EXISTS idx_contacts_assigned_to ON contacts(assigned_to);
CREATE INDEX IF NOT EXISTS idx_contacts_created_by ON contacts(created_by);
CREATE INDEX IF NOT EXISTS idx_contacts_created_date ON contacts(created_date);
CREATE INDEX IF NOT EXISTS idx_contacts_last_modified ON contacts(last_modified);
CREATE INDEX IF NOT EXISTS idx_contacts_last_contacted ON contacts(last_contacted);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_contacts_business_type ON contacts(business_id, contact_type);
CREATE INDEX IF NOT EXISTS idx_contacts_business_status ON contacts(business_id, status);
CREATE INDEX IF NOT EXISTS idx_contacts_business_priority ON contacts(business_id, priority);
CREATE INDEX IF NOT EXISTS idx_contacts_business_assigned ON contacts(business_id, assigned_to);

-- Email and phone indexes for uniqueness within business
CREATE UNIQUE INDEX IF NOT EXISTS idx_contacts_business_email_unique 
ON contacts(business_id, email) 
WHERE email IS NOT NULL AND email != '';

CREATE UNIQUE INDEX IF NOT EXISTS idx_contacts_business_phone_unique 
ON contacts(business_id, phone) 
WHERE phone IS NOT NULL AND phone != '';

-- Text search indexes
CREATE INDEX IF NOT EXISTS idx_contacts_email_search ON contacts USING gin(to_tsvector('english', COALESCE(email, '')));
CREATE INDEX IF NOT EXISTS idx_contacts_name_search ON contacts USING gin(to_tsvector('english', 
    COALESCE(first_name, '') || ' ' || 
    COALESCE(last_name, '') || ' ' || 
    COALESCE(company_name, '')
));

-- JSONB indexes for tags and custom fields
CREATE INDEX IF NOT EXISTS idx_contacts_tags ON contacts USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_contacts_custom_fields ON contacts USING gin(custom_fields);

-- Create contact activities table for tracking interactions
CREATE TABLE IF NOT EXISTS contact_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN (
        'call', 'email', 'meeting', 'note', 'task', 'quote', 'invoice', 'payment', 'other'
    )),
    subject VARCHAR(200),
    description TEXT,
    activity_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    duration_minutes INTEGER,
    outcome VARCHAR(50) CHECK (outcome IN ('successful', 'no_answer', 'busy', 'scheduled', 'completed', 'cancelled')),
    
    -- User who performed the activity
    performed_by TEXT NOT NULL, -- User ID from Supabase Auth
    
    -- Related records (optional references)
    related_job_id UUID,
    related_project_id UUID,
    related_invoice_id UUID,
    
    -- Metadata
    created_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_modified TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    -- Additional data (flexible JSONB storage)
    activity_data JSONB DEFAULT '{}'::jsonb,
    
    CONSTRAINT contact_activities_duration_positive CHECK (
        duration_minutes IS NULL OR duration_minutes >= 0
    ),
    CONSTRAINT contact_activities_data_is_object CHECK (
        jsonb_typeof(activity_data) = 'object'
    )
);

-- Indexes for contact activities
CREATE INDEX IF NOT EXISTS idx_contact_activities_contact_id ON contact_activities(contact_id);
CREATE INDEX IF NOT EXISTS idx_contact_activities_business_id ON contact_activities(business_id);
CREATE INDEX IF NOT EXISTS idx_contact_activities_type ON contact_activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_contact_activities_date ON contact_activities(activity_date);
CREATE INDEX IF NOT EXISTS idx_contact_activities_performed_by ON contact_activities(performed_by);

-- Composite indexes for contact activities
CREATE INDEX IF NOT EXISTS idx_contact_activities_contact_date ON contact_activities(contact_id, activity_date DESC);
CREATE INDEX IF NOT EXISTS idx_contact_activities_business_date ON contact_activities(business_id, activity_date DESC);

-- Create contact notes table for detailed note management
CREATE TABLE IF NOT EXISTS contact_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    title VARCHAR(200),
    content TEXT NOT NULL,
    note_type VARCHAR(20) DEFAULT 'general' CHECK (note_type IN ('general', 'meeting', 'call', 'email', 'task', 'reminder')),
    is_private BOOLEAN DEFAULT false,
    
    -- User who created the note
    created_by TEXT NOT NULL, -- User ID from Supabase Auth
    
    -- Metadata
    created_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_modified TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    -- Tags for note organization
    tags JSONB DEFAULT '[]'::jsonb,
    
    CONSTRAINT contact_notes_tags_is_array CHECK (
        jsonb_typeof(tags) = 'array'
    )
);

-- Indexes for contact notes
CREATE INDEX IF NOT EXISTS idx_contact_notes_contact_id ON contact_notes(contact_id);
CREATE INDEX IF NOT EXISTS idx_contact_notes_business_id ON contact_notes(business_id);
CREATE INDEX IF NOT EXISTS idx_contact_notes_type ON contact_notes(note_type);
CREATE INDEX IF NOT EXISTS idx_contact_notes_created_by ON contact_notes(created_by);
CREATE INDEX IF NOT EXISTS idx_contact_notes_created_date ON contact_notes(created_date DESC);
CREATE INDEX IF NOT EXISTS idx_contact_notes_private ON contact_notes(is_private);

-- Text search index for note content
CREATE INDEX IF NOT EXISTS idx_contact_notes_content_search ON contact_notes USING gin(to_tsvector('english', 
    COALESCE(title, '') || ' ' || COALESCE(content, '')
));

-- JSONB index for note tags
CREATE INDEX IF NOT EXISTS idx_contact_notes_tags ON contact_notes USING gin(tags);

-- Create contact segments table for contact grouping and targeting
CREATE TABLE IF NOT EXISTS contact_segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    segment_type VARCHAR(20) DEFAULT 'manual' CHECK (segment_type IN ('manual', 'dynamic', 'imported')),
    
    -- Dynamic segment criteria (JSONB for flexibility)
    criteria JSONB,
    
    -- Segment metadata
    color VARCHAR(7), -- Hex color code
    is_active BOOLEAN DEFAULT true,
    
    -- User who created the segment
    created_by TEXT NOT NULL, -- User ID from Supabase Auth
    
    -- Metadata
    created_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_modified TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    CONSTRAINT contact_segments_business_name_unique UNIQUE (business_id, name),
    CONSTRAINT contact_segments_color_format CHECK (
        color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'
    ),
    CONSTRAINT contact_segments_criteria_is_object CHECK (
        criteria IS NULL OR jsonb_typeof(criteria) = 'object'
    )
);

-- Indexes for contact segments
CREATE INDEX IF NOT EXISTS idx_contact_segments_business_id ON contact_segments(business_id);
CREATE INDEX IF NOT EXISTS idx_contact_segments_type ON contact_segments(segment_type);
CREATE INDEX IF NOT EXISTS idx_contact_segments_active ON contact_segments(is_active);
CREATE INDEX IF NOT EXISTS idx_contact_segments_created_by ON contact_segments(created_by);

-- Create contact segment memberships table (many-to-many)
CREATE TABLE IF NOT EXISTS contact_segment_memberships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    segment_id UUID NOT NULL REFERENCES contact_segments(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Membership metadata
    added_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    added_by TEXT, -- User ID from Supabase Auth
    
    CONSTRAINT contact_segment_memberships_unique UNIQUE (contact_id, segment_id)
);

-- Indexes for contact segment memberships
CREATE INDEX IF NOT EXISTS idx_contact_segment_memberships_contact ON contact_segment_memberships(contact_id);
CREATE INDEX IF NOT EXISTS idx_contact_segment_memberships_segment ON contact_segment_memberships(segment_id);
CREATE INDEX IF NOT EXISTS idx_contact_segment_memberships_business ON contact_segment_memberships(business_id);

-- Create triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_last_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to relevant tables
CREATE TRIGGER update_contacts_last_modified 
    BEFORE UPDATE ON contacts 
    FOR EACH ROW EXECUTE FUNCTION update_last_modified_column();

CREATE TRIGGER update_contact_activities_last_modified 
    BEFORE UPDATE ON contact_activities 
    FOR EACH ROW EXECUTE FUNCTION update_last_modified_column();

CREATE TRIGGER update_contact_notes_last_modified 
    BEFORE UPDATE ON contact_notes 
    FOR EACH ROW EXECUTE FUNCTION update_last_modified_column();

CREATE TRIGGER update_contact_segments_last_modified 
    BEFORE UPDATE ON contact_segments 
    FOR EACH ROW EXECUTE FUNCTION update_last_modified_column();

-- Create function to update contact's last_contacted when activity is added
CREATE OR REPLACE FUNCTION update_contact_last_contacted()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the contact's last_contacted timestamp when a new activity is added
    IF NEW.activity_type IN ('call', 'email', 'meeting') THEN
        UPDATE contacts 
        SET last_contacted = NEW.activity_date 
        WHERE id = NEW.contact_id 
        AND (last_contacted IS NULL OR last_contacted < NEW.activity_date);
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger for contact activity updates
CREATE TRIGGER update_contact_last_contacted_trigger
    AFTER INSERT ON contact_activities
    FOR EACH ROW EXECUTE FUNCTION update_contact_last_contacted();

-- Create views for common contact queries
CREATE OR REPLACE VIEW contact_summary AS
SELECT 
    c.id,
    c.business_id,
    c.contact_type,
    c.status,
    c.priority,
    COALESCE(c.company_name, CONCAT(c.first_name, ' ', c.last_name)) as display_name,
    COALESCE(c.email, c.phone, c.mobile_phone) as primary_contact,
    c.estimated_value,
    c.assigned_to,
    c.created_date,
    c.last_contacted,
    (SELECT COUNT(*) FROM contact_activities ca WHERE ca.contact_id = c.id) as activity_count,
    (SELECT COUNT(*) FROM contact_notes cn WHERE cn.contact_id = c.id) as note_count
FROM contacts c
WHERE c.status != 'archived';

-- Grant permissions (adjust based on your user roles)
-- These would typically be handled by your application's database user management

-- Add comments for documentation
COMMENT ON TABLE contacts IS 'Core contact information for business customers, leads, prospects, vendors, partners, and contractors';
COMMENT ON TABLE contact_activities IS 'Historical record of all interactions and activities with contacts';
COMMENT ON TABLE contact_notes IS 'Detailed notes and observations about contacts';
COMMENT ON TABLE contact_segments IS 'Contact grouping and segmentation for targeted marketing and organization';
COMMENT ON TABLE contact_segment_memberships IS 'Many-to-many relationship between contacts and segments';

COMMENT ON COLUMN contacts.address IS 'JSONB field storing structured address information: {street_address, city, state, postal_code, country}';
COMMENT ON COLUMN contacts.tags IS 'JSONB array of string tags for contact categorization and filtering';
COMMENT ON COLUMN contacts.custom_fields IS 'JSONB object for storing business-specific custom contact fields';
COMMENT ON COLUMN contact_activities.activity_data IS 'JSONB object for storing activity-specific additional data';
COMMENT ON COLUMN contact_segments.criteria IS 'JSONB object defining dynamic segment rules and filters'; 