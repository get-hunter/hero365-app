import React from 'react';
import { Metadata } from 'next';
import { getBusinessConfig, getBackendUrl, getDefaultHeaders } from '@/lib/config/api-config';
import EliteHeader from '@/components/layout/EliteHeader';
import ProfessionalFooter from '@/components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '@/components/booking/BookingWidgetProvider';
import { CartProvider } from '@/lib/contexts/CartContext';
import ProjectListingClient from './ProjectListingClient';

export const metadata: Metadata = {
  title: 'Project Portfolio | Professional Services',
  description: 'Explore our completed projects and see the quality craftsmanship we deliver.',
};

async function loadProjectData(businessId: string) {
  try {
    console.log('🔄 [PROJECTS] Loading project data for:', businessId);
    
    const backendUrl = getBackendUrl();
    
    const [projectsResponse, categoriesResponse, tagsResponse, profileResponse] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/contractors/featured-projects/${businessId}?limit=12&offset=0&featured_only=true`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 600, tags: ['projects', businessId] } // 10 min ISR
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/project-categories/${businessId}`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 86400, tags: ['categories', businessId] } // 1 day ISR
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/project-tags/${businessId}`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 86400, tags: ['tags', businessId] } // 1 day ISR
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/profile/${businessId}`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 3600, tags: ['profile', businessId] } // 1 hour ISR
      })
    ]);
    
    let projects = [];
    let categories = [];
    let tags = [];
    let profile = null;
    
    if (projectsResponse.ok) {
      projects = await projectsResponse.json();
      console.log('✅ [PROJECTS] Projects loaded:', projects.length, 'items');
      } else {
      console.warn('⚠️ [PROJECTS] Failed to load projects:', projectsResponse.status);
    }
    
    if (categoriesResponse.ok) {
      categories = await categoriesResponse.json();
      console.log('✅ [PROJECTS] Categories loaded:', categories.length, 'categories');
    }
    
    if (tagsResponse.ok) {
      tags = await tagsResponse.json();
      console.log('✅ [PROJECTS] Tags loaded:', tags.length, 'tags');
    }
    
    if (profileResponse.ok) {
      profile = await profileResponse.json();
      console.log('✅ [PROJECTS] Profile loaded:', profile.business_name);
    }
    
    return { projects, categories, tags, profile };
  } catch (error) {
    console.error('⚠️ [PROJECTS] Failed to load project data:', error);
    return { projects: [], categories: [], tags: [], profile: null };
  }
}

export default async function ProjectsPage() {
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.defaultBusinessId;
  
  const { 
    projects: serverProjects,
    categories: serverCategories,
    tags: serverTags,
    profile: serverProfile
  } = await loadProjectData(businessId);
  
  const profile = serverProfile || {
    business_id: businessId,
    business_name: businessConfig.defaultBusinessName,
    trade_type: 'hvac',
    phone: businessConfig.defaultBusinessPhone,
    email: businessConfig.defaultBusinessEmail,
    address: '123 Main St',
    service_areas: ['Local Area'],
    emergency_service: true,
    years_in_business: 10,
    average_rating: 4.8,
    total_reviews: 150
  };

  // Business data for header
  const headerData = {
    businessName: profile.business_name,
    phone: profile.phone,
    email: profile.email,
    address: profile.address,
    serviceAreas: profile.service_areas || ['Local Area'],
    emergencyService: profile.emergency_service,
    yearsInBusiness: profile.years_in_business,
    licenseNumber: profile.license_number || 'Licensed & Insured',
    insuranceVerified: true,
    averageRating: profile.average_rating,
    totalReviews: profile.total_reviews,
    certifications: profile.certifications || []
  };

  // Business data for footer (BusinessData type)
  const footerBusinessData = {
    id: profile.business_id || businessId,
    name: profile.business_name,
    description: profile.description,
    phone_number: profile.phone,
    business_email: profile.email,
    website: profile.website,
    logo_url: profile.logo_url,
    address: profile.address,
    city: profile.service_areas?.[0]?.split(',')[0] || 'Austin',
    state: profile.service_areas?.[0]?.split(',')[1]?.trim() || 'TX',
    zip_code: profile.zip_code,
    trades: profile.trades || ['hvac'],
    service_areas: profile.service_areas || ['Local Area'],
    business_hours: profile.business_hours,
    primary_trade: profile.trade_type || 'hvac',
    seo_keywords: profile.seo_keywords || []
  };

  return (
    <CartProvider businessId={businessId}>
      <BookingWidgetProvider
        businessId={businessId}
        services={[]} // Will be loaded by the provider
        companyName={profile.business_name}
        companyPhone={profile.phone}
      >
      <div className="min-h-screen bg-white">
        <EliteHeader 
            businessName={headerData.businessName}
            city={headerData.serviceAreas[0]?.split(',')[0] || 'Austin'}
            state={headerData.serviceAreas[0]?.split(',')[1]?.trim() || 'TX'}
            phone={headerData.phone}
          />
          
          <ProjectListingClient 
            projects={serverProjects}
            categories={serverCategories}
            tags={serverTags}
            businessId={businessId}
            hasRealData={serverProjects.length > 0}
          />

      <ProfessionalFooter 
            business={footerBusinessData}
        serviceCategories={[]}
        locations={[]}
      />
      </div>
      </BookingWidgetProvider>
    </CartProvider>
  );
}