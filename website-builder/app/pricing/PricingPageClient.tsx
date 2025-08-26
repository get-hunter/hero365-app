/**
 * Client-side Pricing Page Component
 * 
 * Handles all interactive functionality for the pricing page
 */

'use client';

import React from 'react';
import ServicePricingTable from '../../components/services/ServicePricingTable';
import MembershipPlansComparison from '../../components/membership/MembershipPlansComparison';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Phone, Calendar, Shield, Star, Award } from 'lucide-react';
import { ServicePricing, MembershipPlan } from '../../lib/types/membership';

interface PricingPageClientProps {
  servicePricing: Array<{
    category: string;
    services: ServicePricing[];
  }>;
  membershipPlans: MembershipPlan[];
}

export default function PricingPageClient({
  servicePricing,
  membershipPlans
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
        
        <MembershipPlansComparison
          plans={membershipPlans}
          onJoinNow={handleJoinMembership}
          showAnnualSavings={true}
        />
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

        {servicePricing.map((category) => (
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
        ))}
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
