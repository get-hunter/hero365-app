-- Fix requirements field for Tesla Wall Connector installation options
-- Change from array to object format as expected by the API

UPDATE product_installation_options 
SET requirements = '{}'::jsonb
WHERE product_id = '38337322-7b1c-4ebd-9953-623c5b994efd'
  AND business_id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef';
