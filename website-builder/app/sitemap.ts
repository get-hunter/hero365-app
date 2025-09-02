import { MetadataRoute } from 'next'
import { getAllSEOPages } from '@/lib/seo-data'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://elitehvacaustin.com'
  
  try {
    // Get all SEO pages
    const allPages = await getAllSEOPages()
    
    // Convert pages to sitemap entries
    const sitemapEntries: MetadataRoute.Sitemap = Object.entries(allPages).map(([url, pageData]) => ({
      url: `${baseUrl}${url}`,
      lastModified: pageData.created_at ? new Date(pageData.created_at) : new Date(),
      changeFrequency: getChangeFrequency(pageData.page_type),
      priority: getPriority(url, pageData.page_type),
    }))

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
    ]

    return [...staticPages, ...sitemapEntries]
  } catch (error) {
    console.error('Error generating sitemap:', error)
    
    // Fallback sitemap
    return [
      {
        url: baseUrl,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 1,
      },
    ]
  }
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
