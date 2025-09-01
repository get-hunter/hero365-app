-- Fix business validation issues
-- Fix business_hours to be a proper JSON object instead of empty array

-- Update the business_hours to be a proper JSON object
UPDATE businesses 
SET business_hours = '{}'::jsonb
WHERE id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef' AND business_hours = '[]'::jsonb;

-- Success message
SELECT 'Business validation issues fixed! 🎉' as message,
       'Fixed business_hours to be proper JSON object' as summary;
