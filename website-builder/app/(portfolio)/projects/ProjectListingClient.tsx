'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar, MapPin, Clock, Star, Search, Filter, Grid, List, ArrowRight } from 'lucide-react';
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
  slug: string;
  tags: string[];
  display_order: number;
}

interface ProjectCategory {
  id: string;
  name: string;
  slug: string;
  description?: string;
  project_count: number;
}

interface ProjectTag {
  id: string;
  name: string;
  slug: string;
  color: string;
  usage_count: number;
}

interface ProjectListingClientProps {
  projects: FeaturedProject[];
  categories: ProjectCategory[];
  tags: ProjectTag[];
  businessId: string;
  hasRealData?: boolean;
}

export default function ProjectListingClient({
  projects: initialProjects,
  categories,
  tags,
  businessId,
  hasRealData = false
}: ProjectListingClientProps) {
  const [projects, setProjects] = useState<FeaturedProject[]>(initialProjects);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTrade, setSelectedTrade] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedTag, setSelectedTag] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('recent');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const projectsPerPage = 12;

  // Filter projects based on search and filters
  const filteredProjects = projects.filter(project => {
    const matchesSearch = searchQuery === '' || 
      project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.location.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesTrade = selectedTrade === 'all' || project.trade === selectedTrade;
    const matchesCategory = selectedCategory === 'all' || project.service_category === selectedCategory;
    const matchesTag = selectedTag === 'all' || project.tags.includes(selectedTag);
    
    return matchesSearch && matchesTrade && matchesCategory && matchesTag;
  });

  // Sort projects
  const sortedProjects = [...filteredProjects].sort((a, b) => {
    switch (sortBy) {
      case 'recent':
        return new Date(b.completion_date).getTime() - new Date(a.completion_date).getTime();
      case 'oldest':
        return new Date(a.completion_date).getTime() - new Date(b.completion_date).getTime();
      case 'value-high':
        return (b.project_value || 0) - (a.project_value || 0);
      case 'value-low':
        return (a.project_value || 0) - (b.project_value || 0);
      case 'alphabetical':
        return a.title.localeCompare(b.title);
      default:
        return a.display_order - b.display_order;
    }
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getUniqueValues = (key: keyof FeaturedProject) => {
    return [...new Set(projects.map(project => project[key]))].filter(Boolean);
  };

  if (!hasRealData) {
    return (
      <div className="bg-gray-50">
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center space-y-4">
              <h1 className="text-4xl font-bold text-gray-900">Our Project Portfolio</h1>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Explore our completed projects and see the quality craftsmanship we deliver
              </p>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-16">
            <div className="animate-pulse space-y-4">
              <div className="h-8 bg-gray-200 rounded w-1/3 mx-auto"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
            </div>
            <p className="text-gray-500 mt-8">Loading projects...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold text-gray-900">Our Project Portfolio</h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Explore our completed projects and see the quality craftsmanship we deliver
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="space-y-4">
              {/* Search and View Controls */}
              <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
                <div className="relative flex-1 max-w-md">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    placeholder="Search projects..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant={viewMode === 'grid' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('grid')}
                  >
                    <Grid className="w-4 h-4" />
                  </Button>
                  <Button
                    variant={viewMode === 'list' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('list')}
                  >
                    <List className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Filter Dropdowns */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Select value={selectedTrade} onValueChange={setSelectedTrade}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Trades" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Trades</SelectItem>
                    {getUniqueValues('trade').map((trade, index) => (
                      <SelectItem key={`trade-${index}`} value={trade as string}>
                        {trade}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.name}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select value={selectedTag} onValueChange={setSelectedTag}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Tags" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Tags</SelectItem>
                    {tags.map((tag) => (
                      <SelectItem key={tag.id} value={tag.name}>
                        {tag.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="recent">Most Recent</SelectItem>
                    <SelectItem value="oldest">Oldest First</SelectItem>
                    <SelectItem value="value-high">Highest Value</SelectItem>
                    <SelectItem value="value-low">Lowest Value</SelectItem>
                    <SelectItem value="alphabetical">Alphabetical</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Active Filters */}
              <div className="flex flex-wrap gap-2">
                {searchQuery && (
                  <Badge variant="secondary" className="cursor-pointer" onClick={() => setSearchQuery('')}>
                    Search: {searchQuery} ×
                  </Badge>
                )}
                {selectedTrade !== 'all' && (
                  <Badge variant="secondary" className="cursor-pointer" onClick={() => setSelectedTrade('all')}>
                    Trade: {selectedTrade} ×
                  </Badge>
                )}
                {selectedCategory !== 'all' && (
                  <Badge variant="secondary" className="cursor-pointer" onClick={() => setSelectedCategory('all')}>
                    Category: {selectedCategory} ×
                  </Badge>
                )}
                {selectedTag !== 'all' && (
                  <Badge variant="secondary" className="cursor-pointer" onClick={() => setSelectedTag('all')}>
                    Tag: {selectedTag} ×
                  </Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results Count */}
        <div className="mb-6">
          <p className="text-gray-600">
            Showing {sortedProjects.length} project{sortedProjects.length !== 1 ? 's' : ''}
          </p>
        </div>

        {/* Projects Grid */}
        <div className={`grid gap-6 ${
          viewMode === 'grid' 
            ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' 
            : 'grid-cols-1'
        }`}>
          {sortedProjects.map((project) => (
            <Link key={project.id} href={`/projects/${project.slug}`}>
              <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
                <div className="relative h-64">
                  {project.after_images.length > 0 ? (
                    <Image
                      src={project.after_images[0]}
                      alt={project.title}
                      fill
                      className="object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                      <span className="text-gray-400">No image available</span>
                    </div>
                  )}
                  <div className="absolute top-4 left-4">
                    <Badge>{project.trade}</Badge>
                  </div>
                  {project.project_value && (
                    <div className="absolute top-4 right-4">
                      <Badge variant="secondary">
                        {formatCurrency(project.project_value)}
                      </Badge>
                    </div>
                  )}
                </div>
                <CardContent className="p-6">
                  <div className="space-y-3">
                    <h3 className="text-xl font-semibold text-gray-900 line-clamp-2">
                      {project.title}
                    </h3>
                    <p className="text-gray-600 line-clamp-3">
                      {project.description}
                    </p>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        {project.location}
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {formatDate(project.completion_date)}
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {project.project_duration}
                      </div>
                    </div>

                    {project.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {project.tags.slice(0, 3).map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {project.tags.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{project.tags.length - 3} more
                          </Badge>
                        )}
                      </div>
                    )}

                    {project.customer_testimonial && (
                      <div className="bg-gray-50 p-3 rounded-lg">
                        <div className="flex items-center gap-1 mb-2">
                          {[...Array(5)].map((_, i) => (
                            <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                          ))}
                        </div>
                        <p className="text-sm text-gray-700 line-clamp-2">
                          "{project.customer_testimonial}"
                        </p>
                        {project.customer_name && (
                          <p className="text-xs text-gray-500 mt-1">
                            - {project.customer_name}
                          </p>
                        )}
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-2">
                      <span className="text-sm font-medium text-blue-600">
                        View Project Details
                      </span>
                      <ArrowRight className="w-4 h-4 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        {/* Empty State */}
        {sortedProjects.length === 0 && (
          <div className="text-center py-16">
            <div className="space-y-4">
              <div className="text-gray-400">
                <Search className="w-16 h-16 mx-auto mb-4" />
              </div>
              <h3 className="text-lg font-medium text-gray-900">No projects found</h3>
              <p className="text-gray-600">
                Try adjusting your search criteria or filters to find more projects.
              </p>
              <Button 
                variant="outline" 
                onClick={() => {
                  setSearchQuery('');
                  setSelectedTrade('all');
                  setSelectedCategory('all');
                  setSelectedTag('all');
                }}
              >
                Clear all filters
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
