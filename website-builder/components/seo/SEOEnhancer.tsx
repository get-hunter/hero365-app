/**
 * SEO Enhancer Component
 * 
 * Combines structured data, internal linking, and other SEO optimizations
 * for maximum search engine visibility and user experience.
 */

import { useMemo } from 'react';
import StructuredData from './StructuredData';
import InternalLinking from './InternalLinking';

interface SEOEnhancerProps {
  businessData: {
    name: string;
    description: string;
    phone: string;
    email: string;
    address: string;
    website: string;
    serviceAreas: string[];
    trades: string[];
    rating?: number;
    reviewCount?: number;
    yearsInBusiness?: number;
    licenseNumber?: string;
  };
  pageData: {
    type: 'home' | 'about' | 'services' | 'service' | 'contact' | 'location';
    service?: string;
    location?: string;
    title?: string;
    description?: string;
  };
  servicesData?: Array<{
    name: string;
    slug: string;
    description: string;
    category: string;
    priceRange?: string;
    serviceType: string;
    areaServed: string[];
  }>;
  locationsData?: Array<{
    name: string;
    slug: string;
    serviceCount?: number;
  }>;
  showInternalLinks?: boolean;
  className?: string;
}

export default function SEOEnhancer({
  businessData,
  pageData,
  servicesData = [],
  locationsData = [],
  showInternalLinks = true,
  className = ''
}: SEOEnhancerProps) {
  
  // Generate breadcrumbs based on page type
  const breadcrumbs = useMemo(() => {
    const crumbs = [{ name: 'Home', url: '/' }];
    
    switch (pageData.type) {
      case 'about':
        crumbs.push({ name: 'About', url: '/about' });
        break;
      case 'services':
        crumbs.push({ name: 'Services', url: '/services' });
        break;
      case 'service':
        crumbs.push({ name: 'Services', url: '/services' });
        if (pageData.service) {
          const service = servicesData.find(s => s.slug === pageData.service);
          if (service) {
            crumbs.push({ name: service.name, url: `/services/${service.slug}` });
          }
        }
        break;
      case 'contact':
        crumbs.push({ name: 'Contact', url: '/contact' });
        break;
      case 'location':
        if (pageData.location) {
          const location = locationsData.find(l => l.slug === pageData.location);
          if (location) {
            crumbs.push({ name: location.name, url: `/${location.slug}` });
          }
        }
        break;
    }
    
    return crumbs;
  }, [pageData, servicesData, locationsData]);
  
  // Get current service data
  const currentService = useMemo(() => {
    if (pageData.type === 'service' && pageData.service) {
      return servicesData.find(s => s.slug === pageData.service);
    }
    return undefined;
  }, [pageData, servicesData]);
  
  // Prepare services for internal linking
  const serviceLinks = useMemo(() => {
    return servicesData.map(service => ({
      name: service.name,
      slug: service.slug,
      category: service.category,
      isRelated: currentService ? service.category === currentService.category : false
    }));
  }, [servicesData, currentService]);
  
  return (
    <div className={`seo-enhancer ${className}`}>
      {/* Structured Data */}
      <StructuredData
        business={businessData}
        services={servicesData}
        breadcrumbs={breadcrumbs}
        pageType={pageData.type}
        currentService={currentService}
        currentLocation={pageData.location}
      />
      
      {/* Internal Linking */}
      {showInternalLinks && (
        <InternalLinking
          currentPage={pageData}
          allServices={serviceLinks}
          allLocations={locationsData}
          className="mt-8"
        />
      )}
    </div>
  );
}

/**
 * Hook to generate SEO-optimized page metadata
 */
export function useSEOMetadata(
  businessData: SEOEnhancerProps['businessData'],
  pageData: SEOEnhancerProps['pageData'],
  currentService?: SEOEnhancerProps['servicesData'][0],
  currentLocation?: string
) {
  return useMemo(() => {
    const baseTitle = businessData.name;
    const baseDescription = businessData.description;
    
    let title = baseTitle;
    let description = baseDescription;
    let keywords: string[] = [...businessData.trades];
    
    switch (pageData.type) {
      case 'home':
        title = `${baseTitle} - Professional ${businessData.trades[0]} Services`;
        description = `${baseDescription} Serving ${businessData.serviceAreas.join(', ')}.`;
        keywords.push('professional services', 'licensed', 'insured');
        break;
        
      case 'about':
        title = `About ${baseTitle} - Your Trusted ${businessData.trades[0]} Experts`;
        description = `Learn about ${baseTitle} and our professional ${businessData.trades[0].toLowerCase()} services.`;
        keywords.push('about', 'company', 'professional', 'experienced');
        break;
        
      case 'services':
        title = `${businessData.trades[0]} Services - ${baseTitle}`;
        description = `Complete ${businessData.trades[0].toLowerCase()} services including installation, repair, and maintenance.`;
        keywords.push('services', 'installation', 'repair', 'maintenance');
        break;
        
      case 'service':
        if (currentService) {
          title = `${currentService.name} - ${baseTitle}`;
          description = currentService.description;
          keywords.push(currentService.name.toLowerCase(), currentService.category.toLowerCase());
        }
        break;
        
      case 'contact':
        title = `Contact ${baseTitle} - Get Your Free Estimate`;
        description = `Contact ${baseTitle} for professional ${businessData.trades[0].toLowerCase()} services. Free estimates available.`;
        keywords.push('contact', 'free estimate', 'quote');
        break;
        
      case 'location':
        if (currentLocation) {
          title = `${businessData.trades[0]} Services in ${currentLocation} - ${baseTitle}`;
          description = `Professional ${businessData.trades[0].toLowerCase()} services in ${currentLocation}. Licensed, insured, and trusted by local residents.`;
          keywords.push(currentLocation.toLowerCase(), 'local', 'area');
        }
        break;
    }
    
    return {
      title,
      description,
      keywords: keywords.join(', '),
      canonical: getCanonicalUrl(businessData.website, pageData),
      openGraph: {
        title,
        description,
        url: getCanonicalUrl(businessData.website, pageData),
        siteName: baseTitle,
        type: pageData.type === 'home' ? 'website' : 'article',
        images: [
          {
            url: `${businessData.website}/og-image.jpg`,
            width: 1200,
            height: 630,
            alt: title,
          },
        ],
      },
      twitter: {
        card: 'summary_large_image',
        title,
        description,
        images: [`${businessData.website}/og-image.jpg`],
      },
    };
  }, [businessData, pageData, currentService, currentLocation]);
}

/**
 * Generate canonical URL for the current page
 */
function getCanonicalUrl(baseUrl: string, pageData: SEOEnhancerProps['pageData']): string {
  switch (pageData.type) {
    case 'home':
      return baseUrl;
    case 'about':
      return `${baseUrl}/about`;
    case 'services':
      return `${baseUrl}/services`;
    case 'service':
      return pageData.service ? `${baseUrl}/services/${pageData.service}` : `${baseUrl}/services`;
    case 'contact':
      return `${baseUrl}/contact`;
    case 'location':
      return pageData.location ? `${baseUrl}/${pageData.location}` : baseUrl;
    default:
      return baseUrl;
  }
}
