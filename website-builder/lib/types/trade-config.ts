/**
 * Trade Configuration System
 * 
 * Defines all supported trades and their specific configurations
 */

export type TradeType = 'commercial' | 'residential';

export type CommercialTrade = 
  | 'mechanical'
  | 'refrigeration' 
  | 'plumbing'
  | 'electrical'
  | 'security_systems'
  | 'landscaping'
  | 'roofing'
  | 'kitchen_equipment'
  | 'water_treatment'
  | 'pool_spa';

export type ResidentialTrade =
  | 'hvac'
  | 'plumbing'
  | 'electrical'
  | 'chimney'
  | 'roofing'
  | 'garage_door'
  | 'septic'
  | 'pest_control'
  | 'irrigation'
  | 'painting';

export type Trade = CommercialTrade | ResidentialTrade;

export interface ServiceCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  services: TradeService[];
  starting_price?: number;
  is_emergency?: boolean;
  is_popular?: boolean;
}

export interface TradeService {
  id: string;
  name: string;
  description: string;
  estimated_duration_minutes: number;
  base_price?: number;
  price_type: 'fixed' | 'estimate' | 'hourly';
  requires_site_visit: boolean;
  is_emergency?: boolean;
  tags: string[];
}

export interface TradeConfiguration {
  trade: Trade;
  type: TradeType;
  display_name: string;
  industry_terms: {
    professional_title: string; // "HVAC Technician", "Electrician", "Plumber"
    service_area: string; // "HVAC services", "electrical work", "plumbing repairs"
    emergency_type: string; // "HVAC emergency", "electrical emergency", "plumbing emergency"
    maintenance_term: string; // "tune-up", "inspection", "maintenance"
  };
  hero: {
    headline_template: string; // "{city}'s Most Trusted {trade} Experts"
    subtitle_points: string[];
    emergency_message?: string;
    primary_cta: string; // "Book HVAC Service", "Schedule Electrical Work"
    secondary_cta: string; // "Call Now", "Get Free Quote"
  };
  service_categories: ServiceCategory[];
  trust_indicators: {
    certifications: string[];
    guarantees: string[];
    features: string[];
  };
  booking: {
    default_services: string[];
    emergency_services: string[];
    lead_times: {
      emergency_hours: number;
      standard_hours: number;
      maintenance_days: number;
    };
  };
  seo: {
    title_template: string;
    description_template: string;
    keywords: string[];
  };
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    emergency: string;
  };
}

export interface BusinessProfile {
  // Core business info
  name: string;
  trade: Trade;
  type: TradeType;
  
  // Contact details
  phone: string;
  email: string;
  website_url?: string;
  
  // Location & service area
  address: string;
  city: string;
  state: string;
  zip: string;
  service_areas: string[];
  service_radius_miles: number;
  
  // Business details
  established_year?: number;
  license_number?: string;
  insurance_info?: string;
  certifications: string[];
  
  // Branding
  logo_url?: string;
  brand_colors?: {
    primary?: string;
    secondary?: string;
  };
  
  // Social media
  social_media?: {
    facebook?: string;
    instagram?: string;
    linkedin?: string;
    google_business?: string;
  };
  
  // Business hours
  hours: {
    [key: string]: { open: string; close: string; closed?: boolean };
  };
  emergency_available: boolean;
  
  // Stats & credentials
  years_in_business?: number;
  customers_served?: number;
  projects_completed?: number;
  satisfaction_rate?: number;
  
  // Team info
  team_size?: number;
  owner_name?: string;
  owner_bio?: string;
}
