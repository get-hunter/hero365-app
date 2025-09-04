# SEO Artifacts API Documentation

## Overview

The SEO Artifacts API provides programmatic SEO at scale through activity-first content generation, quality gates, A/B testing, and automated sitemap management. This system replaces generic page templates with typed, versioned content artifacts that leverage business context, technician data, and RAG-enhanced LLM orchestration.

## Architecture

### Core Concepts

- **Artifacts**: Typed, versioned content objects for activity pages (e.g., "AC Installation", "Drain Cleaning")
- **Quality Gates**: Automated validation ensuring content meets E-E-A-T standards
- **Activity Modules**: Specialized UI components per trade (HVAC tune-up checklist, plumbing severity triage)
- **Segmented Sitemaps**: Separate sitemaps for services, locations, projects with accurate lastmod
- **A/B Testing**: Content variants with automated winner promotion

### Data Flow

```
Business Context + Technician Data + Projects + Reviews
                    ↓
            RAG-Enhanced Orchestrator
                    ↓
            Activity Page Artifacts
                    ↓
            Quality Gate Validation
                    ↓
            Approved/Published Content
                    ↓
            Segmented Sitemap Generation
```

## Endpoints

### Artifact Generation

#### `POST /api/v1/seo/artifacts/{business_id}/generate`

Generate SEO artifacts for activities using RAG-enhanced LLM orchestration.

**Request Body:**
```json
{
  "business_id": "uuid",
  "activity_slugs": ["ac-installation", "drain-cleaning"],
  "location_slugs": ["austin-tx", "houston-tx"],
  "force_regenerate": false,
  "enable_experiments": true,
  "quality_threshold": 75.0
}
```

**Response:**
```json
{
  "business_id": "uuid",
  "job_id": "uuid",
  "status": "queued",
  "generated_at": "2025-02-07T14:00:00Z",
  "estimated_completion": "2025-02-07T14:10:00Z"
}
```

**Background Processing:**
- Queues artifact generation job
- Uses RAG to retrieve business context, technician data, projects, reviews
- Generates typed content artifacts with quality metrics
- Applies quality gates (E-E-A-T, uniqueness, coverage, local intent)
- Creates A/B test variants if enabled

### Artifact Management

#### `GET /api/v1/seo/artifacts/{business_id}`

List SEO artifacts with filtering and pagination.

**Query Parameters:**
- `status`: Filter by artifact status (`draft`, `approved`, `published`, `archived`)
- `activity_slug`: Filter by specific activity
- `location_slug`: Filter by specific location
- `limit`: Results per page (max 100, default 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "business_id": "uuid",
  "artifacts": [
    {
      "artifact_id": "uuid",
      "business_id": "uuid",
      "activity_slug": "ac-installation",
      "location_slug": null,
      "activity_type": "hvac",
      "activity_name": "AC Installation",
      "title": "Professional AC Installation Services | Elite HVAC Austin",
      "meta_description": "Expert AC installation by licensed technicians. 24/7 service, 5-year warranty, financing available. Call (512) 555-0123 for free estimate.",
      "h1_heading": "Professional AC Installation Services",
      "canonical_url": "/services/ac-installation",
      "target_keywords": ["ac installation", "air conditioning installation", "Austin HVAC"],
      "hero": {
        "headline": "Professional AC Installation You Can Trust",
        "subheading": "Licensed technicians, 5-year warranty, same-day service",
        "cta_primary": "Get Free Estimate",
        "cta_secondary": "Call (512) 555-0123"
      },
      "benefits": {
        "title": "Why Choose Elite HVAC for AC Installation",
        "benefits": [
          {
            "title": "Licensed & Insured",
            "description": "Fully licensed HVAC contractors with comprehensive insurance coverage",
            "icon": "shield"
          },
          {
            "title": "5-Year Warranty",
            "description": "Industry-leading warranty on all installation work and parts",
            "icon": "warranty"
          }
        ]
      },
      "process": {
        "title": "Our AC Installation Process",
        "steps": [
          {
            "name": "Free In-Home Assessment",
            "description": "Comprehensive evaluation of your home's cooling needs",
            "duration": "30-45 minutes"
          },
          {
            "name": "Custom System Design",
            "description": "Right-sized equipment selection for optimal efficiency",
            "duration": "Same day"
          }
        ]
      },
      "faqs": [
        {
          "question": "How long does AC installation take?",
          "answer": "Most residential AC installations are completed in 4-8 hours, depending on system complexity and home layout."
        }
      ],
      "activity_modules": [
        {
          "module_type": "hvac_efficiency_calculator",
          "enabled": true,
          "config": {
            "show_seer_ratings": true,
            "include_rebates": true
          },
          "order": 1
        }
      ],
      "json_ld_schemas": [
        {
          "@context": "https://schema.org",
          "@type": "Service",
          "name": "AC Installation",
          "provider": {
            "@type": "LocalBusiness",
            "name": "Elite HVAC Austin"
          }
        }
      ],
      "internal_links": [
        {
          "anchor_text": "HVAC maintenance",
          "target_url": "/services/hvac-maintenance",
          "context": "Keep your new AC running efficiently with regular maintenance"
        }
      ],
      "quality_metrics": {
        "overall_score": 87.5,
        "overall_level": "good",
        "word_count": 1250,
        "heading_count": 8,
        "internal_link_count": 6,
        "external_link_count": 2,
        "faq_count": 12,
        "readability_score": 82.0,
        "local_intent_density": 0.15,
        "eat_score": 85.0,
        "uniqueness_score": 92.0,
        "coverage_score": 88.0,
        "passed_quality_gate": true
      },
      "content_source": "rag_enhanced",
      "status": "approved",
      "revision": 1,
      "created_at": "2025-02-07T14:00:00Z",
      "updated_at": "2025-02-07T14:05:00Z",
      "approved_at": "2025-02-07T14:05:00Z"
    }
  ],
  "total_count": 25,
  "approved_count": 18,
  "published_count": 15,
  "last_updated": "2025-02-07T14:05:00Z"
}
```

#### `GET /api/v1/seo/artifacts/{business_id}/{artifact_id}`

Get a specific SEO artifact by ID.

**Response:** Single artifact object (same structure as list item above).

#### `PUT /api/v1/seo/artifacts/{business_id}/{artifact_id}/approve`

Approve an SEO artifact for publication.

**Response:**
```json
{
  "business_id": "uuid",
  "artifact_id": "uuid", 
  "status": "approved",
  "approved_at": "2025-02-07T14:05:00Z"
}
```

### Sitemap Management

#### `POST /api/v1/seo/sitemaps/{business_id}/generate`

Generate segmented sitemaps for a business.

**Request Body:**
```json
{
  "business_id": "uuid",
  "base_url": "https://elitehvacaustin.com",
  "include_drafts": false,
  "max_urls_per_sitemap": 50000
}
```

**Response:**
```json
{
  "business_id": "uuid",
  "sitemap_index_url": "https://elitehvacaustin.com/sitemap.xml",
  "sitemaps_generated": [
    "https://elitehvacaustin.com/sitemap-services.xml",
    "https://elitehvacaustin.com/sitemap-locations.xml", 
    "https://elitehvacaustin.com/sitemap-static.xml"
  ],
  "total_urls": 127,
  "generated_at": "2025-02-07T14:00:00Z"
}
```

#### `GET /api/v1/seo/sitemaps/{business_id}`

Get sitemap manifest for a business.

**Response:**
```json
{
  "business_id": "uuid",
  "sitemap_index_url": "https://elitehvacaustin.com/sitemap.xml",
  "total_urls": 127,
  "generated_at": "2025-02-07T14:00:00Z",
  "sitemaps": [
    {
      "type": "services",
      "url": "https://elitehvacaustin.com/sitemap-services.xml",
      "url_count": 45,
      "last_modified": "2025-02-07T14:00:00Z"
    },
    {
      "type": "locations", 
      "url": "https://elitehvacaustin.com/sitemap-locations.xml",
      "url_count": 78,
      "last_modified": "2025-02-07T14:00:00Z"
    }
  ]
}
```

### A/B Testing & Experiments

#### `POST /api/v1/seo/experiments/{business_id}/promote`

Promote winning A/B test variant to production.

**Request Body:**
```json
{
  "business_id": "uuid",
  "artifact_id": "uuid",
  "experiment_key": "hero_headline_test",
  "winning_variant_key": "variant_b",
  "experiment_result": {
    "experiment_key": "hero_headline_test",
    "winning_variant": "variant_b",
    "confidence_level": 0.95,
    "improvement_percentage": 12.5,
    "sample_size": 1250,
    "test_duration_days": 14,
    "metrics": {
      "conversion_rate": 0.087,
      "click_through_rate": 0.234
    }
  }
}
```

**Response:**
```json
{
  "business_id": "uuid",
  "artifact_id": "uuid",
  "experiment_key": "hero_headline_test",
  "winning_variant": "variant_b",
  "promoted_at": "2025-02-07T14:00:00Z"
}
```

## Quality Gates

### Quality Metrics

All artifacts are evaluated against comprehensive quality metrics:

- **Overall Score**: 0-100 composite score
- **E-E-A-T Score**: Experience, Expertise, Authoritativeness, Trustworthiness
- **Word Count**: Minimum thresholds per page type
- **Readability**: Flesch-Kincaid grade level
- **Local Intent Density**: Percentage of location-specific content
- **Uniqueness Score**: Content originality vs. existing pages
- **Coverage Score**: Topic comprehensiveness

### Quality Levels

- **Excellent** (90-100): Publish immediately
- **Good** (75-89): Approve with minor review
- **Acceptable** (60-74): Requires review before approval
- **Needs Improvement** (40-59): Regenerate with feedback
- **Poor** (0-39): Reject and regenerate

## Activity Modules

### Available Modules by Trade

#### HVAC
- `hvac_efficiency_calculator`: SEER/BTU calculator
- `hvac_tune_up_checklist`: Maintenance checklist
- `hvac_seasonal_tips`: Seasonal optimization tips

#### Plumbing  
- `plumbing_severity_triage`: Issue severity assessment
- `plumbing_fixture_estimator`: Fixture count calculator
- `plumbing_emergency_guide`: Emergency response guide

#### Electrical
- `electrical_panel_capacity`: Panel load calculator
- `electrical_safety_guide`: AFCI/GFCI explainer
- `electrical_code_compliance`: Code requirement checker

#### Roofing
- `roofing_material_selector`: Material comparison tool
- `roofing_age_estimator`: Roof age assessment
- `roofing_storm_damage`: Storm damage claim guide

## Error Handling

### Standard Error Responses

```json
{
  "error": {
    "code": "ARTIFACT_NOT_FOUND",
    "message": "SEO artifact not found",
    "details": {
      "business_id": "uuid",
      "artifact_id": "uuid"
    }
  }
}
```

### Common Error Codes

- `BUSINESS_NOT_FOUND`: Business ID not found
- `ARTIFACT_NOT_FOUND`: Artifact ID not found  
- `QUALITY_GATE_FAILED`: Content failed quality validation
- `GENERATION_JOB_FAILED`: Background job failed
- `INVALID_ACTIVITY_SLUG`: Activity not supported
- `SITEMAP_GENERATION_FAILED`: Sitemap creation failed

## Rate Limits

- **Artifact Generation**: 5 requests per minute per business
- **Artifact Retrieval**: 100 requests per minute per business
- **Sitemap Generation**: 2 requests per minute per business

## Webhooks (Future)

Webhook endpoints will be available for:
- Artifact generation completion
- Quality gate results
- A/B test conclusions
- Sitemap updates

## Integration Examples

### Mobile App Integration

```typescript
// Generate artifacts for selected activities
const response = await fetch('/api/v1/seo/artifacts/business-id/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    business_id: 'uuid',
    activity_slugs: ['ac-installation', 'heating-repair'],
    quality_threshold: 80.0,
    enable_experiments: true
  })
});

const job = await response.json();
console.log(`Generation job queued: ${job.job_id}`);
```

### Website Builder Integration

```typescript
// Fetch approved artifacts for website rendering
const artifacts = await fetch('/api/v1/seo/artifacts/business-id?status=approved')
  .then(r => r.json());

// Generate sitemap during deployment
const sitemap = await fetch('/api/v1/seo/sitemaps/business-id/generate', {
  method: 'POST',
  body: JSON.stringify({
    business_id: 'uuid',
    base_url: 'https://business.hero365.ai'
  })
});
```

## Migration from Legacy System

### Compatibility

The new artifact system maintains backward compatibility with existing SEO endpoints:
- `/api/v1/seo/pages/{business_id}` continues to work
- Legacy content is automatically migrated to artifact format
- Existing sitemaps are preserved during transition

### Migration Steps

1. **Phase 1**: Deploy artifact system alongside legacy
2. **Phase 2**: Generate artifacts for existing businesses
3. **Phase 3**: Switch website builder to artifact-based rendering
4. **Phase 4**: Deprecate legacy endpoints (6 months notice)

## Performance Considerations

- **Artifact Generation**: 2-5 minutes per business (background job)
- **Artifact Retrieval**: <100ms average response time
- **Sitemap Generation**: <30 seconds for businesses with <10k pages
- **Quality Gate Validation**: <10 seconds per artifact

## Security

- All endpoints require business membership authentication
- Row-level security enforced at database level
- Content sanitization applied to all user inputs
- Rate limiting prevents abuse
- Audit logging for all artifact modifications
