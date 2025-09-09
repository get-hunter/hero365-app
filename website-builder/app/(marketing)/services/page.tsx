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

  const tradeCount = Object.keys(servicesByCategory).length
  const totalServices = services.length

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
      {/* Compact header (no hero) */}
      <section className="px-6 pt-6 pb-4 border-b border-gray-100">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Services</h1>
            <p className="mt-1 text-sm text-gray-600">Explore all services by trade.</p>
          </div>
          <div className="hidden md:flex items-center gap-2 text-sm text-gray-500">
            <span>{totalServices} services</span>
            <span>•</span>
            <span>{tradeCount} trades</span>
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
          business_id: context.business.id,
          business_name: context.business.name,
          description: context.business.description,
          phone: context.business.phone,
          email: context.business.email,
          address: context.business.address,
          city: context.business.city,
          state: context.business.state,
          postal_code: context.business.postal_code,
          website: context.business.website,
          years_in_business: context.business.years_in_business,
          average_rating: context.average_rating,
          license_number: (context.business as any).license_number,
          emergency_service: true,
          service_areas: context.service_areas?.map((a: any) => a.name) || []
        }}
        services={context.activities?.map((a: any) => ({
          id: a.slug,
          name: a.name,
          slug: a.slug,
          is_featured: a.is_featured,
          category: a.trade_name
        })) || []}
        locations={context.service_areas?.map((area: any) => ({
          id: area.slug,
          slug: area.slug,
          name: area.name,
          city: area.city,
          state: area.state,
          address: area.name,
          is_primary: area.is_primary
        })) || []}
      />
    </div>
  )
}