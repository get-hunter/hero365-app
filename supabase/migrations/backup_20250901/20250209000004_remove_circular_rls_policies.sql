-- Remove circular RLS policies that cause infinite recursion
-- These policies reference each other creating a circular dependency

-- Drop the problematic business isolation policies
DROP POLICY IF EXISTS "business_memberships_business_isolation" ON business_memberships;
DROP POLICY IF EXISTS "businesses_business_isolation" ON businesses;

-- Drop the policies that reference business_memberships from businesses table
DROP POLICY IF EXISTS "Business owners can manage their businesses" ON businesses;

-- Keep only the simple public read access policy for businesses
-- This allows public API endpoints to work without authentication

-- For business_memberships, keep only the simple user-based policies
-- Drop the complex policy that references business_memberships recursively
DROP POLICY IF EXISTS "Business owners can manage memberships" ON business_memberships;

-- Create a simpler policy for business membership management
CREATE POLICY "Simple business membership management" ON business_memberships 
FOR ALL USING (user_id = auth.uid());

COMMIT;
