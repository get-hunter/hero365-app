import React from 'react';
import { loadTemplateData } from '../../../lib/data-loader';
import ProfessionalHero from '../../../components/professional/ProfessionalHero';
import ServicesGrid from '../../../components/professional/ServicesGrid';
import TrustRatingDisplay from '../../../components/professional/TrustRatingDisplay';
import CustomerReviews from '../../../components/professional/CustomerReviews';
import ContactSection from '../../../components/professional/ContactSection';
import ProfessionalFooter from '../../../components/professional/ProfessionalFooter';

export default async function ProfessionalTemplate() {
  // Load all template data from JSON artifacts
  const {
    business,
    serviceCategories,
    promos,
    ratings,
    awards,
    partnerships,
    testimonials,
    locations
  } = await loadTemplateData();

  return (
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
      <CustomerReviews testimonials={testimonials} />

      {/* Contact Section */}
      <ContactSection 
        business={business}
        locations={locations}
      />

      {/* Footer */}
      <ProfessionalFooter 
        business={business}
        serviceCategories={serviceCategories}
        locations={locations}
      />
    </main>
  );
}