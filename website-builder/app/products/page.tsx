import React from 'react';
import { Metadata } from 'next';
import EliteHeader from '../../components/layout/EliteHeader';
import ProfessionalFooter from '../../components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '../../components/booking/BookingWidgetProvider';
import { CartProvider } from '../../lib/contexts/CartContext';
import ProductListingClient from './ProductListingClient';
import { getBusinessConfig } from '../../lib/config/api-config';

export const metadata: Metadata = {
  title: 'Professional Products & Installation Services - Shop Online',
  description: 'Shop professional-grade HVAC, electrical, and plumbing products with expert installation. Get instant pricing with membership discounts.',
};

async function loadProductData(businessId: string) {
  try {
    console.log('🔄 [PRODUCTS] Loading product catalog for:', businessId);
    
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    
    const [catalogResponse, categoriesResponse, profileResponse] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/professional/product-catalog/${businessId}`, {
        headers: { 'Content-Type': 'application/json' },
        next: { revalidate: 300 } // Cache for 5 minutes
      }),
      fetch(`${backendUrl}/api/v1/public/professional/product-categories/${businessId}`, {
        headers: { 'Content-Type': 'application/json' },
        next: { revalidate: 600 } // Cache for 10 minutes
      }),
      fetch(`${backendUrl}/api/v1/public/professional/profile/${businessId}`, {
        headers: { 'Content-Type': 'application/json' },
        next: { revalidate: 600 } // Cache for 10 minutes
      })
    ]);
    
    let products = [];
    let categories = [];
    let profile = null;
    
    if (catalogResponse.ok) {
      products = await catalogResponse.json();
      console.log('✅ [PRODUCTS] Products loaded:', products.length, 'items');
    }
    
    if (categoriesResponse.ok) {
      categories = await categoriesResponse.json();
      console.log('✅ [PRODUCTS] Categories loaded:', categories.length, 'categories');
    }
    
    if (profileResponse.ok) {
      profile = await profileResponse.json();
      console.log('✅ [PRODUCTS] Profile loaded:', profile.business_name);
    }
    
    return { products, categories, profile };
  } catch (error) {
    console.error('⚠️ [PRODUCTS] Failed to load product data:', error);
    return { products: [], categories: [], profile: null };
  }
}

export default async function ProductsPage() {
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.defaultBusinessId;
  
  const { 
    products: serverProducts,
    categories: serverCategories, 
    profile: serverProfile
  } = await loadProductData(businessId);
  
  const profile = serverProfile || {
    business_id: businessId,
    business_name: businessConfig.defaultBusinessName,
    trade_type: 'hvac',
    phone: businessConfig.defaultBusinessPhone,
    email: businessConfig.defaultBusinessEmail,
    address: '123 Main St',
    service_areas: ['Local Area'],
    emergency_service: true,
    years_in_business: 10,
    average_rating: 4.8,
    total_reviews: 150
  };

  const businessData = {
    businessName: profile.business_name,
    phone: profile.phone,
    email: profile.email,
    address: profile.address,
    serviceAreas: profile.service_areas || ['Local Area'],
    emergencyService: profile.emergency_service,
    yearsInBusiness: profile.years_in_business,
    licenseNumber: profile.license_number || 'Licensed & Insured',
    insuranceVerified: true,
    averageRating: profile.average_rating,
    totalReviews: profile.total_reviews,
    certifications: profile.certifications || []
  };

  return (
    <CartProvider businessId={businessId}>
      <BookingWidgetProvider
        businessId={businessId}
        companyName={businessData.businessName}
        companyPhone={businessData.phone}
        companyEmail={businessData.email}
        services={[]}
      >
      <div className="min-h-screen bg-gray-50">
        <EliteHeader 
          businessName={businessData.businessName}
          city={businessData.serviceAreas[0] || 'Austin'}
          state={'TX'}
          phone={businessData.phone}
          supportHours={'24/7'}
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

        <ProfessionalFooter 
          business={{
            name: businessData.businessName,
            phone: businessData.phone,
            email: businessData.email,
            address: businessData.address,
            license_number: businessData.licenseNumber,
            website: undefined,
            service_areas: businessData.serviceAreas
          }}
          serviceCategories={[]}
          locations={[]}
        />

        {serverProducts.length === 0 && (
          <div className="fixed bottom-4 right-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded shadow-lg max-w-sm z-50">
            <strong className="font-bold">Development Notice:</strong>
            <span className="block sm:inline"> Backend connection required for product data.</span>
          </div>
        )}
      </div>
      </BookingWidgetProvider>
    </CartProvider>
  );
}
