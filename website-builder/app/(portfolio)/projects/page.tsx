import React from 'react';
import { Metadata } from 'next';
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver';
import Hero365Header from '@/components/server/layout/Hero365Header';
import Hero365Footer from '@/components/shared/Hero365Footer';
import { notFound } from 'next/navigation';
import ProjectListingClient from './ProjectListingClient';
import { loadPageData } from '@/lib/server/data-fetchers';

export const metadata: Metadata = {
  title: 'Project Portfolio | Professional Services',
  description: 'Explore our completed projects and see the quality craftsmanship we deliver.',
};


export default async function ProjectsPage() {
  // Get business ID from host for multi-tenant support
  const resolution = await getBusinessIdFromHost();
  const businessId = resolution.businessId;
  
  const { 
    profile: serverProfile,
    projects: serverProjects
  } = await loadPageData(businessId, {
    includeProjects: true
  });
  
  // For now, we'll use empty arrays for categories and tags until we add them to loadPageData
  const serverCategories: any[] = [];
  const serverTags: any[] = [];
  
  if (!serverProfile) {
    notFound();
  }
  const profile = serverProfile;

  // Ensure props passed to client components are fully serializable
  const safeProjects = JSON.parse(JSON.stringify(serverProjects || []));
  const safeCategories = JSON.parse(JSON.stringify(serverCategories || []));
  const safeTags = JSON.parse(JSON.stringify(serverTags || []));

  return (
      <div className="min-h-screen bg-white">
        <Hero365Header 
          businessProfile={serverProfile as any}
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
        <Hero365Footer 
          business={profile}
          showEmergencyBanner={!!profile.emergency_service}
        />
      </div>
  );
}