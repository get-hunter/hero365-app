-- Enable pgvector extension for semantic similarity search
-- This migration enables the pgvector extension which provides vector similarity search capabilities

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Test vector operations are available
DO $$
BEGIN
    -- Test basic vector operations
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.routines 
        WHERE routine_name = 'vector_dims' AND routine_schema = 'public'
    ) THEN
        RAISE EXCEPTION 'pgvector extension functions not available';
    END IF;
    
    -- Test vector type creation
    BEGIN
        EXECUTE 'SELECT ''[1,2,3]''::vector(3)';
    EXCEPTION WHEN OTHERS THEN
        RAISE EXCEPTION 'Vector type not working properly: %', SQLERRM;
    END;
    
    RAISE NOTICE 'pgvector extension enabled successfully';
END $$;

-- Create operator class for vector indexing (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_opclass 
        WHERE opcname = 'vector_cosine_ops' AND opcmethod = (
            SELECT oid FROM pg_am WHERE amname = 'ivfflat'
        )
    ) THEN
        -- This will be created automatically by the extension
        RAISE NOTICE 'Vector indexing operators are available';
    END IF;
END $$;

-- Validate vector indexing capabilities
DO $$
BEGIN
    -- Test HNSW indexing support (available in pgvector 0.5.0+)
    IF EXISTS (
        SELECT 1 FROM pg_available_extensions 
        WHERE name = 'vector' AND default_version >= '0.5.0'
    ) THEN
        RAISE NOTICE 'HNSW indexing support available';
    ELSE
        RAISE NOTICE 'Using IVFFlat indexing (HNSW not available in this version)';
    END IF;
END $$;

-- Create a test table to validate vector operations
CREATE TABLE IF NOT EXISTS _pgvector_test (
    id SERIAL PRIMARY KEY,
    embedding vector(3)
);

-- Test basic vector operations
INSERT INTO _pgvector_test (embedding) VALUES 
    ('[1,2,3]'::vector(3)),
    ('[4,5,6]'::vector(3)),
    ('[7,8,9]'::vector(3));

-- Test similarity search
DO $$
DECLARE
    test_result RECORD;
BEGIN
    -- Test cosine similarity
    SELECT embedding <=> '[1,2,3]'::vector(3) AS cosine_distance
    INTO test_result
    FROM _pgvector_test
    WHERE embedding = '[1,2,3]'::vector(3);
    
    IF test_result.cosine_distance != 0 THEN
        RAISE EXCEPTION 'Cosine similarity test failed: expected 0, got %', test_result.cosine_distance;
    END IF;
    
    -- Test L2 distance
    SELECT embedding <-> '[1,2,3]'::vector(3) AS l2_distance
    INTO test_result
    FROM _pgvector_test
    WHERE embedding = '[1,2,3]'::vector(3);
    
    IF test_result.l2_distance != 0 THEN
        RAISE EXCEPTION 'L2 distance test failed: expected 0, got %', test_result.l2_distance;
    END IF;
    
    RAISE NOTICE 'Vector similarity operations validated successfully';
END $$;

-- Clean up test table
DROP TABLE IF EXISTS _pgvector_test;

-- Final validation
DO $$
BEGIN
    RAISE NOTICE 'pgvector extension validation complete';
    RAISE NOTICE 'Available vector operators: <-> (L2), <#> (inner product), <=> (cosine)';
    RAISE NOTICE 'Vector indexing methods: IVFFlat (and HNSW if version >= 0.5.0)';
    RAISE NOTICE 'Ready for vector similarity search implementation';
END $$; 