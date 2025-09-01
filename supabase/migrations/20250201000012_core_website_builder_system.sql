-- =============================================
-- CORE WEBSITE BUILDER SYSTEM
-- =============================================
-- Essential website builder and domain management
-- Required for SEO Revenue Engine functionality
-- Depends on: businesses tables

-- =============================================
-- BUSINESS BRANDING
-- =============================================

CREATE TABLE business_branding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Branding Details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Visual Identity
    color_scheme JSONB DEFAULT '{}',
    typography JSONB DEFAULT '{}',
    assets JSONB DEFAULT '{}', -- logo_url, favicon_url, watermark_url
    
    -- Customizations
    trade_customizations JSONB DEFAULT '[]', -- Trade-specific overrides
    website_settings JSONB DEFAULT '{}',
    document_settings JSONB DEFAULT '{}',
    email_settings JSONB DEFAULT '{}',
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE (business_id) -- Each business has one branding configuration
);

-- =============================================
-- WEBSITE TEMPLATES
-- =============================================

CREATE TABLE website_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Trade Classification
    trade_type VARCHAR(50) NOT NULL,
    trade_category VARCHAR(20) NOT NULL CHECK (trade_category IN ('COMMERCIAL', 'RESIDENTIAL', 'BOTH')),
    
    -- Template Metadata
    name VARCHAR(100) NOT NULL,
    description TEXT,
    preview_url VARCHAR(500),
    
    -- Template Structure
    structure JSONB NOT NULL DEFAULT '{}', -- Page hierarchy and components
    default_content JSONB DEFAULT '{}', -- AI prompts and seed content
    seo_config JSONB DEFAULT '{}', -- Meta tags, schema templates
    
    -- Multi-trade Support
    is_multi_trade BOOLEAN DEFAULT FALSE,
    supported_trades TEXT[], -- Array of supported trade combinations
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_system_template BOOLEAN DEFAULT FALSE,
    
    -- Usage Tracking
    usage_count INTEGER DEFAULT 0 CHECK (usage_count >= 0),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- BUSINESS WEBSITES
-- =============================================

CREATE TABLE business_websites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    branding_id UUID REFERENCES business_branding(id) ON DELETE SET NULL,
    template_id UUID REFERENCES website_templates(id) ON DELETE SET NULL,
    
    -- Domain Configuration
    domain VARCHAR(255) UNIQUE,
    subdomain VARCHAR(100), -- For hero365.ai subdomains
    
    -- Website Status
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN (
        'draft', 'building', 'built', 'deploying', 'deployed', 'error'
    )),
    
    -- Trade-specific Content
    primary_trade VARCHAR(50),
    secondary_trades TEXT[],
    service_areas TEXT[],
    
    -- Customization
    theme_overrides JSONB DEFAULT '{}',
    content_overrides JSONB DEFAULT '{}',
    pages JSONB DEFAULT '{}',
    
    -- Deployment Configuration
    deployment_config JSONB DEFAULT '{}',
    build_config JSONB DEFAULT '{}',
    
    -- Build Tracking
    build_path VARCHAR(500),
    last_build_at TIMESTAMPTZ,
    last_deploy_at TIMESTAMPTZ,
    build_duration_seconds INTEGER,
    
    -- SEO Settings
    seo_keywords JSONB DEFAULT '[]',
    target_locations JSONB DEFAULT '[]',
    google_site_verification VARCHAR(255),
    
    -- Performance Metrics
    lighthouse_score INTEGER CHECK (lighthouse_score >= 0 AND lighthouse_score <= 100),
    core_web_vitals JSONB DEFAULT '{}',
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- DOMAIN REGISTRATIONS
-- =============================================

CREATE TABLE domain_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Domain Details
    domain_name VARCHAR(255) NOT NULL,
    tld VARCHAR(10) NOT NULL, -- .com, .net, .org, etc.
    full_domain VARCHAR(255) GENERATED ALWAYS AS (domain_name || '.' || tld) STORED,
    
    -- Registration Status
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN (
        'available', 'registered', 'pending', 'expired', 'unavailable'
    )),
    
    -- Registration Details
    registrar VARCHAR(100),
    registration_date DATE,
    expiration_date DATE,
    auto_renew BOOLEAN DEFAULT TRUE,
    
    -- Pricing
    registration_cost DECIMAL(8,2),
    renewal_cost DECIMAL(8,2),
    
    -- DNS Configuration
    nameservers TEXT[],
    dns_records JSONB DEFAULT '{}',
    
    -- SEO Analysis
    seo_score INTEGER CHECK (seo_score >= 0 AND seo_score <= 100),
    seo_factors JSONB DEFAULT '{}',
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(domain_name, tld)
);

-- =============================================
-- WEBSITE ANALYTICS (ENHANCED FOR SEO)
-- =============================================

CREATE TABLE website_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES business_websites(id) ON DELETE CASCADE,
    page_url VARCHAR(500), -- Specific page URL (optional, for page-level analytics)
    
    -- Analytics Period
    date DATE NOT NULL,
    period_type VARCHAR(20) DEFAULT 'daily', -- 'daily', 'weekly', 'monthly'
    
    -- Traffic Metrics
    page_views INTEGER DEFAULT 0,
    unique_visitors INTEGER DEFAULT 0,
    sessions INTEGER DEFAULT 0,
    bounce_rate DECIMAL(5,2) DEFAULT 0,
    avg_session_duration INTEGER DEFAULT 0, -- seconds
    
    -- Source Attribution
    organic_traffic INTEGER DEFAULT 0,
    direct_traffic INTEGER DEFAULT 0,
    referral_traffic INTEGER DEFAULT 0,
    social_traffic INTEGER DEFAULT 0,
    
    -- Conversion Metrics
    form_submissions INTEGER DEFAULT 0,
    phone_calls INTEGER DEFAULT 0,
    quote_requests INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0,
    conversions INTEGER DEFAULT 0, -- Total conversions
    revenue DECIMAL(10,2) DEFAULT 0, -- Revenue attributed to this period/page
    
    -- SEO Metrics (consolidated from seo_performance)
    search_impressions INTEGER DEFAULT 0,
    search_clicks INTEGER DEFAULT 0,
    average_position DECIMAL(4,2) DEFAULT 0,
    click_through_rate DECIMAL(5,2) DEFAULT 0,
    
    -- Performance Metrics
    page_load_time INTEGER DEFAULT 0, -- milliseconds
    core_web_vitals_score INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(website_id, date, page_url)
);

-- =============================================
-- SEO KEYWORD TRACKING
-- =============================================

CREATE TABLE seo_keyword_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES business_websites(id) ON DELETE CASCADE,
    
    -- Keyword Details
    keyword VARCHAR(255) NOT NULL,
    keyword_type VARCHAR(50), -- 'primary', 'secondary', 'long_tail'
    search_volume INTEGER DEFAULT 0,
    competition_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high'
    
    -- Ranking Data
    current_position INTEGER,
    previous_position INTEGER,
    best_position INTEGER,
    worst_position INTEGER,
    
    -- Performance Metrics
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    click_through_rate DECIMAL(5,2) DEFAULT 0,
    
    -- Tracking Period
    tracked_since DATE DEFAULT CURRENT_DATE,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    
    -- Target Information
    target_page_url VARCHAR(500),
    target_position INTEGER DEFAULT 1,
    
    -- Metadata
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(website_id, keyword)
);

-- =============================================
-- WEBSITE BUILD JOBS (ENHANCED FOR SEO)
-- =============================================

CREATE TABLE website_build_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES business_websites(id) ON DELETE CASCADE,
    
    -- Job Details
    job_type VARCHAR(50) NOT NULL, -- 'initial_build', 'content_update', 'design_change', 'seo_deployment', 'full_seo'
    status VARCHAR(20) DEFAULT 'queued' CHECK (status IN (
        'queued', 'running', 'completed', 'failed', 'cancelled'
    )),
    
    -- Build Configuration
    build_config JSONB DEFAULT '{}',
    build_output JSONB DEFAULT '{}',
    
    -- SEO-Specific Fields (consolidated from website_deployments)
    deployment_type VARCHAR(20), -- 'full_seo', 'partial_update', 'template_only'
    pages_generated INTEGER DEFAULT 0,
    template_pages INTEGER DEFAULT 0,
    enhanced_pages INTEGER DEFAULT 0,
    cloudflare_deployment_id TEXT,
    
    -- Timing
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    estimated_completion TIMESTAMPTZ,
    duration_seconds INTEGER,
    generation_time_seconds INTEGER, -- SEO-specific timing
    
    -- Results
    success BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    build_log TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Deployment
    deployment_url VARCHAR(500),
    deployment_status VARCHAR(20),
    
    -- Metadata
    triggered_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- INDEXES
-- =============================================

CREATE INDEX idx_business_branding_business ON business_branding(business_id);

CREATE INDEX idx_website_templates_trade ON website_templates(trade_type, trade_category);
CREATE INDEX idx_website_templates_active ON website_templates(is_active);
CREATE INDEX idx_website_templates_system ON website_templates(is_system_template);

CREATE INDEX idx_business_websites_business ON business_websites(business_id);
CREATE INDEX idx_business_websites_domain ON business_websites(domain);
CREATE INDEX idx_business_websites_status ON business_websites(status);
CREATE INDEX idx_business_websites_branding ON business_websites(branding_id);
CREATE INDEX idx_business_websites_template ON business_websites(template_id);

CREATE INDEX idx_domain_registrations_business ON domain_registrations(business_id);
CREATE INDEX idx_domain_registrations_domain ON domain_registrations(full_domain);
CREATE INDEX idx_domain_registrations_status ON domain_registrations(status);
CREATE INDEX idx_domain_registrations_expiration ON domain_registrations(expiration_date);

CREATE INDEX idx_website_analytics_website ON website_analytics(website_id);
CREATE INDEX idx_website_analytics_date ON website_analytics(date);
CREATE INDEX idx_website_analytics_website_date ON website_analytics(website_id, date);

CREATE INDEX idx_seo_keyword_tracking_website ON seo_keyword_tracking(website_id);
CREATE INDEX idx_seo_keyword_tracking_keyword ON seo_keyword_tracking(keyword);
CREATE INDEX idx_seo_keyword_tracking_position ON seo_keyword_tracking(current_position);
CREATE INDEX idx_seo_keyword_tracking_active ON seo_keyword_tracking(is_active);

CREATE INDEX idx_website_build_jobs_website ON website_build_jobs(website_id);
CREATE INDEX idx_website_build_jobs_status ON website_build_jobs(status);
CREATE INDEX idx_website_build_jobs_type ON website_build_jobs(job_type);
CREATE INDEX idx_website_build_jobs_created ON website_build_jobs(created_at);

COMMIT;
