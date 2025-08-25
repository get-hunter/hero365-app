-- Clean up products table - Remove service-related data and columns
-- Since services are now handled by the service template system
-- Date: 2025-01-25
-- Purpose: Remove service-related attributes from products table

-- Step 1: Verify service data has been migrated (safety check)
DO $$
DECLARE
    service_count INTEGER;
    business_service_count INTEGER;
BEGIN
    -- Count services in products table
    SELECT COUNT(*) INTO service_count 
    FROM products 
    WHERE is_service = true OR product_type = 'service';
    
    -- Count migrated services in business_services table
    SELECT COUNT(*) INTO business_service_count 
    FROM business_services 
    WHERE custom_fields->>'migrated_from_products' = 'true';
    
    -- Log migration status
    RAISE NOTICE 'Services in products table: %', service_count;
    RAISE NOTICE 'Migrated services in business_services table: %', business_service_count;
    
    -- Safety check - ensure migration happened
    IF business_service_count = 0 AND service_count > 0 THEN
        RAISE EXCEPTION 'Migration verification failed: Found % services in products but 0 migrated services in business_services', service_count;
    END IF;
    
    RAISE NOTICE '✓ Migration verification passed - safe to clean up products table';
END $$;

-- Step 2: Remove service records from products table
-- These have been migrated to business_services table
DELETE FROM products 
WHERE is_service = true OR product_type = 'service';

-- Step 3: Remove service-related columns
-- These are now handled by the service template system

-- Remove service flag column
ALTER TABLE products DROP COLUMN IF EXISTS is_service;

-- Remove product_type column (products table should only contain products)
ALTER TABLE products DROP COLUMN IF EXISTS product_type;

-- Remove service-specific pricing columns
ALTER TABLE products DROP COLUMN IF EXISTS pricing_model;
ALTER TABLE products DROP COLUMN IF EXISTS minimum_price;

-- Remove markup_percentage (more relevant for services than inventory products)
ALTER TABLE products DROP COLUMN IF EXISTS markup_percentage;

-- Step 4: Update constraints and defaults for products-only table
-- Ensure track_inventory defaults to true for physical products
ALTER TABLE products ALTER COLUMN track_inventory SET DEFAULT true;

-- Ensure is_digital defaults to false for physical products  
ALTER TABLE products ALTER COLUMN is_digital SET DEFAULT false;

-- Step 5: Add helpful constraints for physical products
-- Ensure SKU is meaningful for products
ALTER TABLE products ADD CONSTRAINT products_sku_not_empty 
    CHECK (LENGTH(TRIM(sku)) > 0);

-- Ensure unit_of_measure is appropriate for products
ALTER TABLE products ADD CONSTRAINT products_valid_unit_of_measure 
    CHECK (unit_of_measure IN ('each', 'box', 'case', 'piece', 'unit', 'set', 'kit', 'roll', 'foot', 'meter', 'pound', 'kilogram', 'gallon', 'liter'));

-- Step 6: Update any remaining data inconsistencies
-- Ensure all remaining records have appropriate defaults
UPDATE products SET
    track_inventory = COALESCE(track_inventory, true),
    is_digital = COALESCE(is_digital, false),
    is_taxable = COALESCE(is_taxable, true),
    unit_of_measure = COALESCE(unit_of_measure, 'each')
WHERE track_inventory IS NULL 
   OR is_digital IS NULL 
   OR is_taxable IS NULL 
   OR unit_of_measure IS NULL;

-- Step 7: Add comments for clarity
COMMENT ON TABLE products IS 'Physical products and inventory items only. Services are managed via the service_templates system.';

COMMENT ON COLUMN products.sku IS 'Stock Keeping Unit - unique identifier for physical products';
COMMENT ON COLUMN products.track_inventory IS 'Always true for physical products - inventory tracking is essential';
COMMENT ON COLUMN products.is_digital IS 'Physical products should be false - digital products handled separately';
COMMENT ON COLUMN products.current_stock IS 'Current inventory level for this physical product';
COMMENT ON COLUMN products.unit_of_measure IS 'How this physical product is measured/sold (each, box, case, etc.)';

-- Step 8: Log completion summary
DO $$
DECLARE
    remaining_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO remaining_count FROM products;
    RAISE NOTICE '=== Products Table Cleanup Complete ===';
    RAISE NOTICE 'Remaining physical products: %', remaining_count;
    RAISE NOTICE 'Services moved to: service_templates + business_services tables';
    RAISE NOTICE 'Products table now handles: Physical products and inventory only';
    RAISE NOTICE '=======================================';
END $$;
