/**
 * Server-Side Data Fetchers
 * 
 * Reusable data fetching utilities for Hero365 backend API
 * These handle runtime configuration, error handling, and type safety
 */

import { getRuntimeConfig } from './runtime-config';
import { getDefaultHeaders } from '@/lib/shared/config/api-config';
import type {
  BusinessProfile,
  ServiceItem,
  ProductItem,
  ProjectItem,
  HomepageData,
  ServiceCategory,
  LocationItem
} from '@/lib/shared/types/api-responses';

/**
 * Generic JSON fetcher with error handling
 */
export async function serverFetchJson<T>(endpointPath: string): Promise<T | null> {
  try {
    const config = await getRuntimeConfig();
    const url = `${config.apiUrl}${endpointPath}`;
    const response = await fetch(url, {
      headers: getDefaultHeaders(),
      cache: 'no-store',
      // Abort in 8s to avoid long hangs
      signal: AbortSignal.timeout ? AbortSignal.timeout(8000) : undefined,
    });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch (err) {
    console.warn('serverFetchJson error:', endpointPath, err);
    return null;
  }
}

/**
 * Fetch business profile
 */
export async function fetchBusinessProfile(businessId: string): Promise<BusinessProfile | null> {
  return serverFetchJson<BusinessProfile>(`/api/v1/public/contractors/profile/${businessId}`);
}

/**
 * Fetch business services
 */
export async function fetchBusinessServices(businessId: string): Promise<ServiceItem[]> {
  const result = await serverFetchJson<ServiceItem[]>(`/api/v1/public/contractors/services/${businessId}`);
  return result || [];
}

/**
 * Fetch featured products
 */
export async function fetchFeaturedProducts(
  businessId: string, 
  limit: number = 6
): Promise<ProductItem[]> {
  const result = await serverFetchJson<ProductItem[]>(
    `/api/v1/public/contractors/product-catalog/${businessId}?featured_only=true&limit=${limit}`
  );
  return result || [];
}

/**
 * Fetch featured projects
 */
export async function fetchFeaturedProjects(
  businessId: string,
  limit: number = 6
): Promise<ProjectItem[]> {
  const result = await serverFetchJson<ProjectItem[]>(
    `/api/v1/public/contractors/featured-projects/${businessId}?featured_only=true&limit=${limit}`
  );
  return result || [];
}

/**
 * Fetch all products
 */
export async function fetchAllProducts(businessId: string): Promise<ProductItem[]> {
  const result = await serverFetchJson<ProductItem[]>(
    `/api/v1/public/contractors/product-catalog/${businessId}`
  );
  return result || [];
}

/**
 * Fetch all projects
 */
export async function fetchAllProjects(businessId: string): Promise<ProjectItem[]> {
  const result = await serverFetchJson<ProjectItem[]>(
    `/api/v1/public/contractors/projects/${businessId}`
  );
  return result || [];
}

/**
 * Fetch service categories
 */
export async function fetchServiceCategories(businessId: string): Promise<ServiceCategory[]> {
  const result = await serverFetchJson<ServiceCategory[]>(
    `/api/v1/public/contractors/service-categories/${businessId}`
  );
  return result || [];
}

/**
 * Fetch business locations
 */
export async function fetchBusinessLocations(businessId: string): Promise<LocationItem[]> {
  const result = await serverFetchJson<LocationItem[]>(
    `/api/v1/public/contractors/locations/${businessId}`
  );
  return result || [];
}

/**
 * Load all homepage data in parallel
 */
export async function loadHomepageData(businessId: string): Promise<HomepageData> {
  try {
    console.log('🔄 [SERVER] Loading business data for:', businessId);

    const config = await getRuntimeConfig();
    const backendUrl = config.apiUrl;
    console.log('🔄 [SERVER] Runtime config:', { environment: config.environment, backendUrl });

    const [profile, services, products, projects] = await Promise.all([
      fetchBusinessProfile(businessId),
      fetchBusinessServices(businessId),
      fetchFeaturedProducts(businessId, 6),
      fetchFeaturedProjects(businessId, 6),
    ]);

    const profileOk = !!profile;
    const servicesOk = Array.isArray(services);
    const productsOk = Array.isArray(products);
    const projectsOk = Array.isArray(projects);

    if (profileOk) {
      console.log('✅ [SERVER] Profile loaded:', profile.business_name);
    }
    if (servicesOk) {
      console.log('✅ [SERVER] Services loaded:', services.length, 'items');
    }
    if (productsOk) {
      console.log('✅ [SERVER] Products loaded:', products.length, 'items');
    }
    if (projectsOk) {
      console.log('✅ [SERVER] Projects loaded:', projects.length, 'items');
    }

    return {
      profile,
      services,
      products,
      projects,
      diagnostics: {
        backendUrl,
        profileOk,
        servicesOk,
        productsOk,
        projectsOk,
      },
    };
  } catch (error) {
    console.error('⚠️ [SERVER] Failed to load business data:', error);
    return { profile: null, services: [], products: [], projects: [] };
  }
}

/**
 * Load data for a specific page type
 */
export interface PageDataOptions {
  includeServices?: boolean;
  includeProducts?: boolean;
  includeProjects?: boolean;
  includeLocations?: boolean;
  includeCategories?: boolean;
}

export async function loadPageData(
  businessId: string,
  options: PageDataOptions = {}
) {
  const promises: Promise<any>[] = [fetchBusinessProfile(businessId)];
  
  if (options.includeServices) {
    promises.push(fetchBusinessServices(businessId));
  }
  if (options.includeProducts) {
    promises.push(fetchAllProducts(businessId));
  }
  if (options.includeProjects) {
    promises.push(fetchAllProjects(businessId));
  }
  if (options.includeLocations) {
    promises.push(fetchBusinessLocations(businessId));
  }
  if (options.includeCategories) {
    promises.push(fetchServiceCategories(businessId));
  }

  const results = await Promise.all(promises);
  
  return {
    profile: results[0] as BusinessProfile | null,
    services: options.includeServices ? results[promises.length > 1 ? 1 : 0] as ServiceItem[] : [],
    products: options.includeProducts ? results[promises.findIndex(p => p === fetchAllProducts(businessId))] as ProductItem[] : [],
    projects: options.includeProjects ? results[promises.findIndex(p => p === fetchAllProjects(businessId))] as ProjectItem[] : [],
    locations: options.includeLocations ? results[promises.findIndex(p => p === fetchBusinessLocations(businessId))] as LocationItem[] : [],
    categories: options.includeCategories ? results[promises.findIndex(p => p === fetchServiceCategories(businessId))] as ServiceCategory[] : [],
  };
}
