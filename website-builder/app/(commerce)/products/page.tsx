import React from 'react';
import { Metadata } from 'next';
import Hero365Header from '@/components/server/layout/Hero365Header';
import Hero365Footer from '@/components/shared/Hero365Footer';
import ProductListingClient from './ProductListingClient';
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver';
import { loadPageData } from '@/lib/server/data-fetchers';
import { notFound } from 'next/navigation';
import type { BusinessProfile, ProductItem, ServiceCategory } from '@/lib/shared/types/api-responses';
import type { ProductCatalogItem, ProductCategory } from '@/lib/shared/types/products';


export const metadata: Metadata = {
  title: 'Professional Products & Installation Services - Shop Online',
  description: 'Shop professional-grade HVAC, electrical, and plumbing products with expert installation. Get instant pricing with membership discounts.',
};


export default async function ProductsPage() {
  // Get business ID from host for multi-tenant support
  const resolution = await getBusinessIdFromHost();
  const businessId = resolution.businessId;
  
  // Fetch regular products and service categories
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

  // Convert regular products to ProductCatalogItem[] format
  const convertedProducts: ProductCatalogItem[] = serverProducts.map((product: ProductItem) => ({
    id: product.id.toString(),
    name: product.name,
    sku: product.sku || '',
    description: product.description || '',
    long_description: product.description || '',
    unit_price: typeof product.unit_price === 'string' ? parseFloat(product.unit_price) : (product.unit_price || 0),
    category_name: product.category || 'General',
    warranty_years: undefined,
    energy_efficiency_rating: undefined,
    requires_professional_install: false,
    install_complexity: 'standard' as const,
    installation_time_estimate: undefined,
    featured_image_url: product.image_url || undefined,
    gallery_images: [],
    product_highlights: [],
    technical_specs: {},
    meta_title: undefined,
    meta_description: undefined,
    slug: product.slug || product.name.toLowerCase().replace(/\s+/g, '-'),
    is_active: true,
    is_featured: product.featured || false,
    current_stock: undefined,
    installation_options: []
  }));

  // Create service-based filters using actual service data
  const serviceFilters: ProductCategory[] = [
    {
      id: 'all',
      name: 'All Products',
      product_count: convertedProducts.length,
      sort_order: -1
    },
    ...serverCategories.map((category: ServiceCategory) => ({
      id: category.slug,
      name: category.name,
      product_count: 0, // Will be populated dynamically when filtering
      sort_order: category.sort_order || 0
    }))
  ];

  return (
      <div className="min-h-screen bg-gray-50">
        <Hero365Header 
          businessProfile={{
            business_id: (profile.business_id as string) || '',
            business_name: profile.business_name || '',
            phone: profile.phone || '',
            phone_display: profile.phone || '',
            email: profile.email || '',
            address: profile.address || '',
            city: profile.city || '',
            state: profile.state || '',
            postal_code: profile.postal_code || '',
            logo_url: profile.logo_url || ''
          }}
          showCTA={true}
          showCart={true}
        />

        {/* Compact header (no hero) */}
        <section className="px-4 sm:px-6 lg:px-8 pt-6 pb-4 border-b border-gray-100 bg-white">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Products</h1>
              <p className="mt-1 text-sm text-gray-600">Shop professional-grade products with installation.</p>
            </div>
            <div className="hidden md:flex items-center gap-2 text-sm text-gray-500">
              <span>{convertedProducts.length} items</span>
              <span>•</span>
              <span>{serviceFilters.length - 1} categories</span>
            </div>
          </div>
        </section>

        {/* Product Listing Content */}
        <ProductListingClient 
          products={convertedProducts}
          categories={serviceFilters}
          businessId={businessId}
          hasRealData={serverProducts.length > 0}
        />

        <Hero365Footer 
          business={profile as any}
          showEmergencyBanner={!!(profile as any).emergency_service}
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
