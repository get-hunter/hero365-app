-- Migration: Add service_page_contents table for LLM-generated SEO content
-- This stores structured content blocks and JSON-LD schema for service pages

-- Create enum for content source
CREATE TYPE content_source_enum AS ENUM ('template', 'llm', 'mixed', 'manual');

-- Create enum for page status
CREATE TYPE page_status_enum AS ENUM ('draft', 'published', 'archived');

-- Create service_page_contents table
CREATE TABLE service_page_contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    service_slug TEXT NOT NULL,
    location_slug TEXT NULL, -- NULL for service overview pages
    
    -- SEO metadata
    title TEXT NOT NULL DEFAULT '',
    meta_description TEXT NOT NULL DEFAULT '',
    canonical_url TEXT NOT NULL DEFAULT '',
    target_keywords JSONB NOT NULL DEFAULT '[]'::jsonb,
    
    -- Content structure (JSONB for flexibility)
    content_blocks JSONB NOT NULL DEFAULT '[]'::jsonb,
    schema_blocks JSONB NOT NULL DEFAULT '[]'::jsonb,
    
    -- Generation metadata
    content_source content_source_enum NOT NULL DEFAULT 'template',
    revision INTEGER NOT NULL DEFAULT 1,
    content_hash TEXT NULL, -- For deduplication and idempotency
    
    -- Quality metrics (JSONB for extensibility)
    metrics JSONB NOT NULL DEFAULT '{
        "word_count": 0,
        "heading_count": 0,
        "internal_link_count": 0,
        "external_link_count": 0,
        "image_count": 0,
        "faq_count": 0,
        "readability_score": null,
        "keyword_density": {}
    }'::jsonb,
    
    -- Status and lifecycle
    status page_status_enum NOT NULL DEFAULT 'draft',
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for efficient queries
CREATE INDEX idx_service_page_contents_business_service 
    ON service_page_contents(business_id, service_slug);

CREATE INDEX idx_service_page_contents_business_service_location 
    ON service_page_contents(business_id, service_slug, location_slug);

CREATE INDEX idx_service_page_contents_status 
    ON service_page_contents(status);

CREATE INDEX idx_service_page_contents_content_hash 
    ON service_page_contents(content_hash) 
    WHERE content_hash IS NOT NULL;

-- Create unique constraint for business + service + location combination
CREATE UNIQUE INDEX idx_service_page_contents_unique_page 
    ON service_page_contents(business_id, service_slug, COALESCE(location_slug, ''));

-- Add GIN indexes for JSONB content search
CREATE INDEX idx_service_page_contents_content_blocks_gin 
    ON service_page_contents USING GIN (content_blocks);

CREATE INDEX idx_service_page_contents_schema_blocks_gin 
    ON service_page_contents USING GIN (schema_blocks);

CREATE INDEX idx_service_page_contents_target_keywords_gin 
    ON service_page_contents USING GIN (target_keywords);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_service_page_contents_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_service_page_contents_updated_at
    BEFORE UPDATE ON service_page_contents
    FOR EACH ROW
    EXECUTE FUNCTION update_service_page_contents_updated_at();

-- Create view for easy querying of published content
CREATE VIEW published_service_pages AS
SELECT 
    spc.*,
    b.name as business_name,
    b.city,
    b.state,
    b.phone as phone_number,
    b.email as business_email
FROM service_page_contents spc
JOIN businesses b ON spc.business_id = b.id
WHERE spc.status = 'published';

-- Add RLS (Row Level Security) policies
ALTER TABLE service_page_contents ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access content for their own business
CREATE POLICY service_page_contents_business_access 
    ON service_page_contents
    FOR ALL
    USING (
        business_id IN (
            SELECT id FROM businesses 
            WHERE owner_id = auth.uid()
        )
    );

-- Policy: Allow service role full access (for backend operations)
CREATE POLICY service_page_contents_service_role 
    ON service_page_contents
    FOR ALL
    TO service_role
    USING (true);

-- Add helpful comments
COMMENT ON TABLE service_page_contents IS 'Stores LLM-generated content blocks and schema markup for service pages';
COMMENT ON COLUMN service_page_contents.content_blocks IS 'Array of structured content blocks (hero, benefits, FAQ, etc.)';
COMMENT ON COLUMN service_page_contents.schema_blocks IS 'Array of JSON-LD schema markup blocks';
COMMENT ON COLUMN service_page_contents.content_hash IS 'Hash for deduplication and idempotency checks';
COMMENT ON COLUMN service_page_contents.metrics IS 'Content quality metrics (word count, headings, etc.)';
COMMENT ON INDEX idx_service_page_contents_unique_page IS 'Ensures one content record per business/service/location combination';
