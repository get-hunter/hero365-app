-- Remove owner_id redundancy from businesses table
-- Use only business_memberships for all user-business relationships

-- Step 1: Ensure data consistency - verify all businesses have owner memberships
DO $$
BEGIN
    -- Check for businesses without owner memberships
    IF EXISTS (
        SELECT 1 FROM businesses b 
        LEFT JOIN business_memberships bm ON b.id = bm.business_id AND bm.role = 'owner' AND bm.is_active = true
        WHERE bm.id IS NULL
    ) THEN
        RAISE EXCEPTION 'Data integrity issue: Some businesses do not have owner memberships. Please fix before removing owner_id.';
    END IF;
    
    -- Check for mismatched owner_id vs owner membership
    IF EXISTS (
        SELECT 1 FROM businesses b 
        JOIN business_memberships bm ON b.id = bm.business_id 
        WHERE bm.role = 'owner' AND bm.is_active = true AND b.owner_id != bm.user_id
    ) THEN
        RAISE EXCEPTION 'Data integrity issue: owner_id does not match owner membership. Please fix before removing owner_id.';
    END IF;
END $$;

-- Step 2: Create a convenient view for business owners (for easy querying)
CREATE OR REPLACE VIEW business_owners AS
SELECT 
    b.id AS business_id,
    b.name AS business_name,
    bm.user_id AS owner_id,
    u.full_name AS owner_name,
    u.email AS owner_email,
    bm.joined_date AS ownership_date
FROM businesses b
JOIN business_memberships bm ON b.id = bm.business_id
JOIN users u ON bm.user_id = u.id
WHERE bm.role = 'owner' AND bm.is_active = true;

-- Step 3: Create function to get business owner (for application code)
CREATE OR REPLACE FUNCTION get_business_owner(business_uuid UUID)
RETURNS TABLE(user_id UUID, full_name VARCHAR, email VARCHAR) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, u.full_name, u.email
    FROM business_memberships bm
    JOIN users u ON bm.user_id = u.id
    WHERE bm.business_id = business_uuid 
    AND bm.role = 'owner' 
    AND bm.is_active = true
    LIMIT 1;
END;
$$;

-- Step 4: Remove the owner_id column (this will automatically drop the foreign key constraint)
ALTER TABLE businesses DROP COLUMN IF EXISTS owner_id;

-- Step 5: Add comment explaining the new approach
COMMENT ON TABLE businesses IS 'Business information. Use business_memberships with role=owner to identify business owners.';
COMMENT ON VIEW business_owners IS 'Convenient view to get business owners from business_memberships.';
COMMENT ON FUNCTION get_business_owner IS 'Function to get the active owner of a business.';
