-- Update businesses table to support trade-based model
-- Migration: 20250127000000_update_businesses_table_for_trades.sql
-- Description: Add trade fields and remove business_type column

-- Add trade-related columns
ALTER TABLE "public"."businesses" 
ADD COLUMN IF NOT EXISTS "trade_category" VARCHAR(20) CHECK (trade_category IN ('commercial', 'residential')),
ADD COLUMN IF NOT EXISTS "commercial_trades" TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS "residential_trades" TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS "service_areas" TEXT[] DEFAULT '{}';

-- Add business identity columns that may be missing
ALTER TABLE "public"."businesses" 
ADD COLUMN IF NOT EXISTS "business_registration_number" VARCHAR(100),
ADD COLUMN IF NOT EXISTS "tax_id" VARCHAR(50),
ADD COLUMN IF NOT EXISTS "business_license" VARCHAR(100),
ADD COLUMN IF NOT EXISTS "insurance_number" VARCHAR(100);

-- Add feature management columns
ALTER TABLE "public"."businesses" 
ADD COLUMN IF NOT EXISTS "selected_features" TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS "primary_goals" TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS "enabled_features" TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS "max_team_members" INTEGER CHECK (max_team_members > 0),
ADD COLUMN IF NOT EXISTS "subscription_tier" VARCHAR(50),
ADD COLUMN IF NOT EXISTS "currency" VARCHAR(3) DEFAULT 'USD',
ADD COLUMN IF NOT EXISTS "business_hours" JSONB,
ADD COLUMN IF NOT EXISTS "onboarding_completed_date" TIMESTAMP WITH TIME ZONE;

-- Rename columns to match domain model
ALTER TABLE "public"."businesses" 
RENAME COLUMN "phone" TO "phone_number";
ALTER TABLE "public"."businesses" 
RENAME COLUMN "email" TO "business_email";
ALTER TABLE "public"."businesses" 
RENAME COLUMN "address" TO "business_address";

-- Update column constraints
ALTER TABLE "public"."businesses" 
ALTER COLUMN "name" SET NOT NULL,
ALTER COLUMN "industry" SET NOT NULL;

-- Add constraint to ensure at least one trade is specified
ALTER TABLE "public"."businesses" 
ADD CONSTRAINT "businesses_at_least_one_trade" 
CHECK (
    array_length(commercial_trades, 1) > 0 OR 
    array_length(residential_trades, 1) > 0
);

-- Add constraint for trade category consistency
ALTER TABLE "public"."businesses" 
ADD CONSTRAINT "businesses_trade_category_consistency" 
CHECK (
    (trade_category = 'commercial' AND (array_length(commercial_trades, 1) > 0 OR array_length(residential_trades, 1) IS NULL OR array_length(residential_trades, 1) = 0)) OR
    (trade_category = 'residential' AND (array_length(residential_trades, 1) > 0 OR array_length(commercial_trades, 1) IS NULL OR array_length(commercial_trades, 1) = 0)) OR
    trade_category IS NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS "idx_businesses_commercial_trades" ON "public"."businesses" USING GIN ("commercial_trades");
CREATE INDEX IF NOT EXISTS "idx_businesses_residential_trades" ON "public"."businesses" USING GIN ("residential_trades");
CREATE INDEX IF NOT EXISTS "idx_businesses_service_areas" ON "public"."businesses" USING GIN ("service_areas");
CREATE INDEX IF NOT EXISTS "idx_businesses_trade_category" ON "public"."businesses" ("trade_category");
CREATE INDEX IF NOT EXISTS "idx_businesses_industry" ON "public"."businesses" ("industry");

-- Add comments for documentation
COMMENT ON COLUMN "public"."businesses"."trade_category" IS 'Primary trade category: commercial or residential';
COMMENT ON COLUMN "public"."businesses"."commercial_trades" IS 'Array of commercial trade types offered';
COMMENT ON COLUMN "public"."businesses"."residential_trades" IS 'Array of residential trade types offered';
COMMENT ON COLUMN "public"."businesses"."service_areas" IS 'Geographic areas served by the business';
