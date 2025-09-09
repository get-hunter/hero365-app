/**
 * Server-only navigation data loader
 */

import { getBackendUrl, getDefaultHeaders } from '../shared/config/api-config';
import { getBusinessIdFromHost } from './host-business-resolver';

// Cache for navigation data
let navigationCache: {
  businessId?: string;
  serviceCategories?: any[];
  locations?: any[];
  lastUpdated?: number;
} = {};

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

interface NavigationData {
  serviceCategories: any[];
  locations: any[];
}

/**
 * Load navigation data from backend API
 */
export async function loadNavigationData(): Promise<NavigationData> {
  const { businessId } = await getBusinessIdFromHost();
  const now = Date.now();
  
  // Return cached data if still valid and for same business
  if (navigationCache.businessId === businessId && 
      navigationCache.lastUpdated && 
      (now - navigationCache.lastUpdated) < CACHE_DURATION) {
    return {
      serviceCategories: navigationCache.serviceCategories || [],
      locations: navigationCache.locations || []
    };
  }

  try {
    // Primary: Load from backend navigation API
    const backendUrl = getBackendUrl();
    const navigationUrl = `${backendUrl}/api/v1/public/contractors/${businessId}/navigation`;
    
    console.log(`🔍 [NAV] Fetching navigation data from: ${navigationUrl}`);
    
    const response = await fetch(navigationUrl, {
      headers: getDefaultHeaders(),
      next: { revalidate: 300 } // Cache for 5 minutes
    });
    
    if (response.ok) {
      const navigationData = await response.json();
      
      // Build flat service list for grouping in the header component
      const rawServices = navigationData.services || [];
      let flatServices = rawServices
        .map((svc: any) => {
          const name = svc.name || svc.service_name;
          const slug = svc.canonical_slug || svc.slug;
          const href = svc.href || (slug ? `/services/${slug}` : undefined);
          if (!name || !href) return null;
          return {
            name,
            description: `Professional ${String(name).toLowerCase()} services`,
            href,
            is_emergency: svc.is_emergency,
            is_featured: svc.is_featured,
            trade_slug: svc.trade_slug,
            category: svc.category_name || svc.category || null,
            category_slug: svc.category_slug || null
          };
        })
        .filter(Boolean);

      // Supplement with full services list to include secondary trades
      try {
        const fullRes = await fetch(`${backendUrl}/api/v1/public/contractors/${businessId}/services`, {
          headers: getDefaultHeaders(),
          next: { revalidate: 300 }
        });
        if (fullRes.ok) {
          const full = await fullRes.json();
          const extra = (full || []).map((svc: any) => {
            const name = svc.name || svc.service_name;
            const slug = svc.canonical_slug || svc.slug;
            const href = slug ? `/services/${slug}` : undefined;
            if (!name || !href) return null;
            return {
              name,
              description: `Professional ${String(name).toLowerCase()} services`,
              href,
              is_emergency: svc.is_emergency,
              is_featured: svc.is_featured,
              trade_slug: svc.trade_slug,
              category: svc.category_name || svc.category || null
            };
          }).filter(Boolean) as any[];

          // Deduplicate by href
          const seen = new Set(flatServices.map((s: any) => s.href));
          for (const item of extra) {
            if (!seen.has(item.href)) {
              seen.add(item.href);
              flatServices.push(item);
            }
          }
        }
      } catch (e) {
        console.warn('⚠️ [NAV] Supplement full services fetch failed:', e);
      }
      
      const locations = navigationData.locations?.map((location: any) => ({
        name: location.name,
        slug: location.location_slug,
        href: `/locations/${location.location_slug}`,
        is_primary: location.is_primary
      })) || [];
      
      navigationCache = {
        businessId,
        serviceCategories: flatServices as any[],
        locations,
        lastUpdated: now
      };
      
      console.log(`✅ [NAV] Loaded ${flatServices.length} services, ${locations.length} locations from API`);
      
      return {
        serviceCategories: flatServices as any[],
        locations
      };
    } else {
      console.warn(`⚠️ [NAV] API responded with ${response.status}, trying fallback`);
    }
  } catch (error) {
    console.warn('⚠️ [NAV] Backend API failed, trying generated content fallback:', error);
  }

  // Fallback 1: Try generated content
  try {
    const { getBusinessNavigation } = await import('../generated/seo-pages.js');
    const navigation = getBusinessNavigation();
    
    if (navigation && navigation.services && navigation.locations) {
      const serviceCategories = navigation.services.map((service: any) => ({
        name: service.name,
        slug: service.slug,
        href: `/services/${service.slug}`
      }));
      
      const locations = navigation.locations.map((location: any) => ({
        name: location.name,
        slug: location.slug,
        href: `/locations/${location.slug}`
      }));
      
      navigationCache = {
        businessId,
        serviceCategories,
        locations,
        lastUpdated: now
      };
      
      console.log('✅ [NAV] Loaded from generated content fallback');
      
      return {
        serviceCategories,
        locations
      };
    }
  } catch (error) {
    console.log('⚠️ [NAV] Generated navigation not available, using hardcoded fallback');
  }

  // Fallback 2: Hardcoded basic navigation
  const fallbackNavigation = {
    serviceCategories: [
      { name: 'AC Installation', slug: 'ac-installation', href: '/services/ac-installation' },
      { name: 'HVAC Repair', slug: 'hvac-repair', href: '/services/hvac-repair' },
      { name: 'Heating Installation', slug: 'heating-installation', href: '/services/heating-installation' }
    ],
    locations: [
      { name: 'Austin, TX', slug: 'austin-tx', href: '/locations/austin-tx' },
      { name: 'Round Rock, TX', slug: 'round-rock-tx', href: '/locations/round-rock-tx' },
      { name: 'Cedar Park, TX', slug: 'cedar-park-tx', href: '/locations/cedar-park-tx' }
    ]
  };

  navigationCache = {
    businessId,
    serviceCategories: fallbackNavigation.serviceCategories,
    locations: fallbackNavigation.locations,
    lastUpdated: now
  };

  console.log('⚠️ [NAV] Using hardcoded fallback navigation');
  return fallbackNavigation;
}

/**
 * Get service categories for footer navigation
 */
export async function getServiceCategoriesForFooter() {
  const { serviceCategories } = await loadNavigationData();
  return serviceCategories;
}

/**
 * Get all services
 */
export async function getAllServices() {
  const { serviceCategories } = await loadNavigationData();
  return serviceCategories;
}

/**
 * Get locations for navigation
 */
export async function getLocations() {
  const { locations } = await loadNavigationData();
  return locations;
}

/**
 * Clear navigation cache
 */
export function clearNavigationCache() {
  navigationCache = {};
}


