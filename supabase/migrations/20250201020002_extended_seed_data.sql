-- =============================================
-- EXTENDED SEED DATA
-- =============================================
-- Additional test data for booking, inventory, technicians, and other systems
-- Depends on: core_seed_data.sql

-- =============================================
-- BOOKING SYSTEM DATA
-- =============================================

-- Business hours
INSERT INTO business_hours (business_id, day_of_week, is_open, open_time, close_time, is_emergency_available) VALUES
('550e8400-e29b-41d4-a716-446655440010', 1, true, '08:00', '17:00', false), -- Monday
('550e8400-e29b-41d4-a716-446655440010', 2, true, '08:00', '17:00', false), -- Tuesday
('550e8400-e29b-41d4-a716-446655440010', 3, true, '08:00', '17:00', false), -- Wednesday
('550e8400-e29b-41d4-a716-446655440010', 4, true, '08:00', '17:00', false), -- Thursday
('550e8400-e29b-41d4-a716-446655440010', 5, true, '08:00', '17:00', false), -- Friday
('550e8400-e29b-41d4-a716-446655440010', 6, true, '09:00', '15:00', true),  -- Saturday (emergency available)
('550e8400-e29b-41d4-a716-446655440010', 0, false, NULL, NULL, true)        -- Sunday (emergency only)
ON CONFLICT (business_id, day_of_week) DO NOTHING;

-- Bookable services
INSERT INTO bookable_services (id, business_id, name, description, duration_minutes, base_price, is_active, requires_approval) VALUES
('550e8400-e29b-41d4-a716-446655440100', '550e8400-e29b-41d4-a716-446655440010', 'HVAC Diagnostic', 'Complete system diagnostic and assessment', 120, 150.00, true, false),
('550e8400-e29b-41d4-a716-446655440101', '550e8400-e29b-41d4-a716-446655440010', 'AC Tune-Up', 'Annual air conditioning maintenance', 90, 120.00, true, false),
('550e8400-e29b-41d4-a716-446655440102', '550e8400-e29b-41d4-a716-446655440010', 'Emergency Service', '24/7 emergency HVAC repair', 180, 200.00, true, false),
('550e8400-e29b-41d4-a716-446655440103', '550e8400-e29b-41d4-a716-446655440010', 'System Installation Consultation', 'New system consultation and quote', 60, 0, true, true)
ON CONFLICT (id) DO NOTHING;

-- Service areas
INSERT INTO service_areas (business_id, area_name, city, state, postal_code, service_radius_miles, travel_fee, is_active) VALUES
('550e8400-e29b-41d4-a716-446655440010', 'Central Austin', 'Austin', 'TX', '78701', 10, 0, true),
('550e8400-e29b-41d4-a716-446655440010', 'North Austin', 'Austin', 'TX', '78758', 15, 25.00, true),
('550e8400-e29b-41d4-a716-446655440010', 'South Austin', 'Austin', 'TX', '78704', 15, 25.00, true),
('550e8400-e29b-41d4-a716-446655440010', 'Round Rock', 'Round Rock', 'TX', '78664', 20, 35.00, true),
('550e8400-e29b-41d4-a716-446655440010', 'Cedar Park', 'Cedar Park', 'TX', '78613', 20, 35.00, true)
ON CONFLICT DO NOTHING;

-- Bookings
INSERT INTO bookings (
    id, business_id, service_id, contact_id, booking_number, title, customer_name, customer_email, customer_phone,
    scheduled_at, estimated_duration_minutes, service_address, service_city, service_state, service_zip_code,
    status, quoted_price, special_instructions
) VALUES
('550e8400-e29b-41d4-a716-446655440110', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440100', '550e8400-e29b-41d4-a716-446655440020',
 'BOOK-2023-001', 'HVAC Diagnostic - Smith Residence', 'John Smith', 'john.smith@example.com', '(512) 555-0200',
 '2023-08-15 10:00:00', 120, '456 Oak Street', 'Austin', 'TX', '78702', 'completed', 150.00, 'AC not cooling properly'),

('550e8400-e29b-41d4-a716-446655440111', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440101', '550e8400-e29b-41d4-a716-446655440021',
 'BOOK-2023-002', 'AC Tune-Up - Brown Property', 'Lisa Brown', 'lisa.brown@example.com', '(512) 555-0201',
 '2023-08-20 14:00:00', 90, '789 Pine Avenue', 'Austin', 'TX', '78703', 'confirmed', 120.00, 'Annual maintenance'),

('550e8400-e29b-41d4-a716-446655440112', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440102', '550e8400-e29b-41d4-a716-446655440023',
 'BOOK-2023-003', 'Emergency Service - Garcia Home', 'Maria Garcia', 'maria.garcia@example.com', '(512) 555-0203',
 '2023-08-25 19:00:00', 180, '654 Maple Drive', 'Cedar Park', 'TX', '78613', 'scheduled', 200.00, 'No heat - emergency')
ON CONFLICT (id) DO NOTHING;

-- Calendar events
INSERT INTO calendar_events (
    id, business_id, booking_id, title, event_type, start_datetime, end_datetime,
    assigned_to, customer_id, service_id, status
) VALUES
('550e8400-e29b-41d4-a716-446655440120', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440110',
 'HVAC Diagnostic - Smith Residence', 'booking', '2023-08-15 10:00:00', '2023-08-15 12:00:00',
 '550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440100', 'completed'),

('550e8400-e29b-41d4-a716-446655440121', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440111',
 'AC Tune-Up - Brown Property', 'booking', '2023-08-20 14:00:00', '2023-08-20 15:30:00',
 '550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440021', '550e8400-e29b-41d4-a716-446655440101', 'scheduled')
ON CONFLICT (id) DO NOTHING;

-- =============================================
-- TECHNICIAN SYSTEM DATA
-- =============================================

-- Technicians
INSERT INTO technicians (
    id, business_id, user_id, employee_id, first_name, last_name, email, phone,
    title, hire_date, hourly_rate, is_active, can_be_booked, max_daily_hours,
    emergency_available, jobs_completed, average_job_rating
) VALUES
('550e8400-e29b-41d4-a716-446655440130', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440001',
 'EMP001', 'Sarah', 'Wilson', 'tech1@elitehvac.com', '(512) 555-0301',
 'Senior HVAC Technician', '2020-03-15', 35.00, true, true, 8, true, 156, 4.8),

('550e8400-e29b-41d4-a716-446655440131', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440002',
 'EMP002', 'David', 'Martinez', 'tech2@elitehvac.com', '(512) 555-0302',
 'Commercial HVAC Specialist', '2021-06-01', 32.00, true, true, 8, false, 98, 4.7)
ON CONFLICT (id) DO NOTHING;

-- Skills
INSERT INTO skills (business_id, name, category, description, requires_certification, min_experience_years) VALUES
('550e8400-e29b-41d4-a716-446655440010', 'Residential HVAC Repair', 'hvac', 'Residential heating and cooling system repair', false, 2),
('550e8400-e29b-41d4-a716-446655440010', 'Commercial HVAC Systems', 'hvac', 'Large commercial HVAC system maintenance', true, 5),
('550e8400-e29b-41d4-a716-446655440010', 'Refrigeration Systems', 'hvac', 'Commercial refrigeration and cooling systems', true, 3),
('550e8400-e29b-41d4-a716-446655440010', 'Electrical Troubleshooting', 'electrical', 'HVAC electrical system diagnosis and repair', false, 1),
('550e8400-e29b-41d4-a716-446655440010', 'Duct Installation', 'hvac', 'Ductwork design and installation', false, 2),
('550e8400-e29b-41d4-a716-446655440010', 'Heat Pump Systems', 'hvac', 'Heat pump installation and maintenance', false, 3)
ON CONFLICT (business_id, name) DO NOTHING;

-- Technician skills
INSERT INTO technician_skills (
    technician_id, skill_id, proficiency_level, years_experience, is_certified, certification_name
) VALUES
((SELECT id FROM technicians WHERE employee_id = 'EMP001' LIMIT 1),
 (SELECT id FROM skills WHERE name = 'Residential HVAC Repair' LIMIT 1), 'expert', 8, true, 'NATE Certified'),
((SELECT id FROM technicians WHERE employee_id = 'EMP002' LIMIT 1),
 (SELECT id FROM skills WHERE name = 'Commercial HVAC Systems' LIMIT 1), 'advanced', 5, true, 'EPA Section 608'),
((SELECT id FROM technicians WHERE employee_id = 'EMP001' LIMIT 1),
 (SELECT id FROM skills WHERE name = 'Electrical Troubleshooting' LIMIT 1), 'intermediate', 4, false, NULL)
ON CONFLICT (technician_id, skill_id) DO NOTHING;

-- Technician certifications
INSERT INTO technician_certifications (
    technician_id, certification_name, certification_type, issuing_authority,
    certification_number, issue_date, expiration_date, status
) VALUES
('550e8400-e29b-41d4-a716-446655440130', 'NATE Core Certification', 'certification', 'North American Technician Excellence',
 'NATE-2020-001234', '2020-06-15', '2025-06-15', 'active'),
('550e8400-e29b-41d4-a716-446655440131', 'EPA Section 608 Universal', 'license', 'Environmental Protection Agency',
 'EPA-608-567890', '2021-01-20', NULL, 'active')
ON CONFLICT DO NOTHING;

-- =============================================
-- INVENTORY SYSTEM DATA
-- =============================================

-- Suppliers
INSERT INTO suppliers (
    id, business_id, user_id, supplier_code, name, email, phone, 
    billing_address, currency, payment_terms_days, status, supplier_type,
    total_orders, total_spend, is_preferred
) VALUES
('550e8400-e29b-41d4-a716-446655440140', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440005',
 'HVAC001', 'HVAC Parts Plus', 'orders@hvacpartsplus.com', '(800) 555-0100',
 '{"street": "500 Industrial Blvd", "city": "Dallas", "state": "TX", "zip": "75201"}',
 'USD', 30, 'active', 'parts_supplier', 24, 15680.50, true),

('550e8400-e29b-41d4-a716-446655440141', '550e8400-e29b-41d4-a716-446655440010', NULL,
 'EQUIP001', 'Elite Equipment Supply', 'sales@eliteequip.com', '(800) 555-0200',
 '{"street": "1200 Equipment Way", "city": "Houston", "state": "TX", "zip": "77001"}',
 'USD', 15, 'active', 'equipment_supplier', 8, 45200.00, true)
ON CONFLICT (id) DO NOTHING;

-- Inventory locations
INSERT INTO inventory_locations (business_id, name, location_type, address, city, state, zip_code, is_active, is_default) VALUES
('550e8400-e29b-41d4-a716-446655440010', 'Main Warehouse', 'warehouse', '123 Main St', 'Austin', 'TX', '78701', true, true),
('550e8400-e29b-41d4-a716-446655440010', 'Service Truck #1', 'truck', 'Mobile', 'Austin', 'TX', '78701', true, false),
('550e8400-e29b-41d4-a716-446655440010', 'Service Truck #2', 'truck', 'Mobile', 'Austin', 'TX', '78701', true, false)
ON CONFLICT (business_id, name) DO NOTHING;

-- Products (inventory items)
INSERT INTO products (
    id, business_id, name, description, sku, category, price, cost_price,
    track_inventory, inventory_quantity, low_stock_threshold, status, is_featured
) VALUES
('550e8400-e29b-41d4-a716-446655440150', '550e8400-e29b-41d4-a716-446655440010',
 'R-410A Refrigerant (25lb)', 'R-410A refrigerant cylinder for residential AC systems', 'REF-410A-25',
 'Refrigerants', 180.00, 120.00, true, 12, 5, 'active', false),

('550e8400-e29b-41d4-a716-446655440151', '550e8400-e29b-41d4-a716-446655440010',
 'MERV 8 Air Filter 16x25x1', 'Standard efficiency air filter', 'FILT-16X25-M8',
 'Filters', 8.50, 4.25, true, 48, 10, 'active', false),

('550e8400-e29b-41d4-a716-446655440152', '550e8400-e29b-41d4-a716-446655440010',
 'Contactor 30A 24V', 'Single pole contactor for HVAC systems', 'CONT-30A-24V',
 'Electrical', 35.00, 18.50, true, 8, 3, 'active', false),

('550e8400-e29b-41d4-a716-446655440153', '550e8400-e29b-41d4-a716-446655440010',
 'Trane 3-Ton Heat Pump', 'High-efficiency heat pump system 16 SEER', 'TRANE-HP-3TON',
 'Equipment', 4500.00, 3200.00, true, 2, 1, 'active', true)
ON CONFLICT (id) DO NOTHING;

-- Purchase orders
INSERT INTO purchase_orders (
    id, business_id, supplier_id, po_number, order_date, expected_delivery_date,
    status, subtotal, tax_amount, total_amount
) VALUES
('550e8400-e29b-41d4-a716-446655440160', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440140',
 'PO-2023-001', '2023-08-01', '2023-08-05', 'received', 850.00, 70.13, 920.13),

('550e8400-e29b-41d4-a716-446655440161', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440141',
 'PO-2023-002', '2023-08-10', '2023-08-15', 'confirmed', 4500.00, 371.25, 4871.25)
ON CONFLICT (id) DO NOTHING;

-- Purchase order items
INSERT INTO purchase_order_items (
    purchase_order_id, product_id, product_name, quantity_ordered, quantity_received, unit_cost
) VALUES
('550e8400-e29b-41d4-a716-446655440160', '550e8400-e29b-41d4-a716-446655440150', 'R-410A Refrigerant (25lb)', 5, 5, 120.00),
('550e8400-e29b-41d4-a716-446655440160', '550e8400-e29b-41d4-a716-446655440151', 'MERV 8 Air Filter 16x25x1', 24, 24, 4.25),
('550e8400-e29b-41d4-a716-446655440160', '550e8400-e29b-41d4-a716-446655440152', 'Contactor 30A 24V', 10, 10, 18.50),

('550e8400-e29b-41d4-a716-446655440161', '550e8400-e29b-41d4-a716-446655440153', 'Trane 3-Ton Heat Pump', 1, 0, 3200.00)
ON CONFLICT DO NOTHING;

-- =============================================
-- ECOMMERCE SYSTEM DATA
-- =============================================

-- Product categories
INSERT INTO product_categories (business_id, name, slug, description, is_active, display_order) VALUES
('550e8400-e29b-41d4-a716-446655440010', 'HVAC Equipment', 'hvac-equipment', 'Complete HVAC systems and major components', true, 1),
('550e8400-e29b-41d4-a716-446655440010', 'Parts & Components', 'parts-components', 'Replacement parts and system components', true, 2),
('550e8400-e29b-41d4-a716-446655440010', 'Filters & Accessories', 'filters-accessories', 'Air filters and HVAC accessories', true, 3),
('550e8400-e29b-41d4-a716-446655440010', 'Tools & Supplies', 'tools-supplies', 'Professional tools and installation supplies', true, 4)
ON CONFLICT (business_id, slug) DO NOTHING;

-- Shopping carts
INSERT INTO shopping_carts (
    id, business_id, contact_id, session_id, cart_status, customer_email,
    subtotal, tax_amount, total_amount
) VALUES
('550e8400-e29b-41d4-a716-446655440170', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440020',
 NULL, 'active', 'john.smith@example.com', 188.50, 15.55, 204.05),

('550e8400-e29b-41d4-a716-446655440171', '550e8400-e29b-41d4-a716-446655440010', NULL,
 'sess_abc123', 'abandoned', 'visitor@example.com', 35.00, 2.89, 37.89)
ON CONFLICT (id) DO NOTHING;

-- Cart items
INSERT INTO cart_items (
    cart_id, product_type, product_id, product_name, unit_price, quantity, line_total
) VALUES
('550e8400-e29b-41d4-a716-446655440170', 'product', '550e8400-e29b-41d4-a716-446655440150', 'R-410A Refrigerant (25lb)', 180.00, 1, 180.00),
('550e8400-e29b-41d4-a716-446655440170', 'product', '550e8400-e29b-41d4-a716-446655440151', 'MERV 8 Air Filter 16x25x1', 8.50, 1, 8.50),

('550e8400-e29b-41d4-a716-446655440171', 'product', '550e8400-e29b-41d4-a716-446655440152', 'Contactor 30A 24V', 35.00, 1, 35.00)
ON CONFLICT DO NOTHING;

-- =============================================
-- MEMBERSHIP SYSTEM DATA
-- =============================================

-- Customer membership plans
INSERT INTO customer_membership_plans (
    id, business_id, name, plan_type, description, price_monthly, price_yearly,
    discount_percentage, priority_service, maintenance_included, annual_tune_ups, is_active, is_featured
) VALUES
('550e8400-e29b-41d4-a716-446655440180', '550e8400-e29b-41d4-a716-446655440010',
 'Residential Care Plan', 'residential', 'Complete residential HVAC maintenance and priority service',
 29.99, 299.99, 15, true, true, 2, true, true),

('550e8400-e29b-41d4-a716-446655440181', '550e8400-e29b-41d4-a716-446655440010',
 'Commercial Service Plan', 'commercial', 'Comprehensive commercial HVAC maintenance program',
 99.99, 999.99, 20, true, true, 4, true, false)
ON CONFLICT (id) DO NOTHING;

-- Customer subscriptions
INSERT INTO customer_subscriptions (
    id, business_id, contact_id, plan_id, subscription_number, billing_cycle,
    monthly_amount, status, start_date, next_billing_date
) VALUES
('550e8400-e29b-41d4-a716-446655440190', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440020',
 '550e8400-e29b-41d4-a716-446655440180', 'SUB-2023-001', 'monthly', 29.99, 'active', '2023-06-01', '2023-09-01'),

('550e8400-e29b-41d4-a716-446655440191', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440021',
 '550e8400-e29b-41d4-a716-446655440181', 'SUB-2023-002', 'yearly', 999.99, 'active', '2023-07-01', '2024-07-01')
ON CONFLICT (id) DO NOTHING;

-- =============================================
-- MARKETING SYSTEM DATA
-- =============================================

-- Featured projects
INSERT INTO featured_projects (
    id, business_id, title, description, trade, completion_date,
    project_value, location, is_featured, display_order
) VALUES
('550e8400-e29b-41d4-a716-446655440200', '550e8400-e29b-41d4-a716-446655440010',
 'Downtown Office Complex HVAC Upgrade', 'Complete HVAC system replacement for 50,000 sq ft office building',
 'HVAC', '2023-05-15', 85000.00, 'Downtown Austin, TX', true, 1),

('550e8400-e29b-41d4-a716-446655440201', '550e8400-e29b-41d4-a716-446655440010',
 'Luxury Home Heat Pump Installation', 'High-efficiency heat pump system for 4,500 sq ft custom home',
 'HVAC', '2023-06-20', 18500.00, 'West Lake Hills, TX', true, 2),

('550e8400-e29b-41d4-a716-446655440202', '550e8400-e29b-41d4-a716-446655440010',
 'Restaurant Kitchen Ventilation System', 'Commercial kitchen exhaust and HVAC system installation',
 'HVAC', '2023-07-10', 32000.00, 'South Austin, TX', true, 3)
ON CONFLICT (id) DO NOTHING;

-- Testimonials
INSERT INTO testimonials (
    id, business_id, customer_name, customer_title, testimonial_text,
    rating, service_provided, is_featured, display_order
) VALUES
('550e8400-e29b-41d4-a716-446655440210', '550e8400-e29b-41d4-a716-446655440010',
 'John Smith', 'Homeowner', 'Elite HVAC saved the day when our AC died during the summer heat wave. Fast, professional, and reasonably priced!',
 5, 'AC Repair', true, 1),

('550e8400-e29b-41d4-a716-446655440211', '550e8400-e29b-41d4-a716-446655440010',
 'Lisa Brown', 'Property Manager', 'We use Elite HVAC for all our commercial properties. Their maintenance plans keep our systems running smoothly.',
 5, 'HVAC Maintenance', true, 2),

('550e8400-e29b-41d4-a716-446655440212', '550e8400-e29b-41d4-a716-446655440010',
 'Mike Rodriguez', 'Restaurant Owner', 'Professional installation of our kitchen ventilation system. Completed on time and within budget.',
 4, 'Commercial Installation', false, 3)
ON CONFLICT (id) DO NOTHING;

-- Awards & certifications
INSERT INTO awards_certifications (
    id, business_id, title, issuing_organization, issued_date, description,
    type, display_on_website, display_order
) VALUES
('550e8400-e29b-41d4-a716-446655440220', '550e8400-e29b-41d4-a716-446655440010',
 'BBB A+ Rating', 'Better Business Bureau', '2023-01-01', 'Maintained A+ rating for excellent customer service and business practices',
 'award', true, 1),

('550e8400-e29b-41d4-a716-446655440221', '550e8400-e29b-41d4-a716-446655440010',
 'NATE Excellence Award', 'North American Technician Excellence', '2022-12-15', 'Recognition for technical excellence and customer satisfaction',
 'award', true, 2),

('550e8400-e29b-41d4-a716-446655440222', '550e8400-e29b-41d4-a716-446655440010',
 'Austin Chamber of Commerce Member', 'Austin Chamber of Commerce', '2020-01-01', 'Active member supporting local business community',
 'membership', false, 3)
ON CONFLICT (id) DO NOTHING;

-- =============================================
-- WEBSITE BUILDER DEMO DATA
-- =============================================

-- Enhanced Business Services for Website Builder Testing
INSERT INTO business_services (business_id, service_name, service_slug, category, description, price_type, price_min, price_max, price_unit) VALUES
-- Core HVAC Services
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 'AC Repair', 'ac-repair', 'Repair', 'Emergency air conditioning repair and diagnostics', 'range', 150, 800, 'job'),
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 'Heating Repair', 'heating-repair', 'Repair', 'Furnace and heating system repair services', 'range', 175, 900, 'job'),
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 'HVAC Installation', 'hvac-installation', 'Installation', 'Complete HVAC system installation and replacement', 'range', 3500, 12000, 'job'),
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 'Duct Cleaning', 'duct-cleaning', 'Maintenance', 'Professional air duct cleaning and sanitization', 'range', 200, 600, 'job'),
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 'Preventive Maintenance', 'preventive-maintenance', 'Maintenance', 'Seasonal HVAC tune-ups and maintenance', 'range', 120, 250, 'job'),
-- Additional Services
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 'Indoor Air Quality', 'indoor-air-quality', 'Installation', 'Air purification and filtration system installation', 'range', 500, 2500, 'job'),
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 'Thermostat Installation', 'thermostat-installation', 'Installation', 'Smart and programmable thermostat installation', 'range', 150, 400, 'job'),
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 'Emergency Service', 'emergency-service', 'Emergency', '24/7 emergency HVAC repair services', 'range', 200, 1200, 'job')
ON CONFLICT (business_id, service_slug) DO NOTHING;

-- Enhanced Business Locations for Multi-Location SEO Testing
INSERT INTO business_locations (business_id, name, address, city, state, zip_code, is_primary, service_radius) VALUES
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 'Austin Main Office', '123 Main St', 'Austin', 'TX', '78701', true, 25),
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 'Round Rock Branch', '456 Round Rock Ave', 'Round Rock', 'TX', '78664', false, 20),
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 'Cedar Park Office', '789 Cedar Park Blvd', 'Cedar Park', 'TX', '78613', false, 15);

-- Enhanced Featured Projects for Website Builder
INSERT INTO featured_projects (
    business_id, title, description, trade, completion_date, project_value, 
    gallery_images, before_images, after_images, location, is_featured, display_order,
    project_duration, challenges_faced, solutions_provided, equipment_installed,
    warranty_info, tags, slug, seo_slug, customer_name, customer_testimonial
) VALUES
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 
 'Luxury Home HVAC System', 
 'Complete HVAC system installation for 4,500 sq ft luxury home with zoned climate control', 
 'HVAC', '2024-01-15', 15000.00, 
 '{"https://example.com/project1.jpg"}', 
 '{"https://example.com/before1.jpg"}', 
 '{"https://example.com/after1.jpg"}', 
 'West Lake Hills, TX', true, 1,
 '5 days',
 '{"Old system inefficient", "Complex zoning requirements"}',
 '{"High-efficiency system installation", "Smart zoning controls"}',
 '{"Carrier 19VS Heat Pump", "Ecobee Smart Thermostats", "Zoning dampers"}',
 '10-year manufacturer warranty, 2-year labor warranty',
 '{"luxury-home", "zoned-hvac", "energy-efficient"}',
 'luxury-home-hvac-system',
 'luxury-home-hvac-system',
 'Sarah Johnson',
 'Elite HVAC transformed our home comfort. The zoned system is perfect for our large home.'),

((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 
 'Commercial Office Building', 
 'Multi-zone HVAC system for 20,000 sq ft office complex with energy-efficient design', 
 'HVAC', '2023-12-10', 45000.00, 
 '{"https://example.com/project2.jpg"}', 
 '{"https://example.com/before2.jpg"}', 
 '{"https://example.com/after2.jpg"}', 
 'Downtown Austin, TX', true, 2,
 '2 weeks',
 '{"Outdated system", "High energy costs", "Uneven temperatures"}',
 '{"Variable refrigerant flow system", "Smart controls", "Energy recovery"}',
 '{"Daikin VRV System", "Building automation system", "Energy recovery ventilators"}',
 '5-year comprehensive warranty',
 '{"commercial", "office-building", "energy-efficient", "vrf"}',
 'commercial-office-building-hvac',
 'commercial-office-building-hvac',
 'Mike Chen',
 'Professional installation with minimal disruption to our business operations.'),

((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 
 'Emergency AC Repair', 
 'Emergency repair of commercial AC system during Texas heat wave, completed in 4 hours', 
 'HVAC', '2024-01-20', 2800.00, 
 '{"https://example.com/project3.jpg"}', 
 '{"https://example.com/before3.jpg"}', 
 '{"https://example.com/after3.jpg"}', 
 'South Austin, TX', true, 3,
 '4 hours',
 '{"System failure during heat wave", "Urgent timeline", "Parts availability"}',
 '{"Emergency parts sourcing", "Rapid diagnosis", "Same-day repair"}',
 '{"Compressor replacement", "Refrigerant recharge", "Control board"}',
 '1-year warranty on parts and labor',
 '{"emergency-repair", "commercial", "same-day"}',
 'emergency-ac-repair-heat-wave',
 'emergency-ac-repair-heat-wave',
 'Restaurant Manager',
 'They saved our business! AC fixed in 4 hours during the hottest day of summer.'),

((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 
 'Smart Home Integration', 
 'Integration of smart thermostats and air quality monitoring for modern home', 
 'HVAC', '2024-01-05', 3200.00, 
 '{"https://example.com/project4.jpg"}', 
 '{"https://example.com/before4.jpg"}', 
 '{"https://example.com/after4.jpg"}', 
 'Mueller, Austin, TX', false, 4,
 '1 day',
 '{"Legacy thermostat", "No air quality monitoring", "Manual controls"}',
 '{"Smart thermostat installation", "Air quality sensors", "Mobile app integration"}',
 '{"Nest Learning Thermostat", "Air quality monitors", "Smart vents"}',
 '2-year warranty on smart devices',
 '{"smart-home", "automation", "air-quality"}',
 'smart-home-integration',
 'smart-home-integration',
 'Tech Enthusiast',
 'Love the smart controls and air quality monitoring. Very professional installation.');

-- Enhanced Business Branding for Website Builder
INSERT INTO business_branding (business_id, name, description, color_scheme, typography, assets, website_settings) VALUES
((SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1), 'Elite HVAC Austin', 'Professional HVAC services with 24/7 emergency support',
'{
    "primary": "#1E40AF",
    "secondary": "#DC2626", 
    "accent": "#0EA5E9",
    "neutral": "#6B7280",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444"
}',
'{
    "heading": "Inter",
    "body": "Inter",
    "accent": "Inter"
}',
'{
    "logo_url": "https://example.com/elite-hvac-logo.png",
    "favicon_url": "https://example.com/favicon.ico",
    "hero_image": "https://example.com/hero-hvac.jpg"
}',
'{
    "tagline": "Your Comfort, Our Priority",
    "value_proposition": "Professional HVAC services with 24/7 emergency support",
    "key_benefits": ["Licensed & Insured", "24/7 Emergency Service", "Same Day Service", "Free Estimates"],
    "brand_voice": {
        "tone": "professional",
        "personality": ["trustworthy", "reliable", "expert", "responsive"],
        "communication_style": "clear and direct"
    }
}'
)
ON CONFLICT (business_id) DO NOTHING;

-- Website Configurations for Demo Business
INSERT INTO website_configurations (business_id, subdomain, deployment_status, enabled_pages, seo_config, content_overrides, monthly_conversions, estimated_monthly_revenue) VALUES
(
    (SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1),
    'elite-hvac-austin',
    'deployed',
    '{
        "home": true,
        "services": true,
        "projects": true,
        "contact": true,
        "about": true,
        "booking": true,
        "products": false,
        "pricing": false,
        "locations": ["austin-tx", "round-rock-tx", "cedar-park-tx"]
    }',
    '{
        "title_template": "HVAC Services in {city} | Elite HVAC Austin",
        "meta_description": "Professional HVAC services in Austin, TX. Licensed, insured, 24/7 emergency service. Same day repairs and installations.",
        "keywords": ["hvac", "austin", "emergency", "repair", "installation", "maintenance", "licensed", "insured"],
        "business_schema": {
            "@type": "LocalBusiness",
            "name": "Elite HVAC Austin",
            "telephone": "(512) 555-0100",
            "address": {
                "streetAddress": "123 Main St",
                "addressLocality": "Austin",
                "addressRegion": "TX",
                "postalCode": "78701"
            }
        }
    }',
    '{}',
    45,
    6750.00
)
ON CONFLICT (business_id) DO NOTHING;

-- Note: website_pages table removed in simplified website builder
-- Pages are now generated dynamically based on enabled_pages configuration

-- Website Conversions Demo Data
INSERT INTO website_conversions (business_id, conversion_type, conversion_value, source_page, visitor_data, conversion_data, created_at) VALUES
-- Elite HVAC Austin conversions
(
    (SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1),
    'phone_call',
    450.00,
    '/',
    '{"userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)", "referrer": "https://google.com", "trafficSource": "organic"}',
    '{"contact_info": {"phone": "(512) 555-1234", "service_needed": "AC Repair"}}',
    NOW() - INTERVAL '2 days'
),
(
    (SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1),
    'form_submit',
    850.00,
    '/services',
    '{"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "referrer": "https://facebook.com", "trafficSource": "social"}',
    '{"contact_info": {"name": "Sarah Johnson", "phone": "(512) 555-5678", "email": "sarah@example.com", "service_needed": "AC Installation"}}',
    NOW() - INTERVAL '1 day'
),
(
    (SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1),
    'booking',
    200.00,
    '/booking',
    '{"userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "referrer": "", "trafficSource": "direct"}',
    '{"contact_info": {"name": "Mike Chen", "phone": "(512) 555-9012", "service_needed": "Maintenance"}}',
    NOW() - INTERVAL '6 hours'
),
(
    (SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1),
    'phone_call',
    320.00,
    '/',
    '{"userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)", "referrer": "https://google.com", "trafficSource": "organic"}',
    '{"contact_info": {"phone": "(512) 555-3456", "service_needed": "Emergency Repair"}}',
    NOW() - INTERVAL '3 days'
),
(
    (SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1),
    'form_submit',
    180.00,
    '/contact',
    '{"userAgent": "Mozilla/5.0 (Android 12; Mobile)", "referrer": "https://bing.com", "trafficSource": "organic"}',
    '{"contact_info": {"name": "Lisa Rodriguez", "phone": "(512) 555-7890", "email": "lisa@example.com", "service_needed": "Maintenance Check"}}',
    NOW() - INTERVAL '12 hours'
)
ON CONFLICT DO NOTHING;

COMMIT;