import { Metadata } from 'next'
import Link from 'next/link'
import Hero365Header from '@/components/server/layout/Hero365Header'
import Hero365Footer from '@/components/shared/Hero365Footer'
import { getBusinessContext } from '@/lib/server/business-context-loader'
import ServicesCategorySection from '@/components/client/services/ServicesCategorySection'
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver'

export const metadata: Metadata = {
  title: 'Our Services | Professional Home Services',
  description: 'Explore our comprehensive range of professional home services including HVAC, plumbing, electrical, and more.',
}

// Fetch business-specific services
async function getBusinessServices(businessId: string) {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
  try {
    const response = await fetch(`${backendUrl}/api/v1/public/contractors/${businessId}/services?include_pricing=true`, {
      next: { revalidate: 3600 } // Cache for 1 hour
    })
    if (!response.ok) throw new Error('Failed to fetch business services')
    return await response.json()
  } catch (error) {
    console.error('Failed to fetch business services:', error)
    return []
  }
}

async function getActiveLocations() {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
  try {
    const response = await fetch(`${backendUrl}/api/v1/public/locations/active`, {
      next: { revalidate: 3600 } // Cache for 1 hour
    })
    if (!response.ok) throw new Error('Failed to fetch locations')
    return await response.json()
  } catch (error) {
    console.error('Failed to fetch active locations:', error)
    return []
  }
}

// Helper to get service category and icon
function getServiceCategory(slug: string): { category: string; icon: string; urgent?: boolean } {
  const categoryMap: { [key: string]: { category: string; icon: string; urgent?: boolean } } = {
    // HVAC Services
    'ac-repair': { category: 'HVAC Services', icon: '❄️', urgent: true },
    'ac-installation': { category: 'HVAC Services', icon: '❄️' },
    'hvac-repair': { category: 'HVAC Services', icon: '🔥', urgent: true },
    'hvac-maintenance': { category: 'HVAC Services', icon: '🔧' },
    'heating-repair': { category: 'HVAC Services', icon: '🔥', urgent: true },
    'furnace-installation': { category: 'HVAC Services', icon: '🔥' },
    'duct-cleaning': { category: 'HVAC Services', icon: '🌪️' },
    
    // Plumbing Services
    'drain-cleaning': { category: 'Plumbing Services', icon: '🚿', urgent: true },
    'water-heater-repair': { category: 'Plumbing Services', icon: '🔥', urgent: true },
    'leak-detection': { category: 'Plumbing Services', icon: '💧', urgent: true },
    'pipe-repair': { category: 'Plumbing Services', icon: '🚿', urgent: true },
    'toilet-repair': { category: 'Plumbing Services', icon: '🚽' },
    'faucet-installation': { category: 'Plumbing Services', icon: '🚿' },
    
    // Electrical Services
    'panel-upgrade': { category: 'Electrical Services', icon: '⚡' },
    'lighting-installation': { category: 'Electrical Services', icon: '💡' },
    'wiring-repair': { category: 'Electrical Services', icon: '⚡', urgent: true },
    'outlet-installation': { category: 'Electrical Services', icon: '🔌' },
    'generator-installation': { category: 'Electrical Services', icon: '🔌' },
    'surge-protection': { category: 'Electrical Services', icon: '⚡' },
  }
  
  return categoryMap[slug] || { category: 'Other Services', icon: '🔧' }
}

// Helper to parse location slug
function parseLocationSlug(slug: string) {
  const parts = slug.split('-')
  if (parts.length < 2) return { city: slug, state: 'TX' }
  
  const state = parts[parts.length - 1].toUpperCase()
  const cityParts = parts.slice(0, -1)
  const city = cityParts.map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
  
  return { city, state }
}

// Helper to get category descriptions
function getCategoryDescription(categoryName: string): string {
  const descriptions: { [key: string]: string } = {
    'HVAC Services': 'Heating, ventilation, and air conditioning solutions',
    'Plumbing Services': 'Complete plumbing solutions for your home',
    'Electrical Services': 'Safe and reliable electrical work',
    'Other Services': 'Additional professional home services'
  }
  return descriptions[categoryName] || 'Professional home services'
}

export default async function ServicesPage() {
  // Get business ID from host for multi-tenant support
  const resolution = await getBusinessIdFromHost();
  const businessId = resolution.businessId;

  // Fetch data in parallel
  const [context, services, locations] = await Promise.all([
    getBusinessContext(businessId),
    getBusinessServices(businessId),
    getActiveLocations()
  ])

  // Group services by TRADE first; attach category, description, and pricing for UI
  const servicesByCategory: { [key: string]: any[] } = {}
  services.forEach((service: any) => {
    const trade = (service.trade_slug || 'general')
      .replace('-', ' ')
      .replace(/\b\w/g, (l: string) => l.toUpperCase())
    const map = getServiceCategory(service.canonical_slug)
    const categoryFromSlug = map.category
    const icon = map.icon
    const inferredUrgent = map.urgent
    const serviceName = service.name || service.canonical_slug.replace('-', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())

    if (!servicesByCategory[trade]) {
      servicesByCategory[trade] = []
    }

    const pricingSummary: string | undefined = service.pricing_summary || (service.price_min ? (
      service.price_max ? `$${service.price_min}-$${service.price_max}${service.price_unit ? ` per ${service.price_unit}` : ''}`
      : `$${service.price_min}${service.price_unit ? ` per ${service.price_unit}` : ''}`
    ) : undefined)

    servicesByCategory[trade].push({
      slug: service.canonical_slug,
      name: serviceName,
      icon,
      urgent: Boolean(service.is_emergency) || Boolean(inferredUrgent),
      category: service.category || categoryFromSlug,
      description: service.description || undefined,
      pricingSummary,
      priceMin: service.price_min ?? undefined,
      priceMax: service.price_max ?? undefined,
      priceUnit: service.price_unit ?? undefined,
      image_url: service.image_url ?? undefined,
      image_alt: service.image_alt ?? undefined,
    })
  })

  // Get popular locations for cross-linking
  const popularLocations = locations.slice(0, 3).map((location: any) => {
    const { city, state } = parseLocationSlug(location.slug)
    return {
      slug: location.slug,
      name: `${city}, ${state}`
    }
  })

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <Hero365Header 
        businessProfile={{
          business_id: context.business.id,
          business_name: context.business.name,
          phone: context.business.phone,
          phone_display: context.business.phone,
          email: context.business.email,
          address: context.business.address,
          city: context.business.city,
          state: context.business.state,
          postal_code: context.business.postal_code,
          logo_url: context.business.logo_url
        }}
        showCTA={true}
        showCart={false}
      />
      {/* Hero Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Our Professional Services
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            {context.business.name} provides comprehensive home services with licensed, 
            insured professionals you can trust. Available 24/7 for emergencies.
          </p>
          <div className="flex gap-4 justify-center">
            <a
              href={`tel:${context.business.phone}`}
              className="inline-flex items-center px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              📞 Call Now: {context.business.phone}
            </a>
            <Link
              href="/contact"
              className="inline-flex items-center px-8 py-4 bg-white text-blue-600 font-semibold rounded-lg border-2 border-blue-600 hover:bg-blue-50 transition-colors"
            >
              Get Free Quote
            </Link>
          </div>
        </div>
      </section>

      {/* Service Categories */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          {Object.entries(servicesByCategory).map(([categoryName, categoryServices]) => (
            <ServicesCategorySection
              key={categoryName}
              title={categoryName}
              icon={categoryServices[0]?.icon || '🔧'}
              description={getCategoryDescription(categoryName)}
              services={categoryServices}
              popularLocations={popularLocations}
              initialVisibleCount={9}
            />
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 py-16 px-6">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h2 className="text-3xl font-bold mb-4">
            Need Emergency Service?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            We're available 24/7 for emergency repairs. Licensed, insured, and ready to help.
          </p>
          <a
            href={`tel:${context.business.phone}`}
            className="inline-flex items-center px-8 py-4 bg-white text-blue-600 font-bold rounded-lg hover:bg-gray-100 transition-colors text-lg"
          >
            📞 Call Now for Emergency Service
          </a>
        </div>
      </section>

      {/* SEO Content */}
      <section className="py-12 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Professional Home Services in {context.business.city}
          </h2>
          <p className="text-gray-600 mb-4">
            {context.business.name} has been serving {context.business.city} and surrounding 
            areas for {context.business.years_in_business || 'many'} years. Our team of licensed 
            and insured professionals specializes in HVAC, plumbing, electrical, and more.
          </p>
          <p className="text-gray-600">
            Whether you need emergency repairs, routine maintenance, or new installations, 
            we provide reliable service with upfront pricing and satisfaction guaranteed. 
            Contact us today at {context.business.phone} for a free estimate.
          </p>
        </div>
      </section>

      <Hero365Footer 
        business={{
          id: context.business.id,
          name: context.business.name,
          phone_number: context.business.phone,
          business_email: context.business.email,
          address: context.business.address,
          website: context.business.website,
          service_areas: context.business.service_areas || [],
          trades: context.business.trades || [],
          seo_keywords: []
        }}
        serviceCategories={[]}
        locations={[]}
      />
    </div>
  )
}