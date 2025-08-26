-- Add Electrical and Plumbing services to Austin Elite HVAC
-- This expands the business to be a multi-trade contractor matching the website navigation

DO $$
DECLARE
    business_uuid UUID := 'a1b2c3d4-e5f6-7890-1234-567890abcdef';
    -- Electrical category IDs
    electrical_systems_cat_id UUID;
    lighting_cat_id UUID;
    electrical_install_cat_id UUID;
    electrical_maint_cat_id UUID;
    electrical_repair_cat_id UUID;
    -- Plumbing category IDs
    water_systems_cat_id UUID;
    drain_sewer_cat_id UUID;
    fixtures_appliances_cat_id UUID;
    plumbing_install_cat_id UUID;
    plumbing_maint_cat_id UUID;
    plumbing_repair_cat_id UUID;
    -- Cross-trade categories
    emergency_cat_id UUID;
    diagnostic_cat_id UUID;
    consultation_cat_id UUID;
BEGIN
    -- Get electrical category IDs
    SELECT id INTO electrical_systems_cat_id FROM service_categories WHERE slug = 'electrical-systems';
    SELECT id INTO lighting_cat_id FROM service_categories WHERE slug = 'lighting';
    SELECT id INTO electrical_install_cat_id FROM service_categories WHERE slug = 'electrical-installation';
    SELECT id INTO electrical_maint_cat_id FROM service_categories WHERE slug = 'electrical-maintenance';
    SELECT id INTO electrical_repair_cat_id FROM service_categories WHERE slug = 'electrical-repair';
    
    -- Get plumbing category IDs
    SELECT id INTO water_systems_cat_id FROM service_categories WHERE slug = 'water-systems';
    SELECT id INTO drain_sewer_cat_id FROM service_categories WHERE slug = 'drain-sewer';
    SELECT id INTO fixtures_appliances_cat_id FROM service_categories WHERE slug = 'fixtures-appliances';
    SELECT id INTO plumbing_install_cat_id FROM service_categories WHERE slug = 'plumbing-installation';
    SELECT id INTO plumbing_maint_cat_id FROM service_categories WHERE slug = 'plumbing-maintenance';
    SELECT id INTO plumbing_repair_cat_id FROM service_categories WHERE slug = 'plumbing-repair';
    
    -- Get cross-trade category IDs
    SELECT id INTO emergency_cat_id FROM service_categories WHERE slug = 'emergency-service';
    SELECT id INTO diagnostic_cat_id FROM service_categories WHERE slug = 'diagnostic';
    SELECT id INTO consultation_cat_id FROM service_categories WHERE slug = 'consultation';

    -- Update business to reflect multi-trade capabilities
    UPDATE businesses 
    SET 
        name = 'Austin Elite Home Services',
        description = 'Premier HVAC, electrical, and plumbing services for Austin homes and businesses. Specializing in energy-efficient installations, emergency repairs, and preventative maintenance across all home systems.',
        commercial_trades = ARRAY['HVAC', 'Electrical', 'Plumbing'],
        residential_trades = ARRAY['HVAC', 'Electrical', 'Plumbing']
    WHERE id = business_uuid;

    -- Insert Emergency Electrical Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, emergency_cat_id, '24/7 Emergency Electrical Service',
     'Urgent electrical repairs for power outages, electrical hazards, and safety issues. Licensed electricians available 24/7.',
     'quote_required', 135.00, 95.00, 2.0, true, true, true, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 4),
    
    (business_uuid, emergency_cat_id, '24/7 Emergency Plumbing',
     'Round-the-clock plumbing emergency service for leaks, clogs, burst pipes, and water damage prevention.',
     'hourly', 125.00, 85.00, 1.5, true, true, true, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 5);

    -- Insert Electrical System Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, electrical_systems_cat_id, 'Electrical Panel Upgrade',
     'Upgrade electrical panel to modern code standards. Increase capacity and improve safety.',
     'quote_required', 1800.00, 800.00, 8.0, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 100),
    
    (business_uuid, electrical_systems_cat_id, 'Whole House Rewiring',
     'Complete home electrical rewiring service. Bring your home up to current electrical codes.',
     'quote_required', 8500.00, 5000.00, 40.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 101),
    
    (business_uuid, electrical_systems_cat_id, 'Circuit Breaker Repair',
     'Repair or replace faulty circuit breakers. Restore safe electrical operation.',
     'quote_required', 189.00, 99.00, 1.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 102),
    
    (business_uuid, electrical_systems_cat_id, 'GFCI Outlet Installation',
     'Install GFCI outlets for bathroom and kitchen safety. Code-compliant installations.',
     'fixed', 129.00, 89.00, 1.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 103),
    
    (business_uuid, electrical_systems_cat_id, 'EV Charger Installation',
     'Electric vehicle charging station installation. Level 2 chargers for home use.',
     'quote_required', 899.00, 500.00, 4.0, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 104);

    -- Insert Lighting Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, lighting_cat_id, 'LED Lighting Upgrade',
     'Convert existing lighting to energy-efficient LED systems. Reduce energy costs significantly.',
     'per_unit', 45.00, 25.00, 0.5, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 110),
    
    (business_uuid, lighting_cat_id, 'Ceiling Fan Installation',
     'Install ceiling fans with proper electrical connections. Improve air circulation and comfort.',
     'fixed', 189.00, 129.00, 2.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 111),
    
    (business_uuid, lighting_cat_id, 'Outdoor Lighting Installation',
     'Landscape and security outdoor lighting installation. Enhance curb appeal and safety.',
     'quote_required', 599.00, 299.00, 6.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 112),
    
    (business_uuid, lighting_cat_id, 'Smart Home Lighting',
     'Smart lighting system installation and setup. Control lights with your phone or voice.',
     'quote_required', 899.00, 400.00, 4.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 113),
    
    (business_uuid, lighting_cat_id, 'Recessed Lighting Installation',
     'Professional recessed lighting installation. Modern, clean lighting solutions.',
     'per_unit', 89.00, 65.00, 1.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 114);

    -- Insert Electrical Installation Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, electrical_install_cat_id, 'New Outlet Installation',
     'Install new electrical outlets where you need them. Safe, code-compliant installations.',
     'fixed', 149.00, 99.00, 1.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 120),
    
    (business_uuid, electrical_install_cat_id, 'Generator Installation',
     'Whole house generator installation. Never lose power during outages.',
     'quote_required', 4500.00, 2500.00, 12.0, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 121),
    
    (business_uuid, electrical_install_cat_id, 'Security System Wiring',
     'Professional wiring for security systems, cameras, and alarms.',
     'quote_required', 599.00, 299.00, 4.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 122);

    -- Insert Electrical Repair Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, electrical_repair_cat_id, 'Electrical Troubleshooting',
     'Diagnose and repair electrical problems. Find the root cause of electrical issues.',
     'hourly', 95.00, 95.00, 1.5, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 130),
    
    (business_uuid, electrical_repair_cat_id, 'Outlet & Switch Repair',
     'Repair faulty outlets, switches, and electrical fixtures. Restore proper operation.',
     'fixed', 89.00, 59.00, 1.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 131);

    -- Insert Water System Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, water_systems_cat_id, 'Water Heater Installation',
     'New water heater installation with permits and warranty. Gas, electric, and tankless options.',
     'quote_required', 1200.00, 600.00, 4.0, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 200),
    
    (business_uuid, water_systems_cat_id, 'Water Heater Repair',
     'Water heater troubleshooting and repair services. Restore hot water quickly.',
     'quote_required', 159.00, 89.00, 2.0, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 201),
    
    (business_uuid, water_systems_cat_id, 'Tankless Water Heater Install',
     'Energy-efficient tankless water heater installation. Endless hot water on demand.',
     'quote_required', 2200.00, 1500.00, 6.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 202),
    
    (business_uuid, water_systems_cat_id, 'Water Pressure Repair',
     'Diagnose and repair water pressure issues. Restore proper water flow throughout your home.',
     'quote_required', 129.00, 79.00, 1.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 203),
    
    (business_uuid, water_systems_cat_id, 'Water Filtration System',
     'Whole house water filtration system installation. Clean, pure water throughout your home.',
     'quote_required', 899.00, 500.00, 4.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 204);

    -- Insert Drain & Sewer Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, drain_sewer_cat_id, 'Drain Cleaning',
     'Professional drain cleaning and unclogging service. Clear stubborn blockages safely.',
     'fixed', 149.00, 99.00, 1.5, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 210),
    
    (business_uuid, drain_sewer_cat_id, 'Main Sewer Line Repair',
     'Main sewer line inspection, cleaning, and repair. Prevent costly backups.',
     'quote_required', 899.00, 300.00, 4.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 211),
    
    (business_uuid, drain_sewer_cat_id, 'Hydro Jetting',
     'High-pressure water jetting for severe blockages. Clear even the toughest clogs.',
     'fixed', 299.00, 199.00, 2.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 212),
    
    (business_uuid, drain_sewer_cat_id, 'Sewer Camera Inspection',
     'Video camera inspection of sewer and drain lines. Identify problems before they worsen.',
     'fixed', 199.00, 149.00, 1.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 213);

    -- Insert Plumbing Fixtures Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, fixtures_appliances_cat_id, 'Toilet Installation',
     'New toilet installation with proper sealing and setup. High-efficiency models available.',
     'fixed', 299.00, 199.00, 2.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 220),
    
    (business_uuid, fixtures_appliances_cat_id, 'Faucet Installation',
     'Kitchen and bathroom faucet installation service. Modern, efficient fixtures.',
     'fixed', 159.00, 99.00, 1.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 221),
    
    (business_uuid, fixtures_appliances_cat_id, 'Shower Installation',
     'Complete shower installation including plumbing and fixtures. Custom shower solutions.',
     'quote_required', 899.00, 400.00, 8.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 222),
    
    (business_uuid, fixtures_appliances_cat_id, 'Garbage Disposal Install',
     'Kitchen garbage disposal installation and setup. Convenient food waste management.',
     'fixed', 249.00, 149.00, 2.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 223),
    
    (business_uuid, fixtures_appliances_cat_id, 'Bathtub Installation',
     'New bathtub installation and plumbing connections. Transform your bathroom.',
     'quote_required', 1299.00, 800.00, 8.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 224);

    -- Insert Plumbing Installation Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, plumbing_install_cat_id, 'New Construction Plumbing',
     'Complete plumbing installation for new construction and major renovations.',
     'quote_required', 3500.00, 2000.00, 20.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 230),
    
    (business_uuid, plumbing_install_cat_id, 'Bathroom Remodel Plumbing',
     'Complete plumbing for bathroom remodels. Move fixtures and add new connections.',
     'quote_required', 1899.00, 1000.00, 12.0, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 231),
    
    (business_uuid, plumbing_install_cat_id, 'Kitchen Remodel Plumbing',
     'Plumbing installation for kitchen remodels. Relocate sinks and add appliance connections.',
     'quote_required', 1299.00, 700.00, 8.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 232);

    -- Insert Plumbing Repair Services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, plumbing_repair_cat_id, 'Leak Repair',
     'Fast leak detection and repair service. Stop water damage before it spreads.',
     'quote_required', 149.00, 89.00, 1.5, true, true, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 240),
    
    (business_uuid, plumbing_repair_cat_id, 'Pipe Repair & Replacement',
     'Repair or replace damaged pipes. Restore proper water flow and prevent leaks.',
     'quote_required', 299.00, 150.00, 3.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 241),
    
    (business_uuid, plumbing_repair_cat_id, 'Toilet Repair',
     'Fix running toilets, clogs, and other toilet problems. Restore proper operation.',
     'fixed', 129.00, 79.00, 1.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 242),
    
    (business_uuid, plumbing_repair_cat_id, 'Faucet Repair',
     'Repair dripping faucets and restore proper water flow. Stop annoying leaks.',
     'fixed', 99.00, 69.00, 1.0, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 243);

    -- Add cross-trade diagnostic and consultation services
    INSERT INTO business_services (
        business_id, category_id, name, description, pricing_model, unit_price, minimum_price,
        estimated_duration_hours, is_active, is_featured, is_emergency, requires_booking,
        service_areas, sort_order
    ) VALUES 
    (business_uuid, diagnostic_cat_id, 'Electrical System Diagnostic',
     'Comprehensive electrical system troubleshooting and safety analysis.',
     'fixed', 99.00, 99.00, 1.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 52),
    
    (business_uuid, diagnostic_cat_id, 'Plumbing System Diagnostic',
     'Complete plumbing system inspection and problem identification.',
     'fixed', 99.00, 99.00, 1.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 53),
    
    (business_uuid, consultation_cat_id, 'Electrical Consultation',
     'Professional electrical consultation for upgrades, code compliance, and safety.',
     'hourly', 89.00, 89.00, 1.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 62),
    
    (business_uuid, consultation_cat_id, 'Plumbing Consultation',
     'Expert plumbing consultation for remodels, new construction, and system upgrades.',
     'hourly', 89.00, 89.00, 1.5, true, false, false, true,
     ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'], 63);

    RAISE NOTICE 'Successfully added electrical and plumbing services. Total services: %', 
        (SELECT COUNT(*) FROM business_services WHERE business_id = business_uuid);

END $$;

-- Create multi-trade service bundles
INSERT INTO business_service_bundles (
    business_id, name, description, service_ids, bundle_price, discount_percentage,
    is_active, is_featured, terms_and_conditions
) VALUES 
(
    'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    'Home Safety Inspection Package',
    'Complete home safety inspection including HVAC, electrical, and plumbing systems',
    (SELECT ARRAY_AGG(id) FROM business_services 
     WHERE business_id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef' 
     AND name IN ('HVAC System Diagnostic', 'Electrical System Diagnostic', 'Plumbing System Diagnostic')),
    249.00,
    20.0,
    true,
    true,
    'Comprehensive safety inspection with detailed report and recommendations.'
),
(
    'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    'New Home Complete Package',
    'Complete HVAC, electrical, and plumbing installation for new construction',
    (SELECT ARRAY_AGG(id) FROM business_services 
     WHERE business_id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef' 
     AND name IN ('Central Air Installation', 'Furnace Installation', 'Electrical Panel Upgrade', 'New Construction Plumbing')),
    14999.00,
    15.0,
    true,
    true,
    'Complete home systems installation with 5-year warranty on all equipment and labor.'
);

COMMIT;
