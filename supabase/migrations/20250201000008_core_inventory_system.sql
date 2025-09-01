-- =============================================
-- CORE INVENTORY MANAGEMENT SYSTEM
-- =============================================
-- Essential inventory, supplier, and stock management
-- Depends on: businesses, products tables

-- =============================================
-- SUPPLIERS TABLE
-- =============================================

CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id), -- Link to supplier user account if they have one
    
    -- Basic supplier information
    supplier_code VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    legal_name VARCHAR(200),
    tax_id VARCHAR(50),
    website VARCHAR(255),
    
    -- Contact information
    email VARCHAR(255),
    phone VARCHAR(50),
    mobile VARCHAR(50),
    fax VARCHAR(50),
    
    -- Address information
    billing_address JSONB,
    shipping_address JSONB,
    
    -- Financial information
    currency VARCHAR(3) DEFAULT 'USD',
    payment_terms_days INTEGER DEFAULT 30,
    early_payment_discount_percentage DECIMAL(5,2) DEFAULT 0,
    early_payment_discount_days INTEGER DEFAULT 0,
    credit_limit DECIMAL(15,2) DEFAULT 0,
    
    -- Status and categorization
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive', 'pending', 'suspended')) DEFAULT 'active',
    supplier_type VARCHAR(50),
    category VARCHAR(100),
    
    -- Performance tracking
    total_orders INTEGER NOT NULL DEFAULT 0,
    total_spend DECIMAL(15,2) NOT NULL DEFAULT 0,
    average_lead_time_days INTEGER DEFAULT 0,
    on_time_delivery_rate DECIMAL(5,2) DEFAULT 0,
    quality_score DECIMAL(3,1) DEFAULT 0,
    return_rate DECIMAL(5,2) DEFAULT 0,
    performance_score DECIMAL(3,1) DEFAULT 0,
    performance_grade VARCHAR(1) DEFAULT 'C',
    last_performance_update TIMESTAMPTZ,
    
    -- Relationship management
    primary_contact_name VARCHAR(100),
    primary_contact_email VARCHAR(255),
    primary_contact_phone VARCHAR(50),
    account_manager VARCHAR(100),
    
    -- Additional metadata
    notes TEXT,
    tags TEXT[],
    is_preferred BOOLEAN NOT NULL DEFAULT false,
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    
    CONSTRAINT suppliers_business_code_unique UNIQUE(business_id, supplier_code),
    CONSTRAINT suppliers_performance_score_check CHECK (performance_score >= 0 AND performance_score <= 5),
    CONSTRAINT suppliers_quality_score_check CHECK (quality_score >= 0 AND quality_score <= 5),
    CONSTRAINT suppliers_grade_check CHECK (performance_grade IN ('A', 'B', 'C', 'D', 'F'))
);

-- =============================================
-- PURCHASE ORDERS
-- =============================================

CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    supplier_id UUID NOT NULL REFERENCES suppliers(id),
    
    -- Order Details
    po_number VARCHAR(50) NOT NULL,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    
    -- Status
    status VARCHAR(20) NOT NULL CHECK (status IN ('draft', 'sent', 'confirmed', 'partial', 'received', 'cancelled')) DEFAULT 'draft',
    
    -- Totals
    subtotal DECIMAL(15,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    shipping_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    
    -- Delivery Information
    delivery_address JSONB,
    delivery_instructions TEXT,
    
    -- Payment
    payment_terms_days INTEGER DEFAULT 30,
    payment_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'paid', 'overdue'
    
    -- Notes
    notes TEXT,
    internal_notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT purchase_orders_business_po_unique UNIQUE(business_id, po_number)
);

-- =============================================
-- PURCHASE ORDER ITEMS
-- =============================================

CREATE TABLE purchase_order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_order_id UUID NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    
    -- Item Details (denormalized for historical accuracy)
    product_sku VARCHAR(100),
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Quantities
    quantity_ordered DECIMAL(10,3) NOT NULL,
    quantity_received DECIMAL(10,3) DEFAULT 0,
    quantity_remaining DECIMAL(10,3) GENERATED ALWAYS AS (quantity_ordered - quantity_received) STORED,
    
    -- Pricing
    unit_cost DECIMAL(10,4) NOT NULL,
    line_total DECIMAL(15,2) GENERATED ALWAYS AS (quantity_ordered * unit_cost) STORED,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'partial', 'received', 'cancelled'
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- STOCK MOVEMENTS
-- =============================================

CREATE TABLE stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    
    -- Movement Details
    movement_type VARCHAR(20) NOT NULL CHECK (movement_type IN ('in', 'out', 'adjustment', 'transfer')),
    movement_reason VARCHAR(50), -- 'purchase', 'sale', 'return', 'damaged', 'theft', 'count_adjustment'
    
    -- Quantities
    quantity_before DECIMAL(10,3) NOT NULL,
    quantity_change DECIMAL(10,3) NOT NULL, -- Positive for in, negative for out
    quantity_after DECIMAL(10,3) NOT NULL,
    
    -- Cost Information
    unit_cost DECIMAL(10,4),
    total_cost DECIMAL(15,2),
    
    -- References
    reference_type VARCHAR(50), -- 'purchase_order', 'invoice', 'estimate', 'manual'
    reference_id UUID,
    reference_number VARCHAR(100),
    
    -- Location (if multi-location inventory)
    location_id UUID,
    location_name VARCHAR(100),
    
    -- Notes and Metadata
    notes TEXT,
    performed_by UUID REFERENCES users(id),
    movement_date TIMESTAMPTZ DEFAULT NOW(),
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- INVENTORY LOCATIONS
-- =============================================

CREATE TABLE inventory_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Location Details
    name VARCHAR(100) NOT NULL,
    location_type VARCHAR(50) DEFAULT 'warehouse', -- 'warehouse', 'truck', 'office', 'jobsite'
    description TEXT,
    
    -- Address
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    
    -- Configuration
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT inventory_locations_business_name_unique UNIQUE(business_id, name)
);

-- =============================================
-- PRODUCT INVENTORY (Stock Levels by Location)
-- =============================================

CREATE TABLE product_inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    location_id UUID REFERENCES inventory_locations(id),
    
    -- Stock Levels
    quantity_on_hand DECIMAL(10,3) DEFAULT 0,
    quantity_reserved DECIMAL(10,3) DEFAULT 0, -- Reserved for pending orders
    quantity_available DECIMAL(10,3) GENERATED ALWAYS AS (quantity_on_hand - quantity_reserved) STORED,
    
    -- Reorder Information
    reorder_point DECIMAL(10,3) DEFAULT 0,
    reorder_quantity DECIMAL(10,3) DEFAULT 0,
    max_stock_level DECIMAL(10,3),
    
    -- Cost Information
    average_cost DECIMAL(10,4) DEFAULT 0,
    last_cost DECIMAL(10,4) DEFAULT 0,
    
    -- Status
    is_tracked BOOLEAN DEFAULT true,
    
    -- Metadata
    last_counted_at TIMESTAMPTZ,
    last_movement_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT product_inventory_unique UNIQUE(product_id, location_id)
);

-- =============================================
-- INDEXES
-- =============================================

CREATE INDEX idx_suppliers_business ON suppliers(business_id);
CREATE INDEX idx_suppliers_user ON suppliers(user_id);
CREATE INDEX idx_suppliers_status ON suppliers(business_id, status);
CREATE INDEX idx_suppliers_code ON suppliers(business_id, supplier_code);
CREATE INDEX idx_suppliers_preferred ON suppliers(business_id, is_preferred);
CREATE INDEX idx_suppliers_performance ON suppliers(business_id, performance_grade, performance_score);

CREATE INDEX idx_purchase_orders_business ON purchase_orders(business_id);
CREATE INDEX idx_purchase_orders_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX idx_purchase_orders_po_number ON purchase_orders(po_number);
CREATE INDEX idx_purchase_orders_date ON purchase_orders(order_date);

CREATE INDEX idx_purchase_order_items_po ON purchase_order_items(purchase_order_id);
CREATE INDEX idx_purchase_order_items_product ON purchase_order_items(product_id);

CREATE INDEX idx_stock_movements_business ON stock_movements(business_id);
CREATE INDEX idx_stock_movements_product ON stock_movements(product_id);
CREATE INDEX idx_stock_movements_type ON stock_movements(movement_type);
CREATE INDEX idx_stock_movements_date ON stock_movements(movement_date);
CREATE INDEX idx_stock_movements_reference ON stock_movements(reference_type, reference_id);

CREATE INDEX idx_inventory_locations_business ON inventory_locations(business_id);
CREATE INDEX idx_inventory_locations_active ON inventory_locations(is_active);

CREATE INDEX idx_product_inventory_business ON product_inventory(business_id);
CREATE INDEX idx_product_inventory_product ON product_inventory(product_id);
CREATE INDEX idx_product_inventory_location ON product_inventory(location_id);
CREATE INDEX idx_product_inventory_reorder ON product_inventory(business_id) WHERE quantity_available <= reorder_point;

COMMIT;
