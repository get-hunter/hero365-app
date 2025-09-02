interface SEOPageData {
  title: string
  meta_description: string
  h1_heading: string
  content: string
  schema_markup: any
  target_keywords: string[]
  page_url: string
  generation_method: 'template' | 'llm' | 'fallback'
  page_type: string
  word_count: number
  created_at: string
}

interface ContentBlocks {
  content_blocks: Array<{
    type: string
    order: number
    content: any
    visible: boolean
  }>
}

interface BusinessConfig {
  businessId: string
  businessName: string
  phone: string
  email: string
  address: string
  website: string
  serviceAreas: string[]
  trades: string[]
}

export function generateJSONLD(
  pageData: SEOPageData, 
  contentBlocks: ContentBlocks | null,
  businessConfig: BusinessConfig
): any[] {
  const jsonLdItems: any[] = []

  // Base LocalBusiness schema
  const localBusiness = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": `${businessConfig.website}#business`,
    "name": businessConfig.businessName,
    "description": pageData.meta_description,
    "url": businessConfig.website,
    "telephone": businessConfig.phone,
    "email": businessConfig.email,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": businessConfig.address.split(',')[0],
      "addressLocality": "Austin",
      "addressRegion": "TX",
      "addressCountry": "US"
    },
    "areaServed": businessConfig.serviceAreas.map(area => ({
      "@type": "City",
      "name": area
    })),
    "openingHours": "Mo-Su 00:00-23:59", // 24/7
    "priceRange": "$$",
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.8",
      "reviewCount": "150",
      "bestRating": "5",
      "worstRating": "1"
    }
  }

  jsonLdItems.push(localBusiness)

  // Service-specific schema
  if (pageData.page_type === 'service' || pageData.page_type === 'service_location') {
    const serviceName = extractServiceName(pageData.page_url, pageData.h1_heading)
    const location = extractLocation(pageData.page_url)
    
    const service = {
      "@context": "https://schema.org",
      "@type": "Service",
      "@id": `${businessConfig.website}${pageData.page_url}#service`,
      "name": serviceName,
      "description": pageData.meta_description,
      "provider": {
        "@id": `${businessConfig.website}#business`
      },
      "areaServed": location ? [{
        "@type": "City",
        "name": location
      }] : businessConfig.serviceAreas.map(area => ({
        "@type": "City", 
        "name": area
      })),
      "offers": {
        "@type": "Offer",
        "availability": "https://schema.org/InStock",
        "priceRange": "$$",
        "validFrom": new Date().toISOString(),
        "description": `Professional ${serviceName.toLowerCase()} services`
      }
    }

    jsonLdItems.push(service)
  }

  // FAQ schema from content blocks
  if (contentBlocks?.content_blocks) {
    const faqBlocks = contentBlocks.content_blocks.filter(block => 
      block.type === 'faq' && block.content?.faqs?.length > 0
    )

    faqBlocks.forEach(faqBlock => {
      const faqSchema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faqBlock.content.faqs.map((faq: any) => ({
          "@type": "Question",
          "name": faq.question,
          "acceptedAnswer": {
            "@type": "Answer",
            "text": faq.answer
          }
        }))
      }

      jsonLdItems.push(faqSchema)
    })
  }

  // Breadcrumb schema
  const breadcrumbs = generateBreadcrumbs(pageData.page_url, businessConfig.website)
  if (breadcrumbs.itemListElement.length > 1) {
    jsonLdItems.push(breadcrumbs)
  }

  // WebPage schema
  const webPage = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "@id": `${businessConfig.website}${pageData.page_url}`,
    "url": `${businessConfig.website}${pageData.page_url}`,
    "name": pageData.title,
    "description": pageData.meta_description,
    "isPartOf": {
      "@type": "WebSite",
      "@id": `${businessConfig.website}#website`,
      "url": businessConfig.website,
      "name": businessConfig.businessName
    },
    "about": {
      "@id": `${businessConfig.website}#business`
    },
    "datePublished": pageData.created_at || new Date().toISOString(),
    "dateModified": pageData.created_at || new Date().toISOString()
  }

  jsonLdItems.push(webPage)

  return jsonLdItems
}

function extractServiceName(pageUrl: string, h1Heading: string): string {
  // Extract service name from URL or heading
  if (pageUrl.includes('/services/')) {
    const servicePart = pageUrl.split('/services/')[1]?.split('/')[0]
    if (servicePart) {
      return servicePart.replace(/-/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase())
    }
  }
  
  return h1Heading
}

function extractLocation(pageUrl: string): string | null {
  // Extract location from service/location URLs
  const parts = pageUrl.split('/')
  if (parts.length >= 4 && parts[1] === 'services') {
    const locationPart = parts[3]
    if (locationPart && locationPart.includes('-')) {
      const [city, state] = locationPart.split('-')
      return `${city.charAt(0).toUpperCase() + city.slice(1)}, ${state.toUpperCase()}`
    }
  }
  
  return null
}

function generateBreadcrumbs(pageUrl: string, baseUrl: string) {
  const parts = pageUrl.split('/').filter(Boolean)
  const breadcrumbItems = [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": baseUrl
    }
  ]

  let currentPath = ''
  parts.forEach((part, index) => {
    currentPath += `/${part}`
    const name = part.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    
    breadcrumbItems.push({
      "@type": "ListItem",
      "position": index + 2,
      "name": name,
      "item": `${baseUrl}${currentPath}`
    })
  })

  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": breadcrumbItems
  }
}
