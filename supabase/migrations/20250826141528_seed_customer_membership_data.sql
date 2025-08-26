-- =============================================
-- Seed Customer Membership System Data
-- =============================================
-- Populate the database with default membership plans and pricing data

-- =============================================
-- INSERT MEMBERSHIP PLANS FOR DEFAULT BUSINESS
-- =============================================

-- Get the default business ID (Austin Elite Home Services)
DO $$ 
DECLARE
    default_business_id UUID;
BEGIN
    -- Find the default business or create it if it doesn't exist
    SELECT id INTO default_business_id FROM businesses WHERE name = 'Austin Elite Home Services' LIMIT 1;
    
    IF default_business_id IS NULL THEN
        -- If no business exists, use the hardcoded ID from config
        default_business_id := 'a1b2c3d4-e5f6-7890-1234-567890abcdef'::UUID;
    END IF;

    -- Insert Residential Membership Plan
    INSERT INTO customer_membership_plans (
        id, business_id, name, plan_type, description, tagline,
        price_monthly, price_yearly, yearly_savings,
        discount_percentage, priority_service, extended_warranty, 
        maintenance_included, emergency_response, free_diagnostics, annual_tune_ups,
        is_active, is_featured, color_scheme, sort_order,
        contract_length_months, cancellation_policy
    ) VALUES (
        gen_random_uuid(), default_business_id, 
        'Residential Membership', 'residential',
        'Comprehensive service plan for homeowners',
        'Priority service with exclusive savings',
        29.99, 299.99, 59.89,
        15, true, true, true, false, true, 2,
        true, false, '#10b981', 1,
        12, 'Cancel anytime with 30 days notice'
    ) ON CONFLICT (business_id, plan_type) DO NOTHING;

    -- Insert Commercial Membership Plan
    INSERT INTO customer_membership_plans (
        id, business_id, name, plan_type, description, tagline,
        price_monthly, price_yearly, yearly_savings,
        discount_percentage, priority_service, extended_warranty, 
        maintenance_included, emergency_response, free_diagnostics, annual_tune_ups,
        is_active, is_featured, popular_badge, color_scheme, sort_order,
        contract_length_months, cancellation_policy
    ) VALUES (
        gen_random_uuid(), default_business_id,
        'Commercial Membership', 'commercial',
        'Professional service plan for businesses',
        'Business-focused solutions with priority support',
        89.99, 899.99, 179.89,
        20, true, true, true, true, true, 4,
        true, true, 'Most Popular', '#3b82f6', 2,
        12, 'Cancel anytime with 30 days notice'
    ) ON CONFLICT (business_id, plan_type) DO NOTHING;

    -- Insert Premium Membership Plan
    INSERT INTO customer_membership_plans (
        id, business_id, name, plan_type, description, tagline,
        price_monthly, price_yearly, yearly_savings,
        discount_percentage, priority_service, extended_warranty, 
        maintenance_included, emergency_response, free_diagnostics, annual_tune_ups,
        is_active, is_featured, color_scheme, sort_order,
        contract_length_months, cancellation_policy
    ) VALUES (
        gen_random_uuid(), default_business_id,
        'Premium Membership', 'premium',
        'Ultimate service plan with comprehensive coverage',
        'Complete peace of mind with maximum benefits',
        149.99, 1499.99, 299.89,
        25, true, true, true, true, true, 6,
        true, false, '#8b5cf6', 3,
        12, 'Cancel anytime with 30 days notice'
    ) ON CONFLICT (business_id, plan_type) DO NOTHING;

END $$;

-- =============================================
-- INSERT MEMBERSHIP BENEFITS
-- =============================================
DO $$
DECLARE
    residential_plan_id UUID;
    commercial_plan_id UUID;
    premium_plan_id UUID;
    default_business_id UUID;
BEGIN
    -- Get business and plan IDs
    SELECT id INTO default_business_id FROM businesses WHERE name = 'Austin Elite Home Services' LIMIT 1;
    IF default_business_id IS NULL THEN
        default_business_id := 'a1b2c3d4-e5f6-7890-1234-567890abcdef'::UUID;
    END IF;

    SELECT id INTO residential_plan_id FROM customer_membership_plans 
    WHERE business_id = default_business_id AND plan_type = 'residential';
    
    SELECT id INTO commercial_plan_id FROM customer_membership_plans 
    WHERE business_id = default_business_id AND plan_type = 'commercial';
    
    SELECT id INTO premium_plan_id FROM customer_membership_plans 
    WHERE business_id = default_business_id AND plan_type = 'premium';

    -- Residential Benefits
    INSERT INTO customer_membership_benefits (plan_id, title, description, icon, value, is_highlighted, sort_order) VALUES
    (residential_plan_id, 'Priority Scheduling', 'Get scheduled before non-members', 'calendar-check', NULL, true, 1),
    (residential_plan_id, '15% Service Discount', 'Save on all repair and installation services', 'percent', '15%', true, 2),
    (residential_plan_id, 'FREE Diagnostics', 'No charge for service call diagnostics', 'search', '$69 value', false, 3),
    (residential_plan_id, 'Annual Maintenance', '2 preventive maintenance visits per year', 'wrench', '2 visits', false, 4),
    (residential_plan_id, 'Extended Labor Warranty', 'Up to 2 years labor warranty on repairs', 'shield-check', '2 years', false, 5)
    ON CONFLICT DO NOTHING;

    -- Commercial Benefits
    INSERT INTO customer_membership_benefits (plan_id, title, description, icon, value, is_highlighted, sort_order) VALUES
    (commercial_plan_id, 'Priority Business Support', 'Same-day service for business emergencies', 'zap', NULL, true, 1),
    (commercial_plan_id, '20% Service Discount', 'Save on all commercial services', 'percent', '20%', true, 2),
    (commercial_plan_id, '24/7 Emergency Response', 'Round-the-clock emergency service', 'phone', NULL, true, 3),
    (commercial_plan_id, 'Quarterly Maintenance', '4 preventive maintenance visits per year', 'calendar', '4 visits', false, 4),
    (commercial_plan_id, 'Extended Commercial Warranty', 'Up to 3 years warranty on commercial equipment', 'shield-check', '3 years', false, 5),
    (commercial_plan_id, 'Dedicated Account Manager', 'Personal contact for all service needs', 'user-check', NULL, false, 6)
    ON CONFLICT DO NOTHING;

    -- Premium Benefits
    INSERT INTO customer_membership_benefits (plan_id, title, description, icon, value, is_highlighted, sort_order) VALUES
    (premium_plan_id, 'VIP Priority Service', 'Highest priority scheduling and service', 'crown', NULL, true, 1),
    (premium_plan_id, '25% Service Discount', 'Maximum savings on all services', 'percent', '25%', true, 2),
    (premium_plan_id, 'Priority Emergency Response', 'First in line for emergency services', 'siren', NULL, true, 3),
    (premium_plan_id, 'Bi-Monthly Maintenance', '6 comprehensive maintenance visits per year', 'calendar-days', '6 visits', false, 4),
    (premium_plan_id, 'Maximum Warranty Coverage', 'Up to 5 years warranty on all work', 'shield-check', '5 years', false, 5),
    (premium_plan_id, 'Concierge Service', 'Personal service coordinator', 'headphones', NULL, false, 6),
    (premium_plan_id, 'Parts Discount', 'Discounted rates on replacement parts', 'cog', '15% off', false, 7)
    ON CONFLICT DO NOTHING;

END $$;

-- =============================================
-- INSERT SERVICE PRICING DATA
-- =============================================
DO $$
DECLARE
    default_business_id UUID;
BEGIN
    -- Get business ID
    SELECT id INTO default_business_id FROM businesses WHERE name = 'Austin Elite Home Services' LIMIT 1;
    IF default_business_id IS NULL THEN
        default_business_id := 'a1b2c3d4-e5f6-7890-1234-567890abcdef'::UUID;
    END IF;

    -- HVAC Services
    INSERT INTO service_membership_pricing (
        business_id, service_name, service_category,
        base_price, price_display, description,
        residential_member_price, commercial_member_price, premium_member_price,
        includes, duration_estimate
    ) VALUES 
    (default_business_id, 'HVAC Installation Estimate', 'HVAC', 0, 'free', 'Free professional estimate for HVAC installation', 0, 0, 0, ARRAY['Site evaluation', 'Equipment sizing', 'Written proposal'], NULL),
    (default_business_id, 'Heat Pump Installation/Replacement (Fan Coil and Heat Pump)', 'HVAC', 4500, 'from', 'Complete heat pump system installation', 3825, 3600, 3375, ARRAY['Equipment', 'Installation', 'Basic warranty'], '4-8 hours'),
    (default_business_id, 'AC + Furnace Installation', 'HVAC', 4500, 'from', 'Complete HVAC system installation', 3825, 3600, 3375, ARRAY[]::text[], NULL),
    (default_business_id, 'AC + Furnace Replacement', 'HVAC', 3500, 'from', 'Replace existing HVAC system', 2975, 2800, 2625, ARRAY[]::text[], NULL),
    (default_business_id, 'Service Call (Diagnostic)', 'HVAC', 69, 'fixed', 'Professional system diagnostic', 0, 0, 0, ARRAY[]::text[], NULL),
    (default_business_id, 'Furnace Repair', 'HVAC', 199, 'from', 'Professional furnace repair service', 169, 159, 149, ARRAY[]::text[], NULL),
    (default_business_id, 'AC Repair', 'HVAC', 199, 'from', 'Professional air conditioning repair', 169, 159, 149, ARRAY[]::text[], NULL)
    ON CONFLICT (business_id, service_name, service_category) DO NOTHING;

    -- Electrical Services  
    INSERT INTO service_membership_pricing (
        business_id, service_name, service_category,
        base_price, price_display, description,
        residential_member_price, commercial_member_price, premium_member_price,
        includes
    ) VALUES
    (default_business_id, 'Electrical Estimate', 'Electrical', 0, 'free', 'Free electrical work estimate', 0, 0, 0, ARRAY[]::text[]),
    (default_business_id, 'Service Call (Diagnostic)', 'Electrical', 69, 'fixed', 'Electrical system diagnostic', 0, 0, 0, ARRAY[]::text[]),
    (default_business_id, 'Outlet/Switch 120V Installation/Replacement', 'Electrical', 300, 'from', 'Standard outlet or switch work', 255, 240, 225, ARRAY[]::text[]),
    (default_business_id, 'EV Charger Installation', 'Electrical', 700, 'from', 'Complete EV charger installation', 595, 560, 525, ARRAY[]::text[]),
    (default_business_id, 'Electrical Panel Replacement', 'Electrical', 2000, 'from', 'Main electrical panel replacement', 1700, 1600, 1500, ARRAY[]::text[])
    ON CONFLICT (business_id, service_name, service_category) DO NOTHING;

    -- Plumbing Services
    INSERT INTO service_membership_pricing (
        business_id, service_name, service_category,
        base_price, price_display, description,
        residential_member_price, commercial_member_price, premium_member_price,
        includes
    ) VALUES
    (default_business_id, 'Plumbing Estimate', 'Plumbing', 0, 'free', 'Free plumbing work estimate', 0, 0, 0, ARRAY[]::text[]),
    (default_business_id, 'Water Heater Repair', 'Plumbing', 240, 'from', 'Water heater repair service', 204, 192, 180, ARRAY[]::text[]),
    (default_business_id, '40 gal Gas Tank Water Heater Replacement', 'Plumbing', 1800, 'from', '40 gallon gas water heater replacement', 1530, 1440, 1350, ARRAY[]::text[]),
    (default_business_id, '50 gal Gas Tank Water Heater Replacement', 'Plumbing', 1950, 'from', '50 gallon gas water heater replacement', 1658, 1560, 1463, ARRAY[]::text[]),
    (default_business_id, 'Main Water Valve Replacement', 'Plumbing', 450, 'from', 'Main water shutoff valve replacement', 383, 360, 338, ARRAY[]::text[])
    ON CONFLICT (business_id, service_name, service_category) DO NOTHING;

    -- Refrigeration Services
    INSERT INTO service_membership_pricing (
        business_id, service_name, service_category,
        base_price, price_display, description,
        residential_member_price, commercial_member_price, premium_member_price,
        includes
    ) VALUES
    (default_business_id, 'Walk-in Cooler/Walk-in Freezer Installation Estimate', 'Refrigeration', 0, 'free', 'Commercial refrigeration estimate', 0, 0, 0, ARRAY[]::text[]),
    (default_business_id, 'Walk-in Cooler/Walk-in Freezer Diagnostic', 'Refrigeration', 99, 'fixed', 'Commercial refrigeration diagnostic', 0, 0, 0, ARRAY[]::text[]),
    (default_business_id, 'Commercial Refrigerator Repair', 'Refrigeration', 199, 'from', 'Commercial refrigeration repair', 169, 159, 149, ARRAY[]::text[])
    ON CONFLICT (business_id, service_name, service_category) DO NOTHING;

END $$;
