/**
 * Service Areas API Client
 * 
 * Client for interacting with the service areas API
 */

import { getApiConfig, buildPublicApiUrl, getDefaultHeaders } from '../config/api-config';

export interface ServiceAreaCheckRequest {
  business_id: string;
  postal_code: string;
  country_code?: string;
}

export interface ServiceAreaCheckResponse {
  supported: boolean;
  normalized?: {
    postal_code: string;
    country_code: string;
    city?: string;
    region?: string;
    timezone: string;
    dispatch_fee_cents: number;
    min_response_time_hours: number;
    max_response_time_hours: number;
    emergency_available: boolean;
    regular_available: boolean;
  };
  suggestions?: Array<{
    postal_code: string;
    city?: string;
    region?: string;
    distance_estimate: string;
  }>;
  message?: string;
}

export interface AvailabilityRequestCreate {
  business_id: string;
  contact_name: string;
  phone_e164?: string;
  email?: string;
  postal_code: string;
  country_code?: string;
  city?: string;
  region?: string;
  service_category?: string;
  service_type?: string;
  urgency_level?: 'emergency' | 'urgent' | 'normal' | 'flexible';
  preferred_contact_method?: 'phone' | 'email' | 'sms';
  notes?: string;
  source?: string;
  referrer_url?: string;
  user_agent?: string;
}

export interface AvailabilityRequestResponse {
  created: boolean;
  id: string;
  message?: string;
}

export class ServiceAreasApiClient {
  private config = getApiConfig();
  
  constructor() {
    // Configuration is now handled centrally
  }

  /**
   * Check if a postal code is supported by a business
   */
  async checkServiceAreaSupport(request: ServiceAreaCheckRequest): Promise<ServiceAreaCheckResponse> {
    const params = new URLSearchParams({
      business_id: request.business_id,
      postal_code: request.postal_code,
      country_code: request.country_code || 'US'
    });

    const url = buildPublicApiUrl(`service-areas/check?${params}`);
    const response = await fetch(url, {
      method: 'GET',
      headers: getDefaultHeaders(),
    });

    if (!response.ok) {
      // If the API returns 404 or other errors, treat as unsupported
      if (response.status === 404) {
        return {
          supported: false,
          message: 'Service area not found'
        };
      }
      
      const error = await response.json().catch(() => ({ detail: 'Failed to check service area' }));
      throw new Error(error.detail || 'Failed to check service area');
    }

    return response.json();
  }

  /**
   * Create an availability request for unsupported areas
   */
  async createAvailabilityRequest(request: AvailabilityRequestCreate): Promise<AvailabilityRequestResponse> {
    const url = buildPublicApiUrl('availability/request');
    const response = await fetch(url, {
      method: 'POST',
      headers: getDefaultHeaders(),
      body: JSON.stringify({
        ...request,
        source: request.source || 'booking_widget',
        referrer_url: request.referrer_url || (typeof window !== 'undefined' ? window.location.href : undefined),
        user_agent: request.user_agent || (typeof navigator !== 'undefined' ? navigator.userAgent : undefined)
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create availability request' }));
      throw new Error(error.detail || 'Failed to create availability request');
    }

    return response.json();
  }

  /**
   * Get available time slots for a service in a specific area
   */
  async getAvailableSlots(request: {
    business_id: string;
    service_id: string;
    postal_code: string;
    country_code?: string;
    timezone: string;
    date_range: {
      from: string; // ISO date
      to: string;   // ISO date
    };
  }): Promise<{
    slots: Array<{
      start: string; // ISO datetime
      end: string;   // ISO datetime
      capacity?: number;
    }>;
    first_available?: {
      start: string;
      end: string;
    };
  }> {
    const url = buildPublicApiUrl('availability/slots');
    const response = await fetch(url, {
      method: 'POST',
      headers: getDefaultHeaders(),
      body: JSON.stringify({
        ...request,
        country_code: request.country_code || 'US'
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get available slots' }));
      throw new Error(error.detail || 'Failed to get available slots');
    }

    return response.json();
  }

  /**
   * Normalize a postal code for consistent formatting
   */
  normalizePostalCode(postalCode: string, countryCode: string = 'US'): string {
    // Remove all non-alphanumeric characters and convert to uppercase
    let normalized = postalCode.replace(/[^A-Za-z0-9]/g, '').toUpperCase();
    
    // Country-specific formatting
    switch (countryCode.toUpperCase()) {
      case 'US':
        // US ZIP codes: 5 digits or 5+4 format
        if (normalized.length >= 5) {
          normalized = normalized.substring(0, 5);
        }
        break;
      case 'CA':
        // Canadian postal codes: A1A1A1 format
        if (normalized.length >= 6) {
          normalized = normalized.substring(0, 6);
        }
        break;
      default:
        // Keep as-is for other countries
        break;
    }
    
    return normalized;
  }

  /**
   * Validate postal code format
   */
  validatePostalCode(postalCode: string, countryCode: string = 'US'): boolean {
    const normalized = this.normalizePostalCode(postalCode, countryCode);
    
    switch (countryCode.toUpperCase()) {
      case 'US':
        return /^\d{5}$/.test(normalized);
      case 'CA':
        return /^[A-Z]\d[A-Z]\d[A-Z]\d$/.test(normalized);
      case 'GB':
        return /^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$/i.test(postalCode);
      default:
        return normalized.length >= 3; // Basic validation for other countries
    }
  }

  /**
   * Get country-specific postal code placeholder
   */
  getPostalCodePlaceholder(countryCode: string = 'US'): string {
    switch (countryCode.toUpperCase()) {
      case 'US':
        return '12345';
      case 'CA':
        return 'A1A 1A1';
      case 'GB':
        return 'SW1A 1AA';
      case 'AU':
        return '2000';
      default:
        return 'Enter postal code';
    }
  }

  /**
   * Get country-specific postal code label
   */
  getPostalCodeLabel(countryCode: string = 'US'): string {
    switch (countryCode.toUpperCase()) {
      case 'US':
        return 'ZIP Code';
      case 'CA':
      case 'GB':
      case 'AU':
        return 'Postal Code';
      default:
        return 'Postal Code';
    }
  }
}

// Default client instance
export const serviceAreasApi = new ServiceAreasApiClient();
