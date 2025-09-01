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
-- ULTRA-LEAN WEBSITE CONFIGURATION (10X APPROACH)
-- =============================================

CREATE TABLE website_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Deployment Configuration
    domain VARCHAR(255) UNIQUE,
    subdomain VARCHAR(100) UNIQUE, -- hero365.app/subdomain
    deployment_status VARCHAR(50) DEFAULT 'pending' CHECK (deployment_status IN (
        'pending', 'building', 'deployed', 'error'
    )),
    
    -- Smart Page Selection (auto-detected based on business data)
    enabled_pages JSONB NOT NULL DEFAULT '{}',
    /* Example:
    {
        "home": true,
        "services": true,
        "products": false,  // No products in inventory
        "projects": true,   // Has featured projects
        "booking": true,    // Has bookable services
        "pricing": false,   // Doesn't want public pricing
        "about": true,
        "contact": true,
        "locations": ["austin", "round-rock"]  // Service areas
    }
    */
    
    -- SEO Configuration (auto-generated)
    seo_config JSONB DEFAULT '{}',
    /* Example:
    {
        "title_template": "{service} in {city} | {business_name}",
        "meta_description": "Professional {service} services in {city}. Licensed, insured, available 24/7.",
        "keywords": ["hvac", "austin", "emergency", "repair"],
        "google_site_verification": "abc123...",
        "google_analytics_id": "G-XXXXXXXXXX"
    }
    */
    
    -- Content Overrides (simple text replacements)
    content_overrides JSONB DEFAULT '{}',
    /* Example:
    {
        "hero_title": "Austin's #1 HVAC Service",
        "hero_subtitle": "24/7 Emergency Service • Same Day Repairs",
        "cta_text": "Get Free Estimate",
        "phone_display": "(512) 555-HVAC"
    }
    */
    
    -- Performance & Revenue Metrics
    lighthouse_score INTEGER CHECK (lighthouse_score >= 0 AND lighthouse_score <= 100),
    core_web_vitals JSONB DEFAULT '{}',
    monthly_conversions INTEGER DEFAULT 0,
    estimated_monthly_revenue DECIMAL(10,2) DEFAULT 0,
    
    -- Build Information
    build_version INTEGER DEFAULT 1,
    last_build_duration_seconds INTEGER,
    last_deployed_at TIMESTAMPTZ,
    
    -- Future Component System (ready but not blocking)
    component_config JSONB DEFAULT '{}',
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id)
);

-- =============================================
-- REVENUE TRACKING (THE MONEY MAKER)
-- =============================================

CREATE TABLE website_conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Conversion Details
    conversion_type VARCHAR(50) NOT NULL, -- 'phone_call', 'form_submit', 'booking', 'chat', 'email'
    conversion_value DECIMAL(10,2) DEFAULT 0,
    source_page VARCHAR(500),
    
    -- Visitor Data
    visitor_data JSONB DEFAULT '{}',
    /* Example:
    {
        "userAgent": "Mozilla/5.0...",
        "referrer": "https://google.com",
        "trafficSource": "organic"
    }
    */
    
    -- Conversion Data
    conversion_data JSONB DEFAULT '{}',
    /* Example:
    {
        "contact_info": {
            "name": "John Smith",
            "phone": "(512) 555-1234",
            "email": "john@example.com",
            "service_needed": "AC Repair"
        }
    }
    */
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
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
-- NOTE: Legacy analytics tables removed
-- =============================================
-- Analytics are now handled by website_conversions table
-- This provides simpler, revenue-focused tracking

-- =============================================
-- INDEXES
-- =============================================

CREATE INDEX idx_business_branding_business ON business_branding(business_id);

CREATE INDEX idx_website_configs_business ON website_configurations(business_id);
CREATE INDEX idx_website_configs_subdomain ON website_configurations(subdomain);
CREATE INDEX idx_website_configs_status ON website_configurations(deployment_status);
CREATE INDEX idx_website_configs_deployed ON website_configurations(last_deployed_at);

CREATE INDEX idx_website_conversions_business ON website_conversions(business_id);
CREATE INDEX idx_website_conversions_type ON website_conversions(conversion_type);
CREATE INDEX idx_website_conversions_date ON website_conversions(created_at);
CREATE INDEX idx_website_conversions_value ON website_conversions(conversion_value);

CREATE INDEX idx_domain_registrations_business ON domain_registrations(business_id);
CREATE INDEX idx_domain_registrations_domain ON domain_registrations(full_domain);
CREATE INDEX idx_domain_registrations_status ON domain_registrations(status);
CREATE INDEX idx_domain_registrations_expiration ON domain_registrations(expiration_date);

COMMIT;
