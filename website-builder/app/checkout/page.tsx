import { Suspense } from 'react';
import { getBusinessConfig, getBackendUrl } from '@/lib/config/api-config';
import { CheckoutPageClient } from './CheckoutPageClient';
import EliteHeader from '@/components/layout/EliteHeader';
import ProfessionalFooter from '@/components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '@/components/booking/BookingWidgetProvider';
import { CartProvider } from '@/lib/contexts/CartContext';

// Force dynamic rendering for checkout page
export const dynamic = 'force-dynamic';

async function loadBusinessProfile(businessId: string) {
  try {
    // Use global backend URL configuration
    const backendUrl = getBackendUrl();
      
    console.log('🔧 [CHECKOUT] Loading business profile:', { 
      businessId, 
      backendUrl, 
      nodeEnv: process.env.NODE_ENV 
    });
      
    const response = await fetch(`${backendUrl}/api/v1/public/professional/profile/${businessId}`, {
      headers: { 'Content-Type': 'application/json' },
      cache: 'no-store'
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
    console.log('✅ [CHECKOUT] Business profile loaded successfully');
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

export default async function CheckoutPage() {
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.businessId || businessConfig.defaultBusinessId;
  const businessProfile = await loadBusinessProfile(businessId);

  // Fallback data if API fails
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
      <BookingWidgetProvider businessProfile={profile}>
        <div className="min-h-screen bg-gray-50">
          <EliteHeader businessProfile={profile} />
          
          <main>
            <Suspense 
              fallback={
                <div className="max-w-4xl mx-auto px-4 py-16">
                  <div className="bg-white rounded-lg shadow-md p-8">
                    <div className="animate-pulse space-y-6">
                      <div className="h-8 bg-gray-200 rounded w-1/3"></div>
                      <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                      <div className="space-y-4">
                        <div className="h-12 bg-gray-200 rounded"></div>
                        <div className="h-12 bg-gray-200 rounded"></div>
                        <div className="h-12 bg-gray-200 rounded"></div>
                      </div>
                    </div>
                  </div>
                </div>
              }
            >
              <CheckoutPageClient businessProfile={profile} />
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
