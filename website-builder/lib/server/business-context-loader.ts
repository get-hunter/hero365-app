/**
 * Business Context Loader - Server-Side Only
 * 
 * Loads comprehensive business context for SSR pages.
 * This module runs only on the server and provides optimized
 * data fetching for enhanced artifact pages.
 */

import { BusinessContext } from '@/lib/shared/types/business-context';
import { getBackendUrl, getDefaultHeaders } from '@/lib/shared/config/api-config';

// Cache for business context (in-memory for build time)
const contextCache = new Map<string, { data: BusinessContext; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

/**
 * Get enhanced business context with caching
 */
export async function getBusinessContext(businessId: string): Promise<BusinessContext | null> {
  try {
    // Check cache first
    const cached = contextCache.get(businessId);
    if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
      console.log(`✅ [CACHE] Business context cache hit for: ${businessId}`);
      return cached.data;
    }

    console.log(`🔄 [API] Fetching enhanced business context for: ${businessId}`);
    
    const backendUrl = getBackendUrl();
    const response = await fetch(
      `${backendUrl}/api/v1/public/contractors/website/context/${businessId}?include_templates=true&include_trades=true`,
      {
        headers: getDefaultHeaders(),
        next: { 
          revalidate: 300, // 5 minutes
          tags: ['business-context', businessId] 
        }
      }
    );

    if (!response.ok) {
      console.error(`❌ [API] Business context API failed: ${response.status} ${response.statusText}`);
      return getFallbackBusinessContext(businessId);
    }

    const contextData = await response.json();
    
    // Transform API response to BusinessContext format
    const businessContext = transformToBusinessContext(contextData);
    
    // Cache the result
    contextCache.set(businessId, {
      data: businessContext,
      timestamp: Date.now()
    });

    console.log(`✅ [API] Enhanced business context loaded: ${businessContext.technicians.length} technicians, ${businessContext.projects.length} projects`);
    
    return businessContext;

  } catch (error) {
    console.error(`❌ [API] Error fetching business context for ${businessId}:`, error);
    return getFallbackBusinessContext(businessId);
  }
}

/**
 * Transform API response to BusinessContext format
 */
function transformToBusinessContext(apiData: any): BusinessContext {
  return {
    // Core Business Data
    business: {
      id: apiData.business?.id || '',
      name: apiData.business?.name || 'Professional Services',
      description: apiData.business?.description || '',
      phone: apiData.business?.phone || '',
      email: apiData.business?.email || '',
      address: apiData.business?.address || '',
      city: apiData.business?.city || '',
      state: apiData.business?.state || '',
      postal_code: apiData.business?.postal_code || '',
      website: apiData.business?.website || '',
      primary_trade: apiData.business?.primary_trade || '',
      selected_activities: apiData.business?.selected_activities || [],
      market_focus: apiData.business?.market_focus || 'both',
      years_in_business: apiData.business?.years_in_business || 0,
      company_values: apiData.business?.company_values || [],
      awards_certifications: apiData.business?.awards_certifications || [],
      unique_selling_points: apiData.business?.unique_selling_points || []
    },

    // Trade & Activities
    trade_profile: {
      primary_trade: apiData.business?.primary_trade || '',
      selected_activities: apiData.business?.selected_activities || [],
      market_focus: apiData.business?.market_focus || 'both',
      emergency_services: true,
      commercial_focus: apiData.business?.market_focus === 'commercial' || apiData.business?.market_focus === 'both',
      residential_focus: apiData.business?.market_focus === 'residential' || apiData.business?.market_focus === 'both'
    },

    // Activities
    activities: (apiData.activities || []).map((activity: any) => ({
      slug: activity.slug,
      name: activity.name,
      trade_slug: activity.trade_slug,
      trade_name: activity.trade_name || '',
      synonyms: activity.synonyms || [],
      tags: activity.tags || [],
      is_featured: activity.is_featured || false,
      is_emergency: activity.tags?.includes('emergency') || false,
      booking_frequency: activity.booking_frequency || 0,
      default_booking_fields: activity.default_booking_fields || [],
      required_booking_fields: activity.required_booking_fields || []
    })),

    // Team & Expertise
    technicians: (apiData.technicians || []).map((tech: any) => ({
      id: tech.id,
      name: tech.name,
      title: tech.title || 'Technician',
      years_experience: tech.years_experience || 0,
      certifications: tech.certifications || [],
      specializations: tech.specializations || [],
      bio: tech.bio || null,
      completed_jobs: tech.completed_jobs || 0,
      average_rating: tech.average_rating || 4.8,
      is_public_profile: tech.is_public_profile !== false,
      photo_url: tech.photo_url || null
    })),

    combined_experience_years: (apiData.technicians || []).reduce(
      (sum: number, tech: any) => sum + (tech.years_experience || 0), 0
    ),

    total_certifications: Array.from(new Set(
      (apiData.technicians || []).flatMap((tech: any) => tech.certifications || [])
    )),

    // Service Areas
    service_areas: (apiData.service_areas || []).map((area: any) => ({
      name: area.name,
      slug: area.slug,
      city: area.city,
      state: area.state,
      coverage_radius_miles: area.coverage_radius_miles || 25,
      response_time_hours: area.response_time_hours || 2.0,
      is_primary: area.is_primary || false,
      local_regulations: area.local_regulations || [],
      common_issues: area.common_issues || [],
      seasonal_factors: area.seasonal_factors || []
    })),

    primary_area: (apiData.service_areas || []).find((area: any) => area.is_primary) || 
                  (apiData.service_areas || [])[0] || {
                    name: `${apiData.business?.city || 'Local'}, ${apiData.business?.state || 'Area'}`,
                    slug: 'primary',
                    city: apiData.business?.city || '',
                    state: apiData.business?.state || '',
                    coverage_radius_miles: 25,
                    response_time_hours: 2.0,
                    is_primary: true,
                    local_regulations: [],
                    common_issues: [],
                    seasonal_factors: []
                  },

    // Project Portfolio
    projects: (apiData.projects || []).map((project: any) => ({
      id: project.id,
      title: project.title,
      description: project.description || '',
      category: project.category || 'service',
      location: project.location || 'Service Area',
      initial_problem: project.initial_problem || 'Customer service need',
      solution_implemented: project.solution_implemented || project.description || '',
      outcome: project.outcome || 'Successful completion',
      duration: project.duration || '1 day',
      value: project.value || 0,
      customer_savings: project.customer_savings || null,
      efficiency_improvement: project.efficiency_improvement || null,
      technician_id: project.technician_id || '',
      technician_name: project.technician_name || 'Professional Team',
      technician_certifications: project.technician_certifications || [],
      images: project.images || [],
      customer_feedback: project.customer_feedback || null,
      slug: project.slug || project.title?.toLowerCase().replace(/\s+/g, '-') || ''
    })),

    showcase_projects: (apiData.projects || [])
      .sort((a: any, b: any) => (b.value || 0) - (a.value || 0))
      .slice(0, 6)
      .map((project: any) => ({
        id: project.id,
        title: project.title,
        description: project.description || '',
        category: project.category || 'service',
        location: project.location || 'Service Area',
        initial_problem: project.initial_problem || 'Customer service need',
        solution_implemented: project.solution_implemented || project.description || '',
        outcome: project.outcome || 'Successful completion',
        duration: project.duration || '1 day',
        value: project.value || 0,
        customer_savings: project.customer_savings || null,
        efficiency_improvement: project.efficiency_improvement || null,
        technician_id: project.technician_id || '',
        technician_name: project.technician_name || 'Professional Team',
        technician_certifications: project.technician_certifications || [],
        images: project.images || [],
        customer_feedback: project.customer_feedback || null,
        slug: project.slug || project.title?.toLowerCase().replace(/\s+/g, '-') || ''
      })),

    completed_count: (apiData.projects || []).length,
    average_project_value: (apiData.projects || []).length > 0 
      ? (apiData.projects || []).reduce((sum: number, p: any) => sum + (p.value || 0), 0) / (apiData.projects || []).length
      : 0,

    // Customer Data
    testimonials: apiData.testimonials || [],
    total_served: apiData.total_served || (apiData.projects || []).length,
    average_rating: apiData.average_rating || 4.8,
    repeat_customer_rate: apiData.repeat_customer_rate || 0.3,

    // Market Intelligence
    market_insights: apiData.market_insights || {},
    competitive_advantages: apiData.competitive_advantages || [
      'Local expertise',
      'Fast response times',
      'Quality workmanship'
    ],

    // Metadata
    generated_at: new Date().toISOString(),
    cache_key: `enhanced_context:${apiData.business?.id || ''}`
  };
}

/**
 * Fallback business context when API fails
 */
function getFallbackBusinessContext(businessId: string): BusinessContext {
  console.log(`⚠️ [FALLBACK] Using fallback business context for: ${businessId}`);
  
  return {
    business: {
      id: businessId,
      name: process.env.NEXT_PUBLIC_BUSINESS_NAME || 'Professional Services',
      description: 'Professional home services with expert technicians',
      phone: process.env.NEXT_PUBLIC_BUSINESS_PHONE || '(555) 123-4567',
      email: process.env.NEXT_PUBLIC_BUSINESS_EMAIL || 'info@business.com',
      address: process.env.NEXT_PUBLIC_BUSINESS_ADDRESS || '123 Main St',
      city: process.env.NEXT_PUBLIC_BUSINESS_CITY || 'Austin',
      state: process.env.NEXT_PUBLIC_BUSINESS_STATE || 'TX',
      postal_code: '78701',
      website: process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com',
      primary_trade: 'hvac',
      selected_activities: ['ac-repair', 'hvac-installation'],
      market_focus: 'both',
      years_in_business: 10,
      company_values: ['Quality', 'Reliability', 'Customer Service'],
      awards_certifications: ['BBB A+ Rating', 'Licensed & Insured'],
      unique_selling_points: ['24/7 Emergency Service', 'Satisfaction Guaranteed']
    },

    trade_profile: {
      primary_trade: 'hvac',
      selected_activities: ['ac-repair', 'hvac-installation'],
      market_focus: 'both',
      emergency_services: true,
      commercial_focus: true,
      residential_focus: true
    },

    activities: [
      {
        slug: 'ac-repair',
        name: 'AC Repair',
        trade_slug: 'hvac',
        trade_name: 'HVAC',
        synonyms: ['air conditioning repair'],
        tags: ['emergency', 'repair'],
        is_featured: true,
        is_emergency: true,
        booking_frequency: 100,
        default_booking_fields: [],
        required_booking_fields: []
      }
    ],

    technicians: [
      {
        id: 'tech-1',
        name: 'John Smith',
        title: 'Senior HVAC Technician',
        years_experience: 15,
        certifications: ['NATE Certified', 'EPA Licensed'],
        specializations: ['AC Repair', 'System Installation'],
        bio: null,
        completed_jobs: 500,
        average_rating: 4.9,
        is_public_profile: true,
        photo_url: null
      }
    ],

    combined_experience_years: 15,
    total_certifications: ['NATE Certified', 'EPA Licensed'],

    service_areas: [
      {
        name: `${process.env.NEXT_PUBLIC_BUSINESS_CITY || 'Austin'}, ${process.env.NEXT_PUBLIC_BUSINESS_STATE || 'TX'}`,
        slug: 'primary',
        city: process.env.NEXT_PUBLIC_BUSINESS_CITY || 'Austin',
        state: process.env.NEXT_PUBLIC_BUSINESS_STATE || 'TX',
        coverage_radius_miles: 25,
        response_time_hours: 2.0,
        is_primary: true,
        local_regulations: [],
        common_issues: [],
        seasonal_factors: []
      }
    ],

    primary_area: {
      name: `${process.env.NEXT_PUBLIC_BUSINESS_CITY || 'Austin'}, ${process.env.NEXT_PUBLIC_BUSINESS_STATE || 'TX'}`,
      slug: 'primary',
      city: process.env.NEXT_PUBLIC_BUSINESS_CITY || 'Austin',
      state: process.env.NEXT_PUBLIC_BUSINESS_STATE || 'TX',
      coverage_radius_miles: 25,
      response_time_hours: 2.0,
      is_primary: true,
      local_regulations: [],
      common_issues: [],
      seasonal_factors: []
    },

    projects: [],
    showcase_projects: [],
    completed_count: 0,
    average_project_value: 0,

    testimonials: [],
    total_served: 100,
    average_rating: 4.8,
    repeat_customer_rate: 0.3,

    market_insights: {},
    competitive_advantages: [
      'Local expertise',
      'Fast response times',
      'Quality workmanship'
    ],

    generated_at: new Date().toISOString(),
    cache_key: `fallback_context:${businessId}`
  };
}

/**
 * Invalidate business context cache
 */
export function invalidateBusinessContextCache(businessId: string) {
  contextCache.delete(businessId);
  console.log(`🗑️ [CACHE] Invalidated business context cache for: ${businessId}`);
}

/**
 * Clear all cached business contexts
 */
export function clearBusinessContextCache() {
  contextCache.clear();
  console.log(`🗑️ [CACHE] Cleared all business context cache`);
}
