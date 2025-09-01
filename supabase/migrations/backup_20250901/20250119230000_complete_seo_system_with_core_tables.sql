-- =============================================
-- COMPLETE SEO SYSTEM WITH CORE TABLES
-- =============================================
-- This migration creates all necessary tables for the SEO Revenue Engine
-- including core business tables and SEO-specific tables

-- =============================================
-- CORE BUSINESS TABLES (if not exists)
-- =============================================

-- Users table (simplified for SEO system)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Businesses table (essential for SEO system)
CREATE TABLE IF NOT EXISTS businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    primary_trade VARCHAR(100),
    secondary_trades TEXT[],
    years_in_business INTEGER DEFAULT 0,
    certifications TEXT[],
    service_radius INTEGER DEFAULT 25,
    emergency_available BOOLEAN DEFAULT false,
    year_established INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Business services (for SEO page generation)
CREATE TABLE IF NOT EXISTS business_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL,
    service_slug VARCHAR(100) NOT NULL,
    description TEXT,
    price_range_min DECIMAL(10,2),
    price_range_max DECIMAL(10,2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, service_slug)
);

-- =============================================
-- SEO TEMPLATES
-- =============================================

-- SEO page templates for different page types
CREATE TABLE IF NOT EXISTS seo_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    page_type VARCHAR(50) NOT NULL, -- 'service_location', 'service', 'location', 'emergency_service'
    content JSONB NOT NULL, -- Template structure with variables
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- SEO CONFIGURATION
-- =============================================

-- Service-specific SEO configuration
CREATE TABLE IF NOT EXISTS service_seo_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(100) NOT NULL,
    service_slug VARCHAR(100) NOT NULL UNIQUE,
    target_keywords TEXT[],
    priority_score INTEGER DEFAULT 50, -- 1-100, higher = more important
    enable_llm_enhancement BOOLEAN DEFAULT false,
    meta_title_template TEXT,
    meta_description_template TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- LOCATION PAGES
-- =============================================

-- Location-specific pages and data
CREATE TABLE IF NOT EXISTS location_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    county VARCHAR(100),
    slug VARCHAR(200) NOT NULL UNIQUE, -- 'austin-tx'
    zip_codes TEXT[],
    neighborhoods TEXT[],
    population INTEGER,
    median_income INTEGER,
    monthly_searches INTEGER DEFAULT 0,
    competition_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high'
    conversion_potential DECIMAL(3,2) DEFAULT 0.05, -- 0.00-1.00
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(city, state)
);

-- =============================================
-- SERVICE + LOCATION COMBINATIONS
-- =============================================

-- Specific service+location page configurations
CREATE TABLE IF NOT EXISTS service_location_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_slug VARCHAR(100) NOT NULL,
    location_slug VARCHAR(200) NOT NULL,
    page_url VARCHAR(500) NOT NULL UNIQUE, -- '/services/hvac-repair/austin-tx'
    priority_score INTEGER DEFAULT 50,
    enable_llm_enhancement BOOLEAN DEFAULT false,
    target_keywords TEXT[],
    monthly_search_volume INTEGER DEFAULT 0,
    competition_difficulty VARCHAR(20) DEFAULT 'medium',
    estimated_monthly_visitors INTEGER DEFAULT 0,
    estimated_monthly_revenue DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(service_slug, location_slug)
);

-- =============================================
-- GENERATED SEO PAGES
-- =============================================

-- Storage for generated SEO pages
CREATE TABLE IF NOT EXISTS generated_seo_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    page_url VARCHAR(500) NOT NULL,
    page_type VARCHAR(50) NOT NULL, -- 'service_location', 'service', 'location', etc.
    
    -- SEO Content
    title VARCHAR(200) NOT NULL,
    meta_description VARCHAR(300),
    h1_heading VARCHAR(200),
    content TEXT,
    schema_markup JSONB,
    
    -- Generation info
    generation_method VARCHAR(20) NOT NULL, -- 'template', 'llm_enhanced', 'fallback'
    template_used VARCHAR(100),
    target_keywords TEXT[],
    
    -- Performance tracking
    monthly_visitors INTEGER DEFAULT 0,
    monthly_conversions INTEGER DEFAULT 0,
    monthly_revenue DECIMAL(10,2) DEFAULT 0,
    search_ranking INTEGER,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, page_url)
);

-- =============================================
-- SEO PERFORMANCE TRACKING
-- =============================================

-- Track SEO performance over time
CREATE TABLE IF NOT EXISTS seo_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    page_url VARCHAR(500),
    
    -- Metrics
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue DECIMAL(10,2) DEFAULT 0,
    average_position DECIMAL(4,1),
    
    -- Time period
    measured_at TIMESTAMPTZ DEFAULT NOW(),
    period_type VARCHAR(20) DEFAULT 'daily', -- 'daily', 'weekly', 'monthly'
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- WEBSITE DEPLOYMENTS
-- =============================================

-- Website deployments tracking
CREATE TABLE IF NOT EXISTS website_deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Deployment info
    deployment_type VARCHAR(20) NOT NULL DEFAULT 'full_seo',
    status VARCHAR(20) NOT NULL DEFAULT 'queued',
    
    -- Configuration
    config JSONB NOT NULL DEFAULT '{}',
    
    -- Results
    pages_generated INTEGER DEFAULT 0,
    template_pages INTEGER DEFAULT 0,
    enhanced_pages INTEGER DEFAULT 0,
    website_url TEXT,
    cloudflare_deployment_id TEXT,
    
    -- Timing
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    estimated_completion TIMESTAMPTZ,
    generation_time_seconds INTEGER,
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- Critical indexes for SEO system performance
CREATE INDEX IF NOT EXISTS idx_businesses_owner ON businesses(owner_id);
CREATE INDEX IF NOT EXISTS idx_business_services_business ON business_services(business_id);
CREATE INDEX IF NOT EXISTS idx_generated_pages_business_url ON generated_seo_pages(business_id, page_url);
CREATE INDEX IF NOT EXISTS idx_generated_pages_type ON generated_seo_pages(page_type);
CREATE INDEX IF NOT EXISTS idx_website_deployments_business_status ON website_deployments(business_id, status);
CREATE INDEX IF NOT EXISTS idx_seo_performance_business_date ON seo_performance(business_id, measured_at);
CREATE INDEX IF NOT EXISTS idx_location_pages_slug ON location_pages(slug);
CREATE INDEX IF NOT EXISTS idx_service_location_url ON service_location_pages(page_url);

-- =============================================
-- SEED DATA - SEO TEMPLATES
-- =============================================

-- Insert essential SEO templates
INSERT INTO seo_templates (name, page_type, content, is_active) VALUES
(
    'service_location',
    'service_location',
    '{
        "title": "{service_name} in {city}, {state} | 24/7 Service | {business_name}",
        "meta_description": "Professional {service_name} services in {city}, {state}. Same-day service, licensed & insured. Call {phone} for free estimate.",
        "h1_heading": "Expert {service_name} Services in {city}, {state}",
        "content": "Need reliable {service_name} in {city}? {business_name} has been serving {city} residents for {years_experience} years with professional, affordable {service_name} solutions. Our certified technicians provide comprehensive {service_name} services including installation, repair, and maintenance. We are dedicated to providing top-notch service to our community in {city}, {state}. Contact us today for a free estimate!",
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "Service",
            "serviceType": "{service_name}",
            "areaServed": {
                "@type": "City",
                "name": "{city}"
            },
            "provider": {
                "@type": "LocalBusiness",
                "name": "{business_name}",
                "telephone": "{phone}",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "{city}",
                    "addressRegion": "{state}"
                }
            }
        },
        "target_keywords": ["{service_name} {city}", "{city} {service_name} repair", "{business_name} {service_name}"]
    }',
    true
),
(
    'service',
    'service',
    '{
        "title": "{service_name} Services | Professional {service_name} | {business_name}",
        "meta_description": "Comprehensive {service_name} services by {business_name}. Expert technicians, competitive pricing, and guaranteed satisfaction.",
        "h1_heading": "Professional {service_name} Services",
        "content": "Looking for reliable {service_name} services? {business_name} provides comprehensive {service_name} solutions for residential and commercial clients. Our experienced team delivers quality workmanship with competitive pricing and exceptional customer service.",
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "Service",
            "serviceType": "{service_name}",
            "provider": {
                "@type": "LocalBusiness",
                "name": "{business_name}"
            }
        },
        "target_keywords": ["{service_name} services", "{business_name} {service_name}", "professional {service_name}"]
    }',
    true
),
(
    'location',
    'location',
    '{
        "title": "{business_name} in {city}, {state} | Local {primary_trade} Services",
        "meta_description": "Local {primary_trade} services in {city}, {state}. {business_name} is your trusted local expert for all {primary_trade} needs.",
        "h1_heading": "{business_name} Serving {city}, {state}",
        "content": "Proudly serving {city}, {state} and surrounding areas, {business_name} is your local {primary_trade} expert. We provide comprehensive {primary_trade} services to homeowners and businesses throughout {city}.",
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": "{business_name}",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "{city}",
                "addressRegion": "{state}"
            }
        },
        "target_keywords": ["{city} {primary_trade}", "{business_name} {city}", "local {primary_trade} {city}"]
    }',
    true
),
(
    'emergency_service',
    'emergency_service',
    '{
        "title": "Emergency {service_name} in {city}, {state} | 24/7 Service | {business_name}",
        "meta_description": "24/7 emergency {service_name} in {city}. Fast response, licensed technicians. Call {phone} now for immediate service!",
        "h1_heading": "24/7 Emergency {service_name} in {city}, {state}",
        "content": "Need emergency {service_name} in {city}? {business_name} provides 24/7 emergency {service_name} services with fast response times. Our licensed technicians are available around the clock to handle your urgent {service_name} needs.",
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "EmergencyService",
            "serviceType": "{service_name}",
            "areaServed": {
                "@type": "City",
                "name": "{city}"
            },
            "provider": {
                "@type": "LocalBusiness",
                "name": "{business_name}",
                "telephone": "{phone}"
            }
        },
        "target_keywords": ["emergency {service_name} {city}", "24/7 {service_name} {city}", "{service_name} emergency {city}"]
    }',
    true
)
ON CONFLICT (name) DO NOTHING;

-- =============================================
-- SEED DATA - COMMON SERVICES
-- =============================================

-- Insert common home service SEO configurations
INSERT INTO service_seo_config (service_name, service_slug, target_keywords, priority_score, enable_llm_enhancement) VALUES
('HVAC Repair', 'hvac-repair', ARRAY['hvac repair', 'ac repair', 'heating repair', 'air conditioning repair'], 90, true),
('Plumbing Repair', 'plumbing-repair', ARRAY['plumber', 'plumbing repair', 'emergency plumber', 'drain cleaning'], 85, true),
('Electrical Repair', 'electrical-repair', ARRAY['electrician', 'electrical repair', 'electrical service', 'wiring'], 80, true),
('AC Installation', 'ac-installation', ARRAY['ac installation', 'air conditioning installation', 'hvac installation'], 85, true),
('Water Heater Repair', 'water-heater-repair', ARRAY['water heater repair', 'hot water heater', 'tankless water heater'], 75, false),
('Furnace Repair', 'furnace-repair', ARRAY['furnace repair', 'heating repair', 'furnace service'], 70, false),
('Duct Cleaning', 'duct-cleaning', ARRAY['duct cleaning', 'air duct cleaning', 'hvac cleaning'], 60, false),
('Emergency HVAC', 'emergency-hvac', ARRAY['emergency hvac', '24/7 hvac', 'emergency ac repair'], 95, true),
('Commercial HVAC', 'commercial-hvac', ARRAY['commercial hvac', 'commercial air conditioning', 'business hvac'], 70, false),
('Preventive Maintenance', 'preventive-maintenance', ARRAY['hvac maintenance', 'ac tune up', 'preventive maintenance'], 50, false)
ON CONFLICT (service_slug) DO NOTHING;

-- =============================================
-- SEED DATA - SAMPLE LOCATIONS
-- =============================================

-- Insert sample Texas locations for testing
INSERT INTO location_pages (city, state, county, slug, zip_codes, neighborhoods, population, median_income, monthly_searches, competition_level, conversion_potential) VALUES
('Austin', 'TX', 'Travis', 'austin-tx', ARRAY['78701', '78702', '78703', '78704', '78705'], ARRAY['Downtown', 'South Congress', 'East Austin', 'Zilker'], 1000000, 75000, 5000, 'high', 0.08),
('Round Rock', 'TX', 'Williamson', 'round-rock-tx', ARRAY['78664', '78665', '78681'], ARRAY['Downtown Round Rock', 'Teravista', 'Walsh Ranch'], 130000, 85000, 1200, 'medium', 0.12),
('Cedar Park', 'TX', 'Williamson', 'cedar-park-tx', ARRAY['78613', '78630'], ARRAY['Cedar Park Center', 'Buttercup Creek', 'Anderson Mill'], 80000, 90000, 800, 'low', 0.15),
('Pflugerville', 'TX', 'Travis', 'pflugerville-tx', ARRAY['78660'], ARRAY['Falcon Pointe', 'Springbrook Centre', 'Wilshire'], 70000, 80000, 600, 'low', 0.18),
('Georgetown', 'TX', 'Williamson', 'georgetown-tx', ARRAY['78626', '78628', '78633'], ARRAY['Downtown Georgetown', 'Sun City', 'Wolf Ranch'], 80000, 75000, 700, 'medium', 0.10)
ON CONFLICT (city, state) DO NOTHING;

-- =============================================
-- SEED DATA - SAMPLE BUSINESS FOR TESTING
-- =============================================

-- Insert a sample user and business for testing
INSERT INTO users (id, email, full_name) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'demo@hero365.app', 'Demo User')
ON CONFLICT (email) DO NOTHING;

INSERT INTO businesses (
    id, 
    owner_id, 
    name, 
    email, 
    phone, 
    address, 
    city, 
    state, 
    zip_code, 
    primary_trade, 
    secondary_trades, 
    years_in_business, 
    certifications, 
    service_radius, 
    emergency_available, 
    year_established
) VALUES (
    '550e8400-e29b-41d4-a716-446655440001',
    '550e8400-e29b-41d4-a716-446655440000',
    'Elite HVAC Austin',
    'info@elitehvac.com',
    '(512) 555-0100',
    '123 Main St',
    'Austin',
    'TX',
    '78701',
    'HVAC',
    ARRAY['Plumbing', 'Electrical'],
    15,
    ARRAY['NATE', 'EPA'],
    25,
    true,
    2008
) ON CONFLICT (id) DO NOTHING;

-- Insert sample services for the demo business
INSERT INTO business_services (business_id, service_name, service_slug, description, price_range_min, price_range_max) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'HVAC Repair', 'hvac-repair', 'Professional HVAC repair services', 100, 500),
('550e8400-e29b-41d4-a716-446655440001', 'AC Installation', 'ac-installation', 'Complete AC system installation', 2000, 8000),
('550e8400-e29b-41d4-a716-446655440001', 'Emergency HVAC', 'emergency-hvac', '24/7 emergency HVAC services', 150, 800)
ON CONFLICT (business_id, service_slug) DO NOTHING;

COMMIT;
