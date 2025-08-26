/**
 * Elite Professional Template - Homepage
 * 
 * Professional service website with elite-level design and functionality
 */

'use client';

import React, { useMemo } from 'react';
import EliteHeader from '../components/layout/EliteHeader';
import EliteHero from '../components/hero/EliteHero';
import EliteServicesGrid from '../components/services/EliteServicesGrid';
import TrustRatingDisplay from '../components/professional/TrustRatingDisplay';
import CustomerReviews from '../components/professional/CustomerReviews';
import ContactSection from '../components/professional/ContactSection';
import ProfessionalFooter from '../components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '../components/booking/BookingWidgetProvider';
import { BookableService } from '../lib/types/booking';
import { createTemplateGenerator } from '../lib/services/template-generator';
import { austinEliteHVAC } from '../lib/data/sample-businesses';
import { samplePromotions } from '../lib/data/sample-promotions';

export default function HomePage() {
  // Generate dynamic content based on business profile
  const generatedContent = useMemo(() => {
    const generator = createTemplateGenerator(austinEliteHVAC);
    return generator.generate();
  }, []);

  // Convert trade services to bookable services
  const bookableServices: BookableService[] = useMemo(() => {
    return [
      {
        id: "hvac-inspection",
        business_id: "123e4567-e89b-12d3-a456-426614174000",
        name: "HVAC System Inspection",
        category: "HVAC",
        description: "Comprehensive inspection of your heating and cooling system",
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
        id: "emergency-service",
        business_id: "123e4567-e89b-12d3-a456-426614174000",
        name: "Emergency HVAC Repair",
        category: "Emergency",
        description: "24/7 emergency repair service for system failures",
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
        id: "hvac-installation",
        business_id: "123e4567-e89b-12d3-a456-426614174000",
        name: "HVAC Installation",
        category: "Installation",
        description: "Complete HVAC system installation and replacement",
        is_bookable: true,
        requires_site_visit: true,
        estimated_duration_minutes: 480,
        price_type: "estimate" as const,
        required_skills: [],
        min_technicians: 2,
        max_technicians: 3,
        min_lead_time_hours: 48,
        max_advance_days: 90,
        available_days: [1, 2, 3, 4, 5],
        available_times: { start: "07:00", end: "17:00" }
      }
    ];
  }, []);

  // Elite promotions
  const promotions = [
    {
      id: "rebate-2025",
      title: "Enjoy Up to $1500 Rebate",
      subtitle: "Your friends at Austin Elite HVAC offer incredible rebates for your new efficient equipment. Reach out today to learn more!",
      discount: "Up to $1500",
      badge: "Limited Time",
      type: "rebate" as const,
      ctaText: "More Details"
    },
    {
      id: "thermostat-offer",
      title: "Just $50 for a Thermostat",
      subtitle: "Incredible offer from your favorite contractor—smart thermostats for $50 only.",
      discount: "$50",
      badge: "Hot Offer",
      type: "seasonal" as const,
      ctaText: "Details Here"
    },
    {
      id: "warranty-offer",
      title: "Extended Warranty Up to 12 Years",
      subtitle: "Austin Elite HVAC offers up to 12 years of labor warranty and up to 12 years of parts warranty for your residential HVAC installations",
      type: "membership" as const,
      ctaText: "More Details"
    }
  ];

  // Convert generated content to component props format
  const componentData = useMemo(() => {
    const business = {
      id: "123e4567-e89b-12d3-a456-426614174000",
      name: generatedContent.business.name,
      phone: generatedContent.business.phone,
      email: generatedContent.business.email,
      phone_number: generatedContent.business.phone,
      service_areas: generatedContent.business.service_areas,
      description: generatedContent.about.company_story,
      primary_trade: generatedContent.business.trade,
      trades: generatedContent.booking.default_services,
      logo_url: generatedContent.business.logo_url,
      website_url: generatedContent.business.website_url,
      social_media: generatedContent.business.social_media || {}
    };

    const serviceCategories = generatedContent.services.categories.map(category => ({
      id: category.id,
      name: category.name,
      description: category.description,
      services_count: category.services.length,
      starting_price: category.starting_price,
      is_popular: category.is_popular || false
    }));

    const ratings = [
      { 
        id: "1", 
        platform: "Google", 
        rating: 4.9, 
        review_count: 797, 
        is_featured: true 
      },
      { id: "2", platform: "Yelp", rating: 4.8, review_count: 1067, is_featured: true },
      { id: "3", platform: "Facebook", rating: 4.9, review_count: 427, is_featured: true }
    ];

    const testimonials = [
      {
        id: "1",
        customer_name: "Deena D.",
        review_text: "Very nice, knowledgeable, and helpful technician. Provided the options and associated costs. Would use this company again.",
        rating: 5,
        service_type: "HVAC Service",
        is_featured: true
      },
      {
        id: "2",
        customer_name: "Ron B.",
        review_text: "We chose Austin Elite to do the HVAC portion of our home remodel and we're very happy with their work! They installed a full Mitsubishi Mini-split heat pump system all throughout our house in 6 rooms. It was a massive job and they did the work relatively quickly and efficiently.",
        rating: 5,
        service_type: "HVAC Installation",
        is_featured: true
      },
      {
        id: "3",
        customer_name: "Pablo L. D.",
        review_text: "Great service. They respond really fast and did a great job fixing my thermostat issues.",
        rating: 5,
        service_type: "Thermostat Repair",
        is_featured: true
      },
      {
        id: "4",
        customer_name: "Manu B.",
        review_text: "We got our duct work completely replaced in our 50 yr old home. They recommended the work, other companies didn't do this much due diligence. Honest people and very competitive if not best quote I got.",
        rating: 5,
        service_type: "Ductwork Replacement",
        is_featured: true
      }
    ];

    const locations = [
      {
        id: "1",
        name: "Main Office",
        address: generatedContent.business.formatted_address,
        phone: generatedContent.business.phone,
        is_primary: true
      }
    ];

    return {
      business,
      serviceCategories,
      ratings,
      testimonials,
      locations
    };
  }, [generatedContent]);

  return (
    <BookingWidgetProvider
      businessId="123e4567-e89b-12d3-a456-426614174000"
      services={bookableServices}
      companyName={generatedContent.business.name}
      companyPhone={generatedContent.business.phone}
      companyEmail={generatedContent.business.email}
      primaryColor={generatedContent.colors.primary}
      showLauncher={true}
    >
      <div className="min-h-screen">
        {/* Elite Header */}
        <EliteHeader
          businessName={generatedContent.business.name}
          city={generatedContent.business.city}
          state={generatedContent.business.state}
          phone={generatedContent.business.phone}
          supportHours="24/7"
          primaryColor={generatedContent.colors.primary}
        />

        {/* Elite Hero Section */}
                <EliteHero
          businessName={generatedContent.business.name}
          headline={generatedContent.hero.headline}
          subheadline="24/7 Emergency Service • Same-Day Repairs • 100% Satisfaction Guaranteed • NATE Certified Technicians"
          city={generatedContent.business.city}
          phone={generatedContent.business.phone}
          averageRating={4.9}
          totalReviews={2291}
          promotions={samplePromotions}
          currentTrade="HVAC"
          emergencyMessage="HVAC Emergency? We're Available 24/7 - No Overtime Charges!"
          primaryColor={generatedContent.colors.primary}
        />

        {/* Trust Ratings */}
        <TrustRatingDisplay ratings={componentData.ratings} />

        {/* Elite Services Grid */}
        <EliteServicesGrid 
          businessName={componentData.business.name}
          city={generatedContent.business.city}
          phone={componentData.business.phone}
          primaryColor={generatedContent.colors.primary}
        />

        {/* Customer Reviews */}
        <CustomerReviews testimonials={componentData.testimonials} />

        {/* Contact Section */}
        <ContactSection 
          business={componentData.business}
          locations={componentData.locations}
        />

        {/* Footer */}
        <ProfessionalFooter 
          business={componentData.business}
          serviceCategories={componentData.serviceCategories}
          locations={componentData.locations}
        />
      </div>
    </BookingWidgetProvider>
  );
}