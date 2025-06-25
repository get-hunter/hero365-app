-- Create Users Table Migration
-- This migration creates a public.users table that mirrors essential auth.users data
-- for efficient querying and API responses

-- Create the users table
CREATE TABLE IF NOT EXISTS "public"."users" (
    "id" UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    "email" VARCHAR(320) NOT NULL,
    "full_name" VARCHAR(255),
    "display_name" VARCHAR(255) NOT NULL,
    "avatar_url" VARCHAR(500),
    "phone" VARCHAR(20),
    "is_active" BOOLEAN DEFAULT TRUE,
    "last_sign_in" TIMESTAMP WITH TIME ZONE,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS "idx_users_email" ON "public"."users" USING btree ("email");
CREATE INDEX IF NOT EXISTS "idx_users_display_name" ON "public"."users" USING btree ("display_name");
CREATE INDEX IF NOT EXISTS "idx_users_is_active" ON "public"."users" USING btree ("is_active") WHERE is_active = TRUE;

-- Enable RLS
ALTER TABLE "public"."users" ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "users_business_isolation" ON "public"."users"
FOR ALL USING (
    -- Users can see other users in their business
    EXISTS (
        SELECT 1 FROM business_memberships bm1
        JOIN business_memberships bm2 ON bm1.business_id = bm2.business_id
        WHERE bm1.user_id = auth.uid()
        AND bm2.user_id = users.id
        AND bm1.is_active = TRUE
        AND bm2.is_active = TRUE
    )
);

-- Function to sync auth.users data to public.users
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

-- Create trigger to sync auth.users changes
DROP TRIGGER IF EXISTS sync_user_data_trigger ON auth.users;
CREATE TRIGGER sync_user_data_trigger
    AFTER INSERT OR UPDATE OR DELETE ON auth.users
    FOR EACH ROW EXECUTE FUNCTION sync_user_data();

-- Sync existing auth.users data to public.users
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
ON CONFLICT (id) DO NOTHING;

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_update_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_users_updated_at();

-- Grant permissions
GRANT SELECT ON public.users TO authenticated;
GRANT SELECT ON public.users TO anon; 