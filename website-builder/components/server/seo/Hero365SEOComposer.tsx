/**
 * SEO Composer Component
 * 
 * Activity-first SEO optimization component that combines structured data, 
 * internal linking, and other SEO optimizations for maximum search engine 
 * visibility and user experience.
 */

import { useMemo } from 'react';
import StructuredData from './StructuredData';
import InternalLinking from './InternalLinking';

// Activity-aware service data interface
interface ActivityServiceData {
  slug: string;
  name: string;
  description: string;
  trade_slug: string;
  trade_name: string;
  synonyms: string[];
  tags: string[];
  priceRange?: string;
  areaServed: string[];
}

interface SEOComposerProps {
  businessData: {
    name: string;
    description: string;
    phone: string;
    email: string;
    address: string;
    website: string;
    serviceAreas: string[];
    trades?: string[]; // Legacy fallback
    primary_trade_slug?: string;
    rating?: number;
    reviewCount?: number;
    yearsInBusiness?: number;
    licenseNumber?: string;
  };
  pageData: {
    type: 'home' | 'about' | 'services' | 'service' | 'contact' | 'location' | 'activity';
    service?: string;
    activity?: string; // New: activity slug for activity pages
    location?: string;
    title?: string;
    description?: string;
  };
  // New: Activity-first services data
  activitiesData?: Array<ActivityServiceData>;
  // Legacy: Backward compatibility
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

export default function SEOComposer({
  businessData,
  pageData,
  activitiesData = [],
  servicesData = [], // Legacy fallback
  locationsData = [],
  showInternalLinks = true,
  className = ''
}: SEOComposerProps) {
  
  // Unified services data (prioritize activities, fallback to legacy services)
  const unifiedServicesData = useMemo(() => {
    if (activitiesData.length > 0) {
      return activitiesData.map(activity => ({
        name: activity.name,
        slug: activity.slug,
        description: activity.description,
        category: activity.trade_name,
        serviceType: activity.name,
        areaServed: activity.areaServed,
        priceRange: activity.priceRange,
        // Activity-specific fields
        trade_slug: activity.trade_slug,
        synonyms: activity.synonyms,
        tags: activity.tags
      }));
    }
    return servicesData;
  }, [activitiesData, servicesData]);
  
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
      case 'activity':
        crumbs.push({ name: 'Services', url: '/services' });
        const serviceSlug = pageData.service || pageData.activity;
        if (serviceSlug) {
          const service = unifiedServicesData.find(s => s.slug === serviceSlug);
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
  }, [pageData, unifiedServicesData, locationsData]);
  
  // Get current service/activity data
  const currentService = useMemo(() => {
    const serviceSlug = pageData.service || pageData.activity;
    if ((pageData.type === 'service' || pageData.type === 'activity') && serviceSlug) {
      return unifiedServicesData.find(s => s.slug === serviceSlug);
    }
    return undefined;
  }, [pageData, unifiedServicesData]);
  
  // Prepare services for internal linking
  const serviceLinks = useMemo(() => {
    return unifiedServicesData.map(service => ({
      name: service.name,
      slug: service.slug,
      category: service.category,
      isRelated: currentService ? service.category === currentService.category : false
    }));
  }, [unifiedServicesData, currentService]);
  
  return (
    <div className={`seo-composer ${className}`}>
      {/* Structured Data */}
      <StructuredData
        business={{
          ...businessData,
          trades: businessData.trades || []
        }}
        services={unifiedServicesData}
        breadcrumbs={breadcrumbs}
        pageType={pageData.type === 'activity' ? 'service' : pageData.type}
        currentService={currentService}
        currentLocation={pageData.location}
      />
      
      {/* Internal Linking */}
      {showInternalLinks && (
        <InternalLinking
          currentPage={{
            ...pageData,
            type: pageData.type === 'activity' ? 'service' : pageData.type
          }}
          allServices={serviceLinks}
          allLocations={locationsData}
          className="mt-8"
        />
      )}
    </div>
  );
}

/**
 * Hook to generate SEO-optimized page metadata (Activity-First)
 */
export function useSEOMetadata(
  businessData: SEOComposerProps['businessData'],
  pageData: SEOComposerProps['pageData'],
  activitiesData?: SEOComposerProps['activitiesData'],
  servicesData?: SEOComposerProps['servicesData'], // Legacy fallback
  currentService?: any,
  currentLocation?: string
) {
  return useMemo(() => {
    const baseTitle = businessData.name;
    const baseDescription = businessData.description;
    
    // Prioritize activities over legacy services
    const primaryServices = (activitiesData && activitiesData.length > 0) ? activitiesData : servicesData;
    const primaryService = primaryServices?.[0];
    
    let title = baseTitle;
    let description = baseDescription;
    let keywords: string[] = [];
    
    // Build keywords from activities or fallback to trades
    if (activitiesData && activitiesData.length > 0) {
      keywords = activitiesData.flatMap(activity => [
        activity.name.toLowerCase(),
        activity.trade_name.toLowerCase(),
        ...activity.tags,
        ...activity.synonyms
      ]);
    } else if (businessData.trades && businessData.trades.length > 0) {
      keywords = [...businessData.trades];
    }
    
    switch (pageData.type) {
      case 'home':
        const homeService = primaryService?.name || businessData.trades?.[0] || 'Home Services';
        title = `${baseTitle} - Professional ${homeService}`;
        description = `${baseDescription} Serving ${businessData.serviceAreas?.join(', ')}.`;
        keywords.push('professional services', 'licensed', 'insured');
        break;
        
      case 'about':
        const aboutService = primaryService?.name || businessData.trades?.[0] || 'Service';
        title = `About ${baseTitle} - Your Trusted ${aboutService} Experts`;
        description = `Learn about ${baseTitle} and our professional ${aboutService.toLowerCase()} services.`;
        keywords.push('about', 'company', 'professional', 'experienced');
        break;
        
      case 'services':
        if (primaryServices && primaryServices.length > 0) {
          title = `Our Services - ${baseTitle}`;
          description = `Complete range of professional services including ${primaryServices.slice(0, 3).map(s => s.name.toLowerCase()).join(', ')}.`;
        } else {
          const fallbackService = businessData.trades?.[0] || 'Professional';
          title = `${fallbackService} Services - ${baseTitle}`;
          description = `Complete ${fallbackService.toLowerCase()} services including installation, repair, and maintenance.`;
        }
        keywords.push('services', 'installation', 'repair', 'maintenance');
        break;
        
      case 'service':
      case 'activity':
        if (currentService) {
          title = `${currentService.name} - ${baseTitle}`;
          description = currentService.description;
          keywords.push(currentService.name.toLowerCase());
          if (currentService.category) {
            keywords.push(currentService.category.toLowerCase());
          }
          // Add activity-specific keywords
          if (currentService.tags) {
            keywords.push(...currentService.tags);
          }
          if (currentService.synonyms) {
            keywords.push(...currentService.synonyms);
          }
        }
        break;
        
      case 'contact':
        title = `Contact ${baseTitle} - Get Your Free Estimate`;
        const contactService = primaryService?.name || businessData.trades?.[0] || 'services';
        description = `Contact ${baseTitle} for professional ${contactService.toLowerCase()}. Free estimates available.`;
        keywords.push('contact', 'free estimate', 'quote');
        break;
        
      case 'location':
        if (currentLocation) {
          const locationService = primaryService?.name || businessData.trades?.[0] || 'Services';
          title = `${locationService} in ${currentLocation} - ${baseTitle}`;
          description = `Professional ${locationService.toLowerCase()} in ${currentLocation}. Licensed, insured, and trusted by local residents.`;
          keywords.push(currentLocation.toLowerCase(), 'local', 'area');
        }
        break;
    }
    
    return {
      title,
      description,
      keywords: [...new Set(keywords)].join(', '), // Remove duplicates
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
  }, [businessData, pageData, activitiesData, servicesData, currentService, currentLocation]);
}

/**
 * Generate canonical URL for the current page
 */
function getCanonicalUrl(baseUrl: string, pageData: SEOComposerProps['pageData']): string {
  switch (pageData.type) {
    case 'home':
      return baseUrl;
    case 'about':
      return `${baseUrl}/about`;
    case 'services':
      return `${baseUrl}/services`;
    case 'service':
      return pageData.service ? `${baseUrl}/services/${pageData.service}` : `${baseUrl}/services`;
    case 'activity':
      return pageData.activity ? `${baseUrl}/services/${pageData.activity}` : `${baseUrl}/services`;
    case 'contact':
      return `${baseUrl}/contact`;
    case 'location':
      return pageData.location ? `${baseUrl}/${pageData.location}` : baseUrl;
    default:
      return baseUrl;
  }
}
