/**
 * SEO Data Management
 * Handles dynamic SEO page data for the website builder
 */

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

// This would be populated by the SEO generator service
let seoPages: Record<string, SEOPageData> = {}

/**
 * Load SEO pages from generated content or fallback
 */
export async function loadSEOPages(businessId: string): Promise<void> {
  try {
    const isServerSide = typeof window === 'undefined'

    // Always try backend API first (both server and client)
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || (isServerSide ? 'http://127.0.0.1:8000' : window.location.origin)
      const response = await fetch(`${baseUrl}/api/v1/seo/pages/${businessId}`, {
        cache: 'no-store'
      })

      if (response.ok) {
        const data = await response.json()
        seoPages = data.pages || {}
        console.log('✅ [SEO] Loaded SEO pages from API:', Object.keys(seoPages).length, 'pages')
        return
      } else {
        console.log('⚠️ [SEO] API responded non-OK:', response.status)
      }
    } catch (apiError: any) {
      console.log('⚠️ [SEO] API call failed, will try generated content:', apiError?.message || apiError)
    }

    // Fallback: generated content (built files)
    try {
      const { getAllSEOPages } = await import('./generated/seo-pages.js')
      seoPages = getAllSEOPages()
      console.log('✅ [SEO] Loaded generated SEO pages:', Object.keys(seoPages).length, 'pages')
      return
    } catch (error: any) {
      console.log('⚠️ [SEO] Generated content not available, using demo data:', error?.message || error)
      seoPages = generateDemoSEOPages()
      return
    }
  } catch (error: any) {
    console.log('⚠️ [SEO] Failed to load SEO pages, using demo data:', error?.message || error)
    seoPages = generateDemoSEOPages()
  }
}

/**
 * Get SEO page data by URL path
 */
export async function getSEOPageData(urlPath: string): Promise<SEOPageData | null> {
  // Ensure pages are loaded
  if (Object.keys(seoPages).length === 0) {
    const businessId = getBusinessId()
    await loadSEOPages(businessId)
  }
  
  return seoPages[urlPath] || null
}

/**
 * Get all SEO pages
 */
export async function getAllSEOPages(): Promise<Record<string, SEOPageData>> {
  // Ensure pages are loaded
  if (Object.keys(seoPages).length === 0) {
    const businessId = getBusinessId()
    await loadSEOPages(businessId)
  }
  
  return seoPages
}

/**
 * Get business ID from environment or URL
 */
function getBusinessId(): string {
  // In production, this would be determined from the domain or environment
  return process.env.NEXT_PUBLIC_BUSINESS_ID || process.env.BUSINESS_ID || '550e8400-e29b-41d4-a716-446655440010'
}

/**
 * Generate demo SEO pages for development/fallback
 */
function generateDemoSEOPages(): Record<string, SEOPageData> {
  const services = [
    'hvac-repair', 'ac-repair', 'heating-repair', 'plumbing-repair',
    'electrical-service', 'water-heater-repair'
  ]
  
  const locations = [
    'austin-tx', 'round-rock-tx', 'cedar-park-tx', 'pflugerville-tx'
  ]
  
  const pages: Record<string, SEOPageData> = {}
  
  // Service pages
  services.forEach(service => {
    const serviceName = service.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())
    pages[`/services/${service}`] = {
      title: `${serviceName} Services | Professional ${serviceName} | Elite HVAC`,
      meta_description: `Professional ${serviceName} services. Licensed, insured, and experienced technicians. Same-day service available.`,
      h1_heading: `Professional ${serviceName} Services`,
      content: generateServiceContent(serviceName),
      schema_markup: generateServiceSchema(serviceName),
      target_keywords: [service, `${service} service`, `professional ${service}`],
      page_url: `/services/${service}`,
      generation_method: 'template',
      page_type: 'service',
      word_count: 500,
      created_at: new Date().toISOString()
    }
  })
  
  // Location pages
  locations.forEach(location => {
    const [city, state] = location.split('-')
    const cityName = city.charAt(0).toUpperCase() + city.slice(1)
    const stateName = state.toUpperCase()
    
    pages[`/locations/${location}`] = {
      title: `Elite HVAC in ${cityName}, ${stateName} | Local HVAC Services`,
      meta_description: `Elite HVAC provides professional HVAC services in ${cityName}, ${stateName}. Serving ${cityName} residents with quality workmanship.`,
      h1_heading: `Elite HVAC - Serving ${cityName}, ${stateName}`,
      content: generateLocationContent(cityName, stateName),
      schema_markup: generateLocationSchema(cityName, stateName),
      target_keywords: [`hvac ${city}`, `${city} hvac`, `hvac services ${city}`],
      page_url: `/locations/${location}`,
      generation_method: 'template',
      page_type: 'location',
      word_count: 450,
      created_at: new Date().toISOString()
    }
  })
  
  // Service + Location combinations (the money makers!)
  services.forEach(service => {
    locations.forEach(location => {
      const serviceName = service.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())
      const [city, state] = location.split('-')
      const cityName = city.charAt(0).toUpperCase() + city.slice(1)
      const stateName = state.toUpperCase()
      
      pages[`/services/${service}/${location}`] = {
        title: `${serviceName} in ${cityName}, ${stateName} | 24/7 Service | Elite HVAC`,
        meta_description: `Professional ${serviceName} services in ${cityName}, ${stateName}. Same-day service, licensed & insured. Call for free estimate.`,
        h1_heading: `Expert ${serviceName} Services in ${cityName}, ${stateName}`,
        content: generateServiceLocationContent(serviceName, cityName, stateName),
        schema_markup: generateServiceLocationSchema(serviceName, cityName, stateName),
        target_keywords: [
          `${service} ${city}`,
          `${city} ${service}`,
          `${service} services ${city}`,
          `${service} ${city} ${state}`
        ],
        page_url: `/services/${service}/${location}`,
        generation_method: Math.random() > 0.9 ? 'llm' : 'template', // 10% LLM enhanced
        page_type: 'service_location',
        word_count: 800,
        created_at: new Date().toISOString()
      }
      
      // Emergency variants
      pages[`/emergency/${service}/${location}`] = {
        title: `Emergency ${serviceName} in ${cityName}, ${stateName} | 24/7 Service`,
        meta_description: `24/7 emergency ${serviceName} in ${cityName}, ${stateName}. Fast response, licensed technicians. Call now for immediate service.`,
        h1_heading: `24/7 Emergency ${serviceName} in ${cityName}, ${stateName}`,
        content: generateEmergencyContent(serviceName, cityName, stateName),
        schema_markup: generateEmergencySchema(serviceName, cityName, stateName),
        target_keywords: [
          `emergency ${service} ${city}`,
          `24/7 ${service} ${city}`,
          `${service} emergency ${city}`
        ],
        page_url: `/emergency/${service}/${location}`,
        generation_method: 'template',
        page_type: 'emergency_service',
        word_count: 600,
        created_at: new Date().toISOString()
      }
    })
  })
  
  return pages
}

function generateServiceContent(serviceName: string): string {
  return `
    <div class="service-content">
      <p>Looking for reliable ${serviceName} services? Elite HVAC provides professional ${serviceName} solutions with 15+ years of experience. Our licensed and insured technicians deliver quality workmanship and exceptional customer service.</p>
      
      <h2>Our ${serviceName} Services</h2>
      <ul>
        <li>Emergency ${serviceName} (24/7 availability)</li>
        <li>Routine maintenance and inspections</li>
        <li>New installations and replacements</li>
        <li>Repairs and troubleshooting</li>
        <li>Preventive maintenance programs</li>
      </ul>
      
      <h2>Why Choose Elite HVAC?</h2>
      <ul>
        <li>Licensed and insured professionals</li>
        <li>15+ years of experience</li>
        <li>Same-day service available</li>
        <li>Upfront, transparent pricing</li>
        <li>100% satisfaction guarantee</li>
      </ul>
      
      <p>Contact us today at (512) 555-0100 for expert ${serviceName} services.</p>
    </div>
  `
}

function generateLocationContent(cityName: string, stateName: string): string {
  return `
    <div class="location-content">
      <p>Welcome to Elite HVAC, your trusted HVAC professionals serving ${cityName}, ${stateName} and surrounding areas. We've been providing quality HVAC services to ${cityName} residents for 15+ years.</p>
      
      <h2>About Our ${cityName} Location</h2>
      <p>Our local team understands the unique needs of ${cityName} properties and climate conditions. We're committed to providing fast, reliable service throughout ${cityName}.</p>
      
      <h2>Services Available in ${cityName}</h2>
      <ul>
        <li>Emergency repairs and service calls</li>
        <li>Routine maintenance and inspections</li>
        <li>New installations and replacements</li>
        <li>Preventive maintenance programs</li>
        <li>Commercial and residential services</li>
      </ul>
      
      <h2>Why ${cityName} Residents Choose Us</h2>
      <ul>
        <li>Local ${cityName} expertise and knowledge</li>
        <li>Fast response times throughout ${cityName}</li>
        <li>Licensed, bonded, and insured</li>
        <li>Transparent, upfront pricing</li>
        <li>100% satisfaction guarantee</li>
      </ul>
      
      <p>Contact our ${cityName} team today at (512) 555-0100.</p>
    </div>
  `
}

function generateServiceLocationContent(serviceName: string, cityName: string, stateName: string): string {
  return `
    <div class="service-location-content">
      <p>Need reliable ${serviceName} in ${cityName}? Elite HVAC has been serving ${cityName} residents for 15+ years with professional, affordable ${serviceName} solutions. Our certified technicians provide same-day service throughout ${cityName}, ${stateName}.</p>
      
      <h2>Why Choose Elite HVAC for ${serviceName} in ${cityName}?</h2>
      <ul>
        <li>15+ years serving ${cityName} and surrounding areas</li>
        <li>Licensed, bonded, and insured professionals</li>
        <li>Same-day service available</li>
        <li>100% satisfaction guarantee</li>
        <li>Transparent, upfront pricing</li>
      </ul>
      
      <h2>${serviceName} Services We Provide in ${cityName}</h2>
      <p>Our certified technicians provide comprehensive ${serviceName} services throughout ${cityName}, ${stateName}. Whether you need emergency repairs, routine maintenance, or new installations, we have the expertise to get the job done right.</p>
      
      <h3>Emergency ${serviceName} Service</h3>
      <p>Available 24/7 for urgent ${serviceName} needs in ${cityName}. Our emergency technicians can respond quickly to minimize downtime and restore your comfort.</p>
      
      <h3>Residential ${serviceName}</h3>
      <p>Homeowners in ${cityName} trust us for reliable ${serviceName} solutions. We understand the unique needs of residential properties and provide personalized service.</p>
      
      <h3>Commercial ${serviceName}</h3>
      <p>Businesses in ${cityName} rely on our commercial ${serviceName} expertise. We minimize disruption to your operations while ensuring optimal performance.</p>
      
      <h2>Service Areas</h2>
      <p>We proudly serve ${cityName}, ${stateName} and surrounding areas within 25 miles of our location.</p>
      
      <h2>Contact Elite HVAC Today</h2>
      <p>Ready for professional ${serviceName} service in ${cityName}? Call (512) 555-0100 or contact us online for a free estimate. Emergency service available 24/7!</p>
    </div>
  `
}

function generateEmergencyContent(serviceName: string, cityName: string, stateName: string): string {
  return `
    <div class="emergency-content">
      <p>Emergency ${serviceName} in ${cityName}? Don't panic! Elite HVAC provides 24/7 emergency ${serviceName} services throughout ${cityName}, ${stateName}. Our emergency technicians are on standby and can respond quickly to your urgent ${serviceName} needs.</p>
      
      <h2>Fast Emergency Response</h2>
      <ul>
        <li>Available 24 hours a day, 7 days a week</li>
        <li>Rapid response throughout ${cityName}</li>
        <li>Licensed emergency technicians</li>
        <li>Fully stocked service vehicles</li>
        <li>Upfront emergency pricing</li>
      </ul>
      
      <h2>Common Emergency ${serviceName} Issues</h2>
      <p>Our emergency technicians handle complete system failures, safety hazards, after-hours breakdowns, weekend and holiday emergencies, and storm damage.</p>
      
      <h2>Why Choose Us for Emergency Service?</h2>
      <ul>
        <li>24/7 availability in ${cityName}</li>
        <li>Fast response times</li>
        <li>Licensed emergency technicians</li>
        <li>Transparent emergency pricing</li>
        <li>No hidden fees or surprises</li>
      </ul>
      
      <p><strong>Call (512) 555-0100 now for immediate emergency ${serviceName} service in ${cityName}!</strong></p>
    </div>
  `
}

// Schema markup generators
function generateServiceSchema(serviceName: string) {
  return {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": `${serviceName} Services`,
    "description": `Professional ${serviceName} services`,
    "provider": {
      "@type": "LocalBusiness",
      "name": "Elite HVAC",
      "telephone": "(512) 555-0100"
    }
  }
}

function generateLocationSchema(cityName: string, stateName: string) {
  return {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "Elite HVAC",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": cityName,
      "addressRegion": stateName
    },
    "telephone": "(512) 555-0100"
  }
}

function generateServiceLocationSchema(serviceName: string, cityName: string, stateName: string) {
  return {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": `${serviceName} in ${cityName}`,
    "description": `Professional ${serviceName} services in ${cityName}, ${stateName}`,
    "provider": {
      "@type": "LocalBusiness",
      "name": "Elite HVAC",
      "telephone": "(512) 555-0100",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": cityName,
        "addressRegion": stateName
      }
    },
    "areaServed": {
      "@type": "City",
      "name": cityName
    }
  }
}

function generateEmergencySchema(serviceName: string, cityName: string, stateName: string) {
  return {
    "@context": "https://schema.org",
    "@type": "EmergencyService",
    "name": `Emergency ${serviceName}`,
    "description": `24/7 emergency ${serviceName} services in ${cityName}, ${stateName}`,
    "provider": {
      "@type": "LocalBusiness",
      "name": "Elite HVAC",
      "telephone": "(512) 555-0100"
    },
    "availableAtOrFrom": {
      "@type": "Place",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": cityName,
        "addressRegion": stateName
      }
    }
  }
}
