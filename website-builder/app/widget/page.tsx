/**
 * Embeddable Widget Page
 * 
 * Standalone page for embedding the booking widget in external websites
 */

'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import EmbeddableBookingWidget from '@/components/client/commerce/booking/Hero365BookingWidget';
import { BookableService } from '@/lib/shared/types/booking';

// Sample services - in production this would come from API based on businessId
const getSampleServices = (businessId: string): BookableService[] => [
  {
    id: "service-1",
    business_id: businessId,
    name: "HVAC System Inspection",
    category: "HVAC",
    description: "Comprehensive inspection of your heating and cooling system.",
    is_bookable: true,
    requires_site_visit: true,
    estimated_duration_minutes: 90,
    base_price: 149.99,
    price_type: "fixed" as const,
    required_skills: [],
    min_technicians: 1,
    max_technicians: 1,
    min_lead_time_hours: 4,
    max_advance_days: 60,
    available_days: [1, 2, 3, 4, 5],
    available_times: { start: "08:00", end: "17:00" }
  },
  {
    id: "service-2",
    business_id: businessId,
    name: "Emergency HVAC Repair",
    category: "HVAC",
    description: "24/7 emergency repair service for system failures.",
    is_bookable: true,
    requires_site_visit: true,
    estimated_duration_minutes: 120,
    base_price: 299.99,
    price_type: "estimate" as const,
    required_skills: [],
    min_technicians: 1,
    max_technicians: 2,
    min_lead_time_hours: 2,
    max_advance_days: 30,
    available_days: [1, 2, 3, 4, 5, 6, 7],
    available_times: { start: "06:00", end: "22:00" }
  }
];

function WidgetContent() {
  const searchParams = useSearchParams();
  const [config, setConfig] = useState({
    businessId: '',
    mode: 'inline' as 'popup' | 'inline' | 'sidebar',
    theme: 'light' as 'light' | 'dark' | 'auto',
    primaryColor: '#3b82f6',
    companyName: 'Professional Services',
    companyLogo: '',
    companyPhone: '',
    companyEmail: '',
    showHeader: true,
    showFooter: true,
  });

  useEffect(() => {
    // Parse URL parameters
    const businessId = searchParams.get('businessId') || searchParams.get('business_id') || '';
    const mode = (searchParams.get('mode') as any) || 'inline';
    const theme = (searchParams.get('theme') as any) || 'light';
    const primaryColor = searchParams.get('primaryColor') || searchParams.get('primary_color') || '#3b82f6';
    const companyName = searchParams.get('companyName') || searchParams.get('company_name') || 'Professional Services';
    const companyLogo = searchParams.get('companyLogo') || searchParams.get('company_logo') || '';
    const companyPhone = searchParams.get('companyPhone') || searchParams.get('company_phone') || '';
    const companyEmail = searchParams.get('companyEmail') || searchParams.get('company_email') || '';
    const showHeader = searchParams.get('showHeader') !== 'false';
    const showFooter = searchParams.get('showFooter') !== 'false';

    setConfig({
      businessId,
      mode,
      theme,
      primaryColor,
      companyName,
      companyLogo,
      companyPhone,
      companyEmail,
      showHeader,
      showFooter,
    });

    // Apply theme to document
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }

    // Set CSS custom properties for theming
    document.documentElement.style.setProperty('--primary-color', primaryColor);
  }, [searchParams]);

  const handleBookingComplete = (booking: any) => {
    console.log('Booking completed:', booking);
    
    // Send analytics event
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'booking_completed', {
        business_id: config.businessId,
        service_id: booking.service_id,
        value: booking.quoted_price || 0,
      });
    }
  };

  const handleBookingError = (error: string) => {
    console.error('Booking error:', error);
    
    // Send analytics event
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'booking_error', {
        business_id: config.businessId,
        error_message: error,
      });
    }
  };

  if (!config.businessId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Hero365 Booking Widget
          </h1>
          <p className="text-gray-600 mb-4">
            This widget requires a business ID parameter.
          </p>
          <p className="text-sm text-gray-500">
            Example: ?businessId=your-business-id
          </p>
        </div>
      </div>
    );
  }

  const services = getSampleServices(config.businessId);

  return (
    <div className={`min-h-screen ${config.theme === 'dark' ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
      <Hero365BookingWidget
        businessId={config.businessId}
        services={services}
        theme={config.theme}
        primaryColor={config.primaryColor}
        companyName={config.companyName}
        companyLogo={config.companyLogo}
        companyPhone={config.companyPhone}
        companyEmail={config.companyEmail}
        mode={config.mode}
        showHeader={config.showHeader}
        showFooter={config.showFooter}
        allowMinimize={config.mode === 'popup'}
        onBookingComplete={handleBookingComplete}
        onBookingError={handleBookingError}
        className={config.mode === 'inline' ? 'container mx-auto py-8' : ''}
      />
    </div>
  );
}

export default function WidgetPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading booking widget...</p>
        </div>
      </div>
    }>
      <WidgetContent />
    </Suspense>
  );
}
