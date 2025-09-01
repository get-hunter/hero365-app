-- Fix RLS policies for public API access
-- This addresses the infinite recursion issue and allows public access to business services

-- Drop existing problematic policies for business_services
DROP POLICY IF EXISTS "Business services are private to business" ON business_services;

-- Create new policies that allow public read access for active services
-- This is needed for the public professional API endpoints
CREATE POLICY "Public read access for active business services" ON business_services 
FOR SELECT USING (is_active = true);

-- Allow authenticated users to manage their business services
CREATE POLICY "Business owners can manage their services" ON business_services 
FOR ALL USING (
    business_id IN (
        SELECT b.id FROM businesses b
        JOIN business_memberships bm ON b.id = bm.business_id
        WHERE bm.user_id = auth.uid() AND bm.is_active = true
    )
);

-- Ensure service_categories are publicly readable (they should be already)
DROP POLICY IF EXISTS "Service categories are publicly readable" ON service_categories;
CREATE POLICY "Service categories are publicly readable" ON service_categories FOR SELECT USING (true);

-- Ensure service_templates are publicly readable (they should be already)  
DROP POLICY IF EXISTS "Service templates are publicly readable" ON service_templates;
CREATE POLICY "Service templates are publicly readable" ON service_templates FOR SELECT USING (true);

-- Fix business_service_bundles policies
DROP POLICY IF EXISTS "Business service bundles are private to business" ON business_service_bundles;

-- Allow public read access for active bundles
CREATE POLICY "Public read access for active service bundles" ON business_service_bundles 
FOR SELECT USING (is_active = true);

-- Allow authenticated users to manage their bundles
CREATE POLICY "Business owners can manage their bundles" ON business_service_bundles 
FOR ALL USING (
    business_id IN (
        SELECT b.id FROM businesses b
        JOIN business_memberships bm ON b.id = bm.business_id
        WHERE bm.user_id = auth.uid() AND bm.is_active = true
    )
);

-- Fix service_template_adoptions policies
DROP POLICY IF EXISTS "Service template adoptions are private to business" ON service_template_adoptions;

-- Allow public read access (for analytics and template usage tracking)
CREATE POLICY "Public read access for template adoptions" ON service_template_adoptions 
FOR SELECT USING (true);

-- Allow authenticated users to manage their adoptions
CREATE POLICY "Business owners can manage their adoptions" ON service_template_adoptions 
FOR ALL USING (
    business_id IN (
        SELECT b.id FROM businesses b
        JOIN business_memberships bm ON b.id = bm.business_id
        WHERE bm.user_id = auth.uid() AND bm.is_active = true
    )
);

COMMIT;
