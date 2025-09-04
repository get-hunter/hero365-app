/**
 * Enhanced Activity Page Component
 * 
 * Activity-first page component that combines website context data
 * with activity content packs for rich, tailored content.
 */

import { useMemo } from 'react';
import { useWebsiteContext, useActivityContentPack, WebsiteActivityInfo } from '@/lib/shared/hooks/useWebsiteContext';
import SEOComposer from '../seo/SEOComposer';
import BookingForm from '../forms/BookingForm';

interface EnhancedActivityPageProps {
  businessId: string;
  activitySlug: string;
  showBookingForm?: boolean;
  className?: string;
}

export default function EnhancedActivityPage({
  businessId,
  activitySlug,
  showBookingForm = true,
  className = ''
}: EnhancedActivityPageProps) {
  
  // Fetch website context and activity content pack
  const { data: websiteContext, loading: contextLoading, error: contextError } = useWebsiteContext(businessId);
  const { data: contentPack, loading: contentLoading, error: contentError } = useActivityContentPack(activitySlug);
  
  // Find the current activity
  const currentActivity = useMemo(() => {
    return websiteContext?.activities.find(activity => activity.slug === activitySlug);
  }, [websiteContext, activitySlug]);
  
  // Transform website context for SEO component
  const seoBusinessData = useMemo(() => {
    if (!websiteContext) return null;
    
    const { business } = websiteContext;
    return {
      name: business.name,
      description: business.description || '',
      phone: business.phone || '',
      email: business.email || '',
      address: business.address || '',
      website: business.website || '',
      serviceAreas: business.service_areas,
      trades: websiteContext.trades.map(trade => trade.name),
      primary_trade_slug: business.primary_trade_slug
    };
  }, [websiteContext]);
  
  // Transform activities for SEO component
  const seoActivitiesData = useMemo(() => {
    if (!websiteContext) return [];
    
    return websiteContext.activities.map(activity => ({
      slug: activity.slug,
      name: activity.name,
      description: `Professional ${activity.name.toLowerCase()} services`,
      trade_slug: activity.trade_slug,
      trade_name: activity.trade_name,
      synonyms: activity.synonyms,
      tags: activity.tags,
      areaServed: websiteContext.business.service_areas
    }));
  }, [websiteContext]);
  
  // Page data for SEO
  const pageData = useMemo(() => ({
    type: 'activity' as const,
    activity: activitySlug,
    title: currentActivity ? `${currentActivity.name} - ${websiteContext?.business.name}` : undefined,
    description: contentPack?.seo?.descriptionTemplate || currentActivity ? `Professional ${currentActivity.name.toLowerCase()} services` : undefined
  }), [activitySlug, currentActivity, websiteContext, contentPack]);
  
  // Loading state
  if (contextLoading || contentLoading) {
    return (
      <div className={`enhanced-activity-page ${className}`}>
        <div className="loading-container">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-4"></div>
            <div className="h-4 bg-gray-200 rounded mb-2"></div>
            <div className="h-4 bg-gray-200 rounded mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          </div>
        </div>
      </div>
    );
  }
  
  // Error state
  if (contextError || contentError) {
    return (
      <div className={`enhanced-activity-page ${className}`}>
        <div className="error-container">
          <h2 className="text-xl font-semibold text-red-600 mb-2">Error Loading Page</h2>
          <p className="text-gray-600">{contextError || contentError}</p>
        </div>
      </div>
    );
  }
  
  // No data state
  if (!websiteContext || !currentActivity) {
    return (
      <div className={`enhanced-activity-page ${className}`}>
        <div className="no-data-container">
          <h2 className="text-xl font-semibold text-gray-600 mb-2">Service Not Found</h2>
          <p className="text-gray-500">The requested service could not be found.</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className={`enhanced-activity-page ${className}`}>
      {/* SEO Component */}
      {seoBusinessData && (
        <SEOComposer
          businessData={seoBusinessData}
          pageData={pageData}
          activitiesData={seoActivitiesData}
          showInternalLinks={true}
        />
      )}
      
      {/* Hero Section */}
      <section className="hero-section">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto text-center">
            {contentPack?.hero?.icon && (
              <div className="mb-6">
                <span className="text-4xl">{contentPack.hero.icon}</span>
              </div>
            )}
            
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              {contentPack?.hero?.title || currentActivity.name}
            </h1>
            
            {contentPack?.hero?.subtitle && (
              <p className="text-xl text-gray-600 mb-8">
                {contentPack.hero.subtitle}
              </p>
            )}
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                {contentPack?.hero?.ctaLabel || 'Get Free Quote'}
              </button>
              <button className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
                Call {websiteContext.business.phone}
              </button>
            </div>
          </div>
        </div>
      </section>
      
      {/* Benefits Section */}
      {contentPack?.benefits && (
        <section className="benefits-section bg-gray-50 py-12">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
                {contentPack.benefits.heading}
              </h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {contentPack.benefits.bullets.map((benefit: string, index: number) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center mt-1">
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <p className="text-gray-700">{benefit}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}
      
      {/* Process Section */}
      {contentPack?.process && (
        <section className="process-section py-12">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
                {contentPack.process.heading}
              </h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {contentPack.process.steps.map((step: string, index: number) => (
                  <div key={index} className="text-center">
                    <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                      {index + 1}
                    </div>
                    <p className="text-gray-700">{step}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}
      
      {/* Booking Form Section */}
      {showBookingForm && (
        <section className="booking-section bg-blue-50 py-12">
          <div className="container mx-auto px-4">
            <div className="max-w-2xl mx-auto">
              <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
                Request Service
              </h2>
              <BookingForm
                activity={currentActivity}
                businessInfo={websiteContext.business}
                onSubmit={(data) => {
                  console.log('Booking submitted:', data);
                  // Handle booking submission
                }}
              />
            </div>
          </div>
        </section>
      )}
      
      {/* FAQ Section */}
      {contentPack?.faqs && contentPack.faqs.length > 0 && (
        <section className="faq-section py-12">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
                Frequently Asked Questions
              </h2>
              <div className="space-y-6">
                {contentPack.faqs.map((faq: { q: string; a: string }, index: number) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {faq.q}
                    </h3>
                    <p className="text-gray-700">
                      {faq.a}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
