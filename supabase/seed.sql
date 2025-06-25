-- Hero365 Complete Demo Data Seed
-- Creates one complete business with realistic demo data for all tables

-- Clear all existing data first (in reverse dependency order)
TRUNCATE TABLE 
    activity_reminders,
    activity_participants,
    activity_templates,
    calendar_preferences,
    calendar_events,
    job_attachments,
    job_notes,
    job_activities,
    job_templates,
    contact_notes,
    contact_activities,
    contact_segment_memberships,
    contact_segments,
    activities,
    jobs,
    contacts,
    user_capabilities,
    working_hours_templates,
    business_invitations,
    business_memberships,
    departments,
    businesses,
    users
CASCADE;

-- 1. Create Users (using proper UUIDs)
INSERT INTO public.users (
    id,
    email,
    full_name,
    display_name,
    phone,
    is_active,
    created_at
) VALUES 
-- Business Owner
(
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    'mike@eliteplumbing.com',
    'Mike Johnson',
    'Mike Johnson',
    '+1-512-555-1000',
    true,
    now() - interval '1 year'
),
-- Field Manager
(
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    'sarah@eliteplumbing.com',
    'Sarah Wilson',
    'Sarah Wilson',
    '+1-512-555-1001',
    true,
    now() - interval '6 months'
),
-- Senior Technician
(
    '550e8400-e29b-41d4-a716-446655440003'::uuid,
    'david@eliteplumbing.com',
    'David Chen',
    'David Chen',
    '+1-512-555-1002',
    true,
    now() - interval '3 months'
),
-- Office Administrator
(
    '550e8400-e29b-41d4-a716-446655440004'::uuid,
    'jennifer@eliteplumbing.com',
    'Jennifer Garcia',
    'Jennifer Garcia',
    '+1-512-555-1003',
    true,
    now() - interval '8 months'
),
-- Junior Technician
(
    '550e8400-e29b-41d4-a716-446655440005'::uuid,
    'alex@eliteplumbing.com',
    'Alex Thompson',
    'Alex Thompson',
    '+1-512-555-1004',
    true,
    now() - interval '2 months'
);

-- 2. Create Business
INSERT INTO businesses (
    id,
    name,
    display_name,
    description,
    industry,
    company_size,
    owner_id,
    phone,
    email,
    address,
    city,
    state,
    postal_code,
    country,
    timezone,
    onboarding_completed,
    is_active
) VALUES (
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Elite Plumbing Services',
    'Elite Plumbing',
    'Premier residential and commercial plumbing services with 24/7 emergency support',
    'plumbing',
    'small',
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    '+1-512-555-PIPE',
    'contact@eliteplumbing.com',
    '123 Main St',
    'Austin',
    'TX',
    '78701',
    'US',
    'America/Chicago',
    true,
    true
);

-- 3. Create Departments
INSERT INTO departments (
    id,
    business_id,
    name,
    description,
    manager_id,
    is_active
) VALUES 
(
    '770e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Field Operations',
    'On-site plumbing services and installations',
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    true
),
(
    '770e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Emergency Services',
    '24/7 emergency plumbing response team',
    '550e8400-e29b-41d4-a716-446655440003'::uuid,
    true
),
(
    '770e8400-e29b-41d4-a716-446655440003'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Administration',
    'Office management and customer service',
    '550e8400-e29b-41d4-a716-446655440004'::uuid,
    true
);

-- 4. Create Business Memberships
INSERT INTO business_memberships (
    id,
    business_id,
    user_id,
    role,
    permissions,
    joined_date,
    department_id,
    job_title,
    is_active
) VALUES 
-- Owner
(
    '880e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    'owner',
    '["*"]'::jsonb,
    now() - interval '1 year',
    '770e8400-e29b-41d4-a716-446655440003'::uuid,
    'CEO & Founder',
    true
),
-- Field Manager
(
    '880e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    'manager',
    '["view_team_members", "manage_contacts", "view_contacts", "manage_jobs", "view_jobs", "manage_activities", "view_activities"]'::jsonb,
    now() - interval '6 months',
    '770e8400-e29b-41d4-a716-446655440001'::uuid,
    'Field Operations Manager',
    true
),
-- Senior Technician
(
    '880e8400-e29b-41d4-a716-446655440003'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    '550e8400-e29b-41d4-a716-446655440003'::uuid,
    'employee',
    '["view_contacts", "manage_own_jobs", "view_jobs", "manage_own_activities", "view_activities"]'::jsonb,
    now() - interval '3 months',
    '770e8400-e29b-41d4-a716-446655440002'::uuid,
    'Senior Plumbing Technician',
    true
),
-- Office Administrator
(
    '880e8400-e29b-41d4-a716-446655440004'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    '550e8400-e29b-41d4-a716-446655440004'::uuid,
    'admin',
    '["manage_team", "view_team_members", "invite_team_members", "manage_contacts", "view_contacts", "manage_jobs", "view_jobs", "manage_activities", "view_activities"]'::jsonb,
    now() - interval '8 months',
    '770e8400-e29b-41d4-a716-446655440003'::uuid,
    'Office Administrator',
    true
),
-- Junior Technician
(
    '880e8400-e29b-41d4-a716-446655440005'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    '550e8400-e29b-41d4-a716-446655440005'::uuid,
    'employee',
    '["view_contacts", "manage_own_jobs", "view_jobs", "manage_own_activities", "view_activities"]'::jsonb,
    now() - interval '2 months',
    '770e8400-e29b-41d4-a716-446655440001'::uuid,
    'Junior Plumbing Technician',
    true
);

-- 5. Create Working Hours Templates
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
    is_active
) VALUES 
(
    '990e8400-e29b-41d4-a716-446655440001'::uuid,
    'Standard Business Hours',
    'Monday-Friday 8AM-5PM',
    '08:00', '17:00',
    '08:00', '17:00',
    '08:00', '17:00',
    '08:00', '17:00',
    '08:00', '17:00',
    NULL, NULL,
    NULL, NULL,
    60,
    true
),
(
    '990e8400-e29b-41d4-a716-446655440002'::uuid,
    'Emergency Schedule',
    '24/7 emergency coverage with rotating shifts',
    '00:00', '23:59',
    '00:00', '23:59',
    '00:00', '23:59',
    '00:00', '23:59',
    '00:00', '23:59',
    '00:00', '23:59',
    '00:00', '23:59',
    30,
    true
);

-- 6. Create User Capabilities
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
-- Mike (Owner)
(
    'aa0e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    '123 Main St, Austin, TX 78701',
    30.266667,
    -97.733330,
    'Pickup Truck',
    true,
    '08:00',
    '17:00',
    30,
    45,
    4.8,
    98.5,
    95.2,
    '990e8400-e29b-41d4-a716-446655440001'::uuid,
    true
),
-- Sarah (Manager)
(
    'aa0e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    '456 Oak Ave, Austin, TX 78704',
    30.250000,
    -97.750000,
    'Van',
    true,
    '07:00',
    '16:00',
    45,
    60,
    4.9,
    97.8,
    98.1,
    '990e8400-e29b-41d4-a716-446655440001'::uuid,
    true
),
-- David (Senior Tech)
(
    'aa0e8400-e29b-41d4-a716-446655440003'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    '550e8400-e29b-41d4-a716-446655440003'::uuid,
    '789 Pine St, Austin, TX 78702',
    30.280000,
    -97.720000,
    'Pickup Truck',
    true,
    '06:00',
    '18:00',
    30,
    90,
    4.7,
    96.5,
    92.3,
    '990e8400-e29b-41d4-a716-446655440002'::uuid,
    true
);

-- 7. Create Contacts
INSERT INTO contacts (
    id,
    business_id,
    first_name,
    last_name,
    company_name,
    email,
    phone,
    mobile_phone,
    address,
    city,
    state,
    postal_code,
    country,
    contact_type,
    source,
    status,
    lifecycle_stage,
    priority,
    relationship_status,
    tags,
    notes,
    created_by,
    assigned_to,
    next_contact_date,
    is_active
) VALUES 
-- Residential Customers
(
    'bb0e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'John',
    'Smith',
    NULL,
    'john.smith@email.com',
    '+1-512-555-2001',
    '+1-512-555-2001',
    '1234 Elm Street',
    'Austin',
    'TX',
    '78701',
    'US',
    'individual',
    'referral',
    'active',
    'customer',
    'medium',
    'active_customer',
    ARRAY['residential', 'repeat_customer'],
    'Great customer, always pays on time. Kitchen sink repair completed last month.',
    '550e8400-e29b-41d4-a716-446655440004'::uuid,
    '550e8400-e29b-41d4-a716-446655440003'::uuid,
    (current_date + interval '30 days')::date,
    true
),
(
    'bb0e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Mary',
    'Johnson',
    NULL,
    'mary.johnson@email.com',
    '+1-512-555-2002',
    '+1-512-555-2002',
    '5678 Oak Avenue',
    'Austin',
    'TX',
    '78704',
    'US',
    'individual',
    'online',
    'active',
    'lead',
    'high',
    'new',
    ARRAY['residential', 'emergency'],
    'Emergency call for burst pipe. Potential for bathroom renovation project.',
    '550e8400-e29b-41d4-a716-446655440004'::uuid,
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    (current_date + interval '7 days')::date,
    true
),
-- Commercial Customers
(
    'bb0e8400-e29b-41d4-a716-446655440003'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Robert',
    'Davis',
    'Austin Property Management',
    'robert@austinpm.com',
    '+1-512-555-2003',
    '+1-512-555-2003',
    '999 Business Park Dr',
    'Austin',
    'TX',
    '78759',
    'US',
    'business',
    'referral',
    'active',
    'customer',
    'high',
    'active_customer',
    ARRAY['commercial', 'property_management', 'recurring'],
    'Property management company with 50+ units. Monthly maintenance contract.',
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    (current_date + interval '14 days')::date,
    true
),
(
    'bb0e8400-e29b-41d4-a716-446655440004'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Lisa',
    'Anderson',
    'Sunshine Restaurant',
    'lisa@sunshinerestaurant.com',
    '+1-512-555-2004',
    '+1-512-555-2004',
    '246 Restaurant Row',
    'Austin',
    'TX',
    '78701',
    'US',
    'business',
    'google_ads',
    'active',
    'prospect',
    'medium',
    'follow_up',
    ARRAY['commercial', 'restaurant', 'potential_contract'],
    'Restaurant interested in grease trap maintenance contract. Follow up next week.',
    '550e8400-e29b-41d4-a716-446655440004'::uuid,
    '550e8400-e29b-41d4-a716-446655440005'::uuid,
    (current_date + interval '3 days')::date,
    true
);

-- 8. Create Contact Segments
INSERT INTO contact_segments (
    id,
    business_id,
    name,
    description,
    segment_type,
    criteria,
    created_by,
    is_active
) VALUES 
(
    'cc0e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'VIP Customers',
    'High-value repeat customers',
    'manual',
    '{"min_jobs": 5, "min_revenue": 2000}'::jsonb,
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    true
),
(
    'cc0e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Emergency Prospects',
    'Leads from emergency calls',
    'automatic',
    '{"source": "emergency", "created_days": 30}'::jsonb,
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    true
);

-- 9. Create Contact Segment Memberships
INSERT INTO contact_segment_memberships (
    id,
    business_id,
    contact_id,
    segment_id,
    added_by
) VALUES 
(
    'dd0e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'bb0e8400-e29b-41d4-a716-446655440001'::uuid,
    'cc0e8400-e29b-41d4-a716-446655440001'::uuid,
    '550e8400-e29b-41d4-a716-446655440001'::uuid
),
(
    'dd0e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'bb0e8400-e29b-41d4-a716-446655440002'::uuid,
    'cc0e8400-e29b-41d4-a716-446655440002'::uuid,
    '550e8400-e29b-41d4-a716-446655440002'::uuid
);

-- 10. Create Jobs
INSERT INTO jobs (
    id,
    business_id,
    job_number,
    title,
    description,
    job_type,
    status,
    priority,
    source,
    contact_id,
    assigned_to,
    estimated_duration_hours,
    actual_duration_hours,
    estimated_cost,
    actual_cost,
    scheduled_start,
    scheduled_end,
    actual_start,
    actual_end,
    location_address,
    location_city,
    location_state,
    location_postal_code,
    location_country,
    location_latitude,
    location_longitude,
    special_instructions,
    internal_notes,
    created_by,
    is_active
) VALUES 
-- Completed Job
(
    'ee0e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'JOB-2024-001',
    'Kitchen Sink Repair',
    'Repair leaky kitchen sink faucet and replace worn gaskets',
    'repair',
    'completed',
    'medium',
    'phone',
    'bb0e8400-e29b-41d4-a716-446655440001'::uuid,
    ARRAY['550e8400-e29b-41d4-a716-446655440003'::uuid],
    2.0,
    1.5,
    150.00,
    125.00,
    (now() - interval '7 days'),
    (now() - interval '7 days' + interval '2 hours'),
    (now() - interval '7 days'),
    (now() - interval '7 days' + interval '1.5 hours'),
    '1234 Elm Street',
    'Austin',
    'TX',
    '78701',
    'US',
    30.266667,
    -97.733330,
    'Customer prefers morning appointments. Use side entrance.',
    'Customer very satisfied. Mentioned potential bathroom project.',
    '550e8400-e29b-41d4-a716-446655440004'::uuid,
    true
),
-- Scheduled Job
(
    'ee0e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'JOB-2024-002',
    'Emergency Pipe Repair',
    'Emergency repair of burst pipe in basement',
    'emergency',
    'scheduled',
    'high',
    'emergency',
    'bb0e8400-e29b-41d4-a716-446655440002'::uuid,
    ARRAY['550e8400-e29b-41d4-a716-446655440003'::uuid, '550e8400-e29b-41d4-a716-446655440005'::uuid],
    4.0,
    NULL,
    350.00,
    NULL,
    (now() + interval '2 hours'),
    (now() + interval '6 hours'),
    NULL,
    NULL,
    '5678 Oak Avenue',
    'Austin',
    'TX',
    '78704',
    'US',
    30.250000,
    -97.750000,
    'Emergency access code: 1234. Water shut off at main.',
    'High priority - customer has flooded basement.',
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    true
),
-- In Progress Job
(
    'ee0e8400-e29b-41d4-a716-446655440003'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'JOB-2024-003',
    'Monthly Maintenance Check',
    'Routine maintenance check for commercial property',
    'maintenance',
    'in_progress',
    'low',
    'contract',
    'bb0e8400-e29b-41d4-a716-446655440003'::uuid,
    ARRAY['550e8400-e29b-41d4-a716-446655440002'::uuid],
    3.0,
    NULL,
    200.00,
    NULL,
    (now() - interval '1 hour'),
    (now() + interval '2 hours'),
    (now() - interval '1 hour'),
    NULL,
    '999 Business Park Dr',
    'Austin',
    'TX',
    '78759',
    'US',
    30.400000,
    -97.700000,
    'Check all units. Property manager available until 4 PM.',
    'Monthly contract work. Building has 12 units to check.',
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    true
);

-- 11. Create Job Templates
INSERT INTO job_templates (
    id,
    business_id,
    name,
    description,
    job_type,
    estimated_duration_hours,
    estimated_cost,
    checklist,
    required_skills,
    instructions,
    is_active
) VALUES 
(
    'ff0e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Standard Sink Repair',
    'Template for common sink repairs',
    'repair',
    2.0,
    150.00,
    '["Check faucet connections", "Inspect under-sink plumbing", "Test water pressure", "Replace worn parts", "Test for leaks"]'::jsonb,
    ARRAY['basic_plumbing', 'hand_tools'],
    'Standard procedure for sink repairs. Always turn off water supply first.',
    true
),
(
    'ff0e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Emergency Pipe Repair',
    'Template for emergency pipe repairs',
    'emergency',
    4.0,
    350.00,
    '["Assess damage", "Turn off water supply", "Remove damaged section", "Install replacement", "Test system", "Clean up area"]'::jsonb,
    ARRAY['pipe_fitting', 'emergency_response', 'power_tools'],
    'Emergency protocol. Safety first. Document all damage with photos.',
    true
);

-- 12. Create Activities
INSERT INTO activities (
    id,
    business_id,
    title,
    description,
    activity_type,
    status,
    priority,
    contact_id,
    assigned_to,
    due_date,
    completed_date,
    estimated_duration_minutes,
    actual_duration_minutes,
    outcome,
    notes,
    is_active
) VALUES 
-- Completed Activity
(
    '110e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Follow up on kitchen project',
    'Call John Smith about potential kitchen renovation project mentioned during last visit',
    'task',
    'completed',
    'medium',
    'bb0e8400-e29b-41d4-a716-446655440001'::uuid,
    ARRAY['550e8400-e29b-41d4-a716-446655440004'::uuid],
    (now() - interval '2 days'),
    (now() - interval '1 day'),
    30,
    25,
    'scheduled_estimate',
    'Customer interested. Scheduled estimate for next week.',
    true
),
-- Pending Activity
(
    '110e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Prepare quote for restaurant',
    'Create detailed quote for grease trap maintenance contract',
    'task',
    'pending',
    'high',
    'bb0e8400-e29b-41d4-a716-446655440004'::uuid,
    ARRAY['550e8400-e29b-41d4-a716-446655440001'::uuid],
    (now() + interval '1 day'),
    NULL,
    120,
    NULL,
    NULL,
    'Need to include monthly maintenance and emergency response options.',
    true
);

-- 13. Create Activity Templates
INSERT INTO activity_templates (
    id,
    business_id,
    name,
    description,
    activity_type,
    estimated_duration_minutes,
    checklist,
    instructions,
    is_active
) VALUES 
(
    '120e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Customer Follow-up Call',
    'Standard follow-up call template',
    'task',
    30,
    '["Review previous job details", "Ask about satisfaction", "Inquire about future needs", "Update contact preferences"]'::jsonb,
    'Call within 48 hours of job completion. Be friendly and professional.',
    true
),
(
    '120e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Quote Preparation',
    'Standard quote preparation process',
    'task',
    90,
    '["Review job requirements", "Calculate materials", "Estimate labor", "Add markup", "Format quote", "Schedule delivery"]'::jsonb,
    'Use standard pricing guidelines. Include all materials and labor.',
    true
);

-- 14. Create Contact Activities
INSERT INTO contact_activities (
    id,
    business_id,
    contact_id,
    activity_type,
    description,
    activity_date,
    performed_by,
    outcome,
    notes,
    metadata
) VALUES 
(
    '130e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'bb0e8400-e29b-41d4-a716-446655440001'::uuid,
    'interaction',
    'Phone call about kitchen sink repair',
    (now() - interval '8 days'),
    '550e8400-e29b-41d4-a716-446655440004'::uuid,
    'job_scheduled',
    'Customer reported leaky faucet. Scheduled repair for tomorrow.',
    '{"call_duration": "5 minutes", "urgency": "medium"}'::jsonb
),
(
    '130e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'bb0e8400-e29b-41d4-a716-446655440002'::uuid,
    'interaction',
    'Emergency call - burst pipe',
    (now() - interval '3 hours'),
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    'emergency_scheduled',
    'Customer has flooding in basement. Scheduled emergency response.',
    '{"call_duration": "8 minutes", "urgency": "high", "emergency": true}'::jsonb
);

-- 15. Create Contact Notes
INSERT INTO contact_notes (
    id,
    business_id,
    contact_id,
    note_type,
    content,
    is_private,
    created_by
) VALUES 
(
    '140e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'bb0e8400-e29b-41d4-a716-446655440001'::uuid,
    'general',
    'Excellent customer. Always pays promptly. Mentioned interest in bathroom renovation during last visit.',
    false,
    '550e8400-e29b-41d4-a716-446655440003'::uuid
),
(
    '140e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'bb0e8400-e29b-41d4-a716-446655440003'::uuid,
    'business',
    'Property management company with 50+ rental units. Good potential for ongoing maintenance contract.',
    false,
    '550e8400-e29b-41d4-a716-446655440001'::uuid
);

-- 16. Create Job Activities
INSERT INTO job_activities (
    id,
    business_id,
    job_id,
    activity_type,
    description,
    performed_date,
    user_id,
    old_status,
    new_status,
    metadata
) VALUES 
(
    '150e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'ee0e8400-e29b-41d4-a716-446655440001'::uuid,
    'status_change',
    'Job completed successfully',
    (now() - interval '7 days' + interval '1.5 hours'),
    '550e8400-e29b-41d4-a716-446655440003'::uuid,
    'in_progress',
    'completed',
    '{"completion_notes": "All work completed to customer satisfaction"}'::jsonb
),
(
    '150e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'ee0e8400-e29b-41d4-a716-446655440003'::uuid,
    'status_change',
    'Started monthly maintenance check',
    (now() - interval '1 hour'),
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    'scheduled',
    'in_progress',
    '{"start_notes": "Beginning routine inspection of all units"}'::jsonb
);

-- 17. Create Job Notes
INSERT INTO job_notes (
    id,
    business_id,
    job_id,
    note_type,
    content,
    is_internal,
    user_id
) VALUES 
(
    '160e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'ee0e8400-e29b-41d4-a716-446655440001'::uuid,
    'completion',
    'Faucet repaired and new gaskets installed. Customer very happy with the work. No issues found.',
    false,
    '550e8400-e29b-41d4-a716-446655440003'::uuid
),
(
    '160e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'ee0e8400-e29b-41d4-a716-446655440002'::uuid,
    'preparation',
    'Emergency kit loaded in truck. Customer called ahead - basement is flooded.',
    true,
    '550e8400-e29b-41d4-a716-446655440003'::uuid
);

-- 18. Create Job Attachments
INSERT INTO job_attachments (
    id,
    business_id,
    job_id,
    file_name,
    file_url,
    file_type,
    file_size,
    uploaded_by
) VALUES 
(
    '170e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'ee0e8400-e29b-41d4-a716-446655440001'::uuid,
    'before_photo.jpg',
    'https://storage.example.com/jobs/before_photo.jpg',
    'image/jpeg',
    245760,
    '550e8400-e29b-41d4-a716-446655440003'::uuid
),
(
    '170e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'ee0e8400-e29b-41d4-a716-446655440001'::uuid,
    'after_photo.jpg',
    'https://storage.example.com/jobs/after_photo.jpg',
    'image/jpeg',
    198432,
    '550e8400-e29b-41d4-a716-446655440003'::uuid
);

-- 19. Create Calendar Events
INSERT INTO calendar_events (
    id,
    user_id,
    business_id,
    title,
    description,
    event_type,
    start_datetime,
    end_datetime,
    is_all_day,
    timezone,
    blocks_scheduling,
    is_active
) VALUES 
(
    '180e8400-e29b-41d4-a716-446655440001'::uuid,
    '550e8400-e29b-41d4-a716-446655440003'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Emergency Response Shift',
    'On-call for emergency plumbing responses',
    'work_schedule',
    (now() + interval '18 hours'),
    (now() + interval '42 hours'),
    false,
    'America/Chicago',
    true,
    true
),
(
    '180e8400-e29b-41d4-a716-446655440002'::uuid,
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Team Meeting',
    'Weekly team coordination meeting',
    'meeting',
    (now() + interval '3 days' + interval '9 hours'),
    (now() + interval '3 days' + interval '10 hours'),
    false,
    'America/Chicago',
    false,
    true
);

-- 20. Create Calendar Preferences
INSERT INTO calendar_preferences (
    user_id,
    business_id,
    timezone,
    preferred_working_hours_template_id,
    min_time_between_jobs_minutes,
    max_commute_time_minutes,
    allows_back_to_back_jobs,
    weekend_availability,
    emergency_availability_outside_hours
) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'America/Chicago',
    '990e8400-e29b-41d4-a716-446655440001'::uuid,
    45,
    60,
    false,
    false,
    true
),
(
    '550e8400-e29b-41d4-a716-446655440003'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'America/Chicago',
    '990e8400-e29b-41d4-a716-446655440002'::uuid,
    30,
    90,
    true,
    true,
    true
);

-- 21. Create Activity Participants
INSERT INTO activity_participants (
    id,
    activity_id,
    user_id,
    role
) VALUES 
(
    '190e8400-e29b-41d4-a716-446655440001'::uuid,
    '110e8400-e29b-41d4-a716-446655440001'::uuid,
    '550e8400-e29b-41d4-a716-446655440004'::uuid,
    'primary'
),
(
    '190e8400-e29b-41d4-a716-446655440002'::uuid,
    '110e8400-e29b-41d4-a716-446655440002'::uuid,
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    'primary'
);

-- 22. Create Activity Reminders
INSERT INTO activity_reminders (
    id,
    activity_id,
    reminder_type,
    reminder_time,
    message,
    is_sent
) VALUES 
(
    '200e8400-e29b-41d4-a716-446655440001'::uuid,
    '110e8400-e29b-41d4-a716-446655440002'::uuid,
    'email',
    (now() + interval '12 hours'),
    'Reminder: Prepare quote for Sunshine Restaurant grease trap maintenance',
    false
);

-- 23. Create Business Invitation (optional demo)
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
    '210e8400-e29b-41d4-a716-446655440001'::uuid,
    '660e8400-e29b-41d4-a716-446655440000'::uuid,
    'Elite Plumbing Services',
    'newtech@example.com',
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    'Mike Johnson',
    'employee',
    '["view_contacts", "manage_own_jobs", "view_jobs", "manage_own_activities", "view_activities"]'::jsonb,
    now(),
    (now() + interval '7 days'),
    'pending',
    'Welcome to Elite Plumbing! Please join our team to start managing jobs and customers.'
);

-- Update sequence counters to continue from our demo data
-- (This ensures future records don't conflict with our demo UUIDs)

COMMENT ON DATABASE postgres IS 'Hero365 Demo Database - Complete with realistic plumbing business data'; 