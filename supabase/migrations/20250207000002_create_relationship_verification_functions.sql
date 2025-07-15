-- Create Relationship Verification Functions for Hybrid Search
-- This migration creates functions to verify business relationships between entities
-- Based on the actual database schema relationships

-- =====================================
-- UTILITY FUNCTIONS
-- =====================================

-- Function to get entity details by ID and type
CREATE OR REPLACE FUNCTION get_entity_details(
    p_entity_type entity_type,
    p_entity_id UUID,
    p_business_id UUID
) RETURNS JSONB AS $$
DECLARE
    entity_details JSONB;
    table_name TEXT;
BEGIN
    -- Determine table name based on entity type
    CASE p_entity_type
        WHEN 'contact' THEN table_name := 'contacts';
        WHEN 'job' THEN table_name := 'jobs';
        WHEN 'estimate' THEN table_name := 'estimates';
        WHEN 'invoice' THEN table_name := 'invoices';
        WHEN 'product' THEN table_name := 'products';
        WHEN 'project' THEN table_name := 'projects';
        ELSE
            RAISE EXCEPTION 'Invalid entity type: %', p_entity_type;
    END CASE;
    
    -- Get entity details
    EXECUTE format('SELECT row_to_json(t) FROM %I t WHERE t.id = $1 AND t.business_id = $2', table_name)
    INTO entity_details
    USING p_entity_id, p_business_id;
    
    RETURN entity_details;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- CONTACT RELATIONSHIP VERIFICATION
-- =====================================

-- Function to verify relationships for a contact
CREATE OR REPLACE FUNCTION verify_contact_relationships(
    p_contact_id UUID,
    p_business_id UUID,
    p_related_entity_ids UUID[]
) RETURNS TABLE (
    entity_id UUID,
    entity_type entity_type,
    relationship_type TEXT,
    relationship_strength INTEGER,
    relationship_details JSONB
) AS $$
DECLARE
    related_id UUID;
BEGIN
    -- Verify contact exists
    IF NOT EXISTS (SELECT 1 FROM contacts WHERE id = p_contact_id AND business_id = p_business_id) THEN
        RETURN;
    END IF;
    
    -- Check each related entity
    FOREACH related_id IN ARRAY p_related_entity_ids
    LOOP
        -- Check if related entity is a job linked to this contact
        IF EXISTS (
            SELECT 1 FROM jobs j 
            WHERE j.id = related_id 
            AND j.business_id = p_business_id 
            AND j.contact_id = p_contact_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'job'::entity_type,
                'direct_contact'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'job_assigned_to_contact',
                    'foreign_key', 'jobs.contact_id'
                );
        END IF;
        
        -- Check if related entity is an estimate linked to this contact
        IF EXISTS (
            SELECT 1 FROM estimates e 
            WHERE e.id = related_id 
            AND e.business_id = p_business_id 
            AND e.contact_id = p_contact_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'estimate'::entity_type,
                'direct_contact'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'estimate_for_contact',
                    'foreign_key', 'estimates.contact_id'
                );
        END IF;
        
        -- Check if related entity is an invoice linked to this contact
        IF EXISTS (
            SELECT 1 FROM invoices i 
            WHERE i.id = related_id 
            AND i.business_id = p_business_id 
            AND i.contact_id = p_contact_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'invoice'::entity_type,
                'direct_contact'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'invoice_for_contact',
                    'foreign_key', 'invoices.contact_id'
                );
        END IF;
        
        -- Check if related entity is a project linked to this contact
        IF EXISTS (
            SELECT 1 FROM projects p 
            WHERE p.id = related_id 
            AND p.business_id = p_business_id 
            AND p.client_id = p_contact_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'project'::entity_type,
                'direct_contact'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'project_client',
                    'foreign_key', 'projects.client_id'
                );
        END IF;
        
        -- Check if related entity is a product (business context relationship)
        IF EXISTS (
            SELECT 1 FROM products p 
            WHERE p.id = related_id 
            AND p.business_id = p_business_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'product'::entity_type,
                'business_context'::TEXT,
                3::INTEGER,
                jsonb_build_object(
                    'relationship', 'same_business_context',
                    'reason', 'product_available_to_contact'
                );
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- JOB RELATIONSHIP VERIFICATION
-- =====================================

-- Function to verify relationships for a job
CREATE OR REPLACE FUNCTION verify_job_relationships(
    p_job_id UUID,
    p_business_id UUID,
    p_related_entity_ids UUID[]
) RETURNS TABLE (
    entity_id UUID,
    entity_type entity_type,
    relationship_type TEXT,
    relationship_strength INTEGER,
    relationship_details JSONB
) AS $$
DECLARE
    related_id UUID;
    job_contact_id UUID;
    job_project_id UUID;
BEGIN
    -- Verify job exists and get its contact and project
    SELECT j.contact_id, j.project_id INTO job_contact_id, job_project_id
    FROM jobs j 
    WHERE j.id = p_job_id AND j.business_id = p_business_id;
    
    IF NOT FOUND THEN
        RETURN;
    END IF;
    
    -- Check each related entity
    FOREACH related_id IN ARRAY p_related_entity_ids
    LOOP
        -- Check if related entity is the contact for this job
        IF job_contact_id IS NOT NULL AND related_id = job_contact_id THEN
            RETURN QUERY SELECT 
                related_id,
                'contact'::entity_type,
                'direct_contact'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'job_contact',
                    'foreign_key', 'jobs.contact_id'
                );
        END IF;
        
        -- Check if related entity is the project for this job
        IF job_project_id IS NOT NULL AND related_id = job_project_id THEN
            RETURN QUERY SELECT 
                related_id,
                'project'::entity_type,
                'direct_project'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'job_project',
                    'foreign_key', 'jobs.project_id'
                );
        END IF;
        
        -- Check if related entity is an estimate linked to this job
        IF EXISTS (
            SELECT 1 FROM estimates e 
            WHERE e.id = related_id 
            AND e.business_id = p_business_id 
            AND e.job_id = p_job_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'estimate'::entity_type,
                'direct_job'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'estimate_for_job',
                    'foreign_key', 'estimates.job_id'
                );
        END IF;
        
        -- Check if related entity is an invoice linked to this job
        IF EXISTS (
            SELECT 1 FROM invoices i 
            WHERE i.id = related_id 
            AND i.business_id = p_business_id 
            AND i.job_id = p_job_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'invoice'::entity_type,
                'direct_job'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'invoice_for_job',
                    'foreign_key', 'invoices.job_id'
                );
        END IF;
        
        -- Check if related entity is a product (business context)
        IF EXISTS (
            SELECT 1 FROM products p 
            WHERE p.id = related_id 
            AND p.business_id = p_business_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'product'::entity_type,
                'business_context'::TEXT,
                3::INTEGER,
                jsonb_build_object(
                    'relationship', 'same_business_context',
                    'reason', 'product_available_for_job'
                );
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- ESTIMATE RELATIONSHIP VERIFICATION
-- =====================================

-- Function to verify relationships for an estimate
CREATE OR REPLACE FUNCTION verify_estimate_relationships(
    p_estimate_id UUID,
    p_business_id UUID,
    p_related_entity_ids UUID[]
) RETURNS TABLE (
    entity_id UUID,
    entity_type entity_type,
    relationship_type TEXT,
    relationship_strength INTEGER,
    relationship_details JSONB
) AS $$
DECLARE
    related_id UUID;
    estimate_contact_id UUID;
    estimate_job_id UUID;
    estimate_project_id UUID;
BEGIN
    -- Verify estimate exists and get its relationships
    SELECT e.contact_id, e.job_id, e.project_id 
    INTO estimate_contact_id, estimate_job_id, estimate_project_id
    FROM estimates e 
    WHERE e.id = p_estimate_id AND e.business_id = p_business_id;
    
    IF NOT FOUND THEN
        RETURN;
    END IF;
    
    -- Check each related entity
    FOREACH related_id IN ARRAY p_related_entity_ids
    LOOP
        -- Check if related entity is the contact for this estimate
        IF estimate_contact_id IS NOT NULL AND related_id = estimate_contact_id THEN
            RETURN QUERY SELECT 
                related_id,
                'contact'::entity_type,
                'direct_contact'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'estimate_contact',
                    'foreign_key', 'estimates.contact_id'
                );
        END IF;
        
        -- Check if related entity is the job for this estimate
        IF estimate_job_id IS NOT NULL AND related_id = estimate_job_id THEN
            RETURN QUERY SELECT 
                related_id,
                'job'::entity_type,
                'direct_job'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'estimate_job',
                    'foreign_key', 'estimates.job_id'
                );
        END IF;
        
        -- Check if related entity is the project for this estimate
        IF estimate_project_id IS NOT NULL AND related_id = estimate_project_id THEN
            RETURN QUERY SELECT 
                related_id,
                'project'::entity_type,
                'direct_project'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'estimate_project',
                    'foreign_key', 'estimates.project_id'
                );
        END IF;
        
        -- Check if related entity is an invoice converted from this estimate
        IF EXISTS (
            SELECT 1 FROM invoices i 
            WHERE i.id = related_id 
            AND i.business_id = p_business_id 
            AND i.estimate_id = p_estimate_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'invoice'::entity_type,
                'direct_conversion'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'invoice_from_estimate',
                    'foreign_key', 'invoices.estimate_id'
                );
        END IF;
        
        -- Check if related entity is a product (business context)
        IF EXISTS (
            SELECT 1 FROM products p 
            WHERE p.id = related_id 
            AND p.business_id = p_business_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'product'::entity_type,
                'business_context'::TEXT,
                3::INTEGER,
                jsonb_build_object(
                    'relationship', 'same_business_context',
                    'reason', 'product_available_for_estimate'
                );
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- INVOICE RELATIONSHIP VERIFICATION
-- =====================================

-- Function to verify relationships for an invoice
CREATE OR REPLACE FUNCTION verify_invoice_relationships(
    p_invoice_id UUID,
    p_business_id UUID,
    p_related_entity_ids UUID[]
) RETURNS TABLE (
    entity_id UUID,
    entity_type entity_type,
    relationship_type TEXT,
    relationship_strength INTEGER,
    relationship_details JSONB
) AS $$
DECLARE
    related_id UUID;
    invoice_contact_id UUID;
    invoice_job_id UUID;
    invoice_project_id UUID;
    invoice_estimate_id UUID;
BEGIN
    -- Verify invoice exists and get its relationships
    SELECT i.contact_id, i.job_id, i.project_id, i.estimate_id
    INTO invoice_contact_id, invoice_job_id, invoice_project_id, invoice_estimate_id
    FROM invoices i 
    WHERE i.id = p_invoice_id AND i.business_id = p_business_id;
    
    IF NOT FOUND THEN
        RETURN;
    END IF;
    
    -- Check each related entity
    FOREACH related_id IN ARRAY p_related_entity_ids
    LOOP
        -- Check if related entity is the contact for this invoice
        IF invoice_contact_id IS NOT NULL AND related_id = invoice_contact_id THEN
            RETURN QUERY SELECT 
                related_id,
                'contact'::entity_type,
                'direct_contact'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'invoice_contact',
                    'foreign_key', 'invoices.contact_id'
                );
        END IF;
        
        -- Check if related entity is the job for this invoice
        IF invoice_job_id IS NOT NULL AND related_id = invoice_job_id THEN
            RETURN QUERY SELECT 
                related_id,
                'job'::entity_type,
                'direct_job'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'invoice_job',
                    'foreign_key', 'invoices.job_id'
                );
        END IF;
        
        -- Check if related entity is the project for this invoice
        IF invoice_project_id IS NOT NULL AND related_id = invoice_project_id THEN
            RETURN QUERY SELECT 
                related_id,
                'project'::entity_type,
                'direct_project'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'invoice_project',
                    'foreign_key', 'invoices.project_id'
                );
        END IF;
        
        -- Check if related entity is the estimate for this invoice
        IF invoice_estimate_id IS NOT NULL AND related_id = invoice_estimate_id THEN
            RETURN QUERY SELECT 
                related_id,
                'estimate'::entity_type,
                'direct_estimate'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'invoice_estimate',
                    'foreign_key', 'invoices.estimate_id'
                );
        END IF;
        
        -- Check if related entity is a product (business context)
        IF EXISTS (
            SELECT 1 FROM products p 
            WHERE p.id = related_id 
            AND p.business_id = p_business_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'product'::entity_type,
                'business_context'::TEXT,
                3::INTEGER,
                jsonb_build_object(
                    'relationship', 'same_business_context',
                    'reason', 'product_available_for_invoice'
                );
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- PROJECT RELATIONSHIP VERIFICATION
-- =====================================

-- Function to verify relationships for a project
CREATE OR REPLACE FUNCTION verify_project_relationships(
    p_project_id UUID,
    p_business_id UUID,
    p_related_entity_ids UUID[]
) RETURNS TABLE (
    entity_id UUID,
    entity_type entity_type,
    relationship_type TEXT,
    relationship_strength INTEGER,
    relationship_details JSONB
) AS $$
DECLARE
    related_id UUID;
    project_client_id UUID;
BEGIN
    -- Verify project exists and get its client
    SELECT p.client_id INTO project_client_id
    FROM projects p 
    WHERE p.id = p_project_id AND p.business_id = p_business_id;
    
    IF NOT FOUND THEN
        RETURN;
    END IF;
    
    -- Check each related entity
    FOREACH related_id IN ARRAY p_related_entity_ids
    LOOP
        -- Check if related entity is the client for this project
        IF project_client_id IS NOT NULL AND related_id = project_client_id THEN
            RETURN QUERY SELECT 
                related_id,
                'contact'::entity_type,
                'direct_contact'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'project_client',
                    'foreign_key', 'projects.client_id'
                );
        END IF;
        
        -- Check if related entity is a job linked to this project
        IF EXISTS (
            SELECT 1 FROM jobs j 
            WHERE j.id = related_id 
            AND j.business_id = p_business_id 
            AND j.project_id = p_project_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'job'::entity_type,
                'direct_project'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'job_project',
                    'foreign_key', 'jobs.project_id'
                );
        END IF;
        
        -- Check if related entity is an estimate linked to this project
        IF EXISTS (
            SELECT 1 FROM estimates e 
            WHERE e.id = related_id 
            AND e.business_id = p_business_id 
            AND e.project_id = p_project_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'estimate'::entity_type,
                'direct_project'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'estimate_project',
                    'foreign_key', 'estimates.project_id'
                );
        END IF;
        
        -- Check if related entity is an invoice linked to this project
        IF EXISTS (
            SELECT 1 FROM invoices i 
            WHERE i.id = related_id 
            AND i.business_id = p_business_id 
            AND i.project_id = p_project_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'invoice'::entity_type,
                'direct_project'::TEXT,
                10::INTEGER,
                jsonb_build_object(
                    'relationship', 'invoice_project',
                    'foreign_key', 'invoices.project_id'
                );
        END IF;
        
        -- Check if related entity is a product (business context)
        IF EXISTS (
            SELECT 1 FROM products p 
            WHERE p.id = related_id 
            AND p.business_id = p_business_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'product'::entity_type,
                'business_context'::TEXT,
                3::INTEGER,
                jsonb_build_object(
                    'relationship', 'same_business_context',
                    'reason', 'product_available_for_project'
                );
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- PRODUCT RELATIONSHIP VERIFICATION
-- =====================================

-- Function to verify relationships for a product
CREATE OR REPLACE FUNCTION verify_product_relationships(
    p_product_id UUID,
    p_business_id UUID,
    p_related_entity_ids UUID[]
) RETURNS TABLE (
    entity_id UUID,
    entity_type entity_type,
    relationship_type TEXT,
    relationship_strength INTEGER,
    relationship_details JSONB
) AS $$
DECLARE
    related_id UUID;
BEGIN
    -- Verify product exists
    IF NOT EXISTS (SELECT 1 FROM products WHERE id = p_product_id AND business_id = p_business_id) THEN
        RETURN;
    END IF;
    
    -- Check each related entity (products relate through business context)
    FOREACH related_id IN ARRAY p_related_entity_ids
    LOOP
        -- Check if related entity is a contact (business context)
        IF EXISTS (
            SELECT 1 FROM contacts c 
            WHERE c.id = related_id 
            AND c.business_id = p_business_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'contact'::entity_type,
                'business_context'::TEXT,
                3::INTEGER,
                jsonb_build_object(
                    'relationship', 'same_business_context',
                    'reason', 'product_available_to_contact'
                );
        END IF;
        
        -- Check if related entity is a job (business context)
        IF EXISTS (
            SELECT 1 FROM jobs j 
            WHERE j.id = related_id 
            AND j.business_id = p_business_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'job'::entity_type,
                'business_context'::TEXT,
                3::INTEGER,
                jsonb_build_object(
                    'relationship', 'same_business_context',
                    'reason', 'product_available_for_job'
                );
        END IF;
        
        -- Check if related entity is an estimate (business context)
        IF EXISTS (
            SELECT 1 FROM estimates e 
            WHERE e.id = related_id 
            AND e.business_id = p_business_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'estimate'::entity_type,
                'business_context'::TEXT,
                3::INTEGER,
                jsonb_build_object(
                    'relationship', 'same_business_context',
                    'reason', 'product_available_for_estimate'
                );
        END IF;
        
        -- Check if related entity is an invoice (business context)
        IF EXISTS (
            SELECT 1 FROM invoices i 
            WHERE i.id = related_id 
            AND i.business_id = p_business_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'invoice'::entity_type,
                'business_context'::TEXT,
                3::INTEGER,
                jsonb_build_object(
                    'relationship', 'same_business_context',
                    'reason', 'product_available_for_invoice'
                );
        END IF;
        
        -- Check if related entity is a project (business context)
        IF EXISTS (
            SELECT 1 FROM projects p 
            WHERE p.id = related_id 
            AND p.business_id = p_business_id
        ) THEN
            RETURN QUERY SELECT 
                related_id,
                'project'::entity_type,
                'business_context'::TEXT,
                3::INTEGER,
                jsonb_build_object(
                    'relationship', 'same_business_context',
                    'reason', 'product_available_for_project'
                );
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- UNIFIED RELATIONSHIP VERIFICATION
-- =====================================

-- Main function to verify relationships for any entity type
CREATE OR REPLACE FUNCTION verify_entity_relationships(
    p_entity_type entity_type,
    p_entity_id UUID,
    p_business_id UUID,
    p_related_entity_ids UUID[]
) RETURNS TABLE (
    entity_id UUID,
    entity_type entity_type,
    relationship_type TEXT,
    relationship_strength INTEGER,
    relationship_details JSONB
) AS $$
BEGIN
    CASE p_entity_type
        WHEN 'contact' THEN
            RETURN QUERY SELECT * FROM verify_contact_relationships(p_entity_id, p_business_id, p_related_entity_ids);
        WHEN 'job' THEN
            RETURN QUERY SELECT * FROM verify_job_relationships(p_entity_id, p_business_id, p_related_entity_ids);
        WHEN 'estimate' THEN
            RETURN QUERY SELECT * FROM verify_estimate_relationships(p_entity_id, p_business_id, p_related_entity_ids);
        WHEN 'invoice' THEN
            RETURN QUERY SELECT * FROM verify_invoice_relationships(p_entity_id, p_business_id, p_related_entity_ids);
        WHEN 'project' THEN
            RETURN QUERY SELECT * FROM verify_project_relationships(p_entity_id, p_business_id, p_related_entity_ids);
        WHEN 'product' THEN
            RETURN QUERY SELECT * FROM verify_product_relationships(p_entity_id, p_business_id, p_related_entity_ids);
        ELSE
            RAISE EXCEPTION 'Invalid entity type: %', p_entity_type;
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- COMMENTS AND DOCUMENTATION
-- =====================================

COMMENT ON FUNCTION verify_entity_relationships IS 'Verifies business relationships between entities for hybrid search filtering';
COMMENT ON FUNCTION verify_contact_relationships IS 'Verifies relationships from a contact to other entities';
COMMENT ON FUNCTION verify_job_relationships IS 'Verifies relationships from a job to other entities';
COMMENT ON FUNCTION verify_estimate_relationships IS 'Verifies relationships from an estimate to other entities';
COMMENT ON FUNCTION verify_invoice_relationships IS 'Verifies relationships from an invoice to other entities';
COMMENT ON FUNCTION verify_project_relationships IS 'Verifies relationships from a project to other entities';
COMMENT ON FUNCTION verify_product_relationships IS 'Verifies relationships from a product to other entities';

-- =====================================
-- VALIDATION
-- =====================================

-- Test the relationship verification functions
DO $$
BEGIN
    -- Test that all functions exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.routines WHERE routine_name = 'verify_entity_relationships') THEN
        RAISE EXCEPTION 'verify_entity_relationships function was not created';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.routines WHERE routine_name = 'verify_contact_relationships') THEN
        RAISE EXCEPTION 'verify_contact_relationships function was not created';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.routines WHERE routine_name = 'verify_job_relationships') THEN
        RAISE EXCEPTION 'verify_job_relationships function was not created';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.routines WHERE routine_name = 'verify_estimate_relationships') THEN
        RAISE EXCEPTION 'verify_estimate_relationships function was not created';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.routines WHERE routine_name = 'verify_invoice_relationships') THEN
        RAISE EXCEPTION 'verify_invoice_relationships function was not created';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.routines WHERE routine_name = 'verify_project_relationships') THEN
        RAISE EXCEPTION 'verify_project_relationships function was not created';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.routines WHERE routine_name = 'verify_product_relationships') THEN
        RAISE EXCEPTION 'verify_product_relationships function was not created';
    END IF;
    
    RAISE NOTICE 'All relationship verification functions created successfully';
    RAISE NOTICE 'Functions support relationship strength scoring: 10=direct, 3=business_context';
    RAISE NOTICE 'Functions include detailed relationship metadata for debugging';
END $$; 