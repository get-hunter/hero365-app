/**
 * Enhanced API Response Types
 * 
 * Comprehensive typed models that eliminate the need for 'any' types
 * Includes proper null handling and optional properties
 */

// Enhanced Business Profile with all known properties
export interface EnhancedBusinessProfile {
  id?: string;
  business_id?: string;
  business_name: string;
  primary_trade?: string | null;
  primary_trade_slug?: string | null;
  description?: string | null;
  phone?: string | null;
  phone_display?: string | null;
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
  business_hours?: BusinessHours | null;
}

// Business Hours structure
export interface BusinessHours {
  monday?: DayHours;
  tuesday?: DayHours;
  wednesday?: DayHours;
  thursday?: DayHours;
  friday?: DayHours;
  saturday?: DayHours;
  sunday?: DayHours;
}

export interface DayHours {
  open: string;
  close: string;
  closed?: boolean;
}

// Enhanced Product with all variations and metadata
export interface EnhancedProductItem {
  id: string | number;
  slug: string;
  name: string;
  description?: string | null;
  long_description?: string | null;
  unit_price?: number | string | null;
  category?: string | null;
  category_name?: string | null;
  sku?: string | null;
  brand?: string | null;
  model?: string | null;
  in_stock?: boolean;
  featured?: boolean;
  image_url?: string | null;
  images?: ProductImage[];
  has_variations?: boolean;
  variations?: ProductVariation[];
  specifications?: ProductSpecification[];
  warranty_years?: number;
  installation_available?: boolean;
  installation_options?: InstallationOption[];
}

export interface ProductImage {
  id: string;
  url: string;
  alt_text?: string;
  is_primary?: boolean;
  sort_order?: number;
}

export interface ProductVariation {
  id: string;
  name: string;
  value: string;
  price_adjustment?: number;
  sku_suffix?: string;
}

export interface ProductSpecification {
  name: string;
  value: string;
  unit?: string;
}

export interface InstallationOption {
  id: string;
  name: string;
  description?: string;
  base_install_price: number;
  estimated_duration_hours: number;
  warranty_years?: number;
  included_in_install?: string[];
  additional_fees?: InstallationFee[];
}

export interface InstallationFee {
  name: string;
  description?: string;
  price: number;
  required?: boolean;
}

// Enhanced Project with complete metadata
export interface EnhancedProjectItem {
  id: string | number;
  slug?: string | null;
  title: string;
  description?: string | null;
  long_description?: string | null;
  category?: string | null;
  completion_date?: string | null;
  customer_testimonial?: string | null;
  customer_name?: string | null;
  customer_location?: string | null;
  featured_image_url?: string | null;
  image_gallery?: ProjectImage[];
  location?: string | null;
  budget_range?: string | null;
  actual_cost?: number | null;
  duration?: string | null;
  duration_days?: number | null;
  featured?: boolean;
  tags?: string[];
  before_images?: string[];
  after_images?: string[];
  materials_used?: ProjectMaterial[];
  challenges_overcome?: string[];
  client_satisfaction_score?: number;
}

export interface ProjectImage {
  url: string;
  caption?: string;
  type: 'before' | 'during' | 'after' | 'detail';
  sort_order?: number;
}

export interface ProjectMaterial {
  name: string;
  brand?: string;
  quantity?: number;
  unit?: string;
}

// Enhanced Service with pricing and availability
export interface EnhancedServiceItem {
  id: string | number;
  name: string;
  slug: string;
  description?: string | null;
  long_description?: string | null;
  category?: string;
  category_slug?: string;
  is_featured?: boolean;
  price_range?: string | null;
  starting_price?: number | null;
  typical_duration?: string | null;
  emergency_available?: boolean;
  warranty_included?: boolean;
  warranty_duration?: string | null;
  service_areas?: string[];
  prerequisites?: string[];
  what_included?: string[];
  additional_services?: AdditionalService[];
}

export interface AdditionalService {
  name: string;
  description?: string;
  price?: number;
  duration?: string;
}

// Diagnostics with proper typing
export interface DiagnosticsInfo {
  backendUrl: string;
  profileOk: boolean;
  servicesOk: boolean;
  productsOk: boolean;
  projectsOk: boolean;
  timestamp?: number;
  environment?: string;
}

// Enhanced Homepage Data Bundle
export interface EnhancedHomepageData {
  profile: EnhancedBusinessProfile | null;
  services: EnhancedServiceItem[];
  products: EnhancedProductItem[];
  projects: EnhancedProjectItem[];
  diagnostics?: DiagnosticsInfo;
}

// Business Data for components (normalized interface)
export interface BusinessData {
  id: string;
  name: string;
  phone_number?: string | null;
  business_email?: string | null;
  address?: string | null;
  service_areas?: string[];
  trades?: string[];
  seo_keywords?: string[];
  business_hours?: BusinessHours | null;
  emergency_service?: boolean;
  years_in_business?: number | null;
  license_number?: string | null;
  insurance_verified?: boolean;
  average_rating?: number | null;
  total_reviews?: number | null;
  certifications?: string[];
  website?: string | null;
}

// Location with enhanced data
export interface EnhancedLocationItem {
  id: string | number;
  name: string;
  slug: string;
  city: string;
  state: string;
  is_primary?: boolean;
  address?: string;
  phone?: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  service_radius_miles?: number;
  business_hours?: BusinessHours;
}

// Category with enhanced metadata
export interface EnhancedServiceCategory {
  id: string | number;
  name: string;
  slug: string;
  description?: string;
  services: EnhancedServiceItem[];
  icon?: string;
  sort_order?: number;
  is_featured?: boolean;
}

// Widget configuration types
export type WidgetMode = 'inline' | 'popup' | 'sidebar' | 'fullscreen';
export type WidgetTheme = 'light' | 'dark' | 'auto';

export interface WidgetConfig {
  businessId: string;
  mode: WidgetMode;
  theme: WidgetTheme;
  primaryColor: string;
  companyName: string;
}

// Analytics event types
export interface AnalyticsEvent {
  event: string;
  properties: Record<string, any>;
  timestamp: number;
  session_id?: string;
  user_id?: string;
}

// Membership plan types
export interface MembershipPlan {
  id: string;
  name: string;
  description?: string;
  price: number;
  billing_period: 'monthly' | 'yearly';
  features: string[];
  is_popular?: boolean;
  discount_percentage?: number;
}

// Type guards for runtime type checking
export function isEnhancedBusinessProfile(obj: any): obj is EnhancedBusinessProfile {
  return obj && typeof obj === 'object' && typeof obj.business_name === 'string';
}

export function isEnhancedProductItem(obj: any): obj is EnhancedProductItem {
  return obj && typeof obj === 'object' && typeof obj.name === 'string' && obj.slug;
}

export function isEnhancedProjectItem(obj: any): obj is EnhancedProjectItem {
  return obj && typeof obj === 'object' && typeof obj.title === 'string';
}

export function isEnhancedServiceItem(obj: any): obj is EnhancedServiceItem {
  return obj && typeof obj === 'object' && typeof obj.name === 'string' && obj.slug;
}

// Backward compatibility aliases for existing code
export type BusinessProfile = EnhancedBusinessProfile;
export type ServiceItem = EnhancedServiceItem;
export type ProductItem = EnhancedProductItem;
export type ProjectItem = EnhancedProjectItem;
export type LocationItem = EnhancedLocationItem;
export type ServiceCategory = EnhancedServiceCategory;

// Homepage data with backward compatibility
export interface HomepageData {
  profile: BusinessProfile | null;
  services: ServiceItem[];
  products: ProductItem[];
  projects: ProjectItem[];
  diagnostics?: DiagnosticsInfo;
}

// Utility function to safely extract business data
export function extractBusinessData(profile: EnhancedBusinessProfile): BusinessData {
  return {
    id: profile.business_id || profile.id || '',
    name: profile.business_name,
    phone_number: profile.phone_display || profile.phone,
    business_email: profile.email,
    address: profile.address,
    service_areas: profile.service_areas || [],
    trades: [], // This would come from a separate endpoint
    seo_keywords: [], // This would come from a separate endpoint
    business_hours: profile.business_hours,
    emergency_service: profile.emergency_service,
    years_in_business: profile.years_in_business,
    license_number: profile.license_number,
    insurance_verified: profile.insurance_verified,
    average_rating: profile.average_rating,
    total_reviews: profile.total_reviews,
    certifications: profile.certifications || [],
    website: profile.website
  };
}
