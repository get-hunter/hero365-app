/**
 * Membership and Subscription System Types
 * 
 * Based on elite service companies like Fuse Service offering
 * residential, commercial, and premium membership plans
 */

export type MembershipType = 'residential' | 'commercial' | 'premium';

export type PricingPeriod = 'monthly' | 'yearly' | 'one_time';

export type DiscountType = 'percentage' | 'fixed_amount' | 'free_service';

export interface MembershipBenefit {
  id: string;
  title: string;
  description: string;
  icon?: string;
  value?: string;
  is_highlighted?: boolean;
  sort_order: number;
}

export interface MembershipPlan {
  id: string;
  name: string;
  type: MembershipType;
  description: string;
  tagline?: string;
  
  // Pricing
  price_monthly?: number;
  price_yearly?: number;
  yearly_savings?: number;
  setup_fee?: number;
  
  // Service Benefits
  discount_percentage?: number;
  priority_service: boolean;
  extended_warranty: boolean;
  maintenance_included: boolean;
  emergency_response: boolean;
  free_diagnostics: boolean;
  annual_tune_ups?: number;
  
  // Member Perks
  benefits: MembershipBenefit[];
  
  // Display & Marketing
  is_active: boolean;
  is_featured: boolean;
  popular_badge?: string;
  color_scheme?: string;
  sort_order: number;
  
  // Terms
  contract_length?: number; // months
  cancellation_policy?: string;
  
  created_at: string;
  updated_at: string;
}

export interface ServiceDiscount {
  id: string;
  service_category: string;
  service_name: string;
  membership_type: MembershipType[];
  discount_type: DiscountType;
  discount_value: number;
  description?: string;
  conditions?: string;
  is_active: boolean;
}

export interface MembershipSubscription {
  id: string;
  customer_id: string;
  plan_id: string;
  status: 'active' | 'inactive' | 'suspended' | 'cancelled';
  
  // Billing
  billing_period: PricingPeriod;
  start_date: string;
  next_billing_date?: string;
  end_date?: string;
  
  // Payment
  payment_method_id?: string;
  auto_renew: boolean;
  
  // Usage tracking
  services_used: number;
  discount_savings: number;
  last_service_date?: string;
  
  created_at: string;
  updated_at: string;
}

// Enhanced service pricing with membership integration
export interface ServicePricing {
  id: string;
  service_name: string;
  category: string;
  base_price: number;
  price_display: 'from' | 'fixed' | 'quote_required' | 'free';
  
  // Member pricing
  residential_member_price?: number;
  commercial_member_price?: number;
  premium_member_price?: number;
  
  description?: string;
  includes?: string[];
  duration_estimate?: string;
  minimum_labor_fee?: number;
  
  // Conditions
  height_surcharge?: boolean;
  additional_tech_fee?: boolean;
  parts_separate?: boolean;
  
  is_active: boolean;
  sort_order: number;
}

// Membership marketing content
export interface MembershipContent {
  id: string;
  membership_type: MembershipType;
  
  // Marketing copy
  headline: string;
  subheadline?: string;
  value_proposition: string;
  cta_text: string;
  
  // Social proof
  testimonial?: string;
  testimonial_author?: string;
  member_count?: number;
  satisfaction_rate?: number;
  
  // Visual elements
  hero_image?: string;
  logo_variants?: string[];
  color_scheme?: Record<string, string>;
  
  created_at: string;
  updated_at: string;
}

// Service categories with membership pricing
export interface EnhancedServiceCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  slug: string;
  
  // Pricing overview
  starting_price: number;
  typical_range: {
    min: number;
    max: number;
  };
  
  // Services
  services: ServicePricing[];
  
  // Membership benefits for this category
  membership_benefits: {
    residential: string[];
    commercial: string[];
    premium: string[];
  };
  
  is_featured: boolean;
  sort_order: number;
}
