import { Suspense } from 'react';
import { CheckoutSuccessClient } from './CheckoutSuccessClient';
import EliteHeader from '@/components/layout/EliteHeader';
import ProfessionalFooter from '@/components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '@/components/booking/BookingWidgetProvider';
import { CartProvider } from '@/lib/contexts/CartContext';
import { getBusinessConfig, getBackendUrl } from '@/lib/config/api-config';

// Configure for Edge Runtime (required for Cloudflare Pages)
export const runtime = 'edge';

async function loadBusinessProfile(businessId: string) {
  try {
    // Use global backend URL configuration
    const backendUrl = getBackendUrl();
      
    console.log('🔧 [CHECKOUT-SUCCESS] Loading business profile:', { 
      businessId, 
      backendUrl, 
      nodeEnv: process.env.NODE_ENV 
    });
      
    const response = await fetch(`${backendUrl}/api/v1/public/contractors/profile/${businessId}`, {
      headers: { 'Content-Type': 'application/json' },
      next: { revalidate: 3600, tags: ['profile', businessId] } // 1 hour ISR
    });

    if (!response.ok) {
      console.error('Failed to fetch business profile:', {
        status: response.status,
        statusText: response.statusText,
        url: response.url
      });
      return null;
    }

    const data = await response.json();
    console.log('✅ [CHECKOUT-SUCCESS] Business profile loaded successfully');
    return data;
  } catch (error) {
    console.error('Error loading business profile:', {
      error: error instanceof Error ? error.message : error,
      businessId,
      backendUrl: getBackendUrl()
    });
    return null;
  }
}

export default async function CheckoutSuccessPage() {
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.defaultBusinessId;
  const businessProfile = await loadBusinessProfile(businessId);

  const fallbackProfile = {
    business_id: businessId,
    business_name: "Professional Services",
    phone: "(555) 123-4567",
    email: "info@hero365.app",
    address: "123 Main St, Austin, TX 78701"
  };

  const profile = businessProfile || fallbackProfile;

  return (
    <CartProvider businessId={businessId}>
      <BookingWidgetProvider 
        businessId={businessId}
        services={[]}
        companyName={profile.business_name}
        companyPhone={profile.phone}
        companyEmail={profile.email}
      >
        <div className="min-h-screen bg-gray-50">
          <EliteHeader 
            businessName={profile.business_name}
            city="Austin"
            state="TX"
            phone={profile.phone}
            supportHours="24/7"
          />
          
          <main>
            <Suspense 
              fallback={
                <div className="max-w-4xl mx-auto px-4 py-16">
                  <div className="bg-white rounded-lg shadow-md p-8 text-center">
                    <div className="animate-pulse">
                      <div className="h-8 bg-gray-200 rounded w-1/2 mx-auto mb-4"></div>
                      <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto mb-8"></div>
                      <div className="h-32 bg-gray-200 rounded mb-6"></div>
                    </div>
                  </div>
                </div>
              }
            >
              <CheckoutSuccessClient businessProfile={profile} />
            </Suspense>
          </main>
          
          <ProfessionalFooter 
            business={profile} 
            serviceCategories={[]} 
            locations={[]} 
          />
        </div>
      </BookingWidgetProvider>
    </CartProvider>
  );
}
