/**
 * Professional Business Website - Homepage
 * 
 * Main business website that loads real business data from the Hero365 backend
 * Configured with business ID via environment variables during deployment
 */

'use client';

import React, { useState, useEffect, useMemo } from 'react';
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

export default function HomePage() {
  const businessConfig = getBusinessConfig();
  
  // Use configured business ID
  const businessId = businessConfig.defaultBusinessId;
  
  const [profile, setProfile] = useState<ProfessionalProfile | null>(null);
  const [services, setServices] = useState<ServiceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load business data
  useEffect(() => {
    async function loadBusinessData() {
      try {
        setLoading(true);
        setError(null);

        // Load profile and services in parallel
        const [profileData, servicesData] = await Promise.all([
          professionalApi.getProfessionalProfile(businessId),
          professionalApi.getProfessionalServices(businessId)
        ]);

        setProfile(profileData);
        setServices(servicesData);
      } catch (err) {
        console.error('Error loading business data:', err);
        console.log('Using fallback content since API is not available');
        setError('API not available - using fallback content');
        // Don't set profile to null, let it fall through to fallback content
      } finally {
        setLoading(false);
      }
    }

    if (businessId) {
      loadBusinessData();
    }
  }, [businessId]);

  // Convert services to bookable format
  const bookableServices: BookableService[] = useMemo(() => {
    return services.map(service => ({
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
  }, [services, businessId]);

  // Generate dynamic content based on real business profile
  const generatedContent = useMemo(() => {
    if (!profile) return null;

    return {
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
  }, [profile]);

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading professional profile...</p>
        </div>
      </div>
    );
  }

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
            companyName={fallbackContent.businessName}
            companyPhone={fallbackContent.phone}
            location={fallbackContent.serviceAreas[0]}
            emergencyService={fallbackContent.emergencyService}
          />

          {/* Hero Section */}
          <EliteHero 
            businessName={fallbackContent.businessName}
            tagline={fallbackContent.tagline}
            description={fallbackContent.description}
            phone={fallbackContent.phone}
            serviceAreas={fallbackContent.serviceAreas}
            emergencyService={fallbackContent.emergencyService}
            yearsInBusiness={fallbackContent.yearsInBusiness}
            licenseNumber={fallbackContent.licenseNumber}
            averageRating={fallbackContent.averageRating}
            totalReviews={fallbackContent.totalReviews}
            promotions={[]}
          />

          {/* Services Grid */}
          <EliteServicesGrid 
            services={fallbackServices}
            emergencyService={fallbackContent.emergencyService}
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
            businessName={fallbackContent.businessName}
            phone={fallbackContent.phone}
            email={fallbackContent.email}
            address={fallbackContent.address}
            serviceAreas={fallbackContent.serviceAreas}
            emergencyService={fallbackContent.emergencyService}
          />

          {/* Footer */}
          <ProfessionalFooter 
            companyName={fallbackContent.businessName}
            phone={fallbackContent.phone}
            email={fallbackContent.email}
            address={fallbackContent.address}
            licenseNumber={fallbackContent.licenseNumber}
            website={fallbackContent.website}
          />

          {/* Error message for development */}
          {error && (
            <div className="fixed bottom-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded shadow-lg max-w-sm">
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
          companyName={generatedContent.businessName}
          companyPhone={generatedContent.phone}
          location={generatedContent.serviceAreas[0] || generatedContent.address}
          emergencyService={generatedContent.emergencyService}
        />

        {/* Hero Section */}
        <EliteHero 
          businessName={generatedContent.businessName}
          tagline={generatedContent.tagline}
          description={generatedContent.description}
          phone={generatedContent.phone}
          serviceAreas={generatedContent.serviceAreas}
          emergencyService={generatedContent.emergencyService}
          yearsInBusiness={generatedContent.yearsInBusiness}
          licenseNumber={generatedContent.licenseNumber}
          averageRating={generatedContent.averageRating}
          totalReviews={generatedContent.totalReviews}
          promotions={[]}
        />

        {/* Services Grid */}
        <EliteServicesGrid 
          services={services.map(service => ({
            name: service.name,
            description: service.description,
            icon: getServiceIcon(service.category),
            features: getServiceFeatures(service),
            isEmergency: service.is_emergency,
            priceRange: service.price_range_min && service.price_range_max 
              ? `$${service.price_range_min} - $${service.price_range_max}`
              : service.base_price 
                ? `Starting at $${service.base_price}`
                : 'Contact for pricing'
          }))}
          emergencyService={generatedContent.emergencyService}
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
          businessName={generatedContent.businessName}
          phone={generatedContent.phone}
          email={generatedContent.email}
          address={generatedContent.address}
          serviceAreas={generatedContent.serviceAreas}
          emergencyService={generatedContent.emergencyService}
        />

        {/* Footer */}
        <ProfessionalFooter 
          companyName={generatedContent.businessName}
          phone={generatedContent.phone}
          email={generatedContent.email}
          address={generatedContent.address}
          licenseNumber={generatedContent.licenseNumber}
          website={generatedContent.website}
        />
      </div>
    </BookingWidgetProvider>
  );
}

// Helper functions
function getServiceIcon(category: string): string {
  const iconMap: Record<string, string> = {
    'HVAC': '🌡️',
    'Plumbing': '🔧',
    'Electrical': '⚡',
    'Repair': '🛠️',
    'Installation': '🔨',
    'Maintenance': '⚙️',
    'Emergency': '🚨',
    'Air Quality': '💨',
    'Controls': '🎛️'
  };
  return iconMap[category] || '🔧';
}

function getServiceFeatures(service: ServiceItem): string[] {
  const features = [];
  
  if (service.is_emergency) {
    features.push('24/7 Emergency Service');
  }
  
  if (service.duration_minutes) {
    features.push(`${service.duration_minutes} min service`);
  }
  
  if (service.requires_quote) {
    features.push('Custom Quote');
  } else if (service.base_price) {
    features.push(`Starting at $${service.base_price}`);
  }
  
  if (service.available) {
    features.push('Available Now');
  }
  
  return features.length > 0 ? features : ['Professional Service', 'Licensed & Insured', 'Satisfaction Guaranteed'];
}