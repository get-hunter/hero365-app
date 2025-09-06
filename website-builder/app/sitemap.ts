import { MetadataRoute } from 'next'
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver'
import { headers } from 'next/headers'
import { getBackendUrl, getDefaultHeaders } from '@/lib/shared/config/api-config'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Get business ID from host for multi-tenant support
  const resolution = await getBusinessIdFromHost();
  const businessId = resolution.businessId;
  
  // Get the current host to build the base URL
  const headersList = await headers();
  const host = headersList.get('host') || 'localhost:3000';
  const protocol = host.includes('localhost') ? 'http' : 'https';
  const baseUrl = `${protocol}://${host}`;
  
  try {
    // Use new business-specific service and location endpoints
    const backendUrl = getBackendUrl();
    const [servicesRes, locationsRes] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/contractors/${businessId}/service-slugs`, { 
        headers: getDefaultHeaders(),
        next: { revalidate: 3600 } // Cache for 1 hour
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/${businessId}/location-slugs`, { 
        headers: getDefaultHeaders(),
        next: { revalidate: 3600 } // Cache for 1 hour
      })
    ]);

    const serviceSlugs = await servicesRes.json();
    const locationSlugs = await locationsRes.json();

    const entries: MetadataRoute.Sitemap = [];
    
    // Log sitemap generation for this business
    console.log(`✅ [SITEMAP] Generating for business: ${businessId}`);

    // Homepage - highest priority
    entries.push({
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1.0,
    });

    // Service hub page
    entries.push({
      url: `${baseUrl}/services`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.9,
    });

    // Location hub page
    entries.push({
      url: `${baseUrl}/locations`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.9,
    });

    // Individual service pages (without location)
    for (const serviceSlug of serviceSlugs) {
      entries.push({
        url: `${baseUrl}/services/${serviceSlug}`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.8,
      });
    }

    // Service + Location combination pages
    for (const serviceSlug of serviceSlugs) {
      for (const locationSlug of locationSlugs) {
        entries.push({
          url: `${baseUrl}/services/${serviceSlug}/${locationSlug}`,
          lastModified: new Date(),
          changeFrequency: 'weekly',
          priority: 0.7,
        });
      }
    }

    // About, Contact, Privacy, Terms pages
    const staticPages = ['/about', '/contact', '/privacy', '/terms'];
    for (const page of staticPages) {
      entries.push({
        url: `${baseUrl}${page}`,
        lastModified: new Date(),
        changeFrequency: 'monthly',
        priority: 0.5,
      });
    }

    console.log(`✅ [SITEMAP] Generated ${entries.length} URLs (${serviceSlugs.length} services × ${locationSlugs.length} locations)`);
    return entries;

  } catch (error) {
    console.error('❌ [SITEMAP] Failed to generate sitemap:', error);
    
    // Return minimal sitemap on error
    return [
      {
        url: baseUrl,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 1.0,
      }
    ];
  }
}