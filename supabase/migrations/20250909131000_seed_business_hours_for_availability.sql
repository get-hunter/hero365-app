-- Seed business_hours for availability demo
-- This populates weekly hours so the availability generator can return slots
-- Business: Elite HVAC Austin (example business id used in local dev)

DO $$
DECLARE
    v_business_id UUID := '550e8400-e29b-41d4-a716-446655440010';
BEGIN
    -- Remove existing hours for a clean slate (idempotent)
    DELETE FROM business_hours WHERE business_id = v_business_id;

    -- Insert hours (0=Mon .. 6=Sun)
    INSERT INTO business_hours (
        business_id,
        day_of_week,
        is_open,
        open_time,
        close_time,
        break_start,
        break_end,
        is_emergency_available
    ) VALUES
        -- Monday
        (v_business_id, 0, TRUE,  TIME '09:00', TIME '17:00', TIME '12:00', TIME '13:00', TRUE),
        -- Tuesday
        (v_business_id, 1, TRUE,  TIME '09:00', TIME '17:00', TIME '12:00', TIME '13:00', TRUE),
        -- Wednesday
        (v_business_id, 2, TRUE,  TIME '09:00', TIME '17:00', TIME '12:00', TIME '13:00', TRUE),
        -- Thursday
        (v_business_id, 3, TRUE,  TIME '09:00', TIME '17:00', TIME '12:00', TIME '13:00', TRUE),
        -- Friday
        (v_business_id, 4, TRUE,  TIME '09:00', TIME '17:00', TIME '12:00', TIME '13:00', TRUE),
        -- Saturday (short day)
        (v_business_id, 5, TRUE,  TIME '10:00', TIME '14:00', NULL,       NULL,       TRUE),
        -- Sunday (closed)
        (v_business_id, 6, FALSE, NULL,         NULL,         NULL,       NULL,       TRUE);
END $$;

-- Verification notice
DO $$ BEGIN RAISE NOTICE 'Seeded business_hours for %', '550e8400-e29b-41d4-a716-446655440010'; END $$;


