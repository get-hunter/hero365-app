/**
 * Server-only navigation data loader
 */

import { getBackendUrl, getDefaultHeaders } from '../config/api-config';

// Cache for navigation data
let navigationCache: {
  serviceCategories?: any[];
  locations?: any[];
  lastUpdated?: number;
} = {};

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

/**
 * Load navigation data from backend or generated content
 */
export async function loadNavigationData() {
  const now = Date.now();
  
  // Return cached data if still valid
  if (navigationCache.lastUpdated && (now - navigationCache.lastUpdated) < CACHE_DURATION) {
    return {
      serviceCategories: navigationCache.serviceCategories || [],
      locations: navigationCache.locations || []
    };
  }

  try {
    // Try to load from generated content first
    const { getBusinessNavigation } = await import('../generated/seo-pages.js');
    const navigation = getBusinessNavigation();
    
    if (navigation && navigation.services && navigation.locations) {
      navigationCache = {
        serviceCategories: navigation.services,
        locations: navigation.locations,
        lastUpdated: now
      };
      
      return {
        serviceCategories: navigation.services,
        locations: navigation.locations
      };
    }
  } catch (error) {
    console.log('Generated navigation not available, using fallback');
  }

  // Fallback to basic navigation
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
    serviceCategories: fallbackNavigation.serviceCategories,
    locations: fallbackNavigation.locations,
    lastUpdated: now
  };

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


