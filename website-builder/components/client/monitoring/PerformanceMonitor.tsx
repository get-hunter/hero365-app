/**
 * Performance Monitor Component - Client-Side Component
 * 
 * Monitors and reports website performance metrics:
 * - Core Web Vitals (LCP, FID, CLS)
 * - Page load times
 * - User interactions
 * - Business-specific metrics
 * 
 * This is a client-side component for real-time performance tracking.
 */

'use client';

import React, { useEffect, useRef } from 'react';
import { useABTesting } from '../testing/ABTestingProvider';

interface PerformanceMonitorProps {
  pageType: string;
  businessId: string;
  activitySlug?: string;
  enableRealUserMonitoring?: boolean;
  enableCoreWebVitals?: boolean;
  enableBusinessMetrics?: boolean;
}

interface PerformanceMetric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  timestamp: number;
}

interface BusinessMetric {
  type: 'page_view' | 'engagement' | 'conversion_funnel' | 'user_journey';
  data: Record<string, any>;
  timestamp: number;
}

export function PerformanceMonitor({
  pageType,
  businessId,
  activitySlug,
  enableRealUserMonitoring = true,
  enableCoreWebVitals = true,
  enableBusinessMetrics = true
}: PerformanceMonitorProps) {
  
  const { trackEvent } = useABTesting();
  const metricsRef = useRef<PerformanceMetric[]>([]);
  const businessMetricsRef = useRef<BusinessMetric[]>([]);
  const observersRef = useRef<PerformanceObserver[]>([]);
  
  useEffect(() => {
    if (!enableRealUserMonitoring) return;
    
    // Initialize performance monitoring
    initializePerformanceMonitoring();
    
    // Track page view
    trackPageView();
    
    // Setup engagement tracking
    if (enableBusinessMetrics) {
      setupEngagementTracking();
    }
    
    // Cleanup on unmount
    return () => {
      cleanup();
    };
  }, [pageType, businessId, activitySlug]);
  
  const initializePerformanceMonitoring = () => {
    // Core Web Vitals monitoring
    if (enableCoreWebVitals) {
      setupCoreWebVitalsMonitoring();
    }
    
    // Navigation timing
    setupNavigationTimingMonitoring();
    
    // Resource timing
    setupResourceTimingMonitoring();
    
    // User timing
    setupUserTimingMonitoring();
  };
  
  const setupCoreWebVitalsMonitoring = () => {
    // Largest Contentful Paint (LCP)
    if ('PerformanceObserver' in window) {
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1] as PerformanceEntry & { startTime: number };
          
          if (lastEntry) {
            const lcp = lastEntry.startTime;
            const rating = lcp <= 2500 ? 'good' : lcp <= 4000 ? 'needs-improvement' : 'poor';
            
            recordMetric({
              name: 'LCP',
              value: lcp,
              rating,
              timestamp: Date.now()
            });
          }
        });
        
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        observersRef.current.push(lcpObserver);
      } catch (error) {
        console.warn('LCP monitoring not supported:', error);
      }
      
      // First Input Delay (FID)
      try {
        const fidObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            const fid = entry.processingStart - entry.startTime;
            const rating = fid <= 100 ? 'good' : fid <= 300 ? 'needs-improvement' : 'poor';
            
            recordMetric({
              name: 'FID',
              value: fid,
              rating,
              timestamp: Date.now()
            });
          });
        });
        
        fidObserver.observe({ entryTypes: ['first-input'] });
        observersRef.current.push(fidObserver);
      } catch (error) {
        console.warn('FID monitoring not supported:', error);
      }
      
      // Cumulative Layout Shift (CLS)
      try {
        let clsValue = 0;
        const clsObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          });
          
          // Report CLS after a delay to capture most shifts
          setTimeout(() => {
            const rating = clsValue <= 0.1 ? 'good' : clsValue <= 0.25 ? 'needs-improvement' : 'poor';
            
            recordMetric({
              name: 'CLS',
              value: clsValue,
              rating,
              timestamp: Date.now()
            });
          }, 5000);
        });
        
        clsObserver.observe({ entryTypes: ['layout-shift'] });
        observersRef.current.push(clsObserver);
      } catch (error) {
        console.warn('CLS monitoring not supported:', error);
      }
    }
  };
  
  const setupNavigationTimingMonitoring = () => {
    // Wait for navigation timing to be available
    setTimeout(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      
      if (navigation) {
        // Time to First Byte (TTFB)
        const ttfb = navigation.responseStart - navigation.requestStart;
        const ttfbRating = ttfb <= 800 ? 'good' : ttfb <= 1800 ? 'needs-improvement' : 'poor';
        
        recordMetric({
          name: 'TTFB',
          value: ttfb,
          rating: ttfbRating,
          timestamp: Date.now()
        });
        
        // DOM Content Loaded
        const dcl = navigation.domContentLoadedEventEnd - navigation.navigationStart;
        const dclRating = dcl <= 1500 ? 'good' : dcl <= 3000 ? 'needs-improvement' : 'poor';
        
        recordMetric({
          name: 'DCL',
          value: dcl,
          rating: dclRating,
          timestamp: Date.now()
        });
        
        // Load Complete
        const loadComplete = navigation.loadEventEnd - navigation.navigationStart;
        const loadRating = loadComplete <= 2000 ? 'good' : loadComplete <= 4000 ? 'needs-improvement' : 'poor';
        
        recordMetric({
          name: 'Load',
          value: loadComplete,
          rating: loadRating,
          timestamp: Date.now()
        });
      }
    }, 1000);
  };
  
  const setupResourceTimingMonitoring = () => {
    // Monitor resource loading performance
    const resourceObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      
      entries.forEach((entry: PerformanceResourceTiming) => {
        // Track slow resources
        const duration = entry.responseEnd - entry.startTime;
        
        if (duration > 1000) { // Resources taking more than 1s
          recordBusinessMetric({
            type: 'page_view',
            data: {
              metric_type: 'slow_resource',
              resource_url: entry.name,
              duration,
              resource_type: entry.initiatorType,
              page_type: pageType
            },
            timestamp: Date.now()
          });
        }
      });
    });
    
    resourceObserver.observe({ entryTypes: ['resource'] });
    observersRef.current.push(resourceObserver);
  };
  
  const setupUserTimingMonitoring = () => {
    // Monitor custom user timing marks
    const userTimingObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      
      entries.forEach((entry) => {
        recordBusinessMetric({
          type: 'page_view',
          data: {
            metric_type: 'user_timing',
            name: entry.name,
            duration: entry.duration || entry.startTime,
            page_type: pageType
          },
          timestamp: Date.now()
        });
      });
    });
    
    userTimingObserver.observe({ entryTypes: ['measure', 'mark'] });
    observersRef.current.push(userTimingObserver);
  };
  
  const setupEngagementTracking = () => {
    let startTime = Date.now();
    let isVisible = true;
    let scrollDepth = 0;
    let maxScrollDepth = 0;
    
    // Track time on page
    const trackTimeOnPage = () => {
      if (isVisible) {
        const timeOnPage = Date.now() - startTime;
        
        recordBusinessMetric({
          type: 'engagement',
          data: {
            metric_type: 'time_on_page',
            duration: timeOnPage,
            page_type: pageType,
            activity_slug: activitySlug,
            scroll_depth: maxScrollDepth
          },
          timestamp: Date.now()
        });
      }
    };
    
    // Track scroll depth
    const trackScrollDepth = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      
      scrollDepth = Math.round(((scrollTop + windowHeight) / documentHeight) * 100);
      maxScrollDepth = Math.max(maxScrollDepth, scrollDepth);
      
      // Track milestone scroll depths
      if (scrollDepth >= 25 && scrollDepth < 50 && maxScrollDepth >= 25) {
        recordBusinessMetric({
          type: 'engagement',
          data: {
            metric_type: 'scroll_depth',
            depth: 25,
            page_type: pageType
          },
          timestamp: Date.now()
        });
      }
    };
    
    // Track visibility changes
    const handleVisibilityChange = () => {
      if (document.hidden) {
        isVisible = false;
        trackTimeOnPage();
      } else {
        isVisible = true;
        startTime = Date.now();
      }
    };
    
    // Event listeners
    window.addEventListener('scroll', trackScrollDepth, { passive: true });
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('beforeunload', trackTimeOnPage);
    
    // Cleanup function
    const cleanupEngagement = () => {
      window.removeEventListener('scroll', trackScrollDepth);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('beforeunload', trackTimeOnPage);
    };
    
    // Store cleanup function
    (window as any).__performanceCleanup = cleanupEngagement;
  };
  
  const trackPageView = () => {
    recordBusinessMetric({
      type: 'page_view',
      data: {
        page_type: pageType,
        activity_slug: activitySlug,
        business_id: businessId,
        user_agent: navigator.userAgent,
        viewport_width: window.innerWidth,
        viewport_height: window.innerHeight,
        connection_type: (navigator as any).connection?.effectiveType || 'unknown'
      },
      timestamp: Date.now()
    });
  };
  
  const recordMetric = (metric: PerformanceMetric) => {
    metricsRef.current.push(metric);
    
    // Send to analytics
    trackEvent('performance_metric', {
      metric_name: metric.name,
      metric_value: metric.value,
      metric_rating: metric.rating,
      page_type: pageType,
      business_id: businessId
    });
    
    // Log poor performance
    if (metric.rating === 'poor') {
      console.warn(`⚠️ Poor ${metric.name} performance:`, metric.value);
    }
    
    // Send to monitoring service
    sendToMonitoringService(metric);
  };
  
  const recordBusinessMetric = (metric: BusinessMetric) => {
    businessMetricsRef.current.push(metric);
    
    // Send to analytics
    trackEvent('business_metric', {
      metric_type: metric.type,
      metric_data: metric.data,
      page_type: pageType,
      business_id: businessId
    });
  };
  
  const sendToMonitoringService = async (metric: PerformanceMetric) => {
    try {
      // In production, send to your monitoring service
      // await fetch('/api/monitoring/performance', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({
      //     ...metric,
      //     page_type: pageType,
      //     business_id: businessId,
      //     activity_slug: activitySlug
      //   })
      // });
      
      // For now, store locally
      const metrics = JSON.parse(localStorage.getItem('performance_metrics') || '[]');
      metrics.push({
        ...metric,
        page_type: pageType,
        business_id: businessId,
        activity_slug: activitySlug
      });
      
      // Keep only last 50 metrics
      if (metrics.length > 50) {
        metrics.splice(0, metrics.length - 50);
      }
      
      localStorage.setItem('performance_metrics', JSON.stringify(metrics));
      
    } catch (error) {
      console.error('Failed to send performance metric:', error);
    }
  };
  
  const cleanup = () => {
    // Disconnect all observers
    observersRef.current.forEach(observer => {
      observer.disconnect();
    });
    
    // Cleanup engagement tracking
    if ((window as any).__performanceCleanup) {
      (window as any).__performanceCleanup();
    }
  };
  
  // This component doesn't render anything visible
  return null;
}

/**
 * Hook for manual performance marking
 */
export function usePerformanceMarking() {
  const markStart = (name: string) => {
    if ('performance' in window && 'mark' in performance) {
      performance.mark(`${name}-start`);
    }
  };
  
  const markEnd = (name: string) => {
    if ('performance' in window && 'mark' in performance && 'measure' in performance) {
      performance.mark(`${name}-end`);
      performance.measure(name, `${name}-start`, `${name}-end`);
    }
  };
  
  return { markStart, markEnd };
}

/**
 * Hook for conversion funnel tracking
 */
export function useConversionFunnel(funnelName: string) {
  const { trackEvent } = useABTesting();
  
  const trackFunnelStep = (step: string, data?: Record<string, any>) => {
    trackEvent('conversion_funnel', {
      funnel_name: funnelName,
      step,
      ...data
    });
  };
  
  return { trackFunnelStep };
}
