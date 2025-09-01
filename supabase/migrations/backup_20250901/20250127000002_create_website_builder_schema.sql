-- SEO Website Builder Schema
-- Comprehensive database schema for AI-powered website generation and SEO optimization
-- Date: 2025-01-27
-- Version: Website Builder Feature Implementation

-- =====================================
-- WEBSITE TEMPLATES TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.website_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Trade classification (matches Business entity)
    trade_type VARCHAR(50) NOT NULL, -- Specific trade from CommercialTrade or ResidentialTrade enums
    trade_category VARCHAR(20) NOT NULL CHECK (trade_category IN ('COMMERCIAL', 'RESIDENTIAL', 'BOTH')),
    
    -- Template metadata
    name VARCHAR(100) NOT NULL,
    description TEXT,
    preview_url VARCHAR(500),
    
    -- Template structure and configuration
    structure JSONB NOT NULL DEFAULT '{}'::JSONB, -- Page hierarchy and components
    default_content JSONB DEFAULT '{}'::JSONB, -- AI prompts and seed content
    seo_config JSONB DEFAULT '{}'::JSONB, -- Meta tags, schema templates
    
    -- Multi-trade support
    is_multi_trade BOOLEAN DEFAULT FALSE, -- Support for multi-trade businesses
    supported_trades TEXT[], -- Array of supported trade combinations
    
    -- Template status
    is_active BOOLEAN DEFAULT TRUE,
    is_system_template BOOLEAN DEFAULT FALSE,
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0 CHECK (usage_count >= 0),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT website_templates_valid_trade_category CHECK (
        trade_category IN ('COMMERCIAL', 'RESIDENTIAL', 'BOTH')
    )
);

-- Add missing column for system templates
ALTER TABLE public.website_templates ADD COLUMN IF NOT EXISTS is_system_template BOOLEAN DEFAULT FALSE;

-- Add missing columns for domain registrations
ALTER TABLE public.domain_registrations ADD COLUMN IF NOT EXISTS seo_score INTEGER CHECK (seo_score >= 0 AND seo_score <= 100);
ALTER TABLE public.domain_registrations ADD COLUMN IF NOT EXISTS seo_factors JSONB DEFAULT '{}'::JSONB;

-- =====================================
-- BUSINESS WEBSITES TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.business_websites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    branding_id UUID REFERENCES public.business_branding(id) ON DELETE SET NULL, -- Link to centralized branding
    template_id UUID REFERENCES public.website_templates(id) ON DELETE SET NULL,
    
    -- Domain configuration
    domain VARCHAR(255) UNIQUE,
    subdomain VARCHAR(100), -- for hero365.ai subdomains
    
    -- Website status
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN (
        'draft', 'building', 'built', 'deploying', 'deployed', 'error'
    )),
    
    -- Trade-specific content configuration
    primary_trade VARCHAR(50), -- Primary trade for SEO focus
    secondary_trades TEXT[], -- Additional trades to mention
    service_areas TEXT[], -- Geographic service areas
    
    -- Customization (overrides from central branding if needed)
    theme_overrides JSONB DEFAULT '{}'::JSONB, -- Component-specific overrides
    content_overrides JSONB DEFAULT '{}'::JSONB, -- User edits to AI content
    pages JSONB DEFAULT '{}'::JSONB, -- Generated page structure
    
    -- Deployment configuration
    deployment_config JSONB DEFAULT '{}'::JSONB, -- S3, CloudFront, etc.
    build_config JSONB DEFAULT '{}'::JSONB, -- Build-time configuration
    
    -- Build and deployment tracking
    build_path VARCHAR(500), -- Local build output path
    last_build_at TIMESTAMP WITH TIME ZONE,
    last_deploy_at TIMESTAMP WITH TIME ZONE,
    build_duration_seconds INTEGER, -- Performance tracking
    
    -- SEO Settings
    seo_keywords JSONB DEFAULT '[]'::JSONB, -- Target keywords array
    target_locations JSONB DEFAULT '[]'::JSONB, -- Target geographic locations
    google_site_verification VARCHAR(255),
    
    -- Performance metrics
    lighthouse_score INTEGER CHECK (lighthouse_score >= 0 AND lighthouse_score <= 100),
    core_web_vitals JSONB DEFAULT '{}'::JSONB, -- LCP, FID, CLS scores
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT business_websites_unique_business UNIQUE (business_id), -- One website per business
    CONSTRAINT business_websites_domain_or_subdomain CHECK (
        domain IS NOT NULL OR subdomain IS NOT NULL
    )
);

-- =====================================
-- DOMAIN REGISTRATIONS TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.domain_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    website_id UUID REFERENCES public.business_websites(id) ON DELETE SET NULL,
    
    -- Domain details
    domain VARCHAR(255) NOT NULL UNIQUE,
    provider VARCHAR(50) NOT NULL DEFAULT 'cloudflare',
    
    -- Registration status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN (
        'pending', 'active', 'expired', 'transferred', 'cancelled', 'failed'
    )),
    
    -- Registration details
    registered_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    auto_renew BOOLEAN DEFAULT TRUE,
    privacy_protection BOOLEAN DEFAULT TRUE,
    
    -- Provider details
    provider_order_id VARCHAR(255),
    nameservers JSONB DEFAULT '[]'::JSONB,
    dns_configured BOOLEAN DEFAULT FALSE,
    
    -- Pricing information
    purchase_price DECIMAL(10,2),
    renewal_price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- SEO scoring (calculated at registration time)
    seo_score INTEGER CHECK (seo_score >= 0 AND seo_score <= 100),
    seo_factors JSONB DEFAULT '{}'::JSONB, -- Detailed scoring breakdown
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- WEBSITE ANALYTICS TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.website_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES public.business_websites(id) ON DELETE CASCADE,
    
    -- Time dimension
    date DATE NOT NULL,
    hour INTEGER CHECK (hour >= 0 AND hour <= 23), -- For hourly granularity
    
    -- Traffic metrics
    page_views INTEGER DEFAULT 0,
    unique_visitors INTEGER DEFAULT 0,
    sessions INTEGER DEFAULT 0,
    avg_session_duration INTEGER DEFAULT 0, -- seconds
    bounce_rate DECIMAL(5,2) DEFAULT 0.0,
    
    -- Performance metrics
    core_web_vitals JSONB DEFAULT '{}'::JSONB, -- LCP, FID, CLS scores
    lighthouse_score INTEGER CHECK (lighthouse_score >= 0 AND lighthouse_score <= 100),
    
    -- SEO metrics
    search_impressions INTEGER DEFAULT 0,
    search_clicks INTEGER DEFAULT 0,
    avg_search_position DECIMAL(5,2),
    
    -- Conversion metrics
    contact_form_submissions INTEGER DEFAULT 0,
    phone_clicks INTEGER DEFAULT 0,
    email_clicks INTEGER DEFAULT 0,
    
    -- Geographic data
    top_countries JSONB DEFAULT '[]'::JSONB,
    top_cities JSONB DEFAULT '[]'::JSONB,
    
    -- Device breakdown
    desktop_percentage DECIMAL(5,2) DEFAULT 0.0,
    mobile_percentage DECIMAL(5,2) DEFAULT 0.0,
    tablet_percentage DECIMAL(5,2) DEFAULT 0.0,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(website_id, date, hour) -- Prevent duplicate entries
);

-- =====================================
-- SEO KEYWORD TRACKING TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.seo_keyword_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES public.business_websites(id) ON DELETE CASCADE,
    
    -- Keyword details
    keyword VARCHAR(255) NOT NULL,
    search_volume INTEGER DEFAULT 0,
    competition_level VARCHAR(20) DEFAULT 'unknown' CHECK (competition_level IN (
        'low', 'medium', 'high', 'unknown'
    )),
    
    -- Current ranking
    current_rank INTEGER,
    previous_rank INTEGER,
    best_rank INTEGER,
    worst_rank INTEGER,
    
    -- Geographic targeting
    target_location VARCHAR(255), -- City, state, or country
    location_coordinates POINT, -- For precise geo-targeting
    
    -- Tracking metadata
    first_tracked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    check_frequency_hours INTEGER DEFAULT 24, -- How often to check
    
    -- Trade relevance
    trade_relevance_score INTEGER CHECK (trade_relevance_score >= 0 AND trade_relevance_score <= 100),
    is_primary_keyword BOOLEAN DEFAULT FALSE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(website_id, keyword, target_location) -- Prevent duplicate tracking
);

-- =====================================
-- WEBSITE INTAKE FORMS TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.website_intake_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES public.business_websites(id) ON DELETE CASCADE,
    
    -- Form identification
    form_type VARCHAR(50) NOT NULL CHECK (form_type IN (
        'contact', 'quote', 'booking', 'emergency', 'consultation', 'maintenance'
    )),
    form_name VARCHAR(100) NOT NULL,
    
    -- Form configuration
    fields_config JSONB NOT NULL DEFAULT '[]'::JSONB, -- Form field definitions
    validation_rules JSONB DEFAULT '{}'::JSONB,
    styling_config JSONB DEFAULT '{}'::JSONB,
    
    -- Integration settings
    integration_config JSONB DEFAULT '{}'::JSONB, -- Hero365 API, email, SMS settings
    auto_response_config JSONB DEFAULT '{}'::JSONB, -- Automated responses
    lead_routing_config JSONB DEFAULT '{}'::JSONB, -- How to route different lead types
    
    -- Form status
    is_active BOOLEAN DEFAULT TRUE,
    is_embedded BOOLEAN DEFAULT FALSE, -- Can be embedded on other sites
    
    -- Usage tracking
    submission_count INTEGER DEFAULT 0 CHECK (submission_count >= 0),
    conversion_rate DECIMAL(5,2) DEFAULT 0.0,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- WEBSITE FORM SUBMISSIONS TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.website_form_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES public.business_websites(id) ON DELETE CASCADE,
    form_id UUID NOT NULL REFERENCES public.website_intake_forms(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    
    -- Submission data
    form_data JSONB NOT NULL DEFAULT '{}'::JSONB, -- All form field values
    visitor_info JSONB DEFAULT '{}'::JSONB, -- IP, user agent, referrer, etc.
    
    -- Lead classification
    lead_type VARCHAR(50) NOT NULL CHECK (lead_type IN (
        'quote_request', 'service_booking', 'emergency', 'consultation', 
        'maintenance', 'general_inquiry', 'callback_request'
    )),
    priority_level VARCHAR(20) DEFAULT 'medium' CHECK (priority_level IN (
        'low', 'medium', 'high', 'emergency'
    )),
    
    -- Contact information (extracted from form_data for easy querying)
    contact_name VARCHAR(255),
    contact_email VARCHAR(320),
    contact_phone VARCHAR(20),
    service_address TEXT,
    
    -- Processing status
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN (
        'new', 'contacted', 'qualified', 'converted', 'closed', 'spam'
    )),
    
    -- Integration results
    contact_created_id UUID, -- Reference to created contact
    estimate_created_id UUID, -- Reference to created estimate
    job_created_id UUID, -- Reference to created job/booking
    
    -- Response tracking
    auto_response_sent BOOLEAN DEFAULT FALSE,
    follow_up_scheduled BOOLEAN DEFAULT FALSE,
    first_response_at TIMESTAMP WITH TIME ZONE,
    
    -- Conversion tracking
    converted_at TIMESTAMP WITH TIME ZONE,
    conversion_value DECIMAL(10,2), -- Estimated or actual job value
    
    -- Audit fields
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- WEBSITE BOOKING CALENDAR TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.website_booking_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES public.business_websites(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    
    -- Booking details
    service_type VARCHAR(100) NOT NULL,
    appointment_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    
    -- Customer information
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(320),
    customer_phone VARCHAR(20) NOT NULL,
    service_address TEXT NOT NULL,
    
    -- Booking details
    booking_notes TEXT,
    special_requirements TEXT,
    access_instructions TEXT,
    
    -- Booking status
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN (
        'pending', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show'
    )),
    
    -- Integration
    calendar_event_id UUID, -- Reference to calendar system
    technician_assigned_id UUID, -- Assigned technician
    
    -- Payment information
    requires_deposit BOOLEAN DEFAULT FALSE,
    deposit_amount DECIMAL(10,2),
    deposit_paid BOOLEAN DEFAULT FALSE,
    
    -- Confirmation and reminders
    confirmation_sent BOOLEAN DEFAULT FALSE,
    reminder_24h_sent BOOLEAN DEFAULT FALSE,
    reminder_2h_sent BOOLEAN DEFAULT FALSE,
    
    -- Audit fields
    booked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confirmed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- WEBSITE CONVERSION TRACKING TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.website_conversion_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES public.business_websites(id) ON DELETE CASCADE,
    
    -- Conversion event
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
        'form_submission', 'phone_call', 'email_click', 'booking_completed',
        'quote_requested', 'emergency_call', 'chat_started', 'download'
    )),
    event_value DECIMAL(10,2) DEFAULT 0.0, -- Estimated value of conversion
    
    -- Visitor tracking
    visitor_id VARCHAR(255), -- Anonymous visitor ID
    session_id VARCHAR(255),
    
    -- Attribution
    traffic_source VARCHAR(100), -- organic, paid, direct, referral, social
    campaign_name VARCHAR(255),
    referrer_url TEXT,
    landing_page VARCHAR(500),
    
    -- Event details
    event_data JSONB DEFAULT '{}'::JSONB, -- Additional event information
    
    -- Geographic data
    visitor_country VARCHAR(100),
    visitor_region VARCHAR(100),
    visitor_city VARCHAR(100),
    
    -- Device information
    device_type VARCHAR(50), -- desktop, mobile, tablet
    browser VARCHAR(100),
    operating_system VARCHAR(100),
    
    -- Audit fields
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- GOOGLE BUSINESS PROFILE INTEGRATION TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.google_business_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    website_id UUID REFERENCES public.business_websites(id) ON DELETE SET NULL,
    
    -- Google API credentials (encrypted)
    google_account_id VARCHAR(255),
    location_id VARCHAR(255),
    place_id VARCHAR(255),
    
    -- Sync configuration
    auto_sync_enabled BOOLEAN DEFAULT TRUE,
    sync_frequency_hours INTEGER DEFAULT 24,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    
    -- Profile data cache
    profile_data JSONB DEFAULT '{}'::JSONB, -- Cached profile information
    insights_data JSONB DEFAULT '{}'::JSONB, -- Performance insights
    reviews_data JSONB DEFAULT '{}'::JSONB, -- Recent reviews
    
    -- Sync status
    sync_status VARCHAR(50) DEFAULT 'pending' CHECK (sync_status IN (
        'pending', 'active', 'error', 'disabled'
    )),
    last_error TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(business_id) -- One Google profile per business
);

-- =====================================
-- WEBSITE BUILD JOBS TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.website_build_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES public.business_websites(id) ON DELETE CASCADE,
    
    -- Job details
    job_type VARCHAR(50) NOT NULL CHECK (job_type IN (
        'initial_build', 'content_update', 'theme_update', 'deployment', 'seo_optimization'
    )),
    status VARCHAR(50) DEFAULT 'queued' CHECK (status IN (
        'queued', 'running', 'completed', 'failed', 'cancelled'
    )),
    
    -- Job configuration
    job_config JSONB DEFAULT '{}'::JSONB,
    
    -- Execution tracking
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    
    -- Results and logs
    result_data JSONB DEFAULT '{}'::JSONB,
    error_message TEXT,
    build_logs TEXT,
    
    -- Priority and retry
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10), -- 1 = highest
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- INDEXES FOR PERFORMANCE
-- =====================================

-- Website Templates
CREATE INDEX IF NOT EXISTS idx_website_templates_trade_type ON public.website_templates(trade_type);
CREATE INDEX IF NOT EXISTS idx_website_templates_trade_category ON public.website_templates(trade_category);
CREATE INDEX IF NOT EXISTS idx_website_templates_is_active ON public.website_templates(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_website_templates_is_multi_trade ON public.website_templates(is_multi_trade) WHERE is_multi_trade = TRUE;
CREATE INDEX IF NOT EXISTS idx_website_templates_supported_trades ON public.website_templates USING GIN(supported_trades);

-- Business Websites
CREATE INDEX IF NOT EXISTS idx_business_websites_business_id ON public.business_websites(business_id);
CREATE INDEX IF NOT EXISTS idx_business_websites_branding_id ON public.business_websites(branding_id);
CREATE INDEX IF NOT EXISTS idx_business_websites_template_id ON public.business_websites(template_id);
CREATE INDEX IF NOT EXISTS idx_business_websites_status ON public.business_websites(status);
CREATE INDEX IF NOT EXISTS idx_business_websites_custom_domain ON public.business_websites(custom_domain) WHERE custom_domain IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_business_websites_primary_trade ON public.business_websites(primary_trade);
CREATE INDEX IF NOT EXISTS idx_business_websites_service_areas ON public.business_websites USING GIN(service_areas);

-- Domain Registrations
CREATE INDEX IF NOT EXISTS idx_domain_registrations_business_id ON public.domain_registrations(business_id);
CREATE INDEX IF NOT EXISTS idx_domain_registrations_website_id ON public.domain_registrations(website_id);
CREATE INDEX IF NOT EXISTS idx_domain_registrations_domain ON public.domain_registrations(domain);
CREATE INDEX IF NOT EXISTS idx_domain_registrations_status ON public.domain_registrations(status);
CREATE INDEX IF NOT EXISTS idx_domain_registrations_expires_at ON public.domain_registrations(expires_at);
CREATE INDEX IF NOT EXISTS idx_domain_registrations_provider ON public.domain_registrations(provider);

-- Website Analytics
CREATE INDEX IF NOT EXISTS idx_website_analytics_website_id ON public.website_analytics(website_id);
CREATE INDEX IF NOT EXISTS idx_website_analytics_date ON public.website_analytics(date);
CREATE INDEX IF NOT EXISTS idx_website_analytics_website_date ON public.website_analytics(website_id, date);

-- SEO Keyword Tracking
CREATE INDEX IF NOT EXISTS idx_seo_keyword_tracking_website_id ON public.seo_keyword_tracking(website_id);
CREATE INDEX IF NOT EXISTS idx_seo_keyword_tracking_keyword ON public.seo_keyword_tracking(keyword);
CREATE INDEX IF NOT EXISTS idx_seo_keyword_tracking_current_rank ON public.seo_keyword_tracking(current_rank);
CREATE INDEX IF NOT EXISTS idx_seo_keyword_tracking_is_primary ON public.seo_keyword_tracking(is_primary_keyword) WHERE is_primary_keyword = TRUE;
CREATE INDEX IF NOT EXISTS idx_seo_keyword_tracking_location ON public.seo_keyword_tracking(target_location);

-- Google Business Profiles
CREATE INDEX IF NOT EXISTS idx_google_business_profiles_business_id ON public.google_business_profiles(business_id);
CREATE INDEX IF NOT EXISTS idx_google_business_profiles_website_id ON public.google_business_profiles(website_id);
CREATE INDEX IF NOT EXISTS idx_google_business_profiles_sync_status ON public.google_business_profiles(sync_status);
CREATE INDEX IF NOT EXISTS idx_google_business_profiles_last_sync ON public.google_business_profiles(last_sync_at);

-- Website Build Jobs
CREATE INDEX IF NOT EXISTS idx_website_build_jobs_website_id ON public.website_build_jobs(website_id);
CREATE INDEX IF NOT EXISTS idx_website_build_jobs_status ON public.website_build_jobs(status);
CREATE INDEX IF NOT EXISTS idx_website_build_jobs_job_type ON public.website_build_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_website_build_jobs_priority ON public.website_build_jobs(priority, created_at);
CREATE INDEX IF NOT EXISTS idx_website_build_jobs_created_at ON public.website_build_jobs(created_at);

-- Website Intake Forms
CREATE INDEX IF NOT EXISTS idx_website_intake_forms_website_id ON public.website_intake_forms(website_id);
CREATE INDEX IF NOT EXISTS idx_website_intake_forms_form_type ON public.website_intake_forms(form_type);
CREATE INDEX IF NOT EXISTS idx_website_intake_forms_is_active ON public.website_intake_forms(is_active) WHERE is_active = TRUE;

-- Website Form Submissions
CREATE INDEX IF NOT EXISTS idx_website_form_submissions_website_id ON public.website_form_submissions(website_id);
CREATE INDEX IF NOT EXISTS idx_website_form_submissions_form_id ON public.website_form_submissions(form_id);
CREATE INDEX IF NOT EXISTS idx_website_form_submissions_business_id ON public.website_form_submissions(business_id);
CREATE INDEX IF NOT EXISTS idx_website_form_submissions_lead_type ON public.website_form_submissions(lead_type);
CREATE INDEX IF NOT EXISTS idx_website_form_submissions_priority ON public.website_form_submissions(priority_level);
CREATE INDEX IF NOT EXISTS idx_website_form_submissions_status ON public.website_form_submissions(status);
CREATE INDEX IF NOT EXISTS idx_website_form_submissions_submitted_at ON public.website_form_submissions(submitted_at);
CREATE INDEX IF NOT EXISTS idx_website_form_submissions_contact_phone ON public.website_form_submissions(contact_phone);
CREATE INDEX IF NOT EXISTS idx_website_form_submissions_contact_email ON public.website_form_submissions(contact_email);

-- Website Booking Slots
CREATE INDEX IF NOT EXISTS idx_website_booking_slots_website_id ON public.website_booking_slots(website_id);
CREATE INDEX IF NOT EXISTS idx_website_booking_slots_business_id ON public.website_booking_slots(business_id);
CREATE INDEX IF NOT EXISTS idx_website_booking_slots_appointment_date ON public.website_booking_slots(appointment_date);
CREATE INDEX IF NOT EXISTS idx_website_booking_slots_status ON public.website_booking_slots(status);
CREATE INDEX IF NOT EXISTS idx_website_booking_slots_customer_phone ON public.website_booking_slots(customer_phone);
CREATE INDEX IF NOT EXISTS idx_website_booking_slots_service_type ON public.website_booking_slots(service_type);

-- Website Conversion Tracking
CREATE INDEX IF NOT EXISTS idx_website_conversion_tracking_website_id ON public.website_conversion_tracking(website_id);
CREATE INDEX IF NOT EXISTS idx_website_conversion_tracking_event_type ON public.website_conversion_tracking(event_type);
CREATE INDEX IF NOT EXISTS idx_website_conversion_tracking_event_timestamp ON public.website_conversion_tracking(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_website_conversion_tracking_traffic_source ON public.website_conversion_tracking(traffic_source);
CREATE INDEX IF NOT EXISTS idx_website_conversion_tracking_visitor_id ON public.website_conversion_tracking(visitor_id);

-- =====================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================

-- Enable RLS on all tables
ALTER TABLE public.website_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_websites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.domain_registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.website_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.seo_keyword_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.website_intake_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.website_form_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.website_booking_slots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.website_conversion_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.google_business_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.website_build_jobs ENABLE ROW LEVEL SECURITY;

-- Website Templates - System templates are public, business templates are private
CREATE POLICY "Website templates are viewable by all authenticated users" ON public.website_templates
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "System website templates are insertable by service role" ON public.website_templates
    FOR INSERT WITH CHECK (auth.role() = 'service_role' AND is_system_template = TRUE);

-- Business Websites - Only accessible by business members
CREATE POLICY "Business websites are viewable by business members" ON public.business_websites
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.business_memberships bm
            WHERE bm.business_id = business_websites.business_id
            AND bm.user_id = auth.uid()
        )
    );

CREATE POLICY "Business websites are insertable by business members" ON public.business_websites
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.business_memberships bm
            WHERE bm.business_id = business_websites.business_id
            AND bm.user_id = auth.uid()
        )
    );

CREATE POLICY "Business websites are updatable by business members" ON public.business_websites
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.business_memberships bm
            WHERE bm.business_id = business_websites.business_id
            AND bm.user_id = auth.uid()
        )
    );

-- Domain Registrations - Only accessible by business members
CREATE POLICY "Domain registrations are viewable by business members" ON public.domain_registrations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.business_memberships bm
            WHERE bm.business_id = domain_registrations.business_id
            AND bm.user_id = auth.uid()
        )
    );

CREATE POLICY "Domain registrations are insertable by business members" ON public.domain_registrations
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.business_memberships bm
            WHERE bm.business_id = domain_registrations.business_id
            AND bm.user_id = auth.uid()
        )
    );

-- Website Analytics - Only accessible by business members
CREATE POLICY "Website analytics are viewable by business members" ON public.website_analytics
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.business_websites bw
            JOIN public.business_memberships bm ON bw.business_id = bm.business_id
            WHERE bw.id = website_analytics.website_id
            AND bm.user_id = auth.uid()
        )
    );

-- SEO Keyword Tracking - Only accessible by business members
CREATE POLICY "SEO keyword tracking is viewable by business members" ON public.seo_keyword_tracking
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.business_websites bw
            JOIN public.business_memberships bm ON bw.business_id = bm.business_id
            WHERE bw.id = seo_keyword_tracking.website_id
            AND bm.user_id = auth.uid()
        )
    );

-- Google Business Profiles - Only accessible by business members
CREATE POLICY "Google business profiles are viewable by business members" ON public.google_business_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.business_memberships bm
            WHERE bm.business_id = google_business_profiles.business_id
            AND bm.user_id = auth.uid()
        )
    );

-- Website Build Jobs - Only accessible by business members and service role
CREATE POLICY "Website build jobs are viewable by business members" ON public.website_build_jobs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.business_websites bw
            JOIN public.business_memberships bm ON bw.business_id = bm.business_id
            WHERE bw.id = website_build_jobs.website_id
            AND bm.user_id = auth.uid()
        )
    );

CREATE POLICY "Website build jobs are manageable by service role" ON public.website_build_jobs
    FOR ALL USING (auth.role() = 'service_role');

-- Website Intake Forms - Only accessible by business members
CREATE POLICY "Website intake forms are viewable by business members" ON public.website_intake_forms
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.business_websites bw
            JOIN public.business_memberships bm ON bw.business_id = bm.business_id
            WHERE bw.id = website_intake_forms.website_id
            AND bm.user_id = auth.uid()
        )
    );

CREATE POLICY "Website intake forms are manageable by business members" ON public.website_intake_forms
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.business_websites bw
            JOIN public.business_memberships bm ON bw.business_id = bm.business_id
            WHERE bw.id = website_intake_forms.website_id
            AND bm.user_id = auth.uid()
        )
    );

-- Website Form Submissions - Accessible by business members and anonymous for submission
CREATE POLICY "Website form submissions are viewable by business members" ON public.website_form_submissions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.business_memberships bm
            WHERE bm.business_id = website_form_submissions.business_id
            AND bm.user_id = auth.uid()
        )
    );

CREATE POLICY "Website form submissions are insertable by anyone" ON public.website_form_submissions
    FOR INSERT WITH CHECK (true); -- Allow anonymous form submissions

CREATE POLICY "Website form submissions are updatable by business members" ON public.website_form_submissions
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.business_memberships bm
            WHERE bm.business_id = website_form_submissions.business_id
            AND bm.user_id = auth.uid()
        )
    );

-- Website Booking Slots - Accessible by business members and anonymous for booking
CREATE POLICY "Website booking slots are viewable by business members" ON public.website_booking_slots
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.business_memberships bm
            WHERE bm.business_id = website_booking_slots.business_id
            AND bm.user_id = auth.uid()
        )
    );

CREATE POLICY "Website booking slots are insertable by anyone" ON public.website_booking_slots
    FOR INSERT WITH CHECK (true); -- Allow anonymous bookings

CREATE POLICY "Website booking slots are updatable by business members" ON public.website_booking_slots
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.business_memberships bm
            WHERE bm.business_id = website_booking_slots.business_id
            AND bm.user_id = auth.uid()
        )
    );

-- Website Conversion Tracking - Insertable by anyone, viewable by business members
CREATE POLICY "Website conversion tracking is viewable by business members" ON public.website_conversion_tracking
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.business_websites bw
            JOIN public.business_memberships bm ON bw.business_id = bm.business_id
            WHERE bw.id = website_conversion_tracking.website_id
            AND bm.user_id = auth.uid()
        )
    );

CREATE POLICY "Website conversion tracking is insertable by anyone" ON public.website_conversion_tracking
    FOR INSERT WITH CHECK (true); -- Allow anonymous conversion tracking

-- =====================================
-- FUNCTIONS AND TRIGGERS
-- =====================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to all tables
DROP TRIGGER IF EXISTS update_website_templates_updated_at ON public.website_templates;
CREATE TRIGGER update_website_templates_updated_at BEFORE UPDATE ON public.website_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_business_websites_updated_at ON public.business_websites;
CREATE TRIGGER update_business_websites_updated_at BEFORE UPDATE ON public.business_websites
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_domain_registrations_updated_at ON public.domain_registrations;
CREATE TRIGGER update_domain_registrations_updated_at BEFORE UPDATE ON public.domain_registrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_seo_keyword_tracking_updated_at ON public.seo_keyword_tracking;
CREATE TRIGGER update_seo_keyword_tracking_updated_at BEFORE UPDATE ON public.seo_keyword_tracking
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_google_business_profiles_updated_at ON public.google_business_profiles;
CREATE TRIGGER update_google_business_profiles_updated_at BEFORE UPDATE ON public.google_business_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_website_build_jobs_updated_at ON public.website_build_jobs;
CREATE TRIGGER update_website_build_jobs_updated_at BEFORE UPDATE ON public.website_build_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate domain SEO score
CREATE OR REPLACE FUNCTION calculate_domain_seo_score(
    domain_name TEXT,
    primary_trade TEXT,
    all_trades TEXT[],
    trade_category TEXT
) RETURNS INTEGER AS $$
DECLARE
    score INTEGER := 100;
    domain_without_tld TEXT;
    tld TEXT;
BEGIN
    -- Extract domain parts
    domain_without_tld := split_part(domain_name, '.', 1);
    tld := '.' || split_part(domain_name, '.', 2);
    
    -- TLD scoring
    IF tld = '.com' THEN
        score := score + 20;
    ELSIF tld IN ('.services', '.pro') THEN
        score := score + 15;
    END IF;
    
    -- Length scoring
    IF length(domain_without_tld) < 15 THEN
        score := score + 15;
    ELSIF length(domain_without_tld) > 25 THEN
        score := score - 10;
    END IF;
    
    -- Trade keyword scoring
    IF position(lower(primary_trade) in lower(domain_without_tld)) > 0 THEN
        score := score + 30;
    ELSIF EXISTS (SELECT 1 FROM unnest(all_trades) AS trade WHERE position(lower(trade) in lower(domain_without_tld)) > 0) THEN
        score := score + 20;
    END IF;
    
    -- Trade category specific scoring
    IF trade_category = 'COMMERCIAL' AND (
        position('commercial' in lower(domain_without_tld)) > 0 OR
        position('pro' in lower(domain_without_tld)) > 0 OR
        position('business' in lower(domain_without_tld)) > 0
    ) THEN
        score := score + 10;
    ELSIF trade_category = 'RESIDENTIAL' AND (
        position('home' in lower(domain_without_tld)) > 0 OR
        position('house' in lower(domain_without_tld)) > 0 OR
        position('residential' in lower(domain_without_tld)) > 0
    ) THEN
        score := score + 10;
    END IF;
    
    -- Hyphen penalty
    IF position('-' in domain_without_tld) = 0 THEN
        score := score + 10;
    ELSIF (length(domain_without_tld) - length(replace(domain_without_tld, '-', ''))) = 1 THEN
        score := score + 5;
    END IF;
    
    -- Alphabetic bonus
    IF domain_without_tld ~ '^[a-zA-Z]+$' THEN
        score := score + 10;
    END IF;
    
    -- Exact match bonus
    IF lower(domain_without_tld) = lower(primary_trade) THEN
        score := score + 25;
    END IF;
    
    RETURN LEAST(score, 100);
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================

COMMENT ON TABLE public.website_templates IS 'Trade-specific website templates for AI-powered site generation';
COMMENT ON TABLE public.business_websites IS 'Business websites with trade-specific SEO optimization';
COMMENT ON TABLE public.domain_registrations IS 'Domain registration tracking with SEO scoring';
COMMENT ON TABLE public.website_analytics IS 'Website performance and SEO analytics';
COMMENT ON TABLE public.seo_keyword_tracking IS 'Keyword ranking tracking for local SEO';
COMMENT ON TABLE public.google_business_profiles IS 'Google Business Profile integration and sync';
COMMENT ON TABLE public.website_build_jobs IS 'Async website build and deployment jobs';

COMMENT ON COLUMN public.website_templates.trade_type IS 'Specific trade from CommercialTrade or ResidentialTrade enums';
COMMENT ON COLUMN public.website_templates.structure IS 'JSONB page hierarchy and component configuration';
COMMENT ON COLUMN public.business_websites.primary_trade IS 'Primary trade for SEO focus and template selection';
COMMENT ON COLUMN public.business_websites.seo_keywords IS 'Target keywords array for SEO optimization';
COMMENT ON COLUMN public.domain_registrations.seo_score IS 'Calculated SEO value score (0-100) based on trade relevance';
COMMENT ON COLUMN public.seo_keyword_tracking.trade_relevance_score IS 'How relevant this keyword is to the business trade (0-100)';
