import { NextRequest, NextResponse } from 'next/server'

/**
 * SEO Pages API Endpoint
 * Serves generated SEO page data for dynamic routing
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

export async function GET(
  request: NextRequest,
  { params }: { params: { businessId: string } }
) {
  try {
    const { businessId } = params
    
    // In production, this would fetch from the backend API or database
    // For now, we'll return demo data that matches our SEO generator output
    
    const seoPages = await generateDemoSEOPages(businessId)
    
    return NextResponse.json({
      success: true,
      business_id: businessId,
      pages: seoPages,
      total_pages: Object.keys(seoPages).length,
      generated_at: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to fetch SEO pages:', error)
    
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch SEO pages',
        pages: {}
      },
      { status: 500 }
    )
  }
}

async function generateDemoSEOPages(businessId: string): Promise<Record<string, SEOPageData>> {
  // This simulates the output from our SEO generator service
  const services = [
    { id: 'hvac-repair', name: 'HVAC Repair' },
    { id: 'ac-repair', name: 'AC Repair' },
    { id: 'heating-repair', name: 'Heating Repair' },
    { id: 'plumbing-repair', name: 'Plumbing Repair' },
    { id: 'electrical-service', name: 'Electrical Service' },
    { id: 'water-heater-repair', name: 'Water Heater Repair' }
  ]
  
  const locations = [
    { id: 'austin-tx', city: 'Austin', state: 'TX', searches: 5000 },
    { id: 'round-rock-tx', city: 'Round Rock', state: 'TX', searches: 2000 },
    { id: 'cedar-park-tx', city: 'Cedar Park', state: 'TX', searches: 1500 },
    { id: 'pflugerville-tx', city: 'Pflugerville', state: 'TX', searches: 1200 }
  ]
  
  const pages: Record<string, SEOPageData> = {}
  
  // Generate service overview pages
  services.forEach(service => {
    pages[`/services/${service.id}`] = {
      title: `${service.name} Services | Professional ${service.name} | Elite HVAC`,
      meta_description: `Professional ${service.name} services. Licensed, insured, and experienced technicians. Same-day service available. Call for free estimate.`,
      h1_heading: `Professional ${service.name} Services`,
      content: generateServiceContent(service.name),
      schema_markup: generateServiceSchema(service.name),
      target_keywords: [service.id, `${service.id} service`, `professional ${service.id}`],
      page_url: `/services/${service.id}`,
      generation_method: 'template',
      page_type: 'service',
      word_count: 500,
      created_at: new Date().toISOString()
    }
  })
  
  // Generate location hub pages
  locations.forEach(location => {
    pages[`/locations/${location.id}`] = {
      title: `Elite HVAC in ${location.city}, ${location.state} | Local HVAC Services`,
      meta_description: `Elite HVAC provides professional HVAC services in ${location.city}, ${location.state}. Serving ${location.city} residents with quality workmanship and reliable service.`,
      h1_heading: `Elite HVAC - Serving ${location.city}, ${location.state}`,
      content: generateLocationContent(location.city, location.state),
      schema_markup: generateLocationSchema(location.city, location.state),
      target_keywords: [`hvac ${location.city.toLowerCase()}`, `${location.city.toLowerCase()} hvac`, `hvac services ${location.city.toLowerCase()}`],
      page_url: `/locations/${location.id}`,
      generation_method: 'template',
      page_type: 'location',
      word_count: 450,
      created_at: new Date().toISOString()
    }
  })
  
  // Generate service + location combinations (the revenue generators!)
  services.forEach(service => {
    locations.forEach(location => {
      const isHighValue = location.searches > 1000 && Math.random() > 0.9 // 10% get LLM enhancement
      
      pages[`/services/${service.id}/${location.id}`] = {
        title: `${service.name} in ${location.city}, ${location.state} | 24/7 Service | Elite HVAC`,
        meta_description: `Professional ${service.name} services in ${location.city}, ${location.state}. Same-day service, licensed & insured. Call (512) 555-0100 for free estimate.`,
        h1_heading: `Expert ${service.name} Services in ${location.city}, ${location.state}`,
        content: generateServiceLocationContent(service.name, location.city, location.state, isHighValue),
        schema_markup: generateServiceLocationSchema(service.name, location.city, location.state),
        target_keywords: [
          `${service.id} ${location.city.toLowerCase()}`,
          `${location.city.toLowerCase()} ${service.id}`,
          `${service.id} services ${location.city.toLowerCase()}`,
          `${service.id} ${location.city.toLowerCase()} ${location.state.toLowerCase()}`
        ],
        page_url: `/services/${service.id}/${location.id}`,
        generation_method: isHighValue ? 'llm' : 'template',
        page_type: 'service_location',
        word_count: isHighValue ? 1200 : 800,
        created_at: new Date().toISOString()
      }
      
      // Generate emergency service variants
      pages[`/emergency/${service.id}/${location.id}`] = {
        title: `Emergency ${service.name} in ${location.city}, ${location.state} | 24/7 Service`,
        meta_description: `24/7 emergency ${service.name} in ${location.city}, ${location.state}. Fast response, licensed technicians. Call (512) 555-0100 now for immediate service.`,
        h1_heading: `24/7 Emergency ${service.name} in ${location.city}, ${location.state}`,
        content: generateEmergencyContent(service.name, location.city, location.state),
        schema_markup: generateEmergencySchema(service.name, location.city, location.state),
        target_keywords: [
          `emergency ${service.id} ${location.city.toLowerCase()}`,
          `24/7 ${service.id} ${location.city.toLowerCase()}`,
          `${service.id} emergency ${location.city.toLowerCase()}`
        ],
        page_url: `/emergency/${service.id}/${location.id}`,
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
        <li>✅ Licensed and insured professionals</li>
        <li>🏆 15+ years of experience</li>
        <li>⚡ Same-day service available</li>
        <li>💰 Upfront, transparent pricing</li>
        <li>🛡️ 100% satisfaction guarantee</li>
      </ul>
      
      <p><strong>Contact us today at (512) 555-0100 for expert ${serviceName} services.</strong></p>
    </div>
  `
}

function generateLocationContent(cityName: string, stateName: string): string {
  return `
    <div class="location-content">
      <p>Welcome to Elite HVAC, your trusted HVAC professionals serving ${cityName}, ${stateName} and surrounding areas. We've been providing quality HVAC services to ${cityName} residents for 15+ years.</p>
      
      <h2>About Our ${cityName} Service Area</h2>
      <p>Our local team understands the unique needs of ${cityName} properties and climate conditions. We're committed to providing fast, reliable service throughout ${cityName} and the surrounding areas.</p>
      
      <h2>Services Available in ${cityName}</h2>
      <ul>
        <li>🚨 Emergency repairs and service calls</li>
        <li>🔧 Routine maintenance and inspections</li>
        <li>🏠 New installations and replacements</li>
        <li>📋 Preventive maintenance programs</li>
        <li>🏢 Commercial and residential services</li>
      </ul>
      
      <h2>Why ${cityName} Residents Choose Us</h2>
      <ul>
        <li>🎯 Local ${cityName} expertise and knowledge</li>
        <li>⚡ Fast response times throughout ${cityName}</li>
        <li>✅ Licensed, bonded, and insured</li>
        <li>💰 Transparent, upfront pricing</li>
        <li>🛡️ 100% satisfaction guarantee</li>
      </ul>
      
      <p><strong>Contact our ${cityName} team today at (512) 555-0100.</strong></p>
    </div>
  `
}

function generateServiceLocationContent(serviceName: string, cityName: string, stateName: string, isEnhanced: boolean): string {
  const baseContent = `
    <div class="service-location-content">
      <p>Need reliable ${serviceName} in ${cityName}? Elite HVAC has been serving ${cityName} residents for 15+ years with professional, affordable ${serviceName} solutions. Our certified technicians provide same-day service throughout ${cityName}, ${stateName}.</p>
      
      <h2>Why Choose Elite HVAC for ${serviceName} in ${cityName}?</h2>
      <ul>
        <li>🏆 15+ years serving ${cityName} and surrounding areas</li>
        <li>✅ Licensed, bonded, and insured professionals</li>
        <li>⚡ Same-day service available</li>
        <li>🛡️ 100% satisfaction guarantee</li>
        <li>💰 Transparent, upfront pricing</li>
      </ul>
      
      <h2>${serviceName} Services We Provide in ${cityName}</h2>
      <p>Our certified technicians provide comprehensive ${serviceName} services throughout ${cityName}, ${stateName}. Whether you need emergency repairs, routine maintenance, or new installations, we have the expertise to get the job done right.</p>
      
      <h3>Emergency ${serviceName} Service</h3>
      <p>Available 24/7 for urgent ${serviceName} needs in ${cityName}. Our emergency technicians can respond quickly to minimize downtime and restore your comfort.</p>
      
      <h3>Residential ${serviceName}</h3>
      <p>Homeowners in ${cityName} trust us for reliable ${serviceName} solutions. We understand the unique needs of residential properties and provide personalized service.</p>
      
      <h3>Commercial ${serviceName}</h3>
      <p>Businesses in ${cityName} rely on our commercial ${serviceName} expertise. We minimize disruption to your operations while ensuring optimal performance.</p>
  `
  
  const enhancedContent = isEnhanced ? `
      <h2>Local ${cityName} Expertise</h2>
      <p>As longtime ${cityName} residents ourselves, we understand the unique challenges that ${stateName} weather can present to your HVAC system. From hot summers that strain air conditioning units to occasional cold snaps that test heating systems, we've seen it all in ${cityName}.</p>
      
      <h2>Serving ${cityName} Neighborhoods</h2>
      <p>We proudly serve all areas of ${cityName}, including downtown, surrounding residential neighborhoods, and commercial districts. Our local knowledge helps us provide faster, more effective service to every corner of ${cityName}.</p>
      
      <h2>Customer Reviews in ${cityName}</h2>
      <blockquote class="bg-gray-50 p-4 border-l-4 border-blue-500 italic">
        "Elite HVAC saved the day when our AC went out during the summer heat wave. They were at our ${cityName} home within 2 hours and had us cool again by evening. Highly recommend!" - Sarah M., ${cityName} resident
      </blockquote>
  ` : ''
  
  return baseContent + enhancedContent + `
      <h2>Service Areas</h2>
      <p>We proudly serve ${cityName}, ${stateName} and surrounding areas within 25 miles of our location.</p>
      
      <h2>Contact Elite HVAC Today</h2>
      <p><strong>Ready for professional ${serviceName} service in ${cityName}? Call (512) 555-0100 or contact us online for a free estimate. Emergency service available 24/7!</strong></p>
    </div>
  `
}

function generateEmergencyContent(serviceName: string, cityName: string, stateName: string): string {
  return `
    <div class="emergency-content">
      <div class="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
        <p class="text-red-800 font-bold">🚨 EMERGENCY ${serviceName.toUpperCase()} SERVICE IN ${cityName.toUpperCase()}</p>
      </div>
      
      <p>Emergency ${serviceName} in ${cityName}? Don't panic! Elite HVAC provides 24/7 emergency ${serviceName} services throughout ${cityName}, ${stateName}. Our emergency technicians are on standby and can respond quickly to your urgent ${serviceName} needs.</p>
      
      <h2>⚡ Fast Emergency Response</h2>
      <ul>
        <li>🕐 Available 24 hours a day, 7 days a week</li>
        <li>🚗 Rapid response throughout ${cityName}</li>
        <li>👨‍🔧 Licensed emergency technicians</li>
        <li>🧰 Fully stocked service vehicles</li>
        <li>💰 Upfront emergency pricing</li>
      </ul>
      
      <h2>🚨 Common Emergency ${serviceName} Issues</h2>
      <p>Our emergency technicians handle:</p>
      <ul>
        <li>Complete system failures</li>
        <li>Safety hazards and urgent repairs</li>
        <li>After-hours breakdowns</li>
        <li>Weekend and holiday emergencies</li>
        <li>Storm damage and urgent issues</li>
      </ul>
      
      <h2>✅ Why Choose Us for Emergency Service?</h2>
      <ul>
        <li>🕐 24/7 availability in ${cityName}</li>
        <li>⚡ Fast response times</li>
        <li>👨‍🔧 Licensed emergency technicians</li>
        <li>💰 Transparent emergency pricing</li>
        <li>🚫 No hidden fees or surprises</li>
      </ul>
      
      <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 mt-6">
        <p class="text-yellow-800 font-bold text-lg">📞 Call (512) 555-0100 NOW for immediate emergency ${serviceName} service in ${cityName}!</p>
      </div>
    </div>
  `
}

// Schema markup generators (same as in seo-data.ts)
function generateServiceSchema(serviceName: string) {
  return {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": `${serviceName} Services`,
    "description": `Professional ${serviceName} services by Elite HVAC`,
    "provider": {
      "@type": "LocalBusiness",
      "name": "Elite HVAC",
      "telephone": "(512) 555-0100",
      "url": "https://website.hero365.workers.dev"
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
      "addressRegion": stateName,
      "addressCountry": "US"
    },
    "telephone": "(512) 555-0100",
    "url": "https://website.hero365.workers.dev"
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
        "addressRegion": stateName,
        "addressCountry": "US"
      },
      "url": "https://website.hero365.workers.dev"
    },
    "areaServed": {
      "@type": "City",
      "name": cityName,
      "containedInPlace": {
        "@type": "State",
        "name": stateName
      }
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
        "addressRegion": stateName,
        "addressCountry": "US"
      }
    },
    "hoursAvailable": {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
      ],
      "opens": "00:00",
      "closes": "23:59"
    }
  }
}
