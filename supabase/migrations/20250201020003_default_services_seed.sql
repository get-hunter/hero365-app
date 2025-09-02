-- =============================================
-- DEFAULT SERVICES SEED FROM TRADES & MARKET FOCUS
-- Apply default service pages for seeded demo businesses so the
-- website builder can generate SEO-optimized service routes.
--
-- Relies on the following seeded business IDs from 20250201020000_core_seed_data.sql:
--  - Elite HVAC Austin:               550e8400-e29b-41d4-a716-446655440010
--  - Austin Home Plumbing:            550e8400-e29b-41d4-a716-446655440011
--  - Commercial Electric Solutions:   550e8400-e29b-41d4-a716-446655440012

-- Notes:
--  - Service slugs follow the domain mapping in backend DefaultServicesMapping
--  - Display names are Title Case versions of the slugs
--  - Prices are illustrative to enable pricing UI and SEO pages
--  - Use ON CONFLICT to keep this migration idempotent

-- =============================================
-- RESIDENTIAL: Austin Home Plumbing (residential plumber)
-- =============================================
INSERT INTO business_services (business_id, service_name, service_slug, description, price_min, price_max, is_residential, is_commercial, is_active)
VALUES
('550e8400-e29b-41d4-a716-446655440011', 'Plumbing Repair', 'plumbing-repair', 'General residential plumbing repair services', 150, 1500, true, false, true),
('550e8400-e29b-41d4-a716-446655440011', 'Drain Cleaning', 'drain-cleaning', 'Clog removal and drain line cleaning', 100, 600, true, false, true),
('550e8400-e29b-41d4-a716-446655440011', 'Water Heater Service', 'water-heater-service', 'Repair and maintenance for water heaters', 150, 2000, true, false, true),
('550e8400-e29b-41d4-a716-446655440011', 'Pipe Installation', 'pipe-installation', 'New pipe installation and repiping services', 200, 5000, true, false, true),
('550e8400-e29b-41d4-a716-446655440011', 'Fixture Installation', 'fixture-installation', 'Install sinks, faucets, toilets, and fixtures', 100, 1000, true, false, true),
('550e8400-e29b-41d4-a716-446655440011', 'Leak Detection', 'leak-detection', 'Electronic leak detection and repair', 100, 800, true, false, true),
('550e8400-e29b-41d4-a716-446655440011', 'Sewer Line Service', 'sewer-line-service', 'Sewer line inspection and repair', 500, 8000, true, false, true),
('550e8400-e29b-41d4-a716-446655440011', 'Emergency Plumbing', 'emergency-plumbing', '24/7 emergency plumbing services', 150, 1000, true, false, true),
('550e8400-e29b-41d4-a716-446655440011', 'Bathroom Remodeling', 'bathroom-remodeling', 'Full or partial bathroom remodel plumbing', 1500, 25000, true, false, true)
ON CONFLICT (business_id, service_slug) DO NOTHING;

-- =============================================
-- COMMERCIAL: Commercial Electric Solutions (commercial electrical + security)
-- =============================================
INSERT INTO business_services (business_id, service_name, service_slug, description, price_min, price_max, is_residential, is_commercial, is_active)
VALUES
('550e8400-e29b-41d4-a716-446655440012', 'Electrical Installation', 'electrical-installation', 'Commercial electrical system installations', 500, 5000, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Electrical Repair', 'electrical-repair', 'Troubleshooting and repair for commercial electrical', 150, 1200, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Panel Upgrades', 'panel-upgrades', 'Service panel upgrades and replacements', 1000, 3000, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Lighting Systems', 'lighting-systems', 'Commercial lighting design and installation', 500, 8000, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Power Distribution', 'power-distribution', 'Distribution systems for commercial facilities', 2000, 20000, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Electrical Maintenance', 'electrical-maintenance', 'Preventive electrical maintenance programs', 100, 2000, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Code Compliance', 'code-compliance', 'Compliance audits and remediation', 200, 3000, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Energy Management', 'energy-management', 'Energy efficiency audits and upgrades', 1000, 10000, false, true, true),
-- Security systems
('550e8400-e29b-41d4-a716-446655440012', 'Security Cameras', 'security-cameras', 'CCTV and IP camera systems', 300, 5000, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Access Control', 'access-control', 'Keycard and access control solutions', 1000, 8000, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Alarm Systems', 'alarm-systems', 'Intrusion and alarm systems', 500, 5000, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Fire Safety Systems', 'fire-safety-systems', 'Fire alarms and life safety systems', 1000, 10000, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Intercom Systems', 'intercom-systems', 'Commercial intercom and communication systems', 400, 4000, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Security Monitoring', 'security-monitoring', 'Monitoring and response services', 50, 200, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'System Maintenance', 'system-maintenance', 'Preventive maintenance for security systems', 200, 2000, false, true, true),
('550e8400-e29b-41d4-a716-446655440012', 'Security Consulting', 'security-consulting', 'Risk assessment and security consulting', 200, 2000, false, true, true)
ON CONFLICT (business_id, service_slug) DO NOTHING;

-- =============================================
-- BOTH MARKETS: Elite HVAC Austin (HVAC + Plumbing + Electrical)
-- Add comprehensive services to expand SEO surface area.
-- Note: Some slugs may overlap with existing seed rows; ON CONFLICT prevents dupes.
-- =============================================
INSERT INTO business_services (business_id, service_name, service_slug, description, price_min, price_max, is_residential, is_commercial, is_active)
VALUES
-- Residential HVAC
('550e8400-e29b-41d4-a716-446655440010', 'AC Installation', 'ac-installation', 'Residential air conditioning installation', 2000, 8000, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'AC Repair', 'ac-repair', 'AC diagnosis and repair', 120, 900, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'Furnace Repair', 'furnace-repair', 'Furnace diagnosis and repair', 120, 900, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'Heat Pump Service', 'heat-pump-service', 'Heat pump repair and maintenance', 150, 1200, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'Duct Cleaning', 'duct-cleaning', 'Air duct cleaning and sanitization', 200, 600, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'HVAC Maintenance', 'hvac-maintenance', 'Seasonal HVAC tune-ups', 80, 300, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'Thermostat Installation', 'thermostat-installation', 'Smart thermostat installation', 100, 400, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'Indoor Air Quality', 'indoor-air-quality', 'Filtration and purification solutions', 300, 1500, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'Emergency HVAC', 'emergency-hvac', '24/7 emergency HVAC service', 150, 800, true, false, true),
-- Residential Plumbing
('550e8400-e29b-41d4-a716-446655440010', 'Plumbing Repair', 'plumbing-repair', 'Residential plumbing repair services', 150, 1500, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'Drain Cleaning', 'drain-cleaning', 'Drain clearing and cleaning', 100, 600, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'Water Heater Service', 'water-heater-service', 'Water heater repair and maintenance', 150, 2000, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'Leak Detection', 'leak-detection', 'Leak detection and repairs', 100, 800, true, false, true),
-- Residential Electrical
('550e8400-e29b-41d4-a716-446655440010', 'Electrical Repair', 'electrical-repair', 'Residential electrical troubleshooting and repair', 120, 1200, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'Panel Upgrades', 'panel-upgrades', 'Electrical panel upgrades', 1000, 3000, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'Lighting Installation', 'lighting-installation', 'Interior and exterior lighting installs', 100, 2500, true, false, true),
('550e8400-e29b-41d4-a716-446655440010', 'Generator Installation', 'generator-installation', 'Standby and portable generators', 2000, 9000, true, false, true),
-- Commercial Mechanical (HVAC)
('550e8400-e29b-41d4-a716-446655440010', 'HVAC Installation', 'hvac-installation', 'Commercial HVAC installation', 5000, 50000, false, true, true),
('550e8400-e29b-41d4-a716-446655440010', 'HVAC Repair', 'hvac-repair', 'Commercial HVAC repair', 200, 3000, false, true, true),
('550e8400-e29b-41d4-a716-446655440010', 'Boiler Service', 'boiler-service', 'Boiler maintenance and repairs', 300, 5000, false, true, true),
('550e8400-e29b-41d4-a716-446655440010', 'Chiller Service', 'chiller-service', 'Chiller maintenance and repairs', 500, 10000, false, true, true),
('550e8400-e29b-41d4-a716-446655440010', 'Ventilation Systems', 'ventilation-systems', 'Commercial ventilation solutions', 1000, 15000, false, true, true),
('550e8400-e29b-41d4-a716-446655440010', 'Air Quality Systems', 'air-quality-systems', 'Commercial filtration and IAQ systems', 500, 8000, false, true, true),
('550e8400-e29b-41d4-a716-446655440010', 'Energy Audits', 'energy-audits', 'Energy efficiency audits', 500, 5000, false, true, true)
ON CONFLICT (business_id, service_slug) DO NOTHING;

-- =============================================
-- NORMALIZE ALL SERVICE SLUGS TO KEBAB-CASE
-- =============================================
-- Ensure all service slugs are in kebab-case format
UPDATE business_services 
SET service_slug = snake_to_kebab(service_slug)
WHERE service_slug LIKE '%_%';

-- Update SEO-related tables if they exist
UPDATE service_seo_config 
SET service_slug = snake_to_kebab(service_slug)
WHERE service_slug LIKE '%_%';

UPDATE service_location_pages 
SET service_slug = snake_to_kebab(service_slug)
WHERE service_slug LIKE '%_%';

-- Ensure emergency services are properly flagged
UPDATE business_services 
SET is_emergency = true
WHERE service_name ILIKE '%emergency%' OR service_slug ILIKE '%emergency%';

-- Update service flags based on business market focus
UPDATE business_services 
SET 
    is_residential = CASE 
        WHEN business_id = '550e8400-e29b-41d4-a716-446655440010' THEN true  -- Elite HVAC serves both markets
        WHEN business_id = '550e8400-e29b-41d4-a716-446655440011' THEN true  -- Austin Home Plumbing is residential only
        WHEN business_id = '550e8400-e29b-41d4-a716-446655440012' THEN false -- Commercial Electric is commercial only
        ELSE is_residential
    END,
    is_commercial = CASE 
        WHEN business_id = '550e8400-e29b-41d4-a716-446655440010' THEN true  -- Elite HVAC serves both markets
        WHEN business_id = '550e8400-e29b-41d4-a716-446655440011' THEN false -- Austin Home Plumbing is residential only
        WHEN business_id = '550e8400-e29b-41d4-a716-446655440012' THEN true  -- Commercial Electric is commercial only
        ELSE is_commercial
    END
WHERE business_id IN (
    '550e8400-e29b-41d4-a716-446655440010',  -- Elite HVAC Austin
    '550e8400-e29b-41d4-a716-446655440011',  -- Austin Home Plumbing  
    '550e8400-e29b-41d4-a716-446655440012'   -- Commercial Electric Solutions
);

COMMIT;


