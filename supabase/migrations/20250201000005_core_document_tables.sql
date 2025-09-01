-- =============================================
-- CORE DOCUMENT TABLES
-- =============================================
-- Templates, estimates, invoices, and documents
-- Depends on: businesses, contacts, projects tables

-- =============================================
-- TEMPLATES TABLE
-- =============================================

CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Template Info
    name VARCHAR(255) NOT NULL,
    template_type VARCHAR(50) NOT NULL, -- 'estimate', 'invoice', 'contract', 'email'
    category VARCHAR(100),
    
    -- Content
    content JSONB NOT NULL DEFAULT '{}',
    layout_style VARCHAR(50) DEFAULT 'modern',
    
    -- Status
    is_system BOOLEAN DEFAULT false, -- System templates vs business templates
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    
    -- Usage
    usage_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- ESTIMATES TABLE
-- =============================================

CREATE TABLE estimates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id),
    project_id UUID REFERENCES projects(id),
    
    -- Estimate Info
    estimate_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255),
    description TEXT,
    
    -- Client Info (denormalized for document generation)
    client_name VARCHAR(255),
    client_email VARCHAR(255),
    client_phone VARCHAR(20),
    client_address JSONB, -- Full address object
    
    -- Financial
    subtotal DECIMAL(12,2) DEFAULT 0,
    tax_rate DECIMAL(5,4) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    
    -- Status & Dates
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'sent', 'viewed', 'approved', 'rejected', 'expired'
    issue_date DATE DEFAULT CURRENT_DATE,
    expiry_date DATE,
    po_number VARCHAR(100),
    
    -- Template & Presentation
    template_id UUID REFERENCES templates(id),
    document_type VARCHAR(20) DEFAULT 'estimate',
    
    -- Metadata
    notes TEXT,
    terms_and_conditions TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- ESTIMATE ITEMS TABLE
-- =============================================

CREATE TABLE estimate_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estimate_id UUID NOT NULL REFERENCES estimates(id) ON DELETE CASCADE,
    
    -- Item Info
    item_type VARCHAR(50) DEFAULT 'service', -- 'service', 'product', 'labor', 'material'
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Pricing
    quantity DECIMAL(10,3) DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    
    -- Organization
    display_order INTEGER DEFAULT 0,
    category VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- INVOICES TABLE
-- =============================================

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id),
    project_id UUID REFERENCES projects(id),
    estimate_id UUID REFERENCES estimates(id), -- If converted from estimate
    
    -- Invoice Info
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255),
    description TEXT,
    
    -- Client Info (denormalized)
    client_name VARCHAR(255),
    client_email VARCHAR(255),
    client_phone VARCHAR(20),
    client_address JSONB,
    
    -- Financial
    subtotal DECIMAL(12,2) DEFAULT 0,
    tax_rate DECIMAL(5,4) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    paid_amount DECIMAL(12,2) DEFAULT 0,
    balance_due DECIMAL(12,2) DEFAULT 0,
    
    -- Status & Dates
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'sent', 'viewed', 'partial', 'paid', 'overdue', 'cancelled'
    issue_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    paid_date DATE,
    po_number VARCHAR(100),
    
    -- Template & Presentation
    template_id UUID REFERENCES templates(id),
    document_type VARCHAR(20) DEFAULT 'invoice',
    
    -- Metadata
    notes TEXT,
    terms_and_conditions TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- INVOICE ITEMS TABLE
-- =============================================

CREATE TABLE invoice_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    
    -- Item Info
    item_type VARCHAR(50) DEFAULT 'service',
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Pricing
    quantity DECIMAL(10,3) DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    
    -- Organization
    display_order INTEGER DEFAULT 0,
    category VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- BASIC INDEXES
-- =============================================

CREATE INDEX idx_templates_business ON templates(business_id);
CREATE INDEX idx_templates_type ON templates(template_type);
CREATE INDEX idx_templates_system ON templates(is_system);
CREATE INDEX idx_templates_active ON templates(is_active);

CREATE INDEX idx_estimates_business ON estimates(business_id);
CREATE INDEX idx_estimates_contact ON estimates(contact_id);
CREATE INDEX idx_estimates_project ON estimates(project_id);
CREATE INDEX idx_estimates_number ON estimates(estimate_number);
CREATE INDEX idx_estimates_status ON estimates(status);
CREATE INDEX idx_estimates_issue_date ON estimates(issue_date);

CREATE INDEX idx_estimate_items_estimate ON estimate_items(estimate_id);
CREATE INDEX idx_estimate_items_order ON estimate_items(display_order);

CREATE INDEX idx_invoices_business ON invoices(business_id);
CREATE INDEX idx_invoices_contact ON invoices(contact_id);
CREATE INDEX idx_invoices_project ON invoices(project_id);
CREATE INDEX idx_invoices_estimate ON invoices(estimate_id);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_issue_date ON invoices(issue_date);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);

CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);
CREATE INDEX idx_invoice_items_order ON invoice_items(display_order);

COMMIT;
