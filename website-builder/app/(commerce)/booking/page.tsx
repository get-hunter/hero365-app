/**
 * Booking Page - Server component with client booking wizard
 * 
 * Uses host-based resolution for multi-tenant support
 */

import React from 'react';
import Hero365Header from '@/components/server/layout/Hero365Header';
import Hero365Footer from '@/components/shared/Hero365Footer';
import { Hero365BookingProvider } from '@/components/client/commerce/booking/Hero365BookingProvider';
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver';
import { getDefaultHeaders } from '@/lib/shared/config/api-config';
import { getRuntimeConfig } from '@/lib/server/runtime-config';
import { notFound } from 'next/navigation';
import BookingPageClient from '@/app/(commerce)/booking/BookingPageClient';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

async function loadBusinessData(businessId: string) {
  try {
    console.log('🔄 [BOOKING] Loading business data for:', businessId);
    
    const config = await getRuntimeConfig();
    const backendUrl = config.apiUrl;
    const headers = getDefaultHeaders();

    const [profileResponse, servicesResponse, locationsResponse] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/contractors/profile/${businessId}`, {
        headers,
        next: { revalidate: 3600, tags: ['profile', businessId] }
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/services/${businessId}`, {
        headers,
        next: { revalidate: 3600, tags: ['services', businessId] }
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/${businessId}/locations`, {
        headers,
        next: { revalidate: 3600, tags: ['locations', businessId] }
      })
    ]);

    let profile = null;
    let services = [];
    let locations = [];

    if (profileResponse.ok) {
      profile = await profileResponse.json();
      console.log('✅ [BOOKING] Profile loaded:', profile.business_name);
    } else {
      console.error('❌ [BOOKING] Failed to load profile:', profileResponse.status);
    }

    if (servicesResponse.ok) {
      services = await servicesResponse.json();
      console.log('✅ [BOOKING] Services loaded:', services.length, 'services');
    } else {
      console.error('❌ [BOOKING] Failed to load services:', servicesResponse.status);
    }

    if (locationsResponse.ok) {
      locations = await locationsResponse.json();
      console.log('✅ [BOOKING] Locations loaded:', locations.length, 'locations');
    } else {
      console.error('❌ [BOOKING] Failed to load locations:', locationsResponse.status);
    }

    return { profile, services, locations };
  } catch (error) {
    console.error('❌ [BOOKING] Error loading business data:', error);
    return { profile: null, services: [], locations: [] };
  }
}

export default async function BookingPage() {
  // Get business ID from host for multi-tenant support
  const resolution = await getBusinessIdFromHost();
  const businessId = resolution.businessId;

  const { profile, services, locations } = await loadBusinessData(businessId);

  if (!profile) {
    console.error('❌ [BOOKING] No profile data found for business:', businessId);
    notFound();
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Hero365Header
        businessProfile={profile}
        showCTA={true}
        showCart={true}
      />

      <BookingPageClient 
        businessProfile={profile}
        businessServices={services}
        businessId={businessId}
      />

      <Hero365Footer
        business={profile}
        services={services}
        locations={locations}
        showEmergencyBanner={true}
      />
    </div>
  );
}