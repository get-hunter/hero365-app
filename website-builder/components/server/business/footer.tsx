/**
 * Hero365 Business Footer Component - Server Component Version
 * 
 * Professional footer with business information, contact details, and links
 * Pure server component for SSR compatibility
 */

import React from 'react';
import type { BusinessData, ServiceCategory, Location } from '@/lib/shared/types/content';

interface Hero365BusinessFooterProps {
  business: BusinessData;
  serviceCategories: ServiceCategory[];
  locations: Location[];
}

// SSR-safe phone formatting
function formatPhoneForDisplay(phone: string): string {
  if (!phone) return '';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  if (cleaned.length === 11 && cleaned[0] === '1') {
    return `(${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  }
  return phone;
}

export default function Footer({ 
  business, 
  serviceCategories = [], 
  locations = [] 
}: Hero365BusinessFooterProps) {
  
  const primaryLocation = locations.find(l => l.is_primary) || locations[0];
  const currentYear = new Date().getFullYear();

  // Generate service description
  const getServiceDescription = () => {
    if (business.description) {
      return business.description;
    }
    
    if (business.primary_trade) {
      const serviceName = business.primary_trade.replace('_', ' ').toLowerCase();
      return `Professional ${serviceName} services with guaranteed satisfaction. Licensed, insured, and trusted by thousands of customers.`;
    }
    
    return 'Professional services with guaranteed satisfaction. Licensed, insured, and trusted by thousands of customers.';
  };

  return (
    <footer className="bg-gray-900 text-white">
      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="lg:col-span-1">
            <div className="mb-6">
              {business.logo_url ? (
                <img 
                  src={business.logo_url} 
                  alt={`${business.name} logo`}
                  className="h-12 w-auto"
                />
              ) : (
                <h3 className="text-2xl font-bold">{business.name}</h3>
              )}
            </div>
            
            <p className="text-gray-300 mb-6 leading-relaxed">
              {getServiceDescription()}
            </p>

            {/* Contact Info */}
            <div className="space-y-3">
              {business.phone_number && (
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-blue-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <a 
                    href={`tel:${business.phone_number}`}
                    className="text-gray-300 hover:text-white transition-colors"
                  >
                    {formatPhoneForDisplay(business.phone_number)}
                  </a>
                </div>
              )}

              {business.business_email && (
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-blue-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <a 
                    href={`mailto:${business.business_email}`}
                    className="text-gray-300 hover:text-white transition-colors"
                  >
                    {business.business_email}
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
                  </span>
                </div>
              )}

              <div className="flex items-center">
                <svg className="h-5 w-5 text-blue-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-gray-300">24/7 Emergency Service</span>
              </div>
            </div>
          </div>

          {/* Services */}
          <div>
            <h4 className="text-lg font-semibold mb-6">Our Services</h4>
            <ul className="space-y-3">
              {serviceCategories.slice(0, 6).map((category) => (
                <li key={category.id}>
                  <a 
                    href={`/services/${category.slug}`}
                    className="text-gray-300 hover:text-white transition-colors"
                  >
                    {category.name}
                  </a>
                </li>
              ))}
              {serviceCategories.length === 0 && (
                <>
                  <li><a href="/services/hvac" className="text-gray-300 hover:text-white transition-colors">HVAC Services</a></li>
                  <li><a href="/services/plumbing" className="text-gray-300 hover:text-white transition-colors">Plumbing</a></li>
                  <li><a href="/services/electrical" className="text-gray-300 hover:text-white transition-colors">Electrical</a></li>
                  <li><a href="/services/maintenance" className="text-gray-300 hover:text-white transition-colors">Maintenance</a></li>
                  <li><a href="/services/emergency" className="text-gray-300 hover:text-white transition-colors">Emergency Repair</a></li>
                  <li><a href="/services" className="text-gray-300 hover:text-white transition-colors">View All Services</a></li>
                </>
              )}
            </ul>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-6">Quick Links</h4>
            <ul className="space-y-3">
              <li><a href="/about" className="text-gray-300 hover:text-white transition-colors">About Us</a></li>
              <li><a href="/projects" className="text-gray-300 hover:text-white transition-colors">Our Projects</a></li>
              <li><a href="/pricing" className="text-gray-300 hover:text-white transition-colors">Pricing</a></li>
              <li><a href="/booking" className="text-gray-300 hover:text-white transition-colors">Book Service</a></li>
              <li><a href="/contact" className="text-gray-300 hover:text-white transition-colors">Contact</a></li>
              <li><a href="/reviews" className="text-gray-300 hover:text-white transition-colors">Reviews</a></li>
            </ul>
          </div>

          {/* Service Areas */}
          <div>
            <h4 className="text-lg font-semibold mb-6">Service Areas</h4>
            <ul className="space-y-3">
              {business.service_areas && business.service_areas.length > 0 ? (
                business.service_areas.slice(0, 6).map((area, index) => (
                  <li key={index}>
                    <span className="text-gray-300">{area}</span>
                  </li>
                ))
              ) : (
                <>
                  <li><span className="text-gray-300">Austin, TX</span></li>
                  <li><span className="text-gray-300">Round Rock, TX</span></li>
                  <li><span className="text-gray-300">Cedar Park, TX</span></li>
                  <li><span className="text-gray-300">Georgetown, TX</span></li>
                  <li><span className="text-gray-300">Pflugerville, TX</span></li>
                  <li><span className="text-gray-300">Leander, TX</span></li>
                </>
              )}
            </ul>
          </div>
        </div>

        {/* Social Media & Certifications */}
        <div className="border-t border-gray-800 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            {/* Social Media */}
            <div className="flex space-x-6 mb-6 md:mb-0">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <span className="sr-only">Facebook</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clipRule="evenodd" />
                </svg>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <span className="sr-only">Instagram</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 6.62 5.367 11.987 11.988 11.987s11.987-5.367 11.987-11.987C24.014 5.367 18.647.001 12.017.001zM8.449 16.988c-1.297 0-2.448-.49-3.323-1.297C4.198 14.895 3.708 13.744 3.708 12.447s.49-2.448 1.418-3.323c.875-.807 2.026-1.297 3.323-1.297s2.448.49 3.323 1.297c.928.875 1.418 2.026 1.418 3.323s-.49 2.448-1.418 3.244c-.875.807-2.026 1.297-3.323 1.297zm7.83-9.405c-.49 0-.928-.175-1.297-.49-.367-.315-.49-.753-.49-1.243 0-.49.123-.928.49-1.243.369-.367.807-.49 1.297-.49s.928.123 1.297.49c.367.315.49.753.49 1.243 0 .49-.123.928-.49 1.243-.369.315-.807.49-1.297.49z" clipRule="evenodd" />
                </svg>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <span className="sr-only">LinkedIn</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" clipRule="evenodd" />
                </svg>
              </a>
            </div>

            {/* Certifications */}
            <div className="flex items-center space-x-6 text-sm text-gray-400">
              <div className="flex items-center">
                <svg className="h-5 w-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Licensed & Insured
              </div>
              <div className="flex items-center">
                <svg className="h-5 w-5 text-yellow-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
                BBB Accredited
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="bg-gray-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center text-sm text-gray-400">
            <p>&copy; {currentYear} {business.name}. All rights reserved.</p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="/privacy" className="hover:text-white transition-colors">Privacy Policy</a>
              <a href="/terms" className="hover:text-white transition-colors">Terms of Service</a>
              <a href="/sitemap.xml" className="hover:text-white transition-colors">Sitemap</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
