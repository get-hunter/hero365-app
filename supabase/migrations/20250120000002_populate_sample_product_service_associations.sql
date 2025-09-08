-- Populate sample product-service associations for testing
-- This demonstrates the service-driven product filtering approach

-- First, let's create associations for R-410A Refrigerant with HVAC services
INSERT INTO product_service_associations (business_id, product_id, service_id, association_type, display_order, is_featured, notes)
SELECT 
  '550e8400-e29b-41d4-a716-446655440010'::uuid as business_id,
  p.id as product_id,
  bs.id as service_id,
  CASE 
    WHEN bs.service_name ILIKE '%installation%' THEN 'required'
    WHEN bs.service_name ILIKE '%service%' OR bs.service_name ILIKE '%repair%' THEN 'recommended'
    ELSE 'optional'
  END as association_type,
  1 as display_order,
  CASE WHEN bs.service_name ILIKE '%installation%' THEN true ELSE false END as is_featured,
  'Essential refrigerant for HVAC work' as notes
FROM products p
CROSS JOIN business_services bs
WHERE p.business_id = '550e8400-e29b-41d4-a716-446655440010'
  AND bs.business_id = '550e8400-e29b-41d4-a716-446655440010'
  AND p.name ILIKE '%R-410A%'
  AND (bs.service_name ILIKE '%hvac%' OR bs.service_name ILIKE '%heat%' OR bs.service_name ILIKE '%installation%')
LIMIT 5;

-- Create associations for other products with relevant services
INSERT INTO product_service_associations (business_id, product_id, service_id, association_type, display_order, is_featured, notes)
SELECT 
  '550e8400-e29b-41d4-a716-446655440010'::uuid as business_id,
  p.id as product_id,
  bs.id as service_id,
  CASE 
    WHEN p.name ILIKE '%thermostat%' AND bs.service_name ILIKE '%installation%' THEN 'required'
    WHEN p.name ILIKE '%filter%' AND bs.service_name ILIKE '%maintenance%' THEN 'required'
    WHEN p.name ILIKE '%thermostat%' THEN 'recommended'
    ELSE 'optional'
  END as association_type,
  ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY bs.service_name) as display_order,
  false as is_featured,
  CONCAT('Product for ', bs.service_name) as notes
FROM products p
CROSS JOIN business_services bs
WHERE p.business_id = '550e8400-e29b-41d4-a716-446655440010'
  AND bs.business_id = '550e8400-e29b-41d4-a716-446655440010'
  AND p.name NOT ILIKE '%R-410A%'  -- Skip the refrigerant we already added
  AND (
    (p.name ILIKE '%thermostat%' AND bs.service_name ILIKE '%hvac%') OR
    (p.name ILIKE '%filter%' AND bs.service_name ILIKE '%maintenance%') OR
    (bs.service_name ILIKE '%installation%' OR bs.service_name ILIKE '%repair%')
  )
LIMIT 15;

-- Add some upsell and accessory associations
INSERT INTO product_service_associations (business_id, product_id, service_id, association_type, display_order, is_featured, notes)
SELECT 
  '550e8400-e29b-41d4-a716-446655440010'::uuid as business_id,
  p.id as product_id,
  bs.id as service_id,
  'upsell' as association_type,
  99 as display_order,
  false as is_featured,
  'Upgrade opportunity during service' as notes
FROM products p
CROSS JOIN business_services bs
WHERE p.business_id = '550e8400-e29b-41d4-a716-446655440010'
  AND bs.business_id = '550e8400-e29b-41d4-a716-446655440010'
  AND bs.service_name ILIKE '%repair%'
LIMIT 5;
