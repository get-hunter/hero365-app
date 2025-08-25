-- Create service template system for standardized service management
-- This addresses the issue where each business recreates the same services manually

-- 1. Service Categories (standardized across platform)
CREATE TABLE service_categories (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar(100) NOT NULL,
    description text,
    slug varchar(100) NOT NULL UNIQUE,
    trade_types text[] NOT NULL, -- ['hvac', 'plumbing', 'electrical', 'landscaping', etc.]
    category_type varchar(50) NOT NULL CHECK (category_type IN ('equipment', 'service_type', 'specialization')),
    icon varchar(100), -- Icon name for UI (lucide icon names)
    parent_id uuid REFERENCES service_categories(id),
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 2. Service Templates (pre-defined industry services)
CREATE TABLE service_templates (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id uuid NOT NULL REFERENCES service_categories(id),
    name varchar(200) NOT NULL,
    description text NOT NULL,
    trade_types text[] NOT NULL, -- Which trades typically offer this service
    service_type varchar(50) NOT NULL CHECK (service_type IN ('product', 'service', 'maintenance_plan', 'emergency')),
    pricing_model varchar(50) NOT NULL CHECK (pricing_model IN ('fixed', 'hourly', 'per_unit', 'quote_required', 'tiered')),
    default_unit_price numeric(10,2),
    price_range_min numeric(10,2),
    price_range_max numeric(10,2),
    unit_of_measure varchar(50) DEFAULT 'service',
    estimated_duration_hours numeric(4,2),
    tags text[], -- ['emergency', 'seasonal', 'diagnostic', 'installation', 'maintenance']
    is_common boolean DEFAULT false, -- Most businesses in this trade offer this
    is_emergency boolean DEFAULT false,
    requires_license boolean DEFAULT false,
    skill_level varchar(20) CHECK (skill_level IN ('basic', 'intermediate', 'advanced', 'expert')),
    prerequisites text[], -- Other services that should be offered first
    upsell_templates uuid[], -- Related services to suggest
    seasonal_demand jsonb, -- {"peak_months": ["june", "july", "august"], "demand_multiplier": 1.3}
    metadata jsonb DEFAULT '{}',
    usage_count integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 3. Business Services (business instances of services)
CREATE TABLE business_services (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES businesses(id),
    template_id uuid REFERENCES service_templates(id), -- null for completely custom services
    category_id uuid NOT NULL REFERENCES service_categories(id),
    name varchar(200) NOT NULL,
    description text,
    pricing_model varchar(50) NOT NULL,
    unit_price numeric(10,2),
    minimum_price numeric(10,2),
    unit_of_measure varchar(50) DEFAULT 'service',
    estimated_duration_hours numeric(4,2),
    markup_percentage numeric(5,2) DEFAULT 0,
    cost_price numeric(10,2) DEFAULT 0,
    is_active boolean DEFAULT true,
    is_featured boolean DEFAULT false,
    is_emergency boolean DEFAULT false,
    requires_booking boolean DEFAULT true,
    availability_schedule jsonb, -- Custom availability for this service
    service_areas text[], -- Geographic areas where this service is offered
    booking_settings jsonb DEFAULT '{}', -- Service-specific booking rules
    warranty_terms text,
    terms_and_conditions text,
    custom_fields jsonb DEFAULT '{}',
    sort_order integer DEFAULT 0,
    total_bookings integer DEFAULT 0,
    average_rating numeric(3,2),
    last_booked_at timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    
    -- Ensure business can't have duplicate services
    UNIQUE(business_id, name)
);

-- 4. Business Service Bundles (package deals)
CREATE TABLE business_service_bundles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES businesses(id),
    name varchar(200) NOT NULL,
    description text,
    service_ids uuid[] NOT NULL, -- References to business_services.id
    bundle_price numeric(10,2),
    discount_amount numeric(10,2),
    discount_percentage numeric(5,2),
    is_active boolean DEFAULT true,
    is_seasonal boolean DEFAULT false,
    is_featured boolean DEFAULT false,
    valid_from date,
    valid_until date,
    max_bookings integer, -- Limit number of times this bundle can be booked
    current_bookings integer DEFAULT 0,
    terms_and_conditions text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    
    UNIQUE(business_id, name)
);

-- 5. Service Template Usage Tracking
CREATE TABLE service_template_adoptions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id uuid NOT NULL REFERENCES service_templates(id),
    business_id uuid NOT NULL REFERENCES businesses(id),
    business_service_id uuid NOT NULL REFERENCES business_services(id),
    customizations jsonb DEFAULT '{}', -- What was customized from template
    adopted_at timestamptz DEFAULT now(),
    
    UNIQUE(template_id, business_id)
);

-- Create indexes for performance
CREATE INDEX idx_service_categories_trade_types ON service_categories USING GIN (trade_types);
CREATE INDEX idx_service_categories_slug ON service_categories (slug);
CREATE INDEX idx_service_categories_parent_id ON service_categories (parent_id);

CREATE INDEX idx_service_templates_category_id ON service_templates (category_id);
CREATE INDEX idx_service_templates_trade_types ON service_templates USING GIN (trade_types);
CREATE INDEX idx_service_templates_is_common ON service_templates (is_common);
CREATE INDEX idx_service_templates_tags ON service_templates USING GIN (tags);

CREATE INDEX idx_business_services_business_id ON business_services (business_id);
CREATE INDEX idx_business_services_template_id ON business_services (template_id);
CREATE INDEX idx_business_services_category_id ON business_services (category_id);
CREATE INDEX idx_business_services_active_featured ON business_services (is_active, is_featured);

CREATE INDEX idx_business_service_bundles_business_id ON business_service_bundles (business_id);
CREATE INDEX idx_business_service_bundles_active ON business_service_bundles (is_active);

-- Enable RLS
ALTER TABLE service_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_services ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_service_bundles ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_template_adoptions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Service categories and templates are public (readable by all)
CREATE POLICY "Service categories are publicly readable" ON service_categories FOR SELECT USING (true);
CREATE POLICY "Service templates are publicly readable" ON service_templates FOR SELECT USING (true);

-- Business services are private to the business
CREATE POLICY "Business services are private to business" ON business_services 
FOR ALL USING (business_id IN (
    SELECT business_id FROM business_memberships 
    WHERE user_id = auth.uid() AND is_active = true
));

CREATE POLICY "Business service bundles are private to business" ON business_service_bundles 
FOR ALL USING (business_id IN (
    SELECT business_id FROM business_memberships 
    WHERE user_id = auth.uid() AND is_active = true
));

CREATE POLICY "Service template adoptions are private to business" ON service_template_adoptions 
FOR ALL USING (business_id IN (
    SELECT business_id FROM business_memberships 
    WHERE user_id = auth.uid() AND is_active = true
));

-- Add triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_service_categories_updated_at BEFORE UPDATE ON service_categories 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_templates_updated_at BEFORE UPDATE ON service_templates 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_business_services_updated_at BEFORE UPDATE ON business_services 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_business_service_bundles_updated_at BEFORE UPDATE ON business_service_bundles 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
