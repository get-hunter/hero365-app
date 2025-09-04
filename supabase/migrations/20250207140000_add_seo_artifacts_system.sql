-- Migration: Add SEO Artifacts System
-- Description: Creates tables and views for the new artifact-based programmatic SEO system
-- Date: 2025-02-07

-- ============================================================================
-- ENUMS
-- ============================================================================

-- Activity types for specialized UI modules
CREATE TYPE activity_type AS ENUM (
    'hvac',
    'plumbing', 
    'electrical',
    'roofing',
    'general_contractor',
    'landscaping',
    'security_systems',
    'pool_spa',
    'garage_door',
    'chimney',
    'septic',
    'pest_control',
    'irrigation',
    'painting'
);

-- Content source types
CREATE TYPE content_source AS ENUM (
    'template',
    'llm',
    'rag_enhanced',
    'hybrid',
    'manual'
);

-- Artifact status
CREATE TYPE artifact_status AS ENUM (
    'draft',
    'approved', 
    'published',
    'archived'
);

-- Quality levels
CREATE TYPE quality_level AS ENUM (
    'excellent',
    'good',
    'acceptable',
    'needs_improvement',
    'poor'
);

-- ============================================================================
-- SEO ARTIFACTS TABLE
-- ============================================================================

CREATE TABLE seo_artifacts (
    -- Primary identifiers
    artifact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    activity_slug TEXT NOT NULL,
    location_slug TEXT NULL,
    
    -- Activity context
    activity_type activity_type NOT NULL,
    activity_name TEXT NOT NULL,
    
    -- SEO metadata
    title TEXT NOT NULL CHECK (char_length(title) <= 60),
    meta_description TEXT NOT NULL CHECK (char_length(meta_description) <= 160),
    h1_heading TEXT NOT NULL,
    canonical_url TEXT NOT NULL,
    target_keywords TEXT[] DEFAULT '{}',
    
    -- Content sections (JSONB for flexibility)
    hero JSONB DEFAULT '{}',
    benefits JSONB DEFAULT '{}',
    process JSONB DEFAULT '{}',
    offers JSONB DEFAULT '{}',
    guarantees JSONB DEFAULT '{}',
    faqs JSONB DEFAULT '[]',
    cta_sections JSONB DEFAULT '[]',
    
    -- Activity-specific modules
    activity_modules JSONB DEFAULT '[]',
    
    -- Structured data
    json_ld_schemas JSONB DEFAULT '[]',
    
    -- Internal linking
    internal_links JSONB DEFAULT '[]',
    
    -- A/B testing
    content_variants JSONB DEFAULT '{}',
    active_experiment_keys TEXT[] DEFAULT '{}',
    
    -- Quality metrics (JSONB for complex nested structure)
    quality_metrics JSONB NOT NULL DEFAULT '{
        "overall_score": 0,
        "overall_level": "needs_improvement",
        "word_count": 0,
        "heading_count": 0,
        "internal_link_count": 0,
        "external_link_count": 0,
        "faq_count": 0,
        "readability_score": null,
        "keyword_density": {},
        "local_intent_density": 0,
        "eat_score": 0,
        "uniqueness_score": 0,
        "coverage_score": 0,
        "passed_quality_gate": false
    }',
    
    -- Content versioning
    content_source content_source NOT NULL DEFAULT 'template',
    content_hash TEXT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    
    -- Status and lifecycle
    status artifact_status NOT NULL DEFAULT 'draft',
    approved_at TIMESTAMPTZ NULL,
    published_at TIMESTAMPTZ NULL,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(business_id, activity_slug, location_slug),
    CHECK (
        (location_slug IS NULL AND canonical_url LIKE '/services/%') OR
        (location_slug IS NOT NULL AND canonical_url LIKE '/locations/%')
    )
);

-- Indexes for performance
CREATE INDEX idx_seo_artifacts_business_id ON seo_artifacts(business_id);
CREATE INDEX idx_seo_artifacts_activity_slug ON seo_artifacts(activity_slug);
CREATE INDEX idx_seo_artifacts_location_slug ON seo_artifacts(location_slug) WHERE location_slug IS NOT NULL;
CREATE INDEX idx_seo_artifacts_status ON seo_artifacts(status);
CREATE INDEX idx_seo_artifacts_activity_type ON seo_artifacts(activity_type);
CREATE INDEX idx_seo_artifacts_updated_at ON seo_artifacts(updated_at DESC);
CREATE INDEX idx_seo_artifacts_quality_score ON seo_artifacts(((quality_metrics->>'overall_score')::numeric));

-- ============================================================================
-- SITEMAP MANIFESTS TABLE
-- ============================================================================

CREATE TABLE sitemap_manifests (
    business_id UUID PRIMARY KEY REFERENCES businesses(id) ON DELETE CASCADE,
    sitemap_index_url TEXT NOT NULL,
    total_urls INTEGER NOT NULL DEFAULT 0,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Sitemap entries (JSONB array for flexibility)
    sitemap_entries JSONB DEFAULT '[]',
    
    -- Individual sitemap files metadata
    sitemaps JSONB DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_sitemap_manifests_generated_at ON sitemap_manifests(generated_at DESC);

-- ============================================================================
-- ARTIFACT GENERATION JOBS TABLE
-- ============================================================================

CREATE TABLE artifact_generation_jobs (
    job_id UUID PRIMARY KEY,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    
    -- Job configuration
    activity_slugs TEXT[] NULL,
    location_slugs TEXT[] NULL,
    force_regenerate BOOLEAN DEFAULT FALSE,
    enable_experiments BOOLEAN DEFAULT FALSE,
    quality_threshold NUMERIC(5,2) DEFAULT 70.0,
    
    -- Results
    artifacts_generated INTEGER DEFAULT 0,
    artifacts_approved INTEGER DEFAULT 0,
    quality_gate_failures INTEGER DEFAULT 0,
    error_message TEXT NULL,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL
);

-- Indexes
CREATE INDEX idx_artifact_jobs_business_id ON artifact_generation_jobs(business_id);
CREATE INDEX idx_artifact_jobs_status ON artifact_generation_jobs(status);
CREATE INDEX idx_artifact_jobs_created_at ON artifact_generation_jobs(created_at DESC);

-- ============================================================================
-- EXPERIMENT RESULTS TABLE
-- ============================================================================

CREATE TABLE experiment_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    artifact_id UUID NOT NULL REFERENCES seo_artifacts(artifact_id) ON DELETE CASCADE,
    experiment_key TEXT NOT NULL,
    winning_variant TEXT NOT NULL,
    
    -- Experiment results (JSONB for flexibility)
    result JSONB NOT NULL DEFAULT '{}',
    
    -- Timestamps
    promoted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_experiment_results_business_id ON experiment_results(business_id);
CREATE INDEX idx_experiment_results_artifact_id ON experiment_results(artifact_id);
CREATE INDEX idx_experiment_results_promoted_at ON experiment_results(promoted_at DESC);

-- ============================================================================
-- VIEWS FOR SITEMAP GENERATION
-- ============================================================================

-- View for service pages sitemap
CREATE VIEW sitemap_service_pages AS
SELECT 
    sa.business_id,
    sa.canonical_url as loc,
    sa.updated_at as lastmod,
    'weekly' as changefreq,
    CASE 
        WHEN sa.location_slug IS NULL THEN 0.8
        ELSE 0.6
    END as priority,
    'service' as page_type
FROM seo_artifacts sa
WHERE sa.status IN ('approved', 'published')
    AND sa.location_slug IS NULL;

-- View for location pages sitemap  
CREATE VIEW sitemap_location_pages AS
SELECT 
    sa.business_id,
    sa.canonical_url as loc,
    sa.updated_at as lastmod,
    'weekly' as changefreq,
    0.6 as priority,
    'location' as page_type
FROM seo_artifacts sa
WHERE sa.status IN ('approved', 'published')
    AND sa.location_slug IS NOT NULL;

-- View for all sitemap entries
CREATE VIEW sitemap_all_pages AS
SELECT * FROM sitemap_service_pages
UNION ALL
SELECT * FROM sitemap_location_pages
UNION ALL
-- Static pages (can be extended)
SELECT 
    b.id as business_id,
    '/' as loc,
    NOW() as lastmod,
    'weekly' as changefreq,
    1.0 as priority,
    'static' as page_type
FROM businesses b
UNION ALL
SELECT 
    b.id as business_id,
    '/about' as loc,
    NOW() as lastmod,
    'monthly' as changefreq,
    0.8 as priority,
    'static' as page_type
FROM businesses b
UNION ALL
SELECT 
    b.id as business_id,
    '/contact' as loc,
    NOW() as lastmod,
    'monthly' as changefreq,
    0.8 as priority,
    'static' as page_type
FROM businesses b;

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_seo_artifacts_updated_at 
    BEFORE UPDATE ON seo_artifacts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sitemap_manifests_updated_at 
    BEFORE UPDATE ON sitemap_manifests 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically update sitemap manifest when artifacts change
CREATE OR REPLACE FUNCTION update_sitemap_manifest_on_artifact_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the sitemap manifest for this business
    UPDATE sitemap_manifests 
    SET 
        total_urls = (
            SELECT COUNT(*) 
            FROM seo_artifacts 
            WHERE business_id = COALESCE(NEW.business_id, OLD.business_id)
                AND status IN ('approved', 'published')
        ),
        updated_at = NOW()
    WHERE business_id = COALESCE(NEW.business_id, OLD.business_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Trigger to update sitemap manifest on artifact changes
CREATE TRIGGER update_sitemap_on_artifact_change
    AFTER INSERT OR UPDATE OR DELETE ON seo_artifacts
    FOR EACH ROW EXECUTE FUNCTION update_sitemap_manifest_on_artifact_change();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE seo_artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE sitemap_manifests ENABLE ROW LEVEL SECURITY;
ALTER TABLE artifact_generation_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE experiment_results ENABLE ROW LEVEL SECURITY;

-- RLS policies for seo_artifacts
CREATE POLICY "Users can view artifacts for their businesses" ON seo_artifacts
    FOR SELECT USING (
        business_id IN (
            SELECT business_id FROM business_memberships 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert artifacts for their businesses" ON seo_artifacts
    FOR INSERT WITH CHECK (
        business_id IN (
            SELECT business_id FROM business_memberships 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update artifacts for their businesses" ON seo_artifacts
    FOR UPDATE USING (
        business_id IN (
            SELECT business_id FROM business_memberships 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete artifacts for their businesses" ON seo_artifacts
    FOR DELETE USING (
        business_id IN (
            SELECT business_id FROM business_memberships 
            WHERE user_id = auth.uid()
        )
    );

-- Similar RLS policies for other tables
CREATE POLICY "Users can view sitemap manifests for their businesses" ON sitemap_manifests
    FOR SELECT USING (
        business_id IN (
            SELECT business_id FROM business_memberships 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage sitemap manifests for their businesses" ON sitemap_manifests
    FOR ALL USING (
        business_id IN (
            SELECT business_id FROM business_memberships 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can view generation jobs for their businesses" ON artifact_generation_jobs
    FOR SELECT USING (
        business_id IN (
            SELECT business_id FROM business_memberships 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage generation jobs for their businesses" ON artifact_generation_jobs
    FOR ALL USING (
        business_id IN (
            SELECT business_id FROM business_memberships 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can view experiment results for their businesses" ON experiment_results
    FOR SELECT USING (
        business_id IN (
            SELECT business_id FROM business_memberships 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage experiment results for their businesses" ON experiment_results
    FOR ALL USING (
        business_id IN (
            SELECT business_id FROM business_memberships 
            WHERE user_id = auth.uid()
        )
    );

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE seo_artifacts IS 'SEO artifacts for activity-first programmatic SEO system';
COMMENT ON TABLE sitemap_manifests IS 'Sitemap manifests for segmented sitemap generation';
COMMENT ON TABLE artifact_generation_jobs IS 'Background jobs for SEO artifact generation';
COMMENT ON TABLE experiment_results IS 'A/B test experiment results and winning variants';

COMMENT ON COLUMN seo_artifacts.quality_metrics IS 'JSONB containing comprehensive quality assessment metrics';
COMMENT ON COLUMN seo_artifacts.content_variants IS 'JSONB containing A/B test variants for different content sections';
COMMENT ON COLUMN seo_artifacts.activity_modules IS 'JSONB array of activity-specific UI module configurations';

-- ============================================================================
-- SAMPLE DATA (for development)
-- ============================================================================

-- This would be populated by the artifact generation system
-- Sample data can be added here for testing purposes
