-- Migrate existing products to new service template system
-- This preserves existing business data while transitioning to the new architecture

-- First, enable the similarity extension for fuzzy matching
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create a temporary mapping table to track migration
CREATE TEMP TABLE migration_log (
    product_id uuid,
    business_service_id uuid,
    template_id uuid,
    match_method varchar(50),
    confidence_score numeric(3,2)
);

-- Step 1: Create fallback categories for services that don't match existing categories
INSERT INTO service_categories (name, description, slug, trade_types, category_type, icon, sort_order) VALUES 
('Other Services', 'Miscellaneous professional services', 'other-services', ARRAY['hvac', 'plumbing', 'electrical', 'landscaping', 'roofing'], 'service_type', 'more-horizontal', 998),
('Custom Products', 'Business-specific products and materials', 'custom-products', ARRAY['hvac', 'plumbing', 'electrical'], 'equipment', 'package', 999)
ON CONFLICT (slug) DO NOTHING;

-- Step 2: Migrate products to business_services with template matching
WITH product_migration AS (
    SELECT 
        p.id as product_id,
        p.business_id,
        p.name,
        p.description,
        p.unit_price,
        p.cost_price,
        p.markup_percentage,
        p.unit_of_measure,
        p.is_service,
        p.is_featured,
        p.tags,
        p.created_at,
        p.updated_at,
        b.residential_trades,
        b.commercial_trades,
        b.trade_category,
        
        -- Try exact keyword matching for common services first (highest priority)
        (SELECT st.id
         FROM service_templates st
         WHERE (
               (LOWER(p.name) LIKE '%ac repair%' AND st.name LIKE '%AC Repair%') OR
               (LOWER(p.name) LIKE '%hvac%' AND LOWER(st.name) LIKE '%hvac%') OR
               (LOWER(p.name) LIKE '%furnace%' AND st.name LIKE '%Furnace%') OR
               (LOWER(p.name) LIKE '%water heater%' AND st.name LIKE '%Water Heater%') OR
               (LOWER(p.name) LIKE '%plumbing%' AND LOWER(st.name) LIKE '%plumbing%') OR
               (LOWER(p.name) LIKE '%electrical%' AND LOWER(st.name) LIKE '%electrical%') OR
               (LOWER(p.name) LIKE '%drain%' AND st.name LIKE '%Drain%') OR
               (LOWER(p.name) LIKE '%emergency%' AND st.name LIKE '%Emergency%') OR
               (LOWER(p.name) LIKE '%maintenance%' AND st.name LIKE '%Maintenance%') OR
               (LOWER(p.name) LIKE '%installation%' AND st.name LIKE '%Installation%') OR
               (LOWER(p.name) LIKE '%repair%' AND st.name LIKE '%Repair%')
           )
           AND (
               st.trade_types && COALESCE(b.residential_trades, ARRAY[]::text[]) OR
               st.trade_types && COALESCE(b.commercial_trades, ARRAY[]::text[])
           )
         ORDER BY 
           CASE 
             WHEN LOWER(p.name) = LOWER(st.name) THEN 1
             ELSE 2
           END
         LIMIT 1
        ) as keyword_template_match,
        
        -- Try to match to service templates by name similarity (fuzzy matching)  
        (SELECT st.id
         FROM service_templates st 
         WHERE similarity(LOWER(p.name), LOWER(st.name)) > 0.5
           AND (
               st.trade_types && COALESCE(b.residential_trades, ARRAY[]::text[]) OR
               st.trade_types && COALESCE(b.commercial_trades, ARRAY[]::text[])
           )
         ORDER BY similarity(LOWER(p.name), LOWER(st.name)) DESC 
         LIMIT 1
        ) as fuzzy_template_match,

        -- Get similarity score for the best fuzzy match
        (SELECT similarity(LOWER(p.name), LOWER(st.name))
         FROM service_templates st 
         WHERE similarity(LOWER(p.name), LOWER(st.name)) > 0.5
           AND (
               st.trade_types && COALESCE(b.residential_trades, ARRAY[]::text[]) OR
               st.trade_types && COALESCE(b.commercial_trades, ARRAY[]::text[])
           )
         ORDER BY similarity(LOWER(p.name), LOWER(st.name)) DESC 
         LIMIT 1
        ) as fuzzy_match_score,
        
        -- Map to appropriate category based on business trade and product type
        (SELECT sc.id 
         FROM service_categories sc 
         WHERE (
               sc.trade_types && COALESCE(b.residential_trades, ARRAY[]::text[]) OR
               sc.trade_types && COALESCE(b.commercial_trades, ARRAY[]::text[]) OR
               sc.trade_types && ARRAY[b.trade_category]::text[]
           )
           AND CASE 
               WHEN p.is_service OR p.product_type = 'service' THEN sc.category_type = 'service_type'
               ELSE sc.category_type IN ('equipment', 'service_type')
           END
           AND sc.slug NOT IN ('custom-services', 'other-services', 'custom-products') -- Prefer specific categories
         ORDER BY 
           -- Prefer categories that match business trade exactly
           CASE WHEN sc.trade_types = COALESCE(b.residential_trades, b.commercial_trades) THEN 1 ELSE 2 END,
           sc.sort_order
         LIMIT 1
        ) as mapped_category_id

    FROM products p
    JOIN businesses b ON b.id = p.business_id
    WHERE p.is_active = true
),

-- Choose the best template match (keyword match trumps fuzzy match)
template_selection AS (
    SELECT 
        *,
        COALESCE(
            keyword_template_match, 
            CASE WHEN fuzzy_match_score > 0.7 THEN fuzzy_template_match ELSE NULL END
        ) as final_template_id,
        CASE 
            WHEN keyword_template_match IS NOT NULL THEN 'keyword_match'
            WHEN fuzzy_match_score > 0.7 THEN 'fuzzy_match' 
            ELSE 'no_match'
        END as match_method,
        COALESCE(fuzzy_match_score, 0) as confidence_score
    FROM product_migration
)

-- Insert into business_services
INSERT INTO business_services (
    business_id,
    template_id,
    category_id, 
    name,
    description,
    pricing_model,
    unit_price,
    minimum_price,
    unit_of_measure,
    markup_percentage,
    cost_price,
    is_active,
    is_featured,
    is_emergency,
    custom_fields,
    sort_order,
    created_at,
    updated_at
)
SELECT 
    ts.business_id,
    ts.final_template_id,
    -- Use mapped category or fallback to appropriate default
    COALESCE(
        ts.mapped_category_id,
        -- Fallback based on service vs product
        CASE 
            WHEN ts.is_service THEN (SELECT id FROM service_categories WHERE slug = 'other-services' LIMIT 1)
            ELSE (SELECT id FROM service_categories WHERE slug = 'custom-products' LIMIT 1)
        END
    ),
    ts.name,
    COALESCE(ts.description, 'Migrated from products'),
    -- Determine pricing model based on unit price
    CASE 
        WHEN ts.unit_price = 0 OR ts.unit_price IS NULL THEN 'quote_required'
        WHEN ts.unit_of_measure = 'hour' THEN 'hourly'
        WHEN ts.unit_of_measure IN ('each', 'service', 'unit', 'system') THEN 'fixed'
        ELSE 'per_unit'
    END,
    COALESCE(ts.unit_price, 0),
    CASE WHEN ts.unit_price > 0 THEN ts.unit_price * 0.8 ELSE NULL END, -- Set minimum price as 80% of unit price
    COALESCE(ts.unit_of_measure, 'service'),
    ts.markup_percentage,
    ts.cost_price,
    true, -- is_active
    COALESCE(ts.is_featured, false),
    -- Mark as emergency if name contains emergency keywords
    CASE 
        WHEN LOWER(ts.name) LIKE '%emergency%' OR LOWER(ts.name) LIKE '%urgent%' OR LOWER(ts.name) LIKE '%24/7%' THEN true
        ELSE false
    END,
    -- Store migration metadata and original tags
    jsonb_build_object(
        'migrated_from_products', true,
        'original_product_id', ts.product_id,
        'migration_date', now(),
        'original_tags', COALESCE(ts.tags, ARRAY[]::text[]),
        'match_method', ts.match_method,
        'confidence_score', ts.confidence_score
    ),
    -- Use created_at as sort order (newer services first)
    EXTRACT(epoch FROM ts.created_at)::integer,
    ts.created_at,
    ts.updated_at
FROM template_selection ts
RETURNING id, business_id, template_id, name;

-- Step 3: Track template adoptions for services that matched templates
WITH adoption_tracking AS (
    SELECT 
        bs.template_id,
        bs.business_id,
        bs.id as business_service_id,
        bs.custom_fields->>'match_method' as match_method,
        (bs.custom_fields->>'confidence_score')::numeric as confidence_score,
        st.name as template_name,
        st.default_unit_price as template_price,
        bs.unit_price as business_price,
        st.description as template_description,
        bs.description as business_description
    FROM business_services bs
    JOIN service_templates st ON bs.template_id = st.id
    WHERE bs.template_id IS NOT NULL 
      AND bs.custom_fields->>'migrated_from_products' = 'true'
)
INSERT INTO service_template_adoptions (
    template_id,
    business_id, 
    business_service_id,
    customizations,
    adopted_at
)
SELECT DISTINCT ON (at.template_id, at.business_id)
    at.template_id,
    at.business_id,
    at.business_service_id,
    jsonb_build_object(
        'migration_source', 'products_table',
        'match_method', at.match_method,
        'confidence_score', at.confidence_score,
        'custom_pricing', (at.business_price IS DISTINCT FROM at.template_price),
        'custom_description', (at.business_description IS DISTINCT FROM at.template_description),
        'price_difference', CASE 
            WHEN at.template_price IS NOT NULL AND at.business_price IS NOT NULL 
            THEN at.business_price - at.template_price
            ELSE NULL
        END
    ),
    now()
FROM adoption_tracking at
ORDER BY at.template_id, at.business_id, at.confidence_score DESC NULLS LAST
ON CONFLICT (template_id, business_id) DO UPDATE SET
    customizations = EXCLUDED.customizations,
    adopted_at = GREATEST(service_template_adoptions.adopted_at, EXCLUDED.adopted_at);

-- Step 4: Update service template usage counts
UPDATE service_templates 
SET usage_count = usage_count + adoption_count
FROM (
    SELECT 
        template_id,
        COUNT(*) as adoption_count
    FROM service_template_adoptions
    WHERE template_id IS NOT NULL
    GROUP BY template_id
) uc
WHERE service_templates.id = uc.template_id;

-- Step 5: Create migration summary
CREATE TEMP TABLE migration_summary AS
SELECT 
    'Total products' as metric,
    COUNT(*) as count
FROM products 
WHERE is_active = true

UNION ALL

SELECT 
    'Successfully migrated' as metric,
    COUNT(*) as count
FROM business_services 
WHERE (custom_fields->>'migrated_from_products')::boolean = true

UNION ALL

SELECT 
    'Template matches' as metric,
    COUNT(*) as count
FROM business_services 
WHERE template_id IS NOT NULL 
  AND (custom_fields->>'migrated_from_products')::boolean = true

UNION ALL

SELECT 
    'Keyword matches' as metric,
    COUNT(*) as count
FROM business_services 
WHERE custom_fields->>'match_method' = 'keyword_match'

UNION ALL

SELECT 
    'Fuzzy matches' as metric,
    COUNT(*) as count
FROM business_services 
WHERE custom_fields->>'match_method' = 'fuzzy_match'

UNION ALL

SELECT 
    'No template match' as metric,
    COUNT(*) as count
FROM business_services 
WHERE template_id IS NULL 
  AND (custom_fields->>'migrated_from_products')::boolean = true;

-- Output migration summary (this will appear in migration logs)
DO $$
DECLARE
    summary_record RECORD;
BEGIN
    RAISE NOTICE '--- Service Template Migration Summary ---';
    FOR summary_record IN SELECT * FROM migration_summary ORDER BY count DESC LOOP
        RAISE NOTICE '% : %', summary_record.metric, summary_record.count;
    END LOOP;
    RAISE NOTICE '--- End Migration Summary ---';
END $$;

-- Step 6: Add helpful indexes for the new data
CREATE INDEX IF NOT EXISTS idx_business_services_template_adoption ON business_services (business_id, template_id) 
WHERE template_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_business_services_migration_flag ON business_services ((custom_fields->>'migrated_from_products'))
WHERE (custom_fields->>'migrated_from_products')::boolean = true;

-- Step 7: Update any business service counts/statistics
UPDATE businesses 
SET selected_features = array_append(
    COALESCE(selected_features, ARRAY[]::text[]), 
    'service_templates'
)
WHERE id IN (
    SELECT DISTINCT business_id 
    FROM business_services 
    WHERE template_id IS NOT NULL
) AND NOT ('service_templates' = ANY(COALESCE(selected_features, ARRAY[]::text[])));

-- Note: The products table is NOT dropped - it remains for backward compatibility
-- and non-service products (actual inventory items). A future migration can
-- clean up products that were successfully migrated to business_services.
