/**
 * Server-Side Data Fetchers (Legacy Compatibility)
 * 
 * @deprecated Use BusinessDataService instead for new code
 * This file provides backward compatibility for existing code
 */

import { getBusinessDataService } from '../services/business-data-service';
import type {
  BusinessProfile,
  ServiceItem,
  ProductItem,
  ProjectItem,
  HomepageData,
  ServiceCategory,
  LocationItem
} from '@/lib/shared/types/api-responses';
import type { EnhancedHomepageData } from '@/lib/shared/types/api-responses';

// Get the service instance
const dataService = getBusinessDataService();

/**
 * Generic JSON fetcher with error handling
 * @deprecated Use BusinessDataService instead
 */
export async function serverFetchJson<T>(endpointPath: string): Promise<T | null> {
  console.warn('serverFetchJson is deprecated. Use BusinessDataService instead.');
  // This function is deprecated and should not be used
  return null;
}

/**
 * Fetch business profile
 * @deprecated Use dataService.getBusinessProfile() instead
 */
export async function fetchBusinessProfile(businessId: string): Promise<BusinessProfile | null> {
  return dataService.getBusinessProfile(businessId) as any;
}

/**
 * Fetch business services
 * @deprecated Use dataService.getBusinessServices() instead
 */
export async function fetchBusinessServices(businessId: string): Promise<ServiceItem[]> {
  return dataService.getBusinessServices(businessId) as any;
}

/**
 * Fetch featured products
 */
export async function fetchFeaturedProducts(
  businessId: string, 
  limit: number = 6
): Promise<ProductItem[]> {
  const result = await serverFetchJson<ProductItem[]>(
    `/api/v1/public/contractors/products/${businessId}?featured_only=true&limit=${limit}`
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
    `/api/v1/public/contractors/products/${businessId}`
  );
  return result || [];
}

/**
 * Fetch all projects
 */
export async function fetchAllProjects(businessId: string): Promise<ProjectItem[]> {
  const result = await serverFetchJson<ProjectItem[]>(
    `/api/v1/public/contractors/featured-projects/${businessId}`
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
 * @deprecated Use dataService.loadHomepageData() instead
 */
export async function loadHomepageData(businessId: string): Promise<EnhancedHomepageData> {
  return dataService.loadHomepageData(businessId);
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
  let servicesIndex = -1;
  let productsIndex = -1;
  let projectsIndex = -1;
  let locationsIndex = -1;
  let categoriesIndex = -1;
  
  if (options.includeServices) {
    servicesIndex = promises.length;
    promises.push(fetchBusinessServices(businessId));
  }
  if (options.includeProducts) {
    productsIndex = promises.length;
    promises.push(fetchAllProducts(businessId));
  }
  if (options.includeProjects) {
    projectsIndex = promises.length;
    promises.push(fetchAllProjects(businessId));
  }
  if (options.includeLocations) {
    locationsIndex = promises.length;
    promises.push(fetchBusinessLocations(businessId));
  }
  if (options.includeCategories) {
    categoriesIndex = promises.length;
    promises.push(fetchServiceCategories(businessId));
  }

  const results = await Promise.all(promises);
  
  return {
    profile: results[0] as BusinessProfile | null,
    services: servicesIndex >= 0 ? results[servicesIndex] as ServiceItem[] : [],
    products: productsIndex >= 0 ? results[productsIndex] as ProductItem[] : [],
    projects: projectsIndex >= 0 ? results[projectsIndex] as ProjectItem[] : [],
    locations: locationsIndex >= 0 ? results[locationsIndex] as LocationItem[] : [],
    categories: categoriesIndex >= 0 ? results[categoriesIndex] as ServiceCategory[] : [],
  };
}
