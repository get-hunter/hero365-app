# Legacy SEO System Cleanup Plan

## Overview

With the new artifact-based SEO system implemented, several legacy components need to be deprecated and eventually removed. This document outlines the cleanup strategy to maintain system integrity while transitioning to the new architecture.

## Legacy Components to Deprecate

### 1. Website Builder Legacy Generators

#### Files to Mark as Legacy:
- `website-builder/lib/build-time/seo-generator.ts` - **LEGACY**: Replace with artifact-based generation
- `website-builder/lib/build-time/activity-seo-generator.ts` - **LEGACY**: Superseded by artifact system
- `website-builder/lib/build-time/sitemap-generator.ts` - **LEGACY**: Replace with segmented sitemap API
- `website-builder/scripts/prebuild-seo.js` - **LEGACY**: Replace with artifact fetching
- `website-builder/lib/website-generator-v2.ts` - **LEGACY**: Replace with artifact renderer

#### Replacement Strategy:
```typescript
// OLD: Generic template-based generation
const seoPages = await generateSEOContent(businessData);

// NEW: Artifact-based rendering
const artifacts = await fetch('/api/v1/seo/artifacts/business-id?status=approved');
const pages = artifacts.map(artifact => renderArtifactPage(artifact));
```

### 2. Backend Legacy Services

#### Files to Mark as Legacy:
- `backend/app/application/services/llm_content_orchestrator.py` - **PARTIAL LEGACY**: Refactor for artifact generation
- `backend/app/application/services/seo_scaffolding_service.py` - **LEGACY**: Replace with artifact-based scaffolding
- `backend/app/workers/website_tasks.py` (SEO parts) - **LEGACY**: Replace with artifact generation jobs

#### Migration Path:
1. **Phase 1**: Mark as deprecated, maintain for backward compatibility
2. **Phase 2**: Redirect to new artifact system internally
3. **Phase 3**: Remove after 6 months deprecation period

### 3. Database Tables to Deprecate

#### Legacy Tables:
- `generated_seo_pages` - **LEGACY**: Replace with `seo_artifacts`
- `service_page_contents` - **LEGACY**: Migrate to `seo_artifacts`
- `service_location_pages` - **LEGACY**: Generate from artifacts
- `service_seo_config` - **LEGACY**: Configuration moved to artifacts

#### Migration Strategy:
```sql
-- Migration script to move data from legacy tables
INSERT INTO seo_artifacts (
    business_id, activity_slug, title, meta_description, 
    content_source, status, created_at
)
SELECT 
    business_id, 
    SPLIT_PART(page_url, '/', 3) as activity_slug,
    title, 
    meta_description,
    'template'::content_source,
    'published'::artifact_status,
    created_at
FROM generated_seo_pages
WHERE page_type = 'service';
```

### 4. Frontend Components to Update

#### Components Needing Artifact Integration:
- `website-builder/components/seo/Hero365SEOComposer.tsx` - **UPDATE**: Add artifact support
- `website-builder/components/pages/Hero365SEOPageContent.tsx` - **UPDATE**: Render from artifacts
- `website-builder/app/sitemap.ts` - **UPDATE**: Use artifact-based sitemap API
- `website-builder/app/[...slug]/page.tsx` - **UPDATE**: Fetch from artifact API

#### New Component Architecture:
```typescript
// Artifact-based page renderer
export default function ArtifactPage({ artifact }: { artifact: ActivityPageArtifact }) {
  return (
    <div>
      <ArtifactHero artifact={artifact} />
      <ArtifactBenefits artifact={artifact} />
      <ArtifactProcess artifact={artifact} />
      {artifact.activity_modules.map(module => 
        <ActivityModule key={module.module_type} config={module} />
      )}
      <ArtifactFAQs artifact={artifact} />
    </div>
  );
}
```

## Cleanup Timeline

### Phase 1: Deprecation Marking (Week 1-2)
- [ ] Add `@deprecated` comments to all legacy files
- [ ] Update documentation to point to new system
- [ ] Add console warnings for legacy API usage
- [ ] Create migration guides for developers

### Phase 2: Parallel Operation (Month 1-3)
- [ ] Both systems run in parallel
- [ ] New businesses use artifact system by default
- [ ] Existing businesses gradually migrated
- [ ] Monitor performance and stability

### Phase 3: Legacy Removal (Month 4-6)
- [ ] Remove deprecated code after 6 months notice
- [ ] Drop legacy database tables
- [ ] Clean up unused dependencies
- [ ] Update all documentation

## Legacy Code Markers

### File Header Template:
```typescript
/**
 * @deprecated This file is part of the legacy SEO system and will be removed in v2.0.0
 * 
 * Migration Path:
 * - Replace with artifact-based SEO system
 * - Use /api/v1/seo/artifacts endpoints
 * - See docs/api/seo-artifacts-api.md for new API
 * 
 * Removal Date: 2025-08-07
 */
```

### Function Deprecation:
```typescript
/**
 * @deprecated Use generateSEOArtifacts() instead
 * @see /api/v1/seo/artifacts/{business_id}/generate
 */
export async function generateSEOContent(businessData: any) {
  console.warn('generateSEOContent is deprecated. Use artifact-based generation.');
  // Legacy implementation...
}
```

## Migration Scripts

### 1. Data Migration Script
```bash
#!/bin/bash
# migrate-seo-data.sh

echo "🔄 Migrating SEO data to artifact system..."

# Migrate generated_seo_pages to seo_artifacts
npx supabase db push --file migrations/migrate_seo_pages_to_artifacts.sql

# Migrate service_page_contents to seo_artifacts
npx supabase db push --file migrations/migrate_service_contents_to_artifacts.sql

echo "✅ SEO data migration completed"
```

### 2. Code Migration Script
```bash
#!/bin/bash
# update-seo-imports.sh

echo "🔄 Updating SEO imports to use artifact system..."

# Replace old imports with new ones
find website-builder -name "*.tsx" -o -name "*.ts" | xargs sed -i '' \
  's/import.*seo-generator.*/\/\/ LEGACY: Use artifact API instead/g'

# Add deprecation warnings
find website-builder -name "*.tsx" -o -name "*.ts" | xargs sed -i '' \
  's/generateSEOContent/generateSEOContent \/\/ @deprecated/g'

echo "✅ Import updates completed"
```

## Testing Strategy

### 1. Backward Compatibility Tests
```typescript
describe('Legacy SEO System Compatibility', () => {
  it('should maintain API compatibility during transition', async () => {
    // Test that old endpoints still work
    const legacyResponse = await fetch('/api/v1/seo/pages/business-id');
    const artifactResponse = await fetch('/api/v1/seo/artifacts/business-id');
    
    expect(legacyResponse.status).toBe(200);
    expect(artifactResponse.status).toBe(200);
  });
  
  it('should show deprecation warnings', async () => {
    const consoleSpy = jest.spyOn(console, 'warn');
    await generateSEOContent(mockBusinessData);
    
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('deprecated')
    );
  });
});
```

### 2. Migration Validation Tests
```typescript
describe('SEO Data Migration', () => {
  it('should migrate all legacy pages to artifacts', async () => {
    const legacyCount = await db.count('generated_seo_pages');
    const artifactCount = await db.count('seo_artifacts');
    
    expect(artifactCount).toBeGreaterThanOrEqual(legacyCount);
  });
  
  it('should preserve SEO metadata during migration', async () => {
    const legacyPage = await db.findOne('generated_seo_pages');
    const artifact = await db.findOne('seo_artifacts', { 
      activity_slug: extractSlugFromUrl(legacyPage.page_url) 
    });
    
    expect(artifact.title).toBe(legacyPage.title);
    expect(artifact.meta_description).toBe(legacyPage.meta_description);
  });
});
```

## Performance Monitoring

### Metrics to Track During Migration:
- **Page Load Times**: Artifact pages vs legacy pages
- **SEO Scores**: Lighthouse scores before/after migration
- **Search Rankings**: Monitor for any ranking drops
- **Error Rates**: Track 404s and rendering errors
- **Generation Times**: Artifact generation vs legacy generation

### Monitoring Dashboard:
```typescript
// Migration monitoring metrics
const migrationMetrics = {
  legacyPagesRemaining: await db.count('generated_seo_pages'),
  artifactsGenerated: await db.count('seo_artifacts'),
  migrationProgress: (artifactsGenerated / totalPages) * 100,
  averageQualityScore: await db.avg('seo_artifacts.quality_metrics.overall_score'),
  errorRate: await db.count('artifact_generation_jobs', { status: 'failed' })
};
```

## Rollback Plan

### Emergency Rollback Procedure:
1. **Immediate**: Switch traffic back to legacy system
2. **Database**: Restore legacy tables from backup
3. **Code**: Revert to previous deployment
4. **Monitoring**: Track system stability post-rollback

### Rollback Triggers:
- Page load time increase >50%
- Error rate increase >5%
- SEO score drop >10 points
- Search ranking drop >20%

## Communication Plan

### Developer Communication:
- [ ] Send deprecation notice to development team
- [ ] Update README with migration instructions
- [ ] Create Slack channel for migration questions
- [ ] Schedule knowledge transfer sessions

### Stakeholder Communication:
- [ ] Notify product team of timeline
- [ ] Update project roadmap
- [ ] Communicate benefits of new system
- [ ] Set expectations for migration period

## Success Criteria

### Migration Complete When:
- [ ] All businesses using artifact system
- [ ] Legacy code removed from codebase
- [ ] Legacy database tables dropped
- [ ] Documentation updated
- [ ] Performance metrics stable or improved
- [ ] Zero legacy API usage in logs

### Quality Gates:
- [ ] No degradation in page load times
- [ ] SEO scores maintained or improved
- [ ] Search rankings stable
- [ ] Error rates below baseline
- [ ] Developer satisfaction with new system

## Post-Migration Benefits

### Expected Improvements:
- **Performance**: 40% faster page generation
- **SEO Quality**: 25% higher average quality scores
- **Scalability**: Support for 10x more pages
- **Maintainability**: 60% reduction in SEO-related bugs
- **Developer Experience**: Unified API, better tooling
- **Content Quality**: RAG-enhanced, contextual content
- **A/B Testing**: Built-in experimentation platform
