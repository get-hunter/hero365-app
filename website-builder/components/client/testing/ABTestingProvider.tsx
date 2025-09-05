/**
 * A/B Testing Provider - Client-Side Component
 * 
 * Provides A/B testing functionality for website optimization:
 * - Variant selection and persistence
 * - Conversion tracking
 * - Performance analytics
 * - Real-time experiment management
 * 
 * This is a client-side component for dynamic behavior and analytics.
 */

'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

interface ABTestVariant {
  id: string;
  name: string;
  weight: number;
  config: Record<string, any>;
}

interface ABTestExperiment {
  id: string;
  name: string;
  status: 'draft' | 'running' | 'paused' | 'completed';
  variants: ABTestVariant[];
  traffic_allocation: number; // 0-1 (percentage of users to include)
  start_date?: string;
  end_date?: string;
  conversion_goals: string[];
}

interface ABTestContext {
  experiments: Record<string, ABTestExperiment>;
  activeVariants: Record<string, string>;
  isEnabled: boolean;
  getVariant: (experimentId: string) => string | null;
  trackConversion: (goal: string, value?: number) => void;
  trackEvent: (event: string, properties?: Record<string, any>) => void;
}

interface ABTestingProviderProps {
  enabled: boolean;
  variants: Record<string, any>;
  activeExperiments: string[];
  artifactId: string;
  businessId: string;
  children: ReactNode;
}

const ABTestingContext = createContext<ABTestContext | null>(null);

export function ABTestingProvider({
  enabled,
  variants,
  activeExperiments,
  artifactId,
  businessId,
  children
}: ABTestingProviderProps) {
  
  const [experiments, setExperiments] = useState<Record<string, ABTestExperiment>>({});
  const [activeVariants, setActiveVariants] = useState<Record<string, string>>({});
  const [isInitialized, setIsInitialized] = useState(false);
  
  // Initialize A/B testing on mount
  useEffect(() => {
    if (!enabled) {
      setIsInitialized(true);
      return;
    }
    
    initializeABTesting();
  }, [enabled, activeExperiments, artifactId]);
  
  const initializeABTesting = async () => {
    try {
      // Load experiments configuration
      const experimentsConfig = await loadExperiments();
      setExperiments(experimentsConfig);
      
      // Determine active variants for this user
      const userVariants = determineUserVariants(experimentsConfig);
      setActiveVariants(userVariants);
      
      // Track experiment exposure
      trackExperimentExposure(userVariants);
      
      setIsInitialized(true);
      
      console.log('🧪 A/B Testing initialized:', {
        experiments: Object.keys(experimentsConfig).length,
        activeVariants: userVariants
      });
      
    } catch (error) {
      console.error('❌ A/B Testing initialization failed:', error);
      setIsInitialized(true);
    }
  };
  
  const loadExperiments = async (): Promise<Record<string, ABTestExperiment>> => {
    // In a real implementation, this would fetch from your backend
    // For now, we'll create experiments from the variants prop
    const experiments: Record<string, ABTestExperiment> = {};
    
    activeExperiments.forEach(experimentId => {
      if (variants[experimentId]) {
        experiments[experimentId] = {
          id: experimentId,
          name: `${experimentId} Test`,
          status: 'running',
          variants: [
            {
              id: 'control',
              name: 'Control',
              weight: 0.5,
              config: {}
            },
            {
              id: 'variant',
              name: 'Variant',
              weight: 0.5,
              config: variants[experimentId]
            }
          ],
          traffic_allocation: 1.0,
          conversion_goals: ['contact_form', 'phone_call', 'booking']
        };
      }
    });
    
    return experiments;
  };
  
  const determineUserVariants = (experiments: Record<string, ABTestExperiment>): Record<string, string> => {
    const userVariants: Record<string, string> = {};
    
    // Get or create user ID for consistent variant assignment
    const userId = getUserId();
    
    Object.entries(experiments).forEach(([experimentId, experiment]) => {
      if (experiment.status !== 'running') {
        return;
      }
      
      // Check if user should be included in this experiment
      const userHash = hashUserId(userId + experimentId);
      const shouldInclude = userHash < experiment.traffic_allocation;
      
      if (!shouldInclude) {
        return;
      }
      
      // Determine variant based on weights
      const variant = selectVariant(experiment.variants, userHash);
      userVariants[experimentId] = variant.id;
      
      // Store in localStorage for consistency
      localStorage.setItem(`ab_${experimentId}`, variant.id);
    });
    
    return userVariants;
  };
  
  const getUserId = (): string => {
    let userId = localStorage.getItem('ab_user_id');
    
    if (!userId) {
      userId = generateUserId();
      localStorage.setItem('ab_user_id', userId);
    }
    
    return userId;
  };
  
  const generateUserId = (): string => {
    return 'user_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
  };
  
  const hashUserId = (input: string): number => {
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash) / 2147483647; // Normalize to 0-1
  };
  
  const selectVariant = (variants: ABTestVariant[], userHash: number): ABTestVariant => {
    let cumulativeWeight = 0;
    
    for (const variant of variants) {
      cumulativeWeight += variant.weight;
      if (userHash <= cumulativeWeight) {
        return variant;
      }
    }
    
    // Fallback to first variant
    return variants[0];
  };
  
  const trackExperimentExposure = (userVariants: Record<string, string>) => {
    Object.entries(userVariants).forEach(([experimentId, variantId]) => {
      trackEvent('experiment_exposure', {
        experiment_id: experimentId,
        variant_id: variantId,
        artifact_id: artifactId,
        business_id: businessId
      });
    });
  };
  
  const getVariant = (experimentId: string): string | null => {
    return activeVariants[experimentId] || null;
  };
  
  const trackConversion = (goal: string, value?: number) => {
    if (!enabled || !isInitialized) return;
    
    const conversionData = {
      goal,
      value,
      artifact_id: artifactId,
      business_id: businessId,
      active_variants: activeVariants,
      timestamp: new Date().toISOString()
    };
    
    // Track conversion
    trackEvent('conversion', conversionData);
    
    console.log('🎯 Conversion tracked:', conversionData);
  };
  
  const trackEvent = (event: string, properties?: Record<string, any>) => {
    if (!enabled) return;
    
    const eventData = {
      event,
      properties: {
        ...properties,
        user_id: getUserId(),
        session_id: getSessionId(),
        timestamp: new Date().toISOString()
      }
    };
    
    // Send to analytics service
    sendAnalyticsEvent(eventData);
  };
  
  const getSessionId = (): string => {
    let sessionId = sessionStorage.getItem('ab_session_id');
    
    if (!sessionId) {
      sessionId = 'session_' + Date.now().toString(36) + Math.random().toString(36).substr(2);
      sessionStorage.setItem('ab_session_id', sessionId);
    }
    
    return sessionId;
  };
  
  const sendAnalyticsEvent = async (eventData: any) => {
    try {
      // In a real implementation, send to your analytics service
      // For now, just log to console and store locally
      console.log('📊 Analytics event:', eventData);
      
      // Store events locally for batch sending
      const events = JSON.parse(localStorage.getItem('ab_events') || '[]');
      events.push(eventData);
      
      // Keep only last 100 events
      if (events.length > 100) {
        events.splice(0, events.length - 100);
      }
      
      localStorage.setItem('ab_events', JSON.stringify(events));
      
      // In production, you might batch send these events
      // await fetch('/api/analytics', { method: 'POST', body: JSON.stringify(eventData) });
      
    } catch (error) {
      console.error('❌ Failed to send analytics event:', error);
    }
  };
  
  const contextValue: ABTestContext = {
    experiments,
    activeVariants,
    isEnabled: enabled && isInitialized,
    getVariant,
    trackConversion,
    trackEvent
  };
  
  return (
    <ABTestingContext.Provider value={contextValue}>
      {children}
    </ABTestingContext.Provider>
  );
}

/**
 * Hook to use A/B testing context
 */
export function useABTesting(): ABTestContext {
  const context = useContext(ABTestingContext);
  
  if (!context) {
    // Return disabled context if provider not found
    return {
      experiments: {},
      activeVariants: {},
      isEnabled: false,
      getVariant: () => null,
      trackConversion: () => {},
      trackEvent: () => {}
    };
  }
  
  return context;
}

/**
 * Hook for conversion tracking
 */
export function useConversionTracking() {
  const { trackConversion, isEnabled } = useABTesting();
  
  const trackPhoneCall = () => {
    trackConversion('phone_call', 1);
  };
  
  const trackFormSubmission = (formType: string) => {
    trackConversion('form_submission', 1);
    trackEvent('form_submit', { form_type: formType });
  };
  
  const trackBooking = (value?: number) => {
    trackConversion('booking', value);
  };
  
  const trackEmailClick = () => {
    trackConversion('email_click', 1);
  };
  
  return {
    trackPhoneCall,
    trackFormSubmission,
    trackBooking,
    trackEmailClick,
    isEnabled
  };
}