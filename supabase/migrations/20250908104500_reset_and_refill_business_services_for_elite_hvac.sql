-- Reset and refill business_services for Elite HVAC Austin (development data)
BEGIN;

-- 1) Identify business
WITH biz AS (
  SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1
),
all_trades AS (
  SELECT b.id AS business_id, b.primary_trade_slug AS trade_slug
  FROM businesses b JOIN biz ON biz.id = b.id
  WHERE b.primary_trade_slug IS NOT NULL
  UNION
  SELECT b.id AS business_id, p.slug AS trade_slug
  FROM businesses b JOIN biz ON biz.id = b.id
  JOIN LATERAL unnest(COALESCE(b.secondary_trades, ARRAY[]::text[])) AS st(name) ON TRUE
  JOIN trade_profiles p ON lower(p.name) = lower(st.name)
)
-- 2) Delete existing services for this business
DELETE FROM business_services
WHERE business_id IN (SELECT id FROM biz);

-- 3) Refill from trade_activities for those trades
WITH biz2 AS (
  SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1
),
all_trades2 AS (
  SELECT b.id AS business_id, b.primary_trade_slug AS trade_slug
  FROM businesses b JOIN biz2 ON biz2.id = b.id
  WHERE b.primary_trade_slug IS NOT NULL
  UNION
  SELECT b.id AS business_id, p.slug AS trade_slug
  FROM businesses b JOIN biz2 ON biz2.id = b.id
  JOIN LATERAL unnest(COALESCE(b.secondary_trades, ARRAY[]::text[])) AS st(name) ON TRUE
  JOIN trade_profiles p ON lower(p.name) = lower(st.name)
),
ins AS (
  SELECT t.business_id,
         ta.slug        AS canonical_slug,
         ta.name        AS service_name,
         ta.slug        AS service_slug,
         ta.trade_slug  AS trade_slug,
         TRUE           AS is_active,
         0              AS sort_order,
         FALSE          AS is_featured,
         NOW()          AS created_at,
         NOW()          AS updated_at
  FROM all_trades2 t
  JOIN trade_activities ta ON ta.trade_slug = t.trade_slug
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
SELECT * FROM ins
ON CONFLICT (business_id, canonical_slug) DO NOTHING;

COMMIT;

