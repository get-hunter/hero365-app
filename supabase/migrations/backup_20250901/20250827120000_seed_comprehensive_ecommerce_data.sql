-- =============================================
-- COMPREHENSIVE E-COMMERCE SAMPLE DATA
-- =============================================
-- This migration adds realistic product catalog with installation options
-- to showcase the complete e-commerce system functionality.

DO $$
DECLARE
    business_uuid UUID;
    hvac_category_id UUID;
    electrical_category_id UUID;
    plumbing_category_id UUID;
    
    -- Products
    hvac_unit_id UUID;
    water_heater_id UUID;
    electrical_panel_id UUID;
    smart_thermostat_id UUID;
    air_purifier_id UUID;
    
    -- Services
    hvac_install_service_id UUID;
    electrical_install_service_id UUID;
    plumbing_install_service_id UUID;
    maintenance_service_id UUID;
BEGIN
    -- Get the business ID (assuming we have Austin Elite Home Services)
    SELECT id INTO business_uuid 
    FROM businesses 
    WHERE name ILIKE '%Austin Elite%' OR name ILIKE '%Elite%'
    LIMIT 1;
    
    IF business_uuid IS NULL THEN
        RAISE EXCEPTION 'Business not found. Please ensure a business exists first.';
    END IF;
    
    RAISE NOTICE 'Adding e-commerce data for business: %', business_uuid;
    
    -- =============================================
    -- 1. PRODUCT CATEGORIES
    -- =============================================
    
    -- HVAC Category
    INSERT INTO product_categories (id, business_id, name, description, slug, is_active, sort_order)
    VALUES (
        uuid_generate_v4(), business_uuid, 'HVAC Systems', 
        'Complete heating, ventilation, and air conditioning systems', 
        'hvac-systems', true, 1
    ) RETURNING id INTO hvac_category_id;
    
    -- Electrical Category  
    INSERT INTO product_categories (id, business_id, name, description, slug, is_active, sort_order)
    VALUES (
        uuid_generate_v4(), business_uuid, 'Electrical Equipment', 
        'Professional electrical panels, outlets, and smart home devices', 
        'electrical-equipment', true, 2
    ) RETURNING id INTO electrical_category_id;
    
    -- Plumbing Category
    INSERT INTO product_categories (id, business_id, name, description, slug, is_active, sort_order)
    VALUES (
        uuid_generate_v4(), business_uuid, 'Plumbing Systems', 
        'Water heaters, fixtures, and plumbing equipment', 
        'plumbing-systems', true, 3
    ) RETURNING id INTO plumbing_category_id;
    
    -- =============================================
    -- 2. BUSINESS SERVICES (for installation options)
    -- =============================================
    
    -- HVAC Installation Service
    INSERT INTO business_services (id, business_id, category_id, name, description, pricing_model, unit_price, estimated_duration_hours, is_active)
    SELECT uuid_generate_v4(), business_uuid, sc.id, 'HVAC System Installation', 
           'Complete installation of HVAC systems including ductwork, electrical connections, and commissioning',
           'fixed', 1200.00, 8.0, true
    FROM service_categories sc WHERE sc.name ILIKE '%HVAC%' LIMIT 1
    RETURNING id INTO hvac_install_service_id;
    
    -- Electrical Installation Service
    INSERT INTO business_services (id, business_id, category_id, name, description, pricing_model, unit_price, estimated_duration_hours, is_active)
    SELECT uuid_generate_v4(), business_uuid, sc.id, 'Electrical Installation', 
           'Professional electrical installation including permits, wiring, and code compliance',
           'fixed', 800.00, 4.0, true
    FROM service_categories sc WHERE sc.name ILIKE '%Electric%' LIMIT 1
    RETURNING id INTO electrical_install_service_id;
    
    -- Plumbing Installation Service
    INSERT INTO business_services (id, business_id, category_id, name, description, pricing_model, unit_price, estimated_duration_hours, is_active)
    SELECT uuid_generate_v4(), business_uuid, sc.id, 'Plumbing Installation', 
           'Complete plumbing installation including connections, testing, and permits',
           'fixed', 600.00, 3.0, true
    FROM service_categories sc WHERE sc.name ILIKE '%Plumb%' LIMIT 1
    RETURNING id INTO plumbing_install_service_id;
    
    -- Maintenance Service
    INSERT INTO business_services (id, business_id, category_id, name, description, pricing_model, unit_price, estimated_duration_hours, is_active)
    SELECT uuid_generate_v4(), business_uuid, sc.id, 'Equipment Maintenance', 
           'Annual maintenance and tune-up service for installed equipment',
           'fixed', 150.00, 1.5, true
    FROM service_categories sc WHERE sc.name ILIKE '%Maintenance%' OR sc.name ILIKE '%Service%' LIMIT 1
    RETURNING id INTO maintenance_service_id;
    
    -- =============================================
    -- 3. PRODUCTS WITH E-COMMERCE FEATURES
    -- =============================================
    
    -- High-End HVAC Unit
    INSERT INTO products (
        id, business_id, category_id, sku, name, description, long_description,
        product_type, status, pricing_model, unit_price, cost_price,
        unit_of_measure, weight, dimensions, track_inventory, current_stock,
        available_stock, is_active, is_featured, 
        -- E-commerce specific fields
        show_on_website, requires_professional_install, install_complexity,
        meta_title, meta_description, slug, has_variations, variation_options,
        shipping_weight, shipping_dimensions, requires_freight,
        installation_time_estimate, warranty_years, energy_efficiency_rating,
        featured_image_url, gallery_images, product_highlights, technical_specs,
        installation_requirements
    ) VALUES (
        uuid_generate_v4(), business_uuid, hvac_category_id, 
        'HVAC-TRANE-XR16', 'Trane XR16 Heat Pump System', 
        'High-efficiency 16 SEER heat pump system with advanced comfort features',
        'The Trane XR16 heat pump delivers reliable, efficient heating and cooling with 16 SEER efficiency rating. Features include WeatherGuard™ top, spine fin™ outdoor coil, and Climatuff™ compressor for enhanced durability and performance. Perfect for residential applications up to 2,500 sq ft.',
        'product', 'active', 'fixed', 4299.00, 2800.00,
        'each', 185.5, '{"length": 36, "width": 36, "height": 36, "unit": "inches"}',
        true, 5, 5, true, true,
        -- E-commerce fields
        true, true, 'complex',
        'Trane XR16 Heat Pump - 16 SEER High Efficiency System | Austin Elite',
        'Professional-grade Trane XR16 heat pump with expert installation. 16 SEER efficiency, 10-year warranty, financing available.',
        'trane-xr16-heat-pump-system', true, 
        '{"sizes": ["2 Ton", "2.5 Ton", "3 Ton", "3.5 Ton", "4 Ton"], "efficiency": ["16 SEER"], "fuel_type": ["Electric"]}',
        185.5, '{"length": 36, "width": 36, "height": 36, "unit": "inches", "weight": 185.5}',
        true, '6-8 hours', 10, '16 SEER',
        'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800',
        '["https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800", "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800"]',
        '["16 SEER High Efficiency", "10-Year Parts Warranty", "WeatherGuard™ Top", "Spine Fin™ Coil", "Professional Installation Included"]',
        '{"seer_rating": "16", "btu_capacity": "24000-48000", "refrigerant": "R-410A", "compressor": "Scroll", "warranty_parts": "10 years", "warranty_labor": "1 year"}',
        '{"electrical": "240V dedicated circuit", "pad": "Concrete pad required", "clearances": "24 inches all sides", "permits": "Required in most areas"}'
    ) RETURNING id INTO hvac_unit_id;
    
    -- Tankless Water Heater
    INSERT INTO products (
        id, business_id, category_id, sku, name, description, long_description,
        product_type, status, pricing_model, unit_price, cost_price,
        unit_of_measure, weight, dimensions, track_inventory, current_stock,
        available_stock, is_active, is_featured,
        show_on_website, requires_professional_install, install_complexity,
        meta_title, meta_description, slug, has_variations, variation_options,
        shipping_weight, shipping_dimensions, requires_freight,
        installation_time_estimate, warranty_years, energy_efficiency_rating,
        featured_image_url, gallery_images, product_highlights, technical_specs,
        installation_requirements
    ) VALUES (
        uuid_generate_v4(), business_uuid, plumbing_category_id,
        'WH-RHEEM-RTG95', 'Rheem RTG-95 Tankless Water Heater',
        'High-efficiency condensing tankless water heater with 9.5 GPM flow rate',
        'The Rheem RTG-95 delivers endless hot water with 95% efficiency rating. Features include built-in recirculation pump, Wi-Fi connectivity, and compact wall-mount design. Ideal for homes with 2-3 bathrooms and high hot water demand.',
        'product', 'active', 'fixed', 1899.00, 1200.00,
        'each', 67.0, '{"length": 18.5, "width": 9.8, "height": 27.5, "unit": "inches"}',
        true, 8, 8, true, true,
        true, true, 'standard',
        'Rheem RTG-95 Tankless Water Heater - 9.5 GPM High Efficiency | Austin Elite',
        'Professional Rheem tankless water heater installation. 95% efficiency, endless hot water, Wi-Fi enabled, 12-year warranty.',
        'rheem-rtg95-tankless-water-heater', true,
        '{"flow_rates": ["7.5 GPM", "9.5 GPM", "11.0 GPM"], "fuel_type": ["Natural Gas", "Propane"], "venting": ["Concentric", "Separate"]}',
        67.0, '{"length": 18.5, "width": 9.8, "height": 27.5, "unit": "inches", "weight": 67}',
        false, '3-4 hours', 12, '95% AFUE',
        'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800',
        '["https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800", "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800"]',
        '["95% Efficiency Rating", "9.5 GPM Flow Rate", "Wi-Fi Connectivity", "Built-in Recirculation", "12-Year Warranty", "Endless Hot Water"]',
        '{"efficiency": "95% AFUE", "flow_rate": "9.5 GPM", "input_btu": "199000", "fuel_type": "Natural Gas/Propane", "venting": "Category IV", "warranty": "12 years heat exchanger"}',
        '{"gas_line": "3/4 inch gas line", "venting": "Category IV venting required", "electrical": "120V outlet", "water_lines": "3/4 inch connections", "permits": "Required"}'
    ) RETURNING id INTO water_heater_id;
    
    -- Electrical Panel
    INSERT INTO products (
        id, business_id, category_id, sku, name, description, long_description,
        product_type, status, pricing_model, unit_price, cost_price,
        unit_of_measure, weight, dimensions, track_inventory, current_stock,
        available_stock, is_active, is_featured,
        show_on_website, requires_professional_install, install_complexity,
        meta_title, meta_description, slug, has_variations, variation_options,
        shipping_weight, shipping_dimensions, requires_freight,
        installation_time_estimate, warranty_years, energy_efficiency_rating,
        featured_image_url, gallery_images, product_highlights, technical_specs,
        installation_requirements
    ) VALUES (
        uuid_generate_v4(), business_uuid, electrical_category_id,
        'ELEC-SQ-QO200', 'Square D QO 200A Main Panel',
        'Professional-grade 200-amp main electrical panel with 40 circuit capacity',
        'Square D QO series 200-amp main breaker panel provides reliable electrical distribution for modern homes. Features include QO plug-on neutral design, copper bus bars, and NEMA 3R outdoor rating. Includes main breaker and mounting hardware.',
        'product', 'active', 'fixed', 899.00, 550.00,
        'each', 45.0, '{"length": 20, "width": 14, "height": 6, "unit": "inches"}',
        true, 3, 3, true, true,
        true, true, 'expert',
        'Square D QO 200A Electrical Panel - Professional Installation | Austin Elite',
        'Professional Square D electrical panel installation. 200-amp capacity, 40 circuits, NEMA 3R rated, licensed electrician installation.',
        'square-d-qo-200a-main-panel', true,
        '{"amperage": ["100A", "150A", "200A"], "circuits": ["20", "30", "40"], "mounting": ["Surface", "Flush"]}',
        45.0, '{"length": 20, "width": 14, "height": 6, "unit": "inches", "weight": 45}',
        false, '4-6 hours', 25, 'N/A',
        'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=800',
        '["https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=800", "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800"]',
        '["200-Amp Capacity", "40 Circuit Spaces", "QO Plug-On Neutral", "NEMA 3R Outdoor Rated", "25-Year Warranty", "Copper Bus Bars"]',
        '{"amperage": "200A", "voltage": "120/240V", "phases": "Single", "circuits": "40", "bus_material": "Copper", "rating": "NEMA 3R", "warranty": "25 years"}',
        '{"permits": "Required - electrical permit", "inspection": "Required", "main_disconnect": "Utility coordination required", "grounding": "Proper grounding system required", "clearances": "36 inches working space"}'
    ) RETURNING id INTO electrical_panel_id;
    
    -- Smart Thermostat
    INSERT INTO products (
        id, business_id, category_id, sku, name, description, long_description,
        product_type, status, pricing_model, unit_price, cost_price,
        unit_of_measure, weight, dimensions, track_inventory, current_stock,
        available_stock, is_active, is_featured,
        show_on_website, requires_professional_install, install_complexity,
        meta_title, meta_description, slug, has_variations, variation_options,
        shipping_weight, shipping_dimensions, requires_freight,
        installation_time_estimate, warranty_years, energy_efficiency_rating,
        featured_image_url, gallery_images, product_highlights, technical_specs,
        installation_requirements
    ) VALUES (
        uuid_generate_v4(), business_uuid, hvac_category_id,
        'HVAC-NEST-LEARN', 'Nest Learning Thermostat',
        'Smart Wi-Fi thermostat with learning capabilities and energy savings',
        'The Nest Learning Thermostat learns your schedule and preferences to automatically adjust temperature for comfort and energy savings. Features include remote control via smartphone, energy history reports, and compatibility with most HVAC systems.',
        'product', 'active', 'fixed', 249.00, 180.00,
        'each', 1.2, '{"length": 3.3, "width": 3.3, "height": 1.2, "unit": "inches"}',
        true, 15, 15, true, true,
        true, true, 'standard',
        'Nest Learning Thermostat - Smart Wi-Fi Installation | Austin Elite',
        'Professional Nest thermostat installation. Smart learning, Wi-Fi enabled, energy savings, smartphone control, 2-year warranty.',
        'nest-learning-thermostat', true,
        '{"generation": ["3rd Gen", "4th Gen"], "color": ["Stainless Steel", "White", "Black", "Copper"], "compatibility": ["Most Systems", "Heat Pump", "Dual Fuel"]}',
        1.2, '{"length": 3.3, "width": 3.3, "height": 1.2, "unit": "inches", "weight": 1.2}',
        false, '1-2 hours', 2, 'Energy Star',
        'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800',
        '["https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800", "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800"]',
        '["Auto-Schedule Learning", "Remote Control", "Energy History", "Works with Alexa/Google", "Easy Installation", "2-Year Warranty"]',
        '{"connectivity": "Wi-Fi 802.11n", "display": "2.08 inch color LCD", "sensors": "Temperature, humidity, proximity, ambient light", "compatibility": "95% of systems", "power": "Built-in rechargeable battery"}',
        '{"wiring": "C-wire recommended", "compatibility": "Check system compatibility", "wifi": "2.4GHz Wi-Fi network required", "app": "Nest app setup required"}'
    ) RETURNING id INTO smart_thermostat_id;
    
    -- Air Purifier
    INSERT INTO products (
        id, business_id, category_id, sku, name, description, long_description,
        product_type, status, pricing_model, unit_price, cost_price,
        unit_of_measure, weight, dimensions, track_inventory, current_stock,
        available_stock, is_active, is_featured,
        show_on_website, requires_professional_install, install_complexity,
        meta_title, meta_description, slug, has_variations, variation_options,
        shipping_weight, shipping_dimensions, requires_freight,
        installation_time_estimate, warranty_years, energy_efficiency_rating,
        featured_image_url, gallery_images, product_highlights, technical_specs,
        installation_requirements
    ) VALUES (
        uuid_generate_v4(), business_uuid, hvac_category_id,
        'HVAC-APRILAIRE-5000', 'Aprilaire 5000 Whole-House Air Purifier',
        'Electronic air cleaner with 94% efficiency rating for whole-house installation',
        'The Aprilaire Model 5000 electronic air cleaner removes up to 94% of airborne particles including dust, pollen, pet dander, and smoke. Features washable aluminum pre-filters and electronic cells for long-lasting performance.',
        'product', 'active', 'fixed', 1299.00, 850.00,
        'each', 35.0, '{"length": 25, "width": 20, "height": 6, "unit": "inches"}',
        true, 6, 6, true, false,
        true, true, 'standard',
        'Aprilaire 5000 Electronic Air Cleaner - Whole House Installation | Austin Elite',
        'Professional whole-house air purifier installation. 94% efficiency, washable filters, electronic air cleaning, 5-year warranty.',
        'aprilaire-5000-electronic-air-cleaner', false, '{}',
        35.0, '{"length": 25, "width": 20, "height": 6, "unit": "inches", "weight": 35}',
        false, '2-3 hours', 5, 'Energy Star',
        'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800',
        '["https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800", "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800"]',
        '["94% Particle Removal", "Washable Filters", "Electronic Cleaning", "Whole-House Coverage", "5-Year Warranty", "Energy Efficient"]',
        '{"efficiency": "94% at 1 micron", "airflow": "Up to 2000 CFM", "power": "120V, 60Hz", "filter_type": "Electronic cells + aluminum pre-filter", "coverage": "Whole house", "warranty": "5 years"}',
        '{"ductwork": "Integration with existing HVAC ductwork", "electrical": "120V electrical connection", "space": "6 inches clearance required", "maintenance": "Quarterly filter cleaning"}'
    ) RETURNING id INTO air_purifier_id;
    
    -- =============================================
    -- 4. PRODUCT INSTALLATION OPTIONS
    -- =============================================
    
    -- HVAC Unit Installation Options
    INSERT INTO product_installation_options (
        business_id, product_id, service_id, option_name, description,
        base_install_price, complexity_multiplier, estimated_duration_hours,
        residential_install_price, commercial_install_price, premium_install_price,
        requirements, included_in_install, is_default, sort_order
    ) VALUES 
    (business_uuid, hvac_unit_id, hvac_install_service_id, 'Standard Installation', 
     'Complete installation including ductwork connections, electrical, refrigerant lines, and commissioning',
     1200.00, 1.0, 8.0, 1080.00, 1320.00, 960.00,
     '{"permits": true, "electrical": "240V circuit", "pad": "Concrete pad", "clearances": "24 inches"}',
     '["Equipment placement", "Refrigerant lines", "Electrical connections", "Ductwork connections", "System commissioning", "1-year labor warranty"]',
     true, 1),
    (business_uuid, hvac_unit_id, hvac_install_service_id, 'Complex Installation',
     'Installation requiring additional ductwork modifications, electrical upgrades, or difficult access',
     1200.00, 1.5, 12.0, 1620.00, 1980.00, 1440.00,
     '{"permits": true, "electrical": "Electrical panel upgrade may be required", "ductwork": "Ductwork modifications", "access": "Difficult access considerations"}',
     '["All standard installation items", "Ductwork modifications", "Electrical upgrades if needed", "Crane/special equipment if required", "Extended commissioning", "1-year labor warranty"]',
     false, 2);
    
    -- Water Heater Installation Options
    INSERT INTO product_installation_options (
        business_id, product_id, service_id, option_name, description,
        base_install_price, complexity_multiplier, estimated_duration_hours,
        residential_install_price, commercial_install_price, premium_install_price,
        requirements, included_in_install, is_default, sort_order
    ) VALUES 
    (business_uuid, water_heater_id, plumbing_install_service_id, 'Standard Installation',
     'Complete tankless water heater installation including gas line, venting, and water connections',
     600.00, 1.0, 4.0, 540.00, 660.00, 480.00,
     '{"gas_line": "3/4 inch gas line", "venting": "Category IV venting", "electrical": "120V outlet", "permits": true}',
     '["Unit mounting", "Gas line connections", "Water line connections", "Venting installation", "Electrical connections", "System testing", "1-year labor warranty"]',
     true, 1),
    (business_uuid, water_heater_id, plumbing_install_service_id, 'Complex Installation',
     'Installation requiring gas line upgrades, extensive venting, or structural modifications',
     600.00, 1.8, 6.0, 972.00, 1188.00, 864.00,
     '{"gas_line": "Gas line upgrade required", "venting": "Extended venting run", "structural": "Wall modifications may be required"}',
     '["All standard installation items", "Gas line upgrades", "Extended venting", "Wall modifications", "Structural reinforcement if needed", "Extended testing", "1-year labor warranty"]',
     false, 2);
    
    -- Electrical Panel Installation Options
    INSERT INTO product_installation_options (
        business_id, product_id, service_id, option_name, description,
        base_install_price, complexity_multiplier, estimated_duration_hours,
        residential_install_price, commercial_install_price, premium_install_price,
        requirements, included_in_install, is_default, sort_order
    ) VALUES 
    (business_uuid, electrical_panel_id, electrical_install_service_id, 'Standard Panel Upgrade',
     'Complete electrical panel replacement including permits, inspection, and utility coordination',
     800.00, 1.0, 6.0, 720.00, 880.00, 640.00,
     '{"permits": true, "inspection": true, "utility": "Utility coordination required", "clearances": "36 inch working space"}',
     '["Panel removal and installation", "Circuit transfer", "Grounding system", "Permits and inspections", "Utility coordination", "Code compliance", "1-year labor warranty"]',
     true, 1),
    (business_uuid, electrical_panel_id, electrical_install_service_id, 'Complex Panel Upgrade',
     'Panel upgrade requiring service entrance modifications, extensive rewiring, or code updates',
     800.00, 2.0, 10.0, 1440.00, 1760.00, 1280.00,
     '{"service_entrance": "Service entrance modifications", "rewiring": "Extensive circuit rewiring", "code_updates": "Bring entire system to current code"}',
     '["All standard installation items", "Service entrance modifications", "Extensive rewiring", "Code compliance updates", "Multiple inspections", "Extended warranty", "1-year labor warranty"]',
     false, 2);
    
    -- Smart Thermostat Installation Options
    INSERT INTO product_installation_options (
        business_id, product_id, service_id, option_name, description,
        base_install_price, complexity_multiplier, estimated_duration_hours,
        residential_install_price, commercial_install_price, premium_install_price,
        requirements, included_in_install, is_default, sort_order
    ) VALUES 
    (business_uuid, smart_thermostat_id, electrical_install_service_id, 'Standard Installation',
     'Professional thermostat installation including wiring, setup, and app configuration',
     150.00, 1.0, 1.5, 135.00, 165.00, 120.00,
     '{"wiring": "C-wire recommended", "wifi": "Wi-Fi network required", "compatibility": "System compatibility verified"}',
     '["Thermostat mounting", "Wiring connections", "System testing", "App setup", "User training", "1-year labor warranty"]',
     true, 1),
    (business_uuid, smart_thermostat_id, electrical_install_service_id, 'Complex Installation',
     'Installation requiring C-wire installation, system modifications, or compatibility updates',
     150.00, 2.0, 3.0, 270.00, 330.00, 240.00,
     '{"c_wire": "C-wire installation required", "system_mods": "HVAC system modifications", "compatibility": "System compatibility upgrades"}',
     '["All standard installation items", "C-wire installation", "System modifications", "Compatibility updates", "Extended testing", "Advanced setup", "1-year labor warranty"]',
     false, 2);
    
    -- Air Purifier Installation Options
    INSERT INTO product_installation_options (
        business_id, product_id, service_id, option_name, description,
        base_install_price, complexity_multiplier, estimated_duration_hours,
        residential_install_price, commercial_install_price, premium_install_price,
        requirements, included_in_install, is_default, sort_order
    ) VALUES 
    (business_uuid, air_purifier_id, hvac_install_service_id, 'Standard Installation',
     'Integration with existing HVAC system including ductwork modifications and electrical connections',
     400.00, 1.0, 3.0, 360.00, 440.00, 320.00,
     '{"ductwork": "Integration with existing ducts", "electrical": "120V electrical connection", "space": "6 inches clearance"}',
     '["Unit mounting", "Ductwork integration", "Electrical connections", "System testing", "Filter setup", "User training", "1-year labor warranty"]',
     true, 1);
    
    -- =============================================
    -- 5. PRODUCT VARIANTS (for products with options)
    -- =============================================
    
    -- HVAC Unit Variants (different sizes)
    INSERT INTO product_variants (product_id, variant_name, sku_suffix, price_adjustment, cost_adjustment, stock_quantity, available_stock, variant_attributes, is_default, sort_order)
    VALUES 
    (hvac_unit_id, '2 Ton', '-2TON', 0.00, 0.00, 2, 2, '{"capacity": "24000", "tonnage": "2", "size": "2 Ton"}', false, 1),
    (hvac_unit_id, '2.5 Ton', '-25TON', 400.00, 250.00, 2, 2, '{"capacity": "30000", "tonnage": "2.5", "size": "2.5 Ton"}', false, 2),
    (hvac_unit_id, '3 Ton', '-3TON', 800.00, 500.00, 1, 1, '{"capacity": "36000", "tonnage": "3", "size": "3 Ton"}', true, 3),
    (hvac_unit_id, '3.5 Ton', '-35TON', 1200.00, 750.00, 1, 1, '{"capacity": "42000", "tonnage": "3.5", "size": "3.5 Ton"}', false, 4),
    (hvac_unit_id, '4 Ton', '-4TON', 1600.00, 1000.00, 1, 1, '{"capacity": "48000", "tonnage": "4", "size": "4 Ton"}', false, 5);
    
    -- Water Heater Variants (different flow rates)
    INSERT INTO product_variants (product_id, variant_name, sku_suffix, price_adjustment, cost_adjustment, stock_quantity, available_stock, variant_attributes, is_default, sort_order)
    VALUES 
    (water_heater_id, '7.5 GPM', '-75GPM', -300.00, -200.00, 3, 3, '{"flow_rate": "7.5", "model": "RTG-75", "capacity": "7.5 GPM"}', false, 1),
    (water_heater_id, '9.5 GPM', '-95GPM', 0.00, 0.00, 5, 5, '{"flow_rate": "9.5", "model": "RTG-95", "capacity": "9.5 GPM"}', true, 2),
    (water_heater_id, '11.0 GPM', '-110GPM', 400.00, 250.00, 2, 2, '{"flow_rate": "11.0", "model": "RTG-110", "capacity": "11.0 GPM"}', false, 3);
    
    -- Smart Thermostat Variants (different colors)
    INSERT INTO product_variants (product_id, variant_name, sku_suffix, price_adjustment, cost_adjustment, stock_quantity, available_stock, variant_attributes, is_default, sort_order)
    VALUES 
    (smart_thermostat_id, 'Stainless Steel', '-SS', 0.00, 0.00, 8, 8, '{"color": "stainless_steel", "finish": "Stainless Steel"}', true, 1),
    (smart_thermostat_id, 'White', '-WH', 0.00, 0.00, 4, 4, '{"color": "white", "finish": "White"}', false, 2),
    (smart_thermostat_id, 'Black', '-BK', 0.00, 0.00, 2, 2, '{"color": "black", "finish": "Black"}', false, 3),
    (smart_thermostat_id, 'Copper', '-CP', 50.00, 30.00, 1, 1, '{"color": "copper", "finish": "Copper"}', false, 4);
    
    RAISE NOTICE 'Successfully added comprehensive e-commerce sample data';
    RAISE NOTICE 'Products added: 5 (HVAC Unit, Water Heater, Electrical Panel, Smart Thermostat, Air Purifier)';
    RAISE NOTICE 'Installation options added: 8 options across all products';
    RAISE NOTICE 'Product variants added: 12 variants for customizable products';
    
END $$;
