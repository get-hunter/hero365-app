/**
 * Booking Page - Client-only component for SSR compatibility
 * 
 * This page is fully client-side to avoid server/client hydration issues
 * with the booking wizard and interactive components
 */

'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import Header from '@/components/server/layout/header';
// Client components for header slots
import { SimpleCTAButton } from '@/components/client/interactive/cta-button';
import { SimpleCartIndicator } from '@/components/client/interactive/cart-indicator';
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

export default function BookingPage() {
  // Business data - in a real app this would come from props or context
  const businessData = {
    businessName: "Elite HVAC Services",
    city: "Denver",
    state: "CO",
    phone: "(555) 123-4567",
    supportHours: "24/7",
    primaryColor: "#3b82f6"
  };

  const serviceCategories = [
    {
      name: "Air Conditioning",
      services: [
        { name: "Heat Pump Installation", href: "/services/heat-pump-service" },
        { name: "Ductless Split System", href: "/services/ductless-split-system" },
        { name: "Air Conditioner Repair", href: "/services/ac-repair" },
        { name: "Duct Inspection", href: "/services/duct-inspection" }
      ]
    },
    {
      name: "Heating",
      services: [
        { name: "Furnace Installation", href: "/services/furnace-installation" },
        { name: "Heater Repair", href: "/services/furnace-repair" },
        { name: "Heating Installation", href: "/services/heating-installation" }
      ]
    },
    {
      name: "Electrical",
      services: [
        { name: "Panel Installation", href: "/services/panel-upgrades" },
        { name: "Electrical Repair", href: "/services/electrical-repair" },
        { name: "Lighting Installation", href: "/services/lighting-installation" }
      ]
    },
    {
      name: "Plumbing",
      services: [
        { name: "Water Heater Service", href: "/services/water-heater-service" },
        { name: "Plumbing Repair", href: "/services/plumbing-repair" },
        { name: "Drain Cleaning", href: "/services/drain-cleaning" }
      ]
    }
  ];

  const companyLinks = [
    { name: "About Us", href: "/about" },
    { name: "Service Area", href: "/service-area" },
    { name: "Why Choose Us", href: "/why-us" },
    { name: "Our Work", href: "/projects" },
    { name: "Customer Reviews", href: "/reviews" },
    { name: "Careers", href: "/careers" },
    { name: "Blog", href: "/blog" }
  ];

  // Mock services for the booking provider
  const mockServices = [
    {
      id: '1',
      name: 'HVAC Repair',
      description: 'Emergency HVAC repair service',
      price: 150,
      duration: 60,
      category: 'HVAC'
    },
    {
      id: '2', 
      name: 'AC Installation',
      description: 'New air conditioning installation',
      price: 3500,
      duration: 240,
      category: 'HVAC'
    }
  ];

  return (
    <Hero365BookingProvider
      businessId="550e8400-e29b-41d4-a716-446655440010"
      services={mockServices}
      companyName={businessData.businessName}
      companyPhone={businessData.phone}
      primaryColor={businessData.primaryColor}
    >
      <div className="min-h-screen bg-gray-50">
        <Header
          {...businessData}
          ctaSlot={<HeaderCTAButton />}
          cartSlot={<HeaderCartIndicator />}
        />
        
        {/* Mobile menu toggle - positioned absolutely */}
        <div className="lg:hidden fixed top-4 right-4 z-50">
          <MobileMenuToggle
            businessName={businessData.businessName}
            serviceCategories={serviceCategories}
            companyLinks={companyLinks}
          />
        </div>

        <main>
          <Hero365BookingWizard />
        </main>
      </div>
    </Hero365BookingProvider>
  );
}
