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
  // Delegate to BusinessDataService for backward compatibility if possible
  try {
    // We do not expose a raw fetch by endpoint on the service; callers should
    // migrate to concrete methods. For safety, return null here to avoid
    // accidental network calls with unknown paths.
    return null;
  } catch {
    return null;
  }
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
  // Use new service method
  return (await dataService.getBusinessProducts(businessId, { featuredOnly: true, limit })) as any;
}

/**
 * Fetch featured projects
 */
export async function fetchFeaturedProjects(
  businessId: string,
  limit: number = 6
): Promise<ProjectItem[]> {
  return (await dataService.getBusinessProjects(businessId, { featuredOnly: true, limit })) as any;
}

/**
 * Fetch all products
 */
export async function fetchAllProducts(businessId: string): Promise<ProductItem[]> {
  // Fetch full catalog from new endpoint
  return (await dataService.getBusinessProducts(businessId)) as any;
}

/**
 * Fetch all projects
 */
export async function fetchAllProjects(businessId: string): Promise<ProjectItem[]> {
  return (await dataService.getBusinessProjects(businessId)) as any;
}

/**
 * Fetch service categories
 */
export async function fetchServiceCategories(businessId: string): Promise<ServiceCategory[]> {
  return (await dataService.getServiceCategories(businessId)) as any;
}

/**
 * Fetch business locations
 */
export async function fetchBusinessLocations(businessId: string): Promise<LocationItem[]> {
  return (await dataService.getBusinessLocations(businessId)) as any;
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
