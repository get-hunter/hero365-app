-- =============================================
-- Add 'ductless' service + SEO scaffolding for demo business
-- Applies to business: 550e8400-e29b-41d4-a716-446655440010 (Elite HVAC Austin)
-- =============================================

-- 1) Ensure service exists in business_services
INSERT INTO business_services (
  business_id, service_name, service_slug, category, description,
  price_type, price_min, price_max, price_unit, is_active
)
VALUES (
  '550e8400-e29b-41d4-a716-446655440010',
  'Ductless Mini-Split Installation',
  'ductless',
  'Installation',
  'Ductless mini-split system installation and service',
  'range', 2500, 8500, 'job', true
)
ON CONFLICT (business_id, service_slug) DO NOTHING;

-- 2) Base SEO config for the service
INSERT INTO service_seo_config (
  service_name, service_slug, target_keywords, priority_score, enable_llm_enhancement,
  meta_title_template, meta_description_template
)
VALUES (
  'Ductless Mini-Split Installation',
  'ductless',
  ARRAY['ductless','mini split','ductless AC','mini split installation'],
  80,
  true,
  'Ductless Mini-Split Installation | {city} {state} | {business}',
  'Professional ductless mini-split installation in {city}, {state}. Energy-efficient comfort solutions. Free estimates.'
)
ON CONFLICT (service_slug) DO NOTHING;

-- 3) Service + Location combinations
INSERT INTO service_location_pages (
  service_slug, location_slug, page_url, priority_score, enable_llm_enhancement,
  target_keywords, monthly_search_volume, estimated_monthly_visitors, estimated_monthly_revenue
)
VALUES
('ductless', 'austin-tx', '/services/ductless/austin-tx', 90, true, ARRAY['ductless austin','mini split austin','ductless installation austin'], 1600, 800, 4000),
('ductless', 'round-rock-tx', '/services/ductless/round-rock-tx', 75, true, ARRAY['ductless round rock','mini split round rock'], 600, 300, 1500)
ON CONFLICT (service_slug, location_slug) DO NOTHING;

-- 4) Optional: normalize slugs if needed
UPDATE business_services SET service_slug = REPLACE(service_slug, '_', '-') WHERE service_slug LIKE '%_%';
UPDATE service_location_pages SET service_slug = REPLACE(service_slug, '_', '-') WHERE service_slug LIKE '%_%';

COMMIT;


