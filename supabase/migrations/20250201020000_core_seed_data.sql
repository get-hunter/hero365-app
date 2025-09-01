-- =============================================
-- COMPREHENSIVE CORE SEED DATA
-- =============================================
-- Complete test data for platform testing
-- Depends on: All core tables

-- =============================================
-- DEMO USERS (Multi-User System)
-- =============================================

-- Demo contractor user (business owner)
INSERT INTO users (id, email, full_name, display_name, user_type, primary_role, is_active, is_verified) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'demo@hero365.app', 'Mike Johnson', 'Mike J.', 'contractor', 'business_owner', true, true),
('550e8400-e29b-41d4-a716-446655440001', 'tech1@elitehvac.com', 'Sarah Wilson', 'Sarah W.', 'contractor', 'technician', true, true),
('550e8400-e29b-41d4-a716-446655440002', 'tech2@elitehvac.com', 'David Martinez', 'David M.', 'contractor', 'technician', true, true),
('550e8400-e29b-41d4-a716-446655440003', 'client1@example.com', 'John Smith', 'John S.', 'client', 'customer', true, true),
('550e8400-e29b-41d4-a716-446655440004', 'client2@example.com', 'Lisa Brown', 'Lisa B.', 'client', 'customer', true, true),
('550e8400-e29b-41d4-a716-446655440005', 'supplier@hvacparts.com', 'Tom Anderson', 'Tom A.', 'supplier', 'supplier_rep', true, true)
ON CONFLICT (email) DO NOTHING;

-- User profiles
INSERT INTO user_profiles (user_id, bio, timezone, job_title, company_name, years_experience, onboarding_completed) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'Experienced HVAC business owner with 15+ years in the industry', 'America/Chicago', 'Owner & Master Technician', 'Elite HVAC Austin', 15, true),
('550e8400-e29b-41d4-a716-446655440001', 'Certified HVAC technician specializing in residential systems', 'America/Chicago', 'Senior HVAC Technician', 'Elite HVAC Austin', 8, true),
('550e8400-e29b-41d4-a716-446655440002', 'Commercial HVAC specialist with EPA certification', 'America/Chicago', 'Commercial HVAC Tech', 'Elite HVAC Austin', 5, true),
('550e8400-e29b-41d4-a716-446655440003', 'Homeowner in Austin area', 'America/Chicago', 'Software Engineer', 'Tech Corp', 0, true),
('550e8400-e29b-41d4-a716-446655440004', 'Property manager for residential complexes', 'America/Chicago', 'Property Manager', 'Austin Properties', 0, true),
('550e8400-e29b-41d4-a716-446655440005', 'HVAC parts supplier representative', 'America/Chicago', 'Sales Representative', 'HVAC Parts Plus', 12, true)
ON CONFLICT (user_id) DO NOTHING;

-- =============================================
-- DEMO BUSINESS
-- =============================================

INSERT INTO businesses (
    id, 
    owner_id, 
    name, 
    email, 
    phone, 
    address, 
    city, 
    state, 
    postal_code, 
    primary_trade, 
    secondary_trades, 
    market_focus, 
    residential_services, 
    commercial_services,
    selected_residential_service_keys,
    selected_commercial_service_keys,
    years_in_business, 
    certifications, 
    service_radius, 
    emergency_available, 
    year_established,
    is_active,
    is_verified,
    website
) VALUES (
    '550e8400-e29b-41d4-a716-446655440010',
    '550e8400-e29b-41d4-a716-446655440000',
    'Elite HVAC Austin',
    'info@elitehvac.com',
    '(512) 555-0100',
    '123 Main St',
    'Austin',
    'TX',
    '78701',
    'HVAC',
    ARRAY['Plumbing', 'Electrical'],
    'both',
    '["hvac", "plumbing", "electrical"]'::jsonb,
    '["mechanical", "plumbing", "electrical"]'::jsonb,
    '["hvac_repair", "hvac_installation", "hvac_maintenance", "emergency_hvac", "duct_cleaning", "thermostat_installation", "indoor_air_quality", "plumbing_repair", "drain_cleaning", "water_heater_service", "pipe_installation", "fixture_installation", "leak_detection", "sewer_line_service", "electrical_repair", "electrical_installation", "panel_upgrades", "outlet_installation", "lighting_installation", "electrical_inspection"]'::jsonb,
    '["hvac_installation", "hvac_maintenance", "commercial_hvac", "building_automation", "energy_management", "preventive_maintenance", "electrical_installation", "electrical_repair", "panel_upgrades", "lighting_systems", "power_distribution", "electrical_maintenance", "plumbing_installation", "commercial_plumbing", "backflow_prevention", "grease_trap_service", "water_line_service", "sewer_line_service"]'::jsonb,
    15,
    ARRAY['NATE', 'EPA', 'BBB A+'],
    25,
    true,
    2008,
    true,
    true,
    'https://elitehvac.com'
) ON CONFLICT (id) DO NOTHING;

-- Additional businesses to demonstrate different market focus options

-- Residential-only plumber
INSERT INTO businesses (
    id, 
    owner_id, 
    name, 
    email, 
    phone, 
    address, 
    city, 
    state, 
    postal_code, 
    primary_trade, 
    secondary_trades, 
    market_focus,
    residential_services,
    commercial_services,
    selected_residential_service_keys,
    selected_commercial_service_keys,
    years_in_business, 
    certifications, 
    service_radius, 
    emergency_available, 
    year_established,
    is_active,
    is_verified,
    website
) VALUES (
    '550e8400-e29b-41d4-a716-446655440011',
    '550e8400-e29b-41d4-a716-446655440000',
    'Austin Home Plumbing',
    'info@austinhomeplumbing.com',
    '(512) 555-0200',
    '456 Oak Ave',
    'Austin',
    'TX',
    '78702',
    'Plumbing',
    ARRAY[]::text[],
    'residential',
    '["plumbing"]'::jsonb,
    '[]'::jsonb,
    '["plumbing_repair", "drain_cleaning", "water_heater_service", "pipe_installation", "fixture_installation", "leak_detection", "sewer_line_service", "emergency_plumbing", "toilet_repair", "faucet_installation", "garbage_disposal", "water_filtration"]'::jsonb,
    '[]'::jsonb,
    8,
    ARRAY['Licensed Plumber', 'Insured'],
    20,
    true,
    2016,
    true,
    true,
    'https://austinhomeplumbing.com'
) ON CONFLICT (id) DO NOTHING;

-- Commercial-only electrical contractor
INSERT INTO businesses (
    id, 
    owner_id, 
    name, 
    email, 
    phone, 
    address, 
    city, 
    state, 
    postal_code, 
    primary_trade, 
    secondary_trades, 
    market_focus,
    residential_services,
    commercial_services,
    selected_residential_service_keys,
    selected_commercial_service_keys,
    years_in_business, 
    certifications, 
    service_radius, 
    emergency_available, 
    year_established,
    is_active,
    is_verified,
    website
) VALUES (
    '550e8400-e29b-41d4-a716-446655440012',
    '550e8400-e29b-41d4-a716-446655440000',
    'Commercial Electric Solutions',
    'info@commercialelectricsolutions.com',
    '(512) 555-0300',
    '789 Business Blvd',
    'Austin',
    'TX',
    '78703',
    'Electrical',
    ARRAY['Security Systems'],
    'commercial',
    '[]'::jsonb,
    '["electrical", "security_systems"]'::jsonb,
    '[]'::jsonb,
    '["electrical_installation", "electrical_repair", "panel_upgrades", "lighting_systems", "power_distribution", "electrical_maintenance", "security_cameras", "access_control", "alarm_systems", "fire_safety_systems", "intercom_systems", "security_monitoring", "structured_cabling"]'::jsonb,
    12,
    ARRAY['Master Electrician', 'Commercial Certified'],
    50,
    true,
    2012,
    true,
    true,
    'https://commercialelectricsolutions.com'
) ON CONFLICT (id) DO NOTHING;

-- International examples to demonstrate phone number support

-- UK Business
INSERT INTO businesses (
    id, 
    owner_id, 
    name, 
    email, 
    phone, 
    address, 
    city, 
    state, 
    postal_code, 
    primary_trade, 
    secondary_trades, 
    market_focus,
    residential_services,
    commercial_services,
    years_in_business, 
    certifications, 
    service_radius, 
    emergency_available, 
    year_established,
    is_active,
    is_verified,
    website
) VALUES (
    '550e8400-e29b-41d4-a716-446655440013',
    '550e8400-e29b-41d4-a716-446655440000',
    'London Heating Solutions',
    'info@londonheating.co.uk',
    '+44 20 7123 4567',  -- UK phone number
    '123 Baker Street',
    'London',
    'EN',
    'W1U 6TU',
    'HVAC',
    ARRAY[]::text[],
    'both',
    '["hvac", "plumbing"]'::jsonb,
    '["mechanical", "plumbing"]'::jsonb,
    12,
    ARRAY['Gas Safe', 'OFTEC'],
    30,
    true,
    2012,
    true,
    true,
    'https://londonheating.co.uk'
) ON CONFLICT (id) DO NOTHING;

-- German Business
INSERT INTO businesses (
    id, 
    owner_id, 
    name, 
    email, 
    phone, 
    address, 
    city, 
    state, 
    postal_code, 
    primary_trade, 
    secondary_trades, 
    market_focus,
    residential_services,
    commercial_services,
    years_in_business, 
    certifications, 
    service_radius, 
    emergency_available, 
    year_established,
    is_active,
    is_verified,
    website
) VALUES (
    '550e8400-e29b-41d4-a716-446655440014',
    '550e8400-e29b-41d4-a716-446655440000',
    'Berlin Elektro GmbH',
    'info@berlinelektro.de',
    '+49 30 12345678',  -- German phone number
    'Unter den Linden 1',
    'Berlin',
    'BE',
    '10117',
    'Electrical',
    ARRAY['Security Systems'],
    'commercial',
    '[]'::jsonb,
    '["electrical", "security_systems"]'::jsonb,
    20,
    ARRAY['VDE', 'IHK'],
    50,
    true,
    2004,
    true,
    true,
    'https://berlinelektro.de'
) ON CONFLICT (id) DO NOTHING;

-- Business memberships
INSERT INTO business_memberships (business_id, user_id, role, status, permissions) VALUES
('550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440000', 'owner', 'active', '["all"]'),
('550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440001', 'employee', 'active', '["view_jobs", "edit_jobs", "view_customers"]'),
('550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440002', 'employee', 'active', '["view_jobs", "edit_jobs", "view_customers"]')
ON CONFLICT (business_id, user_id) DO NOTHING;

-- Business services
INSERT INTO business_services (business_id, service_name, service_slug, description, price_min, price_max, is_active) VALUES
('550e8400-e29b-41d4-a716-446655440010', 'HVAC Repair', 'hvac-repair', 'Professional HVAC system diagnosis and repair', 100, 500, true),
('550e8400-e29b-41d4-a716-446655440010', 'AC Installation', 'ac-installation', 'Complete air conditioning system installation', 2000, 8000, true),
('550e8400-e29b-41d4-a716-446655440010', 'Emergency HVAC', 'emergency-hvac', '24/7 emergency HVAC services', 150, 800, true),
('550e8400-e29b-41d4-a716-446655440010', 'Furnace Repair', 'furnace-repair', 'Heating system repair and maintenance', 120, 600, true),
('550e8400-e29b-41d4-a716-446655440010', 'Duct Cleaning', 'duct-cleaning', 'Air duct cleaning and sanitization', 200, 400, true),
('550e8400-e29b-41d4-a716-446655440010', 'HVAC Maintenance', 'hvac-maintenance', 'Preventive maintenance and tune-ups', 80, 200, true),
('550e8400-e29b-41d4-a716-446655440010', 'Heat Pump Installation', 'heat-pump-installation', 'Energy-efficient heat pump systems', 3000, 12000, true),
('550e8400-e29b-41d4-a716-446655440010', 'Indoor Air Quality', 'indoor-air-quality', 'Air purification and filtration systems', 300, 1500, true)
ON CONFLICT (business_id, service_slug) DO NOTHING;

-- Business locations
INSERT INTO business_locations (business_id, name, city, state, postal_code, county, is_primary, service_radius, is_active) VALUES
('550e8400-e29b-41d4-a716-446655440010', 'Main Office', 'Austin', 'TX', '78701', 'Travis', true, 25, true),
('550e8400-e29b-41d4-a716-446655440010', 'North Austin Service Area', 'Round Rock', 'TX', '78664', 'Williamson', false, 15, true),
('550e8400-e29b-41d4-a716-446655440010', 'West Austin Service Area', 'Cedar Park', 'TX', '78613', 'Williamson', false, 15, true)
ON CONFLICT DO NOTHING;

-- =============================================
-- CONTACTS & CUSTOMERS
-- =============================================

INSERT INTO contacts (
    id, business_id, user_id, first_name, last_name, full_name, email, phone, 
    address, city, state, postal_code, contact_type, contact_source, lead_status,
    customer_since, total_jobs, total_revenue, is_active
) VALUES 
('550e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440003', 
 'John', 'Smith', 'John Smith', 'john.smith@example.com', '(512) 555-0200',
 '456 Oak Street', 'Austin', 'TX', '78702', 'customer', 'website', 'won', '2023-01-15', 3, 2450.00, true),

('550e8400-e29b-41d4-a716-446655440021', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440004',
 'Lisa', 'Brown', 'Lisa Brown', 'lisa.brown@example.com', '(512) 555-0201',
 '789 Pine Avenue', 'Austin', 'TX', '78703', 'customer', 'referral', 'won', '2023-03-20', 2, 1800.00, true),

('550e8400-e29b-41d4-a716-446655440022', '550e8400-e29b-41d4-a716-446655440010', NULL,
 'Robert', 'Davis', 'Robert Davis', 'robert.davis@example.com', '(512) 555-0202',
 '321 Elm Street', 'Round Rock', 'TX', '78664', 'lead', 'google', 'qualified', NULL, 0, 0, true),

('550e8400-e29b-41d4-a716-446655440023', '550e8400-e29b-41d4-a716-446655440010', NULL,
 'Maria', 'Garcia', 'Maria Garcia', 'maria.garcia@example.com', '(512) 555-0203',
 '654 Maple Drive', 'Cedar Park', 'TX', '78613', 'customer', 'facebook', 'won', '2023-06-10', 1, 650.00, true)
ON CONFLICT (id) DO NOTHING;

-- Contact notes
INSERT INTO contact_notes (contact_id, business_id, created_by, title, content, note_type, is_important) VALUES
('550e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440000', 
 'Initial Service Call', 'Customer called about AC not cooling properly. Scheduled diagnostic for tomorrow.', 'call', false),
('550e8400-e29b-41d4-a716-446655440021', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440000',
 'Follow-up Required', 'Customer mentioned interest in whole-house air purifier. Follow up in 2 weeks.', 'follow_up', true),
('550e8400-e29b-41d4-a716-446655440022', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440000',
 'Lead Qualification', 'Interested in new HVAC system for 2500 sq ft home. Budget: $8000-12000', 'general', true)
ON CONFLICT DO NOTHING;

-- =============================================
-- PROJECTS & JOBS
-- =============================================

INSERT INTO projects (
    id, business_id, contact_id, title, description, status, priority,
    start_date, end_date, estimated_cost, actual_cost
) VALUES
('550e8400-e29b-41d4-a716-446655440030', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440020',
 'Smith Residence - AC Repair & Maintenance', 'Complete AC system repair and annual maintenance', 'completed', 'medium',
 '2023-07-01', '2023-07-02', 800.00, 750.00),

('550e8400-e29b-41d4-a716-446655440031', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440021',
 'Brown Property - HVAC Installation', 'New HVAC system installation for rental property', 'active', 'high',
 '2023-08-15', '2023-08-20', 6500.00, 0),

('550e8400-e29b-41d4-a716-446655440032', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440022',
 'Davis Home - System Quote', 'Quote for complete HVAC replacement', 'draft', 'medium',
 '2023-09-01', NULL, 0, 0)
ON CONFLICT (id) DO NOTHING;

-- Jobs
INSERT INTO jobs (
    id, project_id, business_id, title, description, status, priority,
    assigned_to, scheduled_date, scheduled_start_time, scheduled_end_time
) VALUES
('550e8400-e29b-41d4-a716-446655440040', '550e8400-e29b-41d4-a716-446655440030', '550e8400-e29b-41d4-a716-446655440010',
 'AC Diagnostic & Repair', 'Diagnose cooling issue and repair refrigerant leak', 'completed', 'medium',
 '550e8400-e29b-41d4-a716-446655440001', '2023-07-01', '09:00:00', '15:00:00'),

('550e8400-e29b-41d4-a716-446655440041', '550e8400-e29b-41d4-a716-446655440030', '550e8400-e29b-41d4-a716-446655440010',
 'Annual Maintenance', 'Complete system tune-up and filter replacement', 'completed', 'medium',
 '550e8400-e29b-41d4-a716-446655440002', '2023-07-02', '10:00:00', '12:00:00'),

('550e8400-e29b-41d4-a716-446655440042', '550e8400-e29b-41d4-a716-446655440031', '550e8400-e29b-41d4-a716-446655440010',
 'Equipment Installation', 'Install new HVAC unit and ductwork', 'in_progress', 'high',
 '550e8400-e29b-41d4-a716-446655440001', '2023-08-15', '08:00:00', '17:00:00')
ON CONFLICT (id) DO NOTHING;

-- Activities (time tracking)
INSERT INTO activities (
    id, job_id, business_id, user_id, title, activity_type, description,
    start_time, end_time, duration_minutes
) VALUES
('550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440040', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440001',
 'System Diagnostic', 'work', 'System diagnostic and leak detection', '2023-07-01 09:00:00', '2023-07-01 11:30:00', 150),

('550e8400-e29b-41d4-a716-446655440051', '550e8400-e29b-41d4-a716-446655440040', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440001',
 'Leak Repair', 'work', 'Refrigerant leak repair and system recharge', '2023-07-01 12:00:00', '2023-07-01 13:00:00', 60),

('550e8400-e29b-41d4-a716-446655440052', '550e8400-e29b-41d4-a716-446655440041', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440002',
 'Annual Maintenance', 'work', 'Annual maintenance and filter replacement', '2023-07-02 10:00:00', '2023-07-02 12:00:00', 120)
ON CONFLICT (id) DO NOTHING;

-- =============================================
-- SYSTEM TEMPLATES
-- =============================================

INSERT INTO templates (id, name, template_type, content, is_system, is_active, is_default, business_id) VALUES
-- System templates (available to all businesses)
('550e8400-e29b-41d4-a716-446655440060', 'Classic Professional Estimate', 'estimate',
 '{"layout": "classic", "colors": {"primary": "#2563eb", "secondary": "#64748b"}, "sections": ["header", "client_info", "items", "totals", "terms"]}',
 true, true, true, NULL),

('550e8400-e29b-41d4-a716-446655440061', 'Classic Professional Invoice', 'invoice',
 '{"layout": "classic", "colors": {"primary": "#2563eb", "secondary": "#64748b"}, "sections": ["header", "client_info", "items", "totals", "payment_info"]}',
 true, true, true, NULL),

('550e8400-e29b-41d4-a716-446655440062', 'Modern HVAC Estimate', 'estimate',
 '{"layout": "modern", "colors": {"primary": "#059669", "secondary": "#374151"}, "sections": ["header", "client_info", "items", "totals", "terms"], "hvac_specific": true}',
 true, true, false, NULL),

-- Business-specific templates
('550e8400-e29b-41d4-a716-446655440063', 'Elite HVAC Custom Estimate', 'estimate',
 '{"layout": "branded", "colors": {"primary": "#1e40af", "secondary": "#64748b"}, "sections": ["header", "client_info", "items", "totals", "terms"], "logo": true}',
 false, true, false, '550e8400-e29b-41d4-a716-446655440010')
ON CONFLICT (id) DO NOTHING;

-- =============================================
-- ESTIMATES & INVOICES
-- =============================================

INSERT INTO estimates (
    id, business_id, contact_id, project_id, template_id, estimate_number, title,
    status, subtotal, tax_rate, tax_amount, total_amount, expiry_date
) VALUES
('550e8400-e29b-41d4-a716-446655440070', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440030',
 '550e8400-e29b-41d4-a716-446655440060', 'EST-2023-001', 'AC Repair & Maintenance Service',
 'approved', 650.00, 0.0825, 53.63, 703.63, '2023-08-01'),

('550e8400-e29b-41d4-a716-446655440071', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440021', '550e8400-e29b-41d4-a716-446655440031',
 '550e8400-e29b-41d4-a716-446655440062', 'EST-2023-002', 'Complete HVAC System Installation',
 'sent', 6200.00, 0.0825, 511.50, 6711.50, '2023-09-15'),

('550e8400-e29b-41d4-a716-446655440072', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440022', '550e8400-e29b-41d4-a716-446655440032',
 '550e8400-e29b-41d4-a716-446655440063', 'EST-2023-003', 'HVAC System Replacement Quote',
 'draft', 8500.00, 0.0825, 701.25, 9201.25, '2023-10-01')
ON CONFLICT (id) DO NOTHING;

-- Estimate items
INSERT INTO estimate_items (estimate_id, item_type, name, description, quantity, unit_price, total_price, display_order) VALUES
('550e8400-e29b-41d4-a716-446655440070', 'service', 'AC Diagnostic', 'Complete system diagnostic and leak detection', 1, 150.00, 150.00, 1),
('550e8400-e29b-41d4-a716-446655440070', 'service', 'Refrigerant Leak Repair', 'Repair refrigerant leak and recharge system', 1, 300.00, 300.00, 2),
('550e8400-e29b-41d4-a716-446655440070', 'service', 'Annual Maintenance', 'Complete system tune-up and filter replacement', 1, 200.00, 200.00, 3),

('550e8400-e29b-41d4-a716-446655440071', 'equipment', '3-Ton HVAC Unit', 'High-efficiency 16 SEER HVAC system', 1, 4500.00, 4500.00, 1),
('550e8400-e29b-41d4-a716-446655440071', 'service', 'Installation Labor', 'Complete installation including ductwork', 1, 1200.00, 1200.00, 2),
('550e8400-e29b-41d4-a716-446655440071', 'material', 'Ductwork & Materials', 'New ductwork and installation materials', 1, 500.00, 500.00, 3)
ON CONFLICT DO NOTHING;

-- Invoices
INSERT INTO invoices (
    id, business_id, contact_id, project_id, estimate_id, template_id, invoice_number,
    title, status, subtotal, tax_rate, tax_amount, total_amount, due_date
) VALUES
('550e8400-e29b-41d4-a716-446655440080', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440030',
 '550e8400-e29b-41d4-a716-446655440070', '550e8400-e29b-41d4-a716-446655440061', 'INV-2023-001',
 'AC Repair & Maintenance Service', 'paid', 650.00, 0.0825, 53.63, 703.63, '2023-08-01')
ON CONFLICT (id) DO NOTHING;

-- Invoice items
INSERT INTO invoice_items (invoice_id, item_type, name, description, quantity, unit_price, total_price, display_order) VALUES
('550e8400-e29b-41d4-a716-446655440080', 'service', 'AC Diagnostic', 'Complete system diagnostic and leak detection', 1, 150.00, 150.00, 1),
('550e8400-e29b-41d4-a716-446655440080', 'service', 'Refrigerant Leak Repair', 'Repair refrigerant leak and recharge system', 1, 300.00, 300.00, 2),
('550e8400-e29b-41d4-a716-446655440080', 'service', 'Annual Maintenance', 'Complete system tune-up and filter replacement', 1, 200.00, 200.00, 3)
ON CONFLICT DO NOTHING;

COMMIT;