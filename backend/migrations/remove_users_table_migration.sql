-- Remove Users and Items Tables Migration
-- This migration removes the local users and items tables and updates the schema to use Supabase Auth only

-- 1. First, remove foreign key constraints from other tables that reference users
-- Note: The items table has a foreign key to users, but we need to check if it exists

-- Check if the items table exists and has a foreign key to users
DO $$
BEGIN
    -- Drop foreign key constraint from items table if it exists
    IF EXISTS (
        SELECT 1
        FROM information_schema.table_constraints 
        WHERE constraint_name = 'item_owner_id_fkey'
        AND table_name = 'item'
    ) THEN
        ALTER TABLE item DROP CONSTRAINT item_owner_id_fkey;
        RAISE NOTICE 'Dropped foreign key constraint item_owner_id_fkey';
    END IF;
    
END $$;

-- 2. Drop the items table if it exists (since items are no longer used)
DROP TABLE IF EXISTS item CASCADE;
DROP TABLE IF EXISTS items CASCADE;

-- 3. Drop the users table if it exists
DROP TABLE IF EXISTS users CASCADE;

-- 4. Remove any item-related indexes that might still exist
DROP INDEX IF EXISTS ix_item_title;
DROP INDEX IF EXISTS ix_item_owner_id;
DROP INDEX IF EXISTS idx_items_title;
DROP INDEX IF EXISTS idx_items_owner_id;
DROP INDEX IF EXISTS idx_items_created_at;
DROP INDEX IF EXISTS idx_items_is_deleted;

-- 5. Remove any user-related indexes that might still exist
DROP INDEX IF EXISTS ix_user_email;
DROP INDEX IF EXISTS idx_users_email;
DROP INDEX IF EXISTS idx_users_phone;
DROP INDEX IF EXISTS idx_users_supabase_id;
DROP INDEX IF EXISTS idx_users_is_active;
DROP INDEX IF EXISTS idx_users_created_at;

-- 6. Remove any item-related functions or triggers
DROP FUNCTION IF EXISTS update_items_last_modified() CASCADE;
DROP TRIGGER IF EXISTS items_update_last_modified ON items;
DROP TRIGGER IF EXISTS item_update_last_modified ON item;

-- 7. Remove any user-related functions or triggers
DROP FUNCTION IF EXISTS update_users_last_modified() CASCADE;
DROP TRIGGER IF EXISTS users_update_last_modified ON users;

-- 8. Remove any item-related sequences
DROP SEQUENCE IF EXISTS item_id_seq CASCADE;
DROP SEQUENCE IF EXISTS items_id_seq CASCADE;

-- 9. Remove any user-related sequences
DROP SEQUENCE IF EXISTS user_id_seq CASCADE;

-- 10. Add comments to document the schema change
COMMENT ON TABLE businesses IS 'Business entities. owner_id references Supabase Auth user IDs (TEXT)';
COMMENT ON COLUMN businesses.owner_id IS 'Supabase Auth user ID (from auth.users.id)';

COMMENT ON TABLE business_memberships IS 'Business team memberships. user_id references Supabase Auth user IDs (TEXT)';
COMMENT ON COLUMN business_memberships.user_id IS 'Supabase Auth user ID (from auth.users.id)';

COMMENT ON TABLE business_invitations IS 'Business team invitations. invited_by references Supabase Auth user IDs (TEXT)';
COMMENT ON COLUMN business_invitations.invited_by IS 'Supabase Auth user ID (from auth.users.id)';

-- Migration complete notification
DO $$
BEGIN
    RAISE NOTICE 'Migration completed successfully:';
    RAISE NOTICE '- Removed users table';
    RAISE NOTICE '- Removed items table (no longer used)';
    RAISE NOTICE '- Removed user and item-related indexes and functions';
    RAISE NOTICE '- Updated schema to use Supabase Auth only';
    RAISE NOTICE '- All user references now point to Supabase Auth user IDs';
END $$; 