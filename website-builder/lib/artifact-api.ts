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
  PromoteVariantRequest
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
    const artifacts = await listArtifacts(businessId, {
      activity_slug: activitySlug,
      location_slug: locationSlug,
      status: 'published',
      limit: 1
    });

    return artifacts.artifacts.length > 0 ? artifacts.artifacts[0] : null;
  } catch (error) {
    console.warn(`Failed to get artifact for ${activitySlug}:`, error);
    return null;
  }
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
