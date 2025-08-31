/**
 * Professional Business Website - Homepage
 * 
 * Main business website that loads real business data from the Hero365 backend
 * Configured with business ID via environment variables during deployment
 */

import React from 'react';
import EliteHeader from '../components/layout/EliteHeader';
import EliteHero from '../components/hero/EliteHero';
import EliteServicesGrid from '../components/services/EliteServicesGrid';
import TrustRatingDisplay from '../components/professional/TrustRatingDisplay';
import CustomerReviews from '../components/professional/CustomerReviews';
import ContactSection from '../components/professional/ContactSection';
import ProfessionalFooter from '../components/professional/ProfessionalFooter';
import FeaturedProjectsGrid from '../components/projects/FeaturedProjectsGrid';
import { BookingWidgetProvider } from '../components/booking/BookingWidgetProvider';
import { CartProvider } from '../lib/contexts/CartContext';
import { professionalApi, ProfessionalProfile, ServiceItem } from '../lib/api/professional-client';
import { BookableService } from '../lib/types/booking';
import { getBusinessConfig, getBackendUrl, getDefaultHeaders } from '../lib/config/api-config';

async function loadBusinessData(businessId: string) {
  try {
    console.log('🔄 [SERVER] Loading business data for:', businessId);
    console.log('🔄 [SERVER] Environment:', process.env.NODE_ENV);
    
    // Make direct API calls to the backend (server-to-server)
    const backendUrl = getBackendUrl();
    console.log('🔄 [SERVER] Backend URL:', backendUrl);
    
    const [profileResponse, servicesResponse, productsResponse] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/contractors/profile/${businessId}`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 3600, tags: ['profile', businessId] } // 1 hour ISR
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/services/${businessId}`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 1800, tags: ['services', businessId] } // 30 min ISR
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/product-catalog/${businessId}?featured_only=true&limit=6`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 900, tags: ['products', businessId] } // 15 min ISR
      })
    ]);
    
    let profile = null;
    let services = [];
    let products = [];
    
    if (profileResponse.ok) {
      profile = await profileResponse.json();
      console.log('✅ [SERVER] Profile loaded:', profile.business_name);
    }
    
    if (servicesResponse.ok) {
      services = await servicesResponse.json();
      console.log('✅ [SERVER] Services loaded:', services.length, 'items');
    }

    if (productsResponse.ok) {
      products = await productsResponse.json();
      console.log('✅ [SERVER] Products loaded:', products.length, 'items');
    }
    
    return { profile, services, products };
  } catch (error) {
    console.error('⚠️ [SERVER] Failed to load business data:', error);
    return { profile: null, services: [], products: [] };
  }
}

export default async function HomePage() {
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.defaultBusinessId;
  
  // Load business data server-side
  const { profile: serverProfile, services: serverServices, products: serverProducts } = await loadBusinessData(businessId);
  
  // Use server data if available, otherwise fallback
  const profile = serverProfile || {
    business_id: businessConfig.defaultBusinessId,
    business_name: businessConfig.defaultBusinessName,
    trade_type: 'hvac',
    description: 'Premier HVAC services for homes and businesses. Specializing in energy-efficient installations, emergency repairs, and preventative maintenance.',
    phone: businessConfig.defaultBusinessPhone,
    email: businessConfig.defaultBusinessEmail,
    address: '123 Main St',
    website: 'https://www.example.com',
    service_areas: ['Local Area'],
    emergency_service: true,
    years_in_business: 10,
    license_number: 'Licensed & Insured',
    insurance_verified: true,
    average_rating: 4.8,
    total_reviews: 150,
    certifications: []
  };
  
  const services = serverServices || [];
  const error = serverProfile ? null : 'Using fallback data - backend not available';

  // Convert services to bookable format
  const bookableServices: BookableService[] = services.map((service: any) => ({
    id: service.id,
    business_id: businessId,
    name: service.name,
    category: service.category,
    description: service.description,
    is_bookable: true,
    requires_site_visit: true,
    estimated_duration_minutes: service.duration_minutes || 90,
    min_duration_minutes: service.duration_minutes ? Math.max(30, service.duration_minutes - 30) : 60,
    max_duration_minutes: service.duration_minutes ? service.duration_minutes + 30 : 120,
    base_price: service.base_price || 0,
    price_type: service.requires_quote ? 'quote' as const : 'fixed' as const,
    required_skills: [],
    min_technicians: 1,
    max_technicians: 1,
    min_lead_time_hours: service.is_emergency ? 1 : 4,
    max_advance_days: 60,
    is_emergency_service: service.is_emergency,
    is_active: service.available,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }));

  // Generate dynamic content based on real business profile
  const generatedContent = !profile ? null : {
    businessName: profile.business_name,
    tagline: `Professional ${profile.trade_type} Services`,
    description: profile.description,
    phone: profile.phone,
    email: profile.email,
    address: profile.address,
    serviceAreas: profile.service_areas,
    emergencyService: profile.emergency_service,
    yearsInBusiness: profile.years_in_business,
    licenseNumber: profile.license_number,
    insuranceVerified: profile.insurance_verified,
    averageRating: profile.average_rating,
    totalReviews: profile.total_reviews,
    certifications: profile.certifications,
    website: profile.website
  };



  // Error state - show fallback content with default configuration
  if (error || !profile || !generatedContent) {
    const fallbackContent = {
      businessName: businessConfig.defaultBusinessName,
      tagline: "Professional Home Services",
      description: "Quality service you can trust. Licensed, insured, and committed to excellence.",
      phone: businessConfig.defaultBusinessPhone,
      email: businessConfig.defaultBusinessEmail,
      address: "Serving Your Local Area",
      serviceAreas: ["Local Area"],
      emergencyService: true,
      yearsInBusiness: 10,
      licenseNumber: "Licensed & Insured",
      insuranceVerified: true,
      averageRating: 4.8,
      totalReviews: 150,
      certifications: ["Licensed Professional", "Insured"],
      website: undefined
    };

    const fallbackServices = [
      {
        name: "Professional Service",
        description: "Quality service for your home or business",
        icon: "🔧",
        features: ["Licensed & Insured", "Same Day Service", "100% Satisfaction Guaranteed"],
        isEmergency: false,
        priceRange: "Contact for pricing"
      },
      {
        name: "Emergency Service",
        description: "24/7 emergency service when you need it most",
        icon: "🚨",
        features: ["24/7 Availability", "Rapid Response", "Emergency Repairs"],
        isEmergency: true,
        priceRange: "Emergency rates apply"
      }
    ];

  return (
    <CartProvider businessId={businessId}>
      <BookingWidgetProvider
        businessId={businessId}
        companyName={fallbackContent.businessName}
        companyPhone={fallbackContent.phone}
        companyEmail={fallbackContent.email}
        services={[]}
      >
        <div className="min-h-screen bg-white">
          {/* Header */}
          <EliteHeader 
            businessName={fallbackContent.businessName}
            city={fallbackContent.serviceAreas[0] || 'Local Area'}
            state={'TX'}
            phone={fallbackContent.phone}
            supportHours={'24/7'}
          />
      
      {/* Hero Section */}
          <EliteHero 
            businessName={fallbackContent.businessName}
            headline={`Professional ${fallbackContent.businessName} Services`}
            subheadline={fallbackContent.tagline}
            city={fallbackContent.serviceAreas[0] || 'Local Area'}
            phone={fallbackContent.phone}
            averageRating={fallbackContent.averageRating}
            totalReviews={fallbackContent.totalReviews}
            emergencyMessage={fallbackContent.emergencyService ? '24/7 Emergency Service Available' : undefined}
            promotions={[]}
          />

          {/* Services Grid */}
          <EliteServicesGrid 
            businessName={fallbackContent.businessName}
            city={fallbackContent.serviceAreas[0] || 'Local Area'}
            phone={fallbackContent.phone}
          />

          {/* Trust & Rating Display */}
          <TrustRatingDisplay 
            ratings={[]}
          />

          {/* Featured Projects */}
          <div className="py-16 bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <FeaturedProjectsGrid 
                businessId={businessId}
                limit={6}
                featuredOnly={true}
                showViewAll={true}
              />
            </div>
          </div>

          {/* Customer Reviews */}
          <CustomerReviews 
            testimonials={[]}
          />

          {/* Contact Section */}
          <ContactSection 
            business={{
              id: businessId,
              name: fallbackContent.businessName,
              phone_number: fallbackContent.phone,
              business_email: fallbackContent.email,
              address: fallbackContent.address,
              service_areas: fallbackContent.serviceAreas,
              trades: [],
              seo_keywords: []
            }}
            locations={[]}
          />

          {/* Footer */}
          <ProfessionalFooter 
            business={{
              id: businessId,
              name: fallbackContent.businessName,
              phone_number: fallbackContent.phone,
              business_email: fallbackContent.email,
              address: fallbackContent.address,
              website: fallbackContent.website,
              service_areas: fallbackContent.serviceAreas,
              trades: [],
              seo_keywords: []
            }}
            serviceCategories={[]}
            locations={[]}
          />

          {/* Error message for development */}
          {error && (
            <div className="fixed bottom-4 right-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded shadow-lg max-w-sm">
              <strong className="font-bold">Development Notice:</strong>
              <span className="block sm:inline"> {error}</span>
            </div>
          )}
        </div>
      </BookingWidgetProvider>
    </CartProvider>
  );
  }

  return (
    <CartProvider businessId={businessId}>
      <BookingWidgetProvider
        businessId={businessId}
        companyName={generatedContent.businessName}
        companyPhone={generatedContent.phone}
        companyEmail={generatedContent.email}
        services={bookableServices}
      >
      <div className="min-h-screen bg-white">
        {/* Header */}
        <EliteHeader 
          businessName={generatedContent.businessName}
          city={generatedContent.serviceAreas[0] || 'Austin'}
          state={'TX'}
          phone={generatedContent.phone}
          supportHours={'24/7'}
        />

        {/* Hero Section */}
        <EliteHero 
          businessName={generatedContent.businessName}
          headline={`Professional ${generatedContent.businessName} Services`}
          subheadline={generatedContent.tagline}
          city={generatedContent.serviceAreas[0] || 'Austin'}
          phone={generatedContent.phone}
          averageRating={generatedContent.averageRating}
          totalReviews={generatedContent.totalReviews}
          emergencyMessage={generatedContent.emergencyService ? '24/7 Emergency Service Available' : undefined}
          promotions={[]}
        />

        {/* Services Grid */}
        <EliteServicesGrid 
          businessName={generatedContent.businessName}
          city={generatedContent.serviceAreas[0] || 'Austin'}
          phone={generatedContent.phone}
        />

        {/* Products Showcase */}
        {serverProducts && serverProducts.length > 0 && (
          <div className="py-16 bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  Professional Equipment & Installation
                </h2>
                <p className="text-lg text-gray-600 max-w-3xl mx-auto mb-6">
                  Shop professional-grade equipment with expert installation services. 
                  Get instant pricing with membership discounts and bundle savings.
                </p>
                <div className="flex justify-center">
                  <a 
                    href="/products"
                    className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Shop All Products
                    <svg className="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </a>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {serverProducts.slice(0, 3).map((product: any) => (
                  <div key={product.id} className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-200 group">
                    <a href={`/products/${product.slug}`} className="block h-full">
                    <div className="relative">
                      <div className="aspect-w-1 aspect-h-1 w-full overflow-hidden rounded-t-lg bg-gray-200">
                        {product.featured_image_url ? (
                          <img
                            src={product.featured_image_url}
                            alt={product.name}
                            className="h-48 w-full object-cover object-center group-hover:scale-105 transition-transform duration-200"
                          />
                        ) : (
                          <div className="h-48 w-full bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center group-hover:from-blue-200 group-hover:to-blue-300 transition-colors duration-200">
                            <svg className="h-12 w-12 text-blue-400 group-hover:text-blue-500 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H3m2 0h4M9 7h6m-6 4h6m-2 4h2" />
                            </svg>
                          </div>
                        )}
                      </div>
                      {product.is_featured && (
                        <div className="absolute top-2 left-2">
                          <span className="px-2 py-1 bg-yellow-500 text-white text-xs font-bold rounded">
                            FEATURED
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2 overflow-hidden" style={{
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical'
                      }}>
                        {product.name}
                      </h3>
                      {product.description && (
                        <p className="text-gray-600 text-sm mb-4 overflow-hidden" style={{
                          display: '-webkit-box',
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: 'vertical'
                        }}>
                          {product.description}
                        </p>
                      )}

                      {/* Product Highlights */}
                      {product.product_highlights && product.product_highlights.length > 0 && (
                        <div className="mb-4">
                          <ul className="text-sm text-gray-600 space-y-1">
                            {product.product_highlights.slice(0, 2).map((highlight: string, index: number) => (
                              <li key={index} className="flex items-center">
                                <svg className="h-3 w-3 text-green-500 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                                </svg>
                                {highlight}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Pricing */}
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <span className="text-lg font-bold text-gray-900">
                            ${product.unit_price.toLocaleString()}
                          </span>
                          {product.requires_professional_install && (
                            <div className="text-xs text-blue-600 mt-1">
                              + Professional Installation
                            </div>
                          )}
                        </div>
                        {product.warranty_years && (
                          <div className="text-xs text-green-600">
                            {product.warranty_years} yr warranty
                          </div>
                        )}
                      </div>

                      {/* Installation Options Info */}
                      {product.installation_options && product.installation_options.length > 0 && (
                        <div className="text-xs text-center text-blue-600 group-hover:text-blue-700 transition-colors duration-200">
                          Professional installation available
                        </div>
                      )}
                    </div>
                    </a>
                  </div>
                ))}
              </div>

              {/* Bottom CTA */}
              <div className="text-center mt-12">
                <div className="bg-blue-50 rounded-lg p-6 inline-block">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Need Help Choosing the Right Product?
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Our experts can help you select the perfect equipment for your needs.
                  </p>
                  <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <a 
                      href={`tel:${generatedContent.phone}`}
                      className="px-6 py-2 bg-white border border-blue-300 text-blue-700 font-medium rounded-lg hover:bg-blue-50 transition-colors"
                    >
                      Call {generatedContent.phone}
                    </a>
                    <a 
                      href="/products"
                      className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Browse All Products
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Featured Projects */}
        <div className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <FeaturedProjectsGrid 
              businessId={businessId}
              limit={6}
              featuredOnly={true}
              showViewAll={true}
            />
          </div>
        </div>

        {/* Trust & Rating Display */}
        <TrustRatingDisplay 
          ratings={[]}
        />

        {/* Customer Reviews */}
        <CustomerReviews 
          testimonials={[]}
        />

        {/* Contact Section */}
        <ContactSection 
          business={{
            id: businessId,
            name: generatedContent.businessName,
            phone_number: generatedContent.phone,
            business_email: generatedContent.email,
            address: generatedContent.address,
            service_areas: generatedContent.serviceAreas,
            trades: [],
            seo_keywords: []
          }}
          locations={[]}
        />

        {/* Footer */}
        <ProfessionalFooter 
          business={{
            id: businessId,
            name: generatedContent.businessName,
            phone_number: generatedContent.phone,
            business_email: generatedContent.email,
            address: generatedContent.address,
            website: generatedContent.website,
            service_areas: generatedContent.serviceAreas,
            trades: [],
            seo_keywords: []
          }}
          serviceCategories={[]}
          locations={[]}
        />
      </div>
      </BookingWidgetProvider>
    </CartProvider>
  );
}

