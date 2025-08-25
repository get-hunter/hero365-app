'use client'

import React from 'react'
import { Business, ServiceCategory } from '../../lib/types/business'
import { 
  Phone, 
  Mail, 
  MapPin, 
  Clock,
  Facebook,
  Twitter,
  Instagram,
  Linkedin,
  ArrowRight
} from 'lucide-react'

interface ProfessionalFooterProps {
  business: Business
  serviceCategories: ServiceCategory[]
}

export default function ProfessionalFooter({ 
  business, 
  serviceCategories 
}: ProfessionalFooterProps) {
  
  const currentYear = new Date().getFullYear()
  
  const handleQuickCall = () => {
    window.location.href = `tel:${business.phone_number}`
  }

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <footer className="bg-gray-900 text-white">
      
      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid lg:grid-cols-4 gap-8">
          
          {/* Company Information */}
          <div className="lg:col-span-1">
            <div className="mb-6">
              <h3 className="text-2xl font-bold mb-4">{business.name}</h3>
              <p className="text-gray-300 mb-4">
                {business.description}
              </p>
              <p className="text-gray-400 text-sm">
                Your best solution for accurate, immediate, and professional help with all of your major service needs.
              </p>
            </div>

            {/* Contact Info */}
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Phone className="h-5 w-5 text-blue-400" />
                <span className="text-blue-400 font-semibold">{business.phone_number}</span>
              </div>
              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-gray-400 mt-0.5" />
                <div className="text-gray-300">
                  <div>{business.address}</div>
                  <div>{business.city}, {business.state} {business.zip_code}</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Mail className="h-5 w-5 text-gray-400" />
                <span className="text-gray-300">{business.business_email}</span>
              </div>
              <div className="flex items-start gap-3">
                <Clock className="h-5 w-5 text-gray-400 mt-0.5" />
                <div className="text-gray-300">
                  <div>8am – 8pm Every Day</div>
                  <div className="text-sm text-gray-400">Customer support 24/7</div>
                </div>
              </div>
            </div>
          </div>

          {/* Services */}
          <div>
            <h4 className="text-lg font-bold mb-6">Services</h4>
            <ul className="space-y-3">
              {serviceCategories.map((category) => (
                <li key={category.id}>
                  <a 
                    href={`#${category.slug || category.name.toLowerCase()}`}
                    className="text-gray-300 hover:text-white transition-colors duration-200 flex items-center gap-2 group"
                  >
                    <span>{category.name}</span>
                    <ArrowRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                  </a>
                  {category.services && category.services.length > 0 && (
                    <ul className="ml-4 mt-2 space-y-1">
                      {category.services.slice(0, 3).map((service) => (
                        <li key={service.id}>
                          <span className="text-sm text-gray-400 hover:text-gray-300 transition-colors duration-200 cursor-pointer">
                            {service.name}
                          </span>
                        </li>
                      ))}
                      {category.services.length > 3 && (
                        <li>
                          <span className="text-sm text-blue-400">
                            +{category.services.length - 3} more
                          </span>
                        </li>
                      )}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h4 className="text-lg font-bold mb-6">Company</h4>
            <ul className="space-y-3">
              <li>
                <button 
                  onClick={scrollToTop}
                  className="text-gray-300 hover:text-white transition-colors duration-200 flex items-center gap-2 group"
                >
                  <span>About</span>
                  <ArrowRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                </button>
              </li>
              <li>
                <a 
                  href="#contact"
                  className="text-gray-300 hover:text-white transition-colors duration-200 flex items-center gap-2 group"
                >
                  <span>Contact</span>
                  <ArrowRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                </a>
              </li>
              <li>
                <a 
                  href="#service-areas"
                  className="text-gray-300 hover:text-white transition-colors duration-200 flex items-center gap-2 group"
                >
                  <span>Service Areas</span>
                  <ArrowRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                </a>
              </li>
              <li>
                <a 
                  href="#reviews"
                  className="text-gray-300 hover:text-white transition-colors duration-200 flex items-center gap-2 group"
                >
                  <span>Customer Reviews</span>
                  <ArrowRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                </a>
              </li>
              <li>
                <span className="text-gray-300 hover:text-white transition-colors duration-200 cursor-pointer">
                  Careers
                </span>
              </li>
              <li>
                <span className="text-gray-300 hover:text-white transition-colors duration-200 cursor-pointer">
                  Blog
                </span>
              </li>
            </ul>
          </div>

          {/* Service Areas & Social */}
          <div>
            <h4 className="text-lg font-bold mb-6">Service Areas</h4>
            
            {/* Service Areas */}
            <div className="mb-8">
              <div className="grid grid-cols-2 gap-2 mb-4">
                {business.service_areas?.slice(0, 8).map((area, index) => (
                  <span 
                    key={index}
                    className="text-sm text-gray-300 hover:text-white transition-colors duration-200 cursor-pointer"
                  >
                    {area}
                  </span>
                ))}
              </div>
              {(business.service_areas?.length || 0) > 8 && (
                <span className="text-sm text-blue-400">
                  +{(business.service_areas?.length || 0) - 8} more locations
                </span>
              )}
            </div>

            {/* Social Media */}
            <div>
              <h5 className="font-semibold mb-4">Follow Us</h5>
              <div className="flex gap-4">
                <a 
                  href="#" 
                  className="w-10 h-10 bg-gray-800 hover:bg-blue-600 rounded-full flex items-center justify-center transition-colors duration-200"
                >
                  <Facebook className="h-5 w-5" />
                </a>
                <a 
                  href="#" 
                  className="w-10 h-10 bg-gray-800 hover:bg-blue-400 rounded-full flex items-center justify-center transition-colors duration-200"
                >
                  <Twitter className="h-5 w-5" />
                </a>
                <a 
                  href="#" 
                  className="w-10 h-10 bg-gray-800 hover:bg-pink-600 rounded-full flex items-center justify-center transition-colors duration-200"
                >
                  <Instagram className="h-5 w-5" />
                </a>
                <a 
                  href="#" 
                  className="w-10 h-10 bg-gray-800 hover:bg-blue-700 rounded-full flex items-center justify-center transition-colors duration-200"
                >
                  <Linkedin className="h-5 w-5" />
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Emergency Contact Bar */}
        <div className="mt-12 pt-8 border-t border-gray-800">
          <div className="bg-red-600 rounded-xl p-6 text-center">
            <h4 className="text-xl font-bold mb-2">24/7 Emergency Service Available</h4>
            <p className="text-red-100 mb-4">
              Need immediate assistance? Our emergency service team is standing by.
            </p>
            <button
              onClick={handleQuickCall}
              className="bg-white hover:bg-red-50 text-red-600 font-bold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2 mx-auto"
            >
              <Phone className="h-5 w-5" />
              Emergency Line: {business.phone_number}
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-gray-400 text-sm">
              © {currentYear} {business.name}. All Rights Reserved.
            </div>
            
            <div className="flex gap-6 text-sm text-gray-400">
              <a href="#" className="hover:text-white transition-colors duration-200">
                Privacy Policy
              </a>
              <a href="#" className="hover:text-white transition-colors duration-200">
                Terms and Conditions
              </a>
              <a href="#" className="hover:text-white transition-colors duration-200">
                Legal Information
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
