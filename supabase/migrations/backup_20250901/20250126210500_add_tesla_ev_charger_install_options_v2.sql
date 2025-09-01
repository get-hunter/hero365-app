-- Add installation options for Tesla Wall Connector EV Charger
-- Product ID: 38337322-7b1c-4ebd-9953-623c5b994efd
-- Using different service IDs to avoid unique constraint conflicts

INSERT INTO product_installation_options (
    business_id,
    product_id,
    service_id,
    option_name,
    description,
    base_install_price,
    residential_install_price,
    commercial_install_price,
    premium_install_price,
    estimated_duration_hours,
    complexity_multiplier,
    is_default,
    is_active,
    requirements,
    included_in_install,
    sort_order
) VALUES 

-- Standard Installation - Using EV Charger Installation service
(
    'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    '38337322-7b1c-4ebd-9953-623c5b994efd',
    'fa22ca89-70e6-4447-8e11-883671358f3b', -- EV Charger Installation
    'Standard Installation',
    'Basic wall mount installation up to 25ft from electrical panel. Includes permit and inspection.',
    450.00,
    400.00,  -- 10% discount for residential members
    380.00,  -- 15% discount for commercial members  
    340.00,  -- 25% discount for premium members
    4.0,
    1.0,
    true,    -- is_default
    true,    -- is_active
    '{}'::jsonb,
    '["Wall mounting hardware", "Basic wiring (up to 25ft)", "Permit acquisition", "Final inspection"]'::jsonb,
    1
),

-- Extended Installation - Using New Outlet Installation service 
(
    'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    '38337322-7b1c-4ebd-9953-623c5b994efd',
    '227e948e-97bb-4b1d-b989-ec181b20b347', -- New Outlet Installation
    'Extended Installation',
    'Installation with extended wiring run (26-50ft). Includes conduit, panel upgrade assessment.',
    750.00,
    675.00,  -- 10% discount
    640.00,  -- 15% discount  
    560.00,  -- 25% discount
    6.0,
    1.5,
    false,   -- is_default
    true,    -- is_active
    '{}'::jsonb,
    '["Wall mounting hardware", "Extended wiring (26-50ft)", "Conduit installation", "Permit acquisition", "Panel assessment", "Final inspection"]'::jsonb,
    2
),

-- Premium Installation - Using Generator Installation service
(
    'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    '38337322-7b1c-4ebd-9953-623c5b994efd',
    'bafe7fa1-1339-4b85-9509-8c2ee23a49e2', -- Generator Installation
    'Premium Installation',
    'Complete installation with panel upgrade if needed. Includes smart monitoring setup.',
    1200.00,
    1080.00, -- 10% discount
    1020.00, -- 15% discount
    900.00,  -- 25% discount
    8.0,
    2.0,
    false,   -- is_default
    true,    -- is_active
    '{}'::jsonb,
    '["Wall mounting hardware", "Complete wiring solution", "Panel upgrade (if needed)", "Smart monitoring setup", "Load balancing", "Permit acquisition", "Final inspection", "1-year service warranty"]'::jsonb,
    3
);
