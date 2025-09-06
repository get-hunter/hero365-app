/**
 * Booking Page Client Component
 * 
 * Client-side booking wizard with real business data
 */

'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import Hero365Header from '@/components/shared/Hero365Header';
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

export function BookingPageClient({ businessProfile, businessServices, businessId }: BookingPageClientProps) {
  // Transform business profile to header format
  // Business data is now handled by Hero365Header component

  // Transform services for booking provider
  const bookingServices = businessServices.map(service => ({
    id: service.id || service.service_id,
    name: service.service_name || service.name,
    description: service.description || `Professional ${service.service_name || service.name} service`,
    price: service.base_price || 150,
    duration: service.estimated_duration || 60,
    category: service.category || 'Service'
  }));

  return (
    <Hero365BookingProvider
      businessId={businessId}
      services={bookingServices}
      companyName={businessProfile.business_name}
      companyPhone={businessProfile.phone_display || businessProfile.phone}
      primaryColor="#2563eb"
    >
      <div className="min-h-screen bg-gray-50">
        <Hero365Header
          businessProfile={businessProfile}
          showCTA={true}
          showCart={true}
        />

        <main>
          <Hero365BookingWizard />
        </main>
      </div>
    </Hero365BookingProvider>
  );
}
