import React from 'react';
import { getCurrentBusinessId } from '@/lib/config/api-config';
import ProjectDetailClient from './ProjectDetailClient';

export const runtime = 'edge';

export default async function ProjectDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const resolvedParams = await params;
  return <ProjectDetailClient params={resolvedParams} />;
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const resolvedParams = await params;
  const businessId = getCurrentBusinessId();
  const projectSlug = resolvedParams.slug;

  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(
      `${backendUrl}/api/v1/public/contractors/featured-projects/${businessId}/${projectSlug}`,
      { headers: { 'Content-Type': 'application/json' }, cache: 'no-store' }
    );
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


