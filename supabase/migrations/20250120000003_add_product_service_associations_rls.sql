-- Add RLS policies for product_service_associations table
-- This allows public read access to product-service associations

-- Enable RLS on the table
ALTER TABLE product_service_associations ENABLE ROW LEVEL SECURITY;

-- Allow public read access to product_service_associations
-- This is needed for the public API to fetch product associations
CREATE POLICY "Allow public read access to product_service_associations" 
ON product_service_associations 
FOR SELECT 
USING (true);

-- Allow authenticated users to manage their business associations
CREATE POLICY "Allow business owners to manage their associations" 
ON product_service_associations 
FOR ALL 
USING (
  auth.uid() IN (
    SELECT owner_id 
    FROM businesses 
    WHERE id = product_service_associations.business_id
  )
);
