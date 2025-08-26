-- Service Areas and Availability Requests Tables
-- Migration: 20250208000001_create_service_areas_tables.sql
-- Description: Create service_areas and availability_requests tables for booking widget ZIP validation
-- Date: 2025-02-08

-- Enable PostGIS extension for geography support
CREATE EXTENSION IF NOT EXISTS postgis;

-- =====================================
-- SERVICE AREAS TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS public.service_areas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    
    -- Location details
    postal_code TEXT NOT NULL,
    country_code TEXT NOT NULL DEFAULT 'US' CHECK (LENGTH(country_code) = 2),
    city TEXT,
    region TEXT, -- State/Province
    timezone TEXT DEFAULT 'America/New_York',
    
    -- Optional geographic boundary (for advanced service area definition)
    polygon GEOGRAPHY(POLYGON),
    
    -- Service area settings
    is_active BOOLEAN DEFAULT TRUE,
    dispatch_fee_cents INTEGER DEFAULT 0,
    min_response_time_hours INTEGER DEFAULT 2,
    max_response_time_hours INTEGER DEFAULT 24,
    
    -- Service availability
    emergency_services_available BOOLEAN DEFAULT TRUE,
    regular_services_available BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Unique constraint: one entry per business/postal_code/country
CREATE UNIQUE INDEX IF NOT EXISTS idx_service_areas_business_postal_country 
ON public.service_areas (business_id, postal_code, country_code);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_service_areas_business_active 
ON public.service_areas (business_id, is_active) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_service_areas_postal_lookup 
ON public.service_areas (postal_code, country_code, is_active) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_service_areas_region 
ON public.service_areas (country_code, region, is_active) WHERE is_active = TRUE;

-- =====================================
-- AVAILABILITY REQUESTS TABLE (for unsupported ZIP leads)
-- =====================================
CREATE TABLE IF NOT EXISTS public.availability_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    
    -- Contact information
    contact_name TEXT NOT NULL,
    phone_e164 TEXT, -- E.164 format: +1234567890
    email TEXT,
    
    -- Location request
    postal_code TEXT NOT NULL,
    country_code TEXT NOT NULL DEFAULT 'US' CHECK (LENGTH(country_code) = 2),
    city TEXT,
    region TEXT,
    
    -- Service request details
    service_category TEXT, -- HVAC, Plumbing, etc.
    service_type TEXT, -- Specific service if known
    urgency_level TEXT DEFAULT 'normal' CHECK (urgency_level IN ('emergency', 'urgent', 'normal', 'flexible')),
    preferred_contact_method TEXT DEFAULT 'phone' CHECK (preferred_contact_method IN ('phone', 'email', 'sms')),
    
    -- Request details
    notes TEXT,
    estimated_service_date DATE,
    
    -- Lead tracking
    status TEXT DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'scheduled', 'converted', 'declined')),
    contacted_at TIMESTAMP WITH TIME ZONE,
    converted_at TIMESTAMP WITH TIME ZONE,
    
    -- Source tracking
    source TEXT DEFAULT 'booking_widget',
    referrer_url TEXT,
    user_agent TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance indexes for availability_requests
CREATE INDEX IF NOT EXISTS idx_availability_requests_business_status 
ON public.availability_requests (business_id, status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_availability_requests_postal_lookup 
ON public.availability_requests (postal_code, country_code, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_availability_requests_created 
ON public.availability_requests (created_at DESC);

-- =====================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================

-- Enable RLS on both tables
ALTER TABLE public.service_areas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.availability_requests ENABLE ROW LEVEL SECURITY;

-- Service Areas RLS Policies
-- Allow business owners to manage their service areas
CREATE POLICY "service_areas_business_owners" ON public.service_areas
    FOR ALL USING (
        business_id IN (
            SELECT business_id FROM public.business_memberships 
            WHERE user_id = auth.uid()
        )
    );

-- Allow public read access for ZIP validation (through specific function only)
CREATE POLICY "service_areas_public_read" ON public.service_areas
    FOR SELECT USING (is_active = TRUE);

-- Availability Requests RLS Policies
-- Allow business owners to view their availability requests
CREATE POLICY "availability_requests_business_owners" ON public.availability_requests
    FOR ALL USING (
        business_id IN (
            SELECT business_id FROM public.business_memberships 
            WHERE user_id = auth.uid()
        )
    );

-- Allow anonymous users to create availability requests (for public booking widget)
CREATE POLICY "availability_requests_public_insert" ON public.availability_requests
    FOR INSERT WITH CHECK (TRUE);

-- =====================================
-- FUNCTIONS FOR PUBLIC API ACCESS
-- =====================================

-- Function to check if a postal code is supported by a business
CREATE OR REPLACE FUNCTION public.check_service_area_support(
    p_business_id UUID,
    p_postal_code TEXT,
    p_country_code TEXT DEFAULT 'US'
)
RETURNS TABLE (
    supported BOOLEAN,
    city TEXT,
    region TEXT,
    timezone TEXT,
    dispatch_fee_cents INTEGER,
    min_response_time_hours INTEGER,
    max_response_time_hours INTEGER,
    emergency_available BOOLEAN,
    regular_available BOOLEAN
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        TRUE as supported,
        sa.city,
        sa.region,
        sa.timezone,
        sa.dispatch_fee_cents,
        sa.min_response_time_hours,
        sa.max_response_time_hours,
        sa.emergency_services_available as emergency_available,
        sa.regular_services_available as regular_available
    FROM public.service_areas sa
    WHERE sa.business_id = p_business_id
        AND sa.postal_code = p_postal_code
        AND sa.country_code = p_country_code
        AND sa.is_active = TRUE
    LIMIT 1;
    
    -- If no exact match found, return unsupported
    IF NOT FOUND THEN
        RETURN QUERY SELECT 
            FALSE as supported,
            NULL::TEXT as city,
            NULL::TEXT as region,
            NULL::TEXT as timezone,
            NULL::INTEGER as dispatch_fee_cents,
            NULL::INTEGER as min_response_time_hours,
            NULL::INTEGER as max_response_time_hours,
            NULL::BOOLEAN as emergency_available,
            NULL::BOOLEAN as regular_available;
    END IF;
END;
$$;

-- Function to get nearby service areas (for suggestions)
CREATE OR REPLACE FUNCTION public.get_nearby_service_areas(
    p_business_id UUID,
    p_postal_code TEXT,
    p_country_code TEXT DEFAULT 'US',
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    postal_code TEXT,
    city TEXT,
    region TEXT,
    distance_estimate TEXT
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Simple implementation: return other postal codes in same region
    -- This can be enhanced with actual distance calculations later
    RETURN QUERY
    SELECT 
        sa.postal_code,
        sa.city,
        sa.region,
        'nearby' as distance_estimate
    FROM public.service_areas sa
    WHERE sa.business_id = p_business_id
        AND sa.country_code = p_country_code
        AND sa.is_active = TRUE
        AND sa.postal_code != p_postal_code
        AND sa.region = (
            SELECT region FROM public.service_areas 
            WHERE postal_code = p_postal_code AND country_code = p_country_code 
            LIMIT 1
        )
    ORDER BY sa.city, sa.postal_code
    LIMIT p_limit;
END;
$$;

-- =====================================
-- TRIGGER FOR UPDATED_AT
-- =====================================

-- Update updated_at timestamp on service_areas changes
CREATE OR REPLACE FUNCTION public.update_service_areas_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER service_areas_updated_at
    BEFORE UPDATE ON public.service_areas
    FOR EACH ROW
    EXECUTE FUNCTION public.update_service_areas_updated_at();

-- Update updated_at timestamp on availability_requests changes
CREATE OR REPLACE FUNCTION public.update_availability_requests_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER availability_requests_updated_at
    BEFORE UPDATE ON public.availability_requests
    FOR EACH ROW
    EXECUTE FUNCTION public.update_availability_requests_updated_at();

-- =====================================
-- SAMPLE DATA (for testing)
-- =====================================

-- Insert sample service areas for testing (Austin, TX area)
-- This will be populated by businesses through the API
INSERT INTO public.service_areas (
    business_id, 
    postal_code, 
    country_code, 
    city, 
    region, 
    timezone,
    dispatch_fee_cents,
    min_response_time_hours,
    max_response_time_hours
) VALUES 
-- Austin Elite HVAC service areas
((SELECT id FROM public.businesses WHERE name ILIKE '%Austin Elite HVAC%' LIMIT 1), '78701', 'US', 'Austin', 'TX', 'America/Chicago', 0, 2, 4),
((SELECT id FROM public.businesses WHERE name ILIKE '%Austin Elite HVAC%' LIMIT 1), '78702', 'US', 'Austin', 'TX', 'America/Chicago', 0, 2, 4),
((SELECT id FROM public.businesses WHERE name ILIKE '%Austin Elite HVAC%' LIMIT 1), '78703', 'US', 'Austin', 'TX', 'America/Chicago', 0, 2, 4),
((SELECT id FROM public.businesses WHERE name ILIKE '%Austin Elite HVAC%' LIMIT 1), '78704', 'US', 'Austin', 'TX', 'America/Chicago', 0, 2, 4),
((SELECT id FROM public.businesses WHERE name ILIKE '%Austin Elite HVAC%' LIMIT 1), '78705', 'US', 'Austin', 'TX', 'America/Chicago', 0, 2, 4)
ON CONFLICT (business_id, postal_code, country_code) DO NOTHING;

-- Grant execute permissions on functions to anon (for public API)
GRANT EXECUTE ON FUNCTION public.check_service_area_support TO anon;
GRANT EXECUTE ON FUNCTION public.get_nearby_service_areas TO anon;
