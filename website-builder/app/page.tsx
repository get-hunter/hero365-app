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
import Hero365ContactSection from '@/components/client/business/Hero365ContactSection';
import Hero365Footer from '@/components/shared/Hero365Footer';
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver';
import { loadHomepageData } from '@/lib/server/data-fetchers';
import { formatCurrencyUSD, formatCompletionYear, formatTradeName } from '@/lib/shared/utils/formatters';
import type { BusinessProfile, ProductItem, ProjectItem } from '@/lib/shared/types/api-responses';


export default async function HomePage() {
  try {
    // Get business ID from host for multi-tenant support
    const resolution = await getBusinessIdFromHost();
    const businessId = resolution.businessId;

    // Load business data server-side
    const { profile: serverProfile, services: serverServices, products: serverProducts, projects: serverProjects, diagnostics } = await loadHomepageData(businessId);

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

    const profile = serverProfile as BusinessProfile;

    const services = serverServices || [];

    // Generate dynamic content based on real business profile
    const primaryTradeSlugSafe = profile.primary_trade_slug || 'hvac';
    const formattedTradeName = formatTradeName(primaryTradeSlugSafe);

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

    const topProducts = (serverProducts || []).slice(0, 3);
    const topProjects = (serverProjects || []).filter((p: ProjectItem) => p.slug).slice(0, 3);

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
        {topProducts && topProducts.length > 0 && (
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
                  <Link 
                    href="/products"
                    className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Shop All Products
                    <svg className="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {topProducts.map((product: ProductItem) => (
                  <div key={product.id} className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-200 group">
                    <Link href={`/products/${product.slug}`} className="block h-full">
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
                          {product.description || ''}
                        </p>
                        <div className="flex items-center justify-between mb-4">
                          <span className="text-lg font-bold text-gray-900">
                            {formatCurrencyUSD(product.unit_price)}
                          </span>
                        </div>
                      </div>
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Projects Showcase */}
        {topProjects && topProjects.length > 0 && (
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
                  <Link 
                    href="/projects"
                    className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    View All Projects
                    <svg className="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {topProjects.map((project: ProjectItem) => (
                  <div key={project.id} className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-200 group border border-gray-200">
                    <Link href={`/projects/${project.slug}`} className="block h-full">
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
                          {project.description || ''}
                        </p>
                        <div className="flex items-center justify-between mb-4">
                          <span className="text-sm font-medium text-blue-600">
                            {project.category || 'Project'}
                          </span>
                          {project.completion_date && (
                            <span className="text-sm text-gray-500">
                              {formatCompletionYear(project.completion_date)}
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
                    </Link>
                  </div>
                ))}
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
        <Hero365Footer 
          business={profile}
          services={serverServices}
          showEmergencyBanner={businessData.emergencyService}
        />
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
