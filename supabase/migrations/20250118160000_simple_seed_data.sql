-- Simple seed data for testing the website builder system
-- This focuses on the essential data needed for API testing

-- Insert a test user
INSERT INTO users (id, email, full_name, display_name, phone, is_active, created_at, updated_at) 
VALUES (
    'a1b2c3d4-e5f6-7890-1234-567890abcdef', 
    'mike@austinelitehvac.com', 
    'Mike Johnson',
    'Mike Johnson', 
    '(512) 555-COOL', 
    true, 
    NOW(), 
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Insert a test business
INSERT INTO businesses (
    id, 
    name, 
    industry, 
    company_size, 
    business_address, 
    city, 
    state, 
    postal_code, 
    country, 
    phone_number, 
    business_email, 
    website, 
    description, 
    is_active,
    created_date, 
    last_modified
) VALUES (
    'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    'Austin Elite HVAC',
    'HVAC',
    'SMALL',
    '123 Main St',
    'Austin',
    'TX',
    '78701',
    'US',
    '(512) 555-COOL',
    'info@austinelitehvac.com',
    'https://www.austinelitehvac.com',
    'Premier HVAC services for Austin homes and businesses. Specializing in energy-efficient installations, emergency repairs, and preventative maintenance.',
    true,
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Insert some product categories if the table exists
INSERT INTO product_categories (id, business_id, name, description, created_at, updated_at) 
VALUES 
    (gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'HVAC Systems', 'Complete heating, ventilation, and air conditioning systems', NOW(), NOW()),
    (gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'Thermostats', 'Smart and traditional thermostats for climate control', NOW(), NOW()),
    (gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'Air Filters', 'High-efficiency air filtration systems', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Skip products for now since they require category references

-- Insert some calendar events for availability if the table exists
INSERT INTO calendar_events (id, user_id, business_id, title, description, start_datetime, end_datetime, event_type, is_active, created_date, last_modified) 
VALUES 
    (gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'Available for Service Calls', 'Open slot for HVAC service appointments', '2025-01-19 09:00:00', '2025-01-19 10:00:00', 'AVAILABLE', true, NOW(), NOW()),
    (gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'Available for Service Calls', 'Open slot for HVAC service appointments', '2025-01-19 10:00:00', '2025-01-19 11:00:00', 'AVAILABLE', true, NOW(), NOW()),
    (gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'Available for Service Calls', 'Open slot for HVAC service appointments', '2025-01-19 14:00:00', '2025-01-19 15:00:00', 'AVAILABLE', true, NOW(), NOW()),
    (gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'Available for Service Calls', 'Open slot for HVAC service appointments', '2025-01-20 09:00:00', '2025-01-20 10:00:00', 'AVAILABLE', true, NOW(), NOW()),
    (gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'Available for Service Calls', 'Open slot for HVAC service appointments', '2025-01-20 11:00:00', '2025-01-20 12:00:00', 'AVAILABLE', true, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

SELECT 'Simple seed data inserted successfully!' as message;
