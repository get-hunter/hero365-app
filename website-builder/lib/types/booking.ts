/**
 * Booking System Types
 * 
 * TypeScript interfaces for the booking system that mirror the backend DTOs
 */

export interface TimeSlot {
  start_time: string; // ISO datetime string
  end_time: string; // ISO datetime string
  available_technicians: string[]; // Array of technician UUIDs
  capacity: number;
  booked_count: number;
  price?: number;
}

export interface AvailabilityRequest {
  business_id: string;
  service_id: string;
  start_date: string; // ISO date string
  end_date?: string; // ISO date string
  preferred_times?: {
    start: string; // HH:MM format
    end: string; // HH:MM format
  };
  customer_address?: string;
  customer_coordinates?: [number, number]; // [lat, lng]
  preferred_technician_id?: string;
  exclude_technician_ids?: string[];
}

export interface AvailabilityResponse {
  business_id: string;
  service_id: string;
  service_name: string;
  available_dates: Record<string, TimeSlot[]>; // date -> slots
  total_slots: number;
  earliest_available?: string; // ISO datetime string
  latest_available?: string; // ISO datetime string
  estimated_duration_minutes: number;
  base_price?: number;
}

export interface BookingRequest {
  // Service Details
  business_id: string;
  service_id: string;
  
  // Scheduling
  requested_at: string; // ISO datetime string
  
  // Customer Information
  customer_name: string;
  customer_email?: string;
  customer_phone: string;
  
  // Service Address
  service_address: string;
  service_city?: string;
  service_state?: string;
  service_zip?: string;
  
  // Booking Details
  problem_description?: string;
  special_instructions?: string;
  access_instructions?: string;
  
  // Communication Preferences
  preferred_contact_method?: 'phone' | 'email' | 'sms';
  sms_consent: boolean;
  email_consent: boolean;
  
  // Metadata
  source?: 'website' | 'phone' | 'mobile_app' | 'referral' | 'walk_in';
  user_agent?: string;
  ip_address?: string;
  
  // Idempotency
  idempotency_key?: string;
}

export interface Booking {
  id: string;
  business_id: string;
  booking_number?: string;
  
  // Service Details
  service_id: string;
  service_name: string;
  estimated_duration_minutes: number;
  
  // Scheduling
  requested_at: string; // ISO datetime string
  scheduled_at?: string; // ISO datetime string
  completed_at?: string; // ISO datetime string
  
  // Assignment
  primary_technician_id?: string;
  additional_technicians: string[];
  
  // Customer Information
  customer_name: string;
  customer_email?: string;
  customer_phone: string;
  
  // Service Address
  service_address: string;
  service_city?: string;
  service_state?: string;
  service_zip?: string;
  service_coordinates?: [number, number];
  
  // Booking Details
  problem_description?: string;
  special_instructions?: string;
  access_instructions?: string;
  
  // Pricing
  quoted_price?: number;
  final_price?: number;
  
  // Status Tracking
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';
  cancellation_reason?: string;
  cancelled_by?: string;
  cancelled_at?: string; // ISO datetime string
  
  // Communication Preferences
  preferred_contact_method: 'phone' | 'email' | 'sms';
  sms_consent: boolean;
  email_consent: boolean;
  
  // Metadata
  source: 'website' | 'phone' | 'mobile_app' | 'referral' | 'walk_in';
  user_agent?: string;
  ip_address?: string;
  idempotency_key?: string;
  
  // Timestamps
  created_at?: string; // ISO datetime string
  updated_at?: string; // ISO datetime string
}

export interface BookingResponse {
  booking: Booking;
  message: string;
  next_steps: string[];
  
  // Additional info
  estimated_arrival_time?: string; // ISO datetime string
  technician_info?: {
    name?: string;
    phone?: string;
    photo?: string;
  };
  payment_info?: {
    cancellation_fee?: number;
    refund_amount?: number;
  };
}

export interface BookableService {
  id: string;
  business_id: string;
  name: string;
  category?: string;
  description?: string;
  is_bookable: boolean;
  requires_site_visit: boolean;
  estimated_duration_minutes: number;
  min_duration_minutes?: number;
  max_duration_minutes?: number;
  base_price?: number;
  price_type: 'fixed' | 'hourly' | 'estimate';
  required_skills: string[];
  min_technicians: number;
  max_technicians: number;
  min_lead_time_hours: number;
  max_advance_days: number;
  available_days: number[]; // 1=Monday, 7=Sunday
  available_times: {
    start: string; // HH:MM
    end: string; // HH:MM
  };
  created_at?: string;
  updated_at?: string;
}

export interface BookingFormData {
  // Service Selection
  serviceId: string;
  
  // Date & Time Selection
  selectedDate: Date;
  selectedTimeSlot: TimeSlot;
  
  // Customer Information
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  
  // Service Address
  serviceAddress: string;
  serviceCity: string;
  serviceState: string;
  serviceZip: string;
  
  // Service Details
  problemDescription: string;
  specialInstructions: string;
  accessInstructions: string;
  
  // Preferences
  preferredContactMethod: 'phone' | 'email' | 'sms';
  smsConsent: boolean;
  emailConsent: boolean;
}

export interface BookingStep {
  id: string;
  title: string;
  description: string;
  isComplete: boolean;
  isActive: boolean;
}

export interface BookingWizardProps {
  businessId: string;
  services: BookableService[];
  onBookingComplete?: (booking: Booking) => void;
  onBookingError?: (error: string) => void;
  className?: string;
}

export interface ServiceSelectorProps {
  services: BookableService[];
  selectedServiceId?: string;
  onServiceSelect: (serviceId: string) => void;
  className?: string;
}

export interface DateTimeSelectorProps {
  businessId: string;
  serviceId: string;
  selectedDate?: Date;
  selectedTimeSlot?: TimeSlot;
  onDateSelect: (date: Date) => void;
  onTimeSlotSelect: (slot: TimeSlot) => void;
  className?: string;
}

export interface CustomerFormProps {
  formData: Partial<BookingFormData>;
  onFormDataChange: (data: Partial<BookingFormData>) => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
  className?: string;
}

export interface BookingConfirmationProps {
  booking: Booking;
  onNewBooking?: () => void;
  className?: string;
}
