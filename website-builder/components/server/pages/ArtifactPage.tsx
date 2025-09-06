/**
 * Artifact Page Component - SSR Optimized
 * 
 * This is the main page component for trade-aware websites with:
 * - Server-side rendering for optimal performance
 * - Context-aware content generation
 * - Trade-specific modules and components
 * - Real business data integration
 */

import React from 'react';
import { Metadata } from 'next';
import { ActivityPageArtifact, ActivityType } from '@/lib/shared/types/seo-artifacts';
import { BusinessContext, TechnicianProfile, ProjectShowcase } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';

// SSR-Optimized Components
import Hero365Header from '@/components/server/layout/Hero365Header';
import { TradeAwareHero } from '@/components/server/trade-aware/TradeAwareHero';
// import { ContextAwareServiceGrid } from '@/components/server/trade-aware/ContextAwareServiceGrid';
import { ActivityModuleSection } from '@/components/client/trade-aware/ActivityModuleSection';
import { ProjectShowcase as ProjectShowcaseComponent } from '@/components/server/trade-aware/ProjectShowcase';
import { TestimonialSection } from '@/components/server/trade-aware/TestimonialSection';
import Hero365Footer from '@/components/shared/Hero365Footer';
import { StructuredDataRenderer } from '@/components/server/seo/StructuredDataRenderer';

// Client Components (hydrated after SSR)
import { ABTestingProvider } from '@/components/client/testing/ABTestingProvider';
import { PerformanceMonitor } from '@/components/client/monitoring/PerformanceMonitor';

interface ArtifactPageProps {
  artifact: ActivityPageArtifact;
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  enableABTesting?: boolean;
  experimentConfig?: Record<string, any>;
}

/**
 * Artifact Page - Server Component
 * 
 * This component is rendered on the server for optimal performance.
 * It uses real business data to create personalized, trade-aware content.
 */
export default function ArtifactPage({ 
  artifact, 
  businessContext,
  tradeConfig,
  enableABTesting = false,
  experimentConfig = {}
}: ArtifactPageProps) {
  
  // Merge artifact variants with experiment config
  const allVariants = {
    ...artifact.content_variants,
    ...experimentConfig
  };

  // Generate structured data with business context
  const structuredData = generateStructuredData(artifact, businessContext, tradeConfig);

  return (
    <ABTestingProvider 
      enabled={enableABTesting}
      variants={allVariants}
      activeExperiments={artifact.active_experiment_keys}
      artifactId={artifact.artifact_id}
      businessId={artifact.business_id}
    >
      <div className={`min-h-screen bg-white trade-${tradeConfig.trade}`}>
        {/* Performance Monitoring */}
        <PerformanceMonitor 
          pageType="artifact"
          businessId={artifact.business_id}
          activitySlug={artifact.activity_slug}
        />
        
        {/* Enhanced Structured Data */}
        <StructuredDataRenderer schemas={structuredData} />
        
        {/* Trade-Aware Header */}
        <Hero365Header 
          businessName={businessContext.business.name}
          city={businessContext.primary_area?.city || businessContext.business.city}
          state={businessContext.primary_area?.state || businessContext.business.state}
          phone={businessContext.business.phone}
          supportHours={tradeConfig.emergency_services ? "24/7" : "Business Hours"}
          logo={businessContext.business.logo_url}
          primaryColor={tradeConfig.colors.primary}
        />

        {/* Main Content */}
        <main>
          {/* Hero Section with Real Business Data */}
          <TradeAwareHero 
            artifact={artifact}
            businessContext={businessContext}
            tradeConfig={tradeConfig}
            testKey="hero"
          />

          {/* Services Overview Section */}
          <section className="py-16 bg-gray-50">
            <div className="container mx-auto px-4">
              <h2 className="text-3xl font-bold text-center mb-8">Our {artifact.activity_name} Services</h2>
              <p className="text-lg text-gray-700 text-center max-w-3xl mx-auto mb-12">
                {artifact.content_blocks?.overview || `Learn more about our expert ${artifact.activity_name} services tailored to your needs.`}
              </p>
              {artifact.content_blocks?.benefits && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                  {artifact.content_blocks.benefits.slice(0, 3).map((benefit, index) => (
                    <div key={index} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                      <h3 className="text-xl font-semibold mb-3 text-gray-900">{benefit.title}</h3>
                      <p className="text-gray-700">{benefit.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>

          {/* Activity-Specific Modules */}
          {artifact.activity_modules.length > 0 && (
            <ActivityModuleSection 
              modules={artifact.activity_modules}
              businessContext={businessContext}
              tradeConfig={tradeConfig}
              testKey="modules"
            />
          )}

          {/* Real Project Showcase */}
          {businessContext.showcase_projects.length > 0 && (
            <ProjectShowcaseComponent 
              projects={businessContext.showcase_projects}
              technicians={businessContext.technicians}
              businessContext={businessContext}
              tradeConfig={tradeConfig}
              testKey="projects"
            />
          )}

          {/* Process Section with Trade Context */}
          {artifact.process && Object.keys(artifact.process).length > 0 && (
            <section className="py-16 bg-gray-50">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-12">
                  <h2 className="text-3xl font-bold text-gray-900 mb-4">
                    Our {tradeConfig.display_name} Process
                  </h2>
                  <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                    {businessContext.combined_experience_years} years of combined experience 
                    delivering exceptional {tradeConfig.display_name.toLowerCase()} services
                  </p>
                </div>
                
                {/* Process steps would be rendered here */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                  {Object.entries(artifact.process).map(([step, content], index) => (
                    <div key={step} className="text-center">
                      <div className={`w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center text-white font-bold text-xl`}
                           style={{ backgroundColor: tradeConfig.colors.primary }}>
                        {index + 1}
                      </div>
                      <h3 className="text-xl font-semibold mb-2">{step}</h3>
                      <p className="text-gray-600">{content}</p>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* Authentic Testimonials */}
          {businessContext.testimonials.length > 0 && (
            <TestimonialSection 
              testimonials={businessContext.testimonials}
              projects={businessContext.projects}
              businessContext={businessContext}
              tradeConfig={tradeConfig}
              testKey="testimonials"
            />
          )}

          {/* Benefits Section with Real Data */}
          {artifact.benefits && Object.keys(artifact.benefits).length > 0 && (
            <section className="py-16 bg-white">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-12">
                  <h2 className="text-3xl font-bold text-gray-900 mb-4">
                    Why Choose {businessContext.business.name}?
                  </h2>
                  <p className="text-xl text-gray-600">
                    {businessContext.technicians.length} expert technicians, 
                    {businessContext.completed_count}+ successful projects
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {Object.entries(artifact.benefits).map(([benefit, description]) => (
                    <div key={benefit} className="text-center p-6 rounded-lg border border-gray-200">
                      <h3 className="text-xl font-semibold mb-3">{benefit}</h3>
                      <p className="text-gray-600">{description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* FAQ Section */}
          {artifact.faqs && artifact.faqs.length > 0 && (
            <section className="py-16 bg-gray-50">
              <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-12">
                  <h2 className="text-3xl font-bold text-gray-900 mb-4">
                    Frequently Asked Questions
                  </h2>
                  <p className="text-xl text-gray-600">
                    Common questions about our {tradeConfig.display_name.toLowerCase()} services
                  </p>
                </div>
                
                <div className="space-y-6">
                  {artifact.faqs.map((faq, index) => (
                    <div key={index} className="bg-white rounded-lg p-6 shadow-sm">
                      <h3 className="text-lg font-semibold mb-3">{faq.question}</h3>
                      <p className="text-gray-600">{faq.answer}</p>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* Call-to-Action Section */}
          <section className="py-16 bg-gradient-to-r from-blue-600 to-blue-800 text-white">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h2 className="text-3xl font-bold mb-4">
                Ready for Expert {tradeConfig.display_name}?
              </h2>
              <p className="text-xl mb-8">
                Join {businessContext.total_served}+ satisfied customers who trust {businessContext.business.name}
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a 
                  href={`tel:${businessContext.business.phone}`}
                  className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                >
                  Call {businessContext.business.phone}
                </a>
                <a 
                  href="/booking"
                  className="bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-800 transition-colors border border-blue-500"
                >
                  Schedule Service
                </a>
              </div>
              
              {tradeConfig.emergency_services && (
                <p className="mt-6 text-blue-200">
                  🚨 Emergency service available 24/7 - No overtime charges!
                </p>
              )}
            </div>
          </section>
        </main>

        {/* Trade-Aware Footer */}
        <Hero365Footer 
          business={{
            business_id: businessContext.business.id,
            business_name: businessContext.business.name,
            description: businessContext.business.description,
            phone: businessContext.business.phone,
            email: businessContext.business.email,
            address: businessContext.business.address,
            city: businessContext.business.city,
            state: businessContext.business.state,
            postal_code: businessContext.business.postal_code,
            website: businessContext.business.website,
            years_in_business: businessContext.business.years_in_business,
            average_rating: businessContext.average_rating,
            license_number: businessContext.business.license_number,
            emergency_service: tradeConfig.emergency_services,
            service_areas: businessContext.service_areas.map(area => area.name)
          }}
          services={businessContext.activities?.map(activity => ({
            id: activity.slug,
            name: activity.name,
            slug: activity.slug,
            is_featured: activity.is_featured,
            category: activity.trade_name
          })) || []}
          locations={businessContext.service_areas?.map(area => ({
            id: area.slug,
            name: area.name,
            city: area.city,
            state: area.state,
            address: area.name,
            is_primary: area.is_primary
          })) || []}
        />
      </div>
    </ABTestingProvider>
  );
}

/**
 * Generate structured data with business context
 */
function generateStructuredData(
  artifact: ActivityPageArtifact,
  businessContext: BusinessContext,
  tradeConfig: TradeConfiguration
) {
  const baseSchemas = artifact.json_ld_schemas || [];
  
  // Enhanced LocalBusiness schema with real data
  const localBusinessSchema = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": businessContext.business.name,
    "description": artifact.meta_description,
    "url": businessContext.business.website,
    "telephone": businessContext.business.phone,
    "email": businessContext.business.email,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": businessContext.business.address,
      "addressLocality": businessContext.business.city,
      "addressRegion": businessContext.business.state,
      "postalCode": businessContext.business.postal_code
    },
    "geo": businessContext.primary_area ? {
      "@type": "GeoCoordinates",
      "addressLocality": businessContext.primary_area.city,
      "addressRegion": businessContext.primary_area.state
    } : undefined,
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": businessContext.average_rating,
      "reviewCount": businessContext.total_served
    },
    "employee": businessContext.technicians.map(tech => ({
      "@type": "Person",
      "name": tech.name,
      "jobTitle": tech.title,
      "hasCredential": tech.certifications.map(cert => ({
        "@type": "EducationalOccupationalCredential",
        "name": cert
      }))
    })),
    "areaServed": businessContext.service_areas.map(area => ({
      "@type": "City",
      "name": area.name
    })),
    "priceRange": tradeConfig.service_categories[0]?.starting_price ? 
      `$${tradeConfig.service_categories[0].starting_price}+` : "$$"
  };

  // Service schema with real technician data
  const serviceSchema = {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": artifact.activity_name,
    "description": artifact.meta_description,
    "provider": {
      "@type": "LocalBusiness",
      "name": businessContext.business.name
    },
    "areaServed": businessContext.service_areas.map(area => area.name),
    "hasOfferCatalog": {
      "@type": "OfferCatalog",
      "name": `${artifact.activity_name} Services`,
      "itemListElement": tradeConfig.service_categories.map(category => ({
        "@type": "Offer",
        "itemOffered": {
          "@type": "Service",
          "name": category.name,
          "description": category.description
        }
      }))
    }
  };

  return [
    ...baseSchemas,
    localBusinessSchema,
    serviceSchema
  ];
}

/**
 * Generate metadata for the page
 */
export async function generateArtifactMetadata({
  artifact,
  businessContext,
  tradeConfig
}: {
  artifact: ActivityPageArtifact;
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
}): Promise<Metadata> {
  
  const title = (artifact.title || artifact.meta_title || `${artifact.activity_name} Services`)
    .replace('{business_name}', businessContext.business.name)
    .replace('{city}', businessContext.primary_area?.city || businessContext.business.city);

  const description = (artifact.meta_description || `Professional ${artifact.activity_name} services`)
    .replace('{business_name}', businessContext.business.name)
    .replace('{years_experience}', businessContext.combined_experience_years?.toString() || '10');

  return {
    title,
    description,
    keywords: (artifact.target_keywords || []).join(', '),
    openGraph: {
      title,
      description,
      url: artifact.canonical_url,
      siteName: businessContext.business.name,
      type: 'website',
      locale: 'en_US',
      images: businessContext.showcase_projects
        .filter(p => p.images.length > 0)
        .slice(0, 3)
        .map(p => ({
          url: p.images[0],
          width: 1200,
          height: 630,
          alt: p.title
        }))
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description
    },
    alternates: {
      canonical: artifact.canonical_url
    },
    robots: {
      index: artifact.status === 'published',
      follow: true,
      googleBot: {
        index: artifact.status === 'published',
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      }
    }
  };
}
