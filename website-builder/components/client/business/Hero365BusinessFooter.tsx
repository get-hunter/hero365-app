'use client';

import React from 'react';
import { Phone, Mail, MapPin, Clock, Facebook, Twitter, Instagram, Linkedin } from 'lucide-react';
import type { BusinessData, ServiceCategory, Location } from '@/lib/shared/types/content';
import { formatPhoneForDisplay, normalizeToE164 } from '@/lib/shared/phone';
import { useWebsiteContext } from '@/lib/client/hooks/useWebsiteContext';

interface Hero365BusinessFooterProps {
  business: BusinessData;
  serviceCategories: ServiceCategory[];
  locations: Location[];
}

export default function Hero365BusinessFooter({ business, serviceCategories = [], locations = [] }: Hero365BusinessFooterProps) {
  // Get website context for activity-first approach
  const { data: websiteContext, loading, error } = useWebsiteContext(business.id);
  
  const primaryLocation = locations.find(l => l.is_primary) || locations[0];
  const currentYear = new Date().getFullYear();

  // Activity-first service description generation
  const getServiceDescription = () => {
    // NEW: Activity-first approach with rich descriptions
    if (websiteContext?.activities && websiteContext.activities.length > 0) {
      const activityNames = websiteContext.activities.slice(0, 3).map(a => a.name.toLowerCase()).join(', ');
      return `Professional ${activityNames} services with guaranteed satisfaction. Licensed, insured, and trusted by thousands of customers.`;
    }
    
    // FALLBACK: Use business description or generate from trade
    if (business.description) {
      return business.description;
    }
    
    // LEGACY: Generate from primary_trade
    if (business.primary_trade) {
      const serviceName = business.primary_trade.replace('_', ' ').toLowerCase();
      return `Professional ${serviceName} services with guaranteed satisfaction. Licensed, insured, and trusted by thousands of customers.`;
    }
    
    // DEFAULT: Generic fallback
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
                <div className="flex items-center text-gray-300">
                  <Phone className="w-4 h-4 mr-3 text-blue-400" />
                  <a 
                    href={`tel:${normalizeToE164(business.phone_number)}`}
                    className="hover:text-white transition-colors"
                  >
                    {formatPhoneForDisplay(business.phone_number)}
                  </a>
                </div>
              )}
              
              {business.business_email && (
                <div className="flex items-center text-gray-300">
                  <Mail className="w-4 h-4 mr-3 text-blue-400" />
                  <a 
                    href={`mailto:${business.business_email}`}
                    className="hover:text-white transition-colors"
                  >
                    {business.business_email}
                  </a>
                </div>
              )}
              
              {primaryLocation && (
                <div className="flex items-start text-gray-300">
                  <MapPin className="w-4 h-4 mr-3 mt-0.5 text-blue-400" />
                  <span>{primaryLocation.address}</span>
                </div>
              )}
            </div>
          </div>

          {/* Services */}
          <div>
            <h4 className="text-lg font-semibold mb-6">Our Services</h4>
            <ul className="space-y-3">
              {(
                // Flatten services across categories and take top 6 for the footer
                (serviceCategories as any[])
                  .flatMap((cat) => (cat?.services || []))
                  .slice(0, 6)
              ).map((service: any, idx: number) => (
                <li key={`${service?.slug || service?.name}-${idx}`}>
                  <a
                    href={service?.url || `/services/${service?.slug || ''}`}
                    className="text-gray-300 hover:text-white transition-colors"
                  >
                    {service?.name}
                  </a>
                </li>
              ))}
              {((serviceCategories as any[]).flatMap((c) => (c?.services || [])).length > 6) && (
                <li>
                  <a
                    href="/services"
                    className="text-blue-400 hover:text-blue-300 transition-colors font-medium"
                  >
                    View All Services →
                  </a>
                </li>
              )}
            </ul>
          </div>

          {/* Service Areas */}
          <div>
            <h4 className="text-lg font-semibold mb-6">Service Areas</h4>
            <ul className="space-y-3">
              {business.service_areas && business.service_areas.slice(0, 6).map((area, index) => (
                <li key={index}>
                  <span className="text-gray-300">{area}</span>
                </li>
              ))}
              {business.service_areas && business.service_areas.length > 6 && (
                <li>
                  <a 
                    href="/service-areas"
                    className="text-blue-400 hover:text-blue-300 transition-colors font-medium"
                  >
                    View All Areas →
                  </a>
                </li>
              )}
            </ul>
          </div>

          {/* Quick Links & Hours */}
          <div>
            <h4 className="text-lg font-semibold mb-6">Quick Links</h4>
            <ul className="space-y-3 mb-8">
              <li>
                <a href="/about" className="text-gray-300 hover:text-white transition-colors">
                  About Us
                </a>
              </li>
              <li>
                <a href="/reviews" className="text-gray-300 hover:text-white transition-colors">
                  Customer Reviews
                </a>
              </li>
              <li>
                <a href="/contact" className="text-gray-300 hover:text-white transition-colors">
                  Contact Us
                </a>
              </li>
              <li>
                <a href="/emergency" className="text-gray-300 hover:text-white transition-colors">
                  Emergency Service
                </a>
              </li>
            </ul>

            {/* Business Hours */}
            <div>
              <h5 className="font-semibold mb-3 flex items-center">
                <Clock className="w-4 h-4 mr-2 text-blue-400" />
                Business Hours
              </h5>
              <div className="text-sm text-gray-300 space-y-1">
                <div className="flex justify-between">
                  <span>Mon - Fri:</span>
                  <span>8:00 AM - 6:00 PM</span>
                </div>
                <div className="flex justify-between">
                  <span>Saturday:</span>
                  <span>9:00 AM - 4:00 PM</span>
                </div>
                <div className="flex justify-between">
                  <span>Sunday:</span>
                  <span>Emergency Only</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Emergency Banner */}
      <div className="bg-red-600 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between">
            <div className="text-center sm:text-left mb-4 sm:mb-0">
              <h3 className="text-lg font-semibold">24/7 Emergency Service Available</h3>
              <p className="text-red-100">Don't wait - call us now for immediate assistance</p>
            </div>
            <a
              href={`tel:${normalizeToE164(business.phone_number || '')}`}
              className="bg-white text-red-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Call Emergency Line
            </a>
          </div>
        </div>
      </div>

      {/* Bottom Footer */}
      <div className="bg-gray-800 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            {/* Copyright */}
            <div className="text-gray-400 text-sm mb-4 md:mb-0">
              © {currentYear} {business.name}. All rights reserved. | 
              <span className="ml-1">Licensed & Insured</span>
            </div>

            {/* Social Links */}
            <div className="flex items-center space-x-4">
              <span className="text-gray-400 text-sm mr-2">Follow Us:</span>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Facebook className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Legal Links */}
          <div className="mt-4 pt-4 border-t border-gray-700">
            <div className="flex flex-wrap justify-center md:justify-start gap-6 text-sm text-gray-400">
              <a href="/privacy-policy" className="hover:text-white transition-colors">
                Privacy Policy
              </a>
              <a href="/terms-of-service" className="hover:text-white transition-colors">
                Terms of Service
              </a>
              <a href="/warranty" className="hover:text-white transition-colors">
                Warranty Information
              </a>
              <a href="/sitemap" className="hover:text-white transition-colors">
                Sitemap
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}