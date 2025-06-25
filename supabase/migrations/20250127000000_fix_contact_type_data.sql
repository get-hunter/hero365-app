-- Fix invalid contact_type values in existing data
-- Convert invalid enum values to valid ones

-- Update 'business' contact_type to 'customer' for commercial entities
UPDATE contacts 
SET contact_type = 'customer'
WHERE contact_type = 'business';

-- Update 'individual' contact_type to 'customer' for individual contacts
UPDATE contacts 
SET contact_type = 'customer'
WHERE contact_type = 'individual';

-- Update any other invalid contact_type values to 'prospect' as default
UPDATE contacts 
SET contact_type = 'prospect'
WHERE contact_type NOT IN ('customer', 'lead', 'prospect', 'vendor', 'partner', 'contractor');

-- Also fix any invalid relationship_status values
UPDATE contacts 
SET relationship_status = 'active_client'
WHERE relationship_status = 'active_customer';

UPDATE contacts 
SET relationship_status = 'qualified_lead'
WHERE relationship_status = 'new';

UPDATE contacts 
SET relationship_status = 'opportunity'
WHERE relationship_status = 'follow_up';

-- Fix any other invalid relationship_status values
UPDATE contacts 
SET relationship_status = 'prospect'
WHERE relationship_status NOT IN ('prospect', 'qualified_lead', 'opportunity', 'active_client', 'past_client', 'lost_lead', 'inactive'); 