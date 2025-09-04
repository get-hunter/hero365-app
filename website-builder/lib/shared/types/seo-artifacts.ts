/**
 * SEO Artifacts TypeScript Types
 * 
 * TypeScript definitions for the artifact-based SEO system.
 * These types mirror the backend DTOs for type safety.
 */

export enum ActivityType {
  HVAC = "hvac",
  PLUMBING = "plumbing",
  ELECTRICAL = "electrical",
  ROOFING = "roofing",
  GENERAL_CONTRACTOR = "general_contractor",
  LANDSCAPING = "landscaping",
  SECURITY_SYSTEMS = "security_systems",
  POOL_SPA = "pool_spa",
  GARAGE_DOOR = "garage_door",
  CHIMNEY = "chimney",
  SEPTIC = "septic",
  PEST_CONTROL = "pest_control",
  IRRIGATION = "irrigation",
  PAINTING = "painting"
}

export enum ContentSource {
  TEMPLATE = "template",
  LLM = "llm",
  RAG_ENHANCED = "rag_enhanced",
  HYBRID = "hybrid",
  MANUAL = "manual"
}

export enum ArtifactStatus {
  DRAFT = "draft",
  APPROVED = "approved",
  PUBLISHED = "published",
  ARCHIVED = "archived"
}

export enum QualityLevel {
  EXCELLENT = "excellent",
  GOOD = "good",
  ACCEPTABLE = "acceptable",
  NEEDS_IMPROVEMENT = "needs_improvement",
  POOR = "poor"
}

export interface ActivityModuleConfig {
  module_type: string;
  enabled: boolean;
  config: Record<string, any>;
  order: number;
}

export interface ContentVariant {
  variant_key: string;
  content: Record<string, any>;
  weight: number;
  performance_metrics: Record<string, number>;
}

export interface QualityMetrics {
  overall_score: number;
  overall_level: QualityLevel;
  word_count: number;
  heading_count: number;
  internal_link_count: number;
  external_link_count: number;
  faq_count: number;
  readability_score?: number;
  keyword_density: Record<string, number>;
  local_intent_density: number;
  eat_score: number;
  uniqueness_score: number;
  coverage_score: number;
  passed_quality_gate: boolean;
}

export interface InternalLink {
  anchor_text: string;
  target_url: string;
  context: string;
  link_type: string;
}

export interface ActivityPageArtifact {
  // Identifiers
  artifact_id?: string;
  business_id: string;
  activity_slug: string;
  location_slug?: string;
  
  // Activity context
  activity_type: ActivityType;
  activity_name: string;
  
  // SEO metadata
  title: string;
  meta_description: string;
  h1_heading: string;
  canonical_url: string;
  target_keywords: string[];
  
  // Content sections
  hero: Record<string, any>;
  benefits: Record<string, any>;
  process: Record<string, any>;
  offers: Record<string, any>;
  guarantees: Record<string, any>;
  faqs: Array<{ question: string; answer: string }>;
  cta_sections: Array<Record<string, any>>;
  
  // Activity-specific modules
  activity_modules: ActivityModuleConfig[];
  
  // Structured data
  json_ld_schemas: Array<Record<string, any>>;
  
  // Internal linking
  internal_links: InternalLink[];
  
  // A/B testing
  content_variants: Record<string, ContentVariant[]>;
  active_experiment_keys: string[];
  
  // Quality and versioning
  quality_metrics: QualityMetrics;
  content_source: ContentSource;
  content_hash?: string;
  revision: number;
  
  // Status and lifecycle
  status: ArtifactStatus;
  approved_at?: string;
  published_at?: string;
  
  // Timestamps
  created_at?: string;
  updated_at?: string;
}

export interface SitemapEntry {
  loc: string;
  lastmod: string;
  changefreq: string;
  priority: number;
  page_type: string;
}

export interface SitemapManifest {
  business_id: string;
  sitemap_index_url: string;
  total_urls: number;
  generated_at: string;
  sitemaps: Array<{
    type: string;
    url: string;
    url_count: number;
    last_modified: string;
  }>;
  service_pages?: SitemapEntry[];
  location_pages?: SitemapEntry[];
  project_pages?: SitemapEntry[];
  static_pages?: SitemapEntry[];
}

export interface GenerateArtifactsRequest {
  business_id: string;
  activity_slugs?: string[];
  location_slugs?: string[];
  force_regenerate: boolean;
  enable_experiments: boolean;
  quality_threshold: number;
}

export interface GenerateArtifactsResponse {
  business_id: string;
  job_id: string;
  status: string;
  artifacts_generated: number;
  artifacts_approved: number;
  quality_gate_failures: number;
  estimated_completion?: string;
  generated_at: string;
}

export interface ArtifactListResponse {
  business_id: string;
  artifacts: ActivityPageArtifact[];
  total_count: number;
  approved_count: number;
  published_count: number;
  last_updated?: string;
}

export interface SitemapGenerationRequest {
  business_id: string;
  base_url: string;
  include_drafts: boolean;
  max_urls_per_sitemap: number;
}

export interface SitemapGenerationResponse {
  business_id: string;
  sitemap_index_url: string;
  sitemaps_generated: string[];
  total_urls: number;
  generated_at: string;
}

export interface ExperimentResult {
  experiment_key: string;
  winning_variant: string;
  confidence_level: number;
  improvement_percentage: number;
  sample_size: number;
  test_duration_days: number;
  metrics: Record<string, number>;
}

export interface PromoteVariantRequest {
  business_id: string;
  artifact_id: string;
  experiment_key: string;
  winning_variant_key: string;
  experiment_result: ExperimentResult;
}

export interface QualityGateResult {
  passed: boolean;
  overall_score: number;
  overall_level: QualityLevel;
  issues: string[];
  recommendations: string[];
  metrics: QualityMetrics;
}

// Utility types for component props
export interface ArtifactSectionProps {
  artifact: ActivityPageArtifact;
  testKey?: string;
  className?: string;
}

export interface ArtifactSectionWithBusinessProps extends ArtifactSectionProps {
  businessData: {
    id: string;
    name: string;
    phone: string;
    email: string;
    address: string;
    website: string;
    city: string;
    state: string;
  };
}

// Activity module types
export interface ActivityModuleProps {
  moduleType: string;
  config: Record<string, any>;
  activityType: ActivityType;
  businessData: {
    id: string;
    name: string;
    phone: string;
    email: string;
    city: string;
    state: string;
  };
}

// A/B testing types
export interface ABTestConfig {
  enabled: boolean;
  variants: Record<string, ContentVariant[]>;
  activeExperiments: string[];
  artifactId?: string;
  businessId: string;
}

export interface ABTestContextValue {
  getVariant: (testKey: string, defaultContent: any) => any;
  trackEvent: (eventName: string, testKey?: string, variantKey?: string) => void;
  isExperimentActive: (testKey: string) => boolean;
}
