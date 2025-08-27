import { Suspense } from 'react';
import { CheckoutSuccessClient } from './CheckoutSuccessClient';
import EliteHeader from '@/components/layout/EliteHeader';
import ProfessionalFooter from '@/components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '@/components/booking/BookingWidgetProvider';
import { CartProvider } from '@/lib/contexts/CartContext';
import { getBusinessConfig } from '@/lib/config/api-config';

// Force dynamic rendering for checkout success page
export const dynamic = 'force-dynamic';

async function loadBusinessProfile(businessId: string) {
  try {
    const backendUrl = process.env.NODE_ENV === 'production' 
      ? 'https://api.hero365.app' 
      : 'http://127.0.0.1:8000';
      
    const response = await fetch(`${backendUrl}/api/v1/public/professional/profile/${businessId}`, {
      headers: { 'Content-Type': 'application/json' },
      cache: 'no-store'
    });

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    return null;
  }
}

export default async function CheckoutSuccessPage() {
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.businessId || businessConfig.defaultBusinessId;
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
      <BookingWidgetProvider businessProfile={profile}>
        <div className="min-h-screen bg-gray-50">
          <EliteHeader businessProfile={profile} />
          
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
