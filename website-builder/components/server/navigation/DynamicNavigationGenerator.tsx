/**
 * Dynamic Navigation Generator - SSR Component
 * 
 * Generates trade-aware navigation menus based on:
 * - Selected business activities
 * - Service areas and locations
 * - Trade-specific service categories
 * - Emergency service availability
 * 
 * This is a server-side component for optimal SEO and performance.
 */

import React from 'react';
import Link from 'next/link';
import { BusinessContext, ActivityInfo, ServiceArea } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';

interface DynamicNavigationProps {
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  currentPath?: string;
  className?: string;
}

interface NavigationStructure {
  services: {
    featured: ActivityInfo[];
    categories: ServiceCategory[];
    emergency: ActivityInfo[];
    popular: ActivityInfo[];
  };
  locations: {
    primary: ServiceArea;
    additional: ServiceArea[];
    coverage_areas: string[];
  };
  company: {
    about_items: NavItem[];
    resource_items: NavItem[];
  };
}

interface ServiceCategory {
  name: string;
  activities: ActivityInfo[];
  icon?: string;
}

interface NavItem {
  label: string;
  href: string;
  description?: string;
}

export function DynamicNavigationGenerator({ 
  businessContext, 
  tradeConfig,
  currentPath = '',
  className = '' 
}: DynamicNavigationProps) {
  
  // Generate navigation structure
  const navigation = generateNavigationStructure(businessContext, tradeConfig);
  
  return (
    <nav className={`dynamic-navigation ${className}`} role="navigation" aria-label="Main navigation">
      
      {/* Desktop Navigation */}
      <div className="hidden lg:flex lg:items-center lg:space-x-8">
        
        {/* Services Mega Menu */}
        <div className="relative group">
          <button 
            className="flex items-center text-gray-700 hover:text-blue-600 font-medium transition-colors"
            aria-expanded="false"
            aria-haspopup="true"
          >
            Services
            <svg className="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {/* Mega Menu Dropdown */}
          <div className="absolute left-0 mt-2 w-screen max-w-4xl bg-white shadow-xl rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                
                {/* Featured Services */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Featured Services
                  </h3>
                  <ul className="space-y-3">
                    {navigation.services.featured.map((activity) => (
                      <li key={activity.slug}>
                        <Link 
                          href={`/services/${activity.slug}`}
                          className="block p-2 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          <div className="font-medium text-gray-900">
                            {activity.name}
                          </div>
                          <div className="text-sm text-gray-600 mt-1">
                            Professional {activity.name.toLowerCase()} services
                          </div>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
                
                {/* Service Categories */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    {tradeConfig.display_name} Services
                  </h3>
                  <ul className="space-y-3">
                    {navigation.services.categories.map((category) => (
                      <li key={category.name}>
                        <div className="font-medium text-gray-900 mb-2">
                          {category.name}
                        </div>
                        <ul className="ml-4 space-y-1">
                          {category.activities.slice(0, 3).map((activity) => (
                            <li key={activity.slug}>
                              <Link 
                                href={`/services/${activity.slug}`}
                                className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
                              >
                                {activity.name}
                              </Link>
                            </li>
                          ))}
                        </ul>
                      </li>
                    ))}
                  </ul>
                </div>
                
                {/* Emergency & Popular */}
                <div>
                  {/* Emergency Services */}
                  {navigation.services.emergency.length > 0 && (
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold text-red-600 mb-4">
                        🚨 Emergency Services
                      </h3>
                      <ul className="space-y-2">
                        {navigation.services.emergency.map((activity) => (
                          <li key={activity.slug}>
                            <Link 
                              href={`/services/${activity.slug}`}
                              className="block p-2 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                            >
                              <div className="font-medium text-red-800">
                                {activity.name}
                              </div>
                              <div className="text-sm text-red-600">
                                24/7 Available
                              </div>
                            </Link>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Popular Services */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Popular Services
                    </h3>
                    <ul className="space-y-2">
                      {navigation.services.popular.map((activity) => (
                        <li key={activity.slug}>
                          <Link 
                            href={`/services/${activity.slug}`}
                            className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
                          >
                            {activity.name}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                
              </div>
              
              {/* Bottom CTA */}
              <div className="mt-8 pt-6 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-gray-900">
                      Need Help Choosing?
                    </h4>
                    <p className="text-sm text-gray-600">
                      Our experts can help you find the right service
                    </p>
                  </div>
                  <div className="flex space-x-4">
                    <a 
                      href={`tel:${businessContext.business.phone}`}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                    >
                      Call {businessContext.business.phone}
                    </a>
                    <Link 
                      href="/booking"
                      className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                    >
                      Book Online
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Locations Menu */}
        <div className="relative group">
          <button 
            className="flex items-center text-gray-700 hover:text-blue-600 font-medium transition-colors"
            aria-expanded="false"
            aria-haspopup="true"
          >
            Service Areas
            <svg className="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <div className="absolute left-0 mt-2 w-80 bg-white shadow-xl rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                We Serve {navigation.locations.primary.city} & Surrounding Areas
              </h3>
              
              {/* Primary Location */}
              <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                <div className="font-medium text-blue-900">
                  📍 {navigation.locations.primary.name}
                </div>
                <div className="text-sm text-blue-700">
                  Primary Service Area • {navigation.locations.primary.response_time_hours}hr Response
                </div>
              </div>
              
              {/* Additional Locations */}
              {navigation.locations.additional.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-900 mb-2">Additional Areas:</h4>
                  <ul className="grid grid-cols-2 gap-2">
                    {navigation.locations.additional.map((area) => (
                      <li key={area.slug}>
                        <Link 
                          href={`/locations/${area.slug}`}
                          className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
                        >
                          {area.city}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Coverage Info */}
              <div className="pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-600">
                  <strong>Service Radius:</strong> {navigation.locations.primary.coverage_radius_miles} miles from {navigation.locations.primary.city}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  <strong>Response Time:</strong> Average {navigation.locations.primary.response_time_hours} hours
                </p>
              </div>
            </div>
          </div>
        </div>
        
        {/* About Menu */}
        <div className="relative group">
          <button 
            className="flex items-center text-gray-700 hover:text-blue-600 font-medium transition-colors"
            aria-expanded="false"
            aria-haspopup="true"
          >
            About
            <svg className="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <div className="absolute left-0 mt-2 w-64 bg-white shadow-xl rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
            <div className="p-4">
              <ul className="space-y-2">
                {navigation.company.about_items.map((item) => (
                  <li key={item.href}>
                    <Link 
                      href={item.href}
                      className="block p-2 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="font-medium text-gray-900">
                        {item.label}
                      </div>
                      {item.description && (
                        <div className="text-sm text-gray-600 mt-1">
                          {item.description}
                        </div>
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
        
        {/* Direct Links */}
        <Link 
          href="/projects"
          className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
        >
          Projects
        </Link>
        
        <Link 
          href="/contact"
          className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
        >
          Contact
        </Link>
        
      </div>
      
      {/* CTA Buttons */}
      <div className="hidden lg:flex lg:items-center lg:space-x-4">
        <a 
          href={`tel:${businessContext.business.phone}`}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Call Now
        </a>
        
        <Link 
          href="/booking"
          className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors"
        >
          Book Service
        </Link>
      </div>
      
    </nav>
  );
}

/**
 * Generate navigation structure from business context
 */
function generateNavigationStructure(
  businessContext: BusinessContext,
  tradeConfig: TradeConfiguration
): NavigationStructure {
  
  // Group activities by service categories
  const serviceCategories = groupActivitiesByCategory(businessContext.activities, tradeConfig);
  
  // Featured services (marked as featured or top 3 by booking frequency)
  const featured = businessContext.activities
    .filter(a => a.is_featured)
    .slice(0, 3);
  
  if (featured.length < 3) {
    const additional = businessContext.activities
      .filter(a => !a.is_featured)
      .sort((a, b) => b.booking_frequency - a.booking_frequency)
      .slice(0, 3 - featured.length);
    featured.push(...additional);
  }
  
  // Emergency services
  const emergency = businessContext.activities.filter(a => a.is_emergency);
  
  // Popular services (by booking frequency)
  const popular = businessContext.activities
    .sort((a, b) => b.booking_frequency - a.booking_frequency)
    .slice(0, 5);
  
  // Location structure
  const locations = {
    primary: businessContext.primary_area,
    additional: businessContext.service_areas.filter(a => !a.is_primary),
    coverage_areas: businessContext.service_areas.map(a => a.name)
  };
  
  // Company navigation items
  const company = {
    about_items: [
      { label: 'Our Story', href: '/about', description: `Learn about ${businessContext.business.name}` },
      { label: 'Our Team', href: '/team', description: `Meet our ${businessContext.technicians.length} expert technicians` },
      { label: 'Certifications', href: '/certifications', description: 'Our professional credentials' },
      { label: 'Reviews', href: '/reviews', description: 'What our customers say' }
    ],
    resource_items: [
      { label: 'FAQ', href: '/faq', description: 'Common questions answered' },
      { label: 'Blog', href: '/blog', description: `${tradeConfig.display_name} tips and insights` },
      { label: 'Maintenance Tips', href: '/maintenance', description: 'Keep your systems running smoothly' }
    ]
  };
  
  return {
    services: {
      featured,
      categories: serviceCategories,
      emergency,
      popular
    },
    locations,
    company
  };
}

/**
 * Group activities by service category
 */
function groupActivitiesByCategory(
  activities: ActivityInfo[],
  tradeConfig: TradeConfiguration
): ServiceCategory[] {
  
  const categoryMap = new Map<string, ActivityInfo[]>();
  
  // Group by trade-specific categories
  tradeConfig.service_categories.forEach(category => {
    categoryMap.set(category.name, []);
  });
  
  // Assign activities to categories based on name matching
  activities.forEach(activity => {
    let assigned = false;
    
    for (const category of tradeConfig.service_categories) {
      const categoryKeywords = category.name.toLowerCase().split(' ');
      const activityName = activity.name.toLowerCase();
      
      if (categoryKeywords.some(keyword => activityName.includes(keyword))) {
        categoryMap.get(category.name)?.push(activity);
        assigned = true;
        break;
      }
    }
    
    // If not assigned, put in first category or create "Other Services"
    if (!assigned) {
      const firstCategory = tradeConfig.service_categories[0];
      if (firstCategory) {
        categoryMap.get(firstCategory.name)?.push(activity);
      }
    }
  });
  
  // Convert to array and filter empty categories
  return Array.from(categoryMap.entries())
    .filter(([_, activities]) => activities.length > 0)
    .map(([name, activities]) => ({ name, activities }));
}
