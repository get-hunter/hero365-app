-- =============================================
-- Customer Service Membership System
-- =============================================
-- This schema handles customer-facing service memberships (residential, commercial, premium)
-- that provide discounts, priority service, and other benefits.

-- =============================================
-- MEMBERSHIP PLANS
-- =============================================
CREATE TABLE customer_membership_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Plan Details
    name VARCHAR(100) NOT NULL, -- "Residential Membership", "Commercial Membership"
    plan_type VARCHAR(20) NOT NULL CHECK (plan_type IN ('residential', 'commercial', 'premium')),
    description TEXT,
    tagline VARCHAR(200),
    
    -- Pricing
    price_monthly DECIMAL(8,2),
    price_yearly DECIMAL(8,2),
    yearly_savings DECIMAL(8,2),
    setup_fee DECIMAL(8,2) DEFAULT 0,
    
    -- Service Benefits
    discount_percentage INTEGER DEFAULT 0 CHECK (discount_percentage >= 0 AND discount_percentage <= 100),
    priority_service BOOLEAN DEFAULT FALSE,
    extended_warranty BOOLEAN DEFAULT FALSE,
    maintenance_included BOOLEAN DEFAULT FALSE,
    emergency_response BOOLEAN DEFAULT FALSE,
    free_diagnostics BOOLEAN DEFAULT FALSE,
    annual_tune_ups INTEGER DEFAULT 0,
    
    -- Display & Marketing
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    popular_badge VARCHAR(50), -- "Most Popular", "Best Value"
    color_scheme VARCHAR(7), -- hex color for UI
    sort_order INTEGER DEFAULT 0,
    
    -- Terms
    contract_length_months INTEGER, -- months
    cancellation_policy TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure business doesn't have duplicate plan types
    UNIQUE(business_id, plan_type)
);

-- =============================================
-- MEMBERSHIP BENEFITS (DETAILED)
-- =============================================
CREATE TABLE customer_membership_benefits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id UUID NOT NULL REFERENCES customer_membership_plans(id) ON DELETE CASCADE,
    
    -- Benefit Details
    title VARCHAR(150) NOT NULL,
    description TEXT,
    icon VARCHAR(50), -- icon name for UI
    value VARCHAR(50), -- "15%", "$69 value", "2 visits"
    
    -- Display
    is_highlighted BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- CUSTOMER SUBSCRIPTIONS (ACTIVE MEMBERSHIPS)
-- =============================================
CREATE TABLE customer_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES customer_membership_plans(id),
    
    -- Customer Information (linked to customer_contacts if exists)
    customer_contact_id UUID REFERENCES customer_contacts(id),
    customer_email VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20),
    customer_name VARCHAR(200) NOT NULL,
    
    -- Subscription Status
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'cancelled', 'expired')),
    
    -- Billing
    billing_period VARCHAR(10) NOT NULL CHECK (billing_period IN ('monthly', 'yearly')),
    start_date DATE NOT NULL,
    next_billing_date DATE,
    end_date DATE,
    
    -- Payment
    payment_method_id VARCHAR(100), -- Stripe/payment processor ID
    auto_renew BOOLEAN DEFAULT TRUE,
    
    -- Usage tracking
    services_used INTEGER DEFAULT 0,
    discount_savings DECIMAL(10,2) DEFAULT 0,
    last_service_date DATE,
    
    -- Cancellation
    cancelled_at TIMESTAMPTZ,
    cancelled_by VARCHAR(50), -- customer, business, system
    cancellation_reason TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure customer can only have one active subscription per business
    CONSTRAINT unique_active_subscription 
        EXCLUDE (business_id WITH =, customer_email WITH =) 
        WHERE (status = 'active')
);

-- =============================================
-- SERVICE PRICING WITH MEMBERSHIP DISCOUNTS
-- =============================================
CREATE TABLE service_membership_pricing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    service_id UUID REFERENCES business_services(id) ON DELETE CASCADE,
    
    -- Service Details (for standalone pricing not tied to business_services)
    service_name VARCHAR(200) NOT NULL,
    service_category VARCHAR(100) NOT NULL,
    
    -- Base Pricing
    base_price DECIMAL(10,2) NOT NULL,
    price_display VARCHAR(20) NOT NULL DEFAULT 'fixed' CHECK (price_display IN ('from', 'fixed', 'quote_required', 'free')),
    
    -- Member Pricing
    residential_member_price DECIMAL(10,2),
    commercial_member_price DECIMAL(10,2),
    premium_member_price DECIMAL(10,2),
    
    -- Service Details
    description TEXT,
    includes TEXT[], -- Array of what's included
    duration_estimate VARCHAR(50), -- "2-4 hours"
    minimum_labor_fee DECIMAL(10,2),
    
    -- Conditions
    height_surcharge BOOLEAN DEFAULT FALSE,
    additional_tech_fee BOOLEAN DEFAULT FALSE,
    parts_separate BOOLEAN DEFAULT FALSE,
    
    -- Display
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure unique service pricing per business
    UNIQUE(business_id, service_name, service_category)
);

-- =============================================
-- MEMBERSHIP CONTENT (MARKETING)
-- =============================================
CREATE TABLE customer_membership_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES customer_membership_plans(id) ON DELETE CASCADE,
    
    -- Marketing Copy
    headline VARCHAR(200) NOT NULL,
    subheadline VARCHAR(300),
    value_proposition TEXT,
    cta_text VARCHAR(50) DEFAULT 'Join Now',
    
    -- Social Proof
    testimonial TEXT,
    testimonial_author VARCHAR(100),
    member_count INTEGER,
    satisfaction_rate DECIMAL(3,1), -- 98.5%
    
    -- Visual Elements
    hero_image VARCHAR(500),
    logo_variants TEXT[], -- Array of logo URLs
    color_scheme JSONB, -- {"primary": "#3b82f6", "secondary": "#10b981"}
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, plan_id)
);

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- Membership plans
CREATE INDEX idx_membership_plans_business ON customer_membership_plans(business_id, is_active);
CREATE INDEX idx_membership_plans_type ON customer_membership_plans(business_id, plan_type) WHERE is_active = true;

-- Benefits
CREATE INDEX idx_membership_benefits_plan ON customer_membership_benefits(plan_id, sort_order);

-- Subscriptions
CREATE INDEX idx_subscriptions_business_status ON customer_subscriptions(business_id, status);
CREATE INDEX idx_subscriptions_customer_email ON customer_subscriptions(business_id, customer_email) WHERE status = 'active';
CREATE INDEX idx_subscriptions_next_billing ON customer_subscriptions(next_billing_date) WHERE status = 'active' AND auto_renew = true;

-- Service pricing
CREATE INDEX idx_service_pricing_business ON service_membership_pricing(business_id, is_active);
CREATE INDEX idx_service_pricing_category ON service_membership_pricing(business_id, service_category) WHERE is_active = true;

-- =============================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================

-- Enable RLS on all tables
ALTER TABLE customer_membership_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_membership_benefits ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_membership_pricing ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_membership_content ENABLE ROW LEVEL SECURITY;

-- Public read access to membership plans (for website display)
CREATE POLICY "Public can view active membership plans" ON customer_membership_plans
    FOR SELECT USING (is_active = true);

-- Public read access to benefits (for website display)
CREATE POLICY "Public can view membership benefits" ON customer_membership_benefits
    FOR SELECT USING (true);

-- Public read access to service pricing (for website display)
CREATE POLICY "Public can view service pricing" ON service_membership_pricing
    FOR SELECT USING (is_active = true);

-- Public read access to membership content (for website display)
CREATE POLICY "Public can view membership content" ON customer_membership_content
    FOR SELECT USING (true);

-- Business owners can manage their membership plans
CREATE POLICY "Business owners can manage membership plans" ON customer_membership_plans
    FOR ALL USING (
        business_id IN (
            SELECT b.id FROM businesses b 
            JOIN business_memberships bm ON b.id = bm.business_id 
            WHERE bm.user_id = auth.uid() AND bm.role IN ('owner', 'admin')
        )
    );

-- Similar policies for other tables...
CREATE POLICY "Business owners can manage membership benefits" ON customer_membership_benefits
    FOR ALL USING (
        plan_id IN (
            SELECT mp.id FROM customer_membership_plans mp
            JOIN businesses b ON mp.business_id = b.id
            JOIN business_memberships bm ON b.id = bm.business_id 
            WHERE bm.user_id = auth.uid() AND bm.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "Business owners can manage subscriptions" ON customer_subscriptions
    FOR ALL USING (
        business_id IN (
            SELECT b.id FROM businesses b 
            JOIN business_memberships bm ON b.id = bm.business_id 
            WHERE bm.user_id = auth.uid() AND bm.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "Business owners can manage service pricing" ON service_membership_pricing
    FOR ALL USING (
        business_id IN (
            SELECT b.id FROM businesses b 
            JOIN business_memberships bm ON b.id = bm.business_id 
            WHERE bm.user_id = auth.uid() AND bm.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "Business owners can manage membership content" ON customer_membership_content
    FOR ALL USING (
        business_id IN (
            SELECT b.id FROM businesses b 
            JOIN business_memberships bm ON b.id = bm.business_id 
            WHERE bm.user_id = auth.uid() AND bm.role IN ('owner', 'admin')
        )
    );
