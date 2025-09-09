/**
 * Booking Page Client Component
 * 
 * Client-side booking wizard with real business data
 */

'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { Hero365BookingProvider } from '@/components/client/commerce/booking/Hero365BookingProvider';

// Dynamically import the booking wizard to avoid SSR issues
const Hero365BookingWizard = dynamic(
  () => import('@/components/client/commerce/booking/Hero365BookingWizard'),
  { 
    ssr: false,
    loading: () => (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading booking system...</p>
        </div>
      </div>
    )
  }
);

interface BookingPageClientProps {
  businessProfile: any;
  businessServices: any[];
  businessId: string;
}

export default function BookingPageClient({ businessProfile, businessServices, businessId }: BookingPageClientProps) {
  // Transform services for booking provider (popup integration, carts, etc.)
  const bookingServices = businessServices.map(service => ({
    id: String(service.id || service.service_id),
    name: service.service_name || service.name,
    description: service.description || `Professional ${service.service_name || service.name} service`,
    price: service.base_price || 150,
    duration: service.estimated_duration || service.estimated_duration_minutes || 60,
    category: service.category || 'Service'
  }));

  // Transform services for inline booking wizard (expects estimated_duration_minutes/base_price)
  const wizardServices = businessServices.map(service => ({
    id: String(service.id || service.service_id),
    name: service.service_name || service.name,
    category: service.category || 'Service',
    description: service.description || '',
    estimated_duration_minutes: service.estimated_duration || service.estimated_duration_minutes || undefined,
    base_price: service.base_price || undefined
  }));

  const countryCode = (businessProfile?.country_code || 'US').toUpperCase();

  return (
    <Hero365BookingProvider
      businessId={businessId}
      services={bookingServices as any}
      companyName={businessProfile.business_name}
      companyPhone={businessProfile.phone_display || businessProfile.phone}
      primaryColor="#2563eb"
      countryCode={countryCode}
    >
      <main>
        <Hero365BookingWizard businessId={businessId} services={wizardServices as any} />
      </main>
    </Hero365BookingProvider>
  );
}
