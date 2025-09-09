-- Backfill service_slug and category defaults while inserting missing services

BEGIN;

WITH all_business_trades AS (
  SELECT b.id AS business_id, b.primary_trade_slug AS trade_slug
  FROM businesses b
  WHERE b.primary_trade_slug IS NOT NULL
  UNION
  SELECT b.id AS business_id, p.slug AS trade_slug
  FROM businesses b
  JOIN LATERAL unnest(COALESCE(b.secondary_trades, ARRAY[]::text[])) AS st(name) ON TRUE
  JOIN trade_profiles p ON lower(p.name) = lower(st.name)
),
missing_services AS (
  SELECT abt.business_id,
         ta.trade_slug,
         ta.slug        AS canonical_slug,
         ta.name        AS service_name,
         -- slugify name for service_slug
         lower(regexp_replace(regexp_replace(ta.name, '[^a-zA-Z0-9\s-]', '', 'g'), '\\s+', '-', 'g')) AS service_slug
  FROM all_business_trades abt
  JOIN trade_activities ta ON ta.trade_slug = abt.trade_slug
  LEFT JOIN business_services bs
    ON bs.business_id = abt.business_id
   AND bs.canonical_slug = ta.slug
  WHERE bs.business_id IS NULL
)
INSERT INTO business_services (
  business_id,
  canonical_slug,
  service_name,
  service_slug,
  trade_slug,
  is_active,
  sort_order,
  is_featured,
  created_at,
  updated_at
)
SELECT ms.business_id,
       ms.canonical_slug,
       ms.service_name,
       ms.service_slug,
       ms.trade_slug,
       TRUE,
       0,
       FALSE,
       NOW(),
       NOW()
FROM missing_services ms;

COMMIT;


