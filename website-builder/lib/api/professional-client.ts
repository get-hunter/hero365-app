/**
 * Contractors API Client
 * 
 * Client for interacting with the public contractors API endpoints
 */

import { buildPublicApiUrl, getDefaultHeaders } from '@/lib/shared/config/api-config';

export interface ProfessionalProfile {
  business_id: string;
  business_name: string;
  trade_type: string;
  description: string;
  phone: string;
  email: string;
  address: string;
  website?: string;
  service_areas: string[];
  emergency_service: boolean;
  years_in_business?: number;
  license_number?: string;
  insurance_verified: boolean;
  average_rating?: number;
  total_reviews?: number;
  certifications: string[];
}

export interface ServiceItem {
  id: string;
  name: string;
  description: string;
  category: string;
  base_price?: number;
  price_range_min?: number;
  price_range_max?: number;
  pricing_unit: string;
  duration_minutes?: number;
  is_emergency: boolean;
  requires_quote: boolean;
  available: boolean;
  service_areas: string[];
  keywords: string[];
}

export interface ProductItem {
  id: string;
  name: string;
  description: string;
  category: string;
  brand?: string;
  model?: string;
  sku?: string;
  price: number;
  msrp?: number;
  in_stock: boolean;
  stock_quantity: number;
  specifications: Record<string, string>;
  warranty_years?: number;
  energy_rating?: string;
}

export interface AvailabilitySlot {
  slot_date: string; // ISO date
  start_time: string; // HH:MM format
  end_time: string; // HH:MM format
  slot_type: string;
  duration_minutes: number;
  available: boolean;
}

export class ProfessionalApiClient {
  constructor() {
    // Configuration is handled centrally
  }

  /**
   * Get professional profile information
   */
  async getProfessionalProfile(businessId: string): Promise<ProfessionalProfile> {
    // Use server-side proxy to avoid browser CORS/connectivity issues
    const url = `/api/contractors/${businessId}`;
    
    console.log('🔍 [DEBUG] Fetching profile via proxy:', url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    console.log('✅ [DEBUG] Proxy response:', response.status, response.statusText);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Professional profile not found');
      }
      const error = await response.json().catch(() => ({ error: 'Failed to get professional profile' }));
      throw new Error(error.error || 'Failed to get professional profile');
    }

    const data = await response.json();
    console.log('✅ [DEBUG] Profile data received:', data.business_name);
    return data;
  }

  /**
   * Get professional services
   */
  async getProfessionalServices(
    businessId: string, 
    options: {
      category?: string;
      emergencyOnly?: boolean;
    } = {}
  ): Promise<ServiceItem[]> {
    const params = new URLSearchParams();
    if (options.category) {
      params.append('category', options.category);
    }
    if (options.emergencyOnly) {
      params.append('emergency_only', 'true');
    }

    // Use server-side proxy to avoid browser CORS/connectivity issues
    const url = `/api/contractors/${businessId}/services${params.toString() ? '?' + params.toString() : ''}`;
    
    console.log('🔍 [DEBUG] Fetching services via proxy:', url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        console.log('⚠️ [DEBUG] No services found, returning empty array');
        return []; // No services found
      }
      const error = await response.json().catch(() => ({ error: 'Failed to get professional services' }));
      throw new Error(error.error || 'Failed to get professional services');
    }

    const data = await response.json();
    console.log('✅ [DEBUG] Services data received:', data.length, 'items');
    return data;
  }

  /**
   * Get professional products
   */
  async getProfessionalProducts(
    businessId: string,
    options: {
      category?: string;
      inStockOnly?: boolean;
    } = {}
  ): Promise<ProductItem[]> {
    const params = new URLSearchParams();
    if (options.category) {
      params.append('category', options.category);
    }
    if (options.inStockOnly !== undefined) {
      params.append('in_stock_only', options.inStockOnly.toString());
    }

    const url = buildPublicApiUrl(`contractors/products/${businessId}${params.toString() ? '?' + params.toString() : ''}`);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: getDefaultHeaders(),
    });

    if (!response.ok) {
      if (response.status === 404) {
        return []; // No products found
      }
      const error = await response.json().catch(() => ({ detail: 'Failed to get professional products' }));
      throw new Error(error.detail || 'Failed to get professional products');
    }

    return response.json();
  }

  /**
   * Get professional availability
   */
  async getProfessionalAvailability(
    businessId: string,
    startDate: string, // ISO date
    endDate: string    // ISO date
  ): Promise<AvailabilitySlot[]> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate
    });

    const url = buildPublicApiUrl(`contractors/availability/${businessId}?${params}`);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: getDefaultHeaders(),
    });

    if (!response.ok) {
      if (response.status === 404) {
        return []; // No availability found
      }
      const error = await response.json().catch(() => ({ detail: 'Failed to get professional availability' }));
      throw new Error(error.detail || 'Failed to get professional availability');
    }

    return response.json();
  }

  /**
   * Convert ServiceItem to BookableService format for compatibility
   */
  serviceItemToBookableService(service: ServiceItem) {
    return {
      id: service.id,
      name: service.name,
      description: service.description,
      category: service.category,
      duration_minutes: service.duration_minutes || 60,
      price_cents: service.base_price ? Math.round(service.base_price * 100) : 0,
      is_emergency: service.is_emergency
    };
  }

  /**
   * Get services in BookableService format for booking widget
   */
  async getBookableServices(businessId: string, category?: string) {
    const services = await this.getProfessionalServices(businessId, { category });
    return services.map(service => this.serviceItemToBookableService(service));
  }
}

// Default client instance
export const professionalApi = new ProfessionalApiClient();
