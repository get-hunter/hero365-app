/**
 * Checkout System Type Definitions
 * 
 * Types for the complete checkout flow including customer information,
 * installation scheduling, and order processing.
 */

export interface CheckoutCustomer {
  name: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
}

export interface InstallationPreferences {
  preferred_date: string; // YYYY-MM-DD format
  preferred_time: 'morning' | 'afternoon' | 'evening';
  special_instructions?: string;
  access_instructions?: string;
}

export interface CheckoutRequest {
  cart_id: string;
  customer: CheckoutCustomer;
  installation: InstallationPreferences;
  membership_type: string;
  payment_method: 'card' | 'check' | 'cash';
  notes?: string;
}

export interface CheckoutResponse {
  success: boolean;
  estimate_id: string;
  booking_id: string;
  estimate_number: string;
  booking_number: string;
  total_amount: number;
  message: string;
}

export interface CheckoutFormData {
  // Customer Information
  customer: CheckoutCustomer;
  
  // Installation Preferences
  installation: InstallationPreferences;
  
  // Payment & Additional Info
  membership_type: string;
  payment_method: 'card' | 'check' | 'cash';
  notes: string;
  
  // Terms & Agreements
  terms_accepted: boolean;
  email_consent: boolean;
  sms_consent: boolean;
}

export interface CheckoutValidation {
  isValid: boolean;
  errors: Record<string, string>;
}

export interface CheckoutStep {
  id: string;
  title: string;
  description: string;
  isComplete: boolean;
  isActive: boolean;
}

// US States for form validation
export const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
] as const;

export type USState = typeof US_STATES[number];
