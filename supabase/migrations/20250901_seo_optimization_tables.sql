-- =============================================
-- SEO OPTIMIZATION TABLES FOR HERO365
-- =============================================
-- This migration creates the database schema for advanced SEO features
-- including dynamic service-location pages, Google integrations, and
-- performance tracking for maximum local search visibility.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis"; -- For geographic calculations

-- =============================================
-- SERVICE SEO CONFIGURATION
-- =============================================
CREATE TABLE IF NOT EXISTS service_seo_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES business_services(id) ON DELETE CASCADE,
    
    -- SEO Content Templates (with variable placeholders)
    meta_title_template TEXT DEFAULT '{service_name} in {city}, {state} | 24/7 Emergency Service',
    meta_description_template TEXT DEFAULT 'Professional {service_name} services in {city}. Same-day service, licensed & insured. Call {phone} for free estimate.',
    h1_template TEXT DEFAULT '{service_name} Services in {city}, {state}',
    content_template TEXT,
    
    -- Keywords
    primary_keywords TEXT[] DEFAULT '{}',
    secondary_keywords TEXT[] DEFAULT '{}',
    long_tail_keywords TEXT[] DEFAULT '{}',
    negative_keywords TEXT[] DEFAULT '{}', -- Keywords to avoid
    
    -- Schema data
    service_schema JSONB DEFAULT '{}',
    faqs JSONB DEFAULT '[]', -- Array of FAQ objects
    how_to_steps JSONB DEFAULT '[]', -- How-to schema steps
    
    -- Content variations
    emergency_content TEXT,
    commercial_content TEXT,
    residential_content TEXT,
    
    -- SEO settings
    priority DECIMAL(2,1) DEFAULT 0.5 CHECK (priority >= 0 AND priority <= 1),
    change_frequency VARCHAR(20) DEFAULT 'weekly', -- always, hourly, daily, weekly, monthly, yearly, never
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, service_id)
);

-- =============================================
-- LOCATION PAGES
-- =============================================
CREATE TABLE IF NOT EXISTS location_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Location identifiers
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    county VARCHAR(100),
    zip_codes TEXT[] DEFAULT '{}',
    neighborhoods TEXT[] DEFAULT '{}',
    slug VARCHAR(200) NOT NULL, -- URL slug (e.g., "austin-tx")
    
    -- Geographic data (for radius calculations)
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    geometry GEOGRAPHY(POINT, 4326), -- PostGIS point for spatial queries
    service_radius_miles INTEGER DEFAULT 25,
    
    -- SEO Content
    meta_title TEXT,
    meta_description TEXT,
    hero_content TEXT,
    about_area TEXT,
    why_choose_us TEXT,
    local_testimonials JSONB DEFAULT '[]',
    
    -- Local market data
    population INTEGER,
    median_income INTEGER,
    demographics JSONB DEFAULT '{}',
    climate_info JSONB DEFAULT '{}', -- Relevant for HVAC
    competitors JSONB DEFAULT '[]',
    local_keywords TEXT[] DEFAULT '{}',
    seasonal_keywords JSONB DEFAULT '{}', -- Keywords by season
    
    -- Performance metrics
    monthly_searches INTEGER,
    competition_level VARCHAR(20) CHECK (competition_level IN ('low', 'medium', 'high', 'very_high')),
    average_cpc DECIMAL(10, 2), -- Cost per click for PPC comparison
    
    -- Local business associations
    local_certifications TEXT[] DEFAULT '{}',
    local_partnerships TEXT[] DEFAULT '{}',
    community_involvement TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_primary BOOLEAN DEFAULT false, -- Primary service area
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, slug),
    INDEX idx_location_geo USING GIST(geometry),
    INDEX idx_location_business (business_id, is_active)
);

-- =============================================
-- SERVICE-LOCATION COMBINATION PAGES
-- =============================================
CREATE TABLE IF NOT EXISTS service_location_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES business_services(id) ON DELETE CASCADE,
    location_id UUID NOT NULL REFERENCES location_pages(id) ON DELETE CASCADE,
    
    -- Page URL
    slug VARCHAR(400) NOT NULL, -- Full slug (e.g., "ac-repair/austin-tx")
    page_type VARCHAR(20) DEFAULT 'standard' CHECK (page_type IN ('standard', 'emergency', 'commercial', 'residential')),
    
    -- Custom content (overrides templates)
    custom_title TEXT,
    custom_description TEXT,
    custom_h1 TEXT,
    custom_content TEXT,
    
    -- Local service details
    local_price_modifier DECIMAL(3, 2) DEFAULT 1.0, -- Price adjustment for this location
    local_availability TEXT,
    local_response_time VARCHAR(100),
    local_team_info TEXT,
    
    -- Performance tracking
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    calls INTEGER DEFAULT 0,
    form_submissions INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue_generated DECIMAL(10, 2) DEFAULT 0,
    
    -- SEO metrics
    current_ranking INTEGER,
    best_ranking INTEGER,
    target_keywords TEXT[] DEFAULT '{}',
    ranking_history JSONB DEFAULT '[]', -- Array of {date, position, keyword}
    
    -- A/B testing
    variant VARCHAR(10) DEFAULT 'A',
    variant_performance JSONB DEFAULT '{}',
    
    -- Status
    is_published BOOLEAN DEFAULT true,
    needs_review BOOLEAN DEFAULT false,
    last_reviewed_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(service_id, location_id, page_type),
    INDEX idx_service_location_slug (slug),
    INDEX idx_service_location_performance (business_id, conversions DESC)
);

-- =============================================
-- SEO PERFORMANCE TRACKING
-- =============================================
CREATE TABLE IF NOT EXISTS seo_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    page_url TEXT NOT NULL,
    page_type VARCHAR(50), -- 'service', 'location', 'service-location', 'blog', etc.
    
    -- Google Search Console metrics
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    ctr DECIMAL(5, 2), -- Click-through rate
    average_position DECIMAL(5, 2),
    
    -- Core Web Vitals
    lcp_score DECIMAL(5, 2), -- Largest Contentful Paint
    fid_score DECIMAL(5, 2), -- First Input Delay
    cls_score DECIMAL(5, 2), -- Cumulative Layout Shift
    ttfb_ms INTEGER, -- Time to First Byte
    
    -- Page metrics
    page_load_time_ms INTEGER,
    bounce_rate DECIMAL(5, 2),
    average_time_on_page INTEGER, -- seconds
    
    -- Rankings by keyword
    keyword_rankings JSONB DEFAULT '{}', -- {keyword: position}
    featured_snippets TEXT[] DEFAULT '{}', -- Keywords with featured snippets
    
    -- Backlinks
    backlink_count INTEGER DEFAULT 0,
    referring_domains INTEGER DEFAULT 0,
    domain_authority INTEGER,
    
    measured_at DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, page_url, measured_at),
    INDEX idx_seo_performance_date (business_id, measured_at DESC)
);

-- =============================================
-- GOOGLE INTEGRATIONS
-- =============================================
CREATE TABLE IF NOT EXISTS google_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Google My Business
    gmb_account_id VARCHAR(255),
    gmb_location_id VARCHAR(255),
    gmb_access_token TEXT,
    gmb_refresh_token TEXT,
    gmb_last_sync TIMESTAMPTZ,
    gmb_sync_enabled BOOLEAN DEFAULT false,
    
    -- Google Search Console
    gsc_site_url VARCHAR(255),
    gsc_access_token TEXT,
    gsc_refresh_token TEXT,
    gsc_verified BOOLEAN DEFAULT false,
    gsc_last_sync TIMESTAMPTZ,
    
    -- Google Analytics
    ga_property_id VARCHAR(50),
    ga_measurement_id VARCHAR(50),
    ga_access_token TEXT,
    ga_refresh_token TEXT,
    
    -- Google Ads (for keyword data)
    gads_customer_id VARCHAR(50),
    gads_access_token TEXT,
    gads_refresh_token TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id)
);

-- =============================================
-- COMPETITOR TRACKING
-- =============================================
CREATE TABLE IF NOT EXISTS competitor_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    location_id UUID REFERENCES location_pages(id) ON DELETE CASCADE,
    
    competitor_name VARCHAR(255) NOT NULL,
    competitor_website VARCHAR(255),
    competitor_gmb_id VARCHAR(255),
    
    -- Rankings
    tracked_keywords JSONB DEFAULT '[]', -- Array of {keyword, our_rank, their_rank}
    
    -- Metrics
    domain_authority INTEGER,
    page_authority INTEGER,
    backlink_count INTEGER,
    review_count INTEGER,
    average_rating DECIMAL(2, 1),
    
    -- Content analysis
    services_offered TEXT[] DEFAULT '{}',
    unique_selling_points TEXT[] DEFAULT '{}',
    pricing_visible BOOLEAN DEFAULT false,
    content_topics TEXT[] DEFAULT '{}',
    
    last_analyzed TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_competitor_business (business_id)
);

-- =============================================
-- AUTOMATED CONTENT GENERATION
-- =============================================
CREATE TABLE IF NOT EXISTS seo_content_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name VARCHAR(100) NOT NULL,
    template_type VARCHAR(50) NOT NULL, -- 'service', 'location', 'blog', 'faq'
    
    -- Template content with variables
    title_template TEXT NOT NULL,
    intro_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    conclusion_template TEXT,
    cta_template TEXT,
    
    -- Variables used in template
    required_variables TEXT[] DEFAULT '{}',
    optional_variables TEXT[] DEFAULT '{}',
    
    -- SEO guidelines
    min_word_count INTEGER DEFAULT 500,
    max_word_count INTEGER DEFAULT 3000,
    keyword_density_percent DECIMAL(3, 1) DEFAULT 1.5,
    
    -- Performance
    average_ranking DECIMAL(5, 2),
    conversion_rate DECIMAL(5, 2),
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- FUNCTIONS AND TRIGGERS
-- =============================================

-- Function to generate location page slug
CREATE OR REPLACE FUNCTION generate_location_slug(city TEXT, state TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(REGEXP_REPLACE(city || '-' || state, '[^a-z0-9-]', '-', 'g'));
END;
$$ LANGUAGE plpgsql;

-- Function to calculate distance between two points
CREATE OR REPLACE FUNCTION calculate_distance_miles(
    lat1 DECIMAL, lon1 DECIMAL,
    lat2 DECIMAL, lon2 DECIMAL
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN ST_Distance(
        ST_MakePoint(lon1, lat1)::geography,
        ST_MakePoint(lon2, lat2)::geography
    ) / 1609.344; -- Convert meters to miles
END;
$$ LANGUAGE plpgsql;

-- Trigger to update geometry when coordinates change
CREATE OR REPLACE FUNCTION update_location_geometry()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.geometry = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_location_geometry_trigger
BEFORE INSERT OR UPDATE OF latitude, longitude ON location_pages
FOR EACH ROW EXECUTE FUNCTION update_location_geometry();

-- Function to generate service-location combinations
CREATE OR REPLACE FUNCTION generate_service_location_pages(p_business_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_service RECORD;
    v_location RECORD;
BEGIN
    FOR v_service IN 
        SELECT id, name FROM business_services 
        WHERE business_id = p_business_id AND is_active = true
    LOOP
        FOR v_location IN 
            SELECT id, slug FROM location_pages 
            WHERE business_id = p_business_id AND is_active = true
        LOOP
            INSERT INTO service_location_pages (
                business_id, service_id, location_id, slug
            ) VALUES (
                p_business_id, 
                v_service.id, 
                v_location.id,
                LOWER(REGEXP_REPLACE(v_service.name, '[^a-z0-9]', '-', 'g')) || '/' || v_location.slug
            )
            ON CONFLICT (service_id, location_id, page_type) DO NOTHING;
            
            v_count := v_count + 1;
        END LOOP;
    END LOOP;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================
CREATE INDEX idx_service_seo_business ON service_seo_config(business_id);
CREATE INDEX idx_location_pages_active ON location_pages(business_id, is_active) WHERE is_active = true;
CREATE INDEX idx_service_location_published ON service_location_pages(business_id, is_published) WHERE is_published = true;
CREATE INDEX idx_seo_performance_recent ON seo_performance(business_id, measured_at DESC);
CREATE INDEX idx_competitor_location ON competitor_analysis(location_id);

-- =============================================
-- ROW LEVEL SECURITY
-- =============================================
ALTER TABLE service_seo_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE location_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_location_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE seo_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE seo_content_templates ENABLE ROW LEVEL SECURITY;

-- Policies for business owners
CREATE POLICY service_seo_config_policy ON service_seo_config
    FOR ALL USING (
        business_id IN (
            SELECT business_id FROM user_businesses 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY location_pages_policy ON location_pages
    FOR ALL USING (
        business_id IN (
            SELECT business_id FROM user_businesses 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY service_location_pages_policy ON service_location_pages
    FOR ALL USING (
        business_id IN (
            SELECT business_id FROM user_businesses 
            WHERE user_id = auth.uid()
        )
    );

-- =============================================
-- SEED DATA FOR TEMPLATES
-- =============================================
INSERT INTO seo_content_templates (template_name, template_type, title_template, intro_template, body_template) VALUES
(
    'HVAC Service Page',
    'service',
    '{service_name} in {city}, {state} | 24/7 Emergency Service | {business_name}',
    'Looking for reliable {service_name} in {city}? {business_name} provides professional {service_name} services with {years_experience} years of experience serving {city} and surrounding areas.',
    'Our certified technicians specialize in {service_name} for both residential and commercial properties in {city}, {state}. We offer same-day service, transparent pricing, and a 100% satisfaction guarantee. Whether you need emergency repairs or scheduled maintenance, our team is available 24/7 to ensure your comfort.'
),
(
    'Location Hub Page',
    'location',
    'HVAC Services in {city}, {state} | Heating & Cooling Experts | {business_name}',
    '{business_name} is {city}''s trusted source for professional HVAC services. From AC repair to heating installation, we serve all of {city} with fast, reliable service.',
    'Serving {city} for over {years_experience} years, we understand the unique climate challenges of {state}. Our local team provides comprehensive HVAC services including repairs, installations, and maintenance for all major brands. We''re proud to be {city}''s highest-rated HVAC contractor with over {review_count} five-star reviews.'
);

-- =============================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================
COMMENT ON TABLE service_seo_config IS 'SEO configuration for each service offered by a business';
COMMENT ON TABLE location_pages IS 'Location-specific landing pages for local SEO';
COMMENT ON TABLE service_location_pages IS 'Combination pages for service + location targeting';
COMMENT ON TABLE seo_performance IS 'Daily SEO performance metrics from various sources';
COMMENT ON TABLE google_integrations IS 'Google service API credentials and settings';
COMMENT ON TABLE competitor_analysis IS 'Competitor tracking for each market';
COMMENT ON TABLE seo_content_templates IS 'Reusable content templates for page generation';
