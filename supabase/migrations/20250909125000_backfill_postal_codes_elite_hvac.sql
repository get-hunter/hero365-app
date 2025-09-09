-- Backfill postal codes for Elite HVAC Austin service areas

-- Add Austin metro postal codes for Elite HVAC Austin
UPDATE service_areas 
SET postal_codes = ARRAY[
  '78701', '78702', '78703', '78704', '78705', '78712', '78717', 
  '78721', '78722', '78723', '78724', '78725', '78726', '78727', 
  '78728', '78729', '78730', '78731', '78732', '78733', '78734', 
  '78735', '78736', '78737', '78738', '78739', '78741', '78742', 
  '78744', '78745', '78746', '78747', '78748', '78749', '78750', 
  '78751', '78752', '78753', '78754', '78756', '78757', '78758', '78759'
]
WHERE business_id = (SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1)
  AND city = 'Austin'
  AND postal_codes IS NULL;

-- Add Round Rock postal codes
UPDATE service_areas 
SET postal_codes = ARRAY['78664', '78665', '78681', '78717']
WHERE business_id = (SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1)
  AND city = 'Round Rock'
  AND postal_codes IS NULL;

-- Add Cedar Park postal codes  
UPDATE service_areas 
SET postal_codes = ARRAY['78613', '78641']
WHERE business_id = (SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1)
  AND city = 'Cedar Park'
  AND postal_codes IS NULL;

-- Add Pflugerville postal codes
UPDATE service_areas 
SET postal_codes = ARRAY['78660', '78691']
WHERE business_id = (SELECT id FROM businesses WHERE name = 'Elite HVAC Austin' LIMIT 1)
  AND city = 'Pflugerville'
  AND postal_codes IS NULL;
