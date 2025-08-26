/**
 * Professional Pricing Page (Server Component)
 * 
 * Comprehensive pricing display inspired by elite service companies
 * Features service pricing tables and membership plans
 */

import React from 'react';
import { Metadata } from 'next';
import { Phone, Star, Award } from 'lucide-react';
import EliteHeader from '../../components/layout/EliteHeader';
import ProfessionalFooter from '../../components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '../../components/booking/BookingWidgetProvider';
import PricingPageClient from './PricingPageClient';
import { getBusinessConfig } from '../../lib/config/api-config';

// Import data
import servicePricingData from '../../lib/data/service-pricing.json';
import membershipPlansData from '../../lib/data/membership-plans.json';
import { ServicePricing, MembershipPlan } from '../../lib/types/membership';

export const metadata: Metadata = {
  title: 'Prices - Professional Service Pricing & Membership Plans',
  description: 'Transparent pricing for all our professional services. Join our membership program for exclusive discounts and priority service.',
};

// Convert JSON data to typed objects
const servicePricing = servicePricingData as Array<{
  category: string;
  services: ServicePricing[];
}>;

const membershipPlans = membershipPlansData as MembershipPlan[];

async function loadBusinessData(businessId: string) {
  try {
    console.log('🔄 [PRICING] Loading business data for:', businessId);
    console.log('🔄 [PRICING] Environment:', process.env.NODE_ENV);
    
    // Make direct API calls to the backend (server-to-server)
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    console.log('🔄 [PRICING] Backend URL:', backendUrl);
    
    const [profileResponse, servicesResponse] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/professional/profile/${businessId}`, {
        headers: { 'Content-Type': 'application/json' }
      }),
      fetch(`${backendUrl}/api/v1/public/professional/services/${businessId}`, {
        headers: { 'Content-Type': 'application/json' }
      })
    ]);
    
    let profile = null;
    let services = [];
    
    if (profileResponse.ok) {
      profile = await profileResponse.json();
      console.log('✅ [PRICING] Profile loaded:', profile.business_name);
    }
    
    if (servicesResponse.ok) {
      services = await servicesResponse.json();
      console.log('✅ [PRICING] Services loaded:', services.length, 'items');
    }
    
    return { profile, services };
  } catch (error) {
    console.error('⚠️ [PRICING] Failed to load business data:', error);
    return { profile: null, services: [] };
  }
}

export default async function PricingPage() {
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.defaultBusinessId;
  
  // Load business data server-side
  const { profile: serverProfile, services: serverServices } = await loadBusinessData(businessId);
  
  // Use server data if available, otherwise fallback
  const profile = serverProfile || {
    business_id: businessConfig.defaultBusinessId,
    business_name: businessConfig.defaultBusinessName,
    trade_type: 'hvac',
    description: 'Premier professional services for homes and businesses.',
    phone: businessConfig.defaultBusinessPhone,
    email: businessConfig.defaultBusinessEmail,
    address: '123 Main St',
    website: 'https://www.example.com',
    service_areas: ['Local Area'],
    emergency_service: true,
    years_in_business: 10,
    license_number: 'Licensed & Insured',
    insurance_verified: true,
    average_rating: 4.8,
    total_reviews: 150,
    certifications: []
  };
  
  const services = serverServices || [];
  const error = serverProfile ? null : 'Using fallback data - backend not available';

  // Generate dynamic content based on real business profile
  const businessData = profile ? {
    businessName: profile.business_name,
    phone: profile.phone,
    email: profile.email,
    address: profile.address,
    serviceAreas: profile.service_areas || ['Local Area'],
    emergencyService: profile.emergency_service,
    yearsInBusiness: profile.years_in_business,
    licenseNumber: profile.license_number,
    insuranceVerified: profile.insurance_verified,
    averageRating: profile.average_rating,
    totalReviews: profile.total_reviews,
    certifications: profile.certifications || []
  } : null;

  // Fallback business data if no profile loaded
  const fallbackBusinessData = {
    businessName: businessConfig.defaultBusinessName,
    phone: businessConfig.defaultBusinessPhone,
    email: businessConfig.defaultBusinessEmail,
    serviceAreas: ['Austin'],
    address: '123 Main St, Austin, TX',
    emergencyService: true,
    yearsInBusiness: 10,
    licenseNumber: 'Licensed & Insured',
    insuranceVerified: true,
    averageRating: 4.8,
    totalReviews: 150,
    certifications: ['Licensed Professional', 'Insured']
  };

  const finalBusinessData = businessData || fallbackBusinessData;

  return (
    <BookingWidgetProvider
      businessId={businessId}
      companyName={finalBusinessData.businessName}
      companyPhone={finalBusinessData.phone}
      companyEmail={finalBusinessData.email}
      services={[]}
    >
      <div className="min-h-screen bg-white">
        {/* Elite Header - Same as main page with real data */}
        <EliteHeader 
          businessName={finalBusinessData.businessName}
          city={finalBusinessData.serviceAreas[0] || 'Austin'}
          state={'TX'}
          phone={finalBusinessData.phone}
          supportHours={'24/7'}
        />

        {/* Pricing Page Content with hero section using real data */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl font-bold mb-4">
              {finalBusinessData.businessName} Pricing
            </h1>
            <div className="flex items-center justify-center gap-2 mb-6">
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <span className="text-xl font-medium">
                Our Policy: "NO satisfaction – NO charge"
              </span>
            </div>
            
            {/* Contact Info with real data */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-white/90">
              <div className="flex items-center gap-2">
                <Phone className="h-5 w-5" />
                <span>Support 24/7: {finalBusinessData.phone}</span>
              </div>
              <div className="flex items-center gap-2">
                <Award className="h-5 w-5" />
                <span>{finalBusinessData.yearsInBusiness} Years Experience</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-400" />
                <span>{finalBusinessData.averageRating}★ {finalBusinessData.totalReviews} Reviews</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main content with gray background like main page */}
        <div className="bg-gray-50">
          <PricingPageClient 
            servicePricing={servicePricing}
            membershipPlans={membershipPlans}
          />
        </div>

        {/* Professional Footer - Same as main page with real data */}
        <ProfessionalFooter 
          business={{
            name: finalBusinessData.businessName,
            phone: finalBusinessData.phone,
            email: finalBusinessData.email,
            address: finalBusinessData.address,
            license_number: finalBusinessData.licenseNumber,
            website: undefined,
            service_areas: finalBusinessData.serviceAreas
          }}
          serviceCategories={[]}
          locations={[]}
        />

        {/* Error message for development */}
        {error && (
          <div className="fixed bottom-4 right-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded shadow-lg max-w-sm z-50">
            <strong className="font-bold">Development Notice:</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
        )}
      </div>
    </BookingWidgetProvider>
  );
}
