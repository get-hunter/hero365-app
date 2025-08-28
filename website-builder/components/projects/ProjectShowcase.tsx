'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { 
  Calendar, 
  MapPin, 
  Clock, 
  DollarSign, 
  Star, 
  CheckCircle, 
  AlertTriangle,
  Wrench,
  Shield,
  Play,
  ExternalLink,
  Share2
} from 'lucide-react';
import Image from 'next/image';
import BeforeAfterGallery from './BeforeAfterGallery';

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

interface ProjectShowcaseProps {
  project: FeaturedProject;
  className?: string;
  showBackButton?: boolean;
  onBack?: () => void;
}

export default function ProjectShowcase({
  project,
  className = "",
  showBackButton = false,
  onBack
}: ProjectShowcaseProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'gallery' | 'details'>('overview');

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
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

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: project.title,
          text: project.description,
          url: window.location.href
        });
      } catch (err) {
        console.log('Error sharing:', err);
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
    }
  };

  // Prepare before/after images for gallery
  const beforeAfterImages = project.before_images.map((beforeImg, index) => ({
    before: beforeImg,
    after: project.after_images[index] || project.after_images[0] || beforeImg,
    title: `${project.title} - View ${index + 1}`,
    description: index === 0 ? project.description : undefined
  }));

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Header */}
      <div className="space-y-4">
        {showBackButton && (
          <Button variant="outline" onClick={onBack} className="mb-4">
            ← Back to Projects
          </Button>
        )}
        
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="outline" className="text-sm">
                {project.trade}
              </Badge>
              <Badge variant="secondary" className="text-sm">
                {project.service_category}
              </Badge>
              {project.is_featured && (
                <Badge className="bg-yellow-500 text-yellow-900">
                  Featured Project
                </Badge>
              )}
            </div>
            
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
              {project.title}
            </h1>
            
            <p className="text-lg text-gray-600 max-w-3xl">
              {project.description}
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleShare}>
              <Share2 className="w-4 h-4 mr-2" />
              Share
            </Button>
            {project.video_url && (
              <Button variant="outline" size="sm" asChild>
                <a href={project.video_url} target="_blank" rel="noopener noreferrer">
                  <Play className="w-4 h-4 mr-2" />
                  Watch Video
                </a>
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Project Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <MapPin className="w-6 h-6 text-blue-600 mx-auto mb-2" />
            <p className="text-sm text-gray-600">Location</p>
            <p className="font-semibold">{project.location}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <Calendar className="w-6 h-6 text-green-600 mx-auto mb-2" />
            <p className="text-sm text-gray-600">Completed</p>
            <p className="font-semibold">{formatDate(project.completion_date)}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <Clock className="w-6 h-6 text-orange-600 mx-auto mb-2" />
            <p className="text-sm text-gray-600">Duration</p>
            <p className="font-semibold">{project.project_duration}</p>
          </CardContent>
        </Card>
        
        {project.project_value && (
          <Card>
            <CardContent className="p-4 text-center">
              <DollarSign className="w-6 h-6 text-purple-600 mx-auto mb-2" />
              <p className="text-sm text-gray-600">Project Value</p>
              <p className="font-semibold">{formatCurrency(project.project_value)}</p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'gallery', 'details'].map((tab) => (
            <button
              key={tab}
              className={`py-2 px-1 border-b-2 font-medium text-sm capitalize ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab(tab as any)}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-8">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Before/After Gallery */}
              {beforeAfterImages.length > 0 && (
                <div>
                  <h3 className="text-xl font-semibold mb-4">Before & After</h3>
                  <BeforeAfterGallery images={beforeAfterImages} />
                </div>
              )}

              {/* Customer Testimonial */}
              {project.customer_testimonial && (
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center gap-1 mb-4">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                      ))}
                    </div>
                    <blockquote className="text-lg text-gray-700 italic mb-4">
                      "{project.customer_testimonial}"
                    </blockquote>
                    {project.customer_name && (
                      <p className="text-gray-600 font-medium">
                        - {project.customer_name}
                      </p>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Challenges & Solutions */}
              {(project.challenges_faced.length > 0 || project.solutions_provided.length > 0) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-orange-600" />
                      Challenges & Solutions
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {project.challenges_faced.length > 0 && (
                      <div>
                        <h4 className="font-medium text-red-700 mb-2">Challenges</h4>
                        <ul className="space-y-1">
                          {project.challenges_faced.map((challenge, index) => (
                            <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                              <AlertTriangle className="w-3 h-3 text-red-500 mt-0.5 flex-shrink-0" />
                              {challenge}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {project.solutions_provided.length > 0 && (
                      <div>
                        <h4 className="font-medium text-green-700 mb-2">Solutions</h4>
                        <ul className="space-y-1">
                          {project.solutions_provided.map((solution, index) => (
                            <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                              <CheckCircle className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                              {solution}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Equipment Installed */}
              {project.equipment_installed.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Wrench className="w-5 h-5 text-blue-600" />
                      Equipment Installed
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {project.equipment_installed.map((equipment, index) => (
                        <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                          <CheckCircle className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                          {equipment}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Warranty Info */}
              {project.warranty_info && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="w-5 h-5 text-green-600" />
                      Warranty Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">{project.warranty_info}</p>
                  </CardContent>
                </Card>
              )}

              {/* Project Tags */}
              {project.tags.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Project Tags</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {project.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        )}

        {activeTab === 'gallery' && (
          <div className="space-y-6">
            {/* Before/After Gallery */}
            {beforeAfterImages.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold mb-4">Before & After Comparison</h3>
                <BeforeAfterGallery images={beforeAfterImages} showThumbnails={true} />
              </div>
            )}

            {/* Additional Gallery Images */}
            {project.gallery_images.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold mb-4">Project Gallery</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {project.gallery_images.map((image, index) => (
                    <div key={index} className="relative aspect-video rounded-lg overflow-hidden">
                      <Image
                        src={image}
                        alt={`${project.title} - Gallery ${index + 1}`}
                        fill
                        className="object-cover hover:scale-105 transition-transform duration-300"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'details' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card>
              <CardHeader>
                <CardTitle>Project Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Trade</p>
                    <p className="font-medium">{project.trade}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Category</p>
                    <p className="font-medium">{project.service_category}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Location</p>
                    <p className="font-medium">{project.location}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Duration</p>
                    <p className="font-medium">{project.project_duration}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Completed</p>
                    <p className="font-medium">{formatDate(project.completion_date)}</p>
                  </div>
                  {project.project_value && (
                    <div>
                      <p className="text-gray-600">Project Value</p>
                      <p className="font-medium">{formatCurrency(project.project_value)}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Project Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">{project.description}</p>
                
                {project.tags.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm text-gray-600 mb-2">Tags:</p>
                    <div className="flex flex-wrap gap-2">
                      {project.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
