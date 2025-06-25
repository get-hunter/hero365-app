-- Ensure User Data Sync Migration
-- This migration ensures all existing auth.users data is properly synced to public.users

-- First, let's make sure we have the sync function (in case it wasn't created properly)
CREATE OR REPLACE FUNCTION sync_user_data()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO public.users (
            id,
            email, 
            full_name,
            display_name,
            phone,
            is_active,
            last_sign_in,
            created_at,
            updated_at
        ) VALUES (
            NEW.id,
            NEW.email,
            COALESCE(
                NEW.raw_user_meta_data->>'full_name',
                NEW.raw_user_meta_data->>'name',
                NEW.raw_user_meta_data->>'display_name',
                SPLIT_PART(NEW.email, '@', 1)
            ),
            COALESCE(
                NEW.raw_user_meta_data->>'display_name',
                NEW.raw_user_meta_data->>'full_name', 
                NEW.raw_user_meta_data->>'name',
                SPLIT_PART(NEW.email, '@', 1)
            ),
            NEW.phone,
            NOT COALESCE(NEW.banned_until > NOW(), FALSE),
            NEW.last_sign_in_at,
            NEW.created_at,
            NOW()
        ) ON CONFLICT (id) DO UPDATE SET
            email = EXCLUDED.email,
            full_name = EXCLUDED.full_name,
            display_name = EXCLUDED.display_name,
            phone = EXCLUDED.phone,
            is_active = EXCLUDED.is_active,
            last_sign_in = EXCLUDED.last_sign_in,
            updated_at = NOW();
        RETURN NEW;
    END IF;
    
    IF TG_OP = 'UPDATE' THEN
        UPDATE public.users SET
            email = NEW.email,
            full_name = COALESCE(
                NEW.raw_user_meta_data->>'full_name',
                NEW.raw_user_meta_data->>'name',
                NEW.raw_user_meta_data->>'display_name',
                SPLIT_PART(NEW.email, '@', 1)
            ),
            display_name = COALESCE(
                NEW.raw_user_meta_data->>'display_name',
                NEW.raw_user_meta_data->>'full_name',
                NEW.raw_user_meta_data->>'name', 
                SPLIT_PART(NEW.email, '@', 1)
            ),
            phone = NEW.phone,
            is_active = NOT COALESCE(NEW.banned_until > NOW(), FALSE),
            last_sign_in = NEW.last_sign_in_at,
            updated_at = NOW()
        WHERE id = NEW.id;
        RETURN NEW;
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        DELETE FROM public.users WHERE id = OLD.id;
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Recreate the trigger to ensure it's working
DROP TRIGGER IF EXISTS sync_user_data_trigger ON auth.users;
CREATE TRIGGER sync_user_data_trigger
    AFTER INSERT OR UPDATE OR DELETE ON auth.users
    FOR EACH ROW EXECUTE FUNCTION sync_user_data();

-- Force sync of all existing auth.users data to public.users
INSERT INTO public.users (
    id,
    email,
    full_name, 
    display_name,
    phone,
    is_active,
    last_sign_in,
    created_at,
    updated_at
)
SELECT 
    au.id,
    au.email,
    COALESCE(
        au.raw_user_meta_data->>'full_name',
        au.raw_user_meta_data->>'name',
        au.raw_user_meta_data->>'display_name',
        SPLIT_PART(au.email, '@', 1)
    ) AS full_name,
    COALESCE(
        au.raw_user_meta_data->>'display_name', 
        au.raw_user_meta_data->>'full_name',
        au.raw_user_meta_data->>'name',
        SPLIT_PART(au.email, '@', 1)
    ) AS display_name,
    au.phone,
    NOT COALESCE(au.banned_until > NOW(), FALSE) AS is_active,
    au.last_sign_in_at,
    au.created_at,
    NOW()
FROM auth.users au
ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    full_name = EXCLUDED.full_name,
    display_name = EXCLUDED.display_name,
    phone = EXCLUDED.phone,
    is_active = EXCLUDED.is_active,
    last_sign_in = EXCLUDED.last_sign_in,
    updated_at = NOW();

-- Log the sync results
DO $$
DECLARE
    user_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM public.users;
    RAISE NOTICE 'Successfully synced % users to public.users table', user_count;
END $$; 