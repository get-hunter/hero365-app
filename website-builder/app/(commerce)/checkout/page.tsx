import { Suspense } from 'react';
import { getBusinessConfig, getDefaultHeaders } from '@/lib/shared/config/api-config';
import { getRuntimeConfig } from '@/lib/server/runtime-config';
import { CheckoutPageClient } from './CheckoutPageClient';
import Header from '@/components/server/layout/header';
import ClientAppProviders from '@/components/client/providers/ClientAppProviders';
import Hero365BusinessFooter from '@/components/client/business/Hero365BusinessFooter';
import { Hero365BookingProvider } from '@/components/client/commerce/booking/Hero365BookingProvider';
import { CartProvider } from '@/lib/client/contexts/CartContext';

// Configure for Edge Runtime (required for Cloudflare Pages)
// Note: Using Node.js runtime for OpenNext compatibility
export const dynamic = 'force-dynamic'
export const runtime = 'nodejs'
export const revalidate = 0

async function loadBusinessProfile(businessId: string) {
  try {
    // Use runtime configuration for backend URL
    const config = await getRuntimeConfig();
    const backendUrl = config.apiUrl;
      
    console.log('🔧 [CHECKOUT] Loading business profile:', { 
      businessId, 
      backendUrl, 
      nodeEnv: process.env.NODE_ENV 
    });
      
    const response = await fetch(`${backendUrl}/api/v1/public/contractors/profile/${businessId}`, {
      headers: getDefaultHeaders(),
      next: { revalidate: 3600, tags: ['profile', businessId] } // 1 hour ISR
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
      backendUrl: (await getRuntimeConfig()).apiUrl
    });
    return null;
  }
}

export default async function CheckoutPage() {
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.defaultBusinessId;
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
    <div className="min-h-screen bg-gray-50">
      <Header 
        businessName={profile.business_name}
        city="Austin"
        state="TX"
        phone={profile.phone}
        supportHours="24/7"
      />
      <ClientAppProviders 
        businessId={businessId} 
        services={[]}
        companyName={profile.business_name}
        companyPhone={profile.phone}
        companyEmail={profile.email}
      >
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
      </ClientAppProviders>
      <Hero365BusinessFooter 
        business={profile} 
        serviceCategories={[]} 
        locations={[]} 
      />
    </div>
  );
}
