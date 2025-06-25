-- Fix invalid lifecycle_stage values in existing data
-- Convert invalid enum values to valid ones

-- Fix lifecycle_stage values that match relationship_status values
UPDATE contacts 
SET lifecycle_stage = 'awareness'
WHERE lifecycle_stage = 'prospect';

UPDATE contacts 
SET lifecycle_stage = 'interest'
WHERE lifecycle_stage = 'qualified_lead';

UPDATE contacts 
SET lifecycle_stage = 'consideration'
WHERE lifecycle_stage = 'opportunity';

UPDATE contacts 
SET lifecycle_stage = 'customer'
WHERE lifecycle_stage = 'active_client';

UPDATE contacts 
SET lifecycle_stage = 'retention'
WHERE lifecycle_stage = 'past_client';

UPDATE contacts 
SET lifecycle_stage = 'consideration'
WHERE lifecycle_stage = 'lost_lead';

UPDATE contacts 
SET lifecycle_stage = 'retention'
WHERE lifecycle_stage = 'inactive';

-- Fix any other invalid lifecycle_stage values to default 'awareness'
UPDATE contacts 
SET lifecycle_stage = 'awareness'
WHERE lifecycle_stage NOT IN ('awareness', 'interest', 'consideration', 'decision', 'retention', 'customer'); 