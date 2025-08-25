'use client'

import React from 'react'
import { Business } from '../../lib/types/business'
import { Phone, MapPin, Clock, Shield } from 'lucide-react'

interface ProfessionalHeroProps {
  business: Business
  heroContent: {
    title: string
    subtitle: string
    features: string[]
  }
  totalServices: number
}

export default function ProfessionalHero({ 
  business, 
  heroContent,
  totalServices 
}: ProfessionalHeroProps) {
  const handleBookNow = () => {
    // Scroll to contact section
    const contactSection = document.getElementById('contact')
    contactSection?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleCallNow = () => {
    window.location.href = `tel:${business.phone_number}`
  }

  return (
    <section className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 text-white overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.4%22%3E%3Ccircle%20cx%3D%227%22%20cy%3D%227%22%20r%3D%221%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')]"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-16 lg:py-24">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            
            {/* Content */}
            <div className="space-y-8">
              {/* Business Location & Contact */}
              <div className="flex flex-col sm:flex-row sm:items-center gap-4 text-blue-100">
                <div className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  <span className="font-semibold">{business.city}, {business.state}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Phone className="h-5 w-5" />
                  <span className="font-semibold">Support 24/7: {business.phone_number}</span>
                </div>
              </div>

              {/* Main Headlines */}
              <div className="space-y-4">
                <h1 className="text-4xl lg:text-6xl font-bold leading-tight">
                  {heroContent.title}
                </h1>
                <p className="text-xl lg:text-2xl text-blue-100 font-medium">
                  {heroContent.subtitle}
                </p>
                <p className="text-lg text-blue-200">
                  {business.description}
                </p>
              </div>

              {/* Key Features */}
              <div className="grid grid-cols-2 gap-4">
                {heroContent.features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                      <Shield className="h-4 w-4 text-white" />
                    </div>
                    <span className="text-white font-medium">{feature}</span>
                  </div>
                ))}
              </div>

              {/* Service Stats */}
              <div className="flex items-center gap-8 py-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-yellow-400">{totalServices}+</div>
                  <div className="text-blue-200">Services Available</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-yellow-400">15+</div>
                  <div className="text-blue-200">Years Experience</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-yellow-400">24/7</div>
                  <div className="text-blue-200">Emergency Service</div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <button
                  onClick={handleBookNow}
                  className="bg-yellow-500 hover:bg-yellow-600 text-blue-900 font-bold py-4 px-8 rounded-lg text-lg transition-colors duration-200 flex items-center justify-center gap-2"
                >
                  Get a Quote Now
                </button>
                <button
                  onClick={handleCallNow}
                  className="border-2 border-white hover:bg-white hover:text-blue-900 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-200 flex items-center justify-center gap-2"
                >
                  <Phone className="h-5 w-5" />
                  Call Now
                </button>
              </div>
            </div>

            {/* Service Image/Illustration */}
            <div className="lg:text-right">
              <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-2xl p-8 border border-white border-opacity-20">
                <div className="space-y-6">
                  <div className="text-center">
                    <div className="w-24 h-24 bg-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Clock className="h-12 w-12 text-blue-900" />
                    </div>
                    <h3 className="text-2xl font-bold mb-2">Same-Day Service</h3>
                    <p className="text-blue-100">
                      Emergency repairs and installations available 7 days a week
                    </p>
                  </div>
                  
                  <div className="border-t border-white border-opacity-20 pt-6">
                    <h4 className="font-bold text-lg mb-4">Service Areas:</h4>
                    <div className="flex flex-wrap gap-2">
                      {business.service_areas?.slice(0, 4).map((area, index) => (
                        <span 
                          key={index}
                          className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm font-medium"
                        >
                          {area}
                        </span>
                      ))}
                      {(business.service_areas?.length || 0) > 4 && (
                        <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm font-medium">
                          +{(business.service_areas?.length || 0) - 4} more
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Wave */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg
          className="w-full h-12 text-white"
          fill="currentColor"
          viewBox="0 0 1200 120"
          preserveAspectRatio="none"
        >
          <path d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z"></path>
        </svg>
      </div>
    </section>
  )
}
