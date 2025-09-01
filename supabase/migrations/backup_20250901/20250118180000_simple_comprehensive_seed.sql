-- Simple comprehensive seed data for testing public API endpoints
-- This focuses on the essential data needed for the public professional API

-- Update existing business with more comprehensive data
UPDATE businesses 
SET 
  description = 'Premier HVAC services for Austin homes and businesses. Specializing in energy-efficient installations, emergency repairs, and preventative maintenance.',
  service_areas = ARRAY['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'],
  residential_trades = ARRAY['HVAC'],
  business_license = 'TACLA123456',
  last_modified = NOW()
WHERE id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef';

-- Insert some contacts for the existing business
INSERT INTO contacts (id, business_id, first_name, last_name, email, phone, address, contact_type, is_active, created_date, last_modified) VALUES
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'John', 'Smith', 'john.smith@email.com', '(512) 555-0101', '{"street": "123 Oak Street", "city": "Austin", "state": "TX", "postal_code": "78701"}'::jsonb, 'CUSTOMER', true, NOW(), NOW()),
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'Mary', 'Johnson', 'mary.johnson@email.com', '(512) 555-0102', '{"street": "456 Pine Avenue", "city": "Round Rock", "state": "TX", "postal_code": "78664"}'::jsonb, 'CUSTOMER', true, NOW(), NOW()),
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'Robert', 'Davis', 'robert.davis@email.com', '(512) 555-0103', '{"street": "789 Cedar Lane", "city": "Cedar Park", "state": "TX", "postal_code": "78613"}'::jsonb, 'LEAD', true, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert some jobs for the existing business
INSERT INTO jobs (id, business_id, contact_id, job_number, title, description, status, priority, scheduled_start, job_address, is_active, created_date, last_modified) 
SELECT 
  gen_random_uuid(),
  'a1b2c3d4-e5f6-7890-1234-567890abcdef',
  c.id,
  job_data.job_number,
  job_data.title,
  job_data.description,
  job_data.status,
  job_data.priority,
  job_data.scheduled_start::timestamp with time zone,
  job_data.job_address::jsonb,
  true,
  NOW(),
  NOW()
FROM (
  VALUES
  ('JOB-2025-001', 'AC System Maintenance', 'Annual maintenance check for residential AC system', 'SCHEDULED', 'MEDIUM', '2025-01-22 10:00:00', '{"street": "123 Oak Street", "city": "Austin", "state": "TX", "postal_code": "78701"}'),
  ('JOB-2025-002', 'Emergency Heater Repair', 'Heater not working - emergency call', 'IN_PROGRESS', 'HIGH', '2025-01-19 14:00:00', '{"street": "456 Pine Avenue", "city": "Round Rock", "state": "TX", "postal_code": "78664"}'),
  ('JOB-2025-003', 'New HVAC Installation', 'Install new HVAC system in new construction', 'PENDING', 'MEDIUM', '2025-01-25 09:00:00', '{"street": "789 Cedar Lane", "city": "Cedar Park", "state": "TX", "postal_code": "78613"}')
) AS job_data(job_number, title, description, status, priority, scheduled_start, job_address)
CROSS JOIN (
  SELECT id FROM contacts 
  WHERE business_id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef' 
  AND contact_type = 'CUSTOMER' 
  LIMIT 1
) c
ON CONFLICT (id) DO NOTHING;

-- Insert some estimates for the existing business
INSERT INTO estimates (id, business_id, contact_id, estimate_number, title, description, subtotal, tax_amount, total_amount, status, valid_until, client_name, created_by, created_date, last_modified)
SELECT 
  gen_random_uuid(),
  'a1b2c3d4-e5f6-7890-1234-567890abcdef',
  c.id,
  est_data.estimate_number,
  est_data.title,
  est_data.description,
  est_data.subtotal,
  est_data.tax_amount,
  est_data.total_amount,
  est_data.status,
  est_data.valid_until::timestamp with time zone,
  CONCAT(c.first_name, ' ', c.last_name),
  'system',
  NOW(),
  NOW()
FROM (
  VALUES
  ('EST-2025-001', 'HVAC System Replacement', 'Complete HVAC system replacement including installation', 4500.00, 371.25, 4871.25, 'sent', '2025-02-18'),
  ('EST-2025-002', 'Duct Cleaning Service', 'Professional duct cleaning and sanitization', 350.00, 28.88, 378.88, 'approved', '2025-02-15')
) AS est_data(estimate_number, title, description, subtotal, tax_amount, total_amount, status, valid_until)
CROSS JOIN (
  SELECT id, first_name, last_name FROM contacts 
  WHERE business_id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef' 
  AND contact_type = 'CUSTOMER' 
  LIMIT 1
) c
ON CONFLICT (id) DO NOTHING;

-- Insert some invoices for the existing business
INSERT INTO invoices (id, business_id, contact_id, invoice_number, title, description, subtotal, tax_amount, total_amount, amount_paid, amount_due, amount_refunded, late_fee_amount, status, due_date, client_name, created_by, created_date, last_modified)
SELECT 
  gen_random_uuid(),
  'a1b2c3d4-e5f6-7890-1234-567890abcdef',
  c.id,
  inv_data.invoice_number,
  inv_data.title,
  inv_data.description,
  inv_data.subtotal,
  inv_data.tax_amount,
  inv_data.total_amount,
  inv_data.amount_paid,
  inv_data.amount_due,
  inv_data.amount_refunded,
  inv_data.late_fee_amount,
  inv_data.status,
  inv_data.due_date::timestamp with time zone,
  CONCAT(c.first_name, ' ', c.last_name),
  'system',
  NOW(),
  NOW()
FROM (
  VALUES
  ('INV-2025-001', 'AC Repair Service', 'Emergency AC repair - replaced compressor', 450.00, 37.13, 487.13, 487.13, 0.00, 0.00, 0.00, 'paid', '2025-02-18'),
  ('INV-2025-002', 'Maintenance Service', 'Annual HVAC maintenance and tune-up', 199.00, 16.42, 215.42, 0.00, 215.42, 0.00, 0.00, 'sent', '2025-02-15')
) AS inv_data(invoice_number, title, description, subtotal, tax_amount, total_amount, amount_paid, amount_due, amount_refunded, late_fee_amount, status, due_date)
CROSS JOIN (
  SELECT id, first_name, last_name FROM contacts 
  WHERE business_id = 'a1b2c3d4-e5f6-7890-1234-567890abcdef' 
  AND contact_type = 'CUSTOMER' 
  LIMIT 1
) c
ON CONFLICT (id) DO NOTHING;

-- Insert a supplier for the existing business
INSERT INTO suppliers (id, business_id, supplier_code, name, email, phone, billing_address, supplier_type, primary_contact_name, primary_contact_email, primary_contact_phone, status, created_at, updated_at) VALUES
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'HVAC-001', 'HVAC Supply Co', 'info@hvacsupply.com', '(512) 555-1001', '{"street": "100 Industrial Blvd", "city": "Austin", "state": "TX", "postal_code": "78744"}'::jsonb, 'EQUIPMENT', 'Tom Wilson', 'tom@hvacsupply.com', '(512) 555-1001', 'active', NOW(), NOW()),
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'FILT-001', 'Filter Express', 'info@filterexpress.com', '(512) 555-1002', '{"street": "200 Commerce St", "city": "Round Rock", "state": "TX", "postal_code": "78664"}'::jsonb, 'PARTS', 'Sarah Chen', 'sarah@filterexpress.com', '(512) 555-1002', 'active', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Success message
SELECT 'Simple comprehensive seed data applied successfully! 🎉' as message,
       'Enhanced existing business with contacts, jobs, estimates, invoices, and suppliers' as summary;
