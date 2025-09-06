import { MetadataRoute } from 'next'
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver'
import { headers } from 'next/headers'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Get business ID from host for multi-tenant support
  const resolution = await getBusinessIdFromHost();
  const businessId = resolution.businessId;
  
  // Get the current host to build the base URL
  const headersList = headers();
  const host = headersList.get('host') || 'localhost:3000';
  const protocol = host.includes('localhost') ? 'http' : 'https';
  const baseUrl = `${protocol}://${host}`;
  
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  
  try {
    // Fetch business-specific data from backend
    const [servicesRes, locationsRes, businessRes] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/services/active`, { 
        next: { revalidate: 3600 } // Cache for 1 hour
      }),
      fetch(`${backendUrl}/api/v1/public/locations/active`, { 
        next: { revalidate: 3600 } // Cache for 1 hour
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/website/context/${businessId}`, {
        next: { revalidate: 3600 } // Cache for 1 hour
      })
    ])

    const services = await servicesRes.json()
    const locations = await locationsRes.json()
    const businessContext = await businessRes.json()

    const entries: MetadataRoute.Sitemap = []
    
    // Log sitemap generation for this business
    console.log(`✅ [SITEMAP] Generating for business: ${businessContext.business?.name || businessId}`)

    // Homepage - highest priority
    entries.push({
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1.0,
    })

    // Service hub page
    entries.push({
      url: `${baseUrl}/services`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.9,
    })

    // Location hub page
    entries.push({
      url: `${baseUrl}/locations`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.9,
    })

    // Individual service pages (without location)
    for (const service of services) {
      entries.push({
        url: `${baseUrl}/services/${service.slug}`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.8,
      })
    }

    // Service + Location combination pages
    for (const service of services) {
      for (const location of locations) {
        entries.push({
          url: `${baseUrl}/services/${service.slug}/${location.slug}`,
          lastModified: new Date(),
          changeFrequency: 'weekly',
          priority: 0.7,
        })
      }
    }

    // About, Contact, Privacy, Terms pages
    const staticPages = ['/about', '/contact', '/privacy', '/terms']
    for (const page of staticPages) {
      entries.push({
        url: `${baseUrl}${page}`,
        lastModified: new Date(),
        changeFrequency: 'monthly',
        priority: 0.5,
      })
    }

    console.log(`✅ [SITEMAP] Generated ${entries.length} URLs`)
    return entries

  } catch (error) {
    console.error('❌ [SITEMAP] Failed to generate sitemap:', error)
    
    // Return minimal sitemap on error
    return [
      {
        url: baseUrl,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 1.0,
      }
    ]
  }
}