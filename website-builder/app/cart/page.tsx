import { Suspense } from 'react';
import { getBusinessConfig } from '@/lib/config/api-config';
import { CartPageClient } from './CartPageClient';
import EliteHeader from '@/components/layout/EliteHeader';
import ProfessionalFooter from '@/components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '@/components/booking/BookingWidgetProvider';
import { CartProvider } from '@/lib/contexts/CartContext';

async function loadBusinessProfile(businessId: string) {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    
    const response = await fetch(`${backendUrl}/api/v1/public/contractors/profile/${businessId}`, {
      headers: { 'Content-Type': 'application/json' }
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
                <p className="text-gray-600">Loading your cart...</p>
              </div>
            </div>
          }>
            <CartPageClient businessProfile={businessProfile} />
          </Suspense>
          
          <ProfessionalFooter 
            business={{
              id: businessProfile.id || 'default-id',
              name: businessProfile.business_name,
              phone_number: businessProfile.phone,
              business_email: businessProfile.email,
              address: businessProfile.address,
              website: profile?.website,
              trades: businessProfile.trades || [],
              service_areas: businessProfile.service_areas || [],
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
