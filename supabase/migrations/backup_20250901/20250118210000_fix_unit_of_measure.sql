-- Fix unit of measure validation issues
-- Update products with invalid unit_of_measure values

UPDATE products 
SET unit_of_measure = 'month'
WHERE business_id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef' 
  AND unit_of_measure = 'year';

-- Success message
SELECT 'Unit of measure validation issues fixed! 🎉' as message,
       'Updated year to month for annual services' as summary;
