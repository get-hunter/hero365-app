import React from 'react';
import { Metadata } from 'next';
import { getBusinessConfig, getDefaultHeaders } from '@/lib/config/api-config';
import EliteHeader from '@/components/layout/EliteHeader';
import ProfessionalFooter from '@/components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '@/components/booking/BookingWidgetProvider';
import { CartProvider } from '@/lib/contexts/CartContext';
import ProjectDetailClient from './ProjectDetailClient';

// Note: Using Node.js runtime for OpenNext compatibility
export const dynamic = 'force-dynamic';

async function loadProjectData(businessId: string, projectSlug: string) {
  try {
    console.log('🔄 [PROJECT DETAIL] Loading project data for:', businessId, projectSlug);
    
    // Try API calls during build time for hybrid rendering
    // Only fall back to demo data if API is actually unavailable
    
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    
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
  seo_slug: string;
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

export default async function ProjectDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const resolvedParams = await params;
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.defaultBusinessId;
  const projectSlug = resolvedParams.slug;

  const { project: serverProject, profile: serverProfile } = await loadProjectData(businessId, projectSlug);

  // Prefer real profile; fallback to defaults
  const profile: BusinessProfile = serverProfile || ({
    business_id: businessId,
    business_name: businessConfig.defaultBusinessName,
    trade_type: 'hvac',
    phone: businessConfig.defaultBusinessPhone,
    email: businessConfig.defaultBusinessEmail,
    address: '123 Main St',
    service_areas: ['Austin, TX'],
    emergency_service: true,
    years_in_business: 10,
    average_rating: 4.8,
    total_reviews: 150
  } as any);

  // Business data for header
  const headerData = {
    businessName: profile.business_name,
    phone: profile.phone,
    email: profile.email,
    address: profile.address,
    serviceAreas: profile.service_areas || ['Local Area'],
    emergencyService: profile.emergency_service,
    yearsInBusiness: profile.years_in_business,
    licenseNumber: 'Licensed & Insured',
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

          <ProjectDetailClient
            project={serverProject}
            businessId={businessId}
            hasRealData={!!serverProject}
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

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const resolvedParams = await params;
  const businessConfig = getBusinessConfig();
  const businessId = businessConfig.defaultBusinessId;
  const projectSlug = resolvedParams.slug;

  // Try to load metadata from API during build time

  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(
      `${backendUrl}/api/v1/public/contractors/featured-projects/${businessId}/${projectSlug}`,
      { headers: { 'Content-Type': 'application/json' }, cache: 'no-store' }
    ).catch(err => {
      console.log('⚠️ [METADATA] Project API failed:', err.message);
      return { ok: false };
    });
    
    if (response.ok) {
      const project = await response.json();
      return {
        title: `${project.title} | Project Portfolio`,
        description: project.description,
        openGraph: {
          title: project.title,
          description: project.description,
          images: project.after_images?.length > 0 ? [project.after_images[0]] : [],
          type: 'article',
        },
        twitter: {
          card: 'summary_large_image',
          title: project.title,
          description: project.description,
          images: project.after_images?.length > 0 ? [project.after_images[0]] : [],
        },
      } as any;
    }
  } catch (e) {
    console.error('metadata error', e);
  }

  return {
    title: 'Project Details | Portfolio',
    description: 'View detailed information about our completed project.',
  } as any;
}


