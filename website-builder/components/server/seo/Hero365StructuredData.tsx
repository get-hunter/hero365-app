/**
 * Structured Data Component
 * 
 * Generates JSON-LD structured data for better SEO and rich results.
 * Supports LocalBusiness, Service, BreadcrumbList, and other schema types.
 */

import Head from 'next/head';

interface BusinessData {
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
}

interface ServiceData {
  name: string;
  description: string;
  category: string;
  priceRange?: string;
  serviceType: string;
  areaServed: string[];
}

interface BreadcrumbItem {
  name: string;
  url: string;
}

interface StructuredDataProps {
  business: BusinessData;
  services?: ServiceData[];
  breadcrumbs?: BreadcrumbItem[];
  pageType?: 'home' | 'about' | 'services' | 'service' | 'contact' | 'location';
  currentService?: ServiceData;
  currentLocation?: string;
}

export default function StructuredData({
  business,
  services = [],
  breadcrumbs = [],
  pageType = 'home',
  currentService,
  currentLocation
}: StructuredDataProps) {
  
  const generateLocalBusinessSchema = () => ({
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": `${business.website}#business`,
    "name": business.name,
    "description": business.description,
    "url": business.website,
    "telephone": business.phone,
    "email": business.email,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": business.address,
      "addressLocality": business.serviceAreas[0] || "Local Area",
      "addressRegion": "TX", // TODO: Make dynamic
      "postalCode": "78701", // TODO: Make dynamic
      "addressCountry": "US"
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": "30.2672", // TODO: Make dynamic
      "longitude": "-97.7431" // TODO: Make dynamic
    },
    "areaServed": business.serviceAreas.map(area => ({
      "@type": "City",
      "name": area
    })),
    "serviceType": business.trades,
    "priceRange": "$$",
    "openingHours": [
      "Mo-Fr 08:00-18:00",
      "Sa 09:00-17:00"
    ],
    "paymentAccepted": ["Cash", "Credit Card", "Check"],
    "currenciesAccepted": "USD",
    ...(business.rating && {
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": business.rating,
        "reviewCount": business.reviewCount || 1,
        "bestRating": 5,
        "worstRating": 1
      }
    }),
    "founder": {
      "@type": "Person",
      "name": "Professional Team"
    },
    "foundingDate": business.yearsInBusiness ? 
      new Date(new Date().getFullYear() - business.yearsInBusiness, 0, 1).toISOString().split('T')[0] : 
      undefined,
    "hasCredential": business.licenseNumber ? {
      "@type": "EducationalOccupationalCredential",
      "credentialCategory": "Professional License",
      "recognizedBy": {
        "@type": "Organization",
        "name": "State Licensing Board"
      }
    } : undefined,
    "sameAs": [
      // TODO: Add social media links
      business.website
    ]
  });

  const generateServiceSchema = (service: ServiceData) => ({
    "@context": "https://schema.org",
    "@type": "Service",
    "@id": `${business.website}/services/${service.name.toLowerCase().replace(/\s+/g, '-')}#service`,
    "name": service.name,
    "description": service.description,
    "serviceType": service.serviceType,
    "category": service.category,
    "provider": {
      "@id": `${business.website}#business`
    },
    "areaServed": service.areaServed.map(area => ({
      "@type": "City",
      "name": area
    })),
    ...(service.priceRange && {
      "offers": {
        "@type": "Offer",
        "priceRange": service.priceRange,
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock",
        "validFrom": new Date().toISOString().split('T')[0]
      }
    }),
    "hasOfferCatalog": {
      "@type": "OfferCatalog",
      "name": `${service.name} Options`,
      "itemListElement": [
        {
          "@type": "Offer",
          "itemOffered": {
            "@type": "Service",
            "name": service.name
          }
        }
      ]
    }
  });

  const generateBreadcrumbSchema = () => {
    if (breadcrumbs.length === 0) return null;

    return {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": breadcrumbs.map((crumb, index) => ({
        "@type": "ListItem",
        "position": index + 1,
        "name": crumb.name,
        "item": `${business.website}${crumb.url}`
      }))
    };
  };

  const generateOrganizationSchema = () => ({
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": `${business.website}#organization`,
    "name": business.name,
    "url": business.website,
    "logo": `${business.website}/logo.png`,
    "contactPoint": {
      "@type": "ContactPoint",
      "telephone": business.phone,
      "contactType": "customer service",
      "email": business.email,
      "availableLanguage": "English"
    },
    "address": {
      "@type": "PostalAddress",
      "streetAddress": business.address,
      "addressLocality": business.serviceAreas[0] || "Local Area",
      "addressRegion": "TX",
      "postalCode": "78701",
      "addressCountry": "US"
    }
  });

  const generateWebPageSchema = () => ({
    "@context": "https://schema.org",
    "@type": "WebPage",
    "@id": `${business.website}${getPageUrl()}#webpage`,
    "url": `${business.website}${getPageUrl()}`,
    "name": getPageTitle(),
    "description": getPageDescription(),
    "isPartOf": {
      "@type": "WebSite",
      "@id": `${business.website}#website`
    },
    "about": {
      "@id": `${business.website}#business`
    },
    "mainEntity": getMainEntity(),
    "breadcrumb": breadcrumbs.length > 0 ? {
      "@id": `${business.website}${getPageUrl()}#breadcrumb`
    } : undefined
  });

  const generateWebSiteSchema = () => ({
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": `${business.website}#website`,
    "url": business.website,
    "name": business.name,
    "description": business.description,
    "publisher": {
      "@id": `${business.website}#organization`
    },
    "potentialAction": {
      "@type": "SearchAction",
      "target": {
        "@type": "EntryPoint",
        "urlTemplate": `${business.website}/search?q={search_term_string}`
      },
      "query-input": "required name=search_term_string"
    }
  });

  const getPageUrl = () => {
    switch (pageType) {
      case 'home': return '/';
      case 'about': return '/about';
      case 'services': return '/services';
      case 'contact': return '/contact';
      case 'service': return currentService ? `/services/${currentService.name.toLowerCase().replace(/\s+/g, '-')}` : '/services';
      case 'location': return currentLocation ? `/${currentLocation.toLowerCase().replace(/\s+/g, '-')}` : '/';
      default: return '/';
    }
  };

  const getPageTitle = () => {
    switch (pageType) {
      case 'home': return `${business.name} - Professional Services`;
      case 'about': return `About ${business.name}`;
      case 'services': return `Services - ${business.name}`;
      case 'contact': return `Contact ${business.name}`;
      case 'service': return currentService ? `${currentService.name} - ${business.name}` : 'Services';
      case 'location': return currentLocation ? `Services in ${currentLocation} - ${business.name}` : business.name;
      default: return business.name;
    }
  };

  const getPageDescription = () => {
    switch (pageType) {
      case 'home': return business.description;
      case 'about': return `Learn about ${business.name} and our professional services.`;
      case 'services': return `Professional services offered by ${business.name}.`;
      case 'contact': return `Contact ${business.name} for professional services.`;
      case 'service': return currentService?.description || 'Professional services';
      case 'location': return currentLocation ? 
        `Professional services in ${currentLocation} by ${business.name}.` : 
        business.description;
      default: return business.description;
    }
  };

  const getMainEntity = () => {
    switch (pageType) {
      case 'home':
      case 'about':
        return { "@id": `${business.website}#business` };
      case 'service':
        return currentService ? { "@id": `${business.website}/services/${currentService.name.toLowerCase().replace(/\s+/g, '-')}#service` } : undefined;
      default:
        return undefined;
    }
  };

  const schemas = [
    generateLocalBusinessSchema(),
    generateOrganizationSchema(),
    generateWebSiteSchema(),
    generateWebPageSchema(),
  ];

  // Add service schemas
  if (currentService) {
    schemas.push(generateServiceSchema(currentService));
  } else if (services.length > 0) {
    services.forEach(service => {
      schemas.push(generateServiceSchema(service));
    });
  }

  // Add breadcrumb schema
  const breadcrumbSchema = generateBreadcrumbSchema();
  if (breadcrumbSchema) {
    schemas.push(breadcrumbSchema);
  }

  return (
    <Head>
      {schemas.map((schema, index) => (
        <script
          key={index}
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(schema, null, 0)
          }}
        />
      ))}
    </Head>
  );
}
