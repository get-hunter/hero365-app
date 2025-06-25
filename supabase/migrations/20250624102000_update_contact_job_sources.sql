-- Migration to update contact and job source values to new standardized format
-- This updates existing data to match the new ContactSource and JobSource enums

-- First, drop the existing check constraints
ALTER TABLE "public"."contacts" DROP CONSTRAINT IF EXISTS "contacts_source_check";
ALTER TABLE "public"."jobs" DROP CONSTRAINT IF EXISTS "jobs_source_check";

-- Update contacts table source values
UPDATE contacts SET 
  source = CASE 
    WHEN source = 'advertising' THEN 'google_ads'
    WHEN source = 'cold_call' THEN 'phone_call'
    WHEN source = 'marketing' THEN 'email_marketing'
    ELSE source
  END
WHERE source IN ('advertising', 'cold_call', 'marketing');

-- Update jobs table source values  
UPDATE jobs SET
  source = CASE
    WHEN source = 'advertising' THEN 'google_ads'
    WHEN source = 'cold_call' THEN 'phone_call'
    WHEN source = 'marketing' THEN 'email_marketing'
    ELSE source
  END
WHERE source IN ('advertising', 'cold_call', 'marketing');

-- Recreate the check constraints with the new values
ALTER TABLE "public"."contacts" ADD CONSTRAINT "contacts_source_check" 
CHECK (((source)::text = ANY ((ARRAY[
  'website'::character varying,
  'google_ads'::character varying,
  'social_media'::character varying,
  'referral'::character varying,
  'phone_call'::character varying,
  'walk_in'::character varying,
  'email_marketing'::character varying,
  'trade_show'::character varying,
  'direct_mail'::character varying,
  'yellow_pages'::character varying,
  'partner'::character varying,
  'existing_customer'::character varying,
  'cold_outreach'::character varying,
  'event'::character varying,
  'direct'::character varying,
  'other'::character varying
])::text[])));

ALTER TABLE "public"."contacts" VALIDATE CONSTRAINT "contacts_source_check";

ALTER TABLE "public"."jobs" ADD CONSTRAINT "jobs_source_check" 
CHECK (((source)::text = ANY ((ARRAY[
  'website'::character varying,
  'google_ads'::character varying,
  'social_media'::character varying,
  'referral'::character varying,
  'phone_call'::character varying,
  'walk_in'::character varying,
  'email_marketing'::character varying,
  'trade_show'::character varying,
  'direct_mail'::character varying,
  'yellow_pages'::character varying,
  'repeat_customer'::character varying,
  'partner'::character varying,
  'existing_customer'::character varying,
  'cold_outreach'::character varying,
  'emergency_call'::character varying,
  'event'::character varying,
  'direct'::character varying,
  'other'::character varying
])::text[])));

ALTER TABLE "public"."jobs" VALIDATE CONSTRAINT "jobs_source_check";

-- Log the migration result
DO $$
DECLARE
  contacts_count integer;
  jobs_count integer;
BEGIN
  SELECT COUNT(*) INTO contacts_count FROM contacts WHERE source IN ('google_ads', 'phone_call', 'email_marketing');
  SELECT COUNT(*) INTO jobs_count FROM jobs WHERE source IN ('google_ads', 'phone_call', 'email_marketing');
  
  RAISE NOTICE 'Lead source migration completed successfully.';
  RAISE NOTICE 'Contacts with updated sources: %', contacts_count;
  RAISE NOTICE 'Jobs with updated sources: %', jobs_count;
END $$; 