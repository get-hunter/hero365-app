/**
 * Trade-Aware Hero Component - SSR Optimized
 * 
 * Generates personalized hero sections using real business data:
 * - Team size and experience
 * - Actual project count
 * - Real customer ratings
 * - Trade-specific messaging
 * - Emergency service availability
 */

import React from 'react';
import { ActivityPageArtifact } from '@/lib/shared/types/seo-artifacts';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';
import { ABTestVariant } from '@/components/client/testing/ABTestVariant';

interface TradeAwareHeroProps {
  artifact: ActivityPageArtifact;
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  testKey?: string;
  className?: string;
}

export function TradeAwareHero({ 
  artifact, 
  businessContext, 
  tradeConfig,
  testKey = 'hero',
  className = '' 
}: TradeAwareHeroProps) {
  
  // Generate dynamic content based on real business data
  const heroContent = generateHeroContent(artifact, businessContext, tradeConfig);
  
  return (
    <ABTestVariant testKey={testKey} fallback={
      <DefaultHeroContent 
        heroContent={heroContent}
        businessContext={businessContext}
        tradeConfig={tradeConfig}
        className={className}
      />
    }>
      <section className={`relative overflow-hidden ${className}`}>
        {/* Background with trade-specific gradient */}
        <div 
          className="absolute inset-0 bg-gradient-to-br opacity-90"
          style={{
            background: `linear-gradient(135deg, ${tradeConfig.colors.primary} 0%, ${tradeConfig.colors.secondary} 100%)`
          }}
        />
        
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-10">
          <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs>
              <pattern id="hero-pattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                <circle cx="10" cy="10" r="1" fill="white" />
              </pattern>
            </defs>
            <rect width="100" height="100" fill="url(#hero-pattern)" />
          </svg>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            
            {/* Content Column */}
            <div className="text-white">
              
              {/* Emergency Banner */}
              {tradeConfig.emergency_services && (
                <div className="inline-flex items-center px-4 py-2 rounded-full bg-red-600 text-white text-sm font-medium mb-6 animate-pulse">
                  <span className="mr-2">🚨</span>
                  24/7 Emergency Service Available - No Overtime Charges!
                </div>
              )}
              
              {/* Main Headline */}
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6">
                {heroContent.headline}
              </h1>
              
              {/* Subheadline */}
              <p className="text-xl md:text-2xl text-blue-100 mb-8 leading-relaxed">
                {heroContent.subheadline}
              </p>
              
              {/* Trust Indicators with Real Data */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                
                {/* Team Size */}
                {businessContext.technicians.length > 0 && (
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white">
                      {businessContext.technicians.length}
                    </div>
                    <div className="text-blue-200 text-sm">
                      Expert Technicians
                    </div>
                  </div>
                )}
                
                {/* Combined Experience */}
                {businessContext.combined_experience_years > 0 && (
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white">
                      {businessContext.combined_experience_years}+
                    </div>
                    <div className="text-blue-200 text-sm">
                      Years Experience
                    </div>
                  </div>
                )}
                
                {/* Projects Completed */}
                {businessContext.completed_count > 0 && (
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white">
                      {businessContext.completed_count}+
                    </div>
                    <div className="text-blue-200 text-sm">
                      Projects Completed
                    </div>
                  </div>
                )}
                
                {/* Customer Rating */}
                <div className="text-center">
                  <div className="text-3xl font-bold text-white">
                    {businessContext.average_rating.toFixed(1)}★
                  </div>
                  <div className="text-blue-200 text-sm">
                    Customer Rating
                  </div>
                </div>
                
              </div>
              
              {/* Certifications */}
              {businessContext.total_certifications.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-8">
                  {businessContext.total_certifications.slice(0, 4).map((cert, index) => (
                    <span 
                      key={index}
                      className="px-3 py-1 bg-white bg-opacity-20 rounded-full text-sm text-white"
                    >
                      ✓ {cert}
                    </span>
                  ))}
                </div>
              )}
              
              {/* Call-to-Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4">
                <a 
                  href={`tel:${businessContext.business.phone}`}
                  className="inline-flex items-center justify-center px-8 py-4 bg-white text-blue-600 font-bold rounded-lg hover:bg-gray-100 transition-colors shadow-lg"
                >
                  <span className="mr-2">📞</span>
                  Call {businessContext.business.phone}
                </a>
                
                <a 
                  href="/booking"
                  className="inline-flex items-center justify-center px-8 py-4 bg-blue-700 text-white font-bold rounded-lg hover:bg-blue-800 transition-colors border-2 border-blue-500"
                >
                  <span className="mr-2">📅</span>
                  Schedule Service
                </a>
              </div>
              
              {/* Response Time */}
              {businessContext.primary_area?.response_time_hours && (
                <p className="mt-6 text-blue-200">
                  ⚡ Average response time: {businessContext.primary_area.response_time_hours} hours
                </p>
              )}
              
            </div>
            
            {/* Visual Column */}
            <div className="relative">
              
              {/* Featured Project Images */}
              {businessContext.showcase_projects.length > 0 && (
                <div className="grid grid-cols-2 gap-4">
                  {businessContext.showcase_projects.slice(0, 4).map((project, index) => (
                    <div 
                      key={project.id}
                      className={`relative rounded-lg overflow-hidden shadow-lg ${
                        index === 0 ? 'col-span-2' : ''
                      }`}
                    >
                      {project.images.length > 0 ? (
                        <img 
                          src={project.images[0]}
                          alt={project.title}
                          className="w-full h-48 object-cover"
                        />
                      ) : (
                        <div className="w-full h-48 bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center">
                          <span className="text-gray-500 font-medium">
                            {project.category.toUpperCase()}
                          </span>
                        </div>
                      )}
                      
                      <div className="absolute inset-0 bg-black bg-opacity-40 flex items-end">
                        <div className="p-4 text-white">
                          <h3 className="font-semibold text-sm">{project.title}</h3>
                          <p className="text-xs text-gray-200">
                            By {project.technician_name}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {/* Technician Showcase */}
              {businessContext.technicians.length > 0 && businessContext.showcase_projects.length === 0 && (
                <div className="bg-white bg-opacity-10 rounded-lg p-6 backdrop-blur-sm">
                  <h3 className="text-white font-bold text-lg mb-4">Our Expert Team</h3>
                  <div className="space-y-3">
                    {businessContext.technicians.slice(0, 3).map((tech) => (
                      <div key={tech.id} className="flex items-center text-white">
                        <div className="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-3">
                          <span className="font-bold">
                            {tech.name.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                        <div>
                          <div className="font-medium">{tech.name}</div>
                          <div className="text-sm text-blue-200">
                            {tech.title} • {tech.years_experience} years
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
            </div>
            
          </div>
        </div>
        
        {/* Bottom Wave */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1200 120" className="w-full h-12 fill-white">
            <path d="M0,60 C300,120 900,0 1200,60 L1200,120 L0,120 Z" />
          </svg>
        </div>
        
      </section>
    </ABTestVariant>
  );
}

/**
 * Default hero content component
 */
function DefaultHeroContent({ 
  heroContent, 
  businessContext, 
  tradeConfig,
  className 
}: {
  heroContent: any;
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  className: string;
}) {
  return (
    <section className={`bg-gradient-to-r from-blue-600 to-blue-800 text-white py-20 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            {heroContent.headline}
          </h1>
          <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto">
            {heroContent.subheadline}
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href={`tel:${businessContext.business.phone}`}
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Call Now
            </a>
            <a 
              href="/booking"
              className="bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-800 transition-colors border border-blue-500"
            >
              Schedule Service
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

/**
 * Generate hero content based on business context
 */
function generateHeroContent(
  artifact: ActivityPageArtifact,
  businessContext: BusinessContext,
  tradeConfig: TradeConfiguration
) {
  const city = businessContext.primary_area?.city || businessContext.business.city || 'Your Area';
  const businessName = businessContext.business.name;
  const teamSize = businessContext.technicians.length;
  const experience = businessContext.combined_experience_years;
  const projectCount = businessContext.completed_count;
  
  // Generate dynamic headline
  let headline = tradeConfig.hero.headline_template
    .replace('{city}', city)
    .replace('{business_name}', businessName);
  
  // Enhance with real data
  if (teamSize > 0) {
    headline = `${city}'s ${teamSize}-Person Expert ${tradeConfig.display_name} Team`;
  }
  
  // Generate dynamic subheadline
  const subheadlinePoints = [
    ...tradeConfig.hero.subtitle_points
  ];
  
  // Add real data points
  if (experience > 0) {
    subheadlinePoints.unshift(`${experience}+ Years Combined Experience`);
  }
  
  if (projectCount > 0) {
    subheadlinePoints.push(`${projectCount}+ Successful Projects`);
  }
  
  const subheadline = subheadlinePoints.slice(0, 3).join(' • ');
  
  return {
    headline,
    subheadline,
    emergency_message: tradeConfig.hero.emergency_message,
    primary_cta: tradeConfig.hero.primary_cta,
    secondary_cta: tradeConfig.hero.secondary_cta
  };
}
