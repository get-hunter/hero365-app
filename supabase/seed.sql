-- Seed data for local development
-- This file contains sample data for testing the Hero365 application locally

-- Sample businesses
INSERT INTO businesses (
    id,
    name,
    industry,
    company_size,
    owner_id,
    description,
    phone_number,
    business_address,
    business_email,
    onboarding_completed,
    timezone,
    currency,
    is_active
) VALUES 
(
    '123e4567-e89b-12d3-a456-426614174000',
    'Demo Plumbing Services',
    'plumbing',
    'small',
    'user_test_123',
    'A demo plumbing business for testing purposes',
    '+1-555-123-4567',
    '123 Main St, Anytown, USA 12345',
    'demo@demoplumbing.com',
    true,
    'America/New_York',
    'USD',
    true
),
(
    '123e4567-e89b-12d3-a456-426614174001',
    'Elite HVAC Solutions',
    'hvac',
    'medium',
    'user_test_456',
    'Premium heating and cooling services',
    '+1-555-987-6543',
    '456 Business Ave, Enterprise City, USA 54321',
    'contact@elitehvac.com',
    true,
    'America/Los_Angeles',
    'USD',
    true
);

-- Sample business memberships
INSERT INTO business_memberships (
    id,
    business_id,
    user_id,
    role,
    permissions,
    joined_date,
    is_active
) VALUES 
(
    '223e4567-e89b-12d3-a456-426614174000',
    '123e4567-e89b-12d3-a456-426614174000',
    'user_test_123',
    'owner',
    '["manage_business", "manage_team", "manage_finances", "view_analytics"]'::jsonb,
    now(),
    true
),
(
    '223e4567-e89b-12d3-a456-426614174001',
    '123e4567-e89b-12d3-a456-426614174001',
    'user_test_456',
    'owner',
    '["manage_business", "manage_team", "manage_finances", "view_analytics"]'::jsonb,
    now(),
    true
),
(
    '223e4567-e89b-12d3-a456-426614174002',
    '123e4567-e89b-12d3-a456-426614174000',
    'user_test_789',
    'employee',
    '["view_jobs", "manage_own_schedule", "submit_timesheets"]'::jsonb,
    now(),
    true
);

-- Sample business invitations
INSERT INTO business_invitations (
    id,
    business_id,
    business_name,
    invited_email,
    invited_by,
    invited_by_name,
    role,
    permissions,
    invitation_date,
    expiry_date,
    status,
    message
) VALUES 
(
    '323e4567-e89b-12d3-a456-426614174000',
    '123e4567-e89b-12d3-a456-426614174000',
    'Demo Plumbing Services',
    'newemployee@example.com',
    'user_test_123',
    'John Demo',
    'employee',
    '["view_jobs", "manage_own_schedule"]'::jsonb,
    now(),
    now() + interval '7 days',
    'pending',
    'Welcome to Demo Plumbing Services! We are excited to have you join our team.'
);

-- Sample departments
INSERT INTO departments (
    id,
    business_id,
    name,
    description,
    manager_id,
    is_active
) VALUES 
(
    '423e4567-e89b-12d3-a456-426614174000',
    '123e4567-e89b-12d3-a456-426614174000',
    'Field Operations',
    'On-site plumbing services and installations',
    'user_test_123',
    true
),
(
    '423e4567-e89b-12d3-a456-426614174001',
    '123e4567-e89b-12d3-a456-426614174001',
    'HVAC Installation',
    'Heating and cooling system installations',
    'user_test_456',
    true
),
(
    '423e4567-e89b-12d3-a456-426614174002',
    '123e4567-e89b-12d3-a456-426614174001',
    'Customer Service',
    'Customer support and scheduling',
    'user_test_456',
    true
);

-- Add comments for documentation
COMMENT ON TABLE businesses IS 'Sample businesses for local development testing';
COMMENT ON TABLE business_memberships IS 'Sample team members for testing business functionality';
COMMENT ON TABLE business_invitations IS 'Sample pending invitations for testing invitation workflow';
COMMENT ON TABLE departments IS 'Sample departments for testing organizational structure'; 