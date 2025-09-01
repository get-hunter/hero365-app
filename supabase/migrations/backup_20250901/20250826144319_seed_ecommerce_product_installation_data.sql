-- =============================================
-- SEED E-COMMERCE PRODUCT + INSTALLATION DATA
-- =============================================
-- Populate the system with realistic products and installation options
-- for HVAC, electrical, and plumbing equipment.

DO $$
DECLARE
    default_business_id UUID;
    hvac_category_id UUID;
    electrical_category_id UUID;
    plumbing_category_id UUID;
    
    -- Service IDs for installation
    hvac_install_service_id UUID;
    electrical_install_service_id UUID;
    plumbing_install_service_id UUID;
    
    -- Product IDs
    heat_pump_id UUID;
    furnace_id UUID;
    water_heater_40_id UUID;
    water_heater_50_id UUID;
    electrical_panel_id UUID;
    ev_charger_id UUID;
    
    -- Installation option IDs
    install_option_id UUID;
BEGIN
    -- Get the default business
    SELECT id INTO default_business_id FROM businesses 
    WHERE name = 'Austin Elite Home Services' LIMIT 1;
    
    IF default_business_id IS NULL THEN
        default_business_id := 'a1b2c3d4-e5f6-7890-1234-567890abcdef'::UUID;
    END IF;

    RAISE NOTICE 'Seeding e-commerce data for business: %', default_business_id;

    -- =============================================
    -- 1. CREATE PRODUCT CATEGORIES
    -- =============================================
    
    -- HVAC Equipment Category
    INSERT INTO product_categories (id, business_id, name, description, level, sort_order, is_active)
    VALUES (
        uuid_generate_v4(), default_business_id, 'HVAC Equipment', 
        'Heating, ventilation, and air conditioning equipment', 0, 1, true
    ) RETURNING id INTO hvac_category_id;
    
    -- Electrical Equipment Category
    INSERT INTO product_categories (id, business_id, name, description, level, sort_order, is_active)
    VALUES (
        uuid_generate_v4(), default_business_id, 'Electrical Equipment', 
        'Electrical panels, outlets, switches, and components', 0, 2, true
    ) RETURNING id INTO electrical_category_id;
    
    -- Plumbing Equipment Category
    INSERT INTO product_categories (id, business_id, name, description, level, sort_order, is_active)
    VALUES (
        uuid_generate_v4(), default_business_id, 'Plumbing Equipment', 
        'Water heaters, fixtures, and plumbing components', 0, 3, true
    ) RETURNING id INTO plumbing_category_id;

    -- =============================================
    -- 2. GET INSTALLATION SERVICE IDs
    -- =============================================
    
    -- Find HVAC installation services
    SELECT id INTO hvac_install_service_id FROM business_services 
    WHERE business_id = default_business_id 
    AND (LOWER(name) LIKE '%installation%' OR LOWER(name) LIKE '%install%')
    AND (LOWER(name) LIKE '%hvac%' OR LOWER(name) LIKE '%heat pump%')
    LIMIT 1;
    
    -- Find electrical installation services
    SELECT id INTO electrical_install_service_id FROM business_services 
    WHERE business_id = default_business_id 
    AND (LOWER(name) LIKE '%installation%' OR LOWER(name) LIKE '%install%')
    AND LOWER(name) LIKE '%electrical%'
    LIMIT 1;
    
    -- Find plumbing installation services  
    SELECT id INTO plumbing_install_service_id FROM business_services 
    WHERE business_id = default_business_id 
    AND (LOWER(name) LIKE '%installation%' OR LOWER(name) LIKE '%install%')
    AND (LOWER(name) LIKE '%water heater%' OR LOWER(name) LIKE '%plumbing%')
    LIMIT 1;

    -- If services don't exist, create basic ones
    IF hvac_install_service_id IS NULL THEN
        INSERT INTO business_services (business_id, name, description, pricing_model, unit_price, is_active, category_id)
        SELECT default_business_id, 'HVAC System Installation', 'Professional installation of HVAC equipment', 'fixed', 800.00, true, id
        FROM service_categories WHERE slug = 'hvac-services' LIMIT 1
        RETURNING id INTO hvac_install_service_id;
    END IF;

    -- =============================================
    -- 3. CREATE HVAC PRODUCTS
    -- =============================================
    
    -- Heat Pump System
    INSERT INTO products (
        id, business_id, category_id, sku, name, description, long_description,
        product_type, unit_price, cost_price, weight, 
        show_on_website, requires_professional_install, install_complexity,
        warranty_years, energy_efficiency_rating, installation_time_estimate,
        meta_title, meta_description, slug,
        featured_image_url, gallery_images, product_highlights, technical_specs,
        installation_requirements, is_active, is_featured
    ) VALUES (
        uuid_generate_v4(), default_business_id, hvac_category_id,
        'HP-3TON-SEER16', 'Carrier 3-Ton 16 SEER Heat Pump System',
        'Energy-efficient heat pump system perfect for homes up to 1,800 sq ft',
        'The Carrier 3-Ton 16 SEER Heat Pump provides year-round comfort with industry-leading energy efficiency. Features advanced scroll compressor technology, durable construction, and quiet operation. Includes both indoor air handler and outdoor condensing unit.',
        'product', 4500.00, 3200.00, 350.0,
        true, true, 'complex',
        10, '16 SEER', '4-8 hours',
        'Carrier 3-Ton Heat Pump - Professional Installation Available',
        'Energy-efficient 16 SEER heat pump system with professional installation. Perfect for homes up to 1,800 sq ft.',
        'carrier-3-ton-heat-pump-system',
        'https://example.com/images/heat-pump-main.jpg',
        '["https://example.com/images/heat-pump-1.jpg", "https://example.com/images/heat-pump-2.jpg"]',
        '["16 SEER Energy Rating", "10-Year Warranty", "Quiet Operation", "Advanced Scroll Compressor"]',
        '{"cooling_capacity": "36000 BTU", "heating_capacity": "36000 BTU", "refrigerant": "R-410A", "electrical": "240V"}',
        '{"electrical_service": "240V/60A circuit", "pad_requirements": "Level concrete pad", "clearances": "24 inches all sides"}',
        true, true
    ) RETURNING id INTO heat_pump_id;

    -- Gas Furnace  
    INSERT INTO products (
        id, business_id, category_id, sku, name, description, long_description,
        product_type, unit_price, cost_price, weight,
        show_on_website, requires_professional_install, install_complexity,
        warranty_years, energy_efficiency_rating, installation_time_estimate,
        meta_title, meta_description, slug,
        featured_image_url, product_highlights, technical_specs,
        installation_requirements, is_active
    ) VALUES (
        uuid_generate_v4(), default_business_id, hvac_category_id,
        'FURN-80K-95AFUE', 'Trane 80,000 BTU 95% AFUE Gas Furnace',
        'High-efficiency gas furnace with 95% AFUE rating for maximum comfort and savings',
        'The Trane XC95m gas furnace delivers outstanding efficiency and reliability. Features modulating gas valve, variable-speed ECM motor, and advanced heat exchanger technology for consistent temperatures and lower utility bills.',
        'product', 2800.00, 2000.00, 200.0,
        true, true, 'complex',
        15, '95% AFUE', '3-6 hours',
        'Trane 80K BTU Gas Furnace - 95% AFUE Efficiency',
        '95% AFUE high-efficiency gas furnace with professional installation. Modulating technology for optimal comfort.',
        'trane-80k-gas-furnace-95-afue',
        'https://example.com/images/furnace-main.jpg',
        '["95% AFUE Efficiency", "15-Year Warranty", "Variable Speed Motor", "Modulating Gas Valve"]',
        '{"input_btuh": "80000", "output_btuh": "76000", "gas_connection": "1/2 inch", "electrical": "115V"}',
        '{"gas_line": "1/2 inch natural gas", "electrical": "115V/15A circuit", "venting": "2-pipe direct vent", "clearances": "Front access required"}',
        true
    ) RETURNING id INTO furnace_id;

    -- =============================================
    -- 4. CREATE PLUMBING PRODUCTS
    -- =============================================
    
    -- 40 Gallon Water Heater
    INSERT INTO products (
        id, business_id, category_id, sku, name, description, long_description,
        product_type, unit_price, cost_price, weight,
        show_on_website, requires_professional_install, install_complexity,
        warranty_years, installation_time_estimate,
        meta_title, meta_description, slug,
        featured_image_url, product_highlights, technical_specs,
        installation_requirements, is_active, is_featured
    ) VALUES (
        uuid_generate_v4(), default_business_id, plumbing_category_id,
        'WH-40GAL-GAS', 'AO Smith 40 Gallon Gas Water Heater',
        'Reliable 40-gallon gas water heater perfect for families of 2-4 people',
        'The AO Smith GCG-40 gas water heater provides dependable hot water for medium-sized households. Features Dynaclean dip tube, Blue Diamond glass coating, and advanced gas valve technology for consistent performance and longevity.',
        'product', 850.00, 600.00, 120.0,
        true, true, 'standard',
        6, '2-3 hours',
        'AO Smith 40 Gallon Gas Water Heater - Professional Installation',
        '40-gallon gas water heater with 6-year warranty. Perfect for families. Professional installation included.',
        'ao-smith-40-gallon-gas-water-heater',
        'https://example.com/images/water-heater-40-main.jpg',
        '["40 Gallon Capacity", "6-Year Warranty", "Energy Efficient", "Blue Diamond Glass Coating"]',
        '{"capacity": "40 gallons", "fuel_type": "natural_gas", "input_btuh": "40000", "recovery_90f": "41 GPH"}',
        '{"gas_line": "1/2 inch natural gas", "water_connections": "3/4 inch NPT", "venting": "3 inch B-vent", "clearances": "6 inches sides, 18 inches front"}',
        true, true
    ) RETURNING id INTO water_heater_40_id;

    -- 50 Gallon Water Heater
    INSERT INTO products (
        id, business_id, category_id, sku, name, description, long_description,
        product_type, unit_price, cost_price, weight,
        show_on_website, requires_professional_install, install_complexity,
        warranty_years, installation_time_estimate,
        meta_title, meta_description, slug,
        featured_image_url, product_highlights, technical_specs,
        installation_requirements, is_active
    ) VALUES (
        uuid_generate_v4(), default_business_id, plumbing_category_id,
        'WH-50GAL-GAS', 'AO Smith 50 Gallon Gas Water Heater',
        'High-capacity 50-gallon gas water heater ideal for families of 4-6 people',
        'The AO Smith GCG-50 gas water heater delivers ample hot water for larger households. Features advanced combustion system, superior insulation, and durable construction for years of reliable service.',
        'product', 950.00, 680.00, 135.0,
        true, true, 'standard',
        6, '2-3 hours',
        'AO Smith 50 Gallon Gas Water Heater - Professional Installation',
        '50-gallon gas water heater with 6-year warranty. Ideal for larger families. Professional installation available.',
        'ao-smith-50-gallon-gas-water-heater',
        'https://example.com/images/water-heater-50-main.jpg',
        '["50 Gallon Capacity", "6-Year Warranty", "High Recovery Rate", "Advanced Combustion System"]',
        '{"capacity": "50 gallons", "fuel_type": "natural_gas", "input_btuh": "40000", "recovery_90f": "48 GPH"}',
        '{"gas_line": "1/2 inch natural gas", "water_connections": "3/4 inch NPT", "venting": "3 inch B-vent", "clearances": "6 inches sides, 18 inches front"}',
        true
    ) RETURNING id INTO water_heater_50_id;

    -- =============================================
    -- 5. CREATE ELECTRICAL PRODUCTS
    -- =============================================
    
    -- Electrical Panel
    INSERT INTO products (
        id, business_id, category_id, sku, name, description, long_description,
        product_type, unit_price, cost_price, weight,
        show_on_website, requires_professional_install, install_complexity,
        warranty_years, installation_time_estimate,
        meta_title, meta_description, slug,
        featured_image_url, product_highlights, technical_specs,
        installation_requirements, is_active, is_featured
    ) VALUES (
        uuid_generate_v4(), default_business_id, electrical_category_id,
        'PANEL-200A-40CKT', 'Square D 200 Amp Main Breaker Panel - 40 Circuit',
        'Professional-grade 200 amp electrical panel with 40 circuit capacity',
        'The Square D Homeline 200 amp main breaker panel provides reliable electrical distribution for modern homes. Features 40 circuit positions, ANSI certified construction, and easy installation design for professional electricians.',
        'product', 320.00, 220.00, 25.0,
        true, true, 'expert',
        10, '3-5 hours',
        'Square D 200 Amp Electrical Panel - Professional Installation Required',
        '200 amp main breaker panel with 40 circuits. Professional installation required. Perfect for home electrical upgrades.',
        'square-d-200-amp-electrical-panel',
        'https://example.com/images/electrical-panel-main.jpg',
        '["200 Amp Capacity", "40 Circuit Positions", "ANSI Certified", "Main Breaker Included"]',
        '{"amperage": "200A", "circuits": "40", "voltage": "120/240V", "type": "main_breaker"}',
        '{"permit_required": true, "electrical_service": "200A service entrance", "mounting": "flush or surface mount", "clearances": "36 inches front, 30 inches wide"}',
        true, true
    ) RETURNING id INTO electrical_panel_id;

    -- EV Charger
    INSERT INTO products (
        id, business_id, category_id, sku, name, description, long_description,
        product_type, unit_price, cost_price, weight,
        show_on_website, requires_professional_install, install_complexity,
        warranty_years, installation_time_estimate,
        meta_title, meta_description, slug,
        featured_image_url, product_highlights, technical_specs,
        installation_requirements, is_active, is_featured
    ) VALUES (
        uuid_generate_v4(), default_business_id, electrical_category_id,
        'EV-CHARGER-L2-40A', 'Tesla Wall Connector - Level 2 EV Charger',
        'High-speed Level 2 electric vehicle charger for home installation',
        'The Tesla Wall Connector delivers up to 44 miles of range per hour of charge. Features Wi-Fi connectivity, automatic software updates, and weather-resistant design for indoor or outdoor installation. Compatible with all electric vehicles.',
        'product', 475.00, 340.00, 12.0,
        true, true, 'complex',
        3, '2-4 hours',
        'Tesla Wall Connector EV Charger - Professional Installation Available',
        'Level 2 EV charger with Wi-Fi connectivity. Professional installation available. Compatible with all EVs.',
        'tesla-wall-connector-ev-charger',
        'https://example.com/images/ev-charger-main.jpg',
        '["Level 2 Charging", "Wi-Fi Connected", "Weather Resistant", "Universal Compatibility"]',
        '{"charging_speed": "up_to_44_miles_per_hour", "power": "11.5kW", "amperage": "up_to_40A", "voltage": "240V"}',
        '{"electrical": "240V/50A circuit", "mounting": "wall mount", "clearances": "18 inches all sides", "permit": "may be required"}',
        true, true
    ) RETURNING id INTO ev_charger_id;

    -- =============================================
    -- 6. CREATE INSTALLATION OPTIONS
    -- =============================================
    
    -- Heat Pump Installation Options
    SELECT add_product_installation_option(
        default_business_id, heat_pump_id, hvac_install_service_id,
        'Standard Heat Pump Installation', 1200.00, 6.0, true
    ) INTO install_option_id;
    
    UPDATE product_installation_options SET 
        description = 'Complete installation including electrical connections, refrigerant lines, and startup',
        residential_install_price = 1020.00, -- 15% discount
        commercial_install_price = 960.00,   -- 20% discount  
        premium_install_price = 900.00,      -- 25% discount
        requirements = '{"electrical_service": "240V/60A circuit", "refrigerant_certification": true, "permits": "mechanical permit required"}',
        included_in_install = '["Electrical connections", "Refrigerant lines", "Condensate drain", "System startup", "Performance testing"]'
    WHERE id = install_option_id;

    -- Add complex installation option for heat pump
    SELECT add_product_installation_option(
        default_business_id, heat_pump_id, hvac_install_service_id,
        'Complex Heat Pump Installation', 1800.00, 8.0, false
    ) INTO install_option_id;
    
    UPDATE product_installation_options SET 
        description = 'Installation with additional complexity (roof access, long line runs, electrical upgrades)',
        complexity_multiplier = 1.5,
        residential_install_price = 1530.00,
        commercial_install_price = 1440.00,
        premium_install_price = 1350.00,
        requirements = '{"electrical_upgrade": "may be required", "special_access": "roof or crawl space work", "extended_runs": "over 25 feet"}',
        included_in_install = '["All standard installation items", "Extended refrigerant runs", "Electrical upgrades", "Special access work"]'
    WHERE id = install_option_id;

    -- Water Heater Installation Options (40 gallon)
    SELECT add_product_installation_option(
        default_business_id, water_heater_40_id, plumbing_install_service_id,
        'Standard Water Heater Installation', 450.00, 2.5, true
    ) INTO install_option_id;
    
    UPDATE product_installation_options SET 
        description = 'Standard replacement installation with existing connections',
        residential_install_price = 383.00, -- 15% discount
        commercial_install_price = 360.00,   -- 20% discount
        premium_install_price = 338.00,      -- 25% discount
        requirements = '{"gas_line": "existing 1/2 inch line", "water_connections": "existing connections", "venting": "existing B-vent"}',
        included_in_install = '["Water heater removal", "New unit installation", "Gas and water connections", "Venting", "Testing"]'
    WHERE id = install_option_id;

    -- Water Heater Installation Options (50 gallon)
    SELECT add_product_installation_option(
        default_business_id, water_heater_50_id, plumbing_install_service_id,
        'Standard Water Heater Installation', 475.00, 2.5, true
    ) INTO install_option_id;
    
    UPDATE product_installation_options SET 
        description = 'Standard replacement installation with existing connections',
        residential_install_price = 404.00,
        commercial_install_price = 380.00,
        premium_install_price = 356.00,
        requirements = '{"gas_line": "existing 1/2 inch line", "water_connections": "existing connections", "venting": "existing B-vent"}',
        included_in_install = '["Water heater removal", "New unit installation", "Gas and water connections", "Venting", "Testing"]'
    WHERE id = install_option_id;

    -- Electrical Panel Installation
    SELECT add_product_installation_option(
        default_business_id, electrical_panel_id, electrical_install_service_id,
        'Electrical Panel Replacement', 800.00, 4.0, true
    ) INTO install_option_id;
    
    UPDATE product_installation_options SET 
        description = 'Complete panel replacement with existing service entrance',
        residential_install_price = 680.00,
        commercial_install_price = 640.00,
        premium_install_price = 600.00,
        requirements = '{"permit": "electrical permit required", "inspection": "electrical inspection required", "existing_service": "200A service entrance"}',
        included_in_install = '["Panel removal", "New panel installation", "Circuit relocation", "Testing and inspection"]'
    WHERE id = install_option_id;

    -- EV Charger Installation
    SELECT add_product_installation_option(
        default_business_id, ev_charger_id, electrical_install_service_id,
        'Standard EV Charger Installation', 350.00, 3.0, true
    ) INTO install_option_id;
    
    UPDATE product_installation_options SET 
        description = 'Installation with new 240V circuit up to 25 feet from panel',
        residential_install_price = 298.00,
        commercial_install_price = 280.00,
        premium_install_price = 263.00,
        requirements = '{"electrical_service": "available space in panel", "distance": "up to 25 feet from panel", "permit": "may be required"}',
        included_in_install = '["240V circuit installation", "Charger mounting", "Electrical connections", "Testing and setup"]'
    WHERE id = install_option_id;

    -- Add long-run installation option for EV charger
    SELECT add_product_installation_option(
        default_business_id, ev_charger_id, electrical_install_service_id,
        'Long-Run EV Charger Installation', 550.00, 4.0, false
    ) INTO install_option_id;
    
    UPDATE product_installation_options SET 
        description = 'Installation with new 240V circuit over 25 feet from panel',
        complexity_multiplier = 1.3,
        residential_install_price = 468.00,
        commercial_install_price = 440.00,
        premium_install_price = 413.00,
        requirements = '{"distance": "25-75 feet from panel", "conduit_run": "may require trenching or conduit", "permit": "electrical permit likely required"}',
        included_in_install = '["Extended 240V circuit", "Conduit installation", "Charger mounting", "Electrical connections", "Testing and setup"]'
    WHERE id = install_option_id;

    -- =============================================
    -- 7. CREATE SAMPLE CART FOR TESTING
    -- =============================================
    
    DECLARE
        sample_cart_id UUID;
        sample_item_id UUID;
    BEGIN
        -- Create a sample cart
        SELECT create_shopping_cart(default_business_id, 'demo-session-123', 'demo@example.com') 
        INTO sample_cart_id;
        
        -- Add heat pump with installation to cart
        INSERT INTO cart_items (
            cart_id, product_id, installation_option_id,
            product_name, product_sku, installation_name,
            quantity, unit_price, install_price, subtotal_price,
            membership_type, product_discount, install_discount, total_discount,
            final_price
        ) VALUES (
            sample_cart_id, heat_pump_id,
            (SELECT id FROM product_installation_options WHERE product_id = heat_pump_id AND is_default = true LIMIT 1),
            'Carrier 3-Ton 16 SEER Heat Pump System', 'HP-3TON-SEER16', 'Standard Heat Pump Installation',
            1, 4500.00, 1200.00, 5700.00,
            'residential', 675.00, 180.00, 855.00, -- 15% discounts
            4845.00
        );
        
        -- Add water heater with installation to cart
        INSERT INTO cart_items (
            cart_id, product_id, installation_option_id,
            product_name, product_sku, installation_name,
            quantity, unit_price, install_price, subtotal_price,
            membership_type, product_discount, install_discount, total_discount,
            final_price
        ) VALUES (
            sample_cart_id, water_heater_40_id,
            (SELECT id FROM product_installation_options WHERE product_id = water_heater_40_id AND is_default = true LIMIT 1),
            'AO Smith 40 Gallon Gas Water Heater', 'WH-40GAL-GAS', 'Standard Water Heater Installation',
            1, 850.00, 450.00, 1300.00,
            'residential', 127.50, 67.50, 195.00, -- 15% discounts
            1105.00
        );
        
        RAISE NOTICE 'Created sample cart % with 2 items', sample_cart_id;
    END;

    RAISE NOTICE '✅ E-commerce seed data completed successfully!';
    RAISE NOTICE '📦 Created % products with installation options', 6;
    RAISE NOTICE '🛒 Created sample shopping cart for testing';
    
END $$;
