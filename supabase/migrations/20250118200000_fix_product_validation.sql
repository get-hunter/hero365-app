-- Fix product validation issues
-- Update existing products to have valid created_by and reorder_quantity values

UPDATE products 
SET 
  created_by = 'system',
  reorder_quantity = CASE 
    WHEN reorder_quantity = 0 THEN 1 
    ELSE reorder_quantity 
  END
WHERE business_id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef' 
  AND (created_by IS NULL OR reorder_quantity = 0);

-- Success message
SELECT 'Product validation issues fixed! 🎉' as message,
       'Updated created_by and reorder_quantity fields' as summary;
