-- =============================================
-- CORE ECOMMERCE SYSTEM TABLES
-- =============================================
-- Essential shopping cart and product sales functionality
-- Depends on: businesses, contacts tables

-- =============================================
-- SHOPPING CARTS
-- =============================================

CREATE TABLE shopping_carts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id),
    
    -- Cart Details
    session_id VARCHAR(255), -- For anonymous users
    cart_status VARCHAR(20) DEFAULT 'active', -- 'active', 'abandoned', 'completed', 'expired'
    
    -- Totals (calculated fields)
    subtotal DECIMAL(12,2) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    shipping_amount DECIMAL(12,2) DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    
    -- Customer Info (for checkout)
    customer_email VARCHAR(255),
    customer_phone VARCHAR(20),
    
    -- Shipping Address
    shipping_address JSONB,
    
    -- Metadata
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days'),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- CART ITEMS
-- =============================================

CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES shopping_carts(id) ON DELETE CASCADE,
    
    -- Product Reference (flexible - could be business_services or products)
    product_type VARCHAR(50) NOT NULL, -- 'service', 'product', 'installation'
    product_id UUID NOT NULL, -- References business_services.id or products.id
    product_name VARCHAR(255) NOT NULL, -- Denormalized for performance
    
    -- Pricing
    unit_price DECIMAL(10,2) NOT NULL,
    quantity DECIMAL(10,3) DEFAULT 1,
    line_total DECIMAL(12,2) NOT NULL,
    
    -- Configuration
    product_options JSONB DEFAULT '{}', -- Size, color, installation options, etc.
    special_instructions TEXT,
    
    -- Metadata
    added_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- PRODUCTS (FOR ECOMMERCE)
-- =============================================

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Product Details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    short_description VARCHAR(500),
    sku VARCHAR(100),
    
    -- Categories
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    
    -- Pricing
    unit_price DECIMAL(10,2) NOT NULL,
    compare_at_price DECIMAL(10,2), -- Original price for discounts
    cost_price DECIMAL(10,2), -- For profit calculations
    
    -- Inventory
    track_inventory BOOLEAN DEFAULT true,
    current_stock DECIMAL(10,2) DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 10,
    
    -- Physical Properties
    weight_lbs DECIMAL(8,2),
    dimensions JSONB, -- {"length": 12, "width": 8, "height": 4}
    
    -- Shipping
    requires_shipping BOOLEAN DEFAULT true,
    shipping_class VARCHAR(50), -- 'standard', 'heavy', 'fragile'
    
    -- Installation
    requires_installation BOOLEAN DEFAULT false,
    installation_time_hours DECIMAL(4,2),
    installation_complexity VARCHAR(20) DEFAULT 'medium', -- 'easy', 'medium', 'complex'
    
    -- Media
    featured_image_url TEXT,
    gallery_images TEXT[], -- Array of image URLs
    
    -- SEO
    slug VARCHAR(255) UNIQUE,
    meta_title VARCHAR(200),
    meta_description VARCHAR(300),
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- PRODUCT CATEGORIES
-- =============================================

CREATE TABLE product_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Category Details
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Hierarchy
    parent_category_id UUID REFERENCES product_categories(id),
    
    -- Display
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    
    -- SEO
    meta_title VARCHAR(200),
    meta_description VARCHAR(300),
    
    -- Media
    image_url TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(business_id, slug)
);

-- =============================================
-- CUSTOMER CONTACTS (ALIAS FOR CONTACTS)
-- =============================================
-- Note: The backend references "customer_contacts" but we use "contacts"
-- This creates a view for compatibility

CREATE VIEW customer_contacts AS
SELECT 
    id,
    business_id,
    first_name,
    last_name,
    full_name,
    email,
    phone,
    address,
    city,
    state,
    postal_code,
    contact_type,
    contact_source,
    is_active,
    notes,
    tags,
    custom_fields,
    created_at,
    updated_at
FROM contacts;

-- =============================================
-- ESTIMATE LINE ITEMS (ALIAS FOR ESTIMATE_ITEMS)
-- =============================================
-- Note: The backend references "estimate_line_items" but we use "estimate_items"
-- This creates a view for compatibility

CREATE VIEW estimate_line_items AS
SELECT 
    id,
    estimate_id,
    item_type,
    name,
    description,
    quantity,
    unit_price,
    total_price,
    display_order,
    category,
    created_at,
    updated_at
FROM estimate_items;

-- =============================================
-- INDEXES
-- =============================================

CREATE INDEX idx_shopping_carts_business ON shopping_carts(business_id);
CREATE INDEX idx_shopping_carts_contact ON shopping_carts(contact_id);
CREATE INDEX idx_shopping_carts_session ON shopping_carts(session_id);
CREATE INDEX idx_shopping_carts_status ON shopping_carts(cart_status);

CREATE INDEX idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product ON cart_items(product_type, product_id);

CREATE INDEX idx_products_business ON products(business_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_products_featured ON products(is_featured);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_slug ON products(slug);

CREATE INDEX idx_product_categories_business ON product_categories(business_id);
CREATE INDEX idx_product_categories_parent ON product_categories(parent_category_id);
CREATE INDEX idx_product_categories_slug ON product_categories(slug);
CREATE INDEX idx_product_categories_active ON product_categories(is_active);

COMMIT;
