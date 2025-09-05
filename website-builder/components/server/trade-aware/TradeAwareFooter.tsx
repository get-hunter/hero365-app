/**
 * Trade-Aware Footer Component - SSR Optimized
 * 
 * Generates dynamic footer content based on:
 * - Business activities and services
 * - Service areas and locations
 * - Trade-specific certifications
 * - Contact information and hours
 * - Legal and compliance information
 * 
 * This is a server-side component for optimal SEO and site structure.
 */

import React from 'react';
import Link from 'next/link';
import { BusinessContext, ActivityInfo, ServiceArea } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';

interface TradeAwareFooterProps {
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  activities: ActivityInfo[];
  serviceAreas: ServiceArea[];
  showServiceLinks?: boolean;
  showLocationLinks?: boolean;
  showCertifications?: boolean;
  showSocialLinks?: boolean;
  className?: string;
}

interface FooterSection {
  title: string;
  links: FooterLink[];
}

interface FooterLink {
  label: string;
  href: string;
  external?: boolean;
  description?: string;
}

export function TradeAwareFooter({ 
  businessContext, 
  tradeConfig,
  activities,
  serviceAreas,
  showServiceLinks = true,
  showLocationLinks = true,
  showCertifications = true,
  showSocialLinks = true,
  className = '' 
}: TradeAwareFooterProps) {
  
  // Generate footer sections based on business context
  const footerSections = generateFooterSections(
    businessContext,
    tradeConfig,
    activities,
    serviceAreas,
    { showServiceLinks, showLocationLinks }
  );
  
  return (
    <footer className={`bg-gray-900 text-white ${className}`}>
      
      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          
          {/* Company Information */}
          <div className="lg:col-span-1">
            <div className="mb-6">
              <h3 className="text-xl font-bold mb-4">
                {businessContext.business.name}
              </h3>
              <p className="text-gray-300 mb-4">
                Professional {tradeConfig.display_name.toLowerCase()} services 
                in {businessContext.primary_area?.city || 'your area'} with{' '}
                {businessContext.combined_experience_years}+ years of combined experience.
              </p>
              
              {/* Contact Information */}
              <div className="space-y-2">
                <div className="flex items-center">
                  <svg className="w-5 h-5 mr-3 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <a 
                    href={`tel:${businessContext.business.phone}`}
                    className="text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    {businessContext.business.phone}
                  </a>
                </div>
                
                <div className="flex items-center">
                  <svg className="w-5 h-5 mr-3 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <a 
                    href={`mailto:${businessContext.business.email}`}
                    className="text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    {businessContext.business.email}
                  </a>
                </div>
                
                {businessContext.business.address && (
                  <div className="flex items-start">
                    <svg className="w-5 h-5 mr-3 mt-0.5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <div className="text-gray-300">
                      <div>{businessContext.business.address}</div>
                      <div>
                        {businessContext.business.city}, {businessContext.business.state} {businessContext.business.postal_code}
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Emergency Service Badge */}
              {tradeConfig.emergency_services && (
                <div className="mt-4 p-3 bg-red-600 rounded-lg">
                  <div className="flex items-center">
                    <span className="text-lg mr-2">🚨</span>
                    <div>
                      <div className="font-semibold">24/7 Emergency Service</div>
                      <div className="text-sm text-red-100">
                        Call {businessContext.business.phone} anytime
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Dynamic Footer Sections */}
          {footerSections.map((section, index) => (
            <div key={section.title} className="lg:col-span-1">
              <h4 className="text-lg font-semibold mb-4">{section.title}</h4>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.href}>
                    {link.external ? (
                      <a
                        href={link.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-gray-300 hover:text-white transition-colors text-sm"
                      >
                        {link.label}
                      </a>
                    ) : (
                      <Link
                        href={link.href}
                        className="text-gray-300 hover:text-white transition-colors text-sm"
                      >
                        {link.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
          
        </div>
        
        {/* Certifications & Trust Indicators */}
        {showCertifications && businessContext.total_certifications.length > 0 && (
          <div className="mt-12 pt-8 border-t border-gray-800">
            <h4 className="text-lg font-semibold mb-4 text-center">
              Licensed & Certified Professionals
            </h4>
            <div className="flex flex-wrap justify-center gap-4">
              {businessContext.total_certifications.slice(0, 6).map((cert, index) => (
                <div 
                  key={index}
                  className="bg-gray-800 px-4 py-2 rounded-lg text-sm text-center"
                >
                  <div className="font-medium text-blue-400">✓</div>
                  <div className="text-gray-300">{cert}</div>
                </div>
              ))}
            </div>
            
            {/* Additional Trust Indicators */}
            <div className="flex flex-wrap justify-center gap-6 mt-6 text-sm text-gray-400">
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-2 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Licensed & Insured
              </div>
              
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-2 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                {businessContext.average_rating.toFixed(1)} Star Rating
              </div>
              
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                {businessContext.technicians.length} Expert Technicians
              </div>
              
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-2 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {businessContext.completed_count}+ Projects Completed
              </div>
            </div>
          </div>
        )}
        
        {/* Social Links */}
        {showSocialLinks && (
          <div className="mt-8 pt-8 border-t border-gray-800">
            <div className="flex justify-center space-x-6">
              <SocialLink 
                href={`https://www.facebook.com/search/top?q=${encodeURIComponent(businessContext.business.name)}`}
                icon="facebook"
                label="Facebook"
              />
              <SocialLink 
                href={`https://www.google.com/search?q=${encodeURIComponent(businessContext.business.name + ' ' + businessContext.business.city)}`}
                icon="google"
                label="Google Reviews"
              />
              <SocialLink 
                href={`https://www.yelp.com/search?find_desc=${encodeURIComponent(businessContext.business.name)}&find_loc=${encodeURIComponent(businessContext.business.city + ', ' + businessContext.business.state)}`}
                icon="yelp"
                label="Yelp"
              />
            </div>
          </div>
        )}
      </div>
      
      {/* Bottom Bar */}
      <div className="bg-gray-950 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center text-sm text-gray-400">
            <div className="mb-2 md:mb-0">
              © {new Date().getFullYear()} {businessContext.business.name}. All rights reserved.
            </div>
            
            <div className="flex space-x-6">
              <Link href="/privacy" className="hover:text-white transition-colors">
                Privacy Policy
              </Link>
              <Link href="/terms" className="hover:text-white transition-colors">
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

/**
 * Social Media Link Component
 */
function SocialLink({ 
  href, 
  icon, 
  label 
}: { 
  href: string; 
  icon: string; 
  label: string; 
}) {
  const getIcon = () => {
    switch (icon) {
      case 'facebook':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M20 10C20 4.477 15.523 0 10 0S0 4.477 0 10c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V10h2.54V7.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V10h2.773l-.443 2.89h-2.33v6.988C16.343 19.128 20 14.991 20 10z" clipRule="evenodd" />
          </svg>
        );
      case 'google':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10.2 2.4c2.1 0 3.9.8 5.3 2.1l-2.1 2.1c-.6-.6-1.5-1.3-3.2-1.3-2.7 0-4.9 2.2-4.9 4.9s2.2 4.9 4.9 4.9c3.1 0 4.3-2.2 4.5-3.4H10.2V8.9h7.5c.1.4.1.9.1 1.4 0 4.8-3.2 8.2-7.6 8.2-4.4 0-8-3.6-8-8s3.6-8 8-8z" />
          </svg>
        );
      case 'yelp':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 0C4.477 0 0 4.477 0 10s4.477 10 10 10 10-4.477 10-10S15.523 0 10 0zm3.5 16l-1.414-1.414L13.5 13.172 15.914 15.586 14.5 17zm-7-7L5.086 7.586 6.5 6.172 8.914 8.586 7.5 10zm7-7L15.914 4.414 14.5 3 12.086 5.414 13.5 6.828z" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-gray-400 hover:text-white transition-colors"
      aria-label={label}
    >
      {getIcon()}
    </a>
  );
}

/**
 * Generate footer sections based on business context
 */
function generateFooterSections(
  businessContext: BusinessContext,
  tradeConfig: TradeConfiguration,
  activities: ActivityInfo[],
  serviceAreas: ServiceArea[],
  options: { showServiceLinks: boolean; showLocationLinks: boolean }
): FooterSection[] {
  
  const sections: FooterSection[] = [];
  
  // Services Section
  if (options.showServiceLinks && activities.length > 0) {
    const serviceLinks: FooterLink[] = [];
    
    // Featured services
    const featuredServices = activities.filter(a => a.is_featured).slice(0, 6);
    featuredServices.forEach(activity => {
      serviceLinks.push({
        label: activity.name,
        href: `/services/${activity.slug}`,
        description: `Professional ${activity.name.toLowerCase()} services`
      });
    });
    
    // Add remaining popular services
    const remainingServices = activities
      .filter(a => !a.is_featured)
      .sort((a, b) => b.booking_frequency - a.booking_frequency)
      .slice(0, 6 - featuredServices.length);
    
    remainingServices.forEach(activity => {
      serviceLinks.push({
        label: activity.name,
        href: `/services/${activity.slug}`
      });
    });
    
    // Add emergency services if available
    if (tradeConfig.emergency_services) {
      serviceLinks.push({
        label: `Emergency ${tradeConfig.display_name}`,
        href: '/emergency'
      });
    }
    
    sections.push({
      title: `${tradeConfig.display_name} Services`,
      links: serviceLinks
    });
  }
  
  // Locations Section
  if (options.showLocationLinks && serviceAreas.length > 0) {
    const locationLinks: FooterLink[] = serviceAreas.map(area => ({
      label: area.name,
      href: `/locations/${area.slug}`,
      description: `${tradeConfig.display_name} services in ${area.name}`
    }));
    
    // Add general service areas page
    locationLinks.unshift({
      label: 'All Service Areas',
      href: '/service-areas'
    });
    
    sections.push({
      title: 'Service Areas',
      links: locationLinks
    });
  }
  
  // Company Section
  const companyLinks: FooterLink[] = [
    { label: 'About Us', href: '/about' },
    { label: 'Our Team', href: '/team' },
    { label: 'Reviews', href: '/reviews' },
    { label: 'Projects', href: '/projects' },
    { label: 'Contact', href: '/contact' },
    { label: 'Careers', href: '/careers' }
  ];
  
  sections.push({
    title: 'Company',
    links: companyLinks
  });
  
  // Resources Section
  const resourceLinks: FooterLink[] = [
    { label: 'FAQ', href: '/faq' },
    { label: 'Blog', href: '/blog' },
    { label: 'Maintenance Tips', href: '/maintenance' },
    { label: 'Warranty Info', href: '/warranty' },
    { label: 'Financing', href: '/financing' },
    { label: 'Get Quote', href: '/quote' }
  ];
  
  sections.push({
    title: 'Resources',
    links: resourceLinks
  });
  
  return sections;
}
