-- Comprehensive Mock Data Population for Hero365 Home Services ERP
-- This file contains realistic sample data for all entities in the system

-- Clear existing data (be careful in production!)
TRUNCATE TABLE 
    activity_reminders,
    activity_participants,
    activities,
    job_notes,
    job_activities,
    jobs,
    contact_notes,
    contact_activities,
    contact_segment_memberships,
    contact_segments,
    contacts,
    availability_windows,
    workload_capacity,
    user_skills,
    user_certifications,
    user_capabilities,
    time_off_requests,
    calendar_preferences,
    calendar_events,
    working_hours_templates,
    business_invitations,
    business_memberships,
    departments,
    businesses
CASCADE;

-- Reset sequences if needed
-- (Note: UUIDs don't use sequences, but keeping this pattern for completeness)

-- =============================================
-- BUSINESSES
-- =============================================
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
    'Elite Plumbing Services',
    'plumbing',
    'small',
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    'Premier residential and commercial plumbing services with 24/7 emergency support',
    '+1-555-123-4567',
    '123 Main St, Austin, TX 78701',
    'contact@eliteplumbing.com',
    true,
    'America/Chicago',
    'USD',
    true
);

-- =============================================
-- DEPARTMENTS
-- =============================================
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
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    true
),
(
    '423e4567-e89b-12d3-a456-426614174001',
    '123e4567-e89b-12d3-a456-426614174000',
    'Emergency Services',
    '24/7 emergency plumbing response team',
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    true
),
(
    '423e4567-e89b-12d3-a456-426614174002',
    '123e4567-e89b-12d3-a456-426614174000',
    'Commercial Services',
    'Large-scale commercial plumbing projects',
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    true
);

-- =============================================
-- BUSINESS MEMBERSHIPS
-- =============================================
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
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    'owner',
    '["view_contacts", "create_contacts", "edit_contacts", "delete_contacts", "view_jobs", "create_jobs", "edit_jobs", "delete_jobs", "edit_business_profile", "view_business_settings", "edit_business_settings", "invite_team_members", "edit_team_members", "remove_team_members", "view_invoices", "create_invoices", "edit_invoices", "delete_invoices", "view_reports", "edit_reports", "view_accounting", "edit_accounting"]'::jsonb,
    now() - interval '2 years',
    true
);

-- =============================================
-- BUSINESS INVITATIONS
-- =============================================
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
    'Elite Plumbing Services',
    'newtech@example.com',
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    'Mike Johnson',
    'employee',
    '["view_contacts", "create_contacts", "edit_contacts", "view_jobs", "create_jobs", "edit_jobs"]'::jsonb,
    now() - interval '2 days',
    now() + interval '5 days',
    'pending',
    'Join our growing plumbing services team! We offer competitive pay and excellent benefits.'
),
(
    '323e4567-e89b-12d3-a456-426614174001',
    '123e4567-e89b-12d3-a456-426614174000',
    'Elite Plumbing Services',
    'seniorplumber@example.com',
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    'Mike Johnson',
    'employee',
    '["view_contacts", "create_contacts", "edit_contacts", "view_jobs", "create_jobs", "edit_jobs"]'::jsonb,
    now() - interval '1 day',
    now() + interval '6 days',
    'pending',
    'We are looking for experienced plumbers to join our emergency services team.'
);

-- =============================================
-- WORKING HOURS TEMPLATES
-- =============================================
INSERT INTO working_hours_templates (
    id,
    name,
    description,
    monday_start, monday_end,
    tuesday_start, tuesday_end,
    wednesday_start, wednesday_end,
    thursday_start, thursday_end,
    friday_start, friday_end,
    saturday_start, saturday_end,
    sunday_start, sunday_end,
    break_duration_minutes,
    lunch_start_time,
    lunch_duration_minutes,
    allows_flexible_start,
    flexible_start_window_minutes,
    allows_overtime,
    max_overtime_hours_per_day,
    is_active
) VALUES 
(
    '624e4567-e89b-12d3-a456-426614174000',
    'Standard Business Hours',
    'Monday to Friday 8 AM to 5 PM with lunch break',
    '08:00', '17:00',
    '08:00', '17:00',
    '08:00', '17:00',
    '08:00', '17:00',
    '08:00', '17:00',
    NULL, NULL,
    NULL, NULL,
    30,
    '12:00',
    60,
    true,
    30,
    true,
    2.0,
    true
),
(
    '624e4567-e89b-12d3-a456-426614174001',
    'Emergency Service Hours',
    '24/7 emergency service schedule',
    '00:00', '23:59',
    '00:00', '23:59',
    '00:00', '23:59',
    '00:00', '23:59',
    '00:00', '23:59',
    '00:00', '23:59',
    '00:00', '23:59',
    30,
    NULL,
    30,
    false,
    0,
    true,
    4.0,
    true
),
(
    '624e4567-e89b-12d3-a456-426614174002',
    'Extended Hours',
    'Monday to Saturday 7 AM to 7 PM',
    '07:00', '19:00',
    '07:00', '19:00',
    '07:00', '19:00',
    '07:00', '19:00',
    '07:00', '19:00',
    '08:00', '16:00',
    NULL, NULL,
    30,
    '12:30',
    45,
    true,
    45,
    true,
    3.0,
    true
);

-- =============================================
-- USER CAPABILITIES
-- =============================================
INSERT INTO user_capabilities (
    id,
    business_id,
    user_id,
    home_base_address,
    home_base_latitude,
    home_base_longitude,
    vehicle_type,
    has_vehicle,
    preferred_start_time,
    preferred_end_time,
    min_time_between_jobs_minutes,
    max_commute_time_minutes,
    average_job_rating,
    completion_rate,
    punctuality_score,
    working_hours_template_id,
    is_active
) VALUES 
(
    '724e4567-e89b-12d3-a456-426614174000',
    '123e4567-e89b-12d3-a456-426614174000',
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    '123 Main St, Austin, TX 78701',
    30.2672, -97.7431,
    'service_van',
    true,
    '07:00',
    '18:00',
    45,
    75,
    4.8,
    98.5,
    96.2,
    '624e4567-e89b-12d3-a456-426614174000',
    true
);

-- =============================================
-- USER SKILLS
-- =============================================
INSERT INTO user_skills (
    id,
    user_capabilities_id,
    skill_id,
    name,
    category,
    level,
    years_experience,
    last_used,
    proficiency_score,
    certification_required
) VALUES 
-- Mike Johnson (Owner - Elite Plumbing) Skills
(
    '824e4567-e89b-12d3-a456-426614174000',
    '724e4567-e89b-12d3-a456-426614174000',
    'residential_plumbing',
    'Residential Plumbing',
    'plumbing',
    'expert',
    15.0,
    now() - interval '1 day',
    95.8,
    true
),
(
    '824e4567-e89b-12d3-a456-426614174001',
    '724e4567-e89b-12d3-a456-426614174000',
    'commercial_plumbing',
    'Commercial Plumbing',
    'plumbing',
    'expert',
    12.0,
    now() - interval '3 days',
    92.4,
    true
),
(
    '824e4567-e89b-12d3-a456-426614174002',
    '724e4567-e89b-12d3-a456-426614174000',
    'drain_cleaning',
    'Drain Cleaning & Sewer',
    'plumbing',
    'expert',
    15.0,
    now() - interval '2 days',
    98.2,
    false
),
(
    '824e4567-e89b-12d3-a456-426614174003',
    '724e4567-e89b-12d3-a456-426614174000',
    'emergency_repair',
    'Emergency Plumbing Repair',
    'plumbing',
    'expert',
    8.0,
    now() - interval '1 day',
    96.5,
    true
),
(
    '824e4567-e89b-12d3-a456-426614174004',
    '724e4567-e89b-12d3-a456-426614174000',
    'pipe_repair',
    'Pipe Installation & Repair',
    'plumbing',
    'expert',
    10.0,
    now() - interval '2 days',
    94.7,
    true
),
(
    '824e4567-e89b-12d3-a456-426614174005',
    '724e4567-e89b-12d3-a456-426614174000',
    'water_heater_service',
    'Water Heater Installation & Service',
    'plumbing',
    'expert',
    12.0,
    now() - interval '4 days',
    93.8,
    true
),
(
    '824e4567-e89b-12d3-a456-426614174006',
    '724e4567-e89b-12d3-a456-426614174000',
    'backflow_prevention',
    'Backflow Prevention & Testing',
    'plumbing',
    'advanced',
    6.0,
    now() - interval '7 days',
    88.5,
    true
);

-- =============================================
-- USER CERTIFICATIONS
-- =============================================
INSERT INTO user_certifications (
    id,
    user_capabilities_id,
    certification_id,
    name,
    issuing_authority,
    issue_date,
    expiry_date,
    status,
    verification_number,
    renewal_required
) VALUES 
(
    '924e4567-e89b-12d3-a456-426614174000',
    '724e4567-e89b-12d3-a456-426614174000',
    'MP-2024-001',
    'Master Plumber License',
    'Texas State Board of Plumbing Examiners',
    '2020-01-15',
    '2025-01-15',
    'active',
    'TX-MP-12345',
    true
),
(
    '924e4567-e89b-12d3-a456-426614174001',
    '724e4567-e89b-12d3-a456-426614174000',
    'BP-2024-001',
    'Backflow Prevention Assembly Tester',
    'Texas Commission on Environmental Quality',
    '2021-05-10',
    '2025-05-10',
    'active',
    'TX-BPT-67890',
    true
);

-- =============================================
-- CONTACTS
-- =============================================
INSERT INTO contacts (
    id,
    business_id,
    contact_type,
    status,
    first_name,
    last_name,
    company_name,
    job_title,
    email,
    phone,
    mobile_phone,
    website,
    address,
    priority,
    source,
    tags,
    notes,
    estimated_value,
    currency,
    assigned_to,
    created_by,
    custom_fields,
    last_contacted
) VALUES 
-- Elite Plumbing Services contacts
(
    '524e4567-e89b-12d3-a456-426614174000',
    '123e4567-e89b-12d3-a456-426614174000',
    'customer',
    'active',
    'John',
    'Smith',
    NULL,
    NULL,
    'john.smith@email.com',
    '+1-512-555-0101',
    '+1-512-555-0102',
    NULL,
    '{
        "street_address": "1234 Residential Way",
        "city": "Austin",
        "state": "TX",
        "postal_code": "78701",
        "country": "US"
    }'::jsonb,
    'high',
    'website',
    '["repeat_customer", "emergency_service"]'::jsonb,
    'Loyal customer since 2019. Has requested emergency services multiple times.',
    2500.00,
    'USD',
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    '{"preferred_contact_method": "phone", "payment_terms": "net_30"}'::jsonb,
    now() - interval '5 days'
),
(
    '524e4567-e89b-12d3-a456-426614174001',
    '123e4567-e89b-12d3-a456-426614174000',
    'lead',
    'active',
    'Sarah',
    'Johnson',
    'Austin Home Builders',
    'Project Manager',
    'sarah.j@austinhomes.com',
    '+1-512-555-0201',
    '+1-512-555-0202',
    'www.austinhomebuilders.com',
    '{
        "street_address": "5678 Commercial Blvd",
        "city": "Austin",
        "state": "TX",
        "postal_code": "78704",
        "country": "US"
    }'::jsonb,
    'urgent',
    'referral',
    '["commercial", "new_construction"]'::jsonb,
    'Large commercial project opportunity. Multiple buildings planned.',
    15000.00,
    'USD',
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    '{"project_timeline": "Q2_2024", "budget_range": "10000-20000"}'::jsonb,
    now() - interval '2 days'
),
(
    '524e4567-e89b-12d3-a456-426614174002',
    '123e4567-e89b-12d3-a456-426614174000',
    'prospect',
    'active',
    'Mike',
    'Davis',
    NULL,
    NULL,
    'mike.davis@email.com',
    '+1-512-555-0301',
    NULL,
    NULL,
    '{
        "street_address": "9012 Family Lane",
        "city": "Austin",
        "state": "TX",
        "postal_code": "78702",
        "country": "US"
    }'::jsonb,
    'medium',
    'advertising',
    '["bathroom_remodel"]'::jsonb,
    'Interested in bathroom renovation. Wants to schedule consultation.',
    3500.00,
    'USD',
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    '{"interest_level": "high", "timeline": "flexible"}'::jsonb,
    NULL
),
(
    '524e4567-e89b-12d3-a456-426614174003',
    '123e4567-e89b-12d3-a456-426614174000',
    'customer',
    'active',
    'Lisa',
    'Martinez',
    'Austin Office Complex',
    'Facilities Manager',
    'lisa.m@austinoffice.com',
    '+1-512-555-0401',
    '+1-512-555-0402',
    'www.austinofficecomplex.com',
    '{
        "street_address": "2468 Business Park Dr",
        "city": "Austin",
        "state": "TX",
        "postal_code": "78705",
        "country": "US"
    }'::jsonb,
    'high',
    'existing_customer',
    '["commercial", "maintenance_contract"]'::jsonb,
    'Annual maintenance contract customer. Multiple office buildings.',
    8000.00,
    'USD',
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    '{"contract_renewal": "2024-06-01", "buildings_count": 3}'::jsonb,
    now() - interval '10 days'
),
(
    '524e4567-e89b-12d3-a456-426614174004',
    '123e4567-e89b-12d3-a456-426614174000',
    'customer',
    'active',
    'Robert',
    'Chen',
    NULL,
    NULL,
    'robert.chen@email.com',
    '+1-512-555-0501',
    '+1-512-555-0502',
    NULL,
    '{
        "street_address": "3456 Suburban St",
        "city": "Austin",
        "state": "TX",
        "postal_code": "78703",
        "country": "US"
    }'::jsonb,
    'medium',
    'referral',
    '["water_heater", "residential"]'::jsonb,
    'Needs water heater replacement and pipe upgrades.',
    1800.00,
    'USD',
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid,
    '{"home_age": "1985", "last_service": "2023-03-15"}'::jsonb,
    now() - interval '7 days'
);

-- =============================================
-- CONTACT SEGMENTS
-- =============================================
INSERT INTO contact_segments (
    id,
    business_id,
    name,
    description,
    segment_type,
    criteria,
    color,
    is_active,
    created_by
) VALUES 
(
    '024e4567-e89b-12d3-a456-426614174000',
    '123e4567-e89b-12d3-a456-426614174000',
    'Emergency Service Customers',
    'Customers who frequently use emergency services',
    'manual',
    '{"tags": ["emergency_service"], "priority": ["high", "urgent"]}'::jsonb,
    '#FF4444',
    true,
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid
),
(
    '024e4567-e89b-12d3-a456-426614174001',
    '123e4567-e89b-12d3-a456-426614174000',
    'Commercial Clients',
    'Business and commercial property contacts',
    'dynamic',
    '{"tags": ["commercial"], "estimated_value": {"min": 5000}}'::jsonb,
    '#4444FF',
    true,
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid
),
(
    '024e4567-e89b-12d3-a456-426614174002',
    '123e4567-e89b-12d3-a456-426614174000',
    'Maintenance Contract Customers',
    'Customers with ongoing maintenance agreements',
    'imported',
    '{"tags": ["maintenance_contract"]}'::jsonb,
    '#44FF44',
    true,
    '37b3ac03-de02-41e0-b8f0-15a1b47980b0'::uuid
);

-- Add comments for documentation
COMMENT ON TABLE businesses IS 'Home services business for comprehensive testing';
COMMENT ON TABLE contacts IS 'Customer contacts across different stages and service types';
COMMENT ON TABLE user_capabilities IS 'Technician capabilities and scheduling preferences';
COMMENT ON TABLE user_skills IS 'Professional skills and certifications for team members'; 