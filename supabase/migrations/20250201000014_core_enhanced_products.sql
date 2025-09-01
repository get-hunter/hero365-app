-- =============================================
-- CORE ENHANCED PRODUCT SYSTEM
-- =============================================
-- Product variants and installation options
-- Depends on: products table from core_ecommerce_system

-- =============================================
-- SERVICE CATEGORIES
-- =============================================

CREATE TABLE service_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Category Details
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Hierarchy
    parent_category_id UUID REFERENCES service_categories(id),
    level INTEGER DEFAULT 0,
    
    -- Display
    display_order INTEGER DEFAULT 0,
    icon VARCHAR(50), -- Icon identifier
    color VARCHAR(7), -- Hex color code
    
    -- SEO
    meta_title VARCHAR(200),
    meta_description VARCHAR(300),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, slug)
);

-- =============================================
-- PRODUCT VARIANTS
-- =============================================

CREATE TABLE product_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    
    -- Variant Details
    variant_name VARCHAR(255) NOT NULL,
    sku VARCHAR(100),
    
    -- Variant Attributes
    attributes JSONB DEFAULT '{}', -- size, color, material, etc.
    
    -- Pricing
    price DECIMAL(10,2) NOT NULL,
    compare_at_price DECIMAL(10,2), -- Original price for discounts
    cost_price DECIMAL(10,2), -- For profit calculations
    
    -- Inventory
    track_inventory BOOLEAN DEFAULT TRUE,
    inventory_quantity INTEGER DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 5,
    
    -- Physical Properties
    weight_lbs DECIMAL(8,2),
    dimensions JSONB, -- {"length": 12, "width": 8, "height": 4}
    
    -- Media
    image_urls TEXT[], -- Array of variant-specific images
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE, -- Is this the default variant?
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(product_id, sku)
);

-- =============================================
-- PRODUCT INSTALLATION OPTIONS
-- =============================================

CREATE TABLE product_installation_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    
    -- Installation Details
    option_name VARCHAR(255) NOT NULL,
    option_type VARCHAR(50) NOT NULL, -- 'basic', 'standard', 'premium', 'custom'
    description TEXT,
    
    -- Pricing
    installation_fee DECIMAL(10,2) NOT NULL DEFAULT 0,
    hourly_rate DECIMAL(10,2),
    estimated_hours DECIMAL(4,2),
    
    -- Requirements
    requires_permit BOOLEAN DEFAULT FALSE,
    requires_inspection BOOLEAN DEFAULT FALSE,
    requires_specialty_tools BOOLEAN DEFAULT FALSE,
    
    -- Skill Requirements
    required_skills TEXT[], -- Array of skill names
    minimum_experience_years INTEGER DEFAULT 0,
    certification_required VARCHAR(100),
    
    -- Scheduling
    estimated_duration_hours DECIMAL(4,2) NOT NULL DEFAULT 1.0,
    preparation_time_hours DECIMAL(4,2) DEFAULT 0,
    cleanup_time_hours DECIMAL(4,2) DEFAULT 0,
    
    -- Materials and Tools
    included_materials JSONB DEFAULT '[]', -- What's included in the installation
    required_tools JSONB DEFAULT '[]', -- Tools needed for installation
    additional_materials JSONB DEFAULT '[]', -- Materials customer needs to provide
    
    -- Warranty and Service
    warranty_period_months INTEGER DEFAULT 12,
    warranty_terms TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_days INTEGER,
    
    -- Complexity and Risk
    complexity_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'expert'
    risk_level VARCHAR(20) DEFAULT 'low', -- 'low', 'medium', 'high'
    safety_requirements TEXT,
    
    -- Availability
    is_available BOOLEAN DEFAULT TRUE,
    seasonal_availability JSONB DEFAULT '{}', -- Seasonal restrictions
    geographic_restrictions TEXT[],
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- PRODUCT BUNDLES
-- =============================================

CREATE TABLE product_bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Bundle Details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    bundle_type VARCHAR(50) DEFAULT 'standard', -- 'standard', 'seasonal', 'promotional'
    
    -- Pricing
    bundle_price DECIMAL(10,2) NOT NULL,
    individual_total DECIMAL(10,2), -- Sum of individual product prices
    savings_amount DECIMAL(10,2) GENERATED ALWAYS AS (individual_total - bundle_price) STORED,
    savings_percentage DECIMAL(5,2),
    
    -- Display
    display_order INTEGER DEFAULT 0,
    featured_image_url TEXT,
    
    -- Availability
    is_active BOOLEAN DEFAULT TRUE,
    start_date DATE,
    end_date DATE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- PRODUCT BUNDLE ITEMS
-- =============================================

CREATE TABLE product_bundle_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bundle_id UUID NOT NULL REFERENCES product_bundles(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_id UUID REFERENCES product_variants(id),
    
    -- Bundle Item Configuration
    quantity INTEGER NOT NULL DEFAULT 1,
    is_optional BOOLEAN DEFAULT FALSE,
    
    -- Pricing Override (if different from product price)
    override_price DECIMAL(10,2),
    
    -- Display
    display_order INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(bundle_id, product_id, variant_id)
);

-- =============================================
-- PRODUCT REVIEWS
-- =============================================

CREATE TABLE product_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id),
    
    -- Review Details
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    review_text TEXT,
    
    -- Reviewer Information (if not linked to contact)
    reviewer_name VARCHAR(255),
    reviewer_email VARCHAR(255),
    
    -- Review Status
    is_verified BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    -- Helpful Votes
    helpful_votes INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    
    -- Metadata
    reviewed_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- INDEXES
-- =============================================

CREATE INDEX idx_service_categories_business ON service_categories(business_id);
CREATE INDEX idx_service_categories_parent ON service_categories(parent_category_id);
CREATE INDEX idx_service_categories_slug ON service_categories(business_id, slug);
CREATE INDEX idx_service_categories_active ON service_categories(is_active);

CREATE INDEX idx_product_variants_product ON product_variants(product_id);
CREATE INDEX idx_product_variants_sku ON product_variants(sku);
CREATE INDEX idx_product_variants_active ON product_variants(is_active);
CREATE INDEX idx_product_variants_default ON product_variants(product_id, is_default);

CREATE INDEX idx_product_installation_options_business ON product_installation_options(business_id);
CREATE INDEX idx_product_installation_options_product ON product_installation_options(product_id);
CREATE INDEX idx_product_installation_options_type ON product_installation_options(option_type);
CREATE INDEX idx_product_installation_options_available ON product_installation_options(is_available);

CREATE INDEX idx_product_bundles_business ON product_bundles(business_id);
CREATE INDEX idx_product_bundles_active ON product_bundles(is_active);
CREATE INDEX idx_product_bundles_dates ON product_bundles(start_date, end_date);

CREATE INDEX idx_product_bundle_items_bundle ON product_bundle_items(bundle_id);
CREATE INDEX idx_product_bundle_items_product ON product_bundle_items(product_id);
CREATE INDEX idx_product_bundle_items_variant ON product_bundle_items(variant_id);

CREATE INDEX idx_product_reviews_product ON product_reviews(product_id);
CREATE INDEX idx_product_reviews_contact ON product_reviews(contact_id);
CREATE INDEX idx_product_reviews_rating ON product_reviews(rating);
CREATE INDEX idx_product_reviews_approved ON product_reviews(is_approved);
CREATE INDEX idx_product_reviews_featured ON product_reviews(is_featured);

COMMIT;
