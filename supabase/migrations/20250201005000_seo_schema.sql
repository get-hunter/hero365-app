-- =============================================
-- SEO REVENUE ENGINE SCHEMA (CONSOLIDATED)
-- =============================================
-- Essential SEO tables for 900+ page generation
-- Overlapping functionality moved to website builder system
-- Depends on: businesses, website_build_jobs, website_analytics tables

-- =============================================
-- SEO TEMPLATES (ESSENTIAL - NO EQUIVALENT)
-- =============================================

CREATE TABLE seo_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    page_type VARCHAR(50) NOT NULL, -- 'service_location', 'service', 'location', 'emergency_service'
    content JSONB NOT NULL, -- Template structure with variables
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- SERVICE SEO CONFIGURATION (ESSENTIAL)
-- =============================================

CREATE TABLE service_seo_config (
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
-- LOCATION PAGES (ESSENTIAL - NO EQUIVALENT)
-- =============================================

CREATE TABLE location_pages (
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
-- SERVICE + LOCATION COMBINATIONS (ESSENTIAL)
-- =============================================

CREATE TABLE service_location_pages (
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
-- GENERATED SEO PAGES (ESSENTIAL - NO EQUIVALENT)
-- =============================================

CREATE TABLE generated_seo_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    website_config_id UUID REFERENCES website_configurations(id), -- Link to website builder
    page_url VARCHAR(500) NOT NULL,
    page_type VARCHAR(50) NOT NULL, -- 'service_location', 'service', 'location', etc.
    
    -- SEO Content
    title VARCHAR(200) NOT NULL,
    meta_description VARCHAR(300),
    h1_heading VARCHAR(200),
    content TEXT,
    schema_markup JSONB,
    
    -- Generation Info
    generation_method VARCHAR(20) NOT NULL, -- 'template', 'llm_enhanced', 'fallback'
    template_used VARCHAR(100),
    target_keywords TEXT[],
    
    -- Performance Tracking (will be supplemented by website_analytics)
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
-- SEO INDEXES FOR PERFORMANCE
-- =============================================

CREATE INDEX idx_seo_templates_type ON seo_templates(page_type);
CREATE INDEX idx_seo_templates_active ON seo_templates(is_active);

CREATE INDEX idx_service_seo_config_slug ON service_seo_config(service_slug);
CREATE INDEX idx_service_seo_config_priority ON service_seo_config(priority_score);

CREATE INDEX idx_location_pages_slug ON location_pages(slug);
CREATE INDEX idx_location_pages_city_state ON location_pages(city, state);
CREATE INDEX idx_location_pages_competition ON location_pages(competition_level);

CREATE INDEX idx_service_location_url ON service_location_pages(page_url);
CREATE INDEX idx_service_location_service ON service_location_pages(service_slug);
CREATE INDEX idx_service_location_location ON service_location_pages(location_slug);

CREATE INDEX idx_generated_pages_business_url ON generated_seo_pages(business_id, page_url);
CREATE INDEX idx_generated_pages_website ON generated_seo_pages(website_config_id);
CREATE INDEX idx_generated_pages_type ON generated_seo_pages(page_type);
CREATE INDEX idx_generated_pages_method ON generated_seo_pages(generation_method);

COMMIT;
