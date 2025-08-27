'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Calendar, MapPin, Clock, Star, ArrowRight, Play } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';

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
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const params = new URLSearchParams({
          limit: limit.toString(),
          offset: '0'
        });
        
        if (featuredOnly) {
          params.append('featured_only', 'true');
        }
        
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
        setProjects(data);
      } catch (err) {
        console.error('Error fetching featured projects:', err);
        setError('Failed to load projects');
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
