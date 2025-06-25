-- Fix Contacts-Users Relationship Migration
-- This migration adds foreign key constraints between contacts and public.users
-- to enable PostgREST to perform JOINs correctly

-- Add foreign key constraints from contacts to public.users
-- Note: We're adding these as nullable foreign keys since assigned_to and created_by can be NULL

-- Add foreign key for contacts.assigned_to -> public.users.id
ALTER TABLE public.contacts 
ADD CONSTRAINT fk_contacts_assigned_to_users 
FOREIGN KEY (assigned_to) REFERENCES public.users(id) ON DELETE SET NULL;

-- Add foreign key for contacts.created_by -> public.users.id  
ALTER TABLE public.contacts 
ADD CONSTRAINT fk_contacts_created_by_users 
FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;

-- Add indexes for better JOIN performance
CREATE INDEX IF NOT EXISTS idx_contacts_assigned_to_users ON public.contacts(assigned_to) WHERE assigned_to IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_contacts_created_by_users ON public.contacts(created_by) WHERE created_by IS NOT NULL;

-- Refresh PostgREST schema cache (this will be handled automatically on next request)
-- But we can add a comment to remind about cache refresh
COMMENT ON TABLE public.users IS 'User profiles synchronized with auth.users - enables efficient JOINs for contact user references'; 