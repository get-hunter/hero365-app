-- =============================================
-- SEED TRADE TAXONOMY DATA
-- =============================================

-- Insert trade profiles (normalized taxonomy from our plan)
INSERT INTO trade_profiles (slug, name, synonyms, segments, icon, description) VALUES
('general-contractor', 'General Contractor', '{"building contractor","general constructor","gc"}', 'both', 'building', 'Full-service construction and renovation projects'),
('carpentry-joinery', 'Carpentry & Joinery', '{"carpenter","joiner","woodworker"}', 'both', 'hammer', 'Custom woodwork, framing, and finish carpentry'),
('roofing', 'Roofing', '{"roofer","roofing contractor"}', 'both', 'home', 'Roof installation, repair, and maintenance'),
('metal-roofing', 'Metal Roofing', '{"standing seam","sheet metal roofing","metal roof"}', 'both', 'home', 'Specialized metal roofing systems'),
('electrical', 'Electrical', '{"electrician","electrical contractor"}', 'both', 'zap', 'Electrical installation, repair, and maintenance'),
('plumbing', 'Plumbing', '{"plumber","plumbing contractor"}', 'both', 'droplet', 'Plumbing installation, repair, and maintenance'),
('hvac', 'HVAC', '{"heating","ventilation","air conditioning","mechanical"}', 'residential', 'thermometer', 'Heating, ventilation, and air conditioning systems'),
('commercial-refrigeration', 'Commercial Refrigeration', '{"walk-in coolers","reach-ins","ice machines"}', 'commercial', 'snowflake', 'Commercial refrigeration systems and equipment'),
('security-systems', 'Security Systems', '{"cctv","access control","alarms","security"}', 'both', 'shield', 'Security and surveillance systems'),
('landscaping-gardening', 'Landscaping & Gardening', '{"landscaper","gardener","lawn care"}', 'both', 'trees', 'Landscape design, installation, and maintenance'),
('irrigation', 'Irrigation', '{"sprinkler systems","drip systems","irrigation"}', 'both', 'droplets', 'Irrigation system installation and maintenance'),
('painting-decorating', 'Painting & Decorating', '{"painter","varnisher","decorator"}', 'both', 'palette', 'Interior and exterior painting services'),
('flooring-tiling', 'Flooring & Tiling', '{"flooring","tiling","screed layer"}', 'both', 'square', 'Flooring installation and tile work'),
('plastering-stucco', 'Plastering & Stucco', '{"plasterer","stucco worker"}', 'both', 'paintbrush', 'Plastering and stucco application'),
('drywall-interior-finishing', 'Drywall & Interior Finishing', '{"drywall","taping","texturing","trim"}', 'both', 'square', 'Drywall installation and interior finishing'),
('commercial-kitchen-equipment', 'Commercial Kitchen Equipment', '{"ovens","fryers","hoods","kitchen equipment"}', 'commercial', 'chef-hat', 'Commercial kitchen equipment service'),
('water-treatment', 'Water Treatment', '{"water softeners","filtration","ro","reverse osmosis"}', 'both', 'droplet', 'Water treatment and filtration systems'),
('pool-spa', 'Pool & Spa', '{"pool service","spa service","pool maintenance"}', 'both', 'waves', 'Pool and spa installation and maintenance'),
('garage-doors', 'Garage Doors', '{"garage door","overhead door"}', 'residential', 'square', 'Garage door installation and repair'),
('chimney-fireplace', 'Chimney & Fireplace', '{"chimney sweep","fireplace repair","chimney lining"}', 'residential', 'flame', 'Chimney and fireplace services'),
('septic-systems', 'Septic Systems', '{"septic pumping","drain field","septic repair"}', 'residential', 'droplet', 'Septic system installation and maintenance'),
('solar-pv', 'Solar PV', '{"solar panels","photovoltaic","solar installation"}', 'both', 'sun', 'Solar panel design, installation, and maintenance'),
('metal-fabrication', 'Metal Fabrication', '{"railings","frames","custom metal","welding"}', 'both', 'wrench', 'Custom metal fabrication and welding'),
('pest-control', 'Pest Control', '{"exterminator","pest management","bug control"}', 'residential', 'bug', 'Pest control and extermination services')
ON CONFLICT (slug) DO NOTHING;

-- Insert common trade activities
INSERT INTO trade_activities (trade_slug, slug, name, synonyms, tags, default_booking_fields, required_booking_fields) VALUES
-- HVAC Activities
('hvac', 'ac-installation', 'AC Installation', '{"air conditioning installation","ac install"}', '{"installation","cooling"}', 
 '[{"key":"system_type","type":"select","label":"System Type","options":["Central Air","Ductless Mini-Split","Window Unit","Heat Pump"]},{"key":"home_size","type":"number","label":"Home Size (sq ft)"},{"key":"existing_ductwork","type":"select","label":"Existing Ductwork","options":["Yes","No","Needs Assessment"]}]',
 '[{"key":"problem_description","type":"textarea","label":"Installation Requirements"},{"key":"preferred_date","type":"date","label":"Preferred Date"},{"key":"contact_method","type":"select","label":"Contact Method","options":["Phone","Email","Text"]}]'),

('hvac', 'ac-repair', 'AC Repair', '{"air conditioning repair","ac fix"}', '{"repair","cooling","emergency"}',
 '[{"key":"problem_description","type":"textarea","label":"Describe the Problem"},{"key":"system_age","type":"number","label":"System Age (years)"},{"key":"last_service","type":"date","label":"Last Service Date"}]',
 '[{"key":"problem_description","type":"textarea","label":"Problem Description"},{"key":"urgency_level","type":"select","label":"Urgency","options":["Low","Medium","High","Emergency"]}]'),

('hvac', 'furnace-repair', 'Furnace Repair', '{"heating repair","furnace fix"}', '{"repair","heating","emergency"}',
 '[{"key":"problem_description","type":"textarea","label":"Describe the Problem"},{"key":"system_type","type":"select","label":"Furnace Type","options":["Gas","Electric","Oil","Propane"]},{"key":"system_age","type":"number","label":"System Age (years)"}]',
 '[{"key":"problem_description","type":"textarea","label":"Problem Description"},{"key":"urgency_level","type":"select","label":"Urgency","options":["Low","Medium","High","Emergency"]}]'),

('hvac', 'hvac-maintenance', 'HVAC Maintenance', '{"tune-up","hvac service","preventive maintenance"}', '{"maintenance","preventive"}',
 '[{"key":"system_type","type":"select","label":"System Type","options":["Central Air","Heat Pump","Furnace","Boiler"]},{"key":"last_service","type":"date","label":"Last Service Date"},{"key":"service_plan","type":"select","label":"Service Plan","options":["One-time","Annual","Bi-annual"]}]',
 '[{"key":"system_type","type":"select","label":"System Type","options":["Central Air","Heat Pump","Furnace","Boiler"]},{"key":"preferred_date","type":"date","label":"Preferred Date"}]'),

-- Plumbing Activities
('plumbing', 'drain-cleaning', 'Drain Cleaning', '{"clog removal","drain clearing","sewer cleaning"}', '{"repair","maintenance"}',
 '[{"key":"drain_location","type":"select","label":"Drain Location","options":["Kitchen Sink","Bathroom Sink","Shower","Toilet","Floor Drain","Main Line"]},{"key":"problem_severity","type":"select","label":"Severity","options":["Slow Drain","Partial Blockage","Complete Blockage","Backup"]}]',
 '[{"key":"drain_location","type":"select","label":"Drain Location","options":["Kitchen Sink","Bathroom Sink","Shower","Toilet","Floor Drain","Main Line"]},{"key":"problem_description","type":"textarea","label":"Problem Description"}]'),

('plumbing', 'pipe-repair', 'Pipe Repair', '{"leak repair","pipe replacement","plumbing repair"}', '{"repair","emergency"}',
 '[{"key":"leak_location","type":"text","label":"Leak Location"},{"key":"pipe_material","type":"select","label":"Pipe Material","options":["Copper","PVC","PEX","Galvanized","Unknown"]},{"key":"water_shutoff","type":"select","label":"Water Shut Off","options":["Yes","No","Cannot Find"]}]',
 '[{"key":"leak_location","type":"text","label":"Leak Location"},{"key":"urgency_level","type":"select","label":"Urgency","options":["Low","Medium","High","Emergency"]}]'),

('plumbing', 'water-heater-service', 'Water Heater Service', '{"water heater repair","hot water heater","tank replacement"}', '{"repair","installation"}',
 '[{"key":"heater_type","type":"select","label":"Water Heater Type","options":["Tank Electric","Tank Gas","Tankless Electric","Tankless Gas","Hybrid"]},{"key":"heater_age","type":"number","label":"Age (years)"},{"key":"problem_type","type":"select","label":"Issue","options":["No Hot Water","Not Enough Hot Water","Leaking","Strange Noises","Other"]}]',
 '[{"key":"heater_type","type":"select","label":"Water Heater Type","options":["Tank Electric","Tank Gas","Tankless Electric","Tankless Gas","Hybrid"]},{"key":"problem_description","type":"textarea","label":"Problem Description"}]'),

-- Electrical Activities
('electrical', 'electrical-repair', 'Electrical Repair', '{"electrical troubleshooting","wiring repair","electrical fix"}', '{"repair","emergency"}',
 '[{"key":"problem_area","type":"select","label":"Problem Area","options":["Outlet","Switch","Light Fixture","Circuit Breaker","Whole House","Other"]},{"key":"safety_concern","type":"select","label":"Safety Concern","options":["None","Sparks","Burning Smell","Shock","Fire Hazard"]}]',
 '[{"key":"problem_description","type":"textarea","label":"Problem Description"},{"key":"safety_concern","type":"select","label":"Safety Concern","options":["None","Sparks","Burning Smell","Shock","Fire Hazard"]}]'),

('electrical', 'panel-upgrade', 'Panel Upgrade', '{"electrical panel","breaker box","service upgrade"}', '{"installation","upgrade"}',
 '[{"key":"current_amperage","type":"select","label":"Current Panel Amperage","options":["60A","100A","150A","200A","Unknown"]},{"key":"desired_amperage","type":"select","label":"Desired Amperage","options":["100A","150A","200A","400A"]},{"key":"permit_needed","type":"select","label":"Permit Required","options":["Yes","No","Unsure"]}]',
 '[{"key":"current_amperage","type":"select","label":"Current Panel Amperage","options":["60A","100A","150A","200A","Unknown"]},{"key":"project_timeline","type":"select","label":"Timeline","options":["ASAP","Within 1 Week","Within 1 Month","Flexible"]}]'),

-- Roofing Activities
('roofing', 'roof-repair', 'Roof Repair', '{"leak repair","shingle replacement","roof fix"}', '{"repair","emergency"}',
 '[{"key":"problem_type","type":"select","label":"Problem Type","options":["Leak","Missing Shingles","Storm Damage","Flashing Issues","Gutter Problems"]},{"key":"roof_age","type":"number","label":"Roof Age (years)"},{"key":"roof_material","type":"select","label":"Roof Material","options":["Asphalt Shingles","Metal","Tile","Slate","Flat/TPO","Other"]}]',
 '[{"key":"problem_description","type":"textarea","label":"Problem Description"},{"key":"urgency_level","type":"select","label":"Urgency","options":["Low","Medium","High","Emergency"]}]'),

('roofing', 'roof-installation', 'Roof Installation', '{"new roof","roof replacement","re-roofing"}', '{"installation","replacement"}',
 '[{"key":"roof_size","type":"number","label":"Approximate Square Footage"},{"key":"desired_material","type":"select","label":"Desired Material","options":["Asphalt Shingles","Metal","Tile","Slate","Flat/TPO","Need Recommendation"]},{"key":"current_layers","type":"select","label":"Current Roof Layers","options":["1","2","3+","Unknown"]}]',
 '[{"key":"roof_size","type":"number","label":"Approximate Square Footage"},{"key":"project_timeline","type":"select","label":"Timeline","options":["ASAP","Within 1 Month","Within 3 Months","Flexible"]}]')

ON CONFLICT (slug) DO NOTHING;

-- Insert service templates mapped to activities (only if service_templates table exists and has the new columns)
DO $$
BEGIN
    IF EXISTS (SELECT column_name FROM information_schema.columns 
               WHERE table_name = 'service_templates' AND column_name = 'template_slug') THEN
        
        INSERT INTO service_templates (template_slug, activity_slug, name, description, pricing_model, pricing_config, is_common, is_emergency) VALUES
        -- HVAC Templates
        ('hvac-ac-installation-residential', 'ac-installation', 'Residential AC Installation', 'Complete air conditioning system installation for homes', 'per_unit', '{"base_price": 3500, "unit_key": "tons", "unit_label": "Tons", "per_unit_price": 1200, "min_units": 1.5, "max_units": 5}', true, false),
        ('hvac-ac-repair-emergency', 'ac-repair', 'Emergency AC Repair', 'Same-day air conditioning repair service', 'hourly', '{"hourly_rate": 150, "emergency_multiplier": 1.5, "minimum_hours": 1}', true, true),
        ('hvac-furnace-repair-standard', 'furnace-repair', 'Furnace Repair Service', 'Professional furnace diagnosis and repair', 'quote', '{"diagnostic_fee": 95, "typical_range_min": 200, "typical_range_max": 800}', true, false),
        ('hvac-maintenance-annual', 'hvac-maintenance', 'Annual HVAC Maintenance', 'Comprehensive system tune-up and inspection', 'fixed', '{"price": 149, "includes": ["filter_replacement", "system_inspection", "cleaning"]}', true, false),
        
        -- Plumbing Templates
        ('plumbing-drain-cleaning-standard', 'drain-cleaning', 'Standard Drain Cleaning', 'Professional drain cleaning and clog removal', 'fixed', '{"price": 125, "additional_drains": 50}', true, false),
        ('plumbing-pipe-repair-emergency', 'pipe-repair', 'Emergency Pipe Repair', '24/7 emergency pipe and leak repair', 'hourly', '{"hourly_rate": 125, "emergency_multiplier": 1.5, "minimum_hours": 1}', true, true),
        ('plumbing-water-heater-repair', 'water-heater-service', 'Water Heater Repair', 'Water heater diagnosis and repair service', 'quote', '{"diagnostic_fee": 85, "typical_range_min": 150, "typical_range_max": 600}', true, false),
        
        -- Electrical Templates
        ('electrical-repair-standard', 'electrical-repair', 'Standard Electrical Repair', 'General electrical troubleshooting and repair', 'hourly', '{"hourly_rate": 95, "minimum_hours": 1, "diagnostic_fee": 75}', true, false),
        ('electrical-panel-upgrade-200a', 'panel-upgrade', '200A Panel Upgrade', 'Upgrade electrical panel to 200 amp service', 'fixed', '{"price": 2500, "permit_included": true, "warranty_years": 5}', true, false),
        
        -- Roofing Templates
        ('roofing-repair-standard', 'roof-repair', 'Standard Roof Repair', 'Professional roof repair and leak fixing', 'quote', '{"minimum_charge": 250, "typical_range_min": 300, "typical_range_max": 1500}', true, false),
        ('roofing-installation-asphalt', 'roof-installation', 'Asphalt Shingle Roof Installation', 'Complete asphalt shingle roof replacement', 'per_unit', '{"base_price": 5000, "unit_key": "square", "unit_label": "Roofing Square", "per_unit_price": 400}', true, false)
        
        ON CONFLICT (template_slug) DO NOTHING;
        
    END IF;
END $$;

-- Update existing businesses to have a primary_trade_slug based on their current data
DO $$
BEGIN
    -- Update businesses that have primary_trade set to map to our new taxonomy
    UPDATE businesses 
    SET primary_trade_slug = CASE 
        WHEN LOWER(primary_trade) LIKE '%hvac%' OR LOWER(primary_trade) LIKE '%heating%' OR LOWER(primary_trade) LIKE '%cooling%' THEN 'hvac'
        WHEN LOWER(primary_trade) LIKE '%plumb%' THEN 'plumbing'
        WHEN LOWER(primary_trade) LIKE '%electric%' THEN 'electrical'
        WHEN LOWER(primary_trade) LIKE '%roof%' THEN 'roofing'
        WHEN LOWER(primary_trade) LIKE '%contractor%' OR LOWER(primary_trade) LIKE '%construction%' THEN 'general-contractor'
        WHEN LOWER(primary_trade) LIKE '%carpet%' OR LOWER(primary_trade) LIKE '%wood%' THEN 'carpentry-joinery'
        WHEN LOWER(primary_trade) LIKE '%paint%' THEN 'painting-decorating'
        WHEN LOWER(primary_trade) LIKE '%landscape%' OR LOWER(primary_trade) LIKE '%garden%' THEN 'landscaping-gardening'
        ELSE NULL
    END
    WHERE primary_trade IS NOT NULL AND primary_trade_slug IS NULL;
    
    -- Set default selected_activity_slugs based on primary_trade_slug
    UPDATE businesses 
    SET selected_activity_slugs = CASE 
        WHEN primary_trade_slug = 'hvac' THEN '{"ac-repair","furnace-repair","hvac-maintenance"}'::text[]
        WHEN primary_trade_slug = 'plumbing' THEN '{"drain-cleaning","pipe-repair","water-heater-service"}'::text[]
        WHEN primary_trade_slug = 'electrical' THEN '{"electrical-repair","panel-upgrade"}'::text[]
        WHEN primary_trade_slug = 'roofing' THEN '{"roof-repair","roof-installation"}'::text[]
        ELSE '{}'::text[]
    END
    WHERE primary_trade_slug IS NOT NULL AND (selected_activity_slugs IS NULL OR selected_activity_slugs = '{}');
    
END $$;

COMMIT;