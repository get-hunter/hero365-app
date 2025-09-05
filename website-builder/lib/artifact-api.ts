/**
 * Artifact API Client
 * 
 * Client library for interacting with the SEO artifact API endpoints.
 * Provides typed functions for fetching artifacts, sitemaps, and managing experiments.
 */

import { 
  ActivityPageArtifact, 
  ArtifactListResponse, 
  SitemapManifest,
  GenerateArtifactsRequest,
  GenerateArtifactsResponse,
  SitemapGenerationRequest,
  SitemapGenerationResponse,
  PromoteVariantRequest,
  ActivityModuleConfig,
  ContentSource,
  ArtifactStatus,
  QualityMetrics
} from '@/lib/shared/types/seo-artifacts';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Generic API client with error handling
 */
async function apiClient<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || 
        errorData.message || 
        `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

// ============================================================================
// ARTIFACT MANAGEMENT
// ============================================================================

/**
 * Generate SEO artifacts for a business
 */
export async function generateArtifacts(
  businessId: string, 
  request: Omit<GenerateArtifactsRequest, 'business_id'>
): Promise<GenerateArtifactsResponse> {
  return apiClient<GenerateArtifactsResponse>(
    `/api/v1/seo/artifacts/${businessId}/generate`,
    {
      method: 'POST',
      body: JSON.stringify({ ...request, business_id: businessId }),
    }
  );
}

/**
 * List SEO artifacts for a business
 */
export async function listArtifacts(
  businessId: string,
  options: {
    status?: string;
    activity_slug?: string;
    location_slug?: string;
    limit?: number;
    offset?: number;
  } = {}
): Promise<ArtifactListResponse> {
  const searchParams = new URLSearchParams();
  
  Object.entries(options).forEach(([key, value]) => {
    if (value !== undefined) {
      searchParams.append(key, value.toString());
    }
  });

  const queryString = searchParams.toString();
  const endpoint = `/api/v1/seo/artifacts/${businessId}${queryString ? `?${queryString}` : ''}`;
  
  return apiClient<ArtifactListResponse>(endpoint);
}

/**
 * Get a specific SEO artifact
 */
export async function getArtifact(
  businessId: string, 
  artifactId: string
): Promise<ActivityPageArtifact> {
  return apiClient<ActivityPageArtifact>(
    `/api/v1/seo/artifacts/${businessId}/${artifactId}`
  );
}

/**
 * Approve an SEO artifact
 */
export async function approveArtifact(
  businessId: string, 
  artifactId: string
): Promise<{ status: string; approved_at: string }> {
  return apiClient(
    `/api/v1/seo/artifacts/${businessId}/${artifactId}/approve`,
    { method: 'PUT' }
  );
}

/**
 * Get artifacts by activity slug (for page rendering)
 */
export async function getArtifactByActivity(
  businessId: string,
  activitySlug: string,
  locationSlug?: string
): Promise<ActivityPageArtifact | null> {
  try {
    // Try new unified content API first
    const params = new URLSearchParams({
      tier: 'enhanced',
      page_variant: 'standard',
    });
    
    if (locationSlug) {
      params.append('location_slug', locationSlug);
    }

    try {
      const response = await apiClient<{ artifact: ActivityPageArtifact }>(
        `/api/v1/content/artifact/${businessId}/${activitySlug}?${params.toString()}`
      );
      
      if (response.artifact) {
        console.log(`✅ [UNIFIED] Got artifact from unified API for ${activitySlug}`);
        return response.artifact;
      }
    } catch (unifiedError) {
      console.warn(`⚠️ [UNIFIED] Unified API failed for ${activitySlug}, falling back to legacy`);
    }

    // Fallback to legacy API
    const artifacts = await listArtifacts(businessId, {
      activity_slug: activitySlug,
      location_slug: locationSlug,
      status: 'published',
      limit: 1
    });

    if (artifacts.artifacts.length > 0) {
      console.log(`✅ [LEGACY] Got artifact from legacy API for ${activitySlug}`);
      return artifacts.artifacts[0];
    }

    // Return fallback artifact if no published artifacts found
    console.log(`⚠️ [FALLBACK] No published artifact found for ${activitySlug}, using fallback`);
    return getFallbackArtifact(businessId, activitySlug);
  } catch (error) {
    console.warn(`Failed to get artifact for ${activitySlug}:`, error);
    // Return fallback artifact on API error
    return getFallbackArtifact(businessId, activitySlug);
  }
}

/**
 * Generate a fallback artifact for development/testing
 */
function getFallbackArtifact(businessId: string, activitySlug: string): ActivityPageArtifact {
  const activityName = activitySlug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  
  return {
    business_id: businessId,
    activity_slug: activitySlug,
    activity_type: activitySlug.includes('hvac') ? 'hvac' : 
                   activitySlug.includes('plumb') ? 'plumbing' :
                   activitySlug.includes('electric') ? 'electrical' :
                   activitySlug.includes('roof') ? 'roofing' : 'general_contractor',
    activity_name: activityName,
    
    // SEO metadata
    title: `${activityName} Services | Professional Home Services`,
    meta_title: `${activityName} Services | Professional Home Services`,
    meta_description: `Expert ${activityName.toLowerCase()} services by licensed professionals. Fast response, quality work, satisfaction guaranteed.`,
    h1_heading: `Professional ${activityName} Services`,
    canonical_url: `${process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com'}/services/${activitySlug}`,
    target_keywords: [activityName.toLowerCase(), 'professional services', 'licensed', 'insured'],
    
    // Content sections
    hero: {
      headline: `Expert ${activityName} Services`,
      subtitle: 'Professional, reliable, and affordable solutions for your home',
      cta_primary: 'Get Free Quote',
      cta_secondary: 'Call Now'
    },
    benefits: {
      'Licensed & Insured': 'Fully licensed professionals with comprehensive insurance coverage',
      'Fast Response': '24/7 emergency service with quick response times',
      'Quality Guarantee': 'Satisfaction guaranteed on all work performed'
    },
    content_blocks: {
      overview: `Learn more about our expert ${activityName.toLowerCase()} services tailored to your needs.`,
      benefits: [
        { title: 'Licensed & Insured', description: 'Fully licensed professionals with comprehensive insurance coverage' },
        { title: 'Fast Response', description: '24/7 emergency service with quick response times' },
        { title: 'Quality Guarantee', description: 'Satisfaction guaranteed on all work performed' }
      ]
    },
    process: {
      'Contact Us': 'Call or schedule online for a free consultation',
      'Assessment': 'Professional evaluation and detailed estimate',
      'Service': 'Expert work completed to your satisfaction'
    },
    offers: {
      title: 'Current Offers',
      items: [
        { title: 'New Customer Discount', description: '10% off first service call' },
        { title: 'Emergency Service', description: '24/7 availability for urgent needs' }
      ]
    },
    guarantees: {
      title: 'Our Guarantees',
      items: [
        { title: 'Satisfaction Guarantee', description: 'Your satisfaction is our top priority' },
        { title: 'Quality Workmanship', description: 'All work backed by our quality guarantee' }
      ]
    },
    faqs: [
      {
        question: `How quickly can you respond to ${activityName.toLowerCase()} requests?`,
        answer: 'We typically respond within 2 hours for emergency calls and can schedule non-emergency services within 24-48 hours.'
      },
      {
        question: 'Are you licensed and insured?',
        answer: 'Yes, we are fully licensed and carry comprehensive insurance for your protection and peace of mind.'
      },
      {
        question: 'Do you provide warranties on your work?',
        answer: 'Yes, all our work comes with a satisfaction guarantee and appropriate warranties based on the type of service provided.'
      }
    ],
    cta_sections: [
      {
        type: 'primary',
        title: `Need ${activityName} Services?`,
        subtitle: 'Get a free quote from our licensed professionals',
        cta_text: 'Get Free Quote',
        cta_url: '/contact'
      }
    ],
    
    // Activity-specific modules
    activity_modules: [
      {
        module_type: activitySlug.includes('hvac') ? 'hvac_efficiency_calculator' :
                     activitySlug.includes('plumb') ? 'plumbing_severity_triage' :
                     activitySlug.includes('electric') ? 'electrical_load_calculator' :
                     activitySlug.includes('roof') ? 'roofing_material_selector' : 'project_estimator',
        config: {
          title: `${activityName} Calculator`,
          description: `Use our professional ${activityName.toLowerCase()} calculator to estimate your needs`
        }
      }
    ],
    
    // Structured data
    json_ld_schemas: [
      {
        '@context': 'https://schema.org',
        '@type': 'Service',
        'name': `${activityName} Services`,
        'description': `Professional ${activityName.toLowerCase()} services`,
        'provider': {
          '@type': 'LocalBusiness',
          'name': 'Professional Home Services'
        }
      }
    ],
    
    // Internal linking
    internal_links: [],
    
    // A/B testing
    content_variants: {},
    active_experiment_keys: [],
    
    // Quality and versioning
    quality_metrics: {
      readability_score: 85,
      seo_score: 90,
      content_depth: 75,
      keyword_density: 2.5,
      internal_links_count: 0,
      external_links_count: 0
    },
    content_source: ContentSource.GENERATED,
    revision: 1,
    
    // Status and lifecycle
    status: ArtifactStatus.PUBLISHED,
    
    // Timestamps
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };
}

// ============================================================================
// SITEMAP MANAGEMENT
// ============================================================================

/**
 * Generate sitemap manifest for a business
 */
export async function generateSitemap(
  businessId: string,
  request: Omit<SitemapGenerationRequest, 'business_id'>
): Promise<SitemapGenerationResponse> {
  return apiClient<SitemapGenerationResponse>(
    `/api/v1/seo/sitemaps/${businessId}/generate`,
    {
      method: 'POST',
      body: JSON.stringify({ ...request, business_id: businessId }),
    }
  );
}

/**
 * Get sitemap manifest for a business
 */
export async function getSitemapManifest(businessId: string): Promise<SitemapManifest | null> {
  try {
    return await apiClient<SitemapManifest>(`/api/v1/seo/sitemaps/${businessId}`);
  } catch (error) {
    console.warn(`Failed to get sitemap manifest for ${businessId}:`, error);
    return null;
  }
}

// ============================================================================
// A/B TESTING & EXPERIMENTS
// ============================================================================

/**
 * Promote winning A/B test variant
 */
export async function promoteVariant(
  businessId: string,
  request: Omit<PromoteVariantRequest, 'business_id'>
): Promise<{ promoted_at: string }> {
  return apiClient(
    `/api/v1/seo/experiments/${businessId}/promote`,
    {
      method: 'POST',
      body: JSON.stringify({ ...request, business_id: businessId }),
    }
  );
}

/**
 * Track A/B test event
 */
export async function trackABTestEvent(eventData: {
  event: string;
  timestamp: string;
  sessionId: string;
  businessId: string;
  artifactId?: string;
  testKey?: string;
  variantKey?: string;
  url: string;
  userAgent: string;
}): Promise<void> {
  try {
    await apiClient('/api/v1/analytics/ab-test-events', {
      method: 'POST',
      body: JSON.stringify(eventData),
    });
  } catch (error) {
    // Don't throw on analytics errors
    console.warn('Failed to track A/B test event:', error);
  }
}

// ============================================================================
// LEGACY COMPATIBILITY
// ============================================================================

/**
 * Get SEO pages (legacy format) - for backward compatibility
 */
export async function getLegacySEOPages(businessId: string): Promise<any> {
  try {
    return await apiClient(`/api/v1/seo/pages/${businessId}`);
  } catch (error) {
    console.warn(`Failed to get legacy SEO pages for ${businessId}:`, error);
    return { pages: {}, total_pages: 0 };
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Check if artifacts are available for a business
 */
export async function hasArtifacts(businessId: string): Promise<boolean> {
  try {
    const response = await listArtifacts(businessId, { limit: 1 });
    return response.total_count > 0;
  } catch (error) {
    return false;
  }
}

/**
 * Get artifact generation status
 */
export async function getGenerationStatus(
  businessId: string,
  jobId: string
): Promise<{ status: string; progress?: number }> {
  try {
    return await apiClient(`/api/v1/seo/artifacts/${businessId}/jobs/${jobId}`);
  } catch (error) {
    return { status: 'unknown' };
  }
}

/**
 * Validate artifact quality
 */
export function validateArtifactQuality(artifact: ActivityPageArtifact): {
  isValid: boolean;
  issues: string[];
  score: number;
} {
  const issues: string[] = [];
  let score = artifact.quality_metrics.overall_score;

  // Check required fields
  if (!artifact.title || artifact.title.length === 0) {
    issues.push('Missing title');
    score -= 10;
  }

  if (!artifact.meta_description || artifact.meta_description.length === 0) {
    issues.push('Missing meta description');
    score -= 10;
  }

  if (artifact.title && artifact.title.length > 60) {
    issues.push('Title too long (>60 characters)');
    score -= 5;
  }

  if (artifact.meta_description && artifact.meta_description.length > 160) {
    issues.push('Meta description too long (>160 characters)');
    score -= 5;
  }

  if (artifact.quality_metrics.word_count < 300) {
    issues.push('Content too short (<300 words)');
    score -= 15;
  }

  if (artifact.quality_metrics.internal_link_count === 0) {
    issues.push('No internal links');
    score -= 5;
  }

  if (artifact.faqs.length === 0) {
    issues.push('No FAQ content');
    score -= 5;
  }

  return {
    isValid: issues.length === 0 && score >= 70,
    issues,
    score: Math.max(0, score)
  };
}

/**
 * Format artifact for display
 */
export function formatArtifactForDisplay(artifact: ActivityPageArtifact) {
  return {
    ...artifact,
    displayTitle: artifact.title,
    displayDescription: artifact.meta_description,
    displayUrl: artifact.canonical_url,
    qualityLabel: getQualityLabel(artifact.quality_metrics.overall_level),
    statusLabel: getStatusLabel(artifact.status),
    lastUpdated: artifact.updated_at ? new Date(artifact.updated_at).toLocaleDateString() : 'Unknown',
    wordCount: artifact.quality_metrics.word_count.toLocaleString(),
    qualityScore: artifact.quality_metrics.overall_score.toFixed(1)
  };
}

function getQualityLabel(level: string): string {
  switch (level) {
    case 'excellent': return 'Excellent';
    case 'good': return 'Good';
    case 'acceptable': return 'Acceptable';
    case 'needs_improvement': return 'Needs Improvement';
    case 'poor': return 'Poor';
    default: return 'Unknown';
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'draft': return 'Draft';
    case 'approved': return 'Approved';
    case 'published': return 'Published';
    case 'archived': return 'Archived';
    default: return 'Unknown';
  }
}
