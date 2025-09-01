-- Seed products and services for the existing business
-- This populates the products table with both product_type='product' and product_type='service'

-- Insert HVAC services (product_type = 'service')
INSERT INTO products (
    id, 
    business_id, 
    sku, 
    name, 
    description, 
    product_type, 
    status, 
    pricing_model, 
    unit_price, 
    cost_price, 
    unit_of_measure, 
    track_inventory, 
    current_stock, 
    is_active, 
    is_service,
    created_by,
    created_at, 
    updated_at
) VALUES 
-- HVAC Services
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'SVC-HVAC-001', 'Emergency AC Repair', '24/7 rapid response for all AC breakdowns. Our certified technicians diagnose and fix AC issues quickly to restore your comfort.', 'service', 'active', 'fixed', 149.00, 75.00, 'hour', false, 0, true, true, 'system', NOW(), NOW()),
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'SVC-HVAC-002', 'HVAC System Installation', 'Complete HVAC system installation and replacement. Energy-efficient systems with professional installation and warranty.', 'service', 'active', 'custom', 0.00, 0.00, 'each', false, 0, true, true, 'system', NOW(), NOW()),
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'SVC-HVAC-003', 'Preventative Maintenance Plan', 'Annual tune-ups to ensure optimal system performance and longevity. Includes filter changes, system cleaning, and efficiency checks.', 'service', 'active', 'fixed', 199.00, 50.00, 'year', false, 0, true, true, 'system', NOW(), NOW()),
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'SVC-HVAC-004', 'Duct Cleaning Service', 'Professional duct cleaning and sanitization to improve air quality and system efficiency. Removes dust, debris, and allergens.', 'service', 'active', 'fixed', 299.00, 100.00, 'each', false, 0, true, true, 'system', NOW(), NOW()),
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'SVC-HVAC-005', 'Thermostat Installation', 'Smart thermostat installation and setup. Includes programming and training on optimal usage for energy savings.', 'service', 'active', 'fixed', 125.00, 25.00, 'each', false, 0, true, true, 'system', NOW(), NOW())
ON CONFLICT (business_id, sku) DO NOTHING;

-- Insert HVAC products (product_type = 'product')
INSERT INTO products (
    id, 
    business_id, 
    sku, 
    name, 
    description, 
    product_type, 
    status, 
    pricing_model, 
    unit_price, 
    cost_price, 
    unit_of_measure, 
    track_inventory, 
    current_stock, 
    available_stock,
    reorder_point,
    reorder_quantity,
    is_active, 
    is_service,
    created_by,
    created_at, 
    updated_at
) VALUES 
-- HVAC Products
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'PRD-THERM-001', 'Smart Thermostat (Ecobee)', 'Energy-saving smart thermostat with remote control, voice integration, and room sensors. Wi-Fi enabled with mobile app control.', 'product', 'active', 'fixed', 249.99, 180.00, 'each', true, 15, 15, 5, 10, true, false, 'system', NOW(), NOW()),
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'PRD-FILTER-001', 'HEPA Air Filter (MERV 13)', 'High-efficiency particulate air filter for superior air purification. 20x20x1 size with 99.97% efficiency at 0.3 microns.', 'product', 'active', 'fixed', 39.99, 25.00, 'each', true, 100, 100, 20, 50, true, false, 'system', NOW(), NOW()),
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'PRD-AC-001', 'Central AC Unit (3 Ton)', 'Energy-efficient central air conditioning system for medium homes. 14.5 SEER rating with R-410A refrigerant and 10-year warranty.', 'product', 'active', 'fixed', 2499.99, 1800.00, 'each', true, 5, 5, 2, 1, true, false, 'system', NOW(), NOW()),
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'PRD-HP-001', 'Heat Pump System (4 Ton)', 'Dual-purpose heating and cooling heat pump system. Energy Star certified with variable speed compressor for maximum efficiency.', 'product', 'active', 'fixed', 3299.99, 2400.00, 'each', true, 3, 3, 1, 1, true, false, 'system', NOW(), NOW()),
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'PRD-DUCT-001', 'Flexible Ductwork (25ft)', 'Insulated flexible ductwork for HVAC installations. R-6 insulation with vapor barrier and reinforced construction.', 'product', 'active', 'fixed', 89.99, 45.00, 'each', true, 50, 50, 10, 25, true, false, 'system', NOW(), NOW())
ON CONFLICT (business_id, sku) DO NOTHING;

-- Success message
SELECT 'Products and services seed data applied successfully! 🎉' as message,
       'Added 5 HVAC services and 5 HVAC products to the database' as summary;
