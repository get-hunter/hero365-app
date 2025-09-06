/**
 * API Response Types
 * 
 * Typed models for Hero365 backend API responses
 * These ensure type safety across all pages and components
 */

// Business Profile Response
export interface BusinessProfile {
  id?: string;
  business_id?: string;
  business_name: string;
  primary_trade?: string | null;
  primary_trade_slug?: string | null;
  description?: string | null;
  phone?: string | null;
  email?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  postal_code?: string | null;
  service_areas?: string[];
  emergency_service?: boolean;
  years_in_business?: number | null;
  license_number?: string | null;
  insurance_verified?: boolean;
  average_rating?: number | null;
  total_reviews?: number | null;
  certifications?: string[];
  website?: string | null;
  logo_url?: string | null;
}

// Service/Activity Item
export interface ServiceItem {
  id: string | number;
  name: string;
  slug: string;
  description?: string | null;
  category?: string;
  is_featured?: boolean;
  price_range?: string | null;
}

// Product Item
export interface ProductItem {
  id: string | number;
  slug: string;
  name: string;
  description?: string | null;
  unit_price?: number | string | null;
  category?: string | null;
  sku?: string | null;
  in_stock?: boolean;
  featured?: boolean;
  image_url?: string | null;
}

// Project Item
export interface ProjectItem {
  id: string | number;
  slug?: string | null;
  title: string;
  description?: string | null;
  category?: string | null;
  completion_date?: string | null;
  customer_testimonial?: string | null;
  featured_image_url?: string | null;
  location?: string | null;
  budget_range?: string | null;
  duration?: string | null;
  featured?: boolean;
}

// Homepage Data Bundle
export interface HomepageData {
  profile: BusinessProfile | null;
  services: ServiceItem[];
  products: ProductItem[];
  projects: ProjectItem[];
  diagnostics?: {
    backendUrl: string;
    profileOk: boolean;
    servicesOk: boolean;
    productsOk: boolean;
    projectsOk: boolean;
  };
}

// Service Category (for structured navigation)
export interface ServiceCategory {
  id: string | number;
  name: string;
  slug: string;
  services: ServiceItem[];
  description?: string;
}

// Location/Service Area
export interface LocationItem {
  id: string | number;
  name: string;
  slug: string;
  city: string;
  state: string;
  is_primary?: boolean;
  address?: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
}
