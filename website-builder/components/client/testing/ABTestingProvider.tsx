/**
 * A/B Testing Provider
 * 
 * Provides A/B testing functionality for SEO artifacts with
 * variant selection, performance tracking, and analytics.
 */

'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { ContentVariant, ABTestConfig, ABTestContextValue } from '@/lib/shared/types/seo-artifacts';

const ABTestContext = createContext<ABTestContextValue | null>(null);

interface ABTestingProviderProps extends ABTestConfig {
  children: React.ReactNode;
}

export function ABTestingProvider({
  enabled,
  variants,
  activeExperiments,
  artifactId,
  businessId,
  children
}: ABTestingProviderProps) {
  const [selectedVariants, setSelectedVariants] = useState<Record<string, string>>({});
  const [sessionId] = useState(() => generateSessionId());

  // Initialize variant selection on mount
  useEffect(() => {
    if (!enabled) return;

    const newSelections: Record<string, string> = {};
    
    Object.entries(variants).forEach(([testKey, testVariants]) => {
      if (activeExperiments.includes(testKey) && testVariants.length > 0) {
        // Check for existing selection in session storage
        const storageKey = `ab_test_${testKey}_${artifactId}`;
        const existingSelection = sessionStorage.getItem(storageKey);
        
        if (existingSelection && testVariants.some(v => v.variant_key === existingSelection)) {
          newSelections[testKey] = existingSelection;
        } else {
          // Select variant based on weighted distribution
          const selectedVariant = selectWeightedVariant(testVariants);
          newSelections[testKey] = selectedVariant.variant_key;
          sessionStorage.setItem(storageKey, selectedVariant.variant_key);
        }
      }
    });

    setSelectedVariants(newSelections);
  }, [enabled, variants, activeExperiments, artifactId]);

  const getVariant = useCallback((testKey: string, defaultContent: any) => {
    if (!enabled || !activeExperiments.includes(testKey)) {
      return defaultContent;
    }

    const selectedVariantKey = selectedVariants[testKey];
    if (!selectedVariantKey) {
      return defaultContent;
    }

    const testVariants = variants[testKey] || [];
    const selectedVariant = testVariants.find(v => v.variant_key === selectedVariantKey);
    
    if (selectedVariant) {
      return { ...defaultContent, ...selectedVariant.content };
    }

    return defaultContent;
  }, [enabled, activeExperiments, selectedVariants, variants]);

  const trackEvent = useCallback((eventName: string, testKey?: string, variantKey?: string) => {
    if (!enabled) return;

    const eventData = {
      event: eventName,
      timestamp: new Date().toISOString(),
      sessionId,
      businessId,
      artifactId,
      testKey,
      variantKey: variantKey || (testKey ? selectedVariants[testKey] : undefined),
      url: window.location.href,
      userAgent: navigator.userAgent
    };

    // Send to analytics endpoint
    if (typeof window !== 'undefined') {
      fetch('/api/v1/analytics/ab-test-events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventData)
      }).catch(error => {
        console.warn('Failed to track A/B test event:', error);
      });
    }

    // Also track with Google Analytics if available
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', eventName, {
        custom_parameter_1: testKey,
        custom_parameter_2: variantKey,
        custom_parameter_3: artifactId
      });
    }
  }, [enabled, sessionId, businessId, artifactId, selectedVariants]);

  const isExperimentActive = useCallback((testKey: string) => {
    return enabled && activeExperiments.includes(testKey);
  }, [enabled, activeExperiments]);

  // Track page view on mount
  useEffect(() => {
    if (enabled && Object.keys(selectedVariants).length > 0) {
      Object.entries(selectedVariants).forEach(([testKey, variantKey]) => {
        trackEvent('page_view', testKey, variantKey);
      });
    }
  }, [enabled, selectedVariants, trackEvent]);

  const contextValue: ABTestContextValue = {
    getVariant,
    trackEvent,
    isExperimentActive
  };

  return (
    <ABTestContext.Provider value={contextValue}>
      {children}
    </ABTestContext.Provider>
  );
}

export function useABTest() {
  const context = useContext(ABTestContext);
  if (!context) {
    // Return no-op functions if not in testing context
    return {
      getVariant: (testKey: string, defaultContent: any) => defaultContent,
      trackEvent: () => {},
      isExperimentActive: () => false
    };
  }
  return context;
}

/**
 * Hook for tracking specific A/B test interactions
 */
export function useABTestTracking(testKey: string) {
  const { trackEvent, isExperimentActive } = useABTest();
  
  const trackClick = useCallback((elementName?: string) => {
    if (isExperimentActive(testKey)) {
      trackEvent('click', testKey);
      if (elementName) {
        trackEvent(`click_${elementName}`, testKey);
      }
    }
  }, [trackEvent, isExperimentActive, testKey]);

  const trackConversion = useCallback((conversionType = 'conversion') => {
    if (isExperimentActive(testKey)) {
      trackEvent(conversionType, testKey);
    }
  }, [trackEvent, isExperimentActive, testKey]);

  const trackEngagement = useCallback((engagementType: string, value?: number) => {
    if (isExperimentActive(testKey)) {
      trackEvent(`engagement_${engagementType}`, testKey);
    }
  }, [trackEvent, isExperimentActive, testKey]);

  return {
    trackClick,
    trackConversion,
    trackEngagement,
    isActive: isExperimentActive(testKey)
  };
}

/**
 * Component wrapper for A/B testing individual sections
 */
interface ABTestSectionProps {
  testKey: string;
  defaultContent: React.ReactNode;
  variants?: Record<string, React.ReactNode>;
  className?: string;
}

export function ABTestSection({ testKey, defaultContent, variants = {}, className }: ABTestSectionProps) {
  const { getVariant, isExperimentActive } = useABTest();
  
  if (!isExperimentActive(testKey)) {
    return <div className={className}>{defaultContent}</div>;
  }

  const variantContent = getVariant(testKey, { content: defaultContent });
  const selectedVariant = variants[variantContent.variant_key];
  
  return (
    <div className={className}>
      {selectedVariant || variantContent.content || defaultContent}
    </div>
  );
}

// Utility functions
function generateSessionId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function selectWeightedVariant(variants: ContentVariant[]): ContentVariant {
  const totalWeight = variants.reduce((sum, variant) => sum + variant.weight, 0);
  let random = Math.random() * totalWeight;
  
  for (const variant of variants) {
    random -= variant.weight;
    if (random <= 0) {
      return variant;
    }
  }
  
  // Fallback to first variant
  return variants[0];
}
