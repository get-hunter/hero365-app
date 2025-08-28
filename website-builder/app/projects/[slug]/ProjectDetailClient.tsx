'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ProjectShowcase from '@/components/projects/ProjectShowcase';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { getCurrentBusinessId } from '@/lib/config/api-config';
import EliteHeader from '@/components/layout/EliteHeader';
import ProfessionalFooter from '@/components/professional/ProfessionalFooter';
import { BookingWidgetProvider } from '@/components/booking/BookingWidgetProvider';
import { CartProvider } from '@/lib/contexts/CartContext';

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

interface ProjectDetailClientProps {
  params: { slug: string };
}

export default function ProjectDetailClient({ params }: ProjectDetailClientProps) {
  const router = useRouter();
  const [project, setProject] = useState<FeaturedProject | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const businessId = getCurrentBusinessId();
  const projectSlug = params.slug;

  useEffect(() => {
    if (projectSlug) {
      fetchProject();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectSlug]);

  const fetchProject = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(
        `${backendUrl}/api/v1/public/contractors/featured-projects/${businessId}/${projectSlug}`,
        { headers: { 'Content-Type': 'application/json' } }
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

  const shell = (
    children: React.ReactNode
  ) => (
    <CartProvider businessId={businessId}>
      <BookingWidgetProvider
        businessId={businessId}
        companyName="Austin Elite Home Services"
        companyPhone="(512) 555-0123"
        companyEmail="info@austinelitehome.com"
        services={[]}
      >
        <div className="min-h-screen bg-white">
          <EliteHeader 
            businessName="Austin Elite Home Services"
            city="Austin"
            state="TX"
            phone="(512) 555-0123"
            supportHours="24/7"
          />
          {children}
          <ProfessionalFooter 
            business={{
              id: businessId,
              name: 'Austin Elite Home Services',
              phone_number: '(512) 555-0123',
              business_email: 'info@austinelitehome.com',
              address: '123 Main St, Austin, TX 78701',
              website: 'https://austinelitehome.com',
              trades: [],
              service_areas: [],
              seo_keywords: []
            }}
            serviceCategories={[]}
            locations={[]}
          />
        </div>
      </BookingWidgetProvider>
    </CartProvider>
  );

  if (loading) {
    return shell(
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="text-gray-600">Loading project details...</p>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return shell(
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4 max-w-md">
          <div className="text-6xl text-gray-400 mb-4">🔍</div>
          <h1 className="text-2xl font-bold text-gray-900">
            {error === 'Project not found' ? 'Project Not Found' : 'Something went wrong'}
          </h1>
          <p className="text-gray-600">
            {error === 'Project not found' 
              ? "The project you're looking for doesn't exist or has been removed."
              : 'We encountered an error while loading the project details.'}
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

  return shell(
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
        <ProjectShowcase project={project} showBackButton={true} onBack={handleBack} />
      </div>
    </div>
  );
}


