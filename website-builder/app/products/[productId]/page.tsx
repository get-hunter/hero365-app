import { Suspense } from 'react';
import { getBusinessConfig } from '@/lib/config/api-config';
import { ProductDetailClient } from './ProductDetailClient';
import EliteHeader from '@/components/layout/EliteHeader';
import ProfessionalFooter from '@/components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '@/components/booking/BookingWidgetProvider';
import { CartProvider } from '@/lib/contexts/CartContext';
import { ProductCatalogItem, ProductCategory } from '@/lib/types/products';

async function loadProductData(businessId: string, productId: string) {
  try {
    console.log('🔄 [PRODUCT DETAIL] Loading product data for:', productId);
    
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    
    const [productResponse, profileResponse, categoriesResponse] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/professional/product/${businessId}/${productId}`, {
        headers: { 'Content-Type': 'application/json' }
      }),
      fetch(`${backendUrl}/api/v1/public/professional/profile/${businessId}`, {
        headers: { 'Content-Type': 'application/json' }
      }),
      fetch(`${backendUrl}/api/v1/public/professional/product-categories/${businessId}`, {
        headers: { 'Content-Type': 'application/json' }
      })
    ]);
    
    let product = null;
    let profile = null;
    let categories: ProductCategory[] = [];
    
    if (productResponse.ok) {
      product = await productResponse.json();
      console.log('✅ [PRODUCT DETAIL] Product loaded:', product.name);
    } else {
      console.error('❌ [PRODUCT DETAIL] Product not found:', productResponse.status);
    }
    
    if (profileResponse.ok) {
      profile = await profileResponse.json();
      console.log('✅ [PRODUCT DETAIL] Profile loaded:', profile.business_name);
    }

    if (categoriesResponse.ok) {
      categories = await categoriesResponse.json();
      console.log('✅ [PRODUCT DETAIL] Categories loaded:', categories.length, 'items');
    }
    
    return { product, profile, categories };
  } catch (error) {
    console.error('⚠️ [PRODUCT DETAIL] Failed to load product data:', error);
    return { product: null, profile: null, categories: [] };
  }
}

interface ProductDetailPageProps {
  params: {
    productId: string;
  };
}

export default async function ProductDetailPage({ params }: ProductDetailPageProps) {
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.defaultBusinessId;
  
  const { product, profile, categories } = await loadProductData(businessId, params.productId);
  
  // If product not found, show 404
  if (!product) {
    return (
      <BookingWidgetProvider
        businessId={businessId}
        companyName={businessConfig.defaultBusinessName}
        companyPhone={businessConfig.defaultBusinessPhone}
        companyEmail={businessConfig.defaultBusinessEmail}
        services={[]}
      >
        <div className="min-h-screen bg-white">
          <EliteHeader 
            businessName={businessConfig.defaultBusinessName}
            city="Austin"
            state="TX"
            phone={businessConfig.defaultBusinessPhone}
            supportHours="24/7"
          />
          
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Product Not Found</h1>
            <p className="text-lg text-gray-600 mb-8">
              The product you're looking for doesn't exist or has been removed.
            </p>
            <div className="space-x-4">
              <a 
                href="/products"
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
              >
                Browse All Products
              </a>
              <a 
                href="/"
                className="inline-flex items-center px-6 py-3 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
              >
                Back to Home
              </a>
            </div>
          </div>
          
          <ProfessionalFooter 
            business={{
              name: businessConfig.defaultBusinessName,
              phone: businessConfig.defaultBusinessPhone,
              email: businessConfig.defaultBusinessEmail,
              address: "Serving Your Local Area",
              license_number: "Licensed & Insured",
              website: undefined,
              service_areas: ["Local Area"]
            }}
            serviceCategories={[]}
            locations={[]}
          />
        </div>
      </BookingWidgetProvider>
    );
  }

  // Use profile data or fallback to config
  const businessProfile = profile || {
    business_name: businessConfig.defaultBusinessName,
    phone: businessConfig.defaultBusinessPhone,
    email: businessConfig.defaultBusinessEmail,
    address: "Serving Your Local Area",
    service_areas: ["Local Area"]
  };

  return (
    <CartProvider businessId={businessId}>
      <BookingWidgetProvider
        businessId={businessId}
        companyName={businessProfile.business_name}
        companyPhone={businessProfile.phone}
        companyEmail={businessProfile.email}
        services={[]}
      >
        <div className="min-h-screen bg-white">
        <EliteHeader 
          businessName={businessProfile.business_name}
          city={businessProfile.service_areas?.[0] || "Austin"}
          state="TX"
          phone={businessProfile.phone}
          supportHours="24/7"
        />
        
        <Suspense fallback={
          <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading product details...</p>
            </div>
          </div>
        }>
          <ProductDetailClient 
            product={product}
            businessId={businessId}
            businessProfile={businessProfile}
            categories={categories}
          />
        </Suspense>
        
        <ProfessionalFooter 
          business={{
            name: businessProfile.business_name,
            phone: businessProfile.phone,
            email: businessProfile.email,
            address: businessProfile.address,
            license_number: profile?.license_number || "Licensed & Insured",
            website: profile?.website,
            service_areas: businessProfile.service_areas
          }}
          serviceCategories={[]}
          locations={[]}
        />
        </div>
      </BookingWidgetProvider>
    </CartProvider>
  );
}
