import React from 'react';
import { Metadata } from 'next';
import { getDefaultHeaders } from '@/lib/shared/config/api-config';
import { getRuntimeConfig } from '@/lib/server/runtime-config';
import BusinessHeader from '@/components/shared/BusinessHeader';
import Hero365Footer from '@/components/shared/Hero365Footer';
import { Hero365BookingProvider } from '@/components/client/commerce/booking/Hero365BookingProvider';
import { CartProvider } from '@/lib/client/contexts/CartContext';
import ProjectDetailClient from './ProjectDetailClient';
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver';
import { notFound } from 'next/navigation';

// Note: Using Node.js runtime for OpenNext compatibility
export const dynamic = 'force-dynamic';

async function loadProjectData(businessId: string, projectSlug: string) {
  try {
    console.log('🔄 [PROJECT DETAIL] Loading project data for:', businessId, projectSlug);
    
    // Try API calls during build time for hybrid rendering
    // Only fall back to demo data if API is actually unavailable
    
    const config = await getRuntimeConfig();
    const backendUrl = config.apiUrl;
    
    const [projectResponse, profileResponse] = await Promise.all([
      fetch(`${backendUrl}/api/v1/public/contractors/featured-projects/${businessId}/${projectSlug}`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 300 } // Cache for 5 minutes
      }).catch(err => {
        console.log('⚠️ [PROJECT DETAIL] Project API failed:', err.message);
        return { ok: false };
      }),
      fetch(`${backendUrl}/api/v1/public/contractors/profile/${businessId}`, {
        headers: getDefaultHeaders(),
        next: { revalidate: 600 } // Cache for 10 minutes
      }).catch(err => {
        console.log('⚠️ [PROJECT DETAIL] Profile API failed:', err.message);
        return { ok: false };
      })
    ]);
    
    let project = null;
    let profile = null;
    
    if (projectResponse.ok) {
      project = await projectResponse.json();
      console.log('✅ [PROJECT DETAIL] Project loaded:', project.title);
    } else {
      console.warn('⚠️ [PROJECT DETAIL] Failed to load project:', projectResponse.status);
    }
    
    if (profileResponse.ok) {
      profile = await profileResponse.json();
      console.log('✅ [PROJECT DETAIL] Profile loaded:', profile.business_name);
    }
    
    return { project, profile };
  } catch (error) {
    console.error('⚠️ [PROJECT DETAIL] Failed to load project data:', error);
    return { project: null, profile: null };
  }
}

interface FeaturedProject {
  id: string;
  title: string;
  description: string;
  trade: string;
  service_category: string;
  location: string;
  completion_date: string;
  project_duration: string;
  project_value?: number;
  customer_name?: string;
  customer_testimonial?: string;
  before_images: string[];
  after_images: string[];
  gallery_images: string[];
  video_url?: string;
  challenges_faced: string[];
  solutions_provided: string[];
  equipment_installed: string[];
  warranty_info?: string;
  is_featured: boolean;
  slug: string;
  tags: string[];
  display_order: number;
}

interface BusinessProfile {
  business_id: string;
  business_name: string;
  trade_type: string;
  phone: string;
  email: string;
  address: string;
  service_areas: string[];
  emergency_service: boolean;
  years_in_business: number;
  average_rating: number;
  total_reviews: number;
  certifications: string[];
  description?: string;
  website?: string;
  logo_url?: string;
  zip_code?: string;
  trades?: string[];
  business_hours?: any;
  seo_keywords?: string[];
}

export default async function ProjectDetailPage({ 
  params 
}: { 
  params: { slug: string } 
}) {
  try {
    // Get business ID from host for multi-tenant support
    const resolution = await getBusinessIdFromHost();
    const businessId = resolution.businessId;
    
    const projectSlug = params.slug;

    const { project: serverProject, profile: serverProfile } = await loadProjectData(businessId, projectSlug);

    // Enforce no-fallback policy
    if (!serverProject || !serverProfile) {
      notFound();
    }

    // Ensure all data is properly serializable
    const profile: BusinessProfile = {
      ...serverProfile,
      business_hours: serverProfile.business_hours || null,
      seo_keywords: Array.isArray(serverProfile.seo_keywords) ? serverProfile.seo_keywords : [],
      // Ensure all string fields are properly serialized
      business_name: typeof serverProfile.business_name === 'string' ? serverProfile.business_name : '',
      description: typeof serverProfile.description === 'string' ? serverProfile.description : '',
      phone: typeof serverProfile.phone === 'string' ? serverProfile.phone : '',
      email: typeof serverProfile.email === 'string' ? serverProfile.email : '',
      website: typeof serverProfile.website === 'string' ? serverProfile.website : null,
      logo_url: typeof serverProfile.logo_url === 'string' ? serverProfile.logo_url : null,
      address: typeof serverProfile.address === 'string' ? serverProfile.address : '',
      service_areas: Array.isArray(serverProfile.service_areas) ? serverProfile.service_areas : [],
      trades: Array.isArray(serverProfile.trades) ? serverProfile.trades : []
    };

    // Ensure project data is properly serializable
    const project = {
      ...serverProject,
      // Ensure all string fields are properly serialized
      id: typeof serverProject.id === 'string' ? serverProject.id : String(serverProject.id || ''),
      title: typeof serverProject.title === 'string' ? serverProject.title : '',
      description: typeof serverProject.description === 'string' ? serverProject.description : '',
      trade: typeof serverProject.trade === 'string' ? serverProject.trade : '',
      service_category: typeof serverProject.service_category === 'string' ? serverProject.service_category : '',
      location: typeof serverProject.location === 'string' ? serverProject.location : '',
      slug: typeof serverProject.slug === 'string' ? serverProject.slug : '',
      // Ensure numeric fields are properly handled
      project_value: typeof serverProject.project_value === 'number' ? serverProject.project_value : null,
      display_order: typeof serverProject.display_order === 'number' ? serverProject.display_order : 0,
      // Ensure boolean fields are properly handled
      is_featured: Boolean(serverProject.is_featured),
      // Ensure optional string fields are properly handled
      video_url: serverProject.video_url || null,
      warranty_info: serverProject.warranty_info || null,
      customer_name: serverProject.customer_name || null,
      customer_testimonial: serverProject.customer_testimonial || null,
      // Ensure date fields are strings, not Date objects
      completion_date: typeof serverProject.completion_date === 'string' ? serverProject.completion_date : 
                      serverProject.completion_date ? String(serverProject.completion_date) : null,
      project_duration: typeof serverProject.project_duration === 'string' ? serverProject.project_duration : 
                       serverProject.project_duration ? String(serverProject.project_duration) : null,
      // Ensure arrays are properly handled
      before_images: Array.isArray(serverProject.before_images) ? serverProject.before_images : [],
      after_images: Array.isArray(serverProject.after_images) ? serverProject.after_images : [],
      gallery_images: Array.isArray(serverProject.gallery_images) ? serverProject.gallery_images : [],
      challenges_faced: Array.isArray(serverProject.challenges_faced) ? serverProject.challenges_faced : [],
      solutions_provided: Array.isArray(serverProject.solutions_provided) ? serverProject.solutions_provided : [],
      equipment_installed: Array.isArray(serverProject.equipment_installed) ? serverProject.equipment_installed : [],
      tags: Array.isArray(serverProject.tags) ? serverProject.tags : []
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

    return (
      <CartProvider businessId={businessId}>
        <Hero365BookingProvider
          businessId={businessId}
          services={[]} // Will be loaded by the provider
          companyName={profile.business_name}
          companyPhone={profile.phone}
        >
          <div className="min-h-screen bg-white">
            <BusinessHeader
              businessProfile={profile}
              showCTA={false}
              showCart={false}
              ctaSlot={undefined}
              cartSlot={undefined}
            />

            <ProjectDetailClient
              project={project}
              businessId={businessId}
              hasRealData={!!project}
            />

            <Hero365Footer
              business={footerBusinessData}
              services={[]}
              locations={[]}
            />
          </div>
        </Hero365BookingProvider>
      </CartProvider>
    );
  } catch (error) {
    console.error('Project page error:', error);
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Project Not Available</h1>
          <p className="mt-4 text-gray-600">There was an error loading this project.</p>
        </div>
      </div>
    );
  }
}

export async function generateMetadata() {
  return {
    title: 'Project Details | Portfolio',
    description: 'View detailed information about our completed project.',
  } as any;
}
