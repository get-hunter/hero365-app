/**
 * Booking Page - Server component with client booking wizard
 * 
 * Uses host-based resolution for multi-tenant support
 */

import React from 'react';
import Header from '@/components/server/layout/header';
import { Hero365BookingProvider } from '@/components/client/commerce/booking/Hero365BookingProvider';
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver';
import { getBackendUrl, getDefaultHeaders } from '@/lib/shared/config/api-config';
import { notFound } from 'next/navigation';
import { BookingPageClient } from './BookingPageClient';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

async function loadBusinessData(businessId: string) {
  try {
    console.log('🔄 [BOOKING] Loading business data for:', businessId);
    
    const backendUrl = getBackendUrl();
    const headers = getDefaultHeaders();

    const [profileResponse, servicesResponse] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/contractors/profile/${businessId}`, {
        headers,
        next: { revalidate: 3600, tags: ['profile', businessId] }
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/services/${businessId}`, {
        headers,
        next: { revalidate: 3600, tags: ['services', businessId] }
      })
    ]);

    let profile = null;
    let services = [];

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

    return { profile, services };
  } catch (error) {
    console.error('❌ [BOOKING] Error loading business data:', error);
    return { profile: null, services: [] };
  }
}

export default async function BookingPage() {
  // Get business ID from host for multi-tenant support
  const resolution = await getBusinessIdFromHost();
  const businessId = resolution.businessId;

  const { profile, services } = await loadBusinessData(businessId);

  if (!profile) {
    console.error('❌ [BOOKING] No profile data found for business:', businessId);
    notFound();
  }

  return (
    <BookingPageClient 
      businessProfile={profile}
      businessServices={services}
      businessId={businessId}
    />
  );
}