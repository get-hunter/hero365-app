-- Fix business_hours field format issue
-- Convert any array values to proper dict format or NULL

-- Fix businesses where business_hours is an empty array
UPDATE businesses 
SET business_hours = NULL 
WHERE business_hours IS NOT NULL 
AND jsonb_typeof(business_hours) = 'array';

-- Set default empty object for businesses that have NULL business_hours
-- This is optional but provides a consistent structure
UPDATE businesses 
SET business_hours = '{}'::jsonb
WHERE business_hours IS NULL;
