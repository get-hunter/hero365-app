/**
 * Dynamic Professional Template - Homepage
 * 
 * Generates professional service website based on business profile and trade configuration
 */

'use client';

import React, { useMemo } from 'react';
import ProfessionalHero from '../components/professional/ProfessionalHero';
import ServicesGrid from '../components/professional/ServicesGrid';
import TrustRatingDisplay from '../components/professional/TrustRatingDisplay';
import CustomerReviews from '../components/professional/CustomerReviews';
import ContactSection from '../components/professional/ContactSection';
import ProfessionalFooter from '../components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '../components/booking/BookingWidgetProvider';
import { BookableService } from '../lib/types/booking';
import { createTemplateGenerator } from '../lib/services/template-generator';
import { austinEliteHVAC } from '../lib/data/sample-businesses';

export default function HomePage() {
  // Generate dynamic content based on business profile
  const generatedContent = useMemo(() => {
    const generator = createTemplateGenerator(austinEliteHVAC);
    return generator.generate();
  }, []);

  // Convert trade services to bookable services
  const bookableServices: BookableService[] = useMemo(() => {
    return generatedContent.services.categories.flatMap(category => 
      category.services.map(service => ({
        id: `${category.id}-${service.name.toLowerCase().replace(/\s+/g, '-')}`,
        business_id: "123e4567-e89b-12d3-a456-426614174000",
        name: service.name,
        category: category.name,
        description: service.description,
        is_bookable: true,
        requires_site_visit: true,
        estimated_duration_minutes: 90,
        min_duration_minutes: 60,
        max_duration_minutes: 120,
        base_price: category.starting_price || 149,
        price_type: "estimate" as const,
        required_skills: [],
        min_technicians: 1,
        max_technicians: 2,
        min_lead_time_hours: category.is_emergency ? 2 : 4,
        max_advance_days: 60,
        available_days: [1, 2, 3, 4, 5, 6, 7],
        available_times: { start: "07:00", end: "20:00" }
      }))
    );
  }, [generatedContent.services]);

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

    const promos = [
      {
        id: "1",
        title: "Winter Special",
        subtitle: "Save on heating maintenance",
        price_label: "$99",
        badge_text: "Limited Time",
        placement: "hero_banner",
        is_featured: true
      }
    ];

    const ratings = [
      { 
        id: "1", 
        platform: "Google", 
        rating: generatedContent.trust.reviews_summary.average_rating, 
        review_count: generatedContent.trust.reviews_summary.total_reviews, 
        is_featured: true 
      },
      { id: "2", platform: "Yelp", rating: 4.7, review_count: 89, is_featured: true }
    ];

    const testimonials = [
      {
        id: "1",
        customer_name: "Sarah Johnson",
        review_text: "Outstanding service! They fixed our AC on the hottest day of the year. The technician was professional, knowledgeable, and got us back up and running quickly. Highly recommend!",
        rating: 5,
        service_type: "AC Repair",
        is_featured: true
      },
      {
        id: "2",
        customer_name: "Mike Rodriguez",
        review_text: "Best HVAC company in Austin! They installed our new system and the difference is incredible. Our energy bills have dropped significantly and the house stays perfectly comfortable.",
        rating: 5,
        service_type: "HVAC Installation",
        is_featured: true
      },
      {
        id: "3",
        customer_name: "Jennifer Chen",
        review_text: "Emergency service at its finest. Called them at 11 PM when our heater stopped working and they had someone out within an hour. Fair pricing and excellent work.",
        rating: 5,
        service_type: "Emergency Heating Repair",
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
      promos,
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
      <main className="min-h-screen">
      {/* Hero Section */}
        <ProfessionalHero 
          business={componentData.business}
          ratings={componentData.ratings}
          promos={componentData.promos}
        />

        {/* Trust Ratings */}
        <TrustRatingDisplay ratings={componentData.ratings} />

        {/* Services Grid */}
        <ServicesGrid 
          serviceCategories={componentData.serviceCategories}
          businessName={componentData.business.name}
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
      </main>
    </BookingWidgetProvider>
  );
}