-- Seed Austin Elite HVAC with comprehensive services
-- This will populate the business_services table with realistic HVAC services

-- First, let's verify the business exists and get the category IDs we need
DO $$
DECLARE
    business_uuid UUID := 'a1b2c3d4-e5f6-7890-1234-567890abcdef';
    hvac_repair_cat_id UUID;
    hvac_install_cat_id UUID;
    hvac_maint_cat_id UUID;
    air_conditioning_cat_id UUID;
    heating_cat_id UUID;
    ventilation_cat_id UUID;
    emergency_cat_id UUID;
    diagnostic_cat_id UUID;
    consultation_cat_id UUID;
BEGIN
    -- Get category IDs
    SELECT id INTO hvac_repair_cat_id FROM service_categories WHERE slug = 'hvac-repair';
    SELECT id INTO hvac_install_cat_id FROM service_categories WHERE slug = 'hvac-installation';
    SELECT id INTO hvac_maint_cat_id FROM service_categories WHERE slug = 'hvac-maintenance';
    SELECT id INTO air_conditioning_cat_id FROM service_categories WHERE slug = 'air-conditioning';
    SELECT id INTO heating_cat_id FROM service_categories WHERE slug = 'heating';
    SELECT id INTO ventilation_cat_id FROM service_categories WHERE slug = 'ventilation';
    SELECT id INTO emergency_cat_id FROM service_categories WHERE slug = 'emergency-service';
    SELECT id INTO diagnostic_cat_id FROM service_categories WHERE slug = 'diagnostic';
    SELECT id INTO consultation_cat_id FROM service_categories WHERE slug = 'consultation';

    -- Clear existing services for this business (if any)
    -- First delete dependent records
    DELETE FROM service_template_adoptions WHERE business_id = business_uuid;
    DELETE FROM business_services WHERE business_id = business_uuid;

    -- Insert Emergency Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, emergency_cat_id, '24/7 Emergency AC Repair', 
     'Urgent air conditioning repair service available 24/7 for cooling emergencies. Fast response time guaranteed.',
     'quote_required', 149.00, 99.00, 2.0, true, true, true, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 1),
    
    (business_uuid, emergency_cat_id, '24/7 Emergency Heating Repair',
     'Urgent heating system repair service available 24/7 for heating emergencies. Priority service for no-heat situations.',
     'quote_required', 159.00, 99.00, 2.5, true, true, true, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 2),
    
    (business_uuid, emergency_cat_id, 'Emergency HVAC Diagnostic',
     'Emergency system diagnostic to quickly identify and resolve critical HVAC issues.',
     'fixed', 99.00, 99.00, 1.5, true, false, true, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 3);

    -- Insert Air Conditioning Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, air_conditioning_cat_id, 'AC Installation & Replacement',
     'Complete air conditioning system installation with warranty. Energy-efficient units available.',
     'quote_required', 3500.00, 1500.00, 8.0, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 10),
    
    (business_uuid, air_conditioning_cat_id, 'AC Repair & Diagnostics',
     'Professional AC system diagnosis and repair. Fast, reliable service with upfront pricing.',
     'quote_required', 199.00, 89.00, 2.0, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 11),
    
    (business_uuid, air_conditioning_cat_id, 'AC Tune-Up & Maintenance',
     'Annual AC system maintenance to ensure peak performance and prevent breakdowns.',
     'fixed', 129.00, 129.00, 1.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 12),
    
    (business_uuid, air_conditioning_cat_id, 'Central Air Installation',
     'Complete central air conditioning system installation for whole-home comfort.',
     'quote_required', 4200.00, 2500.00, 12.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 13),
    
    (business_uuid, air_conditioning_cat_id, 'AC Unit Replacement',
     'Replace your old AC unit with a new energy-efficient model. Professional installation included.',
     'quote_required', 2800.00, 1200.00, 6.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 14);

    -- Insert Heating Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, heating_cat_id, 'Furnace Installation',
     'Complete furnace system installation with ductwork and setup. High-efficiency models available.',
     'quote_required', 4000.00, 2000.00, 10.0, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 20),
    
    (business_uuid, heating_cat_id, 'Furnace Repair',
     'Expert furnace troubleshooting and repair services. Same-day service available.',
     'quote_required', 179.00, 99.00, 2.5, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 21),
    
    (business_uuid, heating_cat_id, 'Heat Pump Installation',
     'Energy-efficient heat pump system installation for year-round comfort.',
     'quote_required', 5500.00, 3000.00, 12.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 22),
    
    (business_uuid, heating_cat_id, 'Heating System Tune-Up',
     'Annual heating system maintenance and efficiency check to prevent winter breakdowns.',
     'fixed', 139.00, 139.00, 2.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 23),
    
    (business_uuid, heating_cat_id, 'Thermostat Installation',
     'Smart thermostat installation and setup for optimal comfort and energy savings.',
     'fixed', 249.00, 149.00, 1.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 24);

    -- Insert Ventilation Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, ventilation_cat_id, 'Duct Cleaning Service',
     'Professional air duct cleaning and sanitization to improve indoor air quality.',
     'fixed', 299.00, 199.00, 4.0, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 30),
    
    (business_uuid, ventilation_cat_id, 'Duct Installation & Repair',
     'New ductwork installation and repair services for optimal airflow.',
     'quote_required', 2500.00, 500.00, 8.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 31),
    
    (business_uuid, ventilation_cat_id, 'Air Quality Testing',
     'Indoor air quality assessment and testing services with detailed report.',
     'fixed', 159.00, 159.00, 1.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 32),
    
    (business_uuid, ventilation_cat_id, 'Ventilation System Repair',
     'Repair and maintenance of ventilation systems for proper air circulation.',
     'quote_required', 149.00, 79.00, 2.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 33);

    -- Insert Maintenance Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, hvac_maint_cat_id, 'Annual HVAC Maintenance Plan',
     'Comprehensive yearly HVAC system maintenance with priority service and discounts.',
     'fixed', 299.00, 299.00, 4.0, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 40),
    
    (business_uuid, hvac_maint_cat_id, 'Seasonal HVAC Check-Up',
     'Bi-annual HVAC system inspection and tune-up for spring and fall seasons.',
     'fixed', 159.00, 159.00, 2.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 41),
    
    (business_uuid, hvac_maint_cat_id, 'Filter Replacement Service',
     'Regular air filter replacement service to maintain system efficiency.',
     'fixed', 49.00, 49.00, 0.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 42);

    -- Insert Diagnostic Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, diagnostic_cat_id, 'HVAC System Diagnostic',
     'Comprehensive HVAC system troubleshooting and performance analysis.',
     'fixed', 99.00, 99.00, 1.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 50),
    
    (business_uuid, diagnostic_cat_id, 'Energy Efficiency Audit',
     'Complete home energy audit to identify efficiency improvements and cost savings.',
     'fixed', 199.00, 199.00, 3.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 51);

    -- Insert Consultation Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, consultation_cat_id, 'Free Estimate',
     'No-obligation consultation and project estimate for all HVAC services.',
     'fixed', 0.00, 0.00, 1.0, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 60),
    
    (business_uuid, consultation_cat_id, 'HVAC System Design Consultation',
     'Professional HVAC system design and planning services for new construction or major renovations.',
     'hourly', 89.00, 89.00, 2.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 61);

    -- Services seeded successfully

    RAISE NOTICE 'Successfully seeded % services for Austin Elite HVAC', 
        (SELECT COUNT(*) FROM business_services WHERE business_id = business_uuid);

END $$;

-- Create some service bundles for package deals
INSERT INTO business_service_bundles (
    business_id, name, description, service_ids, bundle_price, discount_percentage,
    is_active, is_featured, terms_and_conditions
) VALUES 
(
    'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    'Complete HVAC Maintenance Package',
    'Annual maintenance package including AC tune-up, heating system check-up, and duct cleaning',
    (SELECT ARRAY_AGG(id) FROM business_services 
     WHERE business_id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef' 
     AND name IN ('AC Tune-Up & Maintenance', 'Heating System Tune-Up', 'Duct Cleaning Service')),
    499.00,
    15.0,
    true,
    true,
    'Package includes priority scheduling and 10% discount on additional repairs during the year.'
),
(
    'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    'New Home HVAC Package',
    'Complete HVAC installation package for new construction',
    (SELECT ARRAY_AGG(id) FROM business_services 
     WHERE business_id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef' 
     AND name IN ('Central Air Installation', 'Furnace Installation', 'Thermostat Installation')),
    7999.00,
    10.0,
    true,
    true,
    'Complete installation package with 5-year warranty on all equipment and labor.'
);

-- Add some sample adoption records to track which templates were used
INSERT INTO service_template_adoptions (template_id, business_id, business_service_id, customizations)
SELECT 
    st.id as template_id,
    bs.business_id,
    bs.id as business_service_id,
    '{"pricing_customized": true, "description_customized": true}'::jsonb
FROM business_services bs
JOIN service_templates st ON LOWER(st.name) = LOWER(bs.name)
WHERE bs.business_id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef'
ON CONFLICT (template_id, business_id) DO NOTHING;

-- Update template usage counts
UPDATE service_templates 
SET usage_count = usage_count + 1
WHERE id IN (
    SELECT template_id FROM service_template_adoptions 
    WHERE business_id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef'
);

COMMIT;
