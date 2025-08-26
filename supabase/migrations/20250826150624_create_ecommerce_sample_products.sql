-- Create sample e-commerce products for testing
-- These products will have show_on_website = true and all the e-commerce fields populated

DO $$
DECLARE
    default_business_id UUID := 'a1b2c3d4-e5f6-7890-1234-567890abcdef';
    heat_pump_id UUID;
    water_heater_id UUID;
    ev_charger_id UUID;
BEGIN
    RAISE NOTICE 'Creating sample e-commerce products...';

    -- Insert Heat Pump
    INSERT INTO products (
        id, business_id, sku, name, description, long_description,
        unit_price, cost_price,
        show_on_website, requires_professional_install, install_complexity,
        warranty_years, energy_efficiency_rating, installation_time_estimate,
        featured_image_url, product_highlights, technical_specs,
        installation_requirements,
        meta_title, meta_description, slug,
        is_active, is_featured, status
    ) VALUES (
        gen_random_uuid(), 
        default_business_id,
        'HP-3TON-SEER16', 
        'Carrier 3-Ton 16 SEER Heat Pump System',
        'Energy-efficient heat pump system perfect for homes up to 1,800 sq ft',
        'The Carrier 3-Ton 16 SEER Heat Pump provides year-round comfort with industry-leading energy efficiency. Features advanced scroll compressor technology, durable construction, and quiet operation. Includes both indoor air handler and outdoor condensing unit.',
        4500.00, 3200.00,
        true, true, 'complex',
        10, '16 SEER', '4-8 hours',
        'https://example.com/images/heat-pump-main.jpg',
        '["16 SEER Energy Rating", "10-Year Warranty", "Quiet Operation", "Advanced Scroll Compressor"]'::jsonb,
        '{"cooling_capacity": "36000 BTU", "heating_capacity": "36000 BTU", "refrigerant": "R-410A", "electrical": "240V"}'::jsonb,
        '{"electrical_service": "240V/60A circuit", "pad_requirements": "Level concrete pad", "clearances": "24 inches all sides"}'::jsonb,
        'Carrier 3-Ton Heat Pump - Professional Installation Available',
        'Energy-efficient 16 SEER heat pump system with professional installation. Perfect for homes up to 1,800 sq ft.',
        'carrier-3-ton-heat-pump-system',
        true, true, 'active'
    ) RETURNING id INTO heat_pump_id;

    -- Insert Water Heater
    INSERT INTO products (
        id, business_id, sku, name, description, long_description,
        unit_price, cost_price,
        show_on_website, requires_professional_install, install_complexity,
        warranty_years, installation_time_estimate,
        featured_image_url, product_highlights, technical_specs,
        installation_requirements,
        meta_title, meta_description, slug,
        is_active, is_featured, status
    ) VALUES (
        gen_random_uuid(), 
        default_business_id,
        'WH-40GAL-GAS', 
        'AO Smith 40 Gallon Gas Water Heater',
        'Reliable 40-gallon gas water heater perfect for families of 2-4 people',
        'The AO Smith GCG-40 gas water heater provides dependable hot water for medium-sized households. Features Dynaclean dip tube, Blue Diamond glass coating, and advanced gas valve technology for consistent performance and longevity.',
        850.00, 600.00,
        true, true, 'standard',
        6, '2-3 hours',
        'https://example.com/images/water-heater-40-main.jpg',
        '["40 Gallon Capacity", "6-Year Warranty", "Energy Efficient", "Blue Diamond Glass Coating"]'::jsonb,
        '{"capacity": "40 gallons", "fuel_type": "natural_gas", "input_btuh": "40000", "recovery_90f": "41 GPH"}'::jsonb,
        '{"gas_line": "1/2 inch natural gas", "water_connections": "3/4 inch NPT", "venting": "3 inch B-vent", "clearances": "6 inches sides, 18 inches front"}'::jsonb,
        'AO Smith 40 Gallon Gas Water Heater - Professional Installation',
        '40-gallon gas water heater with 6-year warranty. Perfect for families. Professional installation included.',
        'ao-smith-40-gallon-gas-water-heater',
        true, true, 'active'
    ) RETURNING id INTO water_heater_id;

    -- Insert EV Charger  
    INSERT INTO products (
        id, business_id, sku, name, description, long_description,
        unit_price, cost_price,
        show_on_website, requires_professional_install, install_complexity,
        warranty_years, installation_time_estimate,
        featured_image_url, product_highlights, technical_specs,
        installation_requirements,
        meta_title, meta_description, slug,
        is_active, is_featured, status
    ) VALUES (
        gen_random_uuid(), 
        default_business_id,
        'EV-CHARGER-L2-40A', 
        'Tesla Wall Connector - Level 2 EV Charger',
        'High-speed Level 2 electric vehicle charger for home installation',
        'The Tesla Wall Connector delivers up to 44 miles of range per hour of charge. Features Wi-Fi connectivity, automatic software updates, and weather-resistant design for indoor or outdoor installation. Compatible with all electric vehicles.',
        475.00, 340.00,
        true, true, 'complex',
        3, '2-4 hours',
        'https://example.com/images/ev-charger-main.jpg',
        '["Level 2 Charging", "Wi-Fi Connected", "Weather Resistant", "Universal Compatibility"]'::jsonb,
        '{"charging_speed": "up_to_44_miles_per_hour", "power": "11.5kW", "amperage": "up_to_40A", "voltage": "240V"}'::jsonb,
        '{"electrical": "240V/50A circuit", "mounting": "wall mount", "clearances": "18 inches all sides", "permit": "may be required"}'::jsonb,
        'Tesla Wall Connector EV Charger - Professional Installation Available',
        'Level 2 EV charger with Wi-Fi connectivity. Professional installation available. Compatible with all EVs.',
        'tesla-wall-connector-ev-charger',
        true, true, 'active'
    ) RETURNING id INTO ev_charger_id;

    RAISE NOTICE '✅ Created 3 e-commerce products successfully!';
    RAISE NOTICE '   Heat Pump ID: %', heat_pump_id;
    RAISE NOTICE '   Water Heater ID: %', water_heater_id;
    RAISE NOTICE '   EV Charger ID: %', ev_charger_id;

END $$;
