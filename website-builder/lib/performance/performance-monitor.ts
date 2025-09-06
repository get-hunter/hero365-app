/**
 * Performance Monitoring System
 * 
 * Comprehensive performance tracking for Core Web Vitals,
 * business metrics, and user experience optimization
 */

// Performance metric types
export interface CoreWebVitals {
  FCP?: number; // First Contentful Paint
  LCP?: number; // Largest Contentful Paint
  FID?: number; // First Input Delay
  CLS?: number; // Cumulative Layout Shift
  TTFB?: number; // Time to First Byte
  INP?: number; // Interaction to Next Paint
}

export interface BusinessMetrics {
  pageLoadTime: number;
  apiResponseTime: number;
  dataFetchTime: number;
  componentRenderTime: number;
  userEngagementTime: number;
  conversionFunnelStep?: string;
}

export interface UserExperienceMetrics {
  deviceType: 'mobile' | 'tablet' | 'desktop';
  connectionType: string;
  viewportSize: { width: number; height: number };
  scrollDepth: number;
  clicksCount: number;
  formInteractions: number;
  errorCount: number;
}

export interface PerformanceEvent {
  type: 'web-vital' | 'business' | 'user-experience' | 'error';
  name: string;
  value: number;
  timestamp: number;
  sessionId: string;
  pageUrl: string;
  businessId?: string;
  metadata?: Record<string, any>;
}

/**
 * Performance Monitor Class
 */
export class PerformanceMonitor {
  private sessionId: string;
  private businessId?: string;
  private events: PerformanceEvent[] = [];
  private observers: PerformanceObserver[] = [];
  private startTime: number;
  private isEnabled: boolean = true;

  constructor(businessId?: string) {
    this.sessionId = this.generateSessionId();
    this.businessId = businessId;
    this.startTime = performance.now();
    
    if (typeof window !== 'undefined') {
      this.initializeMonitoring();
    }
  }

  /**
   * Initialize all performance monitoring
   */
  private initializeMonitoring(): void {
    this.setupWebVitalsMonitoring();
    this.setupNavigationMonitoring();
    this.setupResourceMonitoring();
    this.setupUserInteractionMonitoring();
    this.setupErrorMonitoring();
    this.setupDataFetchMonitoring();
  }

  /**
   * Setup Core Web Vitals monitoring
   */
  private setupWebVitalsMonitoring(): void {
    // LCP (Largest Contentful Paint)
    if ('PerformanceObserver' in window) {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        this.recordEvent({
          type: 'web-vital',
          name: 'LCP',
          value: lastEntry.startTime,
          timestamp: Date.now(),
          sessionId: this.sessionId,
          pageUrl: window.location.href,
          businessId: this.businessId
        });
      });
      
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.push(lcpObserver);
    }

    // FID (First Input Delay)
    if ('PerformanceObserver' in window) {
      const fidObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordEvent({
            type: 'web-vital',
            name: 'FID',
            value: entry.processingStart - entry.startTime,
            timestamp: Date.now(),
            sessionId: this.sessionId,
            pageUrl: window.location.href,
            businessId: this.businessId
          });
        }
      });
      
      fidObserver.observe({ entryTypes: ['first-input'] });
      this.observers.push(fidObserver);
    }

    // CLS (Cumulative Layout Shift)
    if ('PerformanceObserver' in window) {
      let clsValue = 0;
      const clsObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }
        
        this.recordEvent({
          type: 'web-vital',
          name: 'CLS',
          value: clsValue,
          timestamp: Date.now(),
          sessionId: this.sessionId,
          pageUrl: window.location.href,
          businessId: this.businessId
        });
      });
      
      clsObserver.observe({ entryTypes: ['layout-shift'] });
      this.observers.push(clsObserver);
    }
  }

  /**
   * Setup navigation timing monitoring
   */
  private setupNavigationMonitoring(): void {
    window.addEventListener('load', () => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      
      if (navigation) {
        // TTFB (Time to First Byte)
        this.recordEvent({
          type: 'business',
          name: 'TTFB',
          value: navigation.responseStart - navigation.fetchStart,
          timestamp: Date.now(),
          sessionId: this.sessionId,
          pageUrl: window.location.href,
          businessId: this.businessId
        });

        // Page Load Time
        this.recordEvent({
          type: 'business',
          name: 'PageLoadTime',
          value: navigation.loadEventEnd - navigation.fetchStart,
          timestamp: Date.now(),
          sessionId: this.sessionId,
          pageUrl: window.location.href,
          businessId: this.businessId
        });

        // DOM Content Loaded
        this.recordEvent({
          type: 'business',
          name: 'DOMContentLoaded',
          value: navigation.domContentLoadedEventEnd - navigation.fetchStart,
          timestamp: Date.now(),
          sessionId: this.sessionId,
          pageUrl: window.location.href,
          businessId: this.businessId
        });
      }
    });
  }

  /**
   * Setup resource loading monitoring
   */
  private setupResourceMonitoring(): void {
    if ('PerformanceObserver' in window) {
      const resourceObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const resource = entry as PerformanceResourceTiming;
          
          // Monitor slow resources
          if (resource.duration > 1000) {
            this.recordEvent({
              type: 'business',
              name: 'SlowResource',
              value: resource.duration,
              timestamp: Date.now(),
              sessionId: this.sessionId,
              pageUrl: window.location.href,
              businessId: this.businessId,
              metadata: {
                resourceName: resource.name,
                resourceType: resource.initiatorType
              }
            });
          }
        }
      });
      
      resourceObserver.observe({ entryTypes: ['resource'] });
      this.observers.push(resourceObserver);
    }
  }

  /**
   * Setup user interaction monitoring
   */
  private setupUserInteractionMonitoring(): void {
    let clickCount = 0;
    let scrollDepth = 0;
    let maxScrollDepth = 0;

    // Click tracking
    document.addEventListener('click', () => {
      clickCount++;
      this.recordEvent({
        type: 'user-experience',
        name: 'Click',
        value: clickCount,
        timestamp: Date.now(),
        sessionId: this.sessionId,
        pageUrl: window.location.href,
        businessId: this.businessId
      });
    });

    // Scroll depth tracking
    const trackScrollDepth = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
      scrollDepth = Math.round((scrollTop / documentHeight) * 100);
      
      if (scrollDepth > maxScrollDepth) {
        maxScrollDepth = scrollDepth;
        
        // Track milestone scroll depths
        if (maxScrollDepth >= 25 && maxScrollDepth % 25 === 0) {
          this.recordEvent({
            type: 'user-experience',
            name: 'ScrollDepth',
            value: maxScrollDepth,
            timestamp: Date.now(),
            sessionId: this.sessionId,
            pageUrl: window.location.href,
            businessId: this.businessId
          });
        }
      }
    };

    window.addEventListener('scroll', trackScrollDepth, { passive: true });

    // Form interaction tracking
    document.addEventListener('input', (event) => {
      if (event.target && (event.target as HTMLElement).tagName === 'INPUT') {
        this.recordEvent({
          type: 'user-experience',
          name: 'FormInteraction',
          value: 1,
          timestamp: Date.now(),
          sessionId: this.sessionId,
          pageUrl: window.location.href,
          businessId: this.businessId,
          metadata: {
            inputType: (event.target as HTMLInputElement).type
          }
        });
      }
    });
  }

  /**
   * Setup error monitoring
   */
  private setupErrorMonitoring(): void {
    window.addEventListener('error', (event) => {
      this.recordEvent({
        type: 'error',
        name: 'JavaScriptError',
        value: 1,
        timestamp: Date.now(),
        sessionId: this.sessionId,
        pageUrl: window.location.href,
        businessId: this.businessId,
        metadata: {
          message: event.message,
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno
        }
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.recordEvent({
        type: 'error',
        name: 'UnhandledPromiseRejection',
        value: 1,
        timestamp: Date.now(),
        sessionId: this.sessionId,
        pageUrl: window.location.href,
        businessId: this.businessId,
        metadata: {
          reason: event.reason
        }
      });
    });
  }

  /**
   * Setup data fetch monitoring
   */
  private setupDataFetchMonitoring(): void {
    // Monkey patch fetch to monitor API calls
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const startTime = performance.now();
      const url = args[0] as string;
      
      try {
        const response = await originalFetch(...args);
        const endTime = performance.now();
        
        this.recordEvent({
          type: 'business',
          name: 'APIResponse',
          value: endTime - startTime,
          timestamp: Date.now(),
          sessionId: this.sessionId,
          pageUrl: window.location.href,
          businessId: this.businessId,
          metadata: {
            url,
            status: response.status,
            ok: response.ok
          }
        });
        
        return response;
      } catch (error) {
        const endTime = performance.now();
        
        this.recordEvent({
          type: 'error',
          name: 'APIError',
          value: endTime - startTime,
          timestamp: Date.now(),
          sessionId: this.sessionId,
          pageUrl: window.location.href,
          businessId: this.businessId,
          metadata: {
            url,
            error: error instanceof Error ? error.message : 'Unknown error'
          }
        });
        
        throw error;
      }
    };
  }

  /**
   * Record a performance event
   */
  private recordEvent(event: PerformanceEvent): void {
    if (!this.isEnabled) return;

    this.events.push(event);
    
    // Send to analytics
    this.sendToAnalytics(event);
    
    // Log in development
    if (process.env.NODE_ENV === 'development') {
      console.log('📊 [PERFORMANCE]', event);
    }
  }

  /**
   * Send event to analytics service
   */
  private sendToAnalytics(event: PerformanceEvent): void {
    // Send to Google Analytics 4
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'performance_metric', {
        metric_name: event.name,
        metric_value: Math.round(event.value),
        metric_type: event.type,
        business_id: event.businessId,
        session_id: event.sessionId,
        custom_parameter_1: event.metadata?.resourceType || event.type,
        custom_parameter_2: event.metadata?.status || 'success'
      });
    }

    // Send to custom analytics endpoint (batch every 10 events or 30 seconds)
    if (this.events.length >= 10 || this.shouldFlushEvents()) {
      this.flushEvents();
    }
  }

  /**
   * Check if events should be flushed
   */
  private shouldFlushEvents(): boolean {
    const lastFlush = parseInt(sessionStorage.getItem('lastPerformanceFlush') || '0');
    return Date.now() - lastFlush > 30000; // 30 seconds
  }

  /**
   * Flush events to analytics endpoint
   */
  private async flushEvents(): Promise<void> {
    if (this.events.length === 0) return;

    const eventsToSend = [...this.events];
    this.events = [];

    try {
      await fetch('/api/analytics/performance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: this.sessionId,
          businessId: this.businessId,
          events: eventsToSend,
          userAgent: navigator.userAgent,
          timestamp: Date.now()
        })
      });

      sessionStorage.setItem('lastPerformanceFlush', Date.now().toString());
    } catch (error) {
      // Re-add events if sending failed
      this.events.unshift(...eventsToSend);
      console.warn('Failed to send performance events:', error);
    }
  }

  /**
   * Manual event tracking
   */
  public trackBusinessMetric(name: string, value: number, metadata?: Record<string, any>): void {
    this.recordEvent({
      type: 'business',
      name,
      value,
      timestamp: Date.now(),
      sessionId: this.sessionId,
      pageUrl: window.location.href,
      businessId: this.businessId,
      metadata
    });
  }

  /**
   * Track conversion funnel steps
   */
  public trackConversionStep(step: string, value: number = 1): void {
    this.recordEvent({
      type: 'business',
      name: 'ConversionStep',
      value,
      timestamp: Date.now(),
      sessionId: this.sessionId,
      pageUrl: window.location.href,
      businessId: this.businessId,
      metadata: { step }
    });
  }

  /**
   * Generate unique session ID
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get performance summary
   */
  public getPerformanceSummary(): {
    webVitals: CoreWebVitals;
    businessMetrics: Partial<BusinessMetrics>;
    sessionDuration: number;
    eventsCount: number;
  } {
    const webVitals: CoreWebVitals = {};
    const businessMetrics: Partial<BusinessMetrics> = {};
    
    this.events.forEach(event => {
      if (event.type === 'web-vital') {
        (webVitals as any)[event.name] = event.value;
      } else if (event.type === 'business') {
        (businessMetrics as any)[event.name] = event.value;
      }
    });

    return {
      webVitals,
      businessMetrics,
      sessionDuration: performance.now() - this.startTime,
      eventsCount: this.events.length
    };
  }

  /**
   * Cleanup observers and flush remaining events
   */
  public cleanup(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.flushEvents();
    this.isEnabled = false;
  }
}

// Global performance monitor instance
let performanceMonitor: PerformanceMonitor | null = null;

/**
 * Initialize performance monitoring
 */
export function initializePerformanceMonitoring(businessId?: string): PerformanceMonitor {
  if (!performanceMonitor && typeof window !== 'undefined') {
    performanceMonitor = new PerformanceMonitor(businessId);
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
      performanceMonitor?.cleanup();
    });
  }
  
  return performanceMonitor!;
}

/**
 * Get the global performance monitor
 */
export function getPerformanceMonitor(): PerformanceMonitor | null {
  return performanceMonitor;
}

/**
 * Track a business metric
 */
export function trackBusinessMetric(name: string, value: number, metadata?: Record<string, any>): void {
  performanceMonitor?.trackBusinessMetric(name, value, metadata);
}

/**
 * Track conversion funnel step
 */
export function trackConversionStep(step: string, value?: number): void {
  performanceMonitor?.trackConversionStep(step, value);
}

export default PerformanceMonitor;
