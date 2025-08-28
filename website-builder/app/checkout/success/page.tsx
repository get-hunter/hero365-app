"use client";

import { Suspense } from 'react';
import { CheckoutSuccessClient } from './CheckoutSuccessClient';
import EliteHeader from '@/components/layout/EliteHeader';
import ProfessionalFooter from '@/components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '@/components/booking/BookingWidgetProvider';
import { CartProvider } from '@/lib/contexts/CartContext';
import { getBusinessConfig } from '@/lib/config/api-config';

export default function CheckoutSuccessPage() {
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.defaultBusinessId;

  const profile = {
    business_id: businessId,
    business_name: businessConfig.defaultBusinessName || 'Professional Services',
    phone: businessConfig.defaultBusinessPhone || '(555) 123-4567',
    email: businessConfig.defaultBusinessEmail || 'info@hero365.app',
    address: 'Serving Your Local Area'
  };

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
            <Suspense fallback={null}>
              <CheckoutSuccessClient businessProfile={profile} />
            </Suspense>
          </main>
          
          <ProfessionalFooter 
            business={profile as any} 
            serviceCategories={[]} 
            locations={[]} 
          />
        </div>
      </BookingWidgetProvider>
    </CartProvider>
  );
}
