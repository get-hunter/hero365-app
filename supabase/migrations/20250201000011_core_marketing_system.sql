-- =============================================
-- CORE MARKETING SYSTEM TABLES
-- =============================================
-- Essential portfolio, testimonials, and website content
-- Required for website builder functionality
-- Depends on: businesses tables

-- =============================================
-- FEATURED PROJECTS
-- =============================================

CREATE TABLE IF NOT EXISTS featured_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Project Details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    trade VARCHAR(100), -- 'HVAC', 'Plumbing', 'Electrical', etc.
    service_category VARCHAR(100),
    
    -- Location
    location VARCHAR(255), -- "Austin, TX" or "Downtown Austin"
    project_address TEXT,
    
    -- Project Info
    completion_date DATE,
    project_duration_days INTEGER,
    project_value DECIMAL(12,2),
    
    -- Media
    featured_image_url TEXT,
    gallery_images TEXT[], -- Array of image URLs
    before_images TEXT[] DEFAULT '{}', -- Array of before project images
    after_images TEXT[] DEFAULT '{}', -- Array of after project images
    video_url TEXT,
    
    -- Project Details
    project_duration TEXT, -- Human readable duration (e.g., "3 days", "2 weeks")
    challenges_faced TEXT[] DEFAULT '{}', -- Array of challenges encountered
    solutions_provided TEXT[] DEFAULT '{}', -- Array of solutions implemented
    equipment_installed TEXT[] DEFAULT '{}', -- Array of equipment/systems installed
    warranty_info TEXT, -- Warranty information
    tags TEXT[] DEFAULT '{}', -- Array of tags for categorization
    
    -- SEO
    slug VARCHAR(255) UNIQUE,
    seo_slug VARCHAR(255), -- Alias for slug for API compatibility
    meta_description TEXT,
    
    -- Display
    is_featured BOOLEAN DEFAULT false,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    
    -- Customer Info (optional)
    customer_name VARCHAR(255),
    customer_testimonial TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- PROJECT CATEGORIES
-- =============================================

CREATE TABLE IF NOT EXISTS project_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Category Details
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(100), -- Icon name or URL
    
    -- Display
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, slug)
);

-- =============================================
-- PROJECT TAGS
-- =============================================

CREATE TABLE IF NOT EXISTS project_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Tag Details
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT '#3b82f6', -- Hex color
    
    -- Usage
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, slug)
);

-- =============================================
-- TESTIMONIALS
-- =============================================

CREATE TABLE IF NOT EXISTS testimonials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Customer Details
    customer_name VARCHAR(255) NOT NULL,
    customer_title VARCHAR(255), -- "Homeowner", "Property Manager", etc.
    customer_location VARCHAR(255), -- "Austin, TX"
    customer_avatar_url TEXT,
    
    -- Testimonial Content
    testimonial_text TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    
    -- Service Details
    service_provided VARCHAR(255),
    project_date DATE,
    
    -- Display Settings
    is_featured BOOLEAN DEFAULT false,
    display_on_website BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    
    -- Source
    source VARCHAR(50) DEFAULT 'direct', -- 'direct', 'google', 'yelp', 'facebook'
    source_url TEXT,
    
    -- Verification
    is_verified BOOLEAN DEFAULT false,
    verified_at TIMESTAMPTZ,
    verified_by UUID REFERENCES users(id),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- AWARDS & CERTIFICATIONS
-- =============================================

CREATE TABLE IF NOT EXISTS awards_certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Award/Certification Details
    title VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255),
    description TEXT,
    
    -- Type
    type VARCHAR(50) NOT NULL, -- 'award', 'certification', 'license', 'membership'
    category VARCHAR(100), -- 'safety', 'quality', 'training', 'industry'
    
    -- Dates
    issued_date DATE,
    expiry_date DATE,
    
    -- Media
    badge_image_url TEXT,
    certificate_url TEXT,
    
    -- Display
    display_on_website BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- OEM PARTNERSHIPS
-- =============================================

CREATE TABLE IF NOT EXISTS oem_partnerships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Partner Details
    partner_name VARCHAR(255) NOT NULL,
    partner_type VARCHAR(50), -- 'manufacturer', 'distributor', 'supplier'
    description TEXT,
    
    -- Partnership Details
    partnership_level VARCHAR(50), -- 'authorized_dealer', 'certified_installer', 'preferred_contractor'
    partnership_since DATE,
    
    -- Media
    logo_url TEXT,
    partner_website_url TEXT,
    
    -- Display
    display_on_website BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- INDEXES
-- =============================================

CREATE INDEX IF NOT EXISTS idx_featured_projects_business ON featured_projects(business_id);
CREATE INDEX IF NOT EXISTS idx_featured_projects_trade ON featured_projects(trade);
CREATE INDEX IF NOT EXISTS idx_featured_projects_featured ON featured_projects(is_featured);
CREATE INDEX IF NOT EXISTS idx_featured_projects_active ON featured_projects(is_active);
CREATE INDEX IF NOT EXISTS idx_featured_projects_slug ON featured_projects(slug);

CREATE INDEX IF NOT EXISTS idx_project_categories_business ON project_categories(business_id);
CREATE INDEX IF NOT EXISTS idx_project_categories_slug ON project_categories(slug);
CREATE INDEX IF NOT EXISTS idx_project_categories_active ON project_categories(is_active);

CREATE INDEX IF NOT EXISTS idx_project_tags_business ON project_tags(business_id);
CREATE INDEX IF NOT EXISTS idx_project_tags_slug ON project_tags(slug);
CREATE INDEX IF NOT EXISTS idx_project_tags_usage ON project_tags(usage_count);

CREATE INDEX IF NOT EXISTS idx_testimonials_business ON testimonials(business_id);
CREATE INDEX IF NOT EXISTS idx_testimonials_featured ON testimonials(is_featured);
CREATE INDEX IF NOT EXISTS idx_testimonials_display ON testimonials(display_on_website);
CREATE INDEX IF NOT EXISTS idx_testimonials_rating ON testimonials(rating);

CREATE INDEX IF NOT EXISTS idx_awards_certifications_business ON awards_certifications(business_id);
CREATE INDEX IF NOT EXISTS idx_awards_certifications_type ON awards_certifications(type);
CREATE INDEX IF NOT EXISTS idx_awards_certifications_display ON awards_certifications(display_on_website);

CREATE INDEX IF NOT EXISTS idx_oem_partnerships_business ON oem_partnerships(business_id);
CREATE INDEX IF NOT EXISTS idx_oem_partnerships_display ON oem_partnerships(display_on_website);

COMMIT;
