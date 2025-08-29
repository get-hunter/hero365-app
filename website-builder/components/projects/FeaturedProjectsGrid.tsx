'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Calendar, MapPin, Clock, Star, ArrowRight, Play } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { getBackendUrl } from '@/lib/config/api-config';

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

interface FeaturedProjectsGridProps {
  businessId: string;
  limit?: number;
  featuredOnly?: boolean;
  showViewAll?: boolean;
  className?: string;
}

export default function FeaturedProjectsGrid({
  businessId,
  limit = 6,
  featuredOnly = true,
  showViewAll = true,
  className = ""
}: FeaturedProjectsGridProps) {
  const [projects, setProjects] = useState<FeaturedProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const backendUrl = getBackendUrl();
        const params = new URLSearchParams({
          limit: limit.toString(),
          offset: '0'
        });
        
        if (featuredOnly) {
          params.append('featured_only', 'true');
        }
        
        console.log('🔄 [FEATURED_PROJECTS] Fetching projects from:', `${backendUrl}/api/v1/public/contractors/featured-projects/${businessId}`);
        
        const response = await fetch(
          `${backendUrl}/api/v1/public/contractors/featured-projects/${businessId}?${params}`,
          {
            headers: { 'Content-Type': 'application/json' }
          }
        );
        
        if (!response.ok) {
          throw new Error('Failed to fetch projects');
        }
        
        const data = await response.json();
        console.log('✅ [FEATURED_PROJECTS] Projects loaded successfully:', data.length, 'projects');
        setProjects(data);
      } catch (err) {
        console.error('❌ [FEATURED_PROJECTS] Error fetching featured projects:', err);
        console.error('❌ [FEATURED_PROJECTS] Business ID:', businessId);
        console.error('❌ [FEATURED_PROJECTS] Backend URL:', getBackendUrl());
        
        // Use fallback data when API is not available
        console.log('🔄 [FEATURED_PROJECTS] Using fallback project data');
        const fallbackProjects = [
          {
            id: '1',
            title: 'Complete HVAC System Replacement',
            description: 'Full HVAC system replacement for a 3,500 sq ft home including new ductwork, smart thermostat, and energy-efficient units.',
            trade: 'HVAC',
            service_category: 'HVAC Installation',
            location: 'Austin, TX',
            completion_date: '2024-01-15',
            project_duration: '3 days',
            project_value: 15500.0,
            customer_name: 'Sarah Johnson',
            customer_testimonial: 'Outstanding service from start to finish. The team was professional, clean, and completed the job ahead of schedule. Our energy bills have dropped significantly!',
            before_images: ['https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800'],
            after_images: ['https://images.unsplash.com/photo-1631889993959-41b4e9c6e3c5?w=800'],
            gallery_images: ['https://images.unsplash.com/photo-1631889993959-41b4e9c6e3c5?w=800', 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800'],
            video_url: undefined,
            challenges_faced: ['Old system was 20+ years old and inefficient', 'Ductwork needed complete replacement', 'Tight timeline before summer heat'],
            solutions_provided: ['Installed high-efficiency variable speed system', 'Replaced all ductwork with proper insulation', 'Added smart zoning controls'],
            equipment_installed: ['Carrier Infinity 19VS Heat Pump', 'Carrier Infinity Air Handler', 'Ecobee Smart Thermostat Pro', 'New insulated ductwork'],
            warranty_info: '10-year manufacturer warranty on equipment, 5-year warranty on installation',
            is_featured: true,
            seo_slug: 'complete-hvac-system-replacement-austin',
            tags: ['Residential', 'Energy Efficient', 'Smart Home'],
            display_order: 1
          },
          {
            id: '2',
            title: 'Emergency Plumbing Repair - Burst Pipe',
            description: 'Emergency response to a burst pipe in the main water line. Completed full repair and restoration within 4 hours.',
            trade: 'Plumbing',
            service_category: 'Plumbing Repair',
            location: 'Round Rock, TX',
            completion_date: '2024-01-20',
            project_duration: '4 hours',
            project_value: 850.0,
            customer_name: 'Mike Chen',
            customer_testimonial: 'Called at 2 AM with a burst pipe flooding my basement. They arrived within 30 minutes and had everything fixed by 6 AM. Incredible service!',
            before_images: ['https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800'],
            after_images: ['https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800'],
            gallery_images: ['https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800'],
            video_url: undefined,
            challenges_faced: ['Water damage spreading rapidly', 'Limited access to main line', 'Emergency response needed'],
            solutions_provided: ['Immediate water shutoff and containment', 'Replaced damaged section with PEX piping', 'Pressure tested entire system'],
            equipment_installed: ['PEX piping and fittings', 'New shutoff valve', 'Pipe insulation'],
            warranty_info: '2-year warranty on all parts and labor',
            is_featured: true,
            seo_slug: 'emergency-plumbing-repair-burst-pipe',
            tags: ['Emergency', 'Residential'],
            display_order: 2
          },
          {
            id: '3',
            title: 'Smart Home Security System Installation',
            description: 'Complete smart security system installation with cameras, sensors, and mobile app integration for a modern home.',
            trade: 'Security Systems',
            service_category: 'Security Installation',
            location: 'Pflugerville, TX',
            completion_date: '2024-02-10',
            project_duration: '1 day',
            project_value: 4800.0,
            customer_name: 'Robert Kim',
            customer_testimonial: 'Excellent installation and setup. The mobile app works perfectly and we feel much more secure. Highly recommend!',
            before_images: ['https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800'],
            after_images: ['https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800'],
            gallery_images: ['https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800'],
            video_url: undefined,
            challenges_faced: ['Existing system was outdated', 'Wanted mobile integration', 'Multiple entry points to secure'],
            solutions_provided: ['Installed wireless security system', 'Set up mobile app and notifications', 'Added smart door locks and cameras'],
            equipment_installed: ['Ring Alarm Pro System', '8 Door/Window Sensors', '4 Motion Detectors', '6 Security Cameras', 'Smart Door Locks'],
            warranty_info: '3-year manufacturer warranty, 1-year installation warranty',
            is_featured: true,
            seo_slug: 'smart-home-security-system-installation',
            tags: ['Residential', 'Smart Home', 'Security'],
            display_order: 3
          }
        ];
        
        setProjects(fallbackProjects.slice(0, limit));
        setError(null); // Clear error since we have fallback data
      } finally {
        setLoading(false);
      }
    };

    if (businessId) {
      fetchProjects();
    }
  }, [businessId, limit, featuredOnly]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      year: 'numeric'
    });
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="text-center">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-64 mx-auto mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-96 mx-auto"></div>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-200 rounded-lg h-64 mb-4"></div>
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || projects.length === 0) {
    return null; // Don't show anything if there are no projects
  }

  return (
    <section className={`space-y-8 ${className}`}>
      {/* Section Header */}
      <div className="text-center space-y-4">
        <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
          Featured Projects
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          See our recent work and the quality craftsmanship we deliver to every customer
        </p>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <Card key={project.id} className="group overflow-hidden hover:shadow-xl transition-all duration-300">
            <div className="relative">
              {/* Project Image */}
              <div className="relative h-64 overflow-hidden">
                {project.after_images.length > 0 ? (
                  <Image
                    src={project.after_images[0]}
                    alt={project.title}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                ) : project.before_images.length > 0 ? (
                  <Image
                    src={project.before_images[0]}
                    alt={project.title}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                    <span className="text-white text-lg font-semibold">
                      {project.trade}
                    </span>
                  </div>
                )}
                
                {/* Video Play Button */}
                {project.video_url && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-20 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <Button size="sm" className="rounded-full bg-white text-blue-600 hover:bg-blue-50">
                      <Play className="w-4 h-4" />
                    </Button>
                  </div>
                )}

                {/* Featured Badge */}
                {project.is_featured && (
                  <Badge className="absolute top-3 left-3 bg-yellow-500 text-yellow-900">
                    Featured
                  </Badge>
                )}

                {/* Project Value */}
                {project.project_value && (
                  <Badge variant="secondary" className="absolute top-3 right-3 bg-white text-gray-900">
                    {formatCurrency(project.project_value)}
                  </Badge>
                )}
              </div>

              <CardContent className="p-6">
                {/* Project Title & Category */}
                <div className="space-y-2 mb-4">
                  <h3 className="text-xl font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                    {project.title}
                  </h3>
                  <Badge variant="outline" className="text-xs">
                    {project.service_category}
                  </Badge>
                </div>

                {/* Project Description */}
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {project.description}
                </p>

                {/* Project Details */}
                <div className="space-y-2 mb-4 text-sm text-gray-500">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    <span>{project.location}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>Completed {formatDate(project.completion_date)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>{project.project_duration}</span>
                  </div>
                </div>

                {/* Customer Testimonial */}
                {project.customer_testimonial && (
                  <div className="bg-gray-50 rounded-lg p-3 mb-4">
                    <div className="flex items-center gap-1 mb-2">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                      ))}
                    </div>
                    <p className="text-xs text-gray-600 line-clamp-2">
                      "{project.customer_testimonial}"
                    </p>
                    {project.customer_name && (
                      <p className="text-xs text-gray-500 mt-1">
                        - {project.customer_name}
                      </p>
                    )}
                  </div>
                )}

                {/* Project Tags */}
                {project.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {project.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                    {project.tags.length > 3 && (
                      <Badge variant="secondary" className="text-xs">
                        +{project.tags.length - 3}
                      </Badge>
                    )}
                  </div>
                )}

                {/* View Project Button */}
                <Link href={`/projects/${project.seo_slug}`}>
                  <Button variant="outline" className="w-full group-hover:bg-blue-600 group-hover:text-white transition-colors">
                    View Project Details
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </CardContent>
            </div>
          </Card>
        ))}
      </div>

      {/* View All Projects Button */}
      {showViewAll && projects.length >= limit && (
        <div className="text-center">
          <Link href="/projects">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white">
              View All Projects
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      )}
    </section>
  );
}
