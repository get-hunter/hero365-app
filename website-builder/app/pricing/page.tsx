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

export default function PricingPage() {
  const businessConfig = getBusinessConfig();
  
  // Use business config data
  const businessData = {
    businessName: businessConfig.defaultBusinessName,
    phone: businessConfig.defaultBusinessPhone,
    email: businessConfig.defaultBusinessEmail,
    serviceAreas: ['Austin'], // You can expand this from config if needed
    address: '123 Main St, Austin, TX'
  };

  return (
    <BookingWidgetProvider
      businessId={businessConfig.defaultBusinessId}
      companyName={businessData.businessName}
      companyPhone={businessData.phone}
      companyEmail={businessData.email}
      services={[]}
    >
      <div className="min-h-screen bg-white">
        {/* Elite Header - Same as main page */}
        <EliteHeader 
          businessName={businessData.businessName}
          city={businessData.serviceAreas[0] || 'Austin'}
          state={'TX'}
          phone={businessData.phone}
          supportHours={'24/7'}
        />

        {/* Pricing Page Content with hero section */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl font-bold mb-4">
              Transparent Pricing
            </h1>
            <div className="flex items-center justify-center gap-2 mb-6">
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <span className="text-xl font-medium">
                Our Policy: "NO satisfaction – NO charge"
              </span>
            </div>
            
            {/* Contact Info */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-white/90">
              <div className="flex items-center gap-2">
                <Phone className="h-5 w-5" />
                <span>Support 24/7: {businessData.phone}</span>
              </div>
              <div className="flex items-center gap-2">
                <Award className="h-5 w-5" />
                <span>15 Years Experience</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-400" />
                <span>4.9★ Customer Rating</span>
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

        {/* Professional Footer - Same as main page */}
        <ProfessionalFooter 
          business={{
            name: businessData.businessName,
            phone: businessData.phone,
            email: businessData.email,
            address: businessData.address,
            license_number: 'Licensed & Insured',
            website: undefined,
            service_areas: businessData.serviceAreas
          }}
          serviceCategories={[]}
          locations={[]}
        />
      </div>
    </BookingWidgetProvider>
  );
}
