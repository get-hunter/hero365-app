/**
 * Trade Configuration Types
 * 
 * TypeScript definitions for trade-specific configurations
 * used in the enhanced website generation system.
 */

export interface TradeColors {
  primary: string;
  secondary: string;
  accent: string;
}

export interface TradeHero {
  headline_template: string;
  subtitle_points: string[];
  primary_cta: string;
  secondary_cta: string;
  emergency_message: string;
}

export interface ServiceCategory {
  name: string;
  description: string;
  starting_price: number;
  emergency_available: boolean;
  seasonal_demand: 'year_round' | 'high_summer' | 'high_winter' | 'spring_summer' | 'fall_winter' | 'spring_fall';
}

export interface SeasonalPatterns {
  peak_months: number[];
  slow_months: number[];
  maintenance_months: number[];
}

export interface TradeConfiguration {
  // Basic Info
  trade: string;
  display_name: string;
  full_name: string;
  category: 'residential' | 'commercial';
  description: string;
  
  // Visual Identity
  colors: TradeColors;
  
  // Hero Section Configuration
  hero: TradeHero;
  
  // Service Information
  service_categories: ServiceCategory[];
  emergency_services: boolean;
  seasonal_patterns: SeasonalPatterns;
  
  // Professional Credentials
  certifications: string[];
  
  // Activity Modules
  activity_modules: string[];
}

// Helper types for trade-specific content
export interface TradeMessaging {
  emergency_headline: string;
  value_propositions: string[];
  trust_indicators: string[];
  seasonal_messages: Record<string, string>;
}

export interface TradeKeywords {
  primary: string[];
  secondary: string[];
  local_modifiers: string[];
  service_modifiers: string[];
}

export interface TradeCompliance {
  required_licenses: string[];
  insurance_requirements: string[];
  safety_certifications: string[];
  local_regulations: string[];
}

// Extended trade configuration for advanced features
export interface ExtendedTradeConfiguration extends TradeConfiguration {
  messaging?: TradeMessaging;
  keywords?: TradeKeywords;
  compliance?: TradeCompliance;
  
  // Advanced features
  booking_flow?: {
    required_fields: string[];
    optional_fields: string[];
    emergency_flow: boolean;
  };
  
  pricing_strategy?: {
    model: 'flat_rate' | 'hourly' | 'diagnostic_plus' | 'tiered';
    emergency_multiplier: number;
    after_hours_multiplier: number;
  };
  
  content_templates?: {
    faq_categories: string[];
    process_steps: string[];
    maintenance_tips: string[];
  };
}