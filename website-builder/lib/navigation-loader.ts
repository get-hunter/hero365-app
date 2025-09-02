/**
 * Navigation data loader utility
 * Loads service categories and locations from generated SEO data
 */

interface NavigationService {
  name: string;
  slug: string;
  url: string;
  description: string;
}

interface NavigationCategory {
  name: string;
  description: string;
  slug: string;
  services: NavigationService[];
}

interface NavigationLocation {
  slug: string;
  name: string;
}

interface NavigationData {
  categories: NavigationCategory[];
  locations: NavigationLocation[];
  services: NavigationService[];
}

let cachedNavigation: NavigationData | null = null;

/**
 * Load navigation data from generated SEO pages
 */
export async function loadNavigationData(): Promise<NavigationData> {
  if (cachedNavigation) {
    return cachedNavigation;
  }

  try {
    // Try to load from generated navigation data
    const { getNavigation, getNavigationCategories } = await import('./generated/seo-pages.js');
    const navigation = getNavigation();
    const categories = getNavigationCategories();
    
    cachedNavigation = {
      categories: categories || [],
      locations: navigation?.locations || [],
      services: navigation?.services || []
    };
    
    return cachedNavigation;
  } catch (error) {
    console.log('Navigation data not available, using fallback');
    
    // Fallback navigation data
    cachedNavigation = {
      categories: [
        {
          name: "Air Conditioning",
          description: "Complete AC services",
          slug: "air-conditioning",
          services: [
            { name: "AC Installation", slug: "ac-installation", url: "/services/ac-installation", description: "Professional AC installation" },
            { name: "AC Repair", slug: "ac-repair", url: "/services/ac-repair", description: "Emergency AC repair" },
            { name: "Heat Pump Service", slug: "heat-pump-service", url: "/services/heat-pump-service", description: "Heat pump maintenance" }
          ]
        },
        {
          name: "Heating",
          description: "Heating system services",
          slug: "heating",
          services: [
            { name: "Furnace Repair", slug: "furnace-repair", url: "/services/furnace-repair", description: "Furnace repair and maintenance" },
            { name: "Heating Installation", slug: "heating-installation", url: "/services/heating-installation", description: "New heating systems" }
          ]
        },
        {
          name: "Electrical",
          description: "Electrical services",
          slug: "electrical",
          services: [
            { name: "Electrical Repair", slug: "electrical-repair", url: "/services/electrical-repair", description: "Emergency electrical repair" },
            { name: "Panel Upgrades", slug: "panel-upgrades", url: "/services/panel-upgrades", description: "Electrical panel upgrades" }
          ]
        },
        {
          name: "Plumbing",
          description: "Plumbing services",
          slug: "plumbing",
          services: [
            { name: "Plumbing Repair", slug: "plumbing-repair", url: "/services/plumbing-repair", description: "Emergency plumbing repair" },
            { name: "Water Heater Service", slug: "water-heater-service", url: "/services/water-heater-service", description: "Water heater maintenance" }
          ]
        }
      ],
      locations: [
        { slug: "austin-tx", name: "Austin TX" },
        { slug: "round-rock-tx", name: "Round Rock TX" }
      ],
      services: []
    };
    
    return cachedNavigation;
  }
}

/**
 * Get service categories for footer/navigation
 * Transforms to format expected by ProfessionalFooter
 */
export async function getServiceCategoriesForFooter() {
  const navigation = await loadNavigationData();
  
  return navigation.categories.map(category => ({
    id: category.slug,
    name: category.name,
    slug: category.slug,
    description: category.description,
    services: category.services.slice(0, 6) // Limit for footer display
  }));
}

/**
 * Get all services flattened for SEO/linking
 */
export async function getAllServices(): Promise<NavigationService[]> {
  const navigation = await loadNavigationData();
  
  // Flatten all services from categories
  const allServices: NavigationService[] = [];
  navigation.categories.forEach(category => {
    allServices.push(...category.services);
  });
  
  return allServices;
}

/**
 * Get locations for footer/navigation
 */
export async function getLocations(): Promise<NavigationLocation[]> {
  const navigation = await loadNavigationData();
  return navigation.locations;
}

/**
 * Clear cached navigation data (useful for testing/development)
 */
export function clearNavigationCache(): void {
  cachedNavigation = null;
}
