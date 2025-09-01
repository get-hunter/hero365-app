-- =============================================
-- CORE CUSTOMER MEMBERSHIP SYSTEM
-- =============================================
-- Customer service memberships for recurring revenue
-- Depends on: businesses, contacts tables

-- =============================================
-- CUSTOMER MEMBERSHIP PLANS
-- =============================================

CREATE TABLE customer_membership_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
-- CUSTOMER MEMBERSHIP BENEFITS
-- =============================================

CREATE TABLE customer_membership_benefits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES customer_membership_plans(id) ON DELETE CASCADE,
    
    -- Benefit Details
    benefit_type VARCHAR(50) NOT NULL, -- 'discount', 'service', 'priority', 'warranty'
    title VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Benefit Value
    value_type VARCHAR(20), -- 'percentage', 'fixed_amount', 'boolean', 'quantity'
    value_amount DECIMAL(10,2),
    
    -- Display
    icon VARCHAR(50), -- Icon identifier for UI
    is_highlighted BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- CUSTOMER SUBSCRIPTIONS
-- =============================================

CREATE TABLE customer_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES customer_membership_plans(id),
    
    -- Subscription Details
    subscription_number VARCHAR(50) UNIQUE,
    
    -- Billing
    billing_cycle VARCHAR(20) DEFAULT 'monthly', -- 'monthly', 'yearly'
    monthly_amount DECIMAL(8,2) NOT NULL,
    yearly_amount DECIMAL(8,2),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'paused', 'cancelled', 'expired'
    
    -- Dates
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE, -- For fixed-term contracts
    next_billing_date DATE,
    cancelled_date DATE,
    
    -- Payment
    payment_method VARCHAR(50), -- 'credit_card', 'bank_transfer', 'check'
    payment_status VARCHAR(20) DEFAULT 'current', -- 'current', 'overdue', 'failed'
    
    -- Usage Tracking
    services_used_this_period INTEGER DEFAULT 0,
    discount_amount_saved DECIMAL(10,2) DEFAULT 0,
    
    -- Cancellation
    cancellation_reason VARCHAR(100),
    cancelled_by UUID REFERENCES users(id),
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- SERVICE MEMBERSHIP PRICING
-- =============================================

CREATE TABLE service_membership_pricing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES customer_membership_plans(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES business_services(id) ON DELETE CASCADE,
    
    -- Pricing Configuration
    pricing_type VARCHAR(20) DEFAULT 'discount', -- 'discount', 'fixed_price', 'included'
    
    -- Discount Configuration
    discount_type VARCHAR(20), -- 'percentage', 'fixed_amount'
    discount_value DECIMAL(8,2),
    
    -- Fixed Price Configuration
    member_price DECIMAL(8,2),
    
    -- Inclusion Configuration
    included_quantity INTEGER DEFAULT 0, -- How many included per billing period
    overage_rate DECIMAL(8,2), -- Rate for services beyond included quantity
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT service_membership_pricing_unique UNIQUE(plan_id, service_id)
);

-- =============================================
-- CUSTOMER MEMBERSHIP CONTENT
-- =============================================

CREATE TABLE customer_membership_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Content Details
    content_type VARCHAR(50) NOT NULL, -- 'hero_section', 'benefits_list', 'testimonial', 'faq'
    title VARCHAR(200),
    content TEXT NOT NULL,
    
    -- Display Configuration
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    
    -- Targeting
    plan_types TEXT[], -- Which plan types this content applies to
    
    -- Media
    image_url TEXT,
    video_url TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- MEMBERSHIP USAGE TRACKING
-- =============================================

CREATE TABLE membership_usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES customer_subscriptions(id) ON DELETE CASCADE,
    service_id UUID REFERENCES business_services(id),
    
    -- Usage Details
    usage_date DATE NOT NULL DEFAULT CURRENT_DATE,
    service_name VARCHAR(200), -- Denormalized for historical accuracy
    
    -- Pricing
    regular_price DECIMAL(8,2),
    member_price DECIMAL(8,2),
    discount_amount DECIMAL(8,2),
    
    -- Reference to actual service record
    booking_id UUID, -- Reference to bookings table
    estimate_id UUID REFERENCES estimates(id),
    invoice_id UUID REFERENCES invoices(id),
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- MEMBERSHIP PAYMENT HISTORY
-- =============================================

CREATE TABLE membership_payment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES customer_subscriptions(id) ON DELETE CASCADE,
    
    -- Payment Details
    payment_date DATE NOT NULL,
    amount DECIMAL(8,2) NOT NULL,
    payment_method VARCHAR(50),
    
    -- Status
    payment_status VARCHAR(20) DEFAULT 'completed', -- 'completed', 'failed', 'refunded', 'pending'
    
    -- Reference Information
    transaction_id VARCHAR(100),
    payment_processor VARCHAR(50), -- 'stripe', 'square', 'manual'
    
    -- Billing Period
    billing_period_start DATE,
    billing_period_end DATE,
    
    -- Metadata
    notes TEXT,
    processed_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- INDEXES
-- =============================================

CREATE INDEX idx_customer_membership_plans_business ON customer_membership_plans(business_id);
CREATE INDEX idx_customer_membership_plans_type ON customer_membership_plans(business_id, plan_type);
CREATE INDEX idx_customer_membership_plans_active ON customer_membership_plans(business_id, is_active);

CREATE INDEX idx_customer_membership_benefits_plan ON customer_membership_benefits(plan_id);
CREATE INDEX idx_customer_membership_benefits_type ON customer_membership_benefits(benefit_type);

CREATE INDEX idx_customer_subscriptions_business ON customer_subscriptions(business_id);
CREATE INDEX idx_customer_subscriptions_contact ON customer_subscriptions(contact_id);
CREATE INDEX idx_customer_subscriptions_plan ON customer_subscriptions(plan_id);
CREATE INDEX idx_customer_subscriptions_status ON customer_subscriptions(status);
CREATE INDEX idx_customer_subscriptions_billing_date ON customer_subscriptions(next_billing_date);
CREATE INDEX idx_customer_subscriptions_number ON customer_subscriptions(subscription_number);

CREATE INDEX idx_service_membership_pricing_business ON service_membership_pricing(business_id);
CREATE INDEX idx_service_membership_pricing_plan ON service_membership_pricing(plan_id);
CREATE INDEX idx_service_membership_pricing_service ON service_membership_pricing(service_id);

CREATE INDEX idx_customer_membership_content_business ON customer_membership_content(business_id);
CREATE INDEX idx_customer_membership_content_type ON customer_membership_content(content_type);
CREATE INDEX idx_customer_membership_content_active ON customer_membership_content(is_active);

CREATE INDEX idx_membership_usage_tracking_subscription ON membership_usage_tracking(subscription_id);
CREATE INDEX idx_membership_usage_tracking_date ON membership_usage_tracking(usage_date);
CREATE INDEX idx_membership_usage_tracking_service ON membership_usage_tracking(service_id);

CREATE INDEX idx_membership_payment_history_subscription ON membership_payment_history(subscription_id);
CREATE INDEX idx_membership_payment_history_date ON membership_payment_history(payment_date);
CREATE INDEX idx_membership_payment_history_status ON membership_payment_history(payment_status);

COMMIT;
