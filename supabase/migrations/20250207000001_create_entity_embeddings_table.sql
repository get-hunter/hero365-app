-- Create Entity Embeddings Table for Hybrid Search
-- This migration creates the centralized entity embeddings table for semantic search

-- Create enum type for entity types
CREATE TYPE entity_type AS ENUM (
    'contact',
    'job', 
    'estimate',
    'invoice',
    'product',
    'project'
);

-- Create the main entity embeddings table
CREATE TABLE entity_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type entity_type NOT NULL,
    entity_id UUID NOT NULL,
    business_id UUID NOT NULL,
    embedding vector(1536) NOT NULL, -- OpenAI text-embedding-3-small dimensions
    content_hash TEXT NOT NULL, -- SHA256 hash of the content for change detection
    content_preview TEXT, -- First 200 chars of content for debugging/monitoring
    embedding_model TEXT NOT NULL DEFAULT 'text-embedding-3-small',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    
    -- Ensure uniqueness per entity within a business
    UNIQUE(business_id, entity_type, entity_id)
);

-- Create indexes for optimal performance
-- Primary lookup index: business + entity type + similarity search
CREATE INDEX idx_entity_embeddings_business_type_embedding 
ON entity_embeddings USING ivfflat (business_id, entity_type, embedding vector_cosine_ops);

-- Specific entity lookup index
CREATE INDEX idx_entity_embeddings_entity_lookup 
ON entity_embeddings (business_id, entity_type, entity_id);

-- Similarity search index for cross-entity searches
CREATE INDEX idx_entity_embeddings_similarity_search 
ON entity_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Updated timestamp index for sync operations
CREATE INDEX idx_entity_embeddings_updated_at 
ON entity_embeddings (updated_at);

-- Content hash index for change detection
CREATE INDEX idx_entity_embeddings_content_hash 
ON entity_embeddings (content_hash);

-- Add foreign key constraints to ensure referential integrity
-- Note: We'll add these constraints after verifying the referenced tables exist

-- Add trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_entity_embeddings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_entity_embeddings_updated_at
    BEFORE UPDATE ON entity_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_entity_embeddings_updated_at();

-- Add RLS (Row Level Security) for multi-tenant data isolation
ALTER TABLE entity_embeddings ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for business isolation
CREATE POLICY entity_embeddings_business_isolation ON entity_embeddings
    FOR ALL
    USING (business_id = current_setting('app.current_business_id')::UUID);

-- Create function to validate entity exists and belongs to business
CREATE OR REPLACE FUNCTION validate_entity_embedding(
    p_business_id UUID,
    p_entity_type entity_type,
    p_entity_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    entity_exists BOOLEAN := FALSE;
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
    
    -- Check if entity exists and belongs to the business
    EXECUTE format('SELECT EXISTS(SELECT 1 FROM %I WHERE id = $1 AND business_id = $2)', table_name)
    INTO entity_exists
    USING p_entity_id, p_business_id;
    
    RETURN entity_exists;
END;
$$ LANGUAGE plpgsql;

-- Create trigger function to validate entity before insert/update
CREATE OR REPLACE FUNCTION validate_entity_embedding_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT validate_entity_embedding(NEW.business_id, NEW.entity_type, NEW.entity_id) THEN
        RAISE EXCEPTION 'Entity % with ID % does not exist or does not belong to business %', 
            NEW.entity_type, NEW.entity_id, NEW.business_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to validate entity before insert/update
CREATE TRIGGER trigger_validate_entity_embedding
    BEFORE INSERT OR UPDATE ON entity_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION validate_entity_embedding_trigger();

-- Create function to get embedding statistics
CREATE OR REPLACE FUNCTION get_embedding_stats(p_business_id UUID DEFAULT NULL)
RETURNS TABLE (
    entity_type entity_type,
    total_embeddings BIGINT,
    avg_content_length NUMERIC,
    last_updated TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.entity_type,
        COUNT(*) as total_embeddings,
        AVG(LENGTH(e.content_preview)) as avg_content_length,
        MAX(e.updated_at) as last_updated
    FROM entity_embeddings e
    WHERE (p_business_id IS NULL OR e.business_id = p_business_id)
    GROUP BY e.entity_type
    ORDER BY e.entity_type;
END;
$$ LANGUAGE plpgsql;

-- Create function to clean up orphaned embeddings
CREATE OR REPLACE FUNCTION cleanup_orphaned_embeddings(p_business_id UUID DEFAULT NULL)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    entity_type_rec RECORD;
BEGIN
    FOR entity_type_rec IN 
        SELECT DISTINCT entity_type FROM entity_embeddings 
        WHERE (p_business_id IS NULL OR business_id = p_business_id)
    LOOP
        -- Delete embeddings for entities that no longer exist
        EXECUTE format('
            DELETE FROM entity_embeddings e
            WHERE e.entity_type = %L
            AND ((%L IS NULL) OR e.business_id = %L)
            AND NOT EXISTS (
                SELECT 1 FROM %I t 
                WHERE t.id = e.entity_id 
                AND t.business_id = e.business_id
            )', 
            entity_type_rec.entity_type, 
            p_business_id, 
            p_business_id,
            CASE entity_type_rec.entity_type
                WHEN 'contact' THEN 'contacts'
                WHEN 'job' THEN 'jobs'
                WHEN 'estimate' THEN 'estimates'
                WHEN 'invoice' THEN 'invoices'
                WHEN 'product' THEN 'products'
                WHEN 'project' THEN 'projects'
            END
        );
        
        GET DIAGNOSTICS deleted_count = deleted_count + ROW_COUNT;
    END LOOP;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Add comments for documentation
COMMENT ON TABLE entity_embeddings IS 'Stores vector embeddings for semantic search across all entity types';
COMMENT ON COLUMN entity_embeddings.entity_type IS 'Type of entity (contact, job, estimate, invoice, product, project)';
COMMENT ON COLUMN entity_embeddings.entity_id IS 'ID of the referenced entity';
COMMENT ON COLUMN entity_embeddings.business_id IS 'Business ID for multi-tenant isolation';
COMMENT ON COLUMN entity_embeddings.embedding IS 'Vector embedding for semantic similarity search';
COMMENT ON COLUMN entity_embeddings.content_hash IS 'SHA256 hash of content for change detection';
COMMENT ON COLUMN entity_embeddings.content_preview IS 'First 200 characters of content for debugging';
COMMENT ON COLUMN entity_embeddings.embedding_model IS 'Model used to generate the embedding';

-- Validate the table creation
DO $$
BEGIN
    -- Check if table exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'entity_embeddings') THEN
        RAISE EXCEPTION 'entity_embeddings table was not created successfully';
    END IF;
    
    -- Check if enum type exists
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'entity_type') THEN
        RAISE EXCEPTION 'entity_type enum was not created successfully';
    END IF;
    
    -- Check if indexes exist
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'entity_embeddings' AND indexname = 'idx_entity_embeddings_business_type_embedding') THEN
        RAISE EXCEPTION 'Primary embedding index was not created successfully';
    END IF;
    
    RAISE NOTICE 'Entity embeddings table created successfully with % indexes', 
        (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'entity_embeddings');
    RAISE NOTICE 'Table includes RLS policies, validation triggers, and utility functions';
END $$; 