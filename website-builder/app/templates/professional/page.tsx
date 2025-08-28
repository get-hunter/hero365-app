/**
 * Professional Template - Main Page
 * 
 * Complete professional service website with integrated booking system
 */

'use client';

import React, { useEffect, useState } from 'react';
import ProfessionalHero from '../../../components/professional/ProfessionalHero';
import ServicesGrid from '../../../components/professional/ServicesGrid';
import TrustRatingDisplay from '../../../components/professional/TrustRatingDisplay';
import CustomerReviews from '../../../components/professional/CustomerReviews';
import ContactSection from '../../../components/professional/ContactSection';
import ProfessionalFooter from '../../../components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '../../../components/booking/BookingWidgetProvider';
import { BookableService } from '../../../lib/types/booking';

// Sample bookable services - in production this would come from API
const SAMPLE_SERVICES: BookableService[] = [
  {
    id: "hvac-inspection",
    business_id: "123e4567-e89b-12d3-a456-426614174000",
    name: "HVAC System Inspection",
    category: "HVAC",
    description: "Comprehensive inspection of your heating and cooling system including filters, ducts, and efficiency testing.",
    is_bookable: true,
    requires_site_visit: true,
    estimated_duration_minutes: 90,
    min_duration_minutes: 60,
    max_duration_minutes: 120,
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
    id: "emergency-repair",
    business_id: "123e4567-e89b-12d3-a456-426614174000",
    name: "Emergency HVAC Repair",
    category: "HVAC",
    description: "24/7 emergency repair service for heating and cooling system failures.",
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
  },
  {
    id: "maintenance",
    business_id: "123e4567-e89b-12d3-a456-426614174000",
    name: "Preventive Maintenance",
    category: "HVAC",
    description: "Seasonal maintenance to keep your HVAC system running efficiently.",
    is_bookable: true,
    requires_site_visit: true,
    estimated_duration_minutes: 60,
    base_price: 99.99,
    price_type: "fixed" as const,
    required_skills: [],
    min_technicians: 1,
    max_technicians: 1,
    min_lead_time_hours: 24,
    max_advance_days: 120,
    available_days: [1, 2, 3, 4, 5],
    available_times: { start: "08:00", end: "17:00" }
  }
];

// Sample data for client-side rendering
const SAMPLE_DATA = {
  business: {
    id: "123e4567-e89b-12d3-a456-426614174000",
    name: "Professional HVAC Services",
    business_email: "info@professionalhvac.com",
    phone_number: "(555) 123-4567",
    service_areas: ["Downtown", "Midtown", "Suburbs"],
    description: "Professional HVAC services with 20+ years of experience",
    website: "https://professionalhvac.com",
    trades: ["HVAC"],
    seo_keywords: ["hvac", "heating", "cooling", "air conditioning"]
  },
  serviceCategories: [
    {
      id: "hvac",
      name: "HVAC Services",
      description: "Complete heating, ventilation, and air conditioning services",
      services_count: 8,
      starting_price: 99,
      is_popular: true,
      slug: "hvac-services",
      is_featured: true,
      sort_order: 1
    },
    {
      id: "emergency",
      name: "Emergency Repair",
      description: "24/7 emergency HVAC repair services",
      services_count: 5,
      starting_price: 199,
      is_popular: false,
      slug: "emergency-repair",
      is_featured: false,
      sort_order: 2
    }
  ],
  promos: [
    {
      id: "1",
      title: "Winter Special",
      subtitle: "Save on heating maintenance",
      price_label: "$99",
      badge_text: "Limited Time",
      placement: "hero_banner",
      is_featured: true,
      offer_type: "discount",
      cta_text: "Book Now",
      priority: 1
    }
  ],
  ratings: [
    { id: "1", platform: "Google", display_name: "Google Reviews", rating: 4.8, review_count: 150, is_featured: true },
    { id: "2", platform: "Yelp", display_name: "Yelp Reviews", rating: 4.7, review_count: 89, is_featured: true }
  ],
  awards: [
    {
      id: "1",
      title: "Best HVAC Service 2024",
      issuer: "Local Business Awards",
      year: 2024
    }
  ],
  partnerships: [
    {
      id: "1",
      name: "Carrier",
      type: "Authorized Dealer"
    }
  ],
  testimonials: [
    {
      id: "1",
      customer_name: "John Smith",
      review_text: "Excellent service! Professional and timely.",
      rating: 5,
      service_type: "HVAC Repair",
      is_featured: true
    },
    {
      id: "2",
      customer_name: "Sarah Johnson",
      review_text: "Quick response time and fair pricing. Highly recommend!",
      rating: 5,
      service_type: "Emergency Repair",
      is_featured: true
    }
  ],
  locations: [
    {
      id: "1",
      name: "Main Office",
      address: "123 Main St, City, State 12345",
      phone: "(555) 123-4567",
      is_primary: true
    }
  ]
};

export default function ProfessionalTemplate() {
  const [isLoaded, setIsLoaded] = useState(false);
  
  useEffect(() => {
    setIsLoaded(true);
  }, []);

  // Don't render until client-side hydration is complete
  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Professional Services...</p>
        </div>
      </div>
    );
  }
  
  const {
    business,
    serviceCategories,
    promos,
    ratings,
    awards,
    partnerships,
    testimonials,
    locations
  } = SAMPLE_DATA;

  return (
    <BookingWidgetProvider
      businessId="123e4567-e89b-12d3-a456-426614174000"
      services={SAMPLE_SERVICES}
      companyName={business.name}
      companyPhone={business.phone_number}
      companyEmail={business.business_email}
      primaryColor="#3b82f6"
      showLauncher={true}
    >
      <main className="min-h-screen">
        {/* Hero Section */}
        <ProfessionalHero 
          business={business}
          ratings={ratings}
          promos={promos}
        />

        {/* Trust Ratings */}
        <TrustRatingDisplay ratings={ratings} />

        {/* Services Grid */}
        <ServicesGrid 
          serviceCategories={serviceCategories}
          businessName={business.name}
        />

        {/* Customer Reviews */}
        <CustomerReviews testimonials={testimonials.map(t => ({
          ...t,
          quote: t.review_text,
          is_verified: true
        }))} />

        {/* Contact Section */}
        <ContactSection 
          business={business}
          locations={[]}
        />

        {/* Footer */}
        <ProfessionalFooter 
          business={business}
          serviceCategories={serviceCategories}
          locations={[]}
        />
      </main>
    </BookingWidgetProvider>
  );
}