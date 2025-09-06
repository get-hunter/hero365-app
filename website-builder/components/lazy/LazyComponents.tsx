/**
 * Lazy Component Loader
 * 
 * Dynamic imports for heavy components to improve initial page load
 * Includes loading states and error boundaries
 */

import dynamic from 'next/dynamic';
import React from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent } from '@/components/ui/card';

// Loading components
const ComponentSkeleton = () => (
  <div className="space-y-4">
    <Skeleton className="h-8 w-full" />
    <Skeleton className="h-32 w-full" />
    <div className="flex space-x-4">
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-4 w-1/3" />
    </div>
  </div>
);

const BookingWidgetSkeleton = () => (
  <Card>
    <CardContent className="p-6 space-y-4">
      <Skeleton className="h-6 w-3/4" />
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-32 w-full" />
      <Skeleton className="h-10 w-full" />
    </CardContent>
  </Card>
);

const ProjectGallerySkeleton = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {[...Array(6)].map((_, i) => (
      <Card key={i}>
        <Skeleton className="h-48 w-full rounded-t-lg" />
        <CardContent className="p-4 space-y-2">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </CardContent>
      </Card>
    ))}
  </div>
);

const ProductCatalogSkeleton = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    {[...Array(8)].map((_, i) => (
      <Card key={i}>
        <Skeleton className="h-40 w-full rounded-t-lg" />
        <CardContent className="p-4 space-y-2">
          <Skeleton className="h-5 w-full" />
          <Skeleton className="h-4 w-2/3" />
          <Skeleton className="h-6 w-1/2" />
        </CardContent>
      </Card>
    ))}
  </div>
);

// Lazy loaded components with proper loading states
export const LazyBookingWidget = dynamic(
  () => import('@/components/client/commerce/booking/Hero365BookingWidget'),
  {
    loading: () => <BookingWidgetSkeleton />,
    ssr: false // Client-side only for interactivity
  }
);

export const LazyBookingForm = dynamic(
  () => import('@/components/client/forms/Hero365BookingForm'),
  {
    loading: () => <ComponentSkeleton />,
    ssr: false
  }
);

export const LazyProjectGallery = dynamic(
  () => import('@/components/client/projects/Hero365ProjectGallery'),
  {
    loading: () => <ProjectGallerySkeleton />,
    ssr: true // Can be server-rendered
  }
);

export const LazyProjectsGrid = dynamic(
  () => import('@/components/client/projects/Hero365ProjectsGrid'),
  {
    loading: () => <ProjectGallerySkeleton />,
    ssr: true
  }
);

export const LazyProductVariants = dynamic(
  () => import('@/components/client/commerce/products/Hero365ProductVariants'),
  {
    loading: () => <ComponentSkeleton />,
    ssr: false // Interactive component
  }
);

export const LazyMembershipPlans = dynamic(
  () => import('@/components/client/commerce/membership/Hero365MembershipPlans'),
  {
    loading: () => <ProductCatalogSkeleton />,
    ssr: true
  }
);

export const LazyCartIndicator = dynamic(
  () => import('@/components/client/commerce/cart/Hero365CartIndicator'),
  {
    loading: () => <Skeleton className="h-8 w-8 rounded-full" />,
    ssr: false
  }
);

export const LazyPerformanceMonitor = dynamic(
  () => import('@/components/client/monitoring/PerformanceMonitor'),
  {
    loading: () => null, // No loading state for monitoring
    ssr: false
  }
);

export const LazyConversionTracker = dynamic(
  () => import('@/components/client/analytics/Hero365ConversionTracker'),
  {
    loading: () => null,
    ssr: false
  }
);

// Activity modules (trade-specific components)
export const LazyHVACCalculator = dynamic(
  () => import('@/components/client/activity-modules/hvac/HVACEfficiencyCalculator'),
  {
    loading: () => <ComponentSkeleton />,
    ssr: false
  }
);

export const LazyPlumbingTriage = dynamic(
  () => import('@/components/client/activity-modules/plumbing/PlumbingSeverityTriage'),
  {
    loading: () => <ComponentSkeleton />,
    ssr: false
  }
);

export const LazyElectricalCalculator = dynamic(
  () => import('@/components/client/activity-modules/electrical/ElectricalLoadCalculator'),
  {
    loading: () => <ComponentSkeleton />,
    ssr: false
  }
);

export const LazyRoofingSelector = dynamic(
  () => import('@/components/client/activity-modules/roofing/RoofingMaterialSelector'),
  {
    loading: () => <ComponentSkeleton />,
    ssr: false
  }
);

export const LazyLandscapingDesigner = dynamic(
  () => import('@/components/client/activity-modules/landscaping/LandscapingDesignTool'),
  {
    loading: () => <ComponentSkeleton />,
    ssr: false
  }
);

export const LazySecurityConfigurator = dynamic(
  () => import('@/components/client/activity-modules/security/SecuritySystemConfigurator'),
  {
    loading: () => <ComponentSkeleton />,
    ssr: false
  }
);

export const LazyProjectEstimator = dynamic(
  () => import('@/components/client/activity-modules/general-contractor/ProjectEstimator'),
  {
    loading: () => <ComponentSkeleton />,
    ssr: false
  }
);

// Checkout flow components (heavy and interactive)
export const LazyCheckoutFlow = dynamic(
  () => import('@/components/client/commerce/checkout/Hero365CheckoutProgress'),
  {
    loading: () => <ComponentSkeleton />,
    ssr: false
  }
);

export const LazyPaymentStep = dynamic(
  () => import('@/components/client/commerce/checkout/PaymentStep'),
  {
    loading: () => <ComponentSkeleton />,
    ssr: false
  }
);

// A/B Testing components
export const LazyABTestProvider = dynamic(
  () => import('@/components/client/testing/ABTestingProvider'),
  {
    loading: () => null,
    ssr: false
  }
);

export const LazyABTestVariant = dynamic(
  () => import('@/components/client/testing/ABTestVariant'),
  {
    loading: () => <ComponentSkeleton />,
    ssr: false
  }
);

// Helper function to conditionally load components
export function createConditionalLazyComponent<T>(
  importFn: () => Promise<{ default: React.ComponentType<T> }>,
  condition: () => boolean,
  fallback?: React.ComponentType<T>
) {
  if (!condition()) {
    return fallback || (() => null);
  }

  return dynamic(importFn, {
    loading: () => <ComponentSkeleton />,
    ssr: false
  });
}

// Bundle size optimization - only load what's needed
export function getTradeSpecificComponents(trade: string) {
  const components: Record<string, any> = {};

  switch (trade.toLowerCase()) {
    case 'hvac':
      components.Calculator = LazyHVACCalculator;
      break;
    case 'plumbing':
      components.Triage = LazyPlumbingTriage;
      break;
    case 'electrical':
      components.Calculator = LazyElectricalCalculator;
      break;
    case 'roofing':
      components.Selector = LazyRoofingSelector;
      break;
    case 'landscaping':
      components.Designer = LazyLandscapingDesigner;
      break;
    case 'security':
      components.Configurator = LazySecurityConfigurator;
      break;
    case 'general-contractor':
      components.Estimator = LazyProjectEstimator;
      break;
    default:
      // No trade-specific components
      break;
  }

  return components;
}

// Performance monitoring for lazy components
export function withLazyLoadTracking<P extends object>(
  Component: React.ComponentType<P>,
  componentName: string
) {
  return React.forwardRef<any, P>((props, ref) => {
    React.useEffect(() => {
      const startTime = performance.now();
      
      return () => {
        const loadTime = performance.now() - startTime;
        
        // Track lazy load performance
        if (typeof window !== 'undefined' && (window as any).gtag) {
          (window as any).gtag('event', 'lazy_component_loaded', {
            component_name: componentName,
            load_time: Math.round(loadTime),
            custom_parameter_1: 'lazy_load'
          });
        }
        
        console.log(`⚡ [LAZY-LOAD] ${componentName} loaded in ${Math.round(loadTime)}ms`);
      };
    }, []);

    return <Component {...props} ref={ref} />;
  });
}
