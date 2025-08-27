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

interface ProjectCategory {
  id: string;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
  project_count: number;
  display_order: number;
}

interface ProjectTag {
  id: string;
  name: string;
  slug: string;
  color: string;
  usage_count: number;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<FeaturedProject[]>([]);
  const [categories, setCategories] = useState<ProjectCategory[]>([]);
  const [tags, setTags] = useState<ProjectTag[]>([]);
  const [loading, setLoading] = useState(true);
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

  // Get business ID from configuration
  const businessId = getCurrentBusinessId();

  useEffect(() => {
    fetchProjects();
    fetchCategories();
    fetchTags();
  }, [selectedTrade, selectedCategory, selectedTag, sortBy, currentPage]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const params = new URLSearchParams({
        limit: projectsPerPage.toString(),
        offset: ((currentPage - 1) * projectsPerPage).toString()
      });
      
      if (selectedTrade !== 'all') {
        params.append('trade', selectedTrade);
      }
      if (selectedCategory !== 'all') {
        params.append('category', selectedCategory);
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
      
      if (currentPage === 1) {
        setProjects(data);
      } else {
        setProjects(prev => [...prev, ...data]);
      }
      
      setHasMore(data.length === projectsPerPage);
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(
        `${backendUrl}/api/v1/public/contractors/project-categories/${businessId}`,
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      }
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  };

  const fetchTags = async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(
        `${backendUrl}/api/v1/public/contractors/project-tags/${businessId}`,
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setTags(data);
      }
    } catch (err) {
      console.error('Error fetching tags:', err);
    }
  };

  const handleFilterChange = () => {
    setCurrentPage(1);
    setProjects([]);
  };

  const loadMore = () => {
    setCurrentPage(prev => prev + 1);
  };

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

  // Filter projects based on search query
  const filteredProjects = projects.filter(project => {
    const matchesSearch = searchQuery === '' || 
      project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.location.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesTag = selectedTag === 'all' || project.tags.includes(selectedTag);
    
    return matchesSearch && matchesTag;
  });

  // Get unique trades from projects
  const trades = Array.from(new Set(projects.map(p => p.trade)));

  return (
    <CartProvider businessId={businessId}>
      <BookingWidgetProvider
        businessId={businessId}
        companyName="Austin Elite Home Services"
        companyPhone="(512) 555-0123"
        companyEmail="info@austinelitehome.com"
        services={[]}
      >
      <div className="min-h-screen bg-white">
        {/* Header */}
        <EliteHeader 
          businessName="Austin Elite Home Services"
          city="Austin"
          state="TX"
          phone="(512) 555-0123"
          supportHours="24/7"
        />
        
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
              {/* Search and View Toggle */}
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

              {/* Filter Controls */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Select value={selectedTrade} onValueChange={(value) => {
                  setSelectedTrade(value);
                  handleFilterChange();
                }}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Trades" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Trades</SelectItem>
                    {trades.map(trade => (
                      <SelectItem key={trade} value={trade}>{trade}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select value={selectedCategory} onValueChange={(value) => {
                  setSelectedCategory(value);
                  handleFilterChange();
                }}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {categories.map(category => (
                      <SelectItem key={category.id} value={category.name}>
                        {category.name} ({category.project_count})
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
                    {tags.map(tag => (
                      <SelectItem key={tag.id} value={tag.name}>
                        {tag.name} ({tag.usage_count})
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
                  </SelectContent>
                </Select>
              </div>

              {/* Active Filters */}
              <div className="flex flex-wrap gap-2">
                {selectedTrade !== 'all' && (
                  <Badge variant="secondary" className="cursor-pointer" onClick={() => {
                    setSelectedTrade('all');
                    handleFilterChange();
                  }}>
                    Trade: {selectedTrade} ×
                  </Badge>
                )}
                {selectedCategory !== 'all' && (
                  <Badge variant="secondary" className="cursor-pointer" onClick={() => {
                    setSelectedCategory('all');
                    handleFilterChange();
                  }}>
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
            Showing {filteredProjects.length} project{filteredProjects.length !== 1 ? 's' : ''}
          </p>
        </div>

        {/* Projects Grid/List */}
        {loading && projects.length === 0 ? (
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
        ) : filteredProjects.length === 0 ? (
          <div className="text-center py-12">
            <Filter className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
            <p className="text-gray-600">Try adjusting your filters or search terms</p>
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" 
            : "space-y-6"
          }>
            {filteredProjects.map((project) => (
              <Card key={project.id} className={`group overflow-hidden hover:shadow-xl transition-all duration-300 ${
                viewMode === 'list' ? 'flex' : ''
              }`}>
                <div className={`relative ${viewMode === 'list' ? 'w-80 flex-shrink-0' : ''}`}>
                  {/* Project Image */}
                  <div className={`relative overflow-hidden ${viewMode === 'list' ? 'h-full' : 'h-64'}`}>
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
                </div>

                <CardContent className="p-6 flex-1">
                  {/* Project Title & Category */}
                  <div className="space-y-2 mb-4">
                    <h3 className="text-xl font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                      {project.title}
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="outline" className="text-xs">
                        {project.service_category}
                      </Badge>
                      <Badge variant="secondary" className="text-xs">
                        {project.trade}
                      </Badge>
                    </div>
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
                  {project.customer_testimonial && viewMode === 'list' && (
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
              </Card>
            ))}
          </div>
        )}

        {/* Load More Button */}
        {hasMore && !loading && filteredProjects.length > 0 && (
          <div className="text-center mt-8">
            <Button onClick={loadMore} variant="outline" size="lg">
              Load More Projects
            </Button>
          </div>
        )}

        {/* Loading More */}
        {loading && projects.length > 0 && (
          <div className="text-center mt-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        )}
      </div>
      </div>

      {/* Footer */}
      <ProfessionalFooter 
        business={{
          id: businessId,
          name: "Austin Elite Home Services",
          phone_number: "(512) 555-0123",
          business_email: "info@austinelitehome.com",
          address: "123 Main St, Austin, TX 78701",
          website: "https://austinelitehome.com",
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
}
