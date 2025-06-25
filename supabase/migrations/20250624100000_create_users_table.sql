-- Create Users Table Migration
-- This migration creates a public.users table for development
-- Independent of auth.users for easier testing and development

-- Create the users table (independent of auth.users)
CREATE TABLE IF NOT EXISTS "public"."users" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "email" VARCHAR(320) NOT NULL UNIQUE,
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