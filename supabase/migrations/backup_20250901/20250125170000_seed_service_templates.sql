-- Seed service template system with common industry services
-- This provides immediate value for new businesses in different trades

-- Insert Service Categories
INSERT INTO service_categories (name, description, slug, trade_types, category_type, icon, sort_order) VALUES
-- HVAC Categories
('Air Conditioning', 'Cooling systems, AC units, and related services', 'air-conditioning', ARRAY['hvac'], 'equipment', 'snowflake', 10),
('Heating', 'Furnaces, boilers, heat pumps, and heating services', 'heating', ARRAY['hvac'], 'equipment', 'flame', 20),
('Ventilation', 'Air ducts, ventilation systems, and air quality', 'ventilation', ARRAY['hvac'], 'equipment', 'wind', 30),
('HVAC Installation', 'New system installations and replacements', 'hvac-installation', ARRAY['hvac'], 'service_type', 'wrench', 40),
('HVAC Maintenance', 'Preventive maintenance and tune-ups', 'hvac-maintenance', ARRAY['hvac'], 'service_type', 'settings', 50),
('HVAC Repair', 'System repairs and diagnostics', 'hvac-repair', ARRAY['hvac'], 'service_type', 'tool', 60),

-- Plumbing Categories
('Water Systems', 'Water heaters, pumps, and water treatment', 'water-systems', ARRAY['plumbing'], 'equipment', 'droplets', 70),
('Drain & Sewer', 'Drain cleaning, sewer line services', 'drain-sewer', ARRAY['plumbing'], 'equipment', 'zap', 80),
('Fixtures & Appliances', 'Faucets, toilets, and plumbing fixtures', 'fixtures-appliances', ARRAY['plumbing'], 'equipment', 'home', 90),
('Plumbing Installation', 'New plumbing installations', 'plumbing-installation', ARRAY['plumbing'], 'service_type', 'plus', 100),
('Plumbing Maintenance', 'Preventive plumbing maintenance', 'plumbing-maintenance', ARRAY['plumbing'], 'service_type', 'calendar', 110),
('Plumbing Repair', 'Pipe repairs and leak fixes', 'plumbing-repair', ARRAY['plumbing'], 'service_type', 'wrench', 120),

-- Electrical Categories
('Electrical Systems', 'Panels, wiring, and electrical infrastructure', 'electrical-systems', ARRAY['electrical'], 'equipment', 'zap', 130),
('Lighting', 'Light fixtures, LED upgrades, and lighting design', 'lighting', ARRAY['electrical'], 'equipment', 'lightbulb', 140),
('Electrical Installation', 'New electrical work and installations', 'electrical-installation', ARRAY['electrical'], 'service_type', 'plug', 150),
('Electrical Maintenance', 'Electrical system maintenance and inspections', 'electrical-maintenance', ARRAY['electrical'], 'service_type', 'shield-check', 160),
('Electrical Repair', 'Electrical troubleshooting and repairs', 'electrical-repair', ARRAY['electrical'], 'service_type', 'zap', 170),

-- Cross-Trade Categories
('Emergency Service', '24/7 emergency repairs and service calls', 'emergency-service', ARRAY['hvac', 'plumbing', 'electrical'], 'service_type', 'phone', 1),
('Diagnostic', 'System diagnostics and troubleshooting', 'diagnostic', ARRAY['hvac', 'plumbing', 'electrical'], 'service_type', 'search', 2),
('Consultation', 'Professional consultations and estimates', 'consultation', ARRAY['hvac', 'plumbing', 'electrical'], 'service_type', 'users', 3),
('Warranty Service', 'Warranty repairs and covered services', 'warranty-service', ARRAY['hvac', 'plumbing', 'electrical'], 'service_type', 'shield', 4);

-- Insert Common Service Templates

-- Get category IDs for reference
WITH category_ids AS (
    SELECT 
        id,
        slug
    FROM service_categories
)

-- HVAC Service Templates
INSERT INTO service_templates (category_id, name, description, trade_types, service_type, pricing_model, default_unit_price, price_range_min, price_range_max, unit_of_measure, estimated_duration_hours, tags, is_common, is_emergency, requires_license, skill_level) 
SELECT 
    c.id,
    t.name,
    t.description,
    t.trade_types,
    t.service_type,
    t.pricing_model,
    t.default_unit_price,
    t.price_range_min,
    t.price_range_max,
    t.unit_of_measure,
    t.estimated_duration_hours,
    t.tags,
    t.is_common,
    t.is_emergency,
    t.requires_license,
    t.skill_level
FROM category_ids c
CROSS JOIN (VALUES
    -- Emergency Services
    ('emergency-service', 'Emergency AC Repair', 'Urgent air conditioning repair service available 24/7 for cooling emergencies', ARRAY['hvac'], 'emergency', 'quote_required', 149, 99, 499, 'service', 2, ARRAY['emergency', 'hvac', 'urgent'], true, true, true, 'intermediate'),
    ('emergency-service', 'Emergency Heating Repair', 'Urgent heating system repair service available 24/7 for heating emergencies', ARRAY['hvac'], 'emergency', 'quote_required', 159, 99, 599, 'service', 2.5, ARRAY['emergency', 'heating', 'urgent'], true, true, true, 'intermediate'),
    ('emergency-service', '24/7 Emergency Plumbing', 'Round-the-clock plumbing emergency service for leaks, clogs, and burst pipes', ARRAY['plumbing'], 'emergency', 'hourly', 125, 85, 200, 'hour', 1.5, ARRAY['emergency', 'plumbing', '24/7'], true, true, true, 'intermediate'),
    ('emergency-service', 'Emergency Electrical Service', 'Urgent electrical repairs for power outages and safety hazards', ARRAY['electrical'], 'emergency', 'hourly', 135, 95, 225, 'hour', 2, ARRAY['emergency', 'electrical', 'safety'], true, true, true, 'advanced'),

    -- Air Conditioning
    ('air-conditioning', 'AC Installation', 'Complete air conditioning system installation with warranty and setup', ARRAY['hvac'], 'service', 'quote_required', 3500, 1500, 8000, 'system', 8, ARRAY['installation', 'hvac', 'cooling'], true, false, true, 'advanced'),
    ('air-conditioning', 'AC Repair & Diagnostics', 'Professional AC system diagnosis and repair services', ARRAY['hvac'], 'service', 'quote_required', 199, 89, 599, 'service', 2, ARRAY['repair', 'diagnostic', 'hvac'], true, false, true, 'intermediate'),
    ('air-conditioning', 'AC Tune-Up & Maintenance', 'Annual AC system maintenance and performance optimization', ARRAY['hvac'], 'maintenance_plan', 'fixed', 129, 89, 199, 'service', 1.5, ARRAY['maintenance', 'tune-up', 'annual'], true, false, false, 'basic'),
    ('air-conditioning', 'Central Air Installation', 'Full central air conditioning system installation', ARRAY['hvac'], 'service', 'quote_required', 4200, 2500, 12000, 'system', 12, ARRAY['installation', 'central-air', 'cooling'], true, false, true, 'expert'),
    ('air-conditioning', 'AC Unit Replacement', 'Replace existing air conditioning unit with new energy-efficient model', ARRAY['hvac'], 'service', 'quote_required', 2800, 1200, 6500, 'unit', 6, ARRAY['replacement', 'upgrade', 'efficiency'], true, false, true, 'advanced'),

    -- Heating
    ('heating', 'Furnace Installation', 'Complete furnace system installation with ductwork and setup', ARRAY['hvac'], 'service', 'quote_required', 4000, 2000, 10000, 'system', 10, ARRAY['installation', 'furnace', 'heating'], true, false, true, 'expert'),
    ('heating', 'Furnace Repair', 'Furnace troubleshooting and repair services', ARRAY['hvac'], 'service', 'quote_required', 179, 99, 599, 'service', 2.5, ARRAY['repair', 'furnace', 'heating'], true, false, true, 'intermediate'),
    ('heating', 'Heat Pump Installation', 'Energy-efficient heat pump system installation', ARRAY['hvac'], 'service', 'quote_required', 5500, 3000, 12000, 'system', 12, ARRAY['installation', 'heat-pump', 'efficiency'], true, false, true, 'expert'),
    ('heating', 'Boiler Service & Repair', 'Professional boiler maintenance and repair services', ARRAY['hvac'], 'service', 'quote_required', 189, 109, 699, 'service', 3, ARRAY['repair', 'boiler', 'maintenance'], true, false, true, 'advanced'),
    ('heating', 'Heating System Tune-Up', 'Annual heating system maintenance and efficiency check', ARRAY['hvac'], 'maintenance_plan', 'fixed', 139, 99, 229, 'service', 2, ARRAY['maintenance', 'tune-up', 'annual'], true, false, false, 'basic'),

    -- Ventilation  
    ('ventilation', 'Duct Cleaning Service', 'Professional air duct cleaning and sanitization', ARRAY['hvac'], 'service', 'fixed', 299, 199, 599, 'service', 4, ARRAY['cleaning', 'air-quality', 'ducts'], true, false, false, 'basic'),
    ('ventilation', 'Duct Installation', 'New ductwork installation and design', ARRAY['hvac'], 'service', 'quote_required', 2500, 1000, 6000, 'system', 16, ARRAY['installation', 'ductwork', 'ventilation'], true, false, true, 'advanced'),
    ('ventilation', 'Air Quality Testing', 'Indoor air quality assessment and testing services', ARRAY['hvac'], 'service', 'fixed', 159, 99, 299, 'service', 1.5, ARRAY['testing', 'air-quality', 'assessment'], false, false, false, 'basic'),
    ('ventilation', 'Ventilation Repair', 'Repair and maintenance of ventilation systems', ARRAY['hvac'], 'service', 'quote_required', 149, 79, 399, 'service', 2, ARRAY['repair', 'ventilation', 'maintenance'], true, false, true, 'intermediate'),

    -- Plumbing Services
    ('water-systems', 'Water Heater Installation', 'New water heater installation with permits and warranty', ARRAY['plumbing'], 'service', 'quote_required', 1200, 600, 3000, 'unit', 4, ARRAY['installation', 'water-heater', 'hot-water'], true, false, true, 'intermediate'),
    ('water-systems', 'Water Heater Repair', 'Water heater troubleshooting and repair services', ARRAY['plumbing'], 'service', 'quote_required', 159, 89, 399, 'service', 2, ARRAY['repair', 'water-heater', 'hot-water'], true, false, true, 'intermediate'),
    ('water-systems', 'Tankless Water Heater Install', 'Energy-efficient tankless water heater installation', ARRAY['plumbing'], 'service', 'quote_required', 2200, 1500, 4000, 'unit', 6, ARRAY['installation', 'tankless', 'efficiency'], true, false, true, 'advanced'),
    ('water-systems', 'Water Pressure Repair', 'Diagnose and repair water pressure issues', ARRAY['plumbing'], 'service', 'quote_required', 129, 79, 299, 'service', 1.5, ARRAY['repair', 'pressure', 'water-flow'], true, false, false, 'basic'),

    -- Drain & Sewer
    ('drain-sewer', 'Drain Cleaning', 'Professional drain cleaning and unclogging service', ARRAY['plumbing'], 'service', 'fixed', 149, 99, 299, 'service', 1.5, ARRAY['cleaning', 'unclog', 'maintenance'], true, false, false, 'basic'),
    ('drain-sewer', 'Main Sewer Line Repair', 'Main sewer line inspection, cleaning, and repair', ARRAY['plumbing'], 'service', 'quote_required', 899, 300, 3000, 'service', 4, ARRAY['repair', 'sewer', 'excavation'], true, false, true, 'advanced'),
    ('drain-sewer', 'Hydro Jetting', 'High-pressure water jetting for severe blockages', ARRAY['plumbing'], 'service', 'fixed', 299, 199, 499, 'service', 2, ARRAY['cleaning', 'hydro-jet', 'blockage'], true, false, false, 'intermediate'),
    ('drain-sewer', 'Sewer Camera Inspection', 'Video camera inspection of sewer and drain lines', ARRAY['plumbing'], 'service', 'fixed', 199, 149, 399, 'service', 1, ARRAY['inspection', 'camera', 'diagnostic'], false, false, false, 'intermediate'),

    -- Plumbing Fixtures
    ('fixtures-appliances', 'Toilet Installation', 'New toilet installation with proper sealing and setup', ARRAY['plumbing'], 'service', 'fixed', 299, 199, 599, 'unit', 2, ARRAY['installation', 'toilet', 'fixture'], true, false, false, 'basic'),
    ('fixtures-appliances', 'Faucet Installation', 'Kitchen and bathroom faucet installation service', ARRAY['plumbing'], 'service', 'fixed', 159, 99, 299, 'unit', 1.5, ARRAY['installation', 'faucet', 'fixture'], true, false, false, 'basic'),
    ('fixtures-appliances', 'Shower Installation', 'Complete shower installation including plumbing and fixtures', ARRAY['plumbing'], 'service', 'quote_required', 899, 400, 2500, 'unit', 8, ARRAY['installation', 'shower', 'bathroom'], true, false, true, 'intermediate'),
    ('fixtures-appliances', 'Garbage Disposal Install', 'Kitchen garbage disposal installation and setup', ARRAY['plumbing'], 'service', 'fixed', 249, 149, 399, 'unit', 2, ARRAY['installation', 'disposal', 'kitchen'], true, false, false, 'basic'),

    -- Electrical Services
    ('electrical-systems', 'Electrical Panel Upgrade', 'Upgrade electrical panel to modern code standards', ARRAY['electrical'], 'service', 'quote_required', 1800, 800, 4000, 'panel', 8, ARRAY['upgrade', 'panel', 'safety'], true, false, true, 'expert'),
    ('electrical-systems', 'Whole House Rewiring', 'Complete home electrical rewiring service', ARRAY['electrical'], 'service', 'quote_required', 8500, 5000, 15000, 'house', 40, ARRAY['rewiring', 'upgrade', 'safety'], true, false, true, 'expert'),
    ('electrical-systems', 'Circuit Breaker Repair', 'Repair or replace faulty circuit breakers', ARRAY['electrical'], 'service', 'quote_required', 189, 99, 399, 'service', 1.5, ARRAY['repair', 'breaker', 'safety'], true, false, true, 'intermediate'),
    ('electrical-systems', 'GFCI Outlet Installation', 'Install GFCI outlets for bathroom and kitchen safety', ARRAY['electrical'], 'service', 'fixed', 129, 89, 199, 'outlet', 1, ARRAY['installation', 'gfci', 'safety'], true, false, true, 'basic'),

    -- Lighting
    ('lighting', 'LED Lighting Upgrade', 'Convert existing lighting to energy-efficient LED systems', ARRAY['electrical'], 'service', 'per_unit', 45, 25, 89, 'fixture', 0.5, ARRAY['upgrade', 'led', 'efficiency'], true, false, false, 'basic'),
    ('lighting', 'Ceiling Fan Installation', 'Install ceiling fans with proper electrical connections', ARRAY['electrical'], 'service', 'fixed', 189, 129, 299, 'fan', 2, ARRAY['installation', 'fan', 'cooling'], true, false, true, 'intermediate'),
    ('lighting', 'Outdoor Lighting Install', 'Landscape and security outdoor lighting installation', ARRAY['electrical'], 'service', 'quote_required', 599, 299, 1500, 'project', 6, ARRAY['installation', 'outdoor', 'security'], true, false, true, 'intermediate'),
    ('lighting', 'Smart Home Lighting', 'Smart lighting system installation and setup', ARRAY['electrical'], 'service', 'quote_required', 899, 400, 2000, 'system', 4, ARRAY['installation', 'smart-home', 'automation'], false, false, true, 'advanced'),

    -- Consultation & Diagnostic
    ('consultation', 'Home Energy Audit', 'Comprehensive energy efficiency assessment', ARRAY['hvac', 'electrical'], 'service', 'fixed', 199, 149, 299, 'service', 3, ARRAY['audit', 'efficiency', 'assessment'], false, false, false, 'intermediate'),
    ('consultation', 'Free Estimate', 'No-obligation consultation and project estimate', ARRAY['hvac', 'plumbing', 'electrical'], 'service', 'fixed', 0, 0, 0, 'service', 1, ARRAY['consultation', 'estimate', 'free'], true, false, false, 'basic'),
    ('consultation', 'System Design Consultation', 'Professional system design and planning services', ARRAY['hvac', 'plumbing', 'electrical'], 'service', 'hourly', 89, 59, 150, 'hour', 2, ARRAY['design', 'planning', 'consultation'], false, false, false, 'advanced'),

    -- Diagnostic
    ('diagnostic', 'System Diagnostic', 'Comprehensive system troubleshooting and analysis', ARRAY['hvac', 'plumbing', 'electrical'], 'service', 'fixed', 99, 59, 199, 'service', 1.5, ARRAY['diagnostic', 'troubleshooting', 'analysis'], true, false, false, 'intermediate'),
    ('diagnostic', 'Performance Testing', 'System performance testing and efficiency analysis', ARRAY['hvac', 'electrical'], 'service', 'fixed', 159, 99, 299, 'service', 2, ARRAY['testing', 'performance', 'efficiency'], false, false, false, 'intermediate')

) AS t(category_slug, name, description, trade_types, service_type, pricing_model, default_unit_price, price_range_min, price_range_max, unit_of_measure, estimated_duration_hours, tags, is_common, is_emergency, requires_license, skill_level)
WHERE c.slug = t.category_slug;

-- Update template usage counts and seasonal demand for relevant services
UPDATE service_templates 
SET seasonal_demand = '{"peak_months": ["june", "july", "august"], "demand_multiplier": 1.4}'
WHERE name LIKE '%AC%' OR name LIKE '%Air Conditioning%' OR name LIKE '%Cooling%';

UPDATE service_templates 
SET seasonal_demand = '{"peak_months": ["november", "december", "january", "february"], "demand_multiplier": 1.3}'
WHERE name LIKE '%Heat%' OR name LIKE '%Furnace%' OR name LIKE '%Boiler%';

UPDATE service_templates 
SET seasonal_demand = '{"peak_months": ["march", "april", "may", "september", "october"], "demand_multiplier": 1.1}'
WHERE name LIKE '%Maintenance%' OR name LIKE '%Tune-Up%';

-- Set upsell relationships (related services)
WITH template_relationships AS (
    SELECT 
        t1.id as main_id,
        ARRAY_AGG(t2.id) as related_ids
    FROM service_templates t1
    JOIN service_templates t2 ON t1.id != t2.id 
        AND t1.trade_types && t2.trade_types
        AND (
            -- AC services suggest maintenance
            (t1.name LIKE '%AC%' AND t2.name LIKE '%Maintenance%') OR
            -- Heating services suggest maintenance  
            (t1.name LIKE '%Furnace%' AND t2.name LIKE '%Tune-Up%') OR
            -- Installation services suggest maintenance
            (t1.name LIKE '%Installation%' AND t2.name LIKE '%Maintenance%') OR
            -- Emergency services suggest diagnostics
            (t1.is_emergency AND t2.name LIKE '%Diagnostic%')
        )
    GROUP BY t1.id
)
UPDATE service_templates 
SET upsell_templates = tr.related_ids
FROM template_relationships tr
WHERE service_templates.id = tr.main_id;

-- Add some maintenance plan templates
INSERT INTO service_templates (category_id, name, description, trade_types, service_type, pricing_model, default_unit_price, price_range_min, price_range_max, unit_of_measure, estimated_duration_hours, tags, is_common, is_emergency, requires_license, skill_level, seasonal_demand)
SELECT 
    c.id,
    t.name,
    t.description,
    t.trade_types,
    t.service_type,
    t.pricing_model,
    t.default_unit_price,
    t.price_range_min,
    t.price_range_max,
    t.unit_of_measure,
    t.estimated_duration_hours,
    t.tags,
    t.is_common,
    t.is_emergency,
    t.requires_license,
    t.skill_level,
    t.seasonal_demand::jsonb
FROM service_categories c
CROSS JOIN (VALUES
    ('hvac-maintenance', 'Annual HVAC Maintenance Plan', 'Comprehensive yearly HVAC system maintenance with priority service', ARRAY['hvac'], 'maintenance_plan', 'fixed', 299, 199, 499, 'plan', 4, ARRAY['maintenance', 'annual', 'priority'], true, false, false, 'basic', '{"visits_per_year": 2, "priority_service": true}'),
    ('plumbing-maintenance', 'Plumbing Protection Plan', 'Annual plumbing maintenance with discounted repairs', ARRAY['plumbing'], 'maintenance_plan', 'fixed', 199, 149, 349, 'plan', 2, ARRAY['maintenance', 'protection', 'discount'], true, false, false, 'basic', '{"visits_per_year": 1, "repair_discount": 0.15}'),
    ('electrical-maintenance', 'Electrical Safety Plan', 'Annual electrical system inspection and maintenance', ARRAY['electrical'], 'maintenance_plan', 'fixed', 249, 179, 399, 'plan', 3, ARRAY['maintenance', 'safety', 'inspection'], true, false, true, 'intermediate', '{"visits_per_year": 1, "safety_focused": true}')
) AS t(category_slug, name, description, trade_types, service_type, pricing_model, default_unit_price, price_range_min, price_range_max, unit_of_measure, estimated_duration_hours, tags, is_common, is_emergency, requires_license, skill_level, seasonal_demand)
WHERE c.slug = t.category_slug;
