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
  // Map trade slugs to display names (using the new normalized data model)
  const getTradeDisplayName = (service: any): string => {
    // First try the new normalized fields
    if (service.trade_display_name) {
      return service.trade_display_name;
    }
    
    if (service.trade_slug) {
      const tradeMap: Record<string, string> = {
        'hvac': 'HVAC',
        'plumbing': 'Plumbing', 
        'electrical': 'Electrical',
        'roofing': 'Roofing',
        'chimney': 'Chimney',
        'garage-door': 'Garage Door',
        'septic': 'Septic',
        'pest-control': 'Pest Control',
        'irrigation': 'Irrigation',
        'painting': 'Painting',
        'mechanical': 'Mechanical',
        'refrigeration': 'Refrigeration',
        'security-systems': 'Security Systems',
        'landscaping': 'Landscaping',
        'kitchen-equipment': 'Kitchen Equipment',
        'water-treatment': 'Water Treatment',
        'pool-spa': 'Pool & Spa',
        'general-contractor': 'General'
      };
      return tradeMap[service.trade_slug] || 'General';
    }
    
    // Fallback to legacy category inference for backward compatibility
    const raw = (service.category || service.category_name || '').toString();
    if (raw) {
      const s = raw.toLowerCase();
      if (s.includes('hvac') || s.includes('ac') || s.includes('air')) return 'HVAC';
      if (s.includes('plumb')) return 'Plumbing';
      if (s.includes('elect')) return 'Electrical';
      if (s.includes('roof')) return 'Roofing';
      if (s.includes('security')) return 'Security Systems';
      if (s.includes('landscap')) return 'Landscaping';
    }
    
    const name = (service.service_name || service.name || '').toString().toLowerCase();
    if (/hvac|ac|air/.test(name)) return 'HVAC';
    if (/plumb/.test(name)) return 'Plumbing';
    if (/elect/.test(name)) return 'Electrical';
    return 'General';
  };

  // Transform services for booking provider (popup integration, carts, etc.)
  const bookingServices = businessServices.map(service => ({
    id: String(service.id || service.service_id),
    name: service.service_name || service.name,
    description: service.description || `Professional ${service.service_name || service.name} service`,
    price: service.base_price || 150,
    duration: service.estimated_duration || service.estimated_duration_minutes || 60,
    category: getTradeDisplayName(service),
    // Include new normalized fields
    trade_slug: service.trade_slug,
    service_type_code: service.service_type_code,
    is_emergency: service.is_emergency || false,
    is_bookable: service.is_bookable !== false // Default to true
  }));

  // Transform services for inline booking wizard (expects estimated_duration_minutes/base_price)
  const wizardServices = businessServices.map(service => ({
    id: String(service.id || service.service_id),
    name: service.service_name || service.name,
    category: getTradeDisplayName(service),
    description: service.description || '',
    estimated_duration_minutes: service.estimated_duration || service.estimated_duration_minutes || undefined,
    base_price: service.base_price || undefined,
    // Include new normalized fields for better categorization
    trade_slug: service.trade_slug,
    service_type_code: service.service_type_code,
    is_emergency: service.is_emergency || false,
    is_bookable: service.is_bookable !== false
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
