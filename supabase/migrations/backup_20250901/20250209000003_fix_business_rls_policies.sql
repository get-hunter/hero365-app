-- Fix RLS policies for businesses table to allow public read access
-- This addresses the infinite recursion issue with business_memberships

-- Drop existing problematic policies for businesses
DROP POLICY IF EXISTS "Businesses are private to members" ON businesses;
DROP POLICY IF EXISTS "Business owners can manage their business" ON businesses;

-- Create new policies that allow public read access for active businesses
-- This is needed for the public professional API endpoints
CREATE POLICY "Public read access for active businesses" ON businesses 
FOR SELECT USING (is_active = true);

-- Allow authenticated users to manage their own businesses
CREATE POLICY "Business owners can manage their businesses" ON businesses 
FOR ALL USING (
    id IN (
        SELECT bm.business_id FROM business_memberships bm
        WHERE bm.user_id = auth.uid() AND bm.is_active = true
    )
);

-- Also ensure business_memberships table has proper policies
DROP POLICY IF EXISTS "Business memberships are private to members" ON business_memberships;

-- Allow users to see their own memberships
CREATE POLICY "Users can see their own memberships" ON business_memberships 
FOR SELECT USING (user_id = auth.uid());

-- Allow business owners to manage memberships
CREATE POLICY "Business owners can manage memberships" ON business_memberships 
FOR ALL USING (
    business_id IN (
        SELECT bm.business_id FROM business_memberships bm
        WHERE bm.user_id = auth.uid() AND bm.is_active = true AND bm.role IN ('owner', 'admin')
    )
);

COMMIT;
