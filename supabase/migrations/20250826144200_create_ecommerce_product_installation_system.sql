-- =============================================
-- E-COMMERCE PRODUCT + INSTALLATION SYSTEM
-- =============================================
-- This schema enables selling products with professional installation services,
-- integrating with membership pricing and booking systems.

-- =============================================
-- 1. EXTEND PRODUCTS TABLE FOR E-COMMERCE
-- =============================================

-- E-commerce display flags
ALTER TABLE products ADD COLUMN IF NOT EXISTS show_on_website BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS requires_professional_install BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS install_complexity VARCHAR(20) DEFAULT 'standard';

-- Add check constraint for install_complexity if it doesn't exist
DO $$
BEGIN
    ALTER TABLE products ADD CONSTRAINT products_install_complexity_check 
    CHECK (install_complexity IN ('standard', 'complex', 'expert'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- SEO and marketing
ALTER TABLE products ADD COLUMN IF NOT EXISTS meta_title VARCHAR(255);
ALTER TABLE products ADD COLUMN IF NOT EXISTS meta_description TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS slug VARCHAR(255);

-- Product variations (size, color, model)
ALTER TABLE products ADD COLUMN IF NOT EXISTS has_variations BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS variation_options JSONB DEFAULT '{}';

-- Shipping and logistics
ALTER TABLE products ADD COLUMN IF NOT EXISTS shipping_weight DECIMAL(10,3);
ALTER TABLE products ADD COLUMN IF NOT EXISTS shipping_dimensions JSONB DEFAULT '{}';
ALTER TABLE products ADD COLUMN IF NOT EXISTS requires_freight BOOLEAN DEFAULT FALSE;

-- Installation details
ALTER TABLE products ADD COLUMN IF NOT EXISTS installation_time_estimate VARCHAR(50);
ALTER TABLE products ADD COLUMN IF NOT EXISTS warranty_years INTEGER DEFAULT 1;
ALTER TABLE products ADD COLUMN IF NOT EXISTS energy_efficiency_rating VARCHAR(10);

-- E-commerce specific
ALTER TABLE products ADD COLUMN IF NOT EXISTS featured_image_url VARCHAR(500);
ALTER TABLE products ADD COLUMN IF NOT EXISTS gallery_images JSONB DEFAULT '[]';
ALTER TABLE products ADD COLUMN IF NOT EXISTS product_highlights JSONB DEFAULT '[]';
ALTER TABLE products ADD COLUMN IF NOT EXISTS technical_specs JSONB DEFAULT '{}';
ALTER TABLE products ADD COLUMN IF NOT EXISTS installation_requirements JSONB DEFAULT '{}';

-- Add e-commerce indexes
CREATE INDEX IF NOT EXISTS idx_products_website_display ON products(business_id, show_on_website, status) WHERE show_on_website = TRUE AND status = 'active';
CREATE INDEX IF NOT EXISTS idx_products_slug ON products(business_id, slug) WHERE slug IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_install_required ON products(business_id, requires_professional_install) WHERE requires_professional_install = TRUE;

-- =============================================
-- 2. PRODUCT INSTALLATION OPTIONS
-- =============================================
-- Links products to their available installation services with pricing
CREATE TABLE product_installation_options (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES business_services(id) ON DELETE CASCADE,
    
    -- Installation-specific details
    option_name VARCHAR(200) NOT NULL, -- "Standard Installation", "Complex Installation"
    description TEXT,
    
    -- Base installation pricing
    base_install_price DECIMAL(10,2) NOT NULL DEFAULT 0,
    complexity_multiplier DECIMAL(3,2) DEFAULT 1.0, -- For difficult installs (1.0 = standard, 1.5 = complex, 2.0 = expert)
    
    -- Membership pricing overrides (optional - can use percentage discounts instead)
    residential_install_price DECIMAL(10,2),
    commercial_install_price DECIMAL(10,2),
    premium_install_price DECIMAL(10,2),
    
    -- Installation requirements and details
    requirements JSONB DEFAULT '{}', -- Installation requirements (electrical, access, permits, etc.)
    included_in_install JSONB DEFAULT '[]', -- What's included in installation
    additional_fees JSONB DEFAULT '{}', -- Potential additional fees (height, complexity, permits)
    
    -- Time and logistics
    estimated_duration_hours DECIMAL(4,2),
    requires_permit BOOLEAN DEFAULT FALSE,
    requires_electrical_work BOOLEAN DEFAULT FALSE,
    requires_gas_work BOOLEAN DEFAULT FALSE,
    requires_plumbing_work BOOLEAN DEFAULT FALSE,
    
    -- Availability and constraints
    min_quantity INTEGER DEFAULT 1, -- Minimum quantity to qualify for this install option
    max_quantity INTEGER, -- Maximum quantity for this install type
    available_in_areas TEXT[], -- Service areas where this install is available
    
    -- Display and ordering
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE, -- Default installation option for this product
    sort_order INTEGER DEFAULT 0,
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT product_installation_options_unique UNIQUE(business_id, product_id, service_id),
    CONSTRAINT product_installation_options_pricing_check CHECK (base_install_price >= 0),
    CONSTRAINT product_installation_options_multiplier_check CHECK (complexity_multiplier > 0)
);

-- Indexes for product installation options
CREATE INDEX idx_product_installation_options_product ON product_installation_options(product_id, is_active);
CREATE INDEX idx_product_installation_options_service ON product_installation_options(service_id, is_active);
CREATE INDEX idx_product_installation_options_business ON product_installation_options(business_id, is_active);

-- =============================================
-- 3. SHOPPING CARTS SYSTEM
-- =============================================
-- Shopping cart for anonymous and registered users
CREATE TABLE shopping_carts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- User identification (one of these will be set)
    session_id VARCHAR(255), -- For anonymous users
    customer_email VARCHAR(255), -- For known customers
    customer_phone VARCHAR(20), -- Alternative identifier
    
    -- Cart metadata
    cart_status VARCHAR(20) DEFAULT 'active' CHECK (cart_status IN ('active', 'abandoned', 'converted', 'expired')),
    currency_code VARCHAR(3) DEFAULT 'USD',
    
    -- Totals (calculated fields)
    subtotal DECIMAL(12,2) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    total_savings DECIMAL(12,2) DEFAULT 0, -- Membership savings
    
    -- Customer preferences
    preferred_install_date DATE,
    service_address JSONB, -- Installation address if different from billing
    special_instructions TEXT,
    
    -- Membership context
    membership_type VARCHAR(20), -- residential, commercial, premium
    membership_verified BOOLEAN DEFAULT FALSE,
    
    -- Lifecycle management
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),
    converted_to_estimate_id UUID, -- Reference to created estimate
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT shopping_carts_user_identification CHECK (
        (session_id IS NOT NULL AND customer_email IS NULL) OR 
        (session_id IS NULL AND customer_email IS NOT NULL) OR
        (customer_phone IS NOT NULL)
    )
);

-- Indexes for shopping carts
CREATE INDEX idx_shopping_carts_session ON shopping_carts(session_id, cart_status);
CREATE INDEX idx_shopping_carts_customer ON shopping_carts(customer_email, cart_status);
CREATE INDEX idx_shopping_carts_business ON shopping_carts(business_id, cart_status);
CREATE INDEX idx_shopping_carts_expires ON shopping_carts(expires_at) WHERE cart_status = 'active';

-- =============================================
-- 4. CART ITEMS
-- =============================================
-- Individual items in shopping carts with product + installation combinations
CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cart_id UUID NOT NULL REFERENCES shopping_carts(id) ON DELETE CASCADE,
    
    -- Product information (snapshot for price stability)
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    product_name VARCHAR(200) NOT NULL, -- Snapshot
    product_sku VARCHAR(100) NOT NULL, -- Snapshot
    
    -- Installation option (optional)
    installation_option_id UUID REFERENCES product_installation_options(id) ON DELETE SET NULL,
    installation_name VARCHAR(200), -- Snapshot
    
    -- Quantities
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    
    -- Pricing (all stored as snapshots for price stability)
    unit_price DECIMAL(10,2) NOT NULL, -- Product unit price
    install_price DECIMAL(10,2) DEFAULT 0, -- Installation price per unit
    subtotal_price DECIMAL(12,2) NOT NULL, -- (unit_price + install_price) * quantity
    
    -- Membership discount calculations
    membership_type VARCHAR(20), -- Applied membership type
    product_discount DECIMAL(10,2) DEFAULT 0, -- Discount on product
    install_discount DECIMAL(10,2) DEFAULT 0, -- Discount on installation
    total_discount DECIMAL(12,2) DEFAULT 0, -- Total savings
    
    -- Final pricing
    final_price DECIMAL(12,2) NOT NULL, -- After discounts
    
    -- Installation preferences for this item
    installation_required BOOLEAN DEFAULT TRUE,
    install_notes TEXT,
    
    -- Item configuration (for products with variations)
    configuration JSONB DEFAULT '{}', -- Size, color, model selections
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT cart_items_pricing_check CHECK (subtotal_price >= 0 AND final_price >= 0)
);

-- Indexes for cart items
CREATE INDEX idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product ON cart_items(product_id);
CREATE INDEX idx_cart_items_install_option ON cart_items(installation_option_id);

-- =============================================
-- 5. PRODUCT VARIANTS (FOR PRODUCTS WITH OPTIONS)
-- =============================================
-- Support for products with size, color, model variations
CREATE TABLE product_variants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    
    -- Variant identification
    variant_name VARCHAR(200) NOT NULL, -- "24,000 BTU", "White", "Model XL"
    sku_suffix VARCHAR(50) NOT NULL, -- Added to base SKU
    
    -- Variant-specific pricing
    price_adjustment DECIMAL(10,2) DEFAULT 0, -- Price difference from base product
    cost_adjustment DECIMAL(10,2) DEFAULT 0, -- Cost difference from base product
    
    -- Variant-specific inventory
    stock_quantity DECIMAL(15,3) DEFAULT 0,
    reserved_stock DECIMAL(15,3) DEFAULT 0,
    available_stock DECIMAL(15,3) DEFAULT 0,
    
    -- Variant attributes
    variant_attributes JSONB NOT NULL DEFAULT '{}', -- {"size": "24000", "color": "white", "model": "xl"}
    
    -- Display and availability
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    
    -- Images and media specific to this variant
    variant_images JSONB DEFAULT '[]',
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT product_variants_unique UNIQUE(product_id, sku_suffix),
    CONSTRAINT product_variants_stock_calc CHECK (available_stock = stock_quantity - reserved_stock)
);

-- Indexes for product variants
CREATE INDEX idx_product_variants_product ON product_variants(product_id, is_active);
CREATE INDEX idx_product_variants_attributes ON product_variants USING GIN(variant_attributes);

-- =============================================
-- 6. ROW LEVEL SECURITY (RLS)
-- =============================================

-- Enable RLS on new tables
ALTER TABLE product_installation_options ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopping_carts ENABLE ROW LEVEL SECURITY;
ALTER TABLE cart_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_variants ENABLE ROW LEVEL SECURITY;

-- Public read access to installation options (for website display)
CREATE POLICY "Public can view installation options" ON product_installation_options
    FOR SELECT USING (is_active = true);

-- Public access to shopping carts (session-based)
CREATE POLICY "Users can manage their own carts" ON shopping_carts
    FOR ALL USING (
        session_id = current_setting('app.session_id', true) OR
        customer_email = current_setting('app.customer_email', true)
    );

-- Public access to cart items (through cart ownership)
CREATE POLICY "Users can manage their cart items" ON cart_items
    FOR ALL USING (
        cart_id IN (
            SELECT id FROM shopping_carts 
            WHERE session_id = current_setting('app.session_id', true) OR
                  customer_email = current_setting('app.customer_email', true)
        )
    );

-- Public read access to product variants (for website display)
CREATE POLICY "Public can view active product variants" ON product_variants
    FOR SELECT USING (is_active = true);

-- Business owners can manage their installation options
CREATE POLICY "Business owners can manage installation options" ON product_installation_options
    FOR ALL USING (
        business_id IN (
            SELECT b.id FROM businesses b 
            JOIN business_memberships bm ON b.id = bm.business_id 
            WHERE bm.user_id = auth.uid() AND bm.role IN ('owner', 'admin')
        )
    );

-- Business owners can manage product variants
CREATE POLICY "Business owners can manage product variants" ON product_variants
    FOR ALL USING (
        product_id IN (
            SELECT p.id FROM products p
            JOIN businesses b ON p.business_id = b.id
            JOIN business_memberships bm ON b.id = bm.business_id 
            WHERE bm.user_id = auth.uid() AND bm.role IN ('owner', 'admin')
        )
    );

-- =============================================
-- 7. TRIGGERS FOR CALCULATED FIELDS
-- =============================================

-- Update cart totals when items change
CREATE OR REPLACE FUNCTION update_cart_totals()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE shopping_carts SET 
        subtotal = COALESCE((
            SELECT SUM(subtotal_price) 
            FROM cart_items 
            WHERE cart_id = COALESCE(NEW.cart_id, OLD.cart_id)
        ), 0),
        total_amount = COALESCE((
            SELECT SUM(final_price) 
            FROM cart_items 
            WHERE cart_id = COALESCE(NEW.cart_id, OLD.cart_id)
        ), 0),
        total_savings = COALESCE((
            SELECT SUM(total_discount) 
            FROM cart_items 
            WHERE cart_id = COALESCE(NEW.cart_id, OLD.cart_id)
        ), 0),
        updated_at = NOW()
    WHERE id = COALESCE(NEW.cart_id, OLD.cart_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger to update cart totals
CREATE TRIGGER trigger_update_cart_totals
    AFTER INSERT OR UPDATE OR DELETE ON cart_items
    FOR EACH ROW
    EXECUTE FUNCTION update_cart_totals();

-- Update product variant available stock
CREATE OR REPLACE FUNCTION update_variant_available_stock()
RETURNS TRIGGER AS $$
BEGIN
    NEW.available_stock = NEW.stock_quantity - NEW.reserved_stock;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to calculate variant available stock
CREATE TRIGGER trigger_update_variant_available_stock
    BEFORE INSERT OR UPDATE ON product_variants
    FOR EACH ROW
    EXECUTE FUNCTION update_variant_available_stock();

-- =============================================
-- 8. HELPFUL VIEWS FOR QUERIES
-- =============================================

-- View for products with installation options
CREATE OR REPLACE VIEW products_with_installation AS
SELECT 
    p.*,
    CASE WHEN p.requires_professional_install THEN
        JSON_AGG(
            JSON_BUILD_OBJECT(
                'id', pio.id,
                'option_name', pio.option_name,
                'description', pio.description,
                'base_install_price', pio.base_install_price,
                'residential_price', pio.residential_install_price,
                'commercial_price', pio.commercial_install_price,
                'premium_price', pio.premium_install_price,
                'estimated_duration_hours', pio.estimated_duration_hours,
                'is_default', pio.is_default
            ) ORDER BY pio.sort_order, pio.option_name
        )
    ELSE '[]'::json
    END as installation_options
FROM products p
LEFT JOIN product_installation_options pio ON p.id = pio.product_id AND pio.is_active = true
WHERE p.show_on_website = true AND p.status = 'active'
GROUP BY p.id;

-- View for cart summary with totals
CREATE OR REPLACE VIEW cart_summary AS
SELECT 
    c.*,
    COUNT(ci.id) as item_count,
    SUM(ci.quantity) as total_quantity,
    ARRAY_AGG(
        JSON_BUILD_OBJECT(
            'product_name', ci.product_name,
            'quantity', ci.quantity,
            'final_price', ci.final_price
        ) ORDER BY ci.created_at
    ) as items
FROM shopping_carts c
LEFT JOIN cart_items ci ON c.id = ci.cart_id
GROUP BY c.id;

-- =============================================
-- 9. SAMPLE DATA FUNCTIONS
-- =============================================

-- Function to add installation options for a product
CREATE OR REPLACE FUNCTION add_product_installation_option(
    p_business_id UUID,
    p_product_id UUID,
    p_service_id UUID,
    p_option_name VARCHAR(200),
    p_base_price DECIMAL(10,2),
    p_duration_hours DECIMAL(4,2) DEFAULT 2.0,
    p_is_default BOOLEAN DEFAULT FALSE
)
RETURNS UUID AS $$
DECLARE
    new_option_id UUID;
BEGIN
    INSERT INTO product_installation_options (
        business_id, product_id, service_id, option_name, 
        base_install_price, estimated_duration_hours, is_default
    ) VALUES (
        p_business_id, p_product_id, p_service_id, p_option_name,
        p_base_price, p_duration_hours, p_is_default
    ) RETURNING id INTO new_option_id;
    
    RETURN new_option_id;
END;
$$ LANGUAGE plpgsql;

-- Function to create a shopping cart
CREATE OR REPLACE FUNCTION create_shopping_cart(
    p_business_id UUID,
    p_session_id VARCHAR(255) DEFAULT NULL,
    p_customer_email VARCHAR(255) DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    new_cart_id UUID;
BEGIN
    INSERT INTO shopping_carts (business_id, session_id, customer_email)
    VALUES (p_business_id, p_session_id, p_customer_email)
    RETURNING id INTO new_cart_id;
    
    RETURN new_cart_id;
END;
$$ LANGUAGE plpgsql;
