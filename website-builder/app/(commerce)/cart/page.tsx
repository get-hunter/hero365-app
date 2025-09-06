import { Suspense } from 'react';
import { getBusinessConfig, getDefaultHeaders } from '@/lib/shared/config/api-config';
import { getRuntimeConfig } from '@/lib/server/runtime-config';
import { CartPageClient } from './CartPageClient';

// Static generation enabled for Cloudflare Pages
import Hero365Header from '@/components/server/layout/Hero365Header';
import Hero365Footer from '@/components/shared/Hero365Footer';
import { Hero365BookingProvider } from '@/components/client/commerce/booking/Hero365BookingProvider';
import { CartProvider } from '@/lib/client/contexts/CartContext';

async function loadBusinessProfile(businessId: string) {
  try {
    const config = await getRuntimeConfig();
    const backendUrl = config.apiUrl;
    
    const response = await fetch(`${backendUrl}/api/v1/public/contractors/profile/${businessId}`, {
      headers: getDefaultHeaders()
    });
    
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.error('Failed to load business profile:', error);
  }
  
  return null;
}

export default async function CartPage() {
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.defaultBusinessId;
  
  const profile = await loadBusinessProfile(businessId);
  
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
      <Hero365BookingProvider
        businessId={businessId}
        companyName={businessProfile.business_name}
        companyPhone={businessProfile.phone}
        companyEmail={businessProfile.email}
        services={[]}
      >
        <div className="min-h-screen bg-white">
          <Hero365Header 
            businessProfile={businessProfile}
            showCTA={false}
            showCart={true}
          />
          
          <Suspense fallback={
            <div className="min-h-screen flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading your cart...</p>
              </div>
            </div>
          }>
            <CartPageClient businessProfile={businessProfile} />
          </Suspense>
          
          <Hero365Footer 
            business={businessProfile}
            showEmergencyBanner={!!businessProfile.emergency_service}
          />
        </div>
      </Hero365BookingProvider>
    </CartProvider>
  );
}
