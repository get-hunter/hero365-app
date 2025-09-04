/**
 * Internal Linking Component
 * 
 * Generates contextual internal links for better SEO and user navigation.
 * Includes related services, location-based links, and cross-references.
 */

import Link from 'next/link';
import { useMemo } from 'react';

interface ServiceLink {
  name: string;
  slug: string;
  category: string;
  isRelated?: boolean;
}

interface LocationLink {
  name: string;
  slug: string;
  serviceCount?: number;
}

interface InternalLinkingProps {
  currentPage: {
    type: 'home' | 'about' | 'services' | 'service' | 'contact' | 'location';
    service?: string;
    location?: string;
  };
  allServices: ServiceLink[];
  allLocations: LocationLink[];
  maxRelatedLinks?: number;
  maxLocationLinks?: number;
  className?: string;
}

export default function InternalLinking({
  currentPage,
  allServices,
  allLocations,
  maxRelatedLinks = 6,
  maxLocationLinks = 8,
  className = ''
}: InternalLinkingProps) {
  
  const relatedServices = useMemo(() => {
    if (currentPage.type !== 'service' || !currentPage.service) {
      return [];
    }
    
    const currentService = allServices.find(s => s.slug === currentPage.service);
    if (!currentService) return [];
    
    // Find services in the same category
    const sameCategory = allServices.filter(s => 
      s.category === currentService.category && 
      s.slug !== currentService.slug
    );
    
    // Find other related services (simple keyword matching)
    const otherRelated = allServices.filter(s => 
      s.category !== currentService.category &&
      s.slug !== currentService.slug &&
      (s.name.toLowerCase().includes(currentService.name.split(' ')[0].toLowerCase()) ||
       currentService.name.toLowerCase().includes(s.name.split(' ')[0].toLowerCase()))
    );
    
    return [...sameCategory, ...otherRelated].slice(0, maxRelatedLinks);
  }, [currentPage, allServices, maxRelatedLinks]);
  
  const serviceLocationLinks = useMemo(() => {
    if (currentPage.type !== 'service' || !currentPage.service) {
      return [];
    }
    
    return allLocations.slice(0, maxLocationLinks).map(location => ({
      ...location,
      url: `/${location.slug}/${currentPage.service}`,
      linkText: `${allServices.find(s => s.slug === currentPage.service)?.name} in ${location.name}`
    }));
  }, [currentPage, allServices, allLocations, maxLocationLinks]);
  
  const locationServiceLinks = useMemo(() => {
    if (currentPage.type !== 'location' || !currentPage.location) {
      return [];
    }
    
    return allServices.slice(0, maxRelatedLinks).map(service => ({
      ...service,
      url: `/${currentPage.location}/${service.slug}`,
      linkText: `${service.name} in ${allLocations.find(l => l.slug === currentPage.location)?.name}`
    }));
  }, [currentPage, allServices, allLocations, maxRelatedLinks]);
  
  const breadcrumbLinks = useMemo(() => {
    const links = [{ name: 'Home', url: '/' }];
    
    switch (currentPage.type) {
      case 'about':
        links.push({ name: 'About', url: '/about' });
        break;
      case 'services':
        links.push({ name: 'Services', url: '/services' });
        break;
      case 'service':
        links.push({ name: 'Services', url: '/services' });
        if (currentPage.service) {
          const service = allServices.find(s => s.slug === currentPage.service);
          if (service) {
            links.push({ name: service.name, url: `/services/${service.slug}` });
          }
        }
        break;
      case 'contact':
        links.push({ name: 'Contact', url: '/contact' });
        break;
      case 'location':
        if (currentPage.location) {
          const location = allLocations.find(l => l.slug === currentPage.location);
          if (location) {
            links.push({ name: location.name, url: `/${location.slug}` });
          }
        }
        break;
    }
    
    return links;
  }, [currentPage, allServices, allLocations]);
  
  if (currentPage.type === 'home') {
    return (
      <div className={`internal-links ${className}`}>
        {/* Featured Services Links */}
        <section className="featured-services-links mb-8">
          <h2 className="text-2xl font-bold mb-4">Our Services</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {allServices.slice(0, 6).map((service) => (
              <Link
                key={service.slug}
                href={`/services/${service.slug}`}
                className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <h3 className="font-semibold text-blue-600">{service.name}</h3>
                <p className="text-sm text-gray-600">{service.category}</p>
              </Link>
            ))}
          </div>
        </section>
        
        {/* Service Areas Links */}
        <section className="service-areas-links">
          <h2 className="text-2xl font-bold mb-4">Service Areas</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {allLocations.slice(0, 8).map((location) => (
              <Link
                key={location.slug}
                href={`/${location.slug}`}
                className="block p-3 text-center bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <span className="font-medium text-blue-700">{location.name}</span>
                {location.serviceCount && (
                  <span className="block text-xs text-gray-600 mt-1">
                    {location.serviceCount} services
                  </span>
                )}
              </Link>
            ))}
          </div>
        </section>
      </div>
    );
  }
  
  return (
    <div className={`internal-links ${className}`}>
      {/* Breadcrumbs */}
      <nav className="breadcrumbs mb-6" aria-label="Breadcrumb">
        <ol className="flex items-center space-x-2 text-sm">
          {breadcrumbLinks.map((link, index) => (
            <li key={link.url} className="flex items-center">
              {index > 0 && <span className="mx-2 text-gray-400">/</span>}
              {index === breadcrumbLinks.length - 1 ? (
                <span className="text-gray-600">{link.name}</span>
              ) : (
                <Link href={link.url} className="text-blue-600 hover:text-blue-800">
                  {link.name}
                </Link>
              )}
            </li>
          ))}
        </ol>
      </nav>
      
      {/* Related Services (for service pages) */}
      {relatedServices.length > 0 && (
        <section className="related-services mb-8">
          <h2 className="text-xl font-bold mb-4">Related Services</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {relatedServices.map((service) => (
              <Link
                key={service.slug}
                href={`/services/${service.slug}`}
                className="block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all"
              >
                <h3 className="font-semibold text-blue-600 mb-1">{service.name}</h3>
                <p className="text-sm text-gray-600">{service.category}</p>
              </Link>
            ))}
          </div>
        </section>
      )}
      
      {/* Service in Locations (for service pages) */}
      {serviceLocationLinks.length > 0 && (
        <section className="service-locations mb-8">
          <h2 className="text-xl font-bold mb-4">
            {allServices.find(s => s.slug === currentPage.service)?.name} by Location
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {serviceLocationLinks.map((link) => (
              <Link
                key={link.url}
                href={link.url}
                className="block p-3 text-center bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <span className="text-sm font-medium text-gray-800">
                  {link.location.name}
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}
      
      {/* Services in Location (for location pages) */}
      {locationServiceLinks.length > 0 && (
        <section className="location-services mb-8">
          <h2 className="text-xl font-bold mb-4">
            Services in {allLocations.find(l => l.slug === currentPage.location)?.name}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {locationServiceLinks.map((link) => (
              <Link
                key={link.url}
                href={link.url}
                className="block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all"
              >
                <h3 className="font-semibold text-blue-600 mb-1">{link.service.name}</h3>
                <p className="text-sm text-gray-600">{link.service.category}</p>
              </Link>
            ))}
          </div>
        </section>
      )}
      
      {/* Quick Navigation */}
      <section className="quick-nav">
        <h2 className="text-lg font-bold mb-3">Quick Navigation</h2>
        <div className="flex flex-wrap gap-2">
          <Link href="/" className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors">
            Home
          </Link>
          <Link href="/services" className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors">
            All Services
          </Link>
          <Link href="/about" className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors">
            About Us
          </Link>
          <Link href="/contact" className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors">
            Contact
          </Link>
        </div>
      </section>
    </div>
  );
}
