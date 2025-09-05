/**
 * Testimonial Section Component - SSR Optimized
 * 
 * Displays authentic customer testimonials with:
 * - Real customer reviews and ratings
 * - Project context and outcomes
 * - Technician attribution
 * - Service-specific testimonials
 * - Trust indicators and social proof
 * 
 * This is a server-side component for optimal SEO and trust building.
 */

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Testimonial, ProjectShowcase, TechnicianProfile, BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';
import { ABTestVariant } from '@/components/client/testing/ABTestVariant';

interface TestimonialSectionProps {
  testimonials: Testimonial[];
  projects: ProjectShowcase[];
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  testKey?: string;
  maxTestimonials?: number;
  showProjects?: boolean;
  showTechnicians?: boolean;
  showRatings?: boolean;
  className?: string;
}

interface EnrichedTestimonial extends Testimonial {
  project?: ProjectShowcase;
  technician?: TechnicianProfile;
  service_name?: string;
}

export function TestimonialSection({ 
  testimonials, 
  projects,
  businessContext,
  tradeConfig,
  testKey = 'testimonials',
  maxTestimonials = 6,
  showProjects = true,
  showTechnicians = true,
  showRatings = true,
  className = '' 
}: TestimonialSectionProps) {
  
  // Enrich testimonials with project and technician data
  const enrichedTestimonials = enrichTestimonials(
    testimonials, 
    projects, 
    businessContext.technicians
  ).slice(0, maxTestimonials);
  
  if (enrichedTestimonials.length === 0) {
    return null;
  }
  
  // Calculate aggregate ratings
  const averageRating = businessContext.average_rating;
  const totalReviews = businessContext.total_served;
  const ratingDistribution = calculateRatingDistribution(testimonials);
  
  return (
    <ABTestVariant testKey={testKey} fallback={
      <DefaultTestimonialSection 
        testimonials={enrichedTestimonials}
        businessContext={businessContext}
        tradeConfig={tradeConfig}
        className={className}
      />
    }>
      <section className={`py-16 bg-gray-50 ${className}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Section Header */}
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              What Our Customers Say About Our {tradeConfig.display_name} Services
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-6">
              Real reviews from real customers who trust {businessContext.business.name} 
              for their {tradeConfig.display_name.toLowerCase()} needs
            </p>
            
            {/* Aggregate Rating Display */}
            {showRatings && (
              <div className="flex items-center justify-center space-x-8 mb-8">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <div className="text-3xl font-bold text-yellow-500 mr-2">
                      {averageRating.toFixed(1)}
                    </div>
                    <div className="flex">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <svg
                          key={star}
                          className={`w-6 h-6 ${
                            star <= Math.round(averageRating) 
                              ? 'text-yellow-400' 
                              : 'text-gray-300'
                          }`}
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      ))}
                    </div>
                  </div>
                  <div className="text-sm text-gray-600">
                    Based on {totalReviews}+ reviews
                  </div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {Math.round(businessContext.repeat_customer_rate * 100)}%
                  </div>
                  <div className="text-sm text-gray-600">
                    Repeat Customers
                  </div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {businessContext.completed_count}+
                  </div>
                  <div className="text-sm text-gray-600">
                    Projects Completed
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Testimonials Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            {enrichedTestimonials.map((testimonial, index) => (
              <TestimonialCard 
                key={testimonial.id}
                testimonial={testimonial}
                tradeConfig={tradeConfig}
                showProjects={showProjects}
                showTechnicians={showTechnicians}
                priority={index < 3} // Prioritize first 3 for performance
              />
            ))}
          </div>
          
          {/* Rating Distribution */}
          {showRatings && ratingDistribution && (
            <div className="bg-white rounded-lg shadow-lg p-8 mb-12 max-w-2xl mx-auto">
              <h3 className="text-xl font-semibold text-gray-900 mb-6 text-center">
                Customer Rating Breakdown
              </h3>
              
              <div className="space-y-3">
                {[5, 4, 3, 2, 1].map((rating) => (
                  <div key={rating} className="flex items-center">
                    <div className="flex items-center w-20">
                      <span className="text-sm font-medium text-gray-700 mr-2">
                        {rating}
                      </span>
                      <svg className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    </div>
                    
                    <div className="flex-1 mx-4">
                      <div className="bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-yellow-400 h-2 rounded-full"
                          style={{ 
                            width: `${(ratingDistribution[rating] || 0) * 100}%` 
                          }}
                        ></div>
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-600 w-12 text-right">
                      {Math.round((ratingDistribution[rating] || 0) * 100)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Bottom CTA */}
          <div className="text-center">
            <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Join Our Satisfied Customers
              </h3>
              <p className="text-gray-600 mb-6">
                Experience the quality {tradeConfig.display_name.toLowerCase()} service 
                that {totalReviews}+ customers recommend
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a 
                  href={`tel:${businessContext.business.phone}`}
                  className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <span className="mr-2">📞</span>
                  Call {businessContext.business.phone}
                </a>
                
                <Link 
                  href="/booking"
                  className="inline-flex items-center justify-center px-6 py-3 bg-gray-100 text-gray-900 font-semibold rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <span className="mr-2">📅</span>
                  Get Free Estimate
                </Link>
              </div>
              
              {tradeConfig.emergency_services && (
                <p className="mt-4 text-sm text-red-600 font-medium">
                  🚨 Emergency service available 24/7 - Join our satisfied customers today!
                </p>
              )}
            </div>
          </div>
          
        </div>
      </section>
    </ABTestVariant>
  );
}

/**
 * Individual Testimonial Card Component
 */
function TestimonialCard({ 
  testimonial, 
  tradeConfig,
  showProjects,
  showTechnicians,
  priority = false 
}: {
  testimonial: EnrichedTestimonial;
  tradeConfig: TradeConfiguration;
  showProjects: boolean;
  showTechnicians: boolean;
  priority?: boolean;
}) {
  
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
      
      {/* Rating Stars */}
      <div className="flex items-center mb-4">
        <div className="flex mr-2">
          {[1, 2, 3, 4, 5].map((star) => (
            <svg
              key={star}
              className={`w-5 h-5 ${
                star <= testimonial.rating 
                  ? 'text-yellow-400' 
                  : 'text-gray-300'
              }`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          ))}
        </div>
        <span className="text-sm text-gray-600">
          {testimonial.rating}/5 stars
        </span>
      </div>
      
      {/* Testimonial Text */}
      <blockquote className="text-gray-700 mb-6 italic">
        "{testimonial.text}"
      </blockquote>
      
      {/* Customer Information */}
      <div className="border-t pt-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="font-semibold text-gray-900">
              {testimonial.customer_name}
            </div>
            <div className="text-sm text-gray-600">
              📍 {testimonial.customer_location}
            </div>
          </div>
          
          {/* Service Badge */}
          {testimonial.service_name && (
            <span 
              className="px-3 py-1 text-xs font-medium text-white rounded-full"
              style={{ backgroundColor: tradeConfig.colors.primary }}
            >
              {testimonial.service_name}
            </span>
          )}
        </div>
        
        {/* Project Context */}
        {showProjects && testimonial.project && (
          <div className="bg-gray-50 rounded-lg p-3 mb-3">
            <div className="text-sm font-medium text-gray-900 mb-1">
              Project: {testimonial.project.title}
            </div>
            <div className="text-xs text-gray-600">
              Value: ${testimonial.project.value.toLocaleString()} • 
              Duration: {testimonial.project.duration}
            </div>
          </div>
        )}
        
        {/* Technician Attribution */}
        {showTechnicians && testimonial.technician && (
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
              <span className="text-blue-600 font-semibold text-sm">
                {testimonial.technician.name.split(' ').map(n => n[0]).join('')}
              </span>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-900">
                Served by {testimonial.technician.name}
              </div>
              <div className="text-xs text-gray-600">
                {testimonial.technician.title} • {testimonial.technician.years_experience} years experience
              </div>
            </div>
          </div>
        )}
        
        {/* Date */}
        <div className="text-xs text-gray-500 mt-3">
          {new Date(testimonial.date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </div>
      </div>
      
    </div>
  );
}

/**
 * Default testimonial section (fallback)
 */
function DefaultTestimonialSection({ 
  testimonials, 
  businessContext, 
  tradeConfig,
  className 
}: {
  testimonials: EnrichedTestimonial[];
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  className: string;
}) {
  return (
    <section className={`py-16 bg-gray-50 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Customer Reviews
          </h2>
          <p className="text-xl text-gray-600">
            {businessContext.average_rating.toFixed(1)} stars from {businessContext.total_served}+ customers
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {testimonials.slice(0, 3).map((testimonial) => (
            <div key={testimonial.id} className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex mb-4">
                {[1, 2, 3, 4, 5].map((star) => (
                  <svg
                    key={star}
                    className={`w-5 h-5 ${
                      star <= testimonial.rating ? 'text-yellow-400' : 'text-gray-300'
                    }`}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>
              <blockquote className="text-gray-700 mb-4 italic">
                "{testimonial.text}"
              </blockquote>
              <div className="font-semibold text-gray-900">
                {testimonial.customer_name}
              </div>
              <div className="text-sm text-gray-600">
                {testimonial.customer_location}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/**
 * Enrich testimonials with project and technician data
 */
function enrichTestimonials(
  testimonials: Testimonial[],
  projects: ProjectShowcase[],
  technicians: TechnicianProfile[]
): EnrichedTestimonial[] {
  
  return testimonials.map(testimonial => {
    // Find related project
    const project = projects.find(p => p.id === testimonial.project_id);
    
    // Find technician
    const technician = technicians.find(t => t.id === testimonial.technician_id);
    
    // Determine service name (could be enhanced with service lookup)
    const service_name = project?.category || 'Service';
    
    return {
      ...testimonial,
      project,
      technician,
      service_name
    };
  });
}

/**
 * Calculate rating distribution for display
 */
function calculateRatingDistribution(testimonials: Testimonial[]): Record<number, number> {
  if (testimonials.length === 0) return {};
  
  const distribution: Record<number, number> = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  
  testimonials.forEach(testimonial => {
    const rating = Math.round(testimonial.rating);
    if (rating >= 1 && rating <= 5) {
      distribution[rating]++;
    }
  });
  
  // Convert to percentages
  const total = testimonials.length;
  Object.keys(distribution).forEach(rating => {
    distribution[parseInt(rating)] = distribution[parseInt(rating)] / total;
  });
  
  return distribution;
}
