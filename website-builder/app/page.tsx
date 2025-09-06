/**
 * Homepage
 * 
 * Main business website that loads real business data from the Hero365 backend
 * Uses host-based resolution for multi-tenant support
 */

import React from 'react';
export const dynamic = 'force-dynamic';
export const revalidate = 0;
import Link from 'next/link';
import BusinessHeader from '@/components/shared/BusinessHeader';
import HeroSection from '@/components/server/hero/hero-section';
import ServicesGrid from '@/components/server/services/services-grid';
import { notFound } from 'next/navigation';
import Hero365ContactSection from '@/components/client/business/Hero365ContactSection';
import { getBackendUrl, getDefaultHeaders } from '@/lib/shared/config/api-config';
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver';
import { getRuntimeConfig } from '@/lib/server/runtime-config';

async function loadBusinessData(businessId: string) {
  try {
    console.log('🔄 [SERVER] Loading business data for:', businessId);
    
    // Use runtime configuration to get correct API URL for environment
    const config = await getRuntimeConfig();
    const backendUrl = config.apiUrl;
    console.log('🔄 [SERVER] Runtime config:', { environment: config.environment, backendUrl });
    
    const [profileResponse, servicesResponse, productsResponse, projectsResponse] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/contractors/profile/${businessId}`, {
        headers: getDefaultHeaders(),
        cache: 'no-store'
      }).catch(err => {
        console.log('⚠️ [SERVER] Profile API failed:', err.message);
        return { ok: false };
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/services/${businessId}`, {
        headers: getDefaultHeaders(),
        cache: 'no-store'
      }).catch(err => {
        console.log('⚠️ [SERVER] Services API failed:', err.message);
        return { ok: false };
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/product-catalog/${businessId}?featured_only=true&limit=6`, {
        headers: getDefaultHeaders(),
        cache: 'no-store'
      }).catch(err => {
        console.log('⚠️ [SERVER] Products API failed:', err.message);
        return { ok: false };
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/featured-projects/${businessId}?featured_only=true&limit=6`, {
        headers: getDefaultHeaders(),
        cache: 'no-store'
      }).catch(err => {
        console.log('⚠️ [SERVER] Projects API failed:', err.message);
        return { ok: false };
      })
    ]);
    
    let profile = null;
    let services = [];
    let products = [];
    let projects = [];

    const profileOk = !!(profileResponse && 'ok' in profileResponse && (profileResponse as Response).ok);
    const servicesOk = !!(servicesResponse && 'ok' in servicesResponse && (servicesResponse as Response).ok);
    const productsOk = !!(productsResponse && 'ok' in productsResponse && (productsResponse as Response).ok);
    const projectsOk = !!(projectsResponse && 'ok' in projectsResponse && (projectsResponse as Response).ok);
    
    if (profileOk) {
      profile = await (profileResponse as Response).json();
      console.log('✅ [SERVER] Profile loaded:', profile.business_name);
    }
    
    if (servicesOk) {
      services = await (servicesResponse as Response).json();
      console.log('✅ [SERVER] Services loaded:', services.length, 'items');
    }

    if (productsOk) {
      products = await (productsResponse as Response).json();
      console.log('✅ [SERVER] Products loaded:', products.length, 'items');
    }

    if (projectsOk) {
      projects = await (projectsResponse as Response).json();
      console.log('✅ [SERVER] Projects loaded:', projects.length, 'items');
    }
    
    return { 
      profile, 
      services, 
      products, 
      projects,
      diagnostics: {
        backendUrl,
        profileOk,
        servicesOk,
        productsOk,
        projectsOk
      }
    };
  } catch (error) {
    console.error('⚠️ [SERVER] Failed to load business data:', error);
    return { profile: null, services: [], products: [], projects: [] };
  }
}

export default async function HomePage() {
  try {
    // Get business ID from host for multi-tenant support
    const resolution = await getBusinessIdFromHost();
    const businessId = resolution.businessId;
    
    // Load business data server-side
    const { profile: serverProfile, services: serverServices, products: serverProducts, projects: serverProjects, diagnostics } = await loadBusinessData(businessId);
    
    // Debug logging
    console.log('🔍 [DEBUG] Server profile:', serverProfile ? 'LOADED' : 'NULL');
    console.log('🔍 [DEBUG] Server services count:', serverServices?.length || 0);
    console.log('🔍 [DEBUG] Server products count:', serverProducts?.length || 0);
    console.log('🔍 [DEBUG] Server projects count:', serverProjects?.length || 0);
    console.log('🔍 [DEBUG] Business ID:', businessId);
    
    // Strict: only real data. If profile is missing, show explicit error + diagnostics
    if (!serverProfile) {
      return (
        <div className="min-h-screen bg-white">
          <BusinessHeader businessProfile={null} showCTA={false} showCart={false} />
          <div className="max-w-3xl mx-auto py-16 px-4">
            <h1 className="text-2xl font-bold text-red-600 mb-4">Error: Missing business profile</h1>
            <p className="text-gray-700 mb-6">The backend did not return a profile for this business. No placeholder data is shown.</p>
            <div className="rounded-lg border bg-gray-50 p-4">
              <h2 className="font-semibold mb-2">Diagnostics</h2>
              <ul className="text-sm text-gray-700 space-y-1">
                <li><span className="font-medium">backendUrl:</span> {(diagnostics as any)?.backendUrl}</li>
                <li><span className="font-medium">profileOk:</span> {String((diagnostics as any)?.profileOk)}</li>
                <li><span className="font-medium">servicesOk:</span> {String((diagnostics as any)?.servicesOk)}</li>
                <li><span className="font-medium">productsOk:</span> {String((diagnostics as any)?.productsOk)}</li>
                <li><span className="font-medium">projectsOk:</span> {String((diagnostics as any)?.projectsOk)}</li>
                <li><span className="font-medium">businessId:</span> {businessId}</li>
              </ul>
            </div>
          </div>
        </div>
      );
    }

    const profile = serverProfile as any;

    const services = serverServices || [];

    // Generate dynamic content based on real business profile
    const primaryTradeSlugSafe = typeof (profile as any).primary_trade_slug === 'string'
      ? ((profile as any).primary_trade_slug as string)
      : 'hvac';
    const formattedTradeName = primaryTradeSlugSafe
      .split('-')
      .filter(Boolean)
      .map((word: string) => (word && word.length > 0 ? word[0].toUpperCase() + word.slice(1) : ''))
      .join(' ');

    const businessData = {
      businessName: (profile as any).business_name ?? '',
      tagline: `Professional ${formattedTradeName} Services`,
      description: (profile as any).description ?? '',
      phone: (profile as any).phone?.trim() || null,
      email: (profile as any).email ?? '',
      address: (profile as any).address ?? '',
      serviceAreas: Array.isArray((profile as any).service_areas) ? (profile as any).service_areas : [],
      emergencyService: !!(profile as any).emergency_service,
      yearsInBusiness: (profile as any).years_in_business ?? 0,
      licenseNumber: (profile as any).license_number ?? '',
      insuranceVerified: !!(profile as any).insurance_verified,
      averageRating: (profile as any).average_rating ?? 0,
      totalReviews: (profile as any).total_reviews ?? 0,
      certifications: Array.isArray((profile as any).certifications) ? (profile as any).certifications : [],
      website: (profile as any).website ?? ''
    };

    return (
      <div className="min-h-screen bg-white">
        {/* Header */}
        <BusinessHeader 
          businessProfile={profile as any}
          showCTA={false}
          showCart={false}
        />

        {/* Hero Section */}
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

        {/* Services Grid */}
        <ServicesGrid
          businessName={businessData.businessName}
          city={businessData.serviceAreas[0] || 'Austin'}
          phone={businessData.phone}
        />
        
        {/* View All Services Link */}
        <div className="text-center py-8">
          <Link
            href="/services"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            View All Services →
          </Link>
          <Link
            href="/locations"
            className="inline-flex items-center px-6 py-3 ml-4 bg-white text-blue-600 font-semibold rounded-lg border-2 border-blue-600 hover:bg-blue-50 transition-colors"
          >
            Service Areas →
          </Link>
        </div>

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
                          <div className="h-48 w-full bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center group-hover:from-blue-200 group-hover:to-blue-300 transition-colors duration-200">
                            <svg className="h-12 w-12 text-blue-400 group-hover:text-blue-500 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H3m2 0h4M9 7h6m-6 4h6m-2 4h2" />
                            </svg>
                          </div>
                        </div>
                      </div>

                      <div className="p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {product.name}
                        </h3>
                        <p className="text-gray-600 text-sm mb-4">
                          {product.description}
                        </p>
                        <div className="flex items-center justify-between mb-4">
                          <span className="text-lg font-bold text-gray-900">
                            ${(() => {
                              try {
                                const price = product.unit_price;
                                return typeof price === 'number' && !isNaN(price) ? price.toLocaleString() : '0';
                              } catch {
                                return '0';
                              }
                            })()}
                          </span>
                        </div>
                      </div>
                    </a>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Projects Showcase */}
        {serverProjects && serverProjects.length > 0 && (
          <div className="py-16 bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  Our Recent Projects
                </h2>
                <p className="text-lg text-gray-600 max-w-3xl mx-auto mb-6">
                  See examples of our professional work and satisfied customers.
                </p>
                <div className="flex justify-center">
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

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {serverProjects.slice(0, 3).filter((project: any) => project.slug).length > 0 ? (
                  serverProjects.slice(0, 3).filter((project: any) => project.slug).map((project: any) => (
                  <div key={project.id} className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-200 group border border-gray-200">
                    <a href={`/projects/${project.slug}`} className="block h-full">
                      <div className="relative">
                        <div className="aspect-w-16 aspect-h-9 w-full overflow-hidden rounded-t-lg bg-gray-200">
                          {project.featured_image_url ? (
                            <img 
                              src={project.featured_image_url} 
                              alt={project.title}
                              className="h-48 w-full object-cover group-hover:scale-105 transition-transform duration-200"
                            />
                          ) : (
                            <div className="h-48 w-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center group-hover:from-gray-200 group-hover:to-gray-300 transition-colors duration-200">
                              <svg className="h-12 w-12 text-gray-400 group-hover:text-gray-500 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H3m2 0h4M9 7h6m-6 4h6m-2 4h2" />
                              </svg>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {project.title}
                        </h3>
                        <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                          {project.description}
                        </p>
                        <div className="flex items-center justify-between mb-4">
                          <span className="text-sm font-medium text-blue-600">
                            {project.category || 'Project'}
                          </span>
                          {project.completion_date && (
                            <span className="text-sm text-gray-500">
                              {(() => {
                                try {
                                  const date = new Date(project.completion_date);
                                  return isNaN(date.getTime()) ? '' : date.getFullYear();
                                } catch {
                                  return '';
                                }
                              })()}
                            </span>
                          )}
                        </div>
                        {project.customer_testimonial && (
                          <div className="border-t pt-4">
                            <p className="text-sm text-gray-600 italic">
                              "{(() => {
                                try {
                                  const testimonial = project.customer_testimonial;
                                  return typeof testimonial === 'string' ? testimonial.slice(0, 100) : '';
                                } catch {
                                  return '';
                                }
                              })()}..."
                            </p>
                          </div>
                        )}
                      </div>
                    </a>
                  </div>
                ))) : (
                  <div className="col-span-full text-center py-8">
                    <p className="text-gray-500">No projects available at the moment.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

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
              <div className="lg:col-span-2">
                <h3 className="text-2xl font-bold mb-4">{businessData.businessName}</h3>
                <p className="text-gray-300 mb-4">
                  Professional HVAC services for {businessData.serviceAreas[0] || 'Austin'} and surrounding areas.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <svg className="h-5 w-5 text-blue-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21L6.16 11.37a11.045 11.045 0 005.516 5.516l1.983-4.064a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                    <span>{businessData.phone}</span>
                  </div>
                  <div className="flex items-center">
                    <svg className="h-5 w-5 text-blue-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <span>{businessData.email}</span>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="text-lg font-semibold mb-4">Services</h4>
                <ul className="space-y-2 text-gray-300">
                  <li><a href="/services" className="hover:text-white transition-colors">All Services</a></li>
                  <li><a href="/locations" className="hover:text-white transition-colors">Service Areas</a></li>
                </ul>
              </div>
              <div>
                <h4 className="text-lg font-semibold mb-4">Contact</h4>
                <ul className="space-y-2 text-gray-300">
                  <li><a href="/contact" className="hover:text-white transition-colors">Get Quote</a></li>
                  <li><a href="/projects" className="hover:text-white transition-colors">Our Work</a></li>
                </ul>
              </div>
            </div>
            <div className="border-t border-gray-800 mt-8 pt-8 text-center">
              <p className="text-gray-400 text-sm">
                © {new Date().getFullYear()} {businessData.businessName}. All rights reserved.
              </p>
            </div>
          </div>
        </footer>
      </div>
    );
  } catch (error) {
    console.error('⚠️ [SERVER] HomePage render error:', error);
    // notFound();
    return (
      <div className="min-h-screen bg-white">
        <div className="max-w-3xl mx-auto py-20 px-4 text-center">
          <h1 className="text-3xl font-bold mb-4">Temporary issue</h1>
          <p className="text-gray-600">We couldn’t load the page right now. Please try again shortly.</p>
        </div>
      </div>
    );
  }
}
