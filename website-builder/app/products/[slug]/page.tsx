import { ProductDetailClient } from './ProductDetailClient';
import { getBusinessConfig, getBackendUrl } from '@/lib/config/api-config';
import { BookingWidgetProvider } from '@/components/booking/BookingWidgetProvider';
import { CartProvider } from '@/lib/contexts/CartContext';
import EliteHeader from '@/components/layout/EliteHeader';
import ProfessionalFooter from '@/components/professional/ProfessionalFooter';

export const revalidate = 300;
export const runtime = 'edge';

async function getProduct(businessId: string, slug: string) {
  // Call backend API directly (CORS is allowed in local env), absolute URL required on server
  const base = getBackendUrl();
  const url = `${base}/api/v1/public/contractors/product-by-slug/${businessId}/${encodeURIComponent(slug)}`;
  const res = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
    cache: 'no-store'
  });
  if (!res.ok) {
    return null;
  }
  return res.json();
}

async function getBusinessProfile(businessId: string) {
  const base = getBackendUrl();
  const url = `${base}/api/v1/public/contractors/profile/${businessId}`;
  const res = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
    cache: 'no-store'
  });
  if (!res.ok) return null;
  return res.json();
}

async function getMembershipPlans(businessId: string) {
  try {
    const base = getBackendUrl();
    const url = `${base}/api/v1/public/contractors/membership-plans/${businessId}`;
    const res = await fetch(url, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      cache: 'no-store'
    });
    if (!res.ok) return [];
    return res.json();
  } catch (error) {
    console.error('Failed to load membership plans:', error);
    return [];
  }
}

export default async function ProductDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const businessId = getBusinessConfig().defaultBusinessId;
  const { slug } = await params;
  const [product, profile, membershipPlans] = await Promise.all([
    getProduct(businessId, slug),
    getBusinessProfile(businessId),
    getMembershipPlans(businessId)
  ]);

  if (!product) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16">
        <h1 className="text-2xl font-semibold mb-2">Product not found</h1>
        <p className="text-gray-600">Please go back to the products page and try another item.</p>
        <a href="/products" className="inline-block mt-6 px-4 py-2 bg-blue-600 text-white rounded">Back to Products</a>
      </div>
    );
  }

  // Prefer real profile; fallback to defaults
  const businessProfile = profile || ({
    business_name: 'Professional Services',
    phone: '(555) 123-4567',
    email: 'info@example.com',
    address: 'Local Area',
    service_areas: ['Local Area']
  } as any);
  const categories: any[] = [];

  return (
    <CartProvider businessId={businessId}>
      <BookingWidgetProvider
        businessId={businessId}
        services={[]}
        companyName={businessProfile.business_name}
        companyPhone={businessProfile.phone}
        companyEmail={businessProfile.email}
      >
        <div className="min-h-screen bg-white">
          <EliteHeader 
            businessName={businessProfile.business_name}
            city={businessProfile.service_areas?.[0] || 'Austin'}
            state={'TX'}
            phone={businessProfile.phone}
            supportHours={'24/7'}
          />

          <ProductDetailClient 
            product={product}
            businessId={businessId}
            businessProfile={businessProfile}
            categories={categories}
            membershipPlans={membershipPlans}
          />

          <ProfessionalFooter 
            business={{
              id: businessId,
              name: businessProfile.business_name,
              phone_number: businessProfile.phone,
              business_email: businessProfile.email,
              address: businessProfile.address,
              website: (businessProfile as any)?.website,
              service_areas: businessProfile.service_areas,
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
