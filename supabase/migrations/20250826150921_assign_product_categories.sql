-- Assign product categories to e-commerce products
DO $$
DECLARE
    default_business_id UUID := 'a1b2c3d4-e5f6-7890-1234-567890abcdef';
    hvac_category_id UUID;
    updated_count INTEGER;
BEGIN
    -- Find the HVAC Systems category
    SELECT id INTO hvac_category_id 
    FROM product_categories 
    WHERE business_id = default_business_id AND name = 'HVAC Systems' 
    LIMIT 1;

    IF hvac_category_id IS NOT NULL THEN
        -- Update e-commerce products to use HVAC category
        UPDATE products SET 
            category_id = hvac_category_id
        WHERE business_id = default_business_id 
        AND sku IN ('HP-3TON-SEER16', 'WH-40GAL-GAS', 'EV-CHARGER-L2-40A')
        AND category_id IS NULL;
        
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        RAISE NOTICE '✅ Assigned % products to HVAC Systems category', updated_count;
    ELSE
        RAISE NOTICE '❌ HVAC Systems category not found';
    END IF;

END $$;
