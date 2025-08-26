export interface ProductInstallationOption {
  id: string;
  option_name: string;
  description?: string;
  base_install_price: number;
  residential_install_price?: number;
  commercial_install_price?: number;
  premium_install_price?: number;
  estimated_duration_hours?: number;
  complexity_multiplier?: number;
  is_default: boolean;
  requirements?: Record<string, any>;
  included_in_install?: string[];
}

export interface ProductCatalogItem {
  id: string;
  name: string;
  sku: string;
  description?: string;
  long_description?: string;
  unit_price: number;
  category_name?: string;
  warranty_years?: number;
  energy_efficiency_rating?: string;
  requires_professional_install: boolean;
  install_complexity: 'simple' | 'standard' | 'complex';
  installation_time_estimate?: string;
  featured_image_url?: string;
  gallery_images: string[];
  product_highlights: string[];
  technical_specs: Record<string, any>;
  meta_title?: string;
  meta_description?: string;
  slug?: string;
  is_active: boolean;
  is_featured: boolean;
  current_stock?: number;
  installation_options: ProductInstallationOption[];
}

export interface ProductCategory {
  id: string;
  name: string;
  description?: string;
  product_count: number;
  sort_order?: number;
}

export interface PricingBreakdown {
  product_unit_price: number;
  installation_base_price: number;
  quantity: number;
  product_subtotal: number;
  installation_subtotal: number;
  subtotal_before_discounts: number;
  membership_type?: string;
  product_discount_amount: number;
  installation_discount_amount: number;
  total_discount_amount: number;
  bundle_savings: number;
  subtotal_after_discounts: number;
  tax_rate: number;
  tax_amount: number;
  total_amount: number;
  total_savings: number;
  savings_percentage: number;
  formatted_display_price: string;
  price_display_type: string;
}

export interface CartItem {
  id: string;
  product_id: string;
  product_name: string;
  product_sku: string;
  unit_price: number;
  installation_option_id?: string;
  installation_option_name?: string;
  installation_price: number;
  quantity: number;
  item_total: number;
  discount_amount: number;
  membership_discount: number;
  bundle_savings: number;
}

export interface ShoppingCart {
  id: string;
  business_id?: string;
  session_id?: string;
  customer_email?: string;
  customer_phone?: string;
  cart_status: string;
  currency_code?: string;
  items: CartItem[];
  membership_type?: string;
  membership_verified?: boolean;
  subtotal: number;
  total_savings: number;
  tax_amount: number;
  total_amount: number;
  item_count: number;
  last_activity_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CartSummary {
  item_count: number;
  subtotal: number;
  total_savings: number;
  tax_amount: number;
  total_amount: number;
  savings_percentage: number;
}

export type MembershipType = 'none' | 'residential' | 'commercial' | 'premium';
export type SortOption = 'name' | 'price_low' | 'price_high' | 'featured' | 'rating';
