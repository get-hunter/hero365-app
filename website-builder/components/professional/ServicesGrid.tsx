'use client'

import React from 'react'
import { Business, ServiceCategory, Service } from '../../lib/types/business'
import { 
  Thermometer, 
  Zap, 
  Wrench, 
  Snowflake,
  Shield,
  Clock,
  ArrowRight,
  Star,
  Phone
} from 'lucide-react'

interface ServicesGridProps {
  serviceCategories: ServiceCategory[]
  featuredServices: Service[]
  business: Business
}

export default function ServicesGrid({ 
  serviceCategories, 
  featuredServices,
  business 
}: ServicesGridProps) {
  
  // Icon mapping for different service categories
  const getCategoryIcon = (categoryName: string) => {
    const name = categoryName.toLowerCase()
    if (name.includes('hvac') || name.includes('heating') || name.includes('cooling')) {
      return <Thermometer className="h-8 w-8" />
    }
    if (name.includes('electrical')) {
      return <Zap className="h-8 w-8" />
    }
    if (name.includes('plumbing')) {
      return <Wrench className="h-8 w-8" />
    }
    if (name.includes('refrigeration')) {
      return <Snowflake className="h-8 w-8" />
    }
    return <Shield className="h-8 w-8" />
  }

  const handleServiceInquiry = (serviceName: string) => {
    // Scroll to contact form with pre-filled service
    const contactSection = document.getElementById('contact')
    if (contactSection) {
      contactSection.scrollIntoView({ behavior: 'smooth' })
      // Could add logic to pre-fill form with service name
    }
  }

  const handleEmergencyCall = () => {
    window.location.href = `tel:${business.phone_number}`
  }

  return (
    <section className="py-16 lg:py-24 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            Our Services
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Comprehensive {business.trade_category?.toLowerCase()} services in {business.city}, {business.state} and surrounding areas
          </p>
        </div>

        {/* Main Service Categories Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {serviceCategories.map((category) => (
            <div 
              key={category.id}
              className="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden border border-gray-100 hover:border-blue-200"
            >
              {/* Category Header */}
              <div className="bg-gradient-to-br from-blue-600 to-blue-700 text-white p-6">
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 bg-white bg-opacity-20 rounded-lg">
                    {getCategoryIcon(category.name)}
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold">{category.name}</h3>
                    <p className="text-blue-100">
                      {category.services?.length || 0} Services Available
                    </p>
                  </div>
                </div>
                <p className="text-blue-50">
                  {category.description}
                </p>
              </div>

              {/* Services List */}
              <div className="p-6">
                <div className="space-y-3">
                  {category.services?.slice(0, 4).map((service) => (
                    <div 
                      key={service.id}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 cursor-pointer"
                      onClick={() => handleServiceInquiry(service.name)}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold text-gray-900">{service.name}</h4>
                          {service.is_featured && (
                            <Star className="h-4 w-4 text-yellow-500 fill-current" />
                          )}
                          {service.is_emergency && (
                            <div className="bg-red-100 text-red-600 px-2 py-1 rounded-full text-xs font-medium">
                              24/7
                            </div>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {service.description}
                        </p>
                        <div className="flex items-center gap-2 mt-2">
                          {service.unit_price ? (
                            <span className="text-blue-600 font-semibold">
                              From ${service.unit_price}
                            </span>
                          ) : (
                            <span className="text-gray-500">Custom Quote</span>
                          )}
                        </div>
                      </div>
                      <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-600 transition-colors duration-200" />
                    </div>
                  ))}
                  
                  {(category.services?.length || 0) > 4 && (
                    <div className="text-center pt-4 border-t border-gray-100">
                      <span className="text-blue-600 font-medium">
                        +{(category.services?.length || 0) - 4} more services
                      </span>
                    </div>
                  )}
                </div>

                {/* Learn More Button */}
                <div className="mt-6 pt-6 border-t border-gray-100">
                  <button 
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
                    onClick={() => handleServiceInquiry(category.name)}
                  >
                    Learn More
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Featured Services Highlights */}
        {featuredServices.length > 0 && (
          <div className="mb-16">
            <div className="text-center mb-12">
              <h3 className="text-3xl font-bold text-gray-900 mb-4">
                Popular Services
              </h3>
              <p className="text-lg text-gray-600">
                Our most requested services by customers in {business.city}
              </p>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredServices.slice(0, 6).map((service) => (
                <div 
                  key={service.id}
                  className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 border border-gray-100 cursor-pointer"
                  onClick={() => handleServiceInquiry(service.name)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Star className="h-5 w-5 text-yellow-500 fill-current" />
                      <span className="text-sm font-medium text-yellow-600">Featured</span>
                    </div>
                    {service.is_emergency && (
                      <div className="bg-red-100 text-red-600 px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        Emergency
                      </div>
                    )}
                  </div>
                  
                  <h4 className="font-bold text-gray-900 mb-2">{service.name}</h4>
                  <p className="text-gray-600 text-sm mb-4">{service.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      {service.unit_price ? (
                        <span className="text-lg font-bold text-blue-600">
                          ${service.unit_price}
                        </span>
                      ) : (
                        <span className="text-gray-500 font-medium">Custom Quote</span>
                      )}
                    </div>
                    <button className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center gap-1">
                      Get Quote
                      <ArrowRight className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Emergency Service Call-to-Action */}
        <div className="bg-gradient-to-r from-red-600 to-red-700 rounded-2xl p-8 text-white text-center">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Clock className="h-8 w-8" />
              <h3 className="text-3xl font-bold">Emergency Service Available</h3>
            </div>
            <p className="text-xl mb-6 text-red-100">
              Need immediate assistance? Our emergency service team is available 24/7 
              for urgent {business.trade_category?.toLowerCase()} issues.
            </p>
            <button 
              onClick={handleEmergencyCall}
              className="bg-white hover:bg-red-50 text-red-600 font-bold py-4 px-8 rounded-lg text-lg transition-colors duration-200 flex items-center justify-center gap-2 mx-auto"
            >
              <Phone className="h-5 w-5" />
              Call Emergency Line: {business.phone_number}
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}
