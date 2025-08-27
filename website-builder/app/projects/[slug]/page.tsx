'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ProjectShowcase from '@/components/projects/ProjectShowcase';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2 } from 'lucide-react';

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

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [project, setProject] = useState<FeaturedProject | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get business ID from URL or context
  const businessId = 'demo-business-id'; // This should come from your app context
  const projectSlug = params.slug as string;

  useEffect(() => {
    if (projectSlug) {
      fetchProject();
    }
  }, [projectSlug]);

  const fetchProject = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const response = await fetch(
        `${backendUrl}/api/v1/public/contractors/featured-projects/${businessId}/${projectSlug}`,
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      if (!response.ok) {
        if (response.status === 404) {
          setError('Project not found');
        } else {
          throw new Error('Failed to fetch project');
        }
        return;
      }
      
      const data = await response.json();
      setProject(data);
    } catch (err) {
      console.error('Error fetching project:', err);
      setError('Failed to load project details');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    router.push('/projects');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="text-gray-600">Loading project details...</p>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4 max-w-md">
          <div className="text-6xl text-gray-400 mb-4">🔍</div>
          <h1 className="text-2xl font-bold text-gray-900">
            {error === 'Project not found' ? 'Project Not Found' : 'Something went wrong'}
          </h1>
          <p className="text-gray-600">
            {error === 'Project not found' 
              ? 'The project you\'re looking for doesn\'t exist or has been removed.'
              : 'We encountered an error while loading the project details.'
            }
          </p>
          <div className="space-x-4">
            <Button onClick={handleBack} variant="outline">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Projects
            </Button>
            <Button onClick={() => window.location.reload()}>
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Breadcrumb */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <nav className="flex items-center space-x-2 text-sm text-gray-600">
            <button 
              onClick={() => router.push('/')}
              className="hover:text-blue-600 transition-colors"
            >
              Home
            </button>
            <span>/</span>
            <button 
              onClick={handleBack}
              className="hover:text-blue-600 transition-colors"
            >
              Projects
            </button>
            <span>/</span>
            <span className="text-gray-900 font-medium">{project.title}</span>
          </nav>
        </div>
      </div>

      {/* Project Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ProjectShowcase 
          project={project} 
          showBackButton={true}
          onBack={handleBack}
        />
      </div>
    </div>
  );
}

// Generate metadata for SEO
export async function generateMetadata({ params }: { params: { slug: string } }) {
  const businessId = 'demo-business-id'; // This should come from your app context
  const projectSlug = params.slug;

  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(
      `${backendUrl}/api/v1/public/contractors/featured-projects/${businessId}/${projectSlug}`,
      {
        headers: { 'Content-Type': 'application/json' }
      }
    );

    if (response.ok) {
      const project = await response.json();
      return {
        title: `${project.title} | Project Portfolio`,
        description: project.description,
        openGraph: {
          title: project.title,
          description: project.description,
          images: project.after_images.length > 0 ? [project.after_images[0]] : [],
          type: 'article',
        },
        twitter: {
          card: 'summary_large_image',
          title: project.title,
          description: project.description,
          images: project.after_images.length > 0 ? [project.after_images[0]] : [],
        }
      };
    }
  } catch (error) {
    console.error('Error generating metadata:', error);
  }

  return {
    title: 'Project Details | Portfolio',
    description: 'View detailed information about our completed project.',
  };
}
