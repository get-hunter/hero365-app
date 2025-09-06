import React from 'react';
import { Metadata } from 'next';
import { getDefaultHeaders } from '@/lib/shared/config/api-config';
import { getRuntimeConfig } from '@/lib/server/runtime-config';
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver';
import BusinessHeader from '@/components/shared/BusinessHeader';
import { notFound } from 'next/navigation';
import ProjectListingClient from './ProjectListingClient';
import Footer from '@/components/server/business/footer';

export const metadata: Metadata = {
  title: 'Project Portfolio | Professional Services',
  description: 'Explore our completed projects and see the quality craftsmanship we deliver.',
};

async function loadProjectData(businessId: string) {
  try {
    console.log('🔄 [PROJECTS] Loading project data for:', businessId);
    
    const config = await getRuntimeConfig();
    const backendUrl = config.apiUrl;
    
    const [projectsResponse, categoriesResponse, tagsResponse, profileResponse] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/contractors/featured-projects/${businessId}?limit=12&offset=0&featured_only=true`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 600, tags: ['projects', businessId] } // 10 min ISR
      }).catch(err => {
        console.log('⚠️ [PROJECTS] Projects API failed:', err.message);
        return { ok: false };
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/project-categories/${businessId}`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 86400, tags: ['categories', businessId] } // 1 day ISR
      }).catch(err => {
        console.log('⚠️ [PROJECTS] Categories API failed:', err.message);
        return { ok: false };
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/project-tags/${businessId}`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 86400, tags: ['tags', businessId] } // 1 day ISR
      }).catch(err => {
        console.log('⚠️ [PROJECTS] Tags API failed:', err.message);
        return { ok: false };
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/profile/${businessId}`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 3600, tags: ['profile', businessId] } // 1 hour ISR
      }).catch(err => {
        console.log('⚠️ [PROJECTS] Profile API failed:', err.message);
        return { ok: false };
      })
    ]);
    
    let projects = [];
    let categories = [];
    let tags = [];
    let profile = null;
    
    if (projectsResponse && 'ok' in projectsResponse && projectsResponse.ok) {
      projects = await (projectsResponse as Response).json();
      console.log('✅ [PROJECTS] Projects loaded:', projects.length, 'items');
    }
    
    if (categoriesResponse && 'ok' in categoriesResponse && categoriesResponse.ok) {
      categories = await (categoriesResponse as Response).json();
      console.log('✅ [PROJECTS] Categories loaded:', categories.length, 'categories');
    }
    
    if (tagsResponse && 'ok' in tagsResponse && tagsResponse.ok) {
      tags = await (tagsResponse as Response).json();
      console.log('✅ [PROJECTS] Tags loaded:', tags.length, 'tags');
    }
    
    if (profileResponse && 'ok' in profileResponse && profileResponse.ok) {
      profile = await (profileResponse as Response).json();
      console.log('✅ [PROJECTS] Profile loaded:', profile.business_name);
    }
    
    return { projects, categories, tags, profile };
  } catch (error) {
    console.error('⚠️ [PROJECTS] Failed to load project data:', error);
    return { projects: [], categories: [], tags: [], profile: null };
  }
}

export default async function ProjectsPage() {
  // Get business ID from host for multi-tenant support
  const resolution = await getBusinessIdFromHost();
  const businessId = resolution.businessId;
  
  const { 
    projects: serverProjects,
    categories: serverCategories,
    tags: serverTags,
    profile: serverProfile
  } = await loadProjectData(businessId);
  
  if (!serverProfile) {
    notFound();
  }
  const profile = serverProfile;

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
    primary_trade: profile.primary_trade_slug || 'hvac',
    seo_keywords: profile.seo_keywords || []
  };

  // Ensure props passed to client components are fully serializable
  const safeProjects = JSON.parse(JSON.stringify(serverProjects || []));
  const safeCategories = JSON.parse(JSON.stringify(serverCategories || []));
  const safeTags = JSON.parse(JSON.stringify(serverTags || []));
  const safeFooterBusinessData = JSON.parse(JSON.stringify(footerBusinessData));

  return (
      <div className="min-h-screen bg-white">
        <BusinessHeader 
          businessProfile={serverProfile}
          showCTA={false}
          showCart={false}
        />
        
        <ProjectListingClient 
          projects={safeProjects}
          categories={safeCategories}
          tags={safeTags}
          businessId={businessId}
          hasRealData={safeProjects.length > 0}
        />
        <Footer 
          business={safeFooterBusinessData}
          serviceCategories={[]}
          locations={[]}
        />
      </div>
  );
}