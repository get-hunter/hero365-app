// Business entity types for website template components
// These mirror the backend Python entities to ensure consistency

export enum CompanySize {
  JUST_ME = "just_me",
  SMALL = "small", 
  MEDIUM = "medium",
  LARGE = "large",
  ENTERPRISE = "enterprise"
}

export enum TradeCategory {
  COMMERCIAL = "commercial",
  RESIDENTIAL = "residential"
}

export enum CommercialTrade {
  MECHANICAL = "mechanical",
  REFRIGERATION = "refrigeration", 
  PLUMBING = "plumbing",
  ELECTRICAL = "electrical",
  SECURITY_SYSTEMS = "security_systems",
  LANDSCAPING = "landscaping",
  ROOFING = "roofing",
  KITCHEN_EQUIPMENT = "kitchen_equipment",
  WATER_TREATMENT = "water_treatment",
  POOL_SPA = "pool_spa"
}

export enum ResidentialTrade {
  HVAC = "hvac",
  PLUMBING = "plumbing",
  ELECTRICAL = "electrical",
  CHIMNEY = "chimney",
  ROOFING = "roofing",
  GARAGE_DOOR = "garage_door",
  SEPTIC = "septic", 
  PEST_CONTROL = "pest_control",
  IRRIGATION = "irrigation",
  PAINTING = "painting"
}

export enum ReferralSource {
  TIKTOK = "tiktok",
  TV = "tv",
  ONLINE_AD = "online_ad",
  WEB_SEARCH = "web_search",
  PODCAST_RADIO = "podcast_radio",
  REDDIT = "reddit", 
  REVIEW_SITES = "review_sites",
  YOUTUBE = "youtube",
  FACEBOOK_INSTAGRAM = "facebook_instagram",
  REFERRAL = "referral",
  OTHER = "other"
}

export interface Business {
  id: string
  name: string
  industry: string
  company_size: CompanySize
  
  // Business Profile
  custom_industry?: string
  description?: string
  phone_number?: string
  business_address?: string
  
  // Address components
  address?: string
  city?: string
  state?: string
  zip_code?: string
  
  website?: string
  logo_url?: string
  business_email?: string
  
  // Trade Information
  trade_category?: TradeCategory
  commercial_trades?: CommercialTrade[]
  residential_trades?: ResidentialTrade[]
  service_areas?: string[]
  
  // Business Identity
  business_registration_number?: string
  tax_id?: string
  business_license?: string
  insurance_number?: string
  
  // Onboarding & Setup
  selected_features?: string[]
  primary_goals?: string[]
  referral_source?: ReferralSource
  onboarding_completed?: boolean
  onboarding_completed_date?: string
  
  // Business Settings
  timezone?: string
  currency?: string
  business_hours?: Record<string, any>
  is_active?: boolean
  
  // Team Management
  max_team_members?: number
  
  // Subscription & Features
  subscription_tier?: string
  enabled_features?: string[]
  
  // Metadata
  created_date?: string
  last_modified?: string
}

// Service-related types from the database schema

export enum ServiceType {
  PRODUCT = "product",
  SERVICE = "service", 
  MAINTENANCE_PLAN = "maintenance_plan",
  EMERGENCY = "emergency"
}

export enum PricingModel {
  FIXED = "fixed",
  HOURLY = "hourly",
  PER_UNIT = "per_unit",
  QUOTE_REQUIRED = "quote_required", 
  TIERED = "tiered"
}

export enum CategoryType {
  EQUIPMENT = "equipment",
  SERVICE_TYPE = "service_type",
  SPECIALIZATION = "specialization"
}

export enum SkillLevel {
  BASIC = "basic",
  INTERMEDIATE = "intermediate",
  ADVANCED = "advanced",
  EXPERT = "expert"
}

export interface ServiceCategory {
  id: string
  name: string
  description?: string
  slug: string
  trade_types: string[]
  category_type: CategoryType
  icon?: string
  parent_id?: string
  sort_order?: number
  is_active?: boolean
  services?: Service[]
  created_at?: string
  updated_at?: string
}

export interface ServiceTemplate {
  id: string
  category_id: string
  name: string
  description: string
  trade_types: string[]
  service_type: ServiceType
  pricing_model: PricingModel
  default_unit_price?: number
  price_range_min?: number
  price_range_max?: number
  unit_of_measure?: string
  estimated_duration_hours?: number
  tags?: string[]
  is_common?: boolean
  is_emergency?: boolean
  requires_license?: boolean
  skill_level?: SkillLevel
  prerequisites?: string[]
  upsell_templates?: string[]
  seasonal_demand?: Record<string, any>
  metadata?: Record<string, any>
  usage_count?: number
  is_active?: boolean
  created_at?: string
  updated_at?: string
}

export interface Service {
  id: string
  business_id: string
  template_id?: string
  category_id: string
  name: string
  description?: string
  pricing_model: PricingModel
  unit_price?: number
  minimum_price?: number
  unit_of_measure?: string
  estimated_duration_hours?: number
  markup_percentage?: number
  cost_price?: number
  is_active?: boolean
  is_featured?: boolean
  is_emergency?: boolean
  requires_booking?: boolean
  availability_schedule?: Record<string, any>
  service_areas?: string[]
  booking_settings?: Record<string, any>
  warranty_terms?: string
  terms_and_conditions?: string
  custom_fields?: Record<string, any>
  sort_order?: number
  total_bookings?: number
  average_rating?: number
  last_booked_at?: string
  created_at?: string
  updated_at?: string
}

export interface ServiceBundle {
  id: string
  business_id: string
  name: string
  description?: string
  service_ids: string[]
  bundle_price?: number
  discount_amount?: number
  discount_percentage?: number
  is_active?: boolean
  is_seasonal?: boolean
  is_featured?: boolean
  valid_from?: string
  valid_until?: string
  max_bookings?: number
  current_bookings?: number
  created_at?: string
  updated_at?: string
}

// Website-specific types for the professional template

export interface TrustRating {
  platform: 'google' | 'yelp' | 'facebook' | 'bbb' | 'angie' | 'homeadvisor'
  rating: number
  reviews: number
  url?: string
}

export interface TrustRatings {
  google?: TrustRating
  yelp?: TrustRating
  facebook?: TrustRating
  bbb?: TrustRating
  angie?: TrustRating
  homeadvisor?: TrustRating
}

export interface PromotionalBanner {
  id?: string
  title: string
  subtitle: string
  buttonText: string
  buttonLink: string
  theme: 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'danger'
  icon?: string
  isActive?: boolean
  validFrom?: string
  validUntil?: string
  order?: number
}

export interface HeroContent {
  title?: string
  subtitle?: string
  description?: string
  features?: string[]
  backgroundImage?: string
  videoUrl?: string
}

export interface WebsiteData {
  heroContent?: HeroContent
  promotionalBanners?: PromotionalBanner[]
  trustRatings?: TrustRatings
  awards?: string[]
  certifications?: string[]
  dealerLogos?: string[]
  testimonials?: Testimonial[]
  customSections?: CustomSection[]
}

export interface Testimonial {
  id: string
  customerName: string
  customerTitle?: string
  customerImage?: string
  rating: number
  text: string
  service?: string
  location?: string
  date?: string
  isVerified?: boolean
  platform?: string
  featured?: boolean
}

export interface CustomSection {
  id: string
  name: string
  type: 'text' | 'image' | 'gallery' | 'video' | 'cta' | 'stats'
  content: Record<string, any>
  isActive: boolean
  order: number
}
