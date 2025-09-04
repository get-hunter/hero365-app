import { MetadataRoute } from 'next'
import { getSitemapManifest } from '@/lib/artifact-api'

// Ensure edge runtime where globalThis/self is available during build and runtime
export const runtime = 'nodejs'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://elitehvacaustin.com'
  const businessId = process.env.NEXT_PUBLIC_BUSINESS_ID
  
  // For development and SSR compatibility, always use fallback sitemap
  if (process.env.NODE_ENV === 'development' || !businessId) {
    console.log('Using fallback sitemap for development/missing business ID')
    return getFallbackSitemap(baseUrl)
  }
  
  try {
    // Get sitemap manifest from artifact API
    const manifest = await getSitemapManifest(businessId)
    
    if (!manifest) {
      console.warn('No sitemap manifest found, using fallback')
      return getFallbackSitemap(baseUrl)
    }

    // Convert artifact entries to Next.js sitemap format
    const sitemapEntries: MetadataRoute.Sitemap = []

    // Add service pages from artifacts
    if (manifest.service_pages) {
      manifest.service_pages.forEach(entry => {
        sitemapEntries.push({
          url: `${baseUrl}${entry.loc}`,
          lastModified: new Date(entry.lastmod),
          changeFrequency: entry.changefreq as any,
          priority: entry.priority,
        })
      })
    }

    // Add location pages from artifacts
    if (manifest.location_pages) {
      manifest.location_pages.forEach(entry => {
        sitemapEntries.push({
          url: `${baseUrl}${entry.loc}`,
          lastModified: new Date(entry.lastmod),
          changeFrequency: entry.changefreq as any,
          priority: entry.priority,
        })
      })
    }

    // Add project pages from artifacts
    if (manifest.project_pages) {
      manifest.project_pages.forEach(entry => {
        sitemapEntries.push({
          url: `${baseUrl}${entry.loc}`,
          lastModified: new Date(entry.lastmod),
          changeFrequency: entry.changefreq as any,
          priority: entry.priority,
        })
      })
    }

    // Add static pages
    const staticPages: MetadataRoute.Sitemap = [
      {
        url: baseUrl,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 1,
      },
      {
        url: `${baseUrl}/about`,
        lastModified: new Date(),
        changeFrequency: 'monthly',
        priority: 0.8,
      },
      {
        url: `${baseUrl}/contact`,
        lastModified: new Date(),
        changeFrequency: 'monthly',
        priority: 0.8,
      },
      {
        url: `${baseUrl}/services`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.9,
      },
    ]

    console.log(`Generated sitemap with ${sitemapEntries.length} artifact pages and ${staticPages.length} static pages`)
    
    return [...staticPages, ...sitemapEntries]
    
  } catch (error) {
    console.error('Error generating sitemap from artifacts:', error)
    return getFallbackSitemap(baseUrl)
  }
}

function getFallbackSitemap(baseUrl: string): MetadataRoute.Sitemap {
  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1,
    },
    {
      url: `${baseUrl}/about`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/contact`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/services`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.9,
    },
  ]
}

function getChangeFrequency(pageType: string): 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never' {
  switch (pageType) {
    case 'service':
    case 'service_location':
      return 'weekly'
    case 'location':
      return 'monthly'
    case 'emergency_service':
      return 'daily'
    default:
      return 'monthly'
  }
}

function getPriority(url: string, pageType: string): number {
  // Homepage
  if (url === '/') return 1.0
  
  // High-value service pages
  if (pageType === 'service' && url.includes('/services/')) {
    // Core services get higher priority
    const coreServices = ['hvac-repair', 'ac-repair', 'heating-repair', 'ac-installation']
    const serviceName = url.split('/services/')[1]?.split('/')[0]
    if (coreServices.includes(serviceName)) return 0.9
    return 0.8
  }
  
  // Service + location combinations (money pages)
  if (pageType === 'service_location') return 0.85
  
  // Location pages
  if (pageType === 'location') return 0.7
  
  // Emergency services
  if (pageType === 'emergency_service') return 0.75
  
  // Default
  return 0.6
}
