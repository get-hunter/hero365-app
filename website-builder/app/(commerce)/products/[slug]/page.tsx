import { ProductDetailClient } from './ProductDetailClient';
import { getDefaultHeaders } from '@/lib/shared/config/api-config';
import { getRuntimeConfig } from '@/lib/server/runtime-config';
import { Hero365BookingProvider } from '@/components/client/commerce/booking/Hero365BookingProvider';
import { CartProvider } from '@/lib/client/contexts/CartContext';
import Hero365Header from '@/components/server/layout/Hero365Header';
import Hero365Footer from '@/components/shared/Hero365Footer';
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver';
import { notFound } from 'next/navigation';

export const dynamic = 'force-dynamic';
export const revalidate = 300;
// Note: Using Node.js runtime for OpenNext compatibility

async function getProduct(businessId: string, slug: string) {
  try {
    const config = await getRuntimeConfig();
    const base = config.apiUrl;
    const url = `${base}/api/v1/public/contractors/product-by-slug/${businessId}/${encodeURIComponent(slug)}`;
    console.log('🔄 [PRODUCT] Loading product:', slug, 'for business:', businessId);
    
    const res = await fetch(url, {
      headers: getDefaultHeaders(),
      next: { revalidate: 300, tags: ['product', businessId, slug] }
    });
    
    if (!res.ok) {
      console.error('❌ [PRODUCT] Product API failed:', res.status, res.statusText);
      return null;
    }
    
    const product = await res.json();
    console.log('✅ [PRODUCT] Product loaded:', product.name);
    return product;
  } catch (error) {
    console.error('❌ [PRODUCT] Product API error:', error);
    return null;
  }
}

async function getBusinessProfile(businessId: string) {
  try {
    const config = await getRuntimeConfig();
    const base = config.apiUrl;
    const url = `${base}/api/v1/public/contractors/profile/${businessId}`;
    
    const res = await fetch(url, {
      headers: getDefaultHeaders(),
      next: { revalidate: 3600, tags: ['profile', businessId] }
    });
    
    if (!res.ok) {
      console.error('❌ [PRODUCT] Profile API failed:', res.status, res.statusText);
      return null;
    }
    
    const profile = await res.json();
    console.log('✅ [PRODUCT] Profile loaded:', profile.business_name);
    return profile;
  } catch (error) {
    console.error('❌ [PRODUCT] Profile API error:', error);
    return null;
  }
}

async function getMembershipPlans(businessId: string) {
  // Try API calls during build time for hybrid rendering

  try {
    const config = await getRuntimeConfig();
    const base = config.apiUrl;
    const url = `${base}/api/v1/public/contractors/membership-plans/${businessId}`;
    const res = await fetch(url, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      cache: 'no-store'
    });
    if (!res.ok) return [];
    return res.json();
  } catch (error) {
    console.log('⚠️ [PRODUCT] Membership plans API failed:', error.message);
    return [];
  }
}

export default async function ProductDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  // Get business ID from host for multi-tenant support
  const resolution = await getBusinessIdFromHost();
  const businessId = resolution.businessId;
  
  const { slug } = await params;
  const [product, profile, membershipPlans] = await Promise.all([
    getProduct(businessId, slug),
    getBusinessProfile(businessId),
    getMembershipPlans(businessId)
  ]);

  // Enforce no-fallback policy
  if (!product || !profile) {
    notFound();
  }

  const businessProfile = profile;
  const categories: any[] = [];

  return (
    <CartProvider businessId={businessId}>
      <Hero365BookingProvider
        businessId={businessId}
        services={[]}
        companyName={businessProfile.business_name}
        companyPhone={businessProfile.phone}
        companyEmail={businessProfile.email}
      >
        <div className="min-h-screen bg-white">
          <Hero365Header 
            businessProfile={businessProfile}
            showCTA={true}
            showCart={true}
          />

          <ProductDetailClient 
            product={product}
            businessId={businessId}
            businessProfile={businessProfile}
            categories={categories}
            membershipPlans={membershipPlans}
          />

          <Hero365Footer 
            business={{
              business_id: businessId,
              business_name: businessProfile.business_name,
              description: (businessProfile as any).description,
              phone: businessProfile.phone,
              email: businessProfile.email,
              address: businessProfile.address,
              city: (businessProfile as any).city,
              state: (businessProfile as any).state,
              postal_code: (businessProfile as any).postal_code,
              website: (businessProfile as any)?.website,
              years_in_business: (businessProfile as any).years_in_business,
              average_rating: (businessProfile as any).average_rating,
              license_number: (businessProfile as any).license_number,
              emergency_service: !!(businessProfile as any).emergency_service,
              service_areas: (businessProfile as any).service_areas || []
            }}
            services={[]}
            locations={[]}
          />
        </div>
      </Hero365BookingProvider>
    </CartProvider>
  );
}
