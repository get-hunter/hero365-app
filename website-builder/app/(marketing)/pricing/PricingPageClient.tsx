/**
 * Client-side Pricing Page Component
 * 
 * Handles all interactive functionality for the pricing page
 */

'use client';

import React from 'react';
import Hero365ServicePricingTable from '../../../components/services/Hero365ServicePricingTable';
import Hero365MembershipPlansComparison from '../../../components/commerce/membership/Hero365MembershipPlansComparison';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Phone, Calendar, Shield, Star, Award } from 'lucide-react';
import { ServicePricing, MembershipPlan } from '../../../lib/types/membership';

interface PricingPageClientProps {
  servicePricing: Array<{
    category: string;
    services: ServicePricing[];
  }>;
  membershipPlans: MembershipPlan[];
  hasRealData?: boolean;
}

export default function PricingPageClient({
  servicePricing,
  membershipPlans,
  hasRealData = false
}: PricingPageClientProps) {
  
  const handleServiceSelect = (service: ServicePricing) => {
    // Implement service selection logic - could redirect to service page
    console.log('Service selected:', service.service_name);
    // Example: router.push(`/services/${service.id}`)
  };

  const handleBookNow = (service: ServicePricing) => {
    // Implement booking logic - could open booking modal or redirect
    console.log('Booking service:', service.service_name);
    // Example: open booking widget with pre-selected service
  };

  const handleJoinMembership = (plan: MembershipPlan) => {
    // Implement membership signup logic - could redirect to signup flow
    console.log('Joining plan:', plan.name);
    // Example: router.push(`/membership/signup?plan=${plan.id}`)
  };

  const handleCallClick = () => {
    // Handle phone call
    window.open('tel:(408)898-1576');
  };

  const handleBookingClick = () => {
    // Handle general booking - could open booking widget
    console.log('Opening booking widget');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      
      {/* Data Status Alert */}
      {!hasRealData && (
        <div className="mb-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="h-5 w-5 text-yellow-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.664-.833-2.464 0L5.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <div>
              <h4 className="font-medium text-yellow-800">Database Connection Required</h4>
              <p className="text-sm text-yellow-700 mt-1">
                Membership plans and pricing data will be loaded from the database once the backend is connected.
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Membership Plans Section */}
      <section className="mb-16">
        <div className="text-center mb-12">
          <Badge className="bg-blue-100 text-blue-800 text-sm px-4 py-2 mb-4">
            Lower Prices with Membership
          </Badge>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Membership Plans
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Save money and get priority service with our comprehensive membership plans. 
            Perfect for homeowners and businesses who want peace of mind and exclusive benefits.
          </p>
        </div>
        
        {membershipPlans.length > 0 ? (
          <MembershipPlansComparison
            plans={membershipPlans}
            onJoinNow={handleJoinMembership}
            showAnnualSavings={true}
          />
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <div className="text-gray-500">
              <svg className="h-16 w-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Membership Plans Coming Soon</h3>
              <p className="text-gray-600">Membership plans will be displayed here once configured in the database.</p>
            </div>
          </div>
        )}
      </section>

      {/* Service Pricing Tables */}
      <section className="space-y-12">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Service Pricing
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Transparent, upfront pricing for all our professional services. 
            Members save up to 25% on all services with additional benefits.
          </p>
        </div>

        {servicePricing.length > 0 ? (
          servicePricing.map((category) => (
            <div key={category.category} className="mb-12">
              <ServicePricingTable
                services={category.services}
                category={category.category}
                showMemberPricing={true}
                selectedMembershipType="residential"
                onServiceSelect={handleServiceSelect}
                onBookNow={handleBookNow}
              />
            </div>
          ))
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <div className="text-gray-500">
              <svg className="h-16 w-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Service Pricing Coming Soon</h3>
              <p className="text-gray-600">Detailed service pricing will be displayed here once configured in the database.</p>
            </div>
          </div>
        )}
      </section>

      {/* Additional Services Information */}
      <section className="mt-16 bg-white rounded-lg shadow-lg p-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">
          Additional Information
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Warranty Information */}
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
              <Shield className="h-5 w-5 text-blue-600 mr-2" />
              Warranty Coverage
            </h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Up to 12 Years of HVAC Labor Warranty</li>
              <li>• Extended warranty options available</li>
              <li>• All work guaranteed</li>
              <li>• Parts and labor coverage</li>
            </ul>
          </div>

          {/* Service Features */}
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
              <Calendar className="h-5 w-5 text-green-600 mr-2" />
              Service Features
            </h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Same-day service available</li>
              <li>• Emergency response 24/7</li>
              <li>• Licensed and insured technicians</li>
              <li>• Upfront transparent pricing</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}
