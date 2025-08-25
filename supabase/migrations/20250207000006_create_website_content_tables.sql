-- Website Content Tables for Template-Driven Site Generation
-- Migration: 20250207000006_create_website_content_tables.sql
-- Description: Create content tables needed for professional website templates like Fuse Service
-- Date: 2025-02-07

-- =====================================
-- PROMOTIONAL OFFERS TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.promos_offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    
    -- Offer details
    title VARCHAR(200) NOT NULL,
    subtitle VARCHAR(300),
    description TEXT,
    offer_type VARCHAR(50) NOT NULL CHECK (offer_type IN (
        'percentage_discount', 'fixed_amount', 'buy_one_get_one', 
        'free_service', 'seasonal_special', 'new_customer', 'referral'
    )),
    
    -- Display settings
    price_label VARCHAR(100), -- e.g., "Starting at $99", "Save $200"
    badge_text VARCHAR(50), -- e.g., "Limited Time", "New Customer Special"
    cta_text VARCHAR(100) DEFAULT 'Learn More',
    cta_link VARCHAR(500),
    
    -- Placement and priority
    placement VARCHAR(50) NOT NULL CHECK (placement IN (
        'hero_banner', 'promo_carousel', 'sidebar', 'footer', 'popup', 'inline'
    )),
    priority INTEGER DEFAULT 0, -- Higher numbers = higher priority
    
    -- Targeting and validity
    target_services TEXT[], -- Specific services this promo applies to
    target_trades TEXT[], -- Specific trades this promo applies to
    service_areas TEXT[], -- Geographic areas where offer is valid
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    
    -- Status and tracking
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    conversion_count INTEGER DEFAULT 0,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- RATINGS SNAPSHOT TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.ratings_snapshot (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    
    -- Rating platform
    platform VARCHAR(50) NOT NULL CHECK (platform IN (
        'google', 'yelp', 'bbb', 'angie', 'facebook', 'trustpilot', 'homeadvisor', 'thumbtack'
    )),
    
    -- Rating data
    rating NUMERIC(3,2) NOT NULL CHECK (rating >= 0 AND rating <= 5),
    review_count INTEGER NOT NULL CHECK (review_count >= 0),
    total_reviews INTEGER, -- Total reviews ever (if different from current count)
    
    -- Display settings
    display_name VARCHAR(100), -- Custom display name for the platform
    logo_url VARCHAR(500), -- Platform logo URL
    profile_url VARCHAR(500), -- Link to business profile on platform
    is_featured BOOLEAN DEFAULT FALSE, -- Show prominently on website
    sort_order INTEGER DEFAULT 0,
    
    -- Data freshness
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sync_frequency_hours INTEGER DEFAULT 24,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint per business per platform
    UNIQUE(business_id, platform)
);

-- =====================================
-- AWARDS AND CERTIFICATIONS TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.awards_certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    
    -- Award/Certification details
    name VARCHAR(200) NOT NULL,
    issuing_organization VARCHAR(200),
    description TEXT,
    certificate_type VARCHAR(50) CHECK (certificate_type IN (
        'industry_award', 'certification', 'license', 'accreditation', 
        'safety_certification', 'training_completion', 'quality_assurance'
    )),
    
    -- Display assets
    logo_url VARCHAR(500),
    certificate_url VARCHAR(500), -- Link to certificate document
    verification_url VARCHAR(500), -- Link to verify certification
    
    -- Validity
    issued_date DATE,
    expiry_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    
    -- Display settings
    is_featured BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    display_on_website BOOLEAN DEFAULT TRUE,
    
    -- Categories for filtering
    trade_relevance TEXT[], -- Which trades this applies to
    service_categories TEXT[], -- Which service categories this applies to
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- OEM PARTNERSHIPS TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.oem_partnerships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    
    -- Partner details
    partner_name VARCHAR(200) NOT NULL, -- e.g., "Carrier", "Trane", "Lennox"
    partner_type VARCHAR(50) NOT NULL CHECK (partner_type IN (
        'manufacturer', 'distributor', 'supplier', 'technology_partner', 
        'certification_body', 'trade_association', 'dealer_network'
    )),
    
    -- Partnership details
    partnership_level VARCHAR(50), -- e.g., "Authorized Dealer", "Premier Partner", "Gold Certified"
    description TEXT,
    partnership_benefits TEXT[], -- Array of benefits like "Warranty Extension", "Priority Support"
    
    -- Display assets
    logo_url VARCHAR(500) NOT NULL,
    partner_url VARCHAR(500), -- Link to partner's website
    verification_url VARCHAR(500), -- Link to verify partnership
    
    -- Relevance and targeting
    trade_relevance TEXT[] NOT NULL, -- Which trades this partnership applies to
    service_categories TEXT[], -- Which service categories benefit
    product_lines TEXT[], -- Specific product lines covered
    
    -- Display settings
    is_featured BOOLEAN DEFAULT FALSE, -- Show in prominent partner section
    sort_order INTEGER DEFAULT 0,
    display_on_website BOOLEAN DEFAULT TRUE,
    
    -- Partnership status
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    is_current BOOLEAN DEFAULT TRUE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- TESTIMONIALS TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.testimonials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    
    -- Source and attribution
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN (
        'google_review', 'yelp_review', 'facebook_review', 'direct_feedback',
        'survey_response', 'case_study', 'referral_feedback', 'manual_entry'
    )),
    source_id VARCHAR(200), -- External ID from review platform
    source_url VARCHAR(500), -- Link to original review
    
    -- Testimonial content
    quote TEXT NOT NULL,
    full_review TEXT, -- Full review text if quote is excerpt
    rating NUMERIC(3,2) CHECK (rating >= 0 AND rating <= 5),
    
    -- Customer information
    customer_name VARCHAR(200),
    customer_initial VARCHAR(10), -- e.g., "J.S." for privacy
    customer_location VARCHAR(100), -- City or area
    customer_avatar_url VARCHAR(500),
    
    -- Service context
    service_performed VARCHAR(200), -- What service was provided
    service_date DATE,
    project_value NUMERIC(10,2), -- Project cost range for credibility
    trade_category VARCHAR(50), -- Which trade this testimonial relates to
    
    -- Display settings
    is_featured BOOLEAN DEFAULT FALSE, -- Show in hero/prominent sections
    is_verified BOOLEAN DEFAULT FALSE, -- Verified customer
    display_on_website BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    
    -- Content moderation
    moderation_status VARCHAR(50) DEFAULT 'pending' CHECK (moderation_status IN (
        'pending', 'approved', 'rejected', 'needs_review'
    )),
    moderated_by VARCHAR(255),
    moderated_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- WEBSITE DEPLOYMENTS TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.website_deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    
    -- Template and deployment details
    template_name VARCHAR(100) NOT NULL, -- e.g., "professional", "fuse-inspired"
    template_version VARCHAR(50), -- Template version used
    deployment_type VARCHAR(50) NOT NULL CHECK (deployment_type IN (
        'production', 'staging', 'preview', 'development'
    )),
    
    -- Cloudflare project details
    project_name VARCHAR(200) NOT NULL, -- Cloudflare Pages project name
    deploy_url VARCHAR(500) NOT NULL, -- Full URL to deployed site
    custom_domain VARCHAR(200), -- Custom domain if configured
    
    -- Build information
    build_id VARCHAR(200), -- Cloudflare deployment ID
    build_status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (build_status IN (
        'pending', 'building', 'success', 'failed', 'cancelled'
    )),
    build_log TEXT, -- Build logs for debugging
    build_duration_seconds INTEGER,
    
    -- Performance metrics
    lighthouse_json JSONB, -- Full Lighthouse report
    performance_score INTEGER CHECK (performance_score >= 0 AND performance_score <= 100),
    accessibility_score INTEGER CHECK (accessibility_score >= 0 AND accessibility_score <= 100),
    seo_score INTEGER CHECK (seo_score >= 0 AND seo_score <= 100),
    best_practices_score INTEGER CHECK (best_practices_score >= 0 AND best_practices_score <= 100),
    
    -- Content generation details
    content_generated_at TIMESTAMP WITH TIME ZONE,
    content_generation_model VARCHAR(100), -- AI model used for content
    content_generation_tokens_used INTEGER,
    
    -- Status and metadata
    is_current BOOLEAN DEFAULT FALSE, -- Current live deployment
    error_message TEXT, -- Error details if build failed
    metadata JSONB DEFAULT '{}', -- Additional deployment metadata
    
    -- Audit fields
    deployed_by VARCHAR(255), -- User who triggered deployment
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- LOCATIONS TABLE (Enhanced service areas)
-- =====================================
CREATE TABLE IF NOT EXISTS public.business_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    
    -- Location details
    name VARCHAR(200), -- Location name or identifier
    address TEXT,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(20),
    county VARCHAR(100),
    
    -- Geographic data
    latitude NUMERIC(10,8),
    longitude NUMERIC(11,8),
    service_radius_miles INTEGER, -- Service radius from this location
    
    -- Location type and status
    location_type VARCHAR(50) NOT NULL CHECK (location_type IN (
        'headquarters', 'branch_office', 'service_area', 'coverage_zone', 'warehouse'
    )),
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Service details
    services_offered TEXT[], -- Services available from this location
    trades_covered TEXT[], -- Trades covered from this location
    operating_hours JSONB, -- Location-specific hours
    
    -- SEO and website display
    display_on_website BOOLEAN DEFAULT TRUE,
    seo_description TEXT, -- Location-specific SEO description
    page_slug VARCHAR(100), -- URL slug for location page
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint on primary location per business
    CONSTRAINT business_locations_one_primary UNIQUE (business_id, is_primary) DEFERRABLE INITIALLY DEFERRED
);

-- =====================================
-- INDEXES FOR PERFORMANCE
-- =====================================

-- Promos and offers
CREATE INDEX idx_promos_offers_business_id ON public.promos_offers(business_id);
CREATE INDEX idx_promos_offers_active ON public.promos_offers(is_active, start_date, end_date) WHERE is_active = TRUE;
CREATE INDEX idx_promos_offers_placement ON public.promos_offers(placement, priority DESC) WHERE is_active = TRUE;
CREATE INDEX idx_promos_offers_featured ON public.promos_offers(is_featured) WHERE is_featured = TRUE;

-- Ratings snapshot
CREATE INDEX idx_ratings_snapshot_business_id ON public.ratings_snapshot(business_id);
CREATE INDEX idx_ratings_snapshot_featured ON public.ratings_snapshot(is_featured, rating DESC) WHERE is_featured = TRUE;
CREATE INDEX idx_ratings_snapshot_platform ON public.ratings_snapshot(platform);
CREATE INDEX idx_ratings_snapshot_sync ON public.ratings_snapshot(last_synced_at, sync_frequency_hours) WHERE is_active = TRUE;

-- Awards and certifications
CREATE INDEX idx_awards_certifications_business_id ON public.awards_certifications(business_id);
CREATE INDEX idx_awards_certifications_featured ON public.awards_certifications(is_featured, sort_order) WHERE is_featured = TRUE;
CREATE INDEX idx_awards_certifications_current ON public.awards_certifications(is_current, expiry_date) WHERE is_current = TRUE;
CREATE INDEX idx_awards_certifications_trades ON public.awards_certifications USING gin(trade_relevance);

-- OEM partnerships
CREATE INDEX idx_oem_partnerships_business_id ON public.oem_partnerships(business_id);
CREATE INDEX idx_oem_partnerships_featured ON public.oem_partnerships(is_featured, sort_order) WHERE is_featured = TRUE;
CREATE INDEX idx_oem_partnerships_active ON public.oem_partnerships(is_active, is_current) WHERE is_active = TRUE;
CREATE INDEX idx_oem_partnerships_trades ON public.oem_partnerships USING gin(trade_relevance);

-- Testimonials
CREATE INDEX idx_testimonials_business_id ON public.testimonials(business_id);
CREATE INDEX idx_testimonials_featured ON public.testimonials(is_featured, rating DESC) WHERE is_featured = TRUE;
CREATE INDEX idx_testimonials_approved ON public.testimonials(moderation_status, created_at DESC) WHERE moderation_status = 'approved';
CREATE INDEX idx_testimonials_source ON public.testimonials(source_type, source_id);

-- Website deployments
CREATE INDEX idx_website_deployments_business_id ON public.website_deployments(business_id);
CREATE INDEX idx_website_deployments_current ON public.website_deployments(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_website_deployments_status ON public.website_deployments(build_status, created_at DESC);
CREATE INDEX idx_website_deployments_template ON public.website_deployments(template_name, template_version);

-- Business locations
CREATE INDEX idx_business_locations_business_id ON public.business_locations(business_id);
CREATE INDEX idx_business_locations_primary ON public.business_locations(is_primary) WHERE is_primary = TRUE;
CREATE INDEX idx_business_locations_active ON public.business_locations(is_active, location_type) WHERE is_active = TRUE;
CREATE INDEX idx_business_locations_geo ON public.business_locations(latitude, longitude) WHERE latitude IS NOT NULL AND longitude IS NOT NULL;
CREATE INDEX idx_business_locations_slug ON public.business_locations(page_slug) WHERE page_slug IS NOT NULL;

-- =====================================
-- UPDATE TRIGGERS
-- =====================================

-- Create update trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to all tables
CREATE TRIGGER update_promos_offers_updated_at BEFORE UPDATE ON public.promos_offers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ratings_snapshot_updated_at BEFORE UPDATE ON public.ratings_snapshot FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_awards_certifications_updated_at BEFORE UPDATE ON public.awards_certifications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_oem_partnerships_updated_at BEFORE UPDATE ON public.oem_partnerships FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_testimonials_updated_at BEFORE UPDATE ON public.testimonials FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_website_deployments_updated_at BEFORE UPDATE ON public.website_deployments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_business_locations_updated_at BEFORE UPDATE ON public.business_locations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================
-- HELPER FUNCTIONS
-- =====================================

-- Function to get active promos for a business
CREATE OR REPLACE FUNCTION get_active_promos(p_business_id UUID, p_placement VARCHAR DEFAULT NULL)
RETURNS TABLE (
    id UUID,
    title VARCHAR,
    subtitle VARCHAR,
    price_label VARCHAR,
    badge_text VARCHAR,
    cta_text VARCHAR,
    cta_link VARCHAR,
    priority INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        po.id,
        po.title,
        po.subtitle,
        po.price_label,
        po.badge_text,
        po.cta_text,
        po.cta_link,
        po.priority
    FROM public.promos_offers po
    WHERE po.business_id = p_business_id
    AND po.is_active = TRUE
    AND (po.start_date IS NULL OR po.start_date <= NOW())
    AND (po.end_date IS NULL OR po.end_date >= NOW())
    AND (p_placement IS NULL OR po.placement = p_placement)
    ORDER BY po.priority DESC, po.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get featured ratings for display
CREATE OR REPLACE FUNCTION get_featured_ratings(p_business_id UUID)
RETURNS TABLE (
    platform VARCHAR,
    rating NUMERIC,
    review_count INTEGER,
    display_name VARCHAR,
    logo_url VARCHAR,
    profile_url VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rs.platform,
        rs.rating,
        rs.review_count,
        rs.display_name,
        rs.logo_url,
        rs.profile_url
    FROM public.ratings_snapshot rs
    WHERE rs.business_id = p_business_id
    AND rs.is_active = TRUE
    AND rs.is_featured = TRUE
    ORDER BY rs.sort_order, rs.rating DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to mark a deployment as current (unsets others)
CREATE OR REPLACE FUNCTION set_current_deployment(p_deployment_id UUID, p_business_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    -- Unset current deployment
    UPDATE public.website_deployments
    SET is_current = FALSE
    WHERE business_id = p_business_id
    AND is_current = TRUE
    AND id != p_deployment_id;
    
    -- Set new current deployment
    UPDATE public.website_deployments
    SET is_current = TRUE
    WHERE id = p_deployment_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================

COMMENT ON TABLE public.promos_offers IS 'Promotional offers and banners for website display with targeting and scheduling';
COMMENT ON TABLE public.ratings_snapshot IS 'Cached ratings from review platforms for website trust indicators';
COMMENT ON TABLE public.awards_certifications IS 'Business awards, certifications, and professional credentials for credibility';
COMMENT ON TABLE public.oem_partnerships IS 'Manufacturer and partner relationships for authority and trust';
COMMENT ON TABLE public.testimonials IS 'Customer testimonials and reviews for social proof';
COMMENT ON TABLE public.website_deployments IS 'Website deployment tracking with performance metrics and build information';
COMMENT ON TABLE public.business_locations IS 'Business locations and service areas for local SEO and geographic targeting';

COMMENT ON FUNCTION get_active_promos IS 'Returns active promotional offers for a business, optionally filtered by placement';
COMMENT ON FUNCTION get_featured_ratings IS 'Returns featured ratings for website display';
COMMENT ON FUNCTION set_current_deployment IS 'Sets a deployment as current and unsets others for the same business';
