/**
 * Project Showcase Component - SSR Optimized
 * 
 * Displays real project portfolio with:
 * - Actual project photos and details
 * - Technician attribution
 * - Project outcomes and value
 * - Customer testimonials integration
 * 
 * This is a server-side component for optimal SEO and performance.
 */

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { ProjectShowcase as ProjectType, TechnicianProfile, BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';
import { ABTestVariant } from '@/components/client/testing/ABTestVariant';

interface ProjectShowcaseProps {
  projects: ProjectType[];
  technicians: TechnicianProfile[];
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  testKey?: string;
  maxProjects?: number;
  showTechnicians?: boolean;
  showMetrics?: boolean;
  className?: string;
}

export function ProjectShowcase({ 
  projects, 
  technicians, 
  businessContext,
  tradeConfig,
  testKey = 'projects',
  maxProjects = 6,
  showTechnicians = true,
  showMetrics = true,
  className = '' 
}: ProjectShowcaseProps) {
  
  // Filter and sort projects
  const displayProjects = projects
    .filter(project => project.images.length > 0 || project.value > 0)
    .sort((a, b) => b.value - a.value)
    .slice(0, maxProjects);
  
  if (displayProjects.length === 0) {
    return null;
  }
  
  return (
    <ABTestVariant testKey={testKey} fallback={
      <DefaultProjectShowcase 
        projects={displayProjects}
        businessContext={businessContext}
        tradeConfig={tradeConfig}
        className={className}
      />
    }>
      <section className={`py-16 bg-white ${className}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Section Header */}
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Our Recent {tradeConfig.display_name} Projects
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See the quality work our {businessContext.technicians.length} expert technicians 
              deliver for customers throughout {businessContext.primary_area?.city || 'our service area'}
            </p>
            
            {showMetrics && (
              <div className="flex justify-center space-x-8 mt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {businessContext.completed_count}+
                  </div>
                  <div className="text-sm text-gray-600">Projects Completed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    ${Math.round(businessContext.average_project_value).toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Average Project Value</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {businessContext.average_rating.toFixed(1)}★
                  </div>
                  <div className="text-sm text-gray-600">Customer Rating</div>
                </div>
              </div>
            )}
          </div>
          
          {/* Projects Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            {displayProjects.map((project, index) => (
              <ProjectCard 
                key={project.id}
                project={project}
                technicians={technicians}
                tradeConfig={tradeConfig}
                showTechnicians={showTechnicians}
                priority={index < 3} // Prioritize first 3 images
              />
            ))}
          </div>
          
          {/* Bottom CTA */}
          <div className="text-center">
            <div className="bg-gray-50 rounded-lg p-8 max-w-2xl mx-auto">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Ready for Your Next Project?
              </h3>
              <p className="text-gray-600 mb-6">
                Join {businessContext.total_served}+ satisfied customers who trust {businessContext.business.name} 
                for their {tradeConfig.display_name.toLowerCase()} needs
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
                  🚨 Emergency service available 24/7 - No overtime charges!
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
 * Individual Project Card Component
 */
function ProjectCard({ 
  project, 
  technicians, 
  tradeConfig,
  showTechnicians,
  priority = false 
}: {
  project: ProjectType;
  technicians: TechnicianProfile[];
  tradeConfig: TradeConfiguration;
  showTechnicians: boolean;
  priority?: boolean;
}) {
  
  // Find the technician for this project
  const technician = technicians.find(t => t.id === project.technician_id);
  
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
      
      {/* Project Image */}
      <div className="relative h-48 bg-gray-200">
        {project.images.length > 0 ? (
          <Image
            src={project.images[0]}
            alt={project.title}
            fill
            className="object-cover"
            priority={priority}
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
        ) : (
          <div className="flex items-center justify-center h-full bg-gradient-to-br from-gray-100 to-gray-200">
            <div className="text-center">
              <div className="text-4xl mb-2">🔧</div>
              <div className="text-gray-600 font-medium">
                {project.category.toUpperCase()}
              </div>
            </div>
          </div>
        )}
        
        {/* Project Category Badge */}
        <div className="absolute top-4 left-4">
          <span 
            className="px-3 py-1 text-xs font-medium text-white rounded-full"
            style={{ backgroundColor: tradeConfig.colors.primary }}
          >
            {project.category}
          </span>
        </div>
        
        {/* Project Value Badge */}
        {project.value > 0 && (
          <div className="absolute top-4 right-4">
            <span className="px-3 py-1 text-xs font-medium bg-green-600 text-white rounded-full">
              ${project.value.toLocaleString()}
            </span>
          </div>
        )}
      </div>
      
      {/* Project Details */}
      <div className="p-6">
        
        {/* Title and Location */}
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {project.title}
          </h3>
          <p className="text-sm text-gray-600">
            📍 {project.location}
          </p>
        </div>
        
        {/* Description */}
        <p className="text-gray-700 text-sm mb-4 line-clamp-3">
          {project.description || project.solution_implemented}
        </p>
        
        {/* Project Metrics */}
        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
          {project.duration && (
            <div>
              <span className="text-gray-600">Duration:</span>
              <div className="font-medium">{project.duration}</div>
            </div>
          )}
          
          {project.customer_savings && (
            <div>
              <span className="text-gray-600">Savings:</span>
              <div className="font-medium text-green-600">
                ${project.customer_savings.toLocaleString()}
              </div>
            </div>
          )}
          
          {project.efficiency_improvement && (
            <div className="col-span-2">
              <span className="text-gray-600">Improvement:</span>
              <div className="font-medium text-blue-600">
                {project.efficiency_improvement}
              </div>
            </div>
          )}
        </div>
        
        {/* Technician Attribution */}
        {showTechnicians && technician && (
          <div className="flex items-center pt-4 border-t border-gray-200">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
              <span className="text-blue-600 font-semibold text-sm">
                {technician.name.split(' ').map(n => n[0]).join('')}
              </span>
            </div>
            <div>
              <div className="font-medium text-gray-900 text-sm">
                {technician.name}
              </div>
              <div className="text-xs text-gray-600">
                {technician.title} • {technician.years_experience} years experience
              </div>
            </div>
          </div>
        )}
        
        {/* Customer Feedback */}
        {project.customer_feedback && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-700 italic">
              "{project.customer_feedback}"
            </p>
          </div>
        )}
        
      </div>
    </div>
  );
}

/**
 * Default project showcase (fallback)
 */
function DefaultProjectShowcase({ 
  projects, 
  businessContext, 
  tradeConfig,
  className 
}: {
  projects: ProjectType[];
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  className: string;
}) {
  return (
    <section className={`py-16 bg-gray-50 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Our Work Speaks for Itself
          </h2>
          <p className="text-xl text-gray-600">
            {businessContext.completed_count}+ successful projects completed
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {projects.slice(0, 3).map((project) => (
            <div key={project.id} className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-2">{project.title}</h3>
              <p className="text-gray-600 mb-4">{project.location}</p>
              <div className="text-sm text-gray-700">
                <strong>Value:</strong> ${project.value.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
