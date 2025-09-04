// Shared content types for client and server. No Node APIs here.

export interface BusinessData {
  id: string;
  name: string;
  description?: string;
  phone_number?: string;
  business_email?: string;
  website?: string;
  logo_url?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  trades: string[];
  service_areas: string[];
  business_hours?: any;
  primary_trade?: string;
  seo_keywords: string[];
}

export interface ServiceCategory {
  id: string;
  name: string;
  description?: string;
  icon_name?: string;
  slug: string;
  services_count: number;
  is_featured: boolean;
  sort_order: number;
}

export interface PromoOffer {
  id: string;
  title: string;
  subtitle?: string;
  description?: string;
  offer_type: string;
  price_label?: string;
  badge_text?: string;
  cta_text: string;
  cta_link?: string;
  placement: string;
  priority: number;
  is_featured: boolean;
}

export interface Rating {
  platform: string;
  rating: number;
  review_count: number;
  display_name: string;
  logo_url?: string;
  profile_url?: string;
  is_featured: boolean;
}

export interface Award {
  id: string;
  name: string;
  issuing_organization?: string;
  description?: string;
  certificate_type?: string;
  logo_url?: string;
  certificate_url?: string;
  verification_url?: string;
  is_featured: boolean;
  is_current: boolean;
  trade_relevance: string[];
}

export interface Partnership {
  id: string;
  partner_name: string;
  partner_type: string;
  partnership_level?: string;
  description?: string;
  partnership_benefits: string[];
  logo_url: string;
  partner_url?: string;
  verification_url?: string;
  is_featured: boolean;
  trade_relevance: string[];
}

export interface Testimonial {
  id: string;
  quote: string;
  rating?: number;
  customer_name: string;
  customer_location?: string;
  service_performed?: string;
  service_date?: string;
  is_featured: boolean;
  is_verified: boolean;
}

export interface Location {
  id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  zip_code?: string;
  latitude?: number;
  longitude?: number;
  service_radius_miles?: number;
  location_type: string;
  is_primary: boolean;
  services_offered: string[];
  trades_covered: string[];
  page_slug?: string;
}


