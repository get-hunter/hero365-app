-- =============================================
-- TRADE TAXONOMY SYSTEM - Clean Profile-Activity Model
-- =============================================

-- Create trade profiles table
CREATE TABLE IF NOT EXISTS trade_profiles (
    slug text PRIMARY KEY,
    name text NOT NULL,
    synonyms text[] DEFAULT '{}',
    segments text CHECK (segments IN ('residential','commercial','both')) DEFAULT 'both',
    icon text,
    description text,
    created_at timestamptz DEFAULT NOW(),
    updated_at timestamptz DEFAULT NOW()
);

-- Create trade activities table  
CREATE TABLE IF NOT EXISTS trade_activities (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    trade_slug text NOT NULL REFERENCES trade_profiles(slug) ON DELETE CASCADE,
    slug text UNIQUE NOT NULL,
    name text NOT NULL,
    synonyms text[] DEFAULT '{}',
    tags text[] DEFAULT '{}',
    default_booking_fields jsonb DEFAULT '[]',
    required_booking_fields jsonb DEFAULT '[]',
    created_at timestamptz DEFAULT NOW(),
    updated_at timestamptz DEFAULT NOW()
);

-- Create activity_service_templates mapping table
CREATE TABLE IF NOT EXISTS activity_service_templates (
    activity_id uuid NOT NULL REFERENCES trade_activities(id) ON DELETE CASCADE,
    template_slug text NOT NULL,
    created_at timestamptz DEFAULT NOW(),
    PRIMARY KEY (activity_id, template_slug)
);

-- Add new columns to existing service_templates table (if it exists)
-- Handle both cases: table exists or doesn't exist
DO $$
BEGIN
    -- Check if service_templates table exists
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'service_templates') THEN
        -- Add new columns to existing table
        ALTER TABLE service_templates 
        ADD COLUMN IF NOT EXISTS template_slug text,
        ADD COLUMN IF NOT EXISTS activity_slug text,
        ADD COLUMN IF NOT EXISTS pricing_config jsonb DEFAULT '{}',
        ADD COLUMN IF NOT EXISTS default_booking_fields jsonb DEFAULT '[]',
        ADD COLUMN IF NOT EXISTS required_booking_fields jsonb DEFAULT '[]',
        ADD COLUMN IF NOT EXISTS status text DEFAULT 'active' CHECK (status IN ('active','draft','deprecated')),
        ADD COLUMN IF NOT EXISTS version integer DEFAULT 1,
        ADD COLUMN IF NOT EXISTS is_emergency boolean DEFAULT false,
        ADD COLUMN IF NOT EXISTS is_common boolean DEFAULT false;
        
        -- Add unique constraint on template_slug if it doesn't exist
        IF NOT EXISTS (SELECT FROM information_schema.table_constraints 
                      WHERE table_name = 'service_templates' AND constraint_name = 'service_templates_template_slug_key') THEN
            ALTER TABLE service_templates ADD CONSTRAINT service_templates_template_slug_key UNIQUE (template_slug);
        END IF;
        
        -- Add foreign key constraint to activity_slug if it doesn't exist
        IF NOT EXISTS (SELECT FROM information_schema.table_constraints 
                      WHERE table_name = 'service_templates' AND constraint_name = 'service_templates_activity_slug_fkey') THEN
            ALTER TABLE service_templates ADD CONSTRAINT service_templates_activity_slug_fkey 
            FOREIGN KEY (activity_slug) REFERENCES trade_activities(slug) ON DELETE SET NULL;
        END IF;
    ELSE
        -- Create new service_templates table
        CREATE TABLE service_templates (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            template_slug text UNIQUE NOT NULL,
            activity_slug text REFERENCES trade_activities(slug) ON DELETE SET NULL,
            name text NOT NULL,
            description text,
            pricing_model text CHECK (pricing_model IN ('fixed','hourly','per_unit','tiered','quote')) DEFAULT 'quote',
            pricing_config jsonb DEFAULT '{}',
            unit_of_measure text DEFAULT 'service',
            default_booking_fields jsonb DEFAULT '[]',
            required_booking_fields jsonb DEFAULT '[]',
            is_common boolean DEFAULT false,
            is_emergency boolean DEFAULT false,
            status text CHECK (status IN ('active','draft','deprecated')) DEFAULT 'active',
            version integer DEFAULT 1,
            usage_count integer DEFAULT 0,
            created_at timestamptz DEFAULT NOW(),
            updated_at timestamptz DEFAULT NOW()
        );
    END IF;
END $$;

-- Add primary_trade_slug and selected_activity_slugs to businesses table
ALTER TABLE businesses 
ADD COLUMN IF NOT EXISTS primary_trade_slug text,
ADD COLUMN IF NOT EXISTS selected_activity_slugs text[] DEFAULT '{}';

-- Add foreign key constraint for primary_trade_slug if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.table_constraints 
                  WHERE table_name = 'businesses' AND constraint_name = 'businesses_primary_trade_slug_fkey') THEN
        ALTER TABLE businesses ADD CONSTRAINT businesses_primary_trade_slug_fkey 
        FOREIGN KEY (primary_trade_slug) REFERENCES trade_profiles(slug) ON DELETE SET NULL;
    END IF;
END $$;

-- Update business_services to support new model
ALTER TABLE business_services 
ADD COLUMN IF NOT EXISTS adopted_from_slug text,
ADD COLUMN IF NOT EXISTS template_version integer DEFAULT 1,
ADD COLUMN IF NOT EXISTS pricing_config jsonb DEFAULT '{}',
ADD COLUMN IF NOT EXISTS booking_settings jsonb DEFAULT '{}';

-- Create service_template_adoptions table for tracking
CREATE TABLE IF NOT EXISTS service_template_adoptions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    template_slug text NOT NULL,
    activity_slug text,
    adopted_at timestamptz DEFAULT NOW(),
    customizations_applied boolean DEFAULT false,
    UNIQUE(business_id, template_slug)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_trade_activities_trade_slug ON trade_activities(trade_slug);
CREATE INDEX IF NOT EXISTS idx_trade_activities_slug ON trade_activities(slug);
CREATE INDEX IF NOT EXISTS idx_service_templates_activity_slug ON service_templates(activity_slug);
CREATE INDEX IF NOT EXISTS idx_service_templates_template_slug ON service_templates(template_slug);
CREATE INDEX IF NOT EXISTS idx_service_templates_status ON service_templates(status);
CREATE INDEX IF NOT EXISTS idx_businesses_primary_trade_slug ON businesses(primary_trade_slug);
CREATE INDEX IF NOT EXISTS idx_businesses_selected_activity_slugs ON businesses USING GIN(selected_activity_slugs);
CREATE INDEX IF NOT EXISTS idx_business_services_adopted_from_slug ON business_services(adopted_from_slug);
CREATE INDEX IF NOT EXISTS idx_service_template_adoptions_business_id ON service_template_adoptions(business_id);
CREATE INDEX IF NOT EXISTS idx_service_template_adoptions_template_slug ON service_template_adoptions(template_slug);

-- Enable RLS on new tables
ALTER TABLE trade_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE trade_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_service_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_template_adoptions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for public read access to taxonomy data
CREATE POLICY "Trade profiles are publicly readable" ON trade_profiles FOR SELECT USING (true);
CREATE POLICY "Trade activities are publicly readable" ON trade_activities FOR SELECT USING (true);
CREATE POLICY "Activity templates mapping is publicly readable" ON activity_service_templates FOR SELECT USING (true);

-- Create RLS policies for service template adoptions (business-scoped)
CREATE POLICY "Users can view their business adoptions" ON service_template_adoptions 
FOR SELECT USING (
    business_id IN (
        SELECT business_id FROM business_memberships 
        WHERE user_id = auth.uid() AND status = 'active'
    )
);

CREATE POLICY "Users can create adoptions for their business" ON service_template_adoptions 
FOR INSERT WITH CHECK (
    business_id IN (
        SELECT business_id FROM business_memberships 
        WHERE user_id = auth.uid() AND status = 'active'
    )
);

COMMIT;