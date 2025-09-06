import React from 'react';
import { Metadata } from 'next';
import BusinessHeader from '@/components/shared/BusinessHeader';
import Hero365Footer from '@/components/shared/Hero365Footer';
import ProductListingClient from './ProductListingClient';
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver';
import { loadPageData } from '@/lib/server/data-fetchers';
import { notFound } from 'next/navigation';
import type { BusinessProfile, ProductItem } from '@/lib/shared/types/api-responses';

export const metadata: Metadata = {
  title: 'Professional Products & Installation Services - Shop Online',
  description: 'Shop professional-grade HVAC, electrical, and plumbing products with expert installation. Get instant pricing with membership discounts.',
};


export default async function ProductsPage() {
  // Get business ID from host for multi-tenant support
  const resolution = await getBusinessIdFromHost();
  const businessId = resolution.businessId;
  
  const { 
    profile: serverProfile,
    products: serverProducts,
    categories: serverCategories
  } = await loadPageData(businessId, {
    includeProducts: true,
    includeCategories: true
  });
  
  // Enforce no-fallback policy
  if (!serverProfile) {
    notFound();
  }
  
  const profile = serverProfile;


  return (
      <div className="min-h-screen bg-gray-50">
        <BusinessHeader 
          businessProfile={serverProfile}
          showCTA={false}
          showCart={true}
        />

        {/* Products Page Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h1 className="text-4xl font-bold mb-4">
                Professional Products & Installation
              </h1>
              <p className="text-xl text-blue-100 mb-6 max-w-3xl mx-auto">
                Shop professional-grade equipment with expert installation services. 
                Get instant pricing with membership discounts and bundle savings.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-white/90">
                <div className="flex items-center gap-2">
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                  <span>Instant Pricing Calculator</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <span>Professional Installation</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                  </svg>
                  <span>Member Exclusive Discounts</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Product Listing Content */}
        <ProductListingClient 
          products={serverProducts}
          categories={serverCategories}
          businessId={businessId}
          hasRealData={serverProducts.length > 0}
        />

        <Hero365Footer 
          business={profile}
          showEmergencyBanner={!!profile.emergency_service}
        />

        {serverProducts.length === 0 && (
          <div className="fixed bottom-4 right-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded shadow-lg max-w-sm z-50">
            <strong className="font-bold">Development Notice:</strong>
            <span className="block sm:inline"> Backend connection required for product data.</span>
          </div>
        )}
      </div>
  );
}
