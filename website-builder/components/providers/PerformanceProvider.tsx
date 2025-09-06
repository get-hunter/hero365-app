'use client';

/**
 * Performance Provider
 * 
 * Initializes performance monitoring for the entire application
 * Should be placed high in the component tree
 */

import React, { useEffect } from 'react';
import { initializePerformanceMonitoring, trackConversionStep } from '@/lib/performance/performance-monitor';
import { getUnifiedConfig, isFeatureEnabled } from '@/lib/config/unified-config';

interface PerformanceProviderProps {
  children: React.ReactNode;
  businessId?: string;
  pageName?: string;
}

export default function PerformanceProvider({ 
  children, 
  businessId,
  pageName = 'homepage'
}: PerformanceProviderProps) {
  useEffect(() => {
    // Only initialize if performance monitoring is enabled
    if (!isFeatureEnabled('performanceMonitoring')) {
      return;
    }

    const monitor = initializePerformanceMonitoring(businessId);
    
    // Track page view
    monitor.trackConversionStep('page_view');
    monitor.trackBusinessMetric('page_load_start', Date.now(), {
      page: pageName,
      businessId
    });

    // Track when page is fully loaded
    const handleLoad = () => {
      monitor.trackConversionStep('page_loaded');
      monitor.trackBusinessMetric('page_load_complete', Date.now(), {
        page: pageName,
        businessId
      });
    };

    // Track page visibility changes
    const handleVisibilityChange = () => {
      if (document.hidden) {
        monitor.trackConversionStep('page_hidden');
      } else {
        monitor.trackConversionStep('page_visible');
      }
    };

    // Track when user is about to leave
    const handleBeforeUnload = () => {
      monitor.trackConversionStep('page_exit');
      const summary = monitor.getPerformanceSummary();
      
      // Log performance summary in development
      if (process.env.NODE_ENV === 'development') {
        console.log('📊 [PERFORMANCE-SUMMARY]', summary);
      }
    };

    if (document.readyState === 'complete') {
      handleLoad();
    } else {
      window.addEventListener('load', handleLoad);
    }

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('load', handleLoad);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [businessId, pageName]);

  // Track React hydration completion
  useEffect(() => {
    if (isFeatureEnabled('performanceMonitoring')) {
      const monitor = initializePerformanceMonitoring(businessId);
      monitor.trackBusinessMetric('react_hydration_complete', Date.now(), {
        page: pageName
      });
    }
  }, [businessId, pageName]);

  return <>{children}</>;
}

/**
 * Hook for tracking custom performance metrics
 */
export function usePerformanceTracking(businessId?: string) {
  const trackMetric = React.useCallback((name: string, value: number, metadata?: Record<string, any>) => {
    if (!isFeatureEnabled('performanceMonitoring')) return;
    
    const monitor = initializePerformanceMonitoring(businessId);
    monitor.trackBusinessMetric(name, value, metadata);
  }, [businessId]);

  const trackConversion = React.useCallback((step: string, value?: number) => {
    if (!isFeatureEnabled('performanceMonitoring')) return;
    
    const monitor = initializePerformanceMonitoring(businessId);
    monitor.trackConversionStep(step, value);
  }, [businessId]);

  return { trackMetric, trackConversion };
}
