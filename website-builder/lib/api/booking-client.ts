/**
 * Booking API Client
 * 
 * Client for interacting with the Hero365 booking API
 */

import { 
  AvailabilityRequest, 
  AvailabilityResponse, 
  BookingRequest, 
  BookingResponse, 
  Booking,
  BookableService,
  TimeSlot
} from '../types/booking';

export class BookingApiClient {
  private baseUrl: string;
  
  constructor(baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  /**
   * Get available time slots for a service
   */
  async getAvailability(request: AvailabilityRequest): Promise<AvailabilityResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/bookings/availability`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get availability' }));
      throw new Error(error.detail || 'Failed to get availability');
    }

    return response.json();
  }

  /**
   * Get the next available time slot for a service
   */
  async getNextAvailableSlot(
    businessId: string, 
    serviceId: string, 
    preferredDate?: string
  ): Promise<TimeSlot> {
    const params = new URLSearchParams({
      business_id: businessId,
      service_id: serviceId,
    });
    
    if (preferredDate) {
      params.append('preferred_date', preferredDate);
    }

    const response = await fetch(`${this.baseUrl}/api/v1/bookings/availability/next-slot?${params}`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'No available slots found' }));
      throw new Error(error.detail || 'No available slots found');
    }

    return response.json();
  }

  /**
   * Create a new booking
   */
  async createBooking(request: BookingRequest, autoConfirm: boolean = false): Promise<BookingResponse> {
    const params = new URLSearchParams();
    if (autoConfirm) {
      params.append('auto_confirm', 'true');
    }

    const url = `${this.baseUrl}/api/v1/bookings${params.toString() ? '?' + params.toString() : ''}`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create booking' }));
      throw new Error(error.detail || 'Failed to create booking');
    }

    return response.json();
  }

  /**
   * Get booking details by ID
   */
  async getBooking(bookingId: string): Promise<Booking> {
    const response = await fetch(`${this.baseUrl}/api/v1/bookings/${bookingId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Booking not found' }));
      throw new Error(error.detail || 'Booking not found');
    }

    return response.json();
  }

  /**
   * Reschedule an existing booking
   */
  async rescheduleBooking(
    bookingId: string, 
    newScheduledAt: string, 
    reason?: string,
    notifyCustomer: boolean = true
  ): Promise<BookingResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/bookings/${bookingId}/reschedule`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        booking_id: bookingId,
        new_scheduled_at: newScheduledAt,
        reason,
        notify_customer: notifyCustomer,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to reschedule booking' }));
      throw new Error(error.detail || 'Failed to reschedule booking');
    }

    return response.json();
  }

  /**
   * Cancel an existing booking
   */
  async cancelBooking(
    bookingId: string, 
    reason: string,
    cancelledBy: string = 'customer',
    refundAmount?: number,
    notifyCustomer: boolean = true
  ): Promise<BookingResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/bookings/${bookingId}/cancel`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        booking_id: bookingId,
        reason,
        cancelled_by: cancelledBy,
        refund_amount: refundAmount,
        notify_customer: notifyCustomer,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to cancel booking' }));
      throw new Error(error.detail || 'Failed to cancel booking');
    }

    return response.json();
  }

  /**
   * Generate a unique idempotency key for booking requests
   */
  generateIdempotencyKey(): string {
    return `booking_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Format date for API requests
   */
  formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }

  /**
   * Format datetime for API requests
   */
  formatDateTime(date: Date): string {
    return date.toISOString();
  }

  /**
   * Parse datetime from API responses
   */
  parseDateTime(dateString: string): Date {
    return new Date(dateString);
  }

  /**
   * Get user's IP address for booking requests
   */
  async getUserIpAddress(): Promise<string | undefined> {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch (error) {
      console.warn('Failed to get user IP address:', error);
      return undefined;
    }
  }

  /**
   * Get user agent string for booking requests
   */
  getUserAgent(): string {
    return typeof navigator !== 'undefined' ? navigator.userAgent : '';
  }
}

// Default client instance
export const bookingApi = new BookingApiClient();
