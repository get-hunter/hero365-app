-- Create product-service association table for linking products to services
-- This enables service-driven product recommendations and merchandising

CREATE TABLE IF NOT EXISTS product_service_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES business_services(id) ON DELETE CASCADE,
    
    -- Association type defines the relationship
    association_type TEXT NOT NULL CHECK (association_type IN (
        'required',     -- Required for this service
        'recommended',  -- Recommended for this service
        'optional',     -- Optional add-on
        'upsell',       -- Upsell opportunity
        'accessory',    -- Accessory/complementary product
        'replacement'   -- Replacement part/component
    )),
    
    -- Display and sorting
    display_order INTEGER NOT NULL DEFAULT 0,
    is_featured BOOLEAN NOT NULL DEFAULT false,
    
    -- Pricing context
    service_discount_percentage INTEGER DEFAULT 0 CHECK (service_discount_percentage >= 0 AND service_discount_percentage <= 100),
    bundle_price DECIMAL(10,2), -- Optional bundle price when sold with service
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    -- Constraints
    UNIQUE(business_id, product_id, service_id, association_type)
);

-- Indexes for performance
CREATE INDEX idx_product_service_associations_business_id ON product_service_associations(business_id);
CREATE INDEX idx_product_service_associations_product_id ON product_service_associations(product_id);
CREATE INDEX idx_product_service_associations_service_id ON product_service_associations(service_id);
CREATE INDEX idx_product_service_associations_type ON product_service_associations(association_type);
CREATE INDEX idx_product_service_associations_featured ON product_service_associations(is_featured) WHERE is_featured = true;

-- Add updated_at trigger
CREATE TRIGGER update_product_service_associations_updated_at
    BEFORE UPDATE ON product_service_associations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add RLS policies
ALTER TABLE product_service_associations ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access associations for their businesses
CREATE POLICY product_service_associations_business_access ON product_service_associations
    FOR ALL USING (
        business_id IN (
            SELECT b.id FROM businesses b
            JOIN business_memberships bm ON b.id = bm.business_id
            WHERE bm.user_id = auth.uid()
            AND bm.status = 'active'
        )
    );

-- Add helpful comments
COMMENT ON TABLE product_service_associations IS 'Links products to services for context-driven merchandising and recommendations';
COMMENT ON COLUMN product_service_associations.association_type IS 'Defines the relationship: required, recommended, optional, upsell, accessory, replacement';
COMMENT ON COLUMN product_service_associations.service_discount_percentage IS 'Discount percentage when product is purchased with the service';
COMMENT ON COLUMN product_service_associations.bundle_price IS 'Special bundle price when sold together with service';
