/**
 * Professional Business Website - Homepage
 * 
 * Main business website that loads real business data from the Hero365 backend
 * Configured with business ID via environment variables during deployment
 */

import React from 'react';
import Header from '@/components/server/layout/header';
import HeroSection from '@/components/server/hero/hero-section';
import ServicesGrid from '@/components/server/services/services-grid';
import { notFound } from 'next/navigation';
import Hero365TrustRating from '@/components/client/business/Hero365TrustRating';
import Hero365CustomerReviews from '@/components/client/business/Hero365CustomerReviews';
import Hero365ContactSection from '@/components/client/business/Hero365ContactSection';
import { BookableService } from '@/lib/shared/types/booking';
import { getBusinessConfig, getBackendUrl, getDefaultHeaders } from '@/lib/shared/config/api-config';
import { getServiceCategoriesForFooter, getLocations } from '@/lib/server/navigation-loader';

async function loadBusinessData(businessId: string) {
  try {
    console.log('🔄 [SERVER] Loading business data for:', businessId);
    console.log('🔄 [SERVER] Environment:', process.env.NODE_ENV);
    
    // Try API calls during build time for hybrid rendering
    // Only fall back to demo data if API is actually unavailable
    
    // Make direct API calls to the backend (server-to-server)
    const backendUrl = getBackendUrl();
    console.log('🔄 [SERVER] Backend URL:', backendUrl);
    
    const [profileResponse, servicesResponse, productsResponse] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/contractors/profile/${businessId}`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 3600, tags: ['profile', businessId] } // 1 hour ISR
      }).catch(err => {
        console.log('⚠️ [SERVER] Profile API failed:', err.message);
        return { ok: false };
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/services/${businessId}`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 1800, tags: ['services', businessId] } // 30 min ISR
      }).catch(err => {
        console.log('⚠️ [SERVER] Services API failed:', err.message);
        return { ok: false };
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/product-catalog/${businessId}?featured_only=true&limit=6`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 900, tags: ['products', businessId] } // 15 min ISR
      }).catch(err => {
        console.log('⚠️ [SERVER] Products API failed:', err.message);
        return { ok: false };
      })
    ]);
    
    let profile = null;
    let services = [];
    let products = [];
    
    if (profileResponse && 'ok' in profileResponse && profileResponse.ok) {
      profile = await (profileResponse as Response).json();
      console.log('✅ [SERVER] Profile loaded:', profile.business_name);
    }
    
    if (servicesResponse && 'ok' in servicesResponse && servicesResponse.ok) {
      services = await (servicesResponse as Response).json();
      console.log('✅ [SERVER] Services loaded:', services.length, 'items');
    }

    if (productsResponse && 'ok' in productsResponse && productsResponse.ok) {
      products = await (productsResponse as Response).json();
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
  
  // Load navigation data for footer
  const [footerCategoriesRaw, footerLocationsRaw] = await Promise.all([
    getServiceCategoriesForFooter(),
    getLocations()
  ]);
  
  // Load business data server-side
  const { profile: serverProfile, services: serverServices, products: serverProducts } = await loadBusinessData(businessId);
  
  // Require real data; if missing, show 404
  if (!serverProfile) {
    notFound();
  }

  const profile = serverProfile;
  const services = serverServices || [];

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
  type ContentData = {
    businessName: string;
    tagline: string;
    description: string;
    phone: string;
    email: string;
    address: string;
    serviceAreas: string[];
    emergencyService: boolean;
    yearsInBusiness: number;
    licenseNumber: string;
    insuranceVerified: boolean;
    averageRating: number;
    totalReviews: number;
    certifications: string[];
    website?: string;
  };

  const primaryTradeSlugSafe = typeof (profile as any).primary_trade_slug === 'string'
    ? ((profile as any).primary_trade_slug as string)
    : 'hvac';
  const formattedTradeName = primaryTradeSlugSafe
    .split('-')
    .filter(Boolean)
    .map((word: string) => (word && word.length > 0 ? word[0].toUpperCase() + word.slice(1) : ''))
    .join(' ');

  const businessData: ContentData = {
    businessName: (profile as any).business_name ?? '',
    tagline: `Professional ${formattedTradeName} Services`,
    description: profile.description ?? '',
    phone: profile.phone?.trim() || null,
    email: profile.email ?? '',
    address: profile.address ?? '',
    serviceAreas: Array.isArray(profile.service_areas) ? profile.service_areas : [],
    emergencyService: !!profile.emergency_service,
    yearsInBusiness: profile.years_in_business ?? 0,
    licenseNumber: profile.license_number ?? '',
    insuranceVerified: !!profile.insurance_verified,
    averageRating: profile.average_rating ?? 0,
    totalReviews: profile.total_reviews ?? 0,
    certifications: Array.isArray(profile.certifications) ? profile.certifications : [],
    website: profile.website ?? ''
  };



  // No fallback UI; only render with real data

  return (
      <div className="min-h-screen bg-white">
        {/* Header (server) with client CTA/cart slots */}
        <Header 
          businessName={businessData.businessName}
          city={businessData.serviceAreas[0] || 'Austin'}
          state={'TX'}
          phone={businessData.phone}
          supportHours={'24/7'}
        />

        {/* Server content */}
        <div>
          {/* Hero Section (server component) */}
          <HeroSection
            businessName={businessData.businessName}
            headline={`Professional ${businessData.businessName} Services`}
            subheadline={businessData.tagline}
            city={businessData.serviceAreas[0] || 'Austin'}
            phone={businessData.phone}
            averageRating={businessData.averageRating}
            totalReviews={businessData.totalReviews}
            emergencyMessage={businessData.emergencyService ? '24/7 Emergency Service Available' : undefined}
          />

          {/* Services Grid (server component) */}
          <ServicesGrid
            businessName={businessData.businessName}
            city={businessData.serviceAreas[0] || 'Austin'}
            phone={businessData.phone}
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
                    {businessData.phone && (
                      <a 
                        href={`tel:${businessData.phone}`}
                        className="px-6 py-2 bg-white border border-blue-300 text-blue-700 font-medium rounded-lg hover:bg-blue-50 transition-colors"
                      >
                        Call {businessData.phone}
                      </a>
                    )}
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
          <section className="py-16 bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  Recent Projects
                </h2>
                <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                  See our latest work and successful installations for {businessData.serviceAreas[0] || 'Austin'} area customers
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
                {/* Project Card 1 */}
                <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                  <div className="h-48 bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                    <svg className="h-16 w-16 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H3m2 0h4M9 7h6m-6 4h6m-2 4h2" />
                    </svg>
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Residential HVAC Installation</h3>
                    <p className="text-gray-600 mb-4">Complete system replacement with high-efficiency unit and smart thermostat.</p>
                    <div className="flex items-center text-sm text-gray-500">
                      <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {businessData.serviceAreas[0] || 'Austin'}, TX
                    </div>
                  </div>
                </div>
                
                {/* Project Card 2 */}
                <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                  <div className="h-48 bg-gradient-to-br from-green-100 to-green-200 flex items-center justify-center">
                    <svg className="h-16 w-16 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Commercial Maintenance</h3>
                    <p className="text-gray-600 mb-4">Preventive maintenance program for office building HVAC systems.</p>
                    <div className="flex items-center text-sm text-gray-500">
                      <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {businessData.serviceAreas[0] || 'Austin'}, TX
                    </div>
                  </div>
                </div>
                
                {/* Project Card 3 */}
                <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                  <div className="h-48 bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center">
                    <svg className="h-16 w-16 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Emergency Repair</h3>
                    <p className="text-gray-600 mb-4">24/7 emergency service for heating system failure during winter storm.</p>
                    <div className="flex items-center text-sm text-gray-500">
                      <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {businessData.serviceAreas[0] || 'Austin'}, TX
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="text-center">
                <a 
                  href="/projects"
                  className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                >
                  View All Projects
                  <svg className="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                  </svg>
                </a>
              </div>
            </div>
          </section>

          {/* Trust & Rating Display */}
          <Hero365TrustRating 
            ratings={[]}
          />

          {/* Customer Reviews */}
          <Hero365CustomerReviews 
            testimonials={[]}
          />

          {/* Contact Section */}
          <Hero365ContactSection 
            business={{
              id: businessId,
              name: businessData.businessName,
              phone_number: businessData.phone,
              business_email: businessData.email,
              address: businessData.address,
              service_areas: businessData.serviceAreas,
              trades: [],
              seo_keywords: []
            }}
            locations={[]}
          />

          {/* Footer */}
          <footer className="bg-gray-900 text-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                {/* Company Info */}
                <div className="lg:col-span-2">
                  <h3 className="text-2xl font-bold mb-4">{businessData.businessName || 'Professional HVAC Services'}</h3>
                  <p className="text-gray-300 mb-4">
                    Professional HVAC services for {businessData.serviceAreas[0] || 'Austin'} and surrounding areas. 
                    Licensed, insured, and committed to quality service.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center">
                      <svg className="h-5 w-5 text-blue-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21L6.16 11.37a11.045 11.045 0 005.516 5.516l1.983-4.064a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      <span>{businessData.phone || '(512) 555-0100'}</span>
                    </div>
                    <div className="flex items-center">
                      <svg className="h-5 w-5 text-blue-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      <span>{businessData.email || 'info@example.com'}</span>
                    </div>
                    <div className="flex items-center">
                      <svg className="h-5 w-5 text-blue-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      <span>{businessData.address || 'Austin, TX'}</span>
                    </div>
                  </div>
                </div>

                {/* Services */}
                <div>
                  <h4 className="text-lg font-semibold mb-4">Services</h4>
                  <ul className="space-y-2 text-gray-300">
                    <li><a href="/services/installation" className="hover:text-white transition-colors">Installation</a></li>
                    <li><a href="/services/repair" className="hover:text-white transition-colors">Repair & Maintenance</a></li>
                    <li><a href="/services/emergency" className="hover:text-white transition-colors">Emergency Service</a></li>
                    <li><a href="/services/commercial" className="hover:text-white transition-colors">Commercial Services</a></li>
                  </ul>
                </div>

                {/* Service Areas */}
                <div>
                  <h4 className="text-lg font-semibold mb-4">Service Areas</h4>
                  <ul className="space-y-2 text-gray-300">
                    {businessData.serviceAreas.length > 0 ? (
                      businessData.serviceAreas.slice(0, 4).map((area, index) => (
                        <li key={index}><a href={`/locations/${area.toLowerCase().replace(/[^a-z0-9]/g, '-')}`} className="hover:text-white transition-colors">{area}</a></li>
                      ))
                    ) : (
                      <>
                        <li><a href="/locations/austin" className="hover:text-white transition-colors">Austin, TX</a></li>
                        <li><a href="/locations/round-rock" className="hover:text-white transition-colors">Round Rock, TX</a></li>
                        <li><a href="/locations/cedar-park" className="hover:text-white transition-colors">Cedar Park, TX</a></li>
                        <li><a href="/locations/georgetown" className="hover:text-white transition-colors">Georgetown, TX</a></li>
                      </>
                    )}
                  </ul>
                </div>
              </div>

              {/* Bottom Bar */}
              <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
                <p className="text-gray-400 text-sm">
                  © {new Date().getFullYear()} {businessData.businessName || 'Professional HVAC Services'}. All rights reserved.
                </p>
                <div className="flex space-x-6 mt-4 md:mt-0">
                  <a href="/privacy" className="text-gray-400 hover:text-white text-sm transition-colors">Privacy Policy</a>
                  <a href="/terms" className="text-gray-400 hover:text-white text-sm transition-colors">Terms of Service</a>
                  <a href="/contact" className="text-gray-400 hover:text-white text-sm transition-colors">Contact</a>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </div>
  );
}

