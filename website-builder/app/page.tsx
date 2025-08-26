/**
 * Professional Business Website - Homepage
 * 
 * Main business website that loads real business data from the Hero365 backend
 * Configured with business ID via environment variables during deployment
 */

import React from 'react';
import EliteHeader from '../components/layout/EliteHeader';
import EliteHero from '../components/hero/EliteHero';
import EliteServicesGrid from '../components/services/EliteServicesGrid';
import TrustRatingDisplay from '../components/professional/TrustRatingDisplay';
import CustomerReviews from '../components/professional/CustomerReviews';
import ContactSection from '../components/professional/ContactSection';
import ProfessionalFooter from '../components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '../components/booking/BookingWidgetProvider';
import { professionalApi, ProfessionalProfile, ServiceItem } from '../lib/api/professional-client';
import { BookableService } from '../lib/types/booking';
import { getBusinessConfig } from '../lib/config/api-config';

async function loadBusinessData(businessId: string) {
  try {
    console.log('🔄 [SERVER] Loading business data for:', businessId);
    console.log('🔄 [SERVER] Environment:', process.env.NODE_ENV);
    
    // Make direct API calls to the backend (server-to-server)
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    console.log('🔄 [SERVER] Backend URL:', backendUrl);
    
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
      console.log('✅ [SERVER] Profile loaded:', profile.business_name);
    }
    
    if (servicesResponse.ok) {
      services = await servicesResponse.json();
      console.log('✅ [SERVER] Services loaded:', services.length, 'items');
    }
    
    return { profile, services };
  } catch (error) {
    console.error('⚠️ [SERVER] Failed to load business data:', error);
    return { profile: null, services: [] };
  }
}

export default async function HomePage() {
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.defaultBusinessId;
  
  // Load business data server-side
  const { profile: serverProfile, services: serverServices } = await loadBusinessData(businessId);
  
  // Use server data if available, otherwise fallback
  const profile = serverProfile || {
    business_id: businessConfig.defaultBusinessId,
    business_name: businessConfig.defaultBusinessName,
    trade_type: 'hvac',
    description: 'Premier HVAC services for homes and businesses. Specializing in energy-efficient installations, emergency repairs, and preventative maintenance.',
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

  // Convert services to bookable format
  const bookableServices: BookableService[] = services.map(service => ({
    id: service.id,
    business_id: businessId,
    name: service.name,
    category: service.category,
    description: service.description,
    is_bookable: true,
    requires_site_visit: true,
    estimated_duration_minutes: service.duration_minutes || 90,
    min_duration_minutes: service.duration_minutes ? Math.max(30, service.duration_minutes - 30) : 60,
    max_duration_minutes: service.duration_minutes ? service.duration_minutes + 30 : 120,
    base_price: service.base_price || 0,
    price_type: service.requires_quote ? 'quote' as const : 'fixed' as const,
    required_skills: [],
    min_technicians: 1,
    max_technicians: 1,
    min_lead_time_hours: service.is_emergency ? 1 : 4,
    max_advance_days: 60,
    is_emergency_service: service.is_emergency,
    is_active: service.available,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }));

  // Generate dynamic content based on real business profile
  const generatedContent = !profile ? null : {
    businessName: profile.business_name,
    tagline: `Professional ${profile.trade_type} Services`,
    description: profile.description,
    phone: profile.phone,
    email: profile.email,
    address: profile.address,
    serviceAreas: profile.service_areas,
    emergencyService: profile.emergency_service,
    yearsInBusiness: profile.years_in_business,
    licenseNumber: profile.license_number,
    insuranceVerified: profile.insurance_verified,
    averageRating: profile.average_rating,
    totalReviews: profile.total_reviews,
    certifications: profile.certifications,
    website: profile.website
  };



  // Error state - show fallback content with default configuration
  if (error || !profile || !generatedContent) {
    const fallbackContent = {
      businessName: businessConfig.defaultBusinessName,
      tagline: "Professional Home Services",
      description: "Quality service you can trust. Licensed, insured, and committed to excellence.",
      phone: businessConfig.defaultBusinessPhone,
      email: businessConfig.defaultBusinessEmail,
      address: "Serving Your Local Area",
      serviceAreas: ["Local Area"],
      emergencyService: true,
      yearsInBusiness: 10,
      licenseNumber: "Licensed & Insured",
      insuranceVerified: true,
      averageRating: 4.8,
      totalReviews: 150,
      certifications: ["Licensed Professional", "Insured"],
      website: undefined
    };

    const fallbackServices = [
      {
        name: "Professional Service",
        description: "Quality service for your home or business",
        icon: "🔧",
        features: ["Licensed & Insured", "Same Day Service", "100% Satisfaction Guaranteed"],
        isEmergency: false,
        priceRange: "Contact for pricing"
      },
      {
        name: "Emergency Service",
        description: "24/7 emergency service when you need it most",
        icon: "🚨",
        features: ["24/7 Availability", "Rapid Response", "Emergency Repairs"],
        isEmergency: true,
        priceRange: "Emergency rates apply"
      }
    ];

  return (
      <BookingWidgetProvider
        businessId={businessId}
        companyName={fallbackContent.businessName}
        companyPhone={fallbackContent.phone}
        companyEmail={fallbackContent.email}
        services={[]}
      >
        <div className="min-h-screen bg-white">
          {/* Header */}
          <EliteHeader 
            businessName={fallbackContent.businessName}
            city={fallbackContent.serviceAreas[0] || 'Local Area'}
            state={'TX'}
            phone={fallbackContent.phone}
            supportHours={'24/7'}
          />
      
      {/* Hero Section */}
          <EliteHero 
            businessName={fallbackContent.businessName}
            headline={`Professional ${fallbackContent.businessName} Services`}
            subheadline={fallbackContent.tagline}
            city={fallbackContent.serviceAreas[0] || 'Local Area'}
            phone={fallbackContent.phone}
            averageRating={fallbackContent.averageRating}
            totalReviews={fallbackContent.totalReviews}
            emergencyMessage={fallbackContent.emergencyService ? '24/7 Emergency Service Available' : undefined}
            promotions={[]}
          />

          {/* Services Grid */}
          <EliteServicesGrid 
            businessName={fallbackContent.businessName}
            city={fallbackContent.serviceAreas[0] || 'Local Area'}
            phone={fallbackContent.phone}
          />

          {/* Trust & Rating Display */}
          <TrustRatingDisplay 
            averageRating={fallbackContent.averageRating}
            totalReviews={fallbackContent.totalReviews}
            certifications={fallbackContent.certifications}
            yearsInBusiness={fallbackContent.yearsInBusiness}
            licenseNumber={fallbackContent.licenseNumber}
            insuranceVerified={fallbackContent.insuranceVerified}
          />

          {/* Customer Reviews */}
          <CustomerReviews 
            businessName={fallbackContent.businessName}
            averageRating={fallbackContent.averageRating}
            totalReviews={fallbackContent.totalReviews}
          />

          {/* Contact Section */}
          <ContactSection 
            business={{
              name: fallbackContent.businessName,
              phone: fallbackContent.phone,
              email: fallbackContent.email,
              address: fallbackContent.address,
              service_areas: fallbackContent.serviceAreas,
              emergency_service: fallbackContent.emergencyService
            }}
            locations={[]}
          />

          {/* Footer */}
          <ProfessionalFooter 
            business={{
              name: fallbackContent.businessName,
              phone: fallbackContent.phone,
              email: fallbackContent.email,
              address: fallbackContent.address,
              license_number: fallbackContent.licenseNumber,
              website: fallbackContent.website,
              service_areas: fallbackContent.serviceAreas
            }}
            serviceCategories={[]}
            locations={[]}
          />

          {/* Error message for development */}
          {error && (
            <div className="fixed bottom-4 right-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded shadow-lg max-w-sm">
              <strong className="font-bold">Development Notice:</strong>
              <span className="block sm:inline"> {error}</span>
            </div>
          )}
        </div>
      </BookingWidgetProvider>
    );
  }

  return (
    <BookingWidgetProvider
      businessId={businessId}
      companyName={generatedContent.businessName}
      companyPhone={generatedContent.phone}
      companyEmail={generatedContent.email}
      services={bookableServices}
    >
      <div className="min-h-screen bg-white">
        {/* Header */}
        <EliteHeader 
          businessName={generatedContent.businessName}
          city={generatedContent.serviceAreas[0] || 'Austin'}
          state={'TX'}
          phone={generatedContent.phone}
          supportHours={'24/7'}
        />

        {/* Hero Section */}
        <EliteHero 
          businessName={generatedContent.businessName}
          headline={`Professional ${generatedContent.businessName} Services`}
          subheadline={generatedContent.tagline}
          city={generatedContent.serviceAreas[0] || 'Austin'}
          phone={generatedContent.phone}
          averageRating={generatedContent.averageRating}
          totalReviews={generatedContent.totalReviews}
          emergencyMessage={generatedContent.emergencyService ? '24/7 Emergency Service Available' : undefined}
          promotions={[]}
        />

        {/* Services Grid */}
        <EliteServicesGrid 
          businessName={generatedContent.businessName}
          city={generatedContent.serviceAreas[0] || 'Austin'}
          phone={generatedContent.phone}
        />

        {/* Trust & Rating Display */}
        <TrustRatingDisplay 
          averageRating={generatedContent.averageRating || 4.8}
          totalReviews={generatedContent.totalReviews || 150}
          certifications={generatedContent.certifications}
          yearsInBusiness={generatedContent.yearsInBusiness || 10}
          licenseNumber={generatedContent.licenseNumber}
          insuranceVerified={generatedContent.insuranceVerified}
        />

        {/* Customer Reviews */}
        <CustomerReviews 
          businessName={generatedContent.businessName}
          averageRating={generatedContent.averageRating || 4.8}
          totalReviews={generatedContent.totalReviews || 150}
        />

        {/* Contact Section */}
        <ContactSection 
          business={{
            name: generatedContent.businessName,
            phone: generatedContent.phone,
            email: generatedContent.email,
            address: generatedContent.address,
            service_areas: generatedContent.serviceAreas,
            emergency_service: generatedContent.emergencyService
          }}
          locations={[]}
        />

        {/* Footer */}
        <ProfessionalFooter 
          business={{
            name: generatedContent.businessName,
            phone: generatedContent.phone,
            email: generatedContent.email,
            address: generatedContent.address,
            license_number: generatedContent.licenseNumber,
            website: generatedContent.website,
            service_areas: generatedContent.serviceAreas
          }}
          serviceCategories={[]}
          locations={[]}
        />
      </div>
    </BookingWidgetProvider>
  );
}

