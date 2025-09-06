'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Hero365ProjectShowcase from '@/components/client/projects/Hero365ProjectShowcase';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

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

interface ProjectDetailClientProps {
  project: FeaturedProject | null;
  businessId: string;
  hasRealData: boolean;
}

export default function ProjectDetailClient({ 
  project, 
  businessId, 
  hasRealData 
}: ProjectDetailClientProps) {
  const router = useRouter();

  const handleBack = () => {
    router.push('/projects');
  };

  if (!project) {
    return (
      <div className="bg-gray-50">
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center space-y-4 max-w-md">
            <div className="text-6xl text-gray-400 mb-4">🔍</div>
            <h1 className="text-2xl font-bold text-gray-900">Project Not Found</h1>
            <p className="text-gray-600">
              The project you're looking for doesn't exist or has been removed.
            </p>
            <div className="space-x-4">
              <Button onClick={handleBack} variant="outline">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Projects
              </Button>
              <Button onClick={() => {
                if (typeof window !== 'undefined') {
                  window.location.reload();
                }
              }}>
                Try Again
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50">
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <nav className="flex items-center space-x-2 text-sm text-gray-600">
            <button onClick={() => router.push('/')} className="hover:text-blue-600 transition-colors">Home</button>
            <span>/</span>
            <button onClick={handleBack} className="hover:text-blue-600 transition-colors">Projects</button>
            <span>/</span>
            <span className="text-gray-900 font-medium">{project.title}</span>
          </nav>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Hero365ProjectShowcase project={project} showBackButton={true} onBack={handleBack} />
      </div>
    </div>
  );
}


