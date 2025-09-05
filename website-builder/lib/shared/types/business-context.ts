/**
 * Business Context Types
 * 
 * TypeScript definitions for comprehensive business context
 * used in trade-aware website generation.
 */

export interface TechnicianProfile {
  id: string;
  name: string;
  title: string;
  years_experience: number;
  certifications: string[];
  specializations: string[];
  bio: string | null;
  completed_jobs: number;
  average_rating: number;
  is_public_profile: boolean;
  photo_url: string | null;
}

export interface ProjectShowcase {
  id: string;
  title: string;
  description: string;
  category: string;
  location: string;
  initial_problem: string;
  solution_implemented: string;
  outcome: string;
  duration: string;
  value: number;
  customer_savings: number | null;
  efficiency_improvement: string | null;
  technician_id: string;
  technician_name: string;
  technician_certifications: string[];
  images: string[];
  customer_feedback: string | null;
  slug: string;
}

export interface ServiceArea {
  name: string;
  slug: string;
  city: string;
  state: string;
  coverage_radius_miles: number;
  response_time_hours: number;
  is_primary: boolean;
  local_regulations: string[];
  common_issues: string[];
  seasonal_factors: string[];
}

export interface ActivityInfo {
  slug: string;
  name: string;
  trade_slug: string;
  trade_name: string;
  synonyms: string[];
  tags: string[];
  is_featured: boolean;
  is_emergency: boolean;
  booking_frequency: number;
  default_booking_fields: any[];
  required_booking_fields: any[];
}

export interface BusinessInfo {
  id: string;
  name: string;
  description: string;
  phone: string;
  email: string;
  address: string;
  city: string;
  state: string;
  postal_code: string;
  website: string;
  primary_trade: string;
  selected_activities: string[];
  market_focus: string;
  years_in_business: number;
  company_values: string[];
  awards_certifications: string[];
  unique_selling_points: string[];
  logo_url?: string;
}

export interface TradeProfile {
  primary_trade: string;
  selected_activities: string[];
  market_focus: string;
  emergency_services: boolean;
  commercial_focus: boolean;
  residential_focus: boolean;
}

export interface Testimonial {
  id: string;
  text: string;
  customer_name: string;
  customer_location: string;
  service_id: string;
  technician_id: string;
  rating: number;
  date: string;
  project_id?: string;
}

export interface BusinessContext {
  // Core Business Data
  business: BusinessInfo;
  
  // Trade & Activities
  trade_profile: TradeProfile;
  activities: ActivityInfo[];
  
  // Team & Expertise
  technicians: TechnicianProfile[];
  combined_experience_years: number;
  total_certifications: string[];
  
  // Service Areas
  service_areas: ServiceArea[];
  primary_area: ServiceArea;
  
  // Project Portfolio
  projects: ProjectShowcase[];
  showcase_projects: ProjectShowcase[];
  completed_count: number;
  average_project_value: number;
  
  // Customer Data
  testimonials: Testimonial[];
  total_served: number;
  average_rating: number;
  repeat_customer_rate: number;
  
  // Market Intelligence
  market_insights: Record<string, any>;
  competitive_advantages: string[];
  
  // Metadata
  generated_at: string;
  cache_key: string;
}

// Helper types for API responses
export interface BusinessContextRequest {
  include_templates?: boolean;
  include_trades?: boolean;
  activity_limit?: number;
  template_limit?: number;
}

export interface BusinessContextResponse {
  business: BusinessInfo;
  activities: ActivityInfo[];
  service_templates: any[];
  trades: any[];
  technicians: TechnicianProfile[];
  projects: ProjectShowcase[];
  testimonials: Testimonial[];
  metadata: {
    generated_at: string;
    total_activities: number;
    total_templates: number;
    total_trades: number;
    primary_trade: string;
  };
}
