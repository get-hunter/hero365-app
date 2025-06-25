-- Update Foreign Keys to Point to Public Users Table
-- This migration updates all foreign key constraints to reference public.users instead of auth.users
-- This allows for easier development without complex auth integration

-- Step 1: Drop existing foreign key constraints that reference auth.users (both naming conventions)
ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_id_fkey;
ALTER TABLE business_memberships DROP CONSTRAINT IF EXISTS business_memberships_user_id_fkey;
ALTER TABLE business_memberships DROP CONSTRAINT IF EXISTS fk_business_memberships_user_id;
ALTER TABLE business_memberships DROP CONSTRAINT IF EXISTS fk_business_memberships_invited_by;
ALTER TABLE business_invitations DROP CONSTRAINT IF EXISTS business_invitations_invited_by_fkey;
ALTER TABLE business_invitations DROP CONSTRAINT IF EXISTS fk_business_invitations_invited_by;
ALTER TABLE contacts DROP CONSTRAINT IF EXISTS contacts_created_by_fkey;
ALTER TABLE contacts DROP CONSTRAINT IF EXISTS fk_contacts_created_by;
ALTER TABLE contacts DROP CONSTRAINT IF EXISTS contacts_assigned_to_fkey;
ALTER TABLE contacts DROP CONSTRAINT IF EXISTS fk_contacts_assigned_to;
ALTER TABLE contact_activities DROP CONSTRAINT IF EXISTS contact_activities_performed_by_fkey;
ALTER TABLE contact_activities DROP CONSTRAINT IF EXISTS fk_contact_activities_performed_by;
ALTER TABLE contact_notes DROP CONSTRAINT IF EXISTS contact_notes_created_by_fkey;
ALTER TABLE contact_notes DROP CONSTRAINT IF EXISTS fk_contact_notes_created_by;
ALTER TABLE jobs DROP CONSTRAINT IF EXISTS jobs_created_by_fkey;
ALTER TABLE jobs DROP CONSTRAINT IF EXISTS fk_jobs_created_by;
ALTER TABLE job_activities DROP CONSTRAINT IF EXISTS job_activities_user_id_fkey;
ALTER TABLE job_activities DROP CONSTRAINT IF EXISTS fk_job_activities_user_id;
ALTER TABLE job_notes DROP CONSTRAINT IF EXISTS job_notes_user_id_fkey;
ALTER TABLE job_notes DROP CONSTRAINT IF EXISTS fk_job_notes_user_id;
ALTER TABLE departments DROP CONSTRAINT IF EXISTS departments_manager_id_fkey;
ALTER TABLE businesses DROP CONSTRAINT IF EXISTS businesses_owner_id_fkey;
ALTER TABLE contact_segments DROP CONSTRAINT IF EXISTS contact_segments_created_by_fkey;

-- Step 2: Make public.users independent (remove auth.users reference)
ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_id_fkey;

-- Step 3: Add new foreign key constraints pointing to public.users
ALTER TABLE business_memberships 
ADD CONSTRAINT business_memberships_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

ALTER TABLE business_invitations 
ADD CONSTRAINT business_invitations_invited_by_fkey 
FOREIGN KEY (invited_by) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE contacts 
ADD CONSTRAINT contacts_created_by_fkey 
FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE contacts 
ADD CONSTRAINT contacts_assigned_to_fkey 
FOREIGN KEY (assigned_to) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE contact_activities 
ADD CONSTRAINT contact_activities_performed_by_fkey 
FOREIGN KEY (performed_by) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE contact_notes 
ADD CONSTRAINT contact_notes_created_by_fkey 
FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE jobs 
ADD CONSTRAINT jobs_created_by_fkey 
FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE job_activities 
ADD CONSTRAINT job_activities_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE job_notes 
ADD CONSTRAINT job_notes_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE departments 
ADD CONSTRAINT departments_manager_id_fkey 
FOREIGN KEY (manager_id) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE businesses 
ADD CONSTRAINT businesses_owner_id_fkey 
FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE CASCADE;

ALTER TABLE contact_segments 
ADD CONSTRAINT contact_segments_created_by_fkey 
FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;

-- Step 4: Remove the auth.users sync function and trigger (for development mode)
DROP TRIGGER IF EXISTS sync_user_data_trigger ON auth.users;
DROP FUNCTION IF EXISTS sync_user_data();

-- Step 5: Update users table to remove auth dependency 
-- (Keep it simple for development)
COMMENT ON TABLE public.users IS 'User profiles for development - independent of auth.users'; 