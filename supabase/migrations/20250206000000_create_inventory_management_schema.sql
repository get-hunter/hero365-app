-- =============================================
-- Hero365 Inventory Management System Schema
-- Migration: 20250206000000_create_inventory_management_schema.sql
-- =============================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- PRODUCT CATEGORIES TABLE
-- Hierarchical category structure with defaults
-- =============================================
CREATE TABLE IF NOT EXISTS product_categories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES product_categories(id) ON DELETE CASCADE,
    
    -- Hierarchy management
    level INTEGER NOT NULL DEFAULT 0,
    path TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    
    -- Category status and counts
    is_active BOOLEAN NOT NULL DEFAULT true,
    product_count INTEGER NOT NULL DEFAULT 0,
    active_product_count INTEGER NOT NULL DEFAULT 0,
    subcategory_count INTEGER NOT NULL DEFAULT 0,
    
    -- Category defaults for products
    default_tax_rate DECIMAL(5,4) DEFAULT 0,
    default_markup_percentage DECIMAL(5,2) DEFAULT 0,
    default_cost_of_goods_sold_account VARCHAR(50),
    default_inventory_account VARCHAR(50),
    default_income_account VARCHAR(50),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    
    CONSTRAINT product_categories_business_name_parent_unique UNIQUE(business_id, name, parent_id),
    CONSTRAINT product_categories_level_check CHECK (level >= 0 AND level <= 10),
    CONSTRAINT product_categories_sort_order_check CHECK (sort_order >= 0)
);

-- Indexes for product categories
CREATE INDEX idx_product_categories_business_id ON product_categories(business_id);
CREATE INDEX idx_product_categories_parent_id ON product_categories(parent_id);
CREATE INDEX idx_product_categories_level ON product_categories(level);
CREATE INDEX idx_product_categories_active ON product_categories(business_id, is_active);
CREATE INDEX idx_product_categories_path ON product_categories USING GIN(to_tsvector('english', path));

-- =============================================
-- SUPPLIERS TABLE
-- Supplier management with performance tracking
-- =============================================
CREATE TABLE IF NOT EXISTS suppliers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
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
    
    -- Address information (stored as JSONB for flexibility)
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
    last_performance_update TIMESTAMP WITH TIME ZONE,
    
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    
    CONSTRAINT suppliers_business_code_unique UNIQUE(business_id, supplier_code),
    CONSTRAINT suppliers_business_tax_id_unique UNIQUE(business_id, tax_id),
    CONSTRAINT suppliers_performance_score_check CHECK (performance_score >= 0 AND performance_score <= 5),
    CONSTRAINT suppliers_quality_score_check CHECK (quality_score >= 0 AND quality_score <= 5),
    CONSTRAINT suppliers_grade_check CHECK (performance_grade IN ('A', 'B', 'C', 'D', 'F'))
);

-- Indexes for suppliers
CREATE INDEX idx_suppliers_business_id ON suppliers(business_id);
CREATE INDEX idx_suppliers_status ON suppliers(business_id, status);
CREATE INDEX idx_suppliers_code ON suppliers(business_id, supplier_code);
CREATE INDEX idx_suppliers_name ON suppliers USING GIN(to_tsvector('english', name));
CREATE INDEX idx_suppliers_preferred ON suppliers(business_id, is_preferred);
CREATE INDEX idx_suppliers_performance ON suppliers(business_id, performance_grade, performance_score);

-- =============================================
-- PRODUCTS TABLE
-- Complete product management with inventory tracking
-- =============================================
CREATE TABLE IF NOT EXISTS products (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    category_id UUID REFERENCES product_categories(id) ON DELETE SET NULL,
    
    -- Basic product information
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    long_description TEXT,
    
    -- Product classification
    product_type VARCHAR(20) NOT NULL CHECK (product_type IN ('product', 'service', 'bundle', 'subscription', 'maintenance_plan', 'digital')) DEFAULT 'product',
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive', 'discontinued', 'draft', 'out_of_stock')) DEFAULT 'active',
    
    -- Pricing information
    pricing_model VARCHAR(20) NOT NULL CHECK (pricing_model IN ('fixed', 'hourly', 'per_unit', 'tiered', 'custom')) DEFAULT 'fixed',
    unit_price DECIMAL(15,2) NOT NULL DEFAULT 0,
    cost_price DECIMAL(15,2) NOT NULL DEFAULT 0,
    minimum_price DECIMAL(15,2) DEFAULT 0,
    markup_percentage DECIMAL(5,2) DEFAULT 0,
    
    -- Units and measurements
    unit_of_measure VARCHAR(20) NOT NULL CHECK (unit_of_measure IN ('each', 'hour', 'day', 'week', 'month', 'year', 'square_foot', 'cubic_foot', 'linear_foot', 'gallon', 'liter', 'pound', 'kilogram', 'ton', 'meter', 'kilometer', 'mile', 'piece', 'box', 'case')) DEFAULT 'each',
    weight DECIMAL(10,3),
    dimensions JSONB, -- {"length": 10, "width": 5, "height": 3, "unit": "inches"}
    
    -- Inventory management
    track_inventory BOOLEAN NOT NULL DEFAULT true,
    current_stock DECIMAL(15,3) NOT NULL DEFAULT 0,
    reserved_stock DECIMAL(15,3) NOT NULL DEFAULT 0,
    available_stock DECIMAL(15,3) NOT NULL DEFAULT 0,
    
    -- Reorder management
    reorder_point DECIMAL(15,3) DEFAULT 0,
    reorder_quantity DECIMAL(15,3) DEFAULT 0,
    minimum_stock_level DECIMAL(15,3) DEFAULT 0,
    maximum_stock_level DECIMAL(15,3) DEFAULT 0,
    
    -- Costing method and calculations
    costing_method VARCHAR(25) NOT NULL CHECK (costing_method IN ('fifo', 'lifo', 'weighted_average', 'specific_identification', 'standard_cost')) DEFAULT 'weighted_average',
    weighted_average_cost DECIMAL(15,4) NOT NULL DEFAULT 0,
    last_cost DECIMAL(15,2) DEFAULT 0,
    standard_cost DECIMAL(15,2) DEFAULT 0,
    
    -- Financial accounts
    inventory_account VARCHAR(50),
    cost_of_goods_sold_account VARCHAR(50),
    income_account VARCHAR(50),
    
    -- Tax information
    tax_rate DECIMAL(5,4) DEFAULT 0,
    tax_category VARCHAR(50),
    is_taxable BOOLEAN NOT NULL DEFAULT true,
    
    -- Supplier information
    primary_supplier_id UUID REFERENCES suppliers(id) ON DELETE SET NULL,
    supplier_sku VARCHAR(100),
    lead_time_days INTEGER DEFAULT 0,
    
    -- Additional metadata
    barcode VARCHAR(100),
    qr_code VARCHAR(255),
    images JSONB, -- Array of image URLs
    attachments JSONB, -- Array of document URLs
    notes TEXT,
    tags TEXT[],
    
    -- Status flags
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_featured BOOLEAN NOT NULL DEFAULT false,
    is_digital BOOLEAN NOT NULL DEFAULT false,
    is_service BOOLEAN NOT NULL DEFAULT false,
    
    -- Analytics fields
    total_sold DECIMAL(15,3) NOT NULL DEFAULT 0,
    total_revenue DECIMAL(15,2) NOT NULL DEFAULT 0,
    last_sold_date TIMESTAMP WITH TIME ZONE,
    last_purchased_date TIMESTAMP WITH TIME ZONE,
    last_inventory_update TIMESTAMP WITH TIME ZONE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    
    CONSTRAINT products_business_sku_unique UNIQUE(business_id, sku),
    CONSTRAINT products_stock_check CHECK (current_stock >= 0 AND reserved_stock >= 0 AND available_stock >= 0),
    CONSTRAINT products_reorder_check CHECK (reorder_point >= 0 AND reorder_quantity >= 0),
    CONSTRAINT products_price_check CHECK (unit_price >= 0 AND cost_price >= 0),
    CONSTRAINT products_available_stock_calc CHECK (available_stock = current_stock - reserved_stock)
);

-- Indexes for products
CREATE INDEX idx_products_business_id ON products(business_id);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_sku ON products(business_id, sku);
CREATE INDEX idx_products_name ON products USING GIN(to_tsvector('english', name));
CREATE INDEX idx_products_status ON products(business_id, status);
CREATE INDEX idx_products_type ON products(business_id, product_type);
CREATE INDEX idx_products_inventory ON products(business_id, track_inventory, current_stock);
CREATE INDEX idx_products_reorder ON products(business_id) WHERE current_stock <= reorder_point;
CREATE INDEX idx_products_supplier ON products(primary_supplier_id);
CREATE INDEX idx_products_active ON products(business_id, is_active);

-- =============================================
-- PURCHASE ORDERS TABLE
-- Purchase order management with workflow support
-- =============================================
CREATE TABLE IF NOT EXISTS purchase_orders (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT,
    
    -- Order identification
    po_number VARCHAR(50) NOT NULL,
    reference_number VARCHAR(100),
    
    -- Order dates
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expected_delivery_date DATE,
    requested_delivery_date DATE,
    actual_delivery_date DATE,
    
    -- Status and workflow
    status VARCHAR(25) NOT NULL CHECK (status IN ('draft', 'sent', 'confirmed', 'partially_received', 'received', 'cancelled', 'closed')) DEFAULT 'draft',
    approval_status VARCHAR(20) NOT NULL CHECK (approval_status IN ('pending', 'approved', 'rejected', 'not_required')) DEFAULT 'not_required',
    current_approval_level INTEGER DEFAULT 0,
    required_approval_levels INTEGER DEFAULT 0,
    
    -- Financial information
    subtotal DECIMAL(15,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    shipping_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    other_charges DECIMAL(15,2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Delivery information
    delivery_address JSONB,
    delivery_instructions TEXT,
    shipping_method VARCHAR(100),
    
    -- Payment information
    payment_terms_days INTEGER DEFAULT 30,
    early_payment_discount_percentage DECIMAL(5,2) DEFAULT 0,
    early_payment_discount_days INTEGER DEFAULT 0,
    
    -- Communication tracking
    sent_to_supplier_at TIMESTAMP WITH TIME ZONE,
    sent_by VARCHAR(255),
    confirmed_by_supplier_at TIMESTAMP WITH TIME ZONE,
    supplier_confirmation_number VARCHAR(100),
    
    -- Additional information
    notes TEXT,
    internal_notes TEXT,
    terms_and_conditions TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    
    CONSTRAINT purchase_orders_business_po_number_unique UNIQUE(business_id, po_number),
    CONSTRAINT purchase_orders_amount_check CHECK (subtotal >= 0 AND total_amount >= 0),
    CONSTRAINT purchase_orders_approval_level_check CHECK (current_approval_level <= required_approval_levels)
);

-- Indexes for purchase orders
CREATE INDEX idx_purchase_orders_business_id ON purchase_orders(business_id);
CREATE INDEX idx_purchase_orders_supplier_id ON purchase_orders(supplier_id);
CREATE INDEX idx_purchase_orders_po_number ON purchase_orders(business_id, po_number);
CREATE INDEX idx_purchase_orders_status ON purchase_orders(business_id, status);
CREATE INDEX idx_purchase_orders_approval ON purchase_orders(business_id, approval_status);
CREATE INDEX idx_purchase_orders_dates ON purchase_orders(business_id, order_date, expected_delivery_date);

-- =============================================
-- PURCHASE ORDER LINE ITEMS TABLE
-- Individual line items for purchase orders
-- =============================================
CREATE TABLE IF NOT EXISTS purchase_order_line_items (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    purchase_order_id UUID NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE RESTRICT,
    
    -- Line item details
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    sku VARCHAR(100),
    
    -- Quantities
    quantity_ordered DECIMAL(15,3) NOT NULL DEFAULT 0,
    quantity_received DECIMAL(15,3) NOT NULL DEFAULT 0,
    quantity_remaining DECIMAL(15,3) NOT NULL DEFAULT 0,
    
    -- Pricing
    unit_cost DECIMAL(15,4) NOT NULL DEFAULT 0,
    total_cost DECIMAL(15,2) NOT NULL DEFAULT 0,
    
    -- Unit of measure
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'each',
    
    -- Receiving tracking
    is_fully_received BOOLEAN NOT NULL DEFAULT false,
    last_received_date TIMESTAMP WITH TIME ZONE,
    
    -- Additional information
    notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT po_line_items_quantity_check CHECK (quantity_ordered > 0 AND quantity_received >= 0),
    CONSTRAINT po_line_items_cost_check CHECK (unit_cost >= 0 AND total_cost >= 0),
    CONSTRAINT po_line_items_remaining_calc CHECK (quantity_remaining = quantity_ordered - quantity_received)
);

-- Indexes for purchase order line items
CREATE INDEX idx_po_line_items_po_id ON purchase_order_line_items(purchase_order_id);
CREATE INDEX idx_po_line_items_product_id ON purchase_order_line_items(product_id);
CREATE INDEX idx_po_line_items_pending_receipt ON purchase_order_line_items(purchase_order_id) WHERE NOT is_fully_received;

-- =============================================
-- STOCK MOVEMENTS TABLE
-- Complete audit trail for inventory changes
-- =============================================
CREATE TABLE IF NOT EXISTS stock_movements (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    
    -- Movement identification
    movement_number VARCHAR(50),
    batch_number VARCHAR(50),
    
    -- Movement details
    movement_type VARCHAR(20) NOT NULL CHECK (movement_type IN ('purchase', 'sale', 'adjustment', 'transfer', 'return', 'damage', 'shrinkage', 'promotion', 'sample', 'production', 'consumption', 'initial_stock', 'recount')),
    movement_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Quantities and costs
    quantity DECIMAL(15,3) NOT NULL,
    unit_cost DECIMAL(15,4) NOT NULL DEFAULT 0,
    total_cost DECIMAL(15,2) NOT NULL DEFAULT 0,
    
    -- Before/after snapshots
    quantity_before DECIMAL(15,3) NOT NULL DEFAULT 0,
    quantity_after DECIMAL(15,3) NOT NULL DEFAULT 0,
    cost_before DECIMAL(15,4) NOT NULL DEFAULT 0,
    cost_after DECIMAL(15,4) NOT NULL DEFAULT 0,
    
    -- Reference information
    reference_type VARCHAR(50), -- 'purchase_order', 'sale', 'adjustment', etc.
    reference_id UUID,
    reference_number VARCHAR(100),
    
    -- Location tracking (for future multi-location support)
    from_location_id UUID,
    to_location_id UUID,
    location_id UUID, -- Current location
    
    -- Additional cost information
    landed_cost DECIMAL(15,4) DEFAULT 0, -- Including shipping, duties, etc.
    freight_cost DECIMAL(15,2) DEFAULT 0,
    duty_cost DECIMAL(15,2) DEFAULT 0,
    other_costs DECIMAL(15,2) DEFAULT 0,
    
    -- Context and approval
    reason VARCHAR(255),
    notes TEXT,
    requires_approval BOOLEAN NOT NULL DEFAULT false,
    is_approved BOOLEAN NOT NULL DEFAULT true,
    approved_by VARCHAR(255),
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Reversal tracking
    is_reversed BOOLEAN NOT NULL DEFAULT false,
    reversed_by VARCHAR(255),
    reversed_at TIMESTAMP WITH TIME ZONE,
    reversal_movement_id UUID REFERENCES stock_movements(id),
    original_movement_id UUID REFERENCES stock_movements(id),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    
    CONSTRAINT stock_movements_quantity_change CHECK (quantity != 0),
    CONSTRAINT stock_movements_costs_check CHECK (unit_cost >= 0 AND total_cost >= 0),
    CONSTRAINT stock_movements_before_after_calc CHECK (quantity_after = quantity_before + quantity)
);

-- Indexes for stock movements
CREATE INDEX idx_stock_movements_business_id ON stock_movements(business_id);
CREATE INDEX idx_stock_movements_product_id ON stock_movements(product_id);
CREATE INDEX idx_stock_movements_date ON stock_movements(business_id, movement_date DESC);
CREATE INDEX idx_stock_movements_type ON stock_movements(business_id, movement_type);
CREATE INDEX idx_stock_movements_reference ON stock_movements(reference_type, reference_id);
CREATE INDEX idx_stock_movements_batch ON stock_movements(batch_number) WHERE batch_number IS NOT NULL;
CREATE INDEX idx_stock_movements_approval ON stock_movements(business_id) WHERE requires_approval AND NOT is_approved;
CREATE INDEX idx_stock_movements_reversal ON stock_movements(original_movement_id) WHERE original_movement_id IS NOT NULL;

-- =============================================
-- SUPPLIER CONTACTS TABLE
-- Multiple contacts per supplier
-- =============================================
CREATE TABLE IF NOT EXISTS supplier_contacts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
    
    -- Contact information
    name VARCHAR(100) NOT NULL,
    title VARCHAR(100),
    department VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    mobile VARCHAR(50),
    
    -- Contact type and preferences
    contact_type VARCHAR(20) CHECK (contact_type IN ('primary', 'accounting', 'sales', 'technical', 'shipping', 'other')) DEFAULT 'other',
    is_primary BOOLEAN NOT NULL DEFAULT false,
    
    -- Communication preferences
    preferred_communication_method VARCHAR(20) CHECK (preferred_communication_method IN ('email', 'phone', 'mobile', 'fax')) DEFAULT 'email',
    
    -- Additional information
    notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT supplier_contacts_primary_unique UNIQUE(supplier_id, is_primary) DEFERRABLE INITIALLY DEFERRED
);

-- Indexes for supplier contacts
CREATE INDEX idx_supplier_contacts_supplier_id ON supplier_contacts(supplier_id);
CREATE INDEX idx_supplier_contacts_primary ON supplier_contacts(supplier_id, is_primary);
CREATE INDEX idx_supplier_contacts_type ON supplier_contacts(supplier_id, contact_type);

-- =============================================
-- PRODUCT PRICING TIERS TABLE
-- Volume-based pricing for products
-- =============================================
CREATE TABLE IF NOT EXISTS product_pricing_tiers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    
    -- Tier configuration
    tier_name VARCHAR(50) NOT NULL,
    minimum_quantity DECIMAL(15,3) NOT NULL DEFAULT 0,
    maximum_quantity DECIMAL(15,3),
    
    -- Pricing
    tier_price DECIMAL(15,2) NOT NULL,
    discount_percentage DECIMAL(5,2) DEFAULT 0,
    
    -- Validity
    effective_date DATE DEFAULT CURRENT_DATE,
    expiry_date DATE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT pricing_tiers_quantity_check CHECK (minimum_quantity >= 0 AND (maximum_quantity IS NULL OR maximum_quantity > minimum_quantity)),
    CONSTRAINT pricing_tiers_price_check CHECK (tier_price >= 0),
    CONSTRAINT pricing_tiers_product_tier_unique UNIQUE(product_id, tier_name)
);

-- Indexes for product pricing tiers
CREATE INDEX idx_pricing_tiers_product_id ON product_pricing_tiers(product_id);
CREATE INDEX idx_pricing_tiers_active ON product_pricing_tiers(product_id, is_active);
CREATE INDEX idx_pricing_tiers_quantity ON product_pricing_tiers(product_id, minimum_quantity, maximum_quantity);

-- =============================================
-- PURCHASE ORDER APPROVALS TABLE
-- Approval workflow tracking for purchase orders
-- =============================================
CREATE TABLE IF NOT EXISTS purchase_order_approvals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    purchase_order_id UUID NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    
    -- Approval details
    approval_level INTEGER NOT NULL,
    approver_id VARCHAR(255) NOT NULL,
    approver_name VARCHAR(100),
    
    -- Status and timing
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional information
    comments TEXT,
    rejection_reason TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT po_approvals_level_approver_unique UNIQUE(purchase_order_id, approval_level, approver_id)
);

-- Indexes for purchase order approvals
CREATE INDEX idx_po_approvals_po_id ON purchase_order_approvals(purchase_order_id);
CREATE INDEX idx_po_approvals_approver ON purchase_order_approvals(approver_id, status);
CREATE INDEX idx_po_approvals_pending ON purchase_order_approvals(purchase_order_id, approval_level) WHERE status = 'pending';

-- =============================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =============================================

-- Update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_product_categories_updated_at BEFORE UPDATE ON product_categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_purchase_orders_updated_at BEFORE UPDATE ON purchase_orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_po_line_items_updated_at BEFORE UPDATE ON purchase_order_line_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_supplier_contacts_updated_at BEFORE UPDATE ON supplier_contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pricing_tiers_updated_at BEFORE UPDATE ON product_pricing_tiers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Product available stock calculation trigger
CREATE OR REPLACE FUNCTION calculate_available_stock()
RETURNS TRIGGER AS $$
BEGIN
    NEW.available_stock = NEW.current_stock - NEW.reserved_stock;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER calculate_product_available_stock 
    BEFORE INSERT OR UPDATE OF current_stock, reserved_stock ON products 
    FOR EACH ROW EXECUTE FUNCTION calculate_available_stock();

-- Purchase order line item quantity remaining calculation
CREATE OR REPLACE FUNCTION calculate_quantity_remaining()
RETURNS TRIGGER AS $$
BEGIN
    NEW.quantity_remaining = NEW.quantity_ordered - NEW.quantity_received;
    NEW.is_fully_received = (NEW.quantity_remaining <= 0);
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER calculate_po_line_quantity_remaining 
    BEFORE INSERT OR UPDATE OF quantity_ordered, quantity_received ON purchase_order_line_items 
    FOR EACH ROW EXECUTE FUNCTION calculate_quantity_remaining();

-- Stock movement quantity validation
CREATE OR REPLACE FUNCTION validate_stock_movement()
RETURNS TRIGGER AS $$
BEGIN
    NEW.quantity_after = NEW.quantity_before + NEW.quantity;
    NEW.total_cost = NEW.quantity * NEW.unit_cost;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER validate_stock_movement_trigger 
    BEFORE INSERT OR UPDATE ON stock_movements 
    FOR EACH ROW EXECUTE FUNCTION validate_stock_movement();

-- =============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================

-- Enable RLS on all tables
ALTER TABLE product_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_order_line_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_movements ENABLE ROW LEVEL SECURITY;
ALTER TABLE supplier_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_pricing_tiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_order_approvals ENABLE ROW LEVEL SECURITY;

-- RLS Policies for product_categories
CREATE POLICY "Users can view product categories in their business" ON product_categories
    FOR SELECT USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can insert product categories in their business" ON product_categories
    FOR INSERT WITH CHECK (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can update product categories in their business" ON product_categories
    FOR UPDATE USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete product categories in their business" ON product_categories
    FOR DELETE USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

-- RLS Policies for suppliers
CREATE POLICY "Users can view suppliers in their business" ON suppliers
    FOR SELECT USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can insert suppliers in their business" ON suppliers
    FOR INSERT WITH CHECK (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can update suppliers in their business" ON suppliers
    FOR UPDATE USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete suppliers in their business" ON suppliers
    FOR DELETE USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

-- RLS Policies for products
CREATE POLICY "Users can view products in their business" ON products
    FOR SELECT USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can insert products in their business" ON products
    FOR INSERT WITH CHECK (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can update products in their business" ON products
    FOR UPDATE USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete products in their business" ON products
    FOR DELETE USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

-- RLS Policies for purchase_orders
CREATE POLICY "Users can view purchase orders in their business" ON purchase_orders
    FOR SELECT USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can insert purchase orders in their business" ON purchase_orders
    FOR INSERT WITH CHECK (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can update purchase orders in their business" ON purchase_orders
    FOR UPDATE USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete purchase orders in their business" ON purchase_orders
    FOR DELETE USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

-- RLS Policies for purchase_order_line_items (inherit from purchase_orders)
CREATE POLICY "Users can view PO line items in their business" ON purchase_order_line_items
    FOR SELECT USING (purchase_order_id IN (SELECT id FROM purchase_orders WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

CREATE POLICY "Users can insert PO line items in their business" ON purchase_order_line_items
    FOR INSERT WITH CHECK (purchase_order_id IN (SELECT id FROM purchase_orders WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

CREATE POLICY "Users can update PO line items in their business" ON purchase_order_line_items
    FOR UPDATE USING (purchase_order_id IN (SELECT id FROM purchase_orders WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

CREATE POLICY "Users can delete PO line items in their business" ON purchase_order_line_items
    FOR DELETE USING (purchase_order_id IN (SELECT id FROM purchase_orders WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

-- RLS Policies for stock_movements
CREATE POLICY "Users can view stock movements in their business" ON stock_movements
    FOR SELECT USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can insert stock movements in their business" ON stock_movements
    FOR INSERT WITH CHECK (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

CREATE POLICY "Users can update stock movements in their business" ON stock_movements
    FOR UPDATE USING (business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid()));

-- RLS Policies for supplier_contacts (inherit from suppliers)
CREATE POLICY "Users can view supplier contacts in their business" ON supplier_contacts
    FOR SELECT USING (supplier_id IN (SELECT id FROM suppliers WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

CREATE POLICY "Users can insert supplier contacts in their business" ON supplier_contacts
    FOR INSERT WITH CHECK (supplier_id IN (SELECT id FROM suppliers WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

CREATE POLICY "Users can update supplier contacts in their business" ON supplier_contacts
    FOR UPDATE USING (supplier_id IN (SELECT id FROM suppliers WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

CREATE POLICY "Users can delete supplier contacts in their business" ON supplier_contacts
    FOR DELETE USING (supplier_id IN (SELECT id FROM suppliers WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

-- RLS Policies for product_pricing_tiers (inherit from products)
CREATE POLICY "Users can view pricing tiers in their business" ON product_pricing_tiers
    FOR SELECT USING (product_id IN (SELECT id FROM products WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

CREATE POLICY "Users can insert pricing tiers in their business" ON product_pricing_tiers
    FOR INSERT WITH CHECK (product_id IN (SELECT id FROM products WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

CREATE POLICY "Users can update pricing tiers in their business" ON product_pricing_tiers
    FOR UPDATE USING (product_id IN (SELECT id FROM products WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

CREATE POLICY "Users can delete pricing tiers in their business" ON product_pricing_tiers
    FOR DELETE USING (product_id IN (SELECT id FROM products WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

-- RLS Policies for purchase_order_approvals (inherit from purchase_orders)
CREATE POLICY "Users can view PO approvals in their business" ON purchase_order_approvals
    FOR SELECT USING (purchase_order_id IN (SELECT id FROM purchase_orders WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

CREATE POLICY "Users can insert PO approvals in their business" ON purchase_order_approvals
    FOR INSERT WITH CHECK (purchase_order_id IN (SELECT id FROM purchase_orders WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

CREATE POLICY "Users can update PO approvals in their business" ON purchase_order_approvals
    FOR UPDATE USING (purchase_order_id IN (SELECT id FROM purchase_orders WHERE business_id IN (SELECT business_id FROM business_memberships WHERE user_id = auth.uid())));

-- =============================================
-- MIGRATION COMPLETE
-- =============================================

-- Hero365 Inventory Management System Schema successfully created
-- All tables, indexes, triggers, and RLS policies are now in place
-- 
-- Tables created:
-- - product_categories (hierarchical structure)
-- - suppliers (with performance tracking)
-- - products (complete inventory management)
-- - purchase_orders (workflow support)
-- - purchase_order_line_items
-- - stock_movements (audit trail)
-- - supplier_contacts
-- - product_pricing_tiers
-- - purchase_order_approvals
--
-- Features included:
-- - Business-level data isolation via RLS
-- - Comprehensive indexing for performance
-- - Automated triggers for data consistency
-- - Multi-location inventory support
-- - Complete audit trail capabilities
-- - Purchase order approval workflows 