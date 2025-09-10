/**
 * Booking Analytics Service
 * 
 * Tracks booking funnel events and user behavior
 */

export interface BookingAnalyticsEvent {
  event: string;
  properties: Record<string, any>;
  timestamp?: string;
  sessionId?: string;
  userId?: string;
}

export interface BookingFunnelStep {
  step: 'zip_gate' | 'category' | 'address' | 'datetime' | 'contact' | 'details' | 'review' | 'confirmation';
  action: 'view' | 'next' | 'back' | 'abandon' | 'error' | 'complete';
  metadata?: Record<string, any>;
}

export interface BookingConversionData {
  businessId: string;
  sessionId: string;
  zipCode?: string;
  countryCode?: string;
  serviceCategory?: string;
  serviceId?: string;
  isSupported?: boolean;
  abandonedAt?: string;
  completedAt?: string;
  errorStep?: string;
  errorMessage?: string;
  totalDuration?: number; // in seconds
  stepDurations?: Record<string, number>; // step -> seconds
}

class BookingAnalyticsService {
  private sessionId: string;
  private sessionStartTime: number;
  private stepStartTimes: Record<string, number> = {};
  private conversionData: Partial<BookingConversionData> = {};
  private events: BookingAnalyticsEvent[] = [];

  constructor() {
    this.sessionId = this.generateSessionId();
    this.sessionStartTime = Date.now();
    this.conversionData.sessionId = this.sessionId;
  }

  /**
   * Track a booking funnel step event
   */
  trackStep(step: BookingFunnelStep['step'], action: BookingFunnelStep['action'], metadata?: Record<string, any>) {
    const now = Date.now();
    const event: BookingAnalyticsEvent = {
      event: `booking_${step}_${action}`,
      properties: {
        step,
        action,
        sessionId: this.sessionId,
        timestamp: new Date().toISOString(),
        sessionDuration: Math.round((now - this.sessionStartTime) / 1000),
        ...metadata
      },
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId
    };

    this.events.push(event);

    // Track step timing
    if (action === 'view') {
      this.stepStartTimes[step] = now;
    } else if (action === 'next' || action === 'back' || action === 'abandon') {
      const stepStartTime = this.stepStartTimes[step];
      if (stepStartTime) {
        const stepDuration = Math.round((now - stepStartTime) / 1000);
        event.properties.stepDuration = stepDuration;
        
        if (!this.conversionData.stepDurations) {
          this.conversionData.stepDurations = {};
        }
        this.conversionData.stepDurations[step] = stepDuration;
      }
    }

    // Update conversion data
    this.updateConversionData(step, action, metadata);

    // Send to analytics service (console for now, can be replaced with real service)
    this.sendEvent(event);
  }

  /**
   * Track ZIP code validation
   */
  trackZipValidation(zipCode: string, countryCode: string, isSupported: boolean, suggestions?: any[]) {
    this.conversionData.zipCode = zipCode;
    this.conversionData.countryCode = countryCode;
    this.conversionData.isSupported = isSupported;

    this.trackStep('zip_gate', isSupported ? 'next' : 'error', {
      zipCode,
      countryCode,
      isSupported,
      suggestionsCount: suggestions?.length || 0
    });
  }

  /**
   * Track service selection
   */
  trackServiceSelection(serviceCategory: string, serviceId: string) {
    this.conversionData.serviceCategory = serviceCategory;
    this.conversionData.serviceId = serviceId;

    this.trackStep('category', 'next', {
      serviceCategory,
      serviceId
    });
  }

  /**
   * Track booking completion
   */
  trackBookingComplete(bookingId: string, bookingData: any) {
    const now = Date.now();
    this.conversionData.completedAt = new Date().toISOString();
    this.conversionData.totalDuration = Math.round((now - this.sessionStartTime) / 1000);

    this.trackStep('confirmation', 'complete', {
      bookingId,
      totalDuration: this.conversionData.totalDuration,
      ...bookingData
    });
  }

  /**
   * Track booking abandonment
   */
  trackBookingAbandon(step: BookingFunnelStep['step'], reason?: string) {
    this.conversionData.abandonedAt = new Date().toISOString();
    this.conversionData.totalDuration = Math.round((Date.now() - this.sessionStartTime) / 1000);

    this.trackStep(step, 'abandon', {
      reason,
      totalDuration: this.conversionData.totalDuration
    });
  }

  /**
   * Track booking error
   */
  trackBookingError(step: BookingFunnelStep['step'], error: string | Error) {
    const errorMessage = typeof error === 'string' ? error : error.message;
    this.conversionData.errorStep = step;
    this.conversionData.errorMessage = errorMessage;

    this.trackStep(step, 'error', {
      error: errorMessage,
      errorType: typeof error === 'string' ? 'validation' : 'api'
    });
  }

  /**
   * Track custom event
   */
  trackCustomEvent(eventName: string, properties: Record<string, any>) {
    const event: BookingAnalyticsEvent = {
      event: eventName,
      properties: {
        sessionId: this.sessionId,
        timestamp: new Date().toISOString(),
        ...properties
      },
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId
    };

    this.events.push(event);
    this.sendEvent(event);
  }

  /**
   * Get current session analytics summary
   */
  getSessionSummary() {
    return {
      sessionId: this.sessionId,
      sessionDuration: Math.round((Date.now() - this.sessionStartTime) / 1000),
      eventsCount: this.events.length,
      conversionData: this.conversionData,
      events: this.events
    };
  }

  /**
   * Get conversion funnel metrics
   */
  getFunnelMetrics() {
    const stepCounts = this.events.reduce((acc, event) => {
      const step = event.properties.step;
      const action = event.properties.action;
      
      if (step && action) {
        if (!acc[step]) acc[step] = {};
        if (!acc[step][action]) acc[step][action] = 0;
        acc[step][action]++;
      }
      
      return acc;
    }, {} as Record<string, Record<string, number>>);

    return {
      sessionId: this.sessionId,
      stepCounts,
      stepDurations: this.conversionData.stepDurations,
      totalDuration: this.conversionData.totalDuration,
      completed: !!this.conversionData.completedAt,
      abandoned: !!this.conversionData.abandonedAt
    };
  }

  private updateConversionData(step: string, action: string, metadata?: Record<string, any>) {
    if (!this.conversionData.businessId && metadata?.businessId) {
      this.conversionData.businessId = metadata.businessId;
    }
  }

  private sendEvent(event: BookingAnalyticsEvent) {
    // For now, just log to console
    // In production, this would send to analytics service (Google Analytics, Mixpanel, etc.)
    console.log('📊 Booking Analytics:', event);

    // Example: Send to Google Analytics 4
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', event.event, {
        custom_parameter_1: event.properties.step,
        custom_parameter_2: event.properties.action,
        session_id: event.sessionId,
        ...event.properties
      });
    }

    // Example: Send to custom analytics endpoint (proxy to backend API base)
    if (typeof window !== 'undefined') {
      const base = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
      fetch(`${base}/public/analytics/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(event),
      }).catch(error => {
        console.warn('Failed to send analytics event:', error);
      });
    }
  }

  private generateSessionId(): string {
    return `booking_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Global analytics instance
let analyticsInstance: BookingAnalyticsService | null = null;

export const getBookingAnalytics = (): BookingAnalyticsService => {
  if (!analyticsInstance) {
    analyticsInstance = new BookingAnalyticsService();
  }
  return analyticsInstance;
};

// Hook for React components
export const useBookingAnalytics = () => {
  return getBookingAnalytics();
};

// Export the service class for direct instantiation
export { BookingAnalyticsService };
