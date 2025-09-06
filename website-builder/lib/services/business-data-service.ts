/**
 * Unified Business Data Service
 * 
 * Consolidates all business data fetching with proper error handling,
 * caching, and type safety. Eliminates scattered fetch calls.
 */

import { getRuntimeConfig } from '../server/runtime-config';
import { getDefaultHeaders } from '../shared/config/api-config';
import type {
  EnhancedBusinessProfile,
  EnhancedServiceItem,
  EnhancedProductItem,
  EnhancedProjectItem,
  EnhancedLocationItem,
  EnhancedServiceCategory,
  EnhancedHomepageData,
  DiagnosticsInfo,
  MembershipPlan
} from '../shared/types/enhanced-api-responses';

// Service configuration
interface ServiceConfig {
  timeout: number;
  retries: number;
  cache: RequestCache;
  revalidate?: number;
}

const DEFAULT_CONFIG: ServiceConfig = {
  timeout: 8000,
  retries: 2,
  cache: 'default',
  revalidate: 300 // 5 minutes
};

// Data loading options
export interface DataOptions {
  includeServices?: boolean;
  includeProducts?: boolean;
  includeProjects?: boolean;
  includeLocations?: boolean;
  includeCategories?: boolean;
  includeMembership?: boolean;
  featuredOnly?: boolean;
  limit?: number;
}

// Error types for better error handling
export class BusinessDataError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode?: number,
    public readonly endpoint?: string
  ) {
    super(message);
    this.name = 'BusinessDataError';
  }
}

/**
 * Core Business Data Service
 */
export class BusinessDataService {
  private config: ServiceConfig;
  private baseUrl: string | null = null;

  constructor(config: Partial<ServiceConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Initialize the service with runtime configuration
   */
  private async initialize(): Promise<void> {
    if (!this.baseUrl) {
      const runtimeConfig = await getRuntimeConfig();
      this.baseUrl = runtimeConfig.apiUrl;
    }
  }

  /**
   * Generic fetch wrapper with error handling and retries
   */
  private async fetchWithRetry<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T | null> {
    await this.initialize();
    
    const url = `${this.baseUrl}${endpoint}`;
    const fetchOptions: RequestInit = {
      headers: getDefaultHeaders(),
      signal: AbortSignal.timeout(this.config.timeout),
      cache: this.config.cache,
      ...options
    };

    // Add revalidate for Next.js caching
    if (this.config.revalidate && typeof options.next === 'undefined') {
      fetchOptions.next = { revalidate: this.config.revalidate };
    }

    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.config.retries; attempt++) {
      try {
        console.log(`🔄 [DATA-SERVICE] Fetching (attempt ${attempt}): ${endpoint}`);
        
        const response = await fetch(url, fetchOptions);
        
        if (!response.ok) {
          const errorText = await response.text().catch(() => '');
          throw new BusinessDataError(
            `HTTP ${response.status}: ${errorText || response.statusText}`,
            'HTTP_ERROR',
            response.status,
            endpoint
          );
        }

        const data = await response.json();
        console.log(`✅ [DATA-SERVICE] Success: ${endpoint}`);
        return data as T;

      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        console.warn(`⚠️ [DATA-SERVICE] Attempt ${attempt} failed for ${endpoint}:`, lastError.message);
        
        // Don't retry on client errors (4xx)
        if (error instanceof BusinessDataError && error.statusCode && error.statusCode < 500) {
          break;
        }
        
        // Wait before retry (exponential backoff)
        if (attempt < this.config.retries) {
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
        }
      }
    }

    console.error(`❌ [DATA-SERVICE] All attempts failed for ${endpoint}:`, lastError);
    return null;
  }

  /**
   * Fetch business profile
   */
  async getBusinessProfile(businessId: string): Promise<EnhancedBusinessProfile | null> {
    return this.fetchWithRetry<EnhancedBusinessProfile>(
      `/api/v1/public/contractors/profile/${businessId}`
    );
  }

  /**
   * Fetch business services
   */
  async getBusinessServices(
    businessId: string, 
    options: { featuredOnly?: boolean; limit?: number } = {}
  ): Promise<EnhancedServiceItem[]> {
    const params = new URLSearchParams();
    if (options.featuredOnly) params.set('featured_only', 'true');
    if (options.limit) params.set('limit', String(options.limit));
    
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const result = await this.fetchWithRetry<EnhancedServiceItem[]>(
      `/api/v1/public/contractors/services/${businessId}${queryString}`
    );
    return result || [];
  }

  /**
   * Fetch business products
   */
  async getBusinessProducts(
    businessId: string,
    options: { featuredOnly?: boolean; limit?: number; category?: string } = {}
  ): Promise<EnhancedProductItem[]> {
    const params = new URLSearchParams();
    if (options.featuredOnly) params.set('featured_only', 'true');
    if (options.limit) params.set('limit', String(options.limit));
    if (options.category) params.set('category', options.category);
    
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const result = await this.fetchWithRetry<EnhancedProductItem[]>(
      `/api/v1/public/contractors/product-catalog/${businessId}${queryString}`
    );
    return result || [];
  }

  /**
   * Fetch business projects
   */
  async getBusinessProjects(
    businessId: string,
    options: { featuredOnly?: boolean; limit?: number; category?: string } = {}
  ): Promise<EnhancedProjectItem[]> {
    const params = new URLSearchParams();
    if (options.featuredOnly) params.set('featured_only', 'true');
    if (options.limit) params.set('limit', String(options.limit));
    if (options.category) params.set('category', options.category);
    
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const endpoint = options.featuredOnly ? 'featured-projects' : 'projects';
    const result = await this.fetchWithRetry<EnhancedProjectItem[]>(
      `/api/v1/public/contractors/${endpoint}/${businessId}${queryString}`
    );
    return result || [];
  }

  /**
   * Fetch business locations
   */
  async getBusinessLocations(businessId: string): Promise<EnhancedLocationItem[]> {
    const result = await this.fetchWithRetry<EnhancedLocationItem[]>(
      `/api/v1/public/contractors/locations/${businessId}`
    );
    return result || [];
  }

  /**
   * Fetch service categories
   */
  async getServiceCategories(businessId: string): Promise<EnhancedServiceCategory[]> {
    const result = await this.fetchWithRetry<EnhancedServiceCategory[]>(
      `/api/v1/public/contractors/service-categories/${businessId}`
    );
    return result || [];
  }

  /**
   * Fetch membership plans
   */
  async getMembershipPlans(businessId: string): Promise<MembershipPlan[]> {
    const result = await this.fetchWithRetry<MembershipPlan[]>(
      `/api/v1/public/contractors/membership-plans/${businessId}`
    );
    return result || [];
  }

  /**
   * Fetch single product by slug
   */
  async getProduct(businessId: string, productSlug: string): Promise<EnhancedProductItem | null> {
    return this.fetchWithRetry<EnhancedProductItem>(
      `/api/v1/public/contractors/products/${businessId}/${productSlug}`
    );
  }

  /**
   * Fetch single project by slug
   */
  async getProject(businessId: string, projectSlug: string): Promise<EnhancedProjectItem | null> {
    return this.fetchWithRetry<EnhancedProjectItem>(
      `/api/v1/public/contractors/projects/${businessId}/${projectSlug}`
    );
  }

  /**
   * Load comprehensive business data with parallel requests
   */
  async loadBusinessData(
    businessId: string, 
    options: DataOptions = {}
  ): Promise<EnhancedHomepageData> {
    console.log('🔄 [DATA-SERVICE] Loading comprehensive business data for:', businessId);
    
    const startTime = Date.now();
    const promises: Promise<any>[] = [this.getBusinessProfile(businessId)];
    
    // Build parallel requests based on options
    if (options.includeServices !== false) {
      promises.push(this.getBusinessServices(businessId, {
        featuredOnly: options.featuredOnly,
        limit: options.limit
      }));
    }
    
    if (options.includeProducts) {
      promises.push(this.getBusinessProducts(businessId, {
        featuredOnly: options.featuredOnly,
        limit: options.limit || 6
      }));
    }
    
    if (options.includeProjects) {
      promises.push(this.getBusinessProjects(businessId, {
        featuredOnly: options.featuredOnly,
        limit: options.limit || 6
      }));
    }
    
    if (options.includeLocations) {
      promises.push(this.getBusinessLocations(businessId));
    }
    
    if (options.includeCategories) {
      promises.push(this.getServiceCategories(businessId));
    }

    try {
      const results = await Promise.all(promises);
      const loadTime = Date.now() - startTime;
      
      const data: EnhancedHomepageData = {
        profile: results[0] as EnhancedBusinessProfile | null,
        services: (options.includeServices !== false ? results[1] : []) as EnhancedServiceItem[],
        products: (options.includeProducts ? results[promises.indexOf(this.getBusinessProducts(businessId, {}))] : []) as EnhancedProductItem[],
        projects: (options.includeProjects ? results[promises.findIndex((_, i) => i > 1 && options.includeProjects)] : []) as EnhancedProjectItem[],
        diagnostics: {
          backendUrl: this.baseUrl || '',
          profileOk: !!results[0],
          servicesOk: options.includeServices !== false ? Array.isArray(results[1]) : true,
          productsOk: options.includeProducts ? Array.isArray(results[2]) : true,
          projectsOk: options.includeProjects ? Array.isArray(results[3]) : true,
          timestamp: Date.now(),
          environment: process.env.NODE_ENV || 'development'
        } as DiagnosticsInfo
      };

      console.log(`✅ [DATA-SERVICE] Business data loaded in ${loadTime}ms:`, {
        profile: !!data.profile,
        services: data.services.length,
        products: data.products.length,
        projects: data.projects.length
      });

      return data;
    } catch (error) {
      console.error('❌ [DATA-SERVICE] Failed to load business data:', error);
      
      return {
        profile: null,
        services: [],
        products: [],
        projects: [],
        diagnostics: {
          backendUrl: this.baseUrl || '',
          profileOk: false,
          servicesOk: false,
          productsOk: false,
          projectsOk: false,
          timestamp: Date.now(),
          environment: process.env.NODE_ENV || 'development'
        }
      };
    }
  }

  /**
   * Load homepage data (convenience method)
   */
  async loadHomepageData(businessId: string): Promise<EnhancedHomepageData> {
    return this.loadBusinessData(businessId, {
      includeServices: true,
      includeProducts: true,
      includeProjects: true,
      featuredOnly: true,
      limit: 6
    });
  }

  /**
   * Health check for the service
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.initialize();
      const response = await fetch(`${this.baseUrl}/api/v1/health`, {
        method: 'HEAD',
        signal: AbortSignal.timeout(5000)
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Singleton instance
let serviceInstance: BusinessDataService | null = null;

/**
 * Get the global service instance
 */
export function getBusinessDataService(config?: Partial<ServiceConfig>): BusinessDataService {
  if (!serviceInstance) {
    serviceInstance = new BusinessDataService(config);
  }
  return serviceInstance;
}

/**
 * Create a new service instance (useful for testing)
 */
export function createBusinessDataService(config?: Partial<ServiceConfig>): BusinessDataService {
  return new BusinessDataService(config);
}

// Legacy compatibility - replace existing data-fetchers
export const {
  loadHomepageData,
  getBusinessProfile: fetchBusinessProfile,
  getBusinessServices: fetchBusinessServices,
  getBusinessProducts: fetchFeaturedProducts,
  getBusinessProjects: fetchFeaturedProjects,
  getBusinessLocations: fetchBusinessLocations,
  getServiceCategories: fetchServiceCategories
} = getBusinessDataService();
