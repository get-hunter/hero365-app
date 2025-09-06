import { Metadata } from 'next'
import Link from 'next/link'
import { getBusinessContext } from '@/lib/server/business-context-loader'
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver'

export const metadata: Metadata = {
  title: 'Service Areas | Locations We Serve',
  description: 'We provide professional home services throughout the greater metro area. Find service in your location.',
}

// Fetch active locations and services from backend
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

async function getActiveServices() {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
  try {
    const response = await fetch(`${backendUrl}/api/v1/public/services/active`, {
      next: { revalidate: 3600 } // Cache for 1 hour
    })
    if (!response.ok) throw new Error('Failed to fetch services')
    return await response.json()
  } catch (error) {
    console.error('Failed to fetch active services:', error)
    return []
  }
}

// Helper to parse location slug into city/state
function parseLocationSlug(slug: string) {
  const parts = slug.split('-')
  if (parts.length < 2) return { city: slug, state: 'TX' }
  
  const state = parts[parts.length - 1].toUpperCase()
  const cityParts = parts.slice(0, -1)
  const city = cityParts.map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
  
  return { city, state }
}

// Helper to get service icons
function getServiceIcon(slug: string): string {
  const iconMap: { [key: string]: string } = {
    'ac-repair': '❄️',
    'ac-installation': '❄️',
    'hvac-repair': '🔥',
    'hvac-maintenance': '🔧',
    'heating-repair': '🔥',
    'water-heater-repair': '🔥',
    'drain-cleaning': '🚿',
    'plumbing': '🚿',
    'pipe-repair': '🚿',
    'leak-detection': '💧',
    'electrical-repair': '⚡',
    'electrical': '⚡',
    'panel-upgrade': '⚡',
    'lighting-installation': '💡',
    'wiring-repair': '⚡',
    'generator-installation': '🔌',
  }
  return iconMap[slug] || '🔧'
}

export default async function LocationsPage() {
  // Get business ID from host for multi-tenant support
  const resolution = await getBusinessIdFromHost();
  const businessId = resolution.businessId;

  // Fetch data in parallel
  const [context, locations, services] = await Promise.all([
    getBusinessContext(businessId),
    getActiveLocations(),
    getActiveServices()
  ])

  // Take first 4 services for popular services display
  const popularServices = services.slice(0, 4).map((service: any) => ({
    slug: service.slug,
    name: service.name || service.slug.replace('-', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
    icon: getServiceIcon(service.slug)
  }))

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Service Areas
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            {context.business.name} proudly serves the greater {context.business.city} metro area 
            with professional home services. Find reliable HVAC, plumbing, and electrical services in your neighborhood.
          </p>
          <div className="flex gap-4 justify-center">
            <a
              href={`tel:${context.business.phone}`}
              className="inline-flex items-center px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              📞 Call Now: {context.business.phone}
            </a>
            <Link
              href="/services"
              className="inline-flex items-center px-8 py-4 bg-white text-blue-600 font-semibold rounded-lg border-2 border-blue-600 hover:bg-blue-50 transition-colors"
            >
              View All Services
            </Link>
          </div>
        </div>
      </section>

      {/* Interactive Map Placeholder */}
      <section className="py-8 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-12 text-center">
            <p className="text-blue-700 font-semibold text-lg">
              🗺️ Interactive Service Area Map
            </p>
            <p className="text-blue-600 mt-2">
              Coverage includes {context.business.city} and surrounding communities within 30 miles
            </p>
          </div>
        </div>
      </section>

      {/* Location Cards */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 mb-12 text-center">
            Cities We Serve
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {locations.map((location: any) => {
              const { city, state } = parseLocationSlug(location.slug)
              return (
                <div key={location.slug} className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow overflow-hidden">
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-2xl font-bold text-gray-900">
                          {city}, {state}
                        </h3>
                        <p className="text-sm text-gray-500">Service Area: {location.slug}</p>
                      </div>
                      <span className="bg-green-100 text-green-700 text-xs font-semibold px-2 py-1 rounded">
                        Active
                      </span>
                    </div>
                    
                    <p className="text-gray-600 mb-4">
                      Professional home services available in {city} and surrounding areas.
                    </p>
                    
                    <div className="mb-4">
                      <p className="text-sm font-semibold text-gray-700 mb-2">Available Services:</p>
                      <div className="space-y-1">
                        {popularServices.slice(0, 3).map((service) => (
                          <div key={service.slug} className="text-sm text-gray-600">
                            {service.icon} {service.name}
                          </div>
                        ))}
                        {services.length > 3 && (
                          <div className="text-sm text-gray-500">
                            + {services.length - 3} more services
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="pt-4 border-t border-gray-100 space-y-3">
                      <div className="grid grid-cols-2 gap-2">
                        {popularServices.slice(0, 4).map((service) => (
                          <Link
                            key={service.slug}
                            href={`/services/${service.slug}/${location.slug}`}
                            className="text-xs text-center bg-gray-50 hover:bg-gray-100 py-2 px-2 rounded transition-colors"
                          >
                            {service.icon} {service.name}
                          </Link>
                        ))}
                      </div>
                      
                      <div className="text-center">
                        <a
                          href={`tel:${context.business.phone}`}
                          className="inline-block bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors font-semibold text-sm"
                        >
                          Call for {city} Service
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Service Coverage Details */}
      <section className="py-12 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Comprehensive Coverage Across the Metro Area
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">30+</div>
              <p className="text-gray-600">Mile Service Radius</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">24/7</div>
              <p className="text-gray-600">Emergency Service</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">60min</div>
              <p className="text-gray-600">Average Response Time</p>
            </div>
          </div>
          
          <p className="text-gray-600 mb-4">
            {context.business.name} provides comprehensive home services throughout {context.business.city} 
            and the surrounding metropolitan area. Our licensed and insured technicians are strategically 
            located to ensure rapid response times for both scheduled maintenance and emergency repairs.
          </p>
          
          <p className="text-gray-600">
            Whether you're in the heart of downtown or in the growing suburbs, we're committed to 
            delivering the same high-quality service with transparent pricing and guaranteed satisfaction. 
            Call {context.business.phone} to schedule service in your area today.
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 py-16 px-6">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h2 className="text-3xl font-bold mb-4">
            Not Sure If We Service Your Area?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Give us a call! We're expanding our service areas and may be able to help.
          </p>
          <a
            href={`tel:${context.business.phone}`}
            className="inline-flex items-center px-8 py-4 bg-white text-blue-600 font-bold rounded-lg hover:bg-gray-100 transition-colors text-lg"
          >
            📞 Call {context.business.phone} to Confirm Coverage
          </a>
        </div>
      </section>
    </div>
  )
}
