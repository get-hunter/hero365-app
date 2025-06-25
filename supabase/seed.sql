-- Hero365 Simplified Seed Data
-- Creates one complete business with all related entities for testing

-- Clear all existing data first
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
    businesses,
    users
CASCADE;

-- Create Users (must be first due to foreign key constraints)
INSERT INTO public.users (
    id,
    email,
    full_name,
    display_name,
    phone,
    is_active,
    created_at
) VALUES 
(
    '11111111-1111-1111-1111-111111111111'::uuid,
    'owner@eliteplumbing.com',
    'Mike Johnson',
    'Mike Johnson',
    '+1-512-555-1000',
    true,
    now() - interval '1 year'
),
(
    '22222222-2222-2222-2222-222222222222'::uuid,
    'tech1@eliteplumbing.com',
    'Sarah Wilson',
    'Sarah Wilson',
    '+1-512-555-1001',
    true,
    now() - interval '6 months'
),
(
    '33333333-3333-3333-3333-333333333333'::uuid,
    'tech2@eliteplumbing.com',
    'David Chen',
    'David Chen',
    '+1-512-555-1002',
    true,
    now() - interval '3 months'
),
(
    '44444444-4444-4444-4444-444444444444'::uuid,
    'admin@eliteplumbing.com',
    'Jennifer Garcia',
    'Jennifer Garcia',
    '+1-512-555-1003',
    true,
    now() - interval '8 months'
);

-- Create Business
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
) VALUES (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'Elite Plumbing Services',
    'plumbing',
    'small',
    '11111111-1111-1111-1111-111111111111'::uuid,
    'Premier residential and commercial plumbing services with 24/7 emergency support',
    '+1-512-555-PIPE',
    '123 Main St, Austin, TX 78701',
    'contact@eliteplumbing.com',
    true,
    'America/Chicago',
    'USD',
    true
);

-- Create Departments
INSERT INTO departments (
    id,
    business_id,
    name,
    description,
    manager_id,
    is_active
) VALUES 
(
    'dddddddd-dddd-dddd-dddd-dddddddddddd'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'Field Operations',
    'On-site plumbing services and installations',
    '22222222-2222-2222-2222-222222222222'::uuid,
    true
),
(
    'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'Emergency Services',
    '24/7 emergency plumbing response team',
    '33333333-3333-3333-3333-333333333333'::uuid,
    true
);

-- Create Business Memberships
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
    'mmmmmmmm-mmmm-mmmm-mmmm-mmmmmmmmmmmm'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    'owner',
    '["*"]'::jsonb,
    now() - interval '1 year',
    true
),
(
    'nnnnnnnn-nnnn-nnnn-nnnn-nnnnnnnnnnnn'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    'manager',
    '["view_contacts", "create_contacts", "edit_contacts", "view_jobs", "create_jobs", "edit_jobs", "manage_team"]'::jsonb,
    now() - interval '6 months',
    true
),
(
    'oooooooo-oooo-oooo-oooo-oooooooooooo'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    '33333333-3333-3333-3333-333333333333'::uuid,
    'employee',
    '["view_contacts", "create_contacts", "edit_contacts", "view_jobs", "create_jobs", "edit_jobs"]'::jsonb,
    now() - interval '3 months',
    true
),
(
    'pppppppp-pppp-pppp-pppp-pppppppppppp'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    '44444444-4444-4444-4444-444444444444'::uuid,
    'admin',
    '["view_contacts", "create_contacts", "edit_contacts", "delete_contacts", "view_jobs", "create_jobs", "edit_jobs", "delete_jobs", "view_business_settings", "edit_business_settings"]'::jsonb,
    now() - interval '8 months',
    true
);

-- Create User Capabilities
INSERT INTO user_capabilities (
    id,
    business_id,
    user_id,
    home_base_address,
    vehicle_type,
    has_vehicle,
    preferred_start_time,
    preferred_end_time,
    min_time_between_jobs_minutes,
    max_commute_time_minutes,
    is_active
) VALUES 
(
    'cccccccc-cccc-cccc-cccc-cccccccccccc'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '123 Main St, Austin, TX 78701',
    'service_van',
    true,
    '07:00',
    '17:00',
    45,
    60,
    true
),
(
    'ffffffff-ffff-ffff-ffff-ffffffffffff'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    '33333333-3333-3333-3333-333333333333'::uuid,
    '456 Oak St, Austin, TX 78702',
    'pickup_truck',
    true,
    '08:00',
    '18:00',
    30,
    45,
    true
);

-- Create Contacts
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
    created_by,
    assigned_to,
    custom_fields,
    last_contacted
) VALUES 
(
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'customer',
    'active',
    'John',
    'Smith',
    NULL,
    NULL,
    'john.smith@email.com',
    '+1-512-555-2000',
    NULL,
    NULL,
    '{"street_address": "456 Oak Ave", "city": "Austin", "state": "TX", "postal_code": "78702", "country": "US"}'::jsonb,
    'medium',
    'website',
    '["residential", "repeat_customer"]'::jsonb,
    'Kitchen sink repair completed. Very satisfied customer.',
    1500.00,
    'USD',
    '22222222-2222-2222-2222-222222222222'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '{"preferred_contact_time": "morning", "has_pets": true}'::jsonb,
    now() - interval '3 days'
),
(
    'iiiiiiii-iiii-iiii-iiii-iiiiiiiiiiii'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'lead',
    'new',
    'Lisa',
    'Rodriguez',
    'Austin Office Complex',
    'Facilities Manager',
    'lisa.r@austinoffice.com',
    '+1-512-555-3000',
    '+1-512-555-3001',
    'www.austinofficecomplex.com',
    '{"street_address": "789 Business Park Dr", "city": "Austin", "state": "TX", "postal_code": "78705", "country": "US"}'::jsonb,
    'high',
    'referral',
    '["commercial", "potential_contract"]'::jsonb,
    'Interested in annual maintenance contract for 3 office buildings.',
    8000.00,
    'USD',
    '44444444-4444-4444-4444-444444444444'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '{"buildings_count": 3, "current_provider": "competitor"}'::jsonb,
    now() - interval '1 day'
),
(
    'jjjjjjjj-jjjj-jjjj-jjjj-jjjjjjjjjjjj'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'customer',
    'active',
    'Robert',
    'Williams',
    NULL,
    NULL,
    'robert.w@email.com',
    '+1-512-555-4000',
    NULL,
    NULL,
    '{"street_address": "321 Pine St", "city": "Austin", "state": "TX", "postal_code": "78703", "country": "US"}'::jsonb,
    'high',
    'emergency_call',
    '["residential", "emergency_service"]'::jsonb,
    'Emergency water heater replacement. Available for future work.',
    2200.00,
    'USD',
    '33333333-3333-3333-3333-333333333333'::uuid,
    '33333333-3333-3333-3333-333333333333'::uuid,
    '{"emergency_contact": true, "payment_terms": "immediate"}'::jsonb,
    now() - interval '7 days'
);

-- Create Jobs
INSERT INTO jobs (
    id,
    business_id,
    contact_id,
    job_number,
    title,
    description,
    job_type,
    status,
    priority,
    source,
    job_address,
    scheduled_start,
    scheduled_end,
    actual_start,
    actual_end,
    assigned_to,
    created_by,
    time_tracking,
    cost_estimate,
    tags,
    notes,
    internal_notes,
    customer_requirements,
    completion_notes,
    custom_fields
) VALUES 
(
    'qqqqqqqq-qqqq-qqqq-qqqq-qqqqqqqqqqqq'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid,
    'JOB-2024-001',
    'Kitchen Sink Repair',
    'Fix leaking kitchen sink faucet and replace garbage disposal',
    'repair',
    'completed',
    'medium',
    'customer_request',
    '{"street_address": "456 Oak Ave", "city": "Austin", "state": "TX", "postal_code": "78702", "country": "US"}'::jsonb,
    now() - interval '5 days',
    now() - interval '5 days' + interval '3 hours',
    now() - interval '5 days',
    now() - interval '5 days' + interval '2.5 hours',
    '["22222222-2222-2222-2222-222222222222"]'::uuid[],
    '22222222-2222-2222-2222-222222222222'::uuid,
    '{"total_hours": 2.5, "billable_hours": 2.5}'::jsonb,
    '{"parts": 125.50, "labor": 212.50, "total": 338.00}'::jsonb,
    '["residential", "repair", "completed"]'::jsonb,
    'Customer very satisfied with quick service',
    'Used premium faucet as requested by customer',
    'Customer prefers morning appointments',
    'Job completed successfully, customer paid immediately',
    '{"warranty_period": "1_year", "follow_up_date": "2024-07-01"}'::jsonb
),
(
    'rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'jjjjjjjj-jjjj-jjjj-jjjj-jjjjjjjjjjjj'::uuid,
    'JOB-2024-002',
    'Emergency Water Heater Replacement',
    'Replace failed 40-gallon water heater in garage',
    'installation',
    'completed',
    'urgent',
    'emergency_call',
    '{"street_address": "321 Pine St", "city": "Austin", "state": "TX", "postal_code": "78703", "country": "US"}'::jsonb,
    now() - interval '8 days',
    now() - interval '8 days' + interval '4 hours',
    now() - interval '8 days',
    now() - interval '8 days' + interval '3.5 hours',
    '["33333333-3333-3333-3333-333333333333"]'::uuid[],
    '33333333-3333-3333-3333-333333333333'::uuid,
    '{"total_hours": 3.5, "billable_hours": 3.5, "emergency_rate": true}'::jsonb,
    '{"parts": 850.00, "labor": 525.00, "emergency_fee": 100.00, "total": 1475.00}'::jsonb,
    '["residential", "emergency", "installation", "completed"]'::jsonb,
    'Emergency replacement completed same day',
    'Customer was very grateful for quick response',
    'No hot water, family with small children',
    'High-efficiency unit installed, customer educated on maintenance',
    '{"warranty_period": "5_years", "maintenance_schedule": "annual"}'::jsonb
),
(
    'ssssssss-ssss-ssss-ssss-ssssssssssss'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'iiiiiiii-iiii-iiii-iiii-iiiiiiiiiiii'::uuid,
    'JOB-2024-003',
    'Commercial Building Assessment',
    'Comprehensive plumbing assessment for potential maintenance contract',
    'assessment',
    'scheduled',
    'high',
    'referral',
    '{"street_address": "789 Business Park Dr", "city": "Austin", "state": "TX", "postal_code": "78705", "country": "US"}'::jsonb,
    now() + interval '2 days',
    now() + interval '2 days' + interval '6 hours',
    NULL,
    NULL,
    '["11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222"]'::uuid[],
    '44444444-4444-4444-4444-444444444444'::uuid,
    '{"estimated_hours": 6}'::jsonb,
    '{"labor": 510.00, "total": 510.00}'::jsonb,
    '["commercial", "assessment", "potential_contract"]'::jsonb,
    'Potential for large maintenance contract',
    'Bring inspection equipment and assessment forms',
    '3 buildings, focus on main plumbing systems',
    NULL,
    '{"buildings": ["Building A", "Building B", "Building C"], "scope": "full_assessment"}'::jsonb
);

-- Create Contact Activities
INSERT INTO contact_activities (
    id,
    business_id,
    contact_id,
    activity_type,
    subject,
    description,
    activity_date,
    performed_by,
    duration_minutes,
    outcome,
    follow_up_required,
    follow_up_date,
    custom_fields
) VALUES 
(
    'tttttttt-tttt-tttt-tttt-tttttttttttt'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid,
    'call',
    'Follow-up call after kitchen sink repair',
    'Called to ensure customer satisfaction with recent repair work',
    now() - interval '1 day',
    '22222222-2222-2222-2222-222222222222'::uuid,
    10,
    'positive',
    false,
    NULL,
    '{"satisfaction_score": 10, "would_recommend": true}'::jsonb
),
(
    'uuuuuuuu-uuuu-uuuu-uuuu-uuuuuuuuuuuu'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'iiiiiiii-iiii-iiii-iiii-iiiiiiiiiiii'::uuid,
    'email',
    'Commercial assessment proposal sent',
    'Sent detailed proposal for comprehensive plumbing assessment',
    now() - interval '2 hours',
    '44444444-4444-4444-4444-444444444444'::uuid,
    5,
    'pending',
    true,
    now() + interval '3 days',
    '{"proposal_value": 8000, "decision_timeline": "2_weeks"}'::jsonb
);

-- Create Contact Notes
INSERT INTO contact_notes (
    id,
    business_id,
    contact_id,
    note_type,
    title,
    content,
    is_private,
    created_by,
    tags
) VALUES 
(
    'vvvvvvvv-vvvv-vvvv-vvvv-vvvvvvvvvvvv'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid,
    'general',
    'Customer Preferences',
    'Prefers morning appointments between 8-10 AM. Has a friendly golden retriever named Max. Garage access through side gate.',
    false,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '["preferences", "pets", "access"]'::jsonb
),
(
    'wwwwwwww-wwww-wwww-wwww-wwwwwwwwwwww'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'iiiiiiii-iiii-iiii-iiii-iiiiiiiiiiii'::uuid,
    'commercial',
    'Building Details',
    'Three office buildings: Building A (5 floors), Building B (3 floors), Building C (2 floors). Current maintenance provider contract expires in 3 months.',
    false,
    '44444444-4444-4444-4444-444444444444'::uuid,
    '["buildings", "contract", "competitor"]'::jsonb
);

-- Create Job Activities  
INSERT INTO job_activities (
    id,
    business_id,
    job_id,
    activity_type,
    description,
    activity_date,
    user_id,
    duration_minutes,
    custom_fields
) VALUES 
(
    'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'qqqqqqqq-qqqq-qqqq-qqqq-qqqqqqqqqqqq'::uuid,
    'started',
    'Arrived on site and began kitchen sink assessment',
    now() - interval '5 days',
    '22222222-2222-2222-2222-222222222222'::uuid,
    0,
    '{"arrival_time": "08:30", "customer_present": true}'::jsonb
),
(
    'yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'qqqqqqqq-qqqq-qqqq-qqqq-qqqqqqqqqqqq'::uuid,
    'completed',
    'Kitchen sink repair and garbage disposal replacement completed',
    now() - interval '5 days' + interval '2.5 hours',
    '22222222-2222-2222-2222-222222222222'::uuid,
    150,
    '{"completion_time": "11:00", "customer_signature": true}'::jsonb
);

-- Create Job Notes
INSERT INTO job_notes (
    id,
    business_id,
    job_id,
    note_type,
    title,
    content,
    is_private,
    user_id,
    custom_fields
) VALUES 
(
    'zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'qqqqqqqq-qqqq-qqqq-qqqq-qqqqqqqqqqqq'::uuid,
    'technical',
    'Parts Used',
    'Installed Moen Arbor single-handle faucet (model 7594) and InSinkErator Evolution Compact garbage disposal',
    false,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '{"faucet_model": "Moen 7594", "disposal_model": "InSinkErator Evolution Compact"}'::jsonb
);

-- Create Contact Segments
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
    '12345678-1234-1234-1234-123456789012'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'High Value Customers',
    'Customers with estimated value over $2000',
    'dynamic',
    '{"estimated_value": {"min": 2000}}'::jsonb,
    '#28a745',
    true,
    '44444444-4444-4444-4444-444444444444'::uuid
),
(
    '23456789-2345-2345-2345-234567890123'::uuid,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid,
    'Commercial Clients',
    'All commercial and business contacts',
    'manual',
    '{"contact_type": ["commercial"], "tags": ["commercial"]}'::jsonb,
    '#007bff',
    true,
    '44444444-4444-4444-4444-444444444444'::uuid
);

-- Create Working Hours Template
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
) VALUES (
    '87654321-8765-4321-8765-876543218765'::uuid,
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
);

COMMENT ON TABLE public.users IS 'User profiles for Hero365 platform';
COMMENT ON TABLE businesses IS 'Home services business entity';
COMMENT ON TABLE contacts IS 'Customer and lead contact information';
COMMENT ON TABLE jobs IS 'Service jobs and work orders';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Seed data successfully created for Elite Plumbing Services!';
    RAISE NOTICE 'Created: 4 users, 1 business, 4 memberships, 3 contacts, 3 jobs, and related data';
END $$; 