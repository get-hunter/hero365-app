/**
 * A/B Test Variant Component - Client-Side Component
 * 
 * Renders different variants based on A/B testing configuration.
 * This component handles the client-side logic for showing
 * different content variations to different users.
 */

'use client';

import React, { ReactNode, useEffect, useState } from 'react';
import { useABTesting } from './ABTestingProvider';

interface ABTestVariantProps {
  testKey: string;
  variants?: Record<string, ReactNode>;
  fallback: ReactNode;
  children?: ReactNode;
}

export function ABTestVariant({ 
  testKey, 
  variants = {}, 
  fallback, 
  children 
}: ABTestVariantProps) {
  
  const { getVariant, isEnabled, trackEvent } = useABTesting();
  const [selectedVariant, setSelectedVariant] = useState<string | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);
  
  useEffect(() => {
    // Only run on client side after hydration
    setIsHydrated(true);
    
    if (isEnabled) {
      const variant = getVariant(testKey);
      setSelectedVariant(variant);
      
      if (variant) {
        // Track variant view
        trackEvent('variant_view', {
          test_key: testKey,
          variant_id: variant
        });
      }
    }
  }, [testKey, isEnabled, getVariant, trackEvent]);
  
  // During SSR or before hydration, always show fallback
  if (!isHydrated || !isEnabled || !selectedVariant) {
    return <>{fallback}</>;
  }
  
  // Show variant content if available
  if (variants[selectedVariant]) {
    return <>{variants[selectedVariant]}</>;
  }
  
  // Show children if it's a variant test
  if (selectedVariant === 'variant' && children) {
    return <>{children}</>;
  }
  
  // Default to fallback (control)
  return <>{fallback}</>;
}

/**
 * Hook for conditional A/B test rendering
 */
export function useABTestVariant(testKey: string): {
  variant: string | null;
  isVariant: (variantId: string) => boolean;
  isControl: boolean;
  isEnabled: boolean;
} {
  const { getVariant, isEnabled } = useABTesting();
  const [variant, setVariant] = useState<string | null>(null);
  
  useEffect(() => {
    if (isEnabled) {
      const selectedVariant = getVariant(testKey);
      setVariant(selectedVariant);
    }
  }, [testKey, isEnabled, getVariant]);
  
  const isVariant = (variantId: string): boolean => {
    return variant === variantId;
  };
  
  const isControl = variant === 'control' || variant === null;
  
  return {
    variant,
    isVariant,
    isControl,
    isEnabled
  };
}

/**
 * Higher-order component for A/B testing
 */
export function withABTest<P extends object>(
  Component: React.ComponentType<P>,
  testKey: string,
  variants: Record<string, React.ComponentType<P>>
) {
  return function ABTestWrapper(props: P) {
    const { variant } = useABTestVariant(testKey);
    
    // Use variant component if available
    if (variant && variants[variant]) {
      const VariantComponent = variants[variant];
      return <VariantComponent {...props} />;
    }
    
    // Default to original component (control)
    return <Component {...props} />;
  };
}

/**
 * Conditional rendering based on A/B test
 */
export function ABTestConditional({ 
  testKey, 
  variantId, 
  children 
}: {
  testKey: string;
  variantId: string;
  children: ReactNode;
}) {
  const { isVariant } = useABTestVariant(testKey);
  
  if (!isVariant(variantId)) {
    return null;
  }
  
  return <>{children}</>;
}

/**
 * A/B Test Button with conversion tracking
 */
export function ABTestButton({
  testKey,
  conversionGoal,
  onClick,
  children,
  className = '',
  ...props
}: {
  testKey: string;
  conversionGoal?: string;
  onClick?: () => void;
  children: ReactNode;
  className?: string;
  [key: string]: any;
}) {
  const { trackConversion, trackEvent } = useABTesting();
  const { variant } = useABTestVariant(testKey);
  
  const handleClick = () => {
    // Track button click
    trackEvent('button_click', {
      test_key: testKey,
      variant_id: variant,
      conversion_goal: conversionGoal
    });
    
    // Track conversion if specified
    if (conversionGoal) {
      trackConversion(conversionGoal);
    }
    
    // Call original onClick
    if (onClick) {
      onClick();
    }
  };
  
  return (
    <button 
      onClick={handleClick}
      className={className}
      {...props}
    >
      {children}
    </button>
  );
}

/**
 * A/B Test Link with conversion tracking
 */
export function ABTestLink({
  testKey,
  conversionGoal,
  href,
  onClick,
  children,
  className = '',
  ...props
}: {
  testKey: string;
  conversionGoal?: string;
  href: string;
  onClick?: () => void;
  children: ReactNode;
  className?: string;
  [key: string]: any;
}) {
  const { trackConversion, trackEvent } = useABTesting();
  const { variant } = useABTestVariant(testKey);
  
  const handleClick = () => {
    // Track link click
    trackEvent('link_click', {
      test_key: testKey,
      variant_id: variant,
      href,
      conversion_goal: conversionGoal
    });
    
    // Track conversion if specified
    if (conversionGoal) {
      trackConversion(conversionGoal);
    }
    
    // Call original onClick
    if (onClick) {
      onClick();
    }
  };
  
  return (
    <a 
      href={href}
      onClick={handleClick}
      className={className}
      {...props}
    >
      {children}
    </a>
  );
}
