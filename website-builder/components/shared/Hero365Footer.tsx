/**
 * Hero365 Footer Component
 * 
 * A single, consistent footer component that can be used across all pages
 * Works as a server component by default, with optional client features
 */

import React from 'react';
import Link from 'next/link';
import { formatPhoneForDisplay, normalizeToE164 } from '@/lib/shared/utils/formatters';
import type { BusinessProfile, ServiceItem, LocationItem } from '@/lib/shared/types/api-responses';

interface Hero365FooterProps {
  business: BusinessProfile;
  services?: ServiceItem[];
  locations?: LocationItem[];
  showEmergencyBanner?: boolean;
  className?: string;
}

export default function Hero365Footer({
  business,
  services = [],
  locations = [],
  showEmergencyBanner = true,
  className = ''
}: Hero365FooterProps) {
  
  const currentYear = new Date().getFullYear();
  const primaryLocation = locations.find(l => l.is_primary) || locations[0];
  
  // Get top services for footer
  const topServices = services
    .filter(s => s.is_featured)
    .concat(services.filter(s => !s.is_featured))
    .slice(0, 6);

  // Get service areas
  const serviceAreas = business.service_areas || [];
  const topServiceAreas = serviceAreas.slice(0, 6);

  return (
    <footer className={`bg-gray-900 text-white ${className}`}>
      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          
          {/* Company Info */}
          <div className="lg:col-span-1">
            <h3 className="text-2xl font-bold mb-4">{business.business_name}</h3>
            <p className="text-gray-300 mb-6">
              {business.description || `Professional services with guaranteed satisfaction. Licensed, insured, and trusted by thousands of customers.`}
            </p>
            
            {/* Contact Info */}
            <div className="space-y-3">
              {business.phone && (
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-blue-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <a 
                    href={`tel:${normalizeToE164(business.phone)}`}
                    className="text-gray-300 hover:text-white transition-colors"
                  >
                    {formatPhoneForDisplay(business.phone)}
                  </a>
                </div>
              )}
              
              {business.email && (
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-blue-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <a 
                    href={`mailto:${business.email}`}
                    className="text-gray-300 hover:text-white transition-colors"
                  >
                    {business.email}
                  </a>
                </div>
              )}
              
              {(business.address || primaryLocation?.address) && (
                <div className="flex items-start">
                  <svg className="h-5 w-5 text-blue-400 mr-3 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span className="text-gray-300">
                    {business.address || primaryLocation?.address}
                    {(business.city || primaryLocation?.city) && (
                      <>, {business.city || primaryLocation?.city}, {business.state || primaryLocation?.state}</>
                    )}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Services */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Services</h4>
            <ul className="space-y-2 text-gray-300">
              {topServices.length > 0 ? (
                <>
                  {topServices.map((service) => (
                    <li key={service.id}>
                      <Link 
                        href={`/services/${service.slug}`}
                        className="hover:text-white transition-colors"
                      >
                        {service.name}
                      </Link>
                    </li>
                  ))}
                  {services.length > 6 && (
                    <li>
                      <Link 
                        href="/services"
                        className="text-blue-400 hover:text-blue-300 transition-colors font-medium"
                      >
                        View All Services →
                      </Link>
                    </li>
                  )}
                </>
              ) : (
                <>
                  <li><Link href="/services" className="hover:text-white transition-colors">All Services</Link></li>
                  <li><Link href="/emergency" className="hover:text-white transition-colors">Emergency Service</Link></li>
                  <li><Link href="/maintenance" className="hover:text-white transition-colors">Maintenance Plans</Link></li>
                </>
              )}
            </ul>
          </div>

          {/* Service Areas */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Service Areas</h4>
            <ul className="space-y-2 text-gray-300">
              {topServiceAreas.length > 0 ? (
                <>
                  {topServiceAreas.map((area, index) => (
                    <li key={`${area}-${index}`}>
                      <span>{area}</span>
                    </li>
                  ))}
                  {serviceAreas.length > 6 && (
                    <li>
                      <Link 
                        href="/locations"
                        className="text-blue-400 hover:text-blue-300 transition-colors font-medium"
                      >
                        View All Areas →
                      </Link>
                    </li>
                  )}
                </>
              ) : locations.length > 0 ? (
                <>
                  {locations.slice(0, 6).map((location, i) => (
                    <li key={location.id ?? `${location.city}-${location.state}-${i}`}>
                      <span>{location.city}, {location.state}</span>
                    </li>
                  ))}
                </>
              ) : (
                <li><span className="text-gray-400">Contact us for service area information</span></li>
              )}
            </ul>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-gray-300">
              <li><Link href="/about" className="hover:text-white transition-colors">About Us</Link></li>
              <li><Link href="/projects" className="hover:text-white transition-colors">Our Work</Link></li>
              <li><Link href="/products" className="hover:text-white transition-colors">Products</Link></li>
              <li><Link href="/contact" className="hover:text-white transition-colors">Get Quote</Link></li>
              <li><Link href="/booking" className="hover:text-white transition-colors">Book Online</Link></li>
              <li><Link href="/reviews" className="hover:text-white transition-colors">Reviews</Link></li>
            </ul>
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="mt-12 pt-8 border-t border-gray-800">
          <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-400">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Licensed & Insured
            </div>
            
            {business.average_rating && business.average_rating > 0 && (
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-2 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                {business.average_rating.toFixed(1)} Star Rating
              </div>
            )}
            
            {business.years_in_business && business.years_in_business > 0 && (
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {business.years_in_business}+ Years Experience
              </div>
            )}
            
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              24/7 Emergency Service
            </div>
          </div>
        </div>
      </div>

      {/* Emergency Banner */}
      {showEmergencyBanner && business.emergency_service && business.phone && (
        <div className="bg-red-600">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex flex-col sm:flex-row items-center justify-between">
              <div className="text-center sm:text-left mb-4 sm:mb-0">
                <h3 className="text-lg font-semibold">24/7 Emergency Service Available</h3>
                <p className="text-red-100">Don't wait - call us now for immediate assistance</p>
              </div>
              <a
                href={`tel:${normalizeToE164(business.phone)}`}
                className="bg-white text-red-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
              >
                Call Emergency Line
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Bar */}
      <div className="bg-gray-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm mb-4 md:mb-0">
              © {currentYear} {business.business_name}. All rights reserved.
              {business.license_number && <span className="ml-2">| License #{business.license_number}</span>}
            </p>
            
            <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-400">
              <Link href="/privacy-policy" className="hover:text-white transition-colors">
                Privacy Policy
              </Link>
              <Link href="/terms-of-service" className="hover:text-white transition-colors">
                Terms of Service
              </Link>
              <Link href="/sitemap" className="hover:text-white transition-colors">
                Sitemap
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
