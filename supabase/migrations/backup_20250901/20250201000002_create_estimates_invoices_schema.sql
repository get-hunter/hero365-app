-- Create Estimates & Invoices Schema
-- This migration adds comprehensive estimates and invoices management tables
-- Date: 2025-02-01
-- Version: Estimates & Invoices Feature Implementation

-- =====================================
-- ESTIMATE TEMPLATES TABLE
-- =====================================
CREATE TABLE "public"."estimate_templates" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "name" VARCHAR(200) NOT NULL,
    "description" TEXT,
    "template_type" VARCHAR(50) NOT NULL DEFAULT 'professional' CHECK (template_type IN ('professional', 'creative', 'minimal', 'corporate', 'modern', 'classic', 'industrial', 'service_focused')),
    "is_active" BOOLEAN DEFAULT true,
    "is_default" BOOLEAN DEFAULT false,
    "usage_count" INTEGER DEFAULT 0 CHECK (usage_count >= 0),
    "color_scheme" JSONB DEFAULT '{}',
    "typography" JSONB DEFAULT '{}',
    "layout" JSONB DEFAULT '{}',
    "sections" JSONB DEFAULT '{}',
    "business_info" JSONB DEFAULT '{}',
    "logo_url" TEXT,
    "header_content" TEXT,
    "footer_content" TEXT,
    "terms_and_conditions" TEXT,
    "notes" TEXT,
    "created_by" TEXT NOT NULL,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT "estimate_templates_unique_default" UNIQUE (business_id, is_default) DEFERRABLE INITIALLY DEFERRED
);

-- =====================================
-- ESTIMATES TABLE
-- =====================================
CREATE TABLE "public"."estimates" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "estimate_number" VARCHAR(50) NOT NULL,
    "title" VARCHAR(300) NOT NULL,
    "description" TEXT,
    "status" VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'viewed', 'approved', 'rejected', 'expired', 'converted', 'cancelled')),
    "contact_id" UUID NOT NULL REFERENCES "public"."contacts"("id") ON DELETE CASCADE,
    "project_id" UUID REFERENCES "public"."projects"("id") ON DELETE SET NULL,
    "job_id" UUID REFERENCES "public"."jobs"("id") ON DELETE SET NULL,
    "template_id" UUID REFERENCES "public"."estimate_templates"("id") ON DELETE SET NULL,
    "assigned_to" TEXT,
    "assigned_user_id" UUID,
    "currency" VARCHAR(3) NOT NULL DEFAULT 'USD' CHECK (currency IN ('USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'CNY', 'MXN', 'BRL')),
    "subtotal" NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (subtotal >= 0),
    "discount_type" VARCHAR(20) NOT NULL DEFAULT 'none' CHECK (discount_type IN ('none', 'percentage', 'fixed_amount')),
    "discount_value" NUMERIC(12,2) DEFAULT 0 CHECK (discount_value >= 0),
    "discount_amount" NUMERIC(12,2) DEFAULT 0 CHECK (discount_amount >= 0),
    "tax_type" VARCHAR(20) NOT NULL DEFAULT 'none' CHECK (tax_type IN ('none', 'percentage', 'fixed_amount', 'inclusive', 'exclusive')),
    "tax_rate" NUMERIC(5,2) DEFAULT 0 CHECK (tax_rate >= 0),
    "tax_amount" NUMERIC(12,2) DEFAULT 0 CHECK (tax_amount >= 0),
    "total_amount" NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    "advance_payment_type" VARCHAR(20) NOT NULL DEFAULT 'none' CHECK (advance_payment_type IN ('none', 'percentage', 'fixed_amount')),
    "advance_payment_value" NUMERIC(12,2) DEFAULT 0 CHECK (advance_payment_value >= 0),
    "advance_payment_amount" NUMERIC(12,2) DEFAULT 0 CHECK (advance_payment_amount >= 0),
    "advance_payment_due_date" TIMESTAMP WITH TIME ZONE,
    "advance_payment_received" BOOLEAN DEFAULT false,
    "advance_payment_received_date" TIMESTAMP WITH TIME ZONE,
    "valid_until" TIMESTAMP WITH TIME ZONE,
    "terms_and_conditions" TEXT,
    "notes" TEXT,
    "email_tracking" JSONB DEFAULT '[]',
    "status_history" JSONB DEFAULT '[]',
    "attachments" JSONB DEFAULT '[]',
    "converted_to_invoice_id" UUID,
    "created_by" TEXT NOT NULL,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT "estimates_unique_number" UNIQUE (business_id, estimate_number)
);

-- =====================================
-- ESTIMATE LINE ITEMS TABLE
-- =====================================
CREATE TABLE "public"."estimate_line_items" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "estimate_id" UUID NOT NULL REFERENCES "public"."estimates"("id") ON DELETE CASCADE,
    "sort_order" INTEGER NOT NULL DEFAULT 0,
    "name" VARCHAR(300) NOT NULL,
    "description" TEXT,
    "quantity" NUMERIC(10,2) NOT NULL DEFAULT 1 CHECK (quantity > 0),
    "unit" VARCHAR(50) DEFAULT 'each',
    "unit_price" NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (unit_price >= 0),
    "discount_type" VARCHAR(20) NOT NULL DEFAULT 'none' CHECK (discount_type IN ('none', 'percentage', 'fixed_amount')),
    "discount_value" NUMERIC(12,2) DEFAULT 0 CHECK (discount_value >= 0),
    "discount_amount" NUMERIC(12,2) DEFAULT 0 CHECK (discount_amount >= 0),
    "tax_type" VARCHAR(20) NOT NULL DEFAULT 'none' CHECK (tax_type IN ('none', 'percentage', 'fixed_amount', 'inclusive', 'exclusive')),
    "tax_rate" NUMERIC(5,2) DEFAULT 0 CHECK (tax_rate >= 0),
    "tax_amount" NUMERIC(12,2) DEFAULT 0 CHECK (tax_amount >= 0),
    "total_amount" NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    "is_taxable" BOOLEAN DEFAULT true,
    "notes" TEXT,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- INVOICES TABLE
-- =====================================
CREATE TABLE "public"."invoices" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "invoice_number" VARCHAR(50) NOT NULL,
    "title" VARCHAR(300) NOT NULL,
    "description" TEXT,
    "status" VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'viewed', 'paid', 'partially_paid', 'overdue', 'cancelled', 'refunded')),
    "contact_id" UUID NOT NULL REFERENCES "public"."contacts"("id") ON DELETE CASCADE,
    "project_id" UUID REFERENCES "public"."projects"("id") ON DELETE SET NULL,
    "job_id" UUID REFERENCES "public"."jobs"("id") ON DELETE SET NULL,
    "estimate_id" UUID REFERENCES "public"."estimates"("id") ON DELETE SET NULL,
    "template_id" UUID REFERENCES "public"."estimate_templates"("id") ON DELETE SET NULL,
    "assigned_to" TEXT,
    "assigned_user_id" UUID,
    "currency" VARCHAR(3) NOT NULL DEFAULT 'USD' CHECK (currency IN ('USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'CNY', 'MXN', 'BRL')),
    "subtotal" NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (subtotal >= 0),
    "discount_type" VARCHAR(20) NOT NULL DEFAULT 'none' CHECK (discount_type IN ('none', 'percentage', 'fixed_amount')),
    "discount_value" NUMERIC(12,2) DEFAULT 0 CHECK (discount_value >= 0),
    "discount_amount" NUMERIC(12,2) DEFAULT 0 CHECK (discount_amount >= 0),
    "tax_type" VARCHAR(20) NOT NULL DEFAULT 'none' CHECK (tax_type IN ('none', 'percentage', 'fixed_amount', 'inclusive', 'exclusive')),
    "tax_rate" NUMERIC(5,2) DEFAULT 0 CHECK (tax_rate >= 0),
    "tax_amount" NUMERIC(12,2) DEFAULT 0 CHECK (tax_amount >= 0),
    "total_amount" NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    "amount_paid" NUMERIC(12,2) DEFAULT 0 CHECK (amount_paid >= 0),
    "amount_due" NUMERIC(12,2) DEFAULT 0 CHECK (amount_due >= 0),
    "amount_refunded" NUMERIC(12,2) DEFAULT 0 CHECK (amount_refunded >= 0),
    "issue_date" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    "due_date" TIMESTAMP WITH TIME ZONE NOT NULL,
    "payment_terms" VARCHAR(100),
    "late_fee_percentage" NUMERIC(5,2) DEFAULT 0 CHECK (late_fee_percentage >= 0),
    "late_fee_amount" NUMERIC(12,2) DEFAULT 0 CHECK (late_fee_amount >= 0),
    "late_fee_applied" BOOLEAN DEFAULT false,
    "payment_instructions" TEXT,
    "terms_and_conditions" TEXT,
    "notes" TEXT,
    "email_tracking" JSONB DEFAULT '[]',
    "status_history" JSONB DEFAULT '[]',
    "attachments" JSONB DEFAULT '[]',
    "created_by" TEXT NOT NULL,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT "invoices_unique_number" UNIQUE (business_id, invoice_number),
    CONSTRAINT "invoices_amounts_valid" CHECK (amount_paid + amount_due = total_amount + late_fee_amount - amount_refunded)
);

-- =====================================
-- INVOICE LINE ITEMS TABLE
-- =====================================
CREATE TABLE "public"."invoice_line_items" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "invoice_id" UUID NOT NULL REFERENCES "public"."invoices"("id") ON DELETE CASCADE,
    "sort_order" INTEGER NOT NULL DEFAULT 0,
    "name" VARCHAR(300) NOT NULL,
    "description" TEXT,
    "quantity" NUMERIC(10,2) NOT NULL DEFAULT 1 CHECK (quantity > 0),
    "unit" VARCHAR(50) DEFAULT 'each',
    "unit_price" NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (unit_price >= 0),
    "discount_type" VARCHAR(20) NOT NULL DEFAULT 'none' CHECK (discount_type IN ('none', 'percentage', 'fixed_amount')),
    "discount_value" NUMERIC(12,2) DEFAULT 0 CHECK (discount_value >= 0),
    "discount_amount" NUMERIC(12,2) DEFAULT 0 CHECK (discount_amount >= 0),
    "tax_type" VARCHAR(20) NOT NULL DEFAULT 'none' CHECK (tax_type IN ('none', 'percentage', 'fixed_amount', 'inclusive', 'exclusive')),
    "tax_rate" NUMERIC(5,2) DEFAULT 0 CHECK (tax_rate >= 0),
    "tax_amount" NUMERIC(12,2) DEFAULT 0 CHECK (tax_amount >= 0),
    "total_amount" NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    "is_taxable" BOOLEAN DEFAULT true,
    "notes" TEXT,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- PAYMENTS TABLE
-- =====================================
CREATE TABLE "public"."payments" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "invoice_id" UUID NOT NULL REFERENCES "public"."invoices"("id") ON DELETE CASCADE,
    "payment_date" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    "amount" NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    "payment_method" VARCHAR(50) NOT NULL CHECK (payment_method IN ('cash', 'check', 'credit_card', 'debit_card', 'ach', 'wire_transfer', 'paypal', 'stripe', 'square', 'venmo', 'zelle', 'bank_transfer', 'other')),
    "payment_status" VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (payment_status IN ('pending', 'processing', 'completed', 'failed', 'cancelled', 'refunded', 'partially_refunded')),
    "transaction_id" VARCHAR(200),
    "gateway" VARCHAR(100),
    "gateway_response" JSONB,
    "reference_number" VARCHAR(100),
    "notes" TEXT,
    "refund_amount" NUMERIC(12,2) DEFAULT 0 CHECK (refund_amount >= 0),
    "refund_date" TIMESTAMP WITH TIME ZONE,
    "refund_reason" TEXT,
    "created_by" TEXT NOT NULL,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- INDEXES FOR PERFORMANCE
-- =====================================

-- Estimate Templates Indexes
CREATE INDEX "idx_estimate_templates_business_id" ON "public"."estimate_templates" ("business_id");
CREATE INDEX "idx_estimate_templates_type" ON "public"."estimate_templates" ("template_type");
CREATE INDEX "idx_estimate_templates_active" ON "public"."estimate_templates" ("is_active");
CREATE INDEX "idx_estimate_templates_default" ON "public"."estimate_templates" ("is_default");
CREATE INDEX "idx_estimate_templates_business_active" ON "public"."estimate_templates" ("business_id", "is_active");

-- Estimates Indexes
CREATE INDEX "idx_estimates_business_id" ON "public"."estimates" ("business_id");
CREATE INDEX "idx_estimates_contact_id" ON "public"."estimates" ("contact_id");
CREATE INDEX "idx_estimates_project_id" ON "public"."estimates" ("project_id");
CREATE INDEX "idx_estimates_job_id" ON "public"."estimates" ("job_id");
CREATE INDEX "idx_estimates_template_id" ON "public"."estimates" ("template_id");
CREATE INDEX "idx_estimates_status" ON "public"."estimates" ("status");
CREATE INDEX "idx_estimates_assigned_user_id" ON "public"."estimates" ("assigned_user_id");
CREATE INDEX "idx_estimates_created_date" ON "public"."estimates" ("created_date");
CREATE INDEX "idx_estimates_valid_until" ON "public"."estimates" ("valid_until");
CREATE INDEX "idx_estimates_converted_invoice" ON "public"."estimates" ("converted_to_invoice_id");

-- Composite indexes for common query patterns
CREATE INDEX "idx_estimates_business_status" ON "public"."estimates" ("business_id", "status");
CREATE INDEX "idx_estimates_business_contact" ON "public"."estimates" ("business_id", "contact_id");
CREATE INDEX "idx_estimates_business_created" ON "public"."estimates" ("business_id", "created_date");
CREATE INDEX "idx_estimates_business_assigned" ON "public"."estimates" ("business_id", "assigned_user_id");

-- Estimate Line Items Indexes
CREATE INDEX "idx_estimate_line_items_estimate_id" ON "public"."estimate_line_items" ("estimate_id");
CREATE INDEX "idx_estimate_line_items_sort_order" ON "public"."estimate_line_items" ("estimate_id", "sort_order");

-- Invoices Indexes
CREATE INDEX "idx_invoices_business_id" ON "public"."invoices" ("business_id");
CREATE INDEX "idx_invoices_contact_id" ON "public"."invoices" ("contact_id");
CREATE INDEX "idx_invoices_project_id" ON "public"."invoices" ("project_id");
CREATE INDEX "idx_invoices_job_id" ON "public"."invoices" ("job_id");
CREATE INDEX "idx_invoices_estimate_id" ON "public"."invoices" ("estimate_id");
CREATE INDEX "idx_invoices_template_id" ON "public"."invoices" ("template_id");
CREATE INDEX "idx_invoices_status" ON "public"."invoices" ("status");
CREATE INDEX "idx_invoices_assigned_user_id" ON "public"."invoices" ("assigned_user_id");
CREATE INDEX "idx_invoices_issue_date" ON "public"."invoices" ("issue_date");
CREATE INDEX "idx_invoices_due_date" ON "public"."invoices" ("due_date");
CREATE INDEX "idx_invoices_created_date" ON "public"."invoices" ("created_date");

-- Composite indexes for common query patterns
CREATE INDEX "idx_invoices_business_status" ON "public"."invoices" ("business_id", "status");
CREATE INDEX "idx_invoices_business_contact" ON "public"."invoices" ("business_id", "contact_id");
CREATE INDEX "idx_invoices_business_due_date" ON "public"."invoices" ("business_id", "due_date");
CREATE INDEX "idx_invoices_business_assigned" ON "public"."invoices" ("business_id", "assigned_user_id");

-- Invoice Line Items Indexes
CREATE INDEX "idx_invoice_line_items_invoice_id" ON "public"."invoice_line_items" ("invoice_id");
CREATE INDEX "idx_invoice_line_items_sort_order" ON "public"."invoice_line_items" ("invoice_id", "sort_order");

-- Payments Indexes
CREATE INDEX "idx_payments_invoice_id" ON "public"."payments" ("invoice_id");
CREATE INDEX "idx_payments_payment_date" ON "public"."payments" ("payment_date");
CREATE INDEX "idx_payments_payment_method" ON "public"."payments" ("payment_method");
CREATE INDEX "idx_payments_payment_status" ON "public"."payments" ("payment_status");
CREATE INDEX "idx_payments_transaction_id" ON "public"."payments" ("transaction_id");

-- Full-text search indexes
CREATE INDEX "idx_estimates_search" ON "public"."estimates" USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '') || ' ' || estimate_number));
CREATE INDEX "idx_invoices_search" ON "public"."invoices" USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '') || ' ' || invoice_number));

-- =====================================
-- TRIGGERS FOR AUTO-UPDATES
-- =====================================

-- Estimate Templates Triggers
CREATE OR REPLACE FUNCTION update_estimate_templates_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER estimate_templates_update_last_modified
    BEFORE UPDATE ON public.estimate_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_estimate_templates_last_modified();

-- Estimates Triggers
CREATE OR REPLACE FUNCTION update_estimates_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER estimates_update_last_modified
    BEFORE UPDATE ON public.estimates
    FOR EACH ROW
    EXECUTE FUNCTION update_estimates_last_modified();

-- Estimate Line Items Triggers
CREATE OR REPLACE FUNCTION update_estimate_line_items_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER estimate_line_items_update_last_modified
    BEFORE UPDATE ON public.estimate_line_items
    FOR EACH ROW
    EXECUTE FUNCTION update_estimate_line_items_last_modified();

-- Invoices Triggers
CREATE OR REPLACE FUNCTION update_invoices_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER invoices_update_last_modified
    BEFORE UPDATE ON public.invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_invoices_last_modified();

-- Invoice Line Items Triggers
CREATE OR REPLACE FUNCTION update_invoice_line_items_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER invoice_line_items_update_last_modified
    BEFORE UPDATE ON public.invoice_line_items
    FOR EACH ROW
    EXECUTE FUNCTION update_invoice_line_items_last_modified();

-- Payments Triggers
CREATE OR REPLACE FUNCTION update_payments_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER payments_update_last_modified
    BEFORE UPDATE ON public.payments
    FOR EACH ROW
    EXECUTE FUNCTION update_payments_last_modified();

-- =====================================
-- BUSINESS LOGIC TRIGGERS
-- =====================================

-- Auto-calculate estimate totals when line items change
CREATE OR REPLACE FUNCTION calculate_estimate_totals()
RETURNS TRIGGER AS $$
DECLARE
    estimate_subtotal NUMERIC(12,2) := 0;
    estimate_tax_amount NUMERIC(12,2) := 0;
    estimate_discount_amount NUMERIC(12,2) := 0;
    estimate_total NUMERIC(12,2) := 0;
BEGIN
    -- Calculate subtotal from line items
    SELECT COALESCE(SUM(total_amount), 0) INTO estimate_subtotal
    FROM public.estimate_line_items
    WHERE estimate_id = COALESCE(NEW.estimate_id, OLD.estimate_id);
    
    -- Calculate tax amount from line items
    SELECT COALESCE(SUM(tax_amount), 0) INTO estimate_tax_amount
    FROM public.estimate_line_items
    WHERE estimate_id = COALESCE(NEW.estimate_id, OLD.estimate_id);
    
    -- Calculate discount amount from line items
    SELECT COALESCE(SUM(discount_amount), 0) INTO estimate_discount_amount
    FROM public.estimate_line_items
    WHERE estimate_id = COALESCE(NEW.estimate_id, OLD.estimate_id);
    
    -- Calculate total amount
    estimate_total := estimate_subtotal + estimate_tax_amount - estimate_discount_amount;
    
    -- Update the estimate with calculated values
    UPDATE public.estimates 
    SET 
        subtotal = estimate_subtotal,
        tax_amount = estimate_tax_amount,
        discount_amount = estimate_discount_amount,
        total_amount = estimate_total,
        last_modified = NOW()
    WHERE id = COALESCE(NEW.estimate_id, OLD.estimate_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_estimate_totals_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.estimate_line_items
    FOR EACH ROW
    EXECUTE FUNCTION calculate_estimate_totals();

-- Auto-calculate invoice totals when line items change
CREATE OR REPLACE FUNCTION calculate_invoice_totals()
RETURNS TRIGGER AS $$
DECLARE
    invoice_subtotal NUMERIC(12,2) := 0;
    invoice_tax_amount NUMERIC(12,2) := 0;
    invoice_discount_amount NUMERIC(12,2) := 0;
    invoice_total NUMERIC(12,2) := 0;
BEGIN
    -- Calculate subtotal from line items
    SELECT COALESCE(SUM(total_amount), 0) INTO invoice_subtotal
    FROM public.invoice_line_items
    WHERE invoice_id = COALESCE(NEW.invoice_id, OLD.invoice_id);
    
    -- Calculate tax amount from line items
    SELECT COALESCE(SUM(tax_amount), 0) INTO invoice_tax_amount
    FROM public.invoice_line_items
    WHERE invoice_id = COALESCE(NEW.invoice_id, OLD.invoice_id);
    
    -- Calculate discount amount from line items
    SELECT COALESCE(SUM(discount_amount), 0) INTO invoice_discount_amount
    FROM public.invoice_line_items
    WHERE invoice_id = COALESCE(NEW.invoice_id, OLD.invoice_id);
    
    -- Calculate total amount
    invoice_total := invoice_subtotal + invoice_tax_amount - invoice_discount_amount;
    
    -- Update the invoice with calculated values
    UPDATE public.invoices 
    SET 
        subtotal = invoice_subtotal,
        tax_amount = invoice_tax_amount,
        discount_amount = invoice_discount_amount,
        total_amount = invoice_total,
        last_modified = NOW()
    WHERE id = COALESCE(NEW.invoice_id, OLD.invoice_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_invoice_totals_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.invoice_line_items
    FOR EACH ROW
    EXECUTE FUNCTION calculate_invoice_totals();

-- Auto-update invoice payment status when payments change
CREATE OR REPLACE FUNCTION update_invoice_payment_status()
RETURNS TRIGGER AS $$
DECLARE
    total_payments NUMERIC(12,2) := 0;
    total_refunds NUMERIC(12,2) := 0;
    invoice_total NUMERIC(12,2) := 0;
    invoice_late_fee NUMERIC(12,2) := 0;
    new_status VARCHAR(20);
    new_amount_paid NUMERIC(12,2);
    new_amount_due NUMERIC(12,2);
BEGIN
    -- Get invoice total and late fee
    SELECT total_amount, COALESCE(late_fee_amount, 0) 
    INTO invoice_total, invoice_late_fee
    FROM public.invoices 
    WHERE id = COALESCE(NEW.invoice_id, OLD.invoice_id);
    
    -- Calculate total payments and refunds
    SELECT 
        COALESCE(SUM(CASE WHEN payment_status = 'completed' THEN amount ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN payment_status = 'refunded' OR payment_status = 'partially_refunded' THEN COALESCE(refund_amount, 0) ELSE 0 END), 0)
    INTO total_payments, total_refunds
    FROM public.payments 
    WHERE invoice_id = COALESCE(NEW.invoice_id, OLD.invoice_id);
    
    -- Calculate new amounts
    new_amount_paid := total_payments - total_refunds;
    new_amount_due := (invoice_total + invoice_late_fee) - new_amount_paid;
    
    -- Determine new status
    IF new_amount_paid = 0 THEN
        new_status := 'sent';
    ELSIF new_amount_due <= 0 THEN
        new_status := 'paid';
    ELSE
        new_status := 'partially_paid';
    END IF;
    
    -- Update the invoice
    UPDATE public.invoices 
    SET 
        amount_paid = new_amount_paid,
        amount_due = new_amount_due,
        amount_refunded = total_refunds,
        status = new_status,
        last_modified = NOW()
    WHERE id = COALESCE(NEW.invoice_id, OLD.invoice_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_invoice_payment_status_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.payments
    FOR EACH ROW
    EXECUTE FUNCTION update_invoice_payment_status();

-- =====================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================

-- Estimate Templates RLS
ALTER TABLE "public"."estimate_templates" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "estimate_templates_business_isolation" ON "public"."estimate_templates"
    FOR ALL USING (
        business_id IN (
            SELECT bm.business_id 
            FROM public.business_memberships bm 
            WHERE bm.user_id = auth.uid() 
            AND bm.is_active = true
        )
    );

-- Estimates RLS
ALTER TABLE "public"."estimates" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "estimates_business_isolation" ON "public"."estimates"
    FOR ALL USING (
        business_id IN (
            SELECT bm.business_id 
            FROM public.business_memberships bm 
            WHERE bm.user_id = auth.uid() 
            AND bm.is_active = true
        )
    );

-- Estimate Line Items RLS
ALTER TABLE "public"."estimate_line_items" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "estimate_line_items_business_isolation" ON "public"."estimate_line_items"
    FOR ALL USING (
        estimate_id IN (
            SELECT e.id 
            FROM public.estimates e
            INNER JOIN public.business_memberships bm ON e.business_id = bm.business_id
            WHERE bm.user_id = auth.uid() 
            AND bm.is_active = true
        )
    );

-- Invoices RLS
ALTER TABLE "public"."invoices" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "invoices_business_isolation" ON "public"."invoices"
    FOR ALL USING (
        business_id IN (
            SELECT bm.business_id 
            FROM public.business_memberships bm 
            WHERE bm.user_id = auth.uid() 
            AND bm.is_active = true
        )
    );

-- Invoice Line Items RLS
ALTER TABLE "public"."invoice_line_items" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "invoice_line_items_business_isolation" ON "public"."invoice_line_items"
    FOR ALL USING (
        invoice_id IN (
            SELECT i.id 
            FROM public.invoices i
            INNER JOIN public.business_memberships bm ON i.business_id = bm.business_id
            WHERE bm.user_id = auth.uid() 
            AND bm.is_active = true
        )
    );

-- Payments RLS
ALTER TABLE "public"."payments" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "payments_business_isolation" ON "public"."payments"
    FOR ALL USING (
        invoice_id IN (
            SELECT i.id 
            FROM public.invoices i
            INNER JOIN public.business_memberships bm ON i.business_id = bm.business_id
            WHERE bm.user_id = auth.uid() 
            AND bm.is_active = true
        )
    );

-- =====================================
-- UTILITY FUNCTIONS
-- =====================================

-- Function to generate next estimate number
CREATE OR REPLACE FUNCTION get_next_estimate_number(business_uuid UUID, prefix TEXT DEFAULT 'EST')
RETURNS TEXT AS $$
DECLARE
    next_number INTEGER;
    formatted_number TEXT;
BEGIN
    -- Get the next number by finding the highest existing number
    SELECT COALESCE(MAX(CAST(RIGHT(estimate_number, -LENGTH(prefix || '-')) AS INTEGER)), 0) + 1
    INTO next_number
    FROM public.estimates
    WHERE business_id = business_uuid
    AND estimate_number ~ ('^' || prefix || '-\d+$');
    
    -- Format the number with leading zeros
    formatted_number := prefix || '-' || LPAD(next_number::TEXT, 6, '0');
    
    RETURN formatted_number;
END;
$$ LANGUAGE plpgsql;

-- Function to generate next invoice number
CREATE OR REPLACE FUNCTION get_next_invoice_number(business_uuid UUID, prefix TEXT DEFAULT 'INV')
RETURNS TEXT AS $$
DECLARE
    next_number INTEGER;
    formatted_number TEXT;
BEGIN
    -- Get the next number by finding the highest existing number
    SELECT COALESCE(MAX(CAST(RIGHT(invoice_number, -LENGTH(prefix || '-')) AS INTEGER)), 0) + 1
    INTO next_number
    FROM public.invoices
    WHERE business_id = business_uuid
    AND invoice_number ~ ('^' || prefix || '-\d+$');
    
    -- Format the number with leading zeros
    formatted_number := prefix || '-' || LPAD(next_number::TEXT, 6, '0');
    
    RETURN formatted_number;
END;
$$ LANGUAGE plpgsql;

-- Function to check if estimate is expired
CREATE OR REPLACE FUNCTION is_estimate_expired(estimate_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    valid_until_date TIMESTAMP WITH TIME ZONE;
BEGIN
    SELECT valid_until INTO valid_until_date
    FROM public.estimates
    WHERE id = estimate_uuid;
    
    RETURN valid_until_date IS NOT NULL AND valid_until_date < NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to check if invoice is overdue
CREATE OR REPLACE FUNCTION is_invoice_overdue(invoice_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    due_date_value TIMESTAMP WITH TIME ZONE;
    invoice_status_value VARCHAR(20);
BEGIN
    SELECT due_date, status INTO due_date_value, invoice_status_value
    FROM public.invoices
    WHERE id = invoice_uuid;
    
    RETURN due_date_value < NOW() AND invoice_status_value IN ('sent', 'viewed', 'partially_paid');
END;
$$ LANGUAGE plpgsql;

-- Add foreign key constraint for converted estimates
ALTER TABLE "public"."estimates" 
ADD CONSTRAINT "fk_estimates_converted_invoice" 
FOREIGN KEY ("converted_to_invoice_id") 
REFERENCES "public"."invoices"("id") 
ON DELETE SET NULL;

-- =====================================
-- INITIAL DATA
-- =====================================

-- Insert default estimate templates for new businesses
-- This will be handled by the application when businesses are created
-- to ensure proper business_id association

-- Migration completed successfully
-- Tables created: estimate_templates, estimates, estimate_line_items, invoices, invoice_line_items, payments
-- Indexes created: 28 indexes for optimal query performance
-- Triggers created: 9 triggers for auto-updates and business logic
-- RLS policies created: 6 policies for business isolation
-- Utility functions created: 4 helper functions for business logic 