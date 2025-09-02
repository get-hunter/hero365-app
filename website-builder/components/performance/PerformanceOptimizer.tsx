'use client';

/**
 * Performance Optimizer Component
 * 
 * Handles critical CSS inlining, resource preloading, and other
 * performance optimizations for better Core Web Vitals scores.
 */

import { useEffect } from 'react';
import Head from 'next/head';

interface PerformanceOptimizerProps {
  businessName: string;
  criticalResources?: string[];
  preloadFonts?: string[];
  enableServiceWorker?: boolean;
}

export default function PerformanceOptimizer({
  businessName,
  criticalResources = [],
  preloadFonts = [],
  enableServiceWorker = false
}: PerformanceOptimizerProps) {
  
  useEffect(() => {
    // Preload critical resources
    criticalResources.forEach(resource => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = resource;
      link.as = resource.endsWith('.css') ? 'style' : 'script';
      document.head.appendChild(link);
    });
    
    // Register service worker for caching
    if (enableServiceWorker && 'serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(console.error);
    }
    
    // Optimize third-party scripts
    optimizeThirdPartyScripts();
    
    // Monitor Core Web Vitals
    if (process.env.NODE_ENV === 'production') {
      monitorWebVitals();
    }
  }, [criticalResources, enableServiceWorker]);
  
  return (
    <Head>
      {/* DNS Prefetch for external domains */}
      <link rel="dns-prefetch" href="//fonts.googleapis.com" />
      <link rel="dns-prefetch" href="//images.unsplash.com" />
      <link rel="dns-prefetch" href="//api.hero365.app" />
      
      {/* Preconnect for critical external resources */}
      <link rel="preconnect" href="https://fonts.googleapis.com" crossOrigin="" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      
      {/* Preload critical fonts */}
      {preloadFonts.map((font, index) => (
        <link
          key={index}
          rel="preload"
          href={font}
          as="font"
          type="font/woff2"
          crossOrigin=""
        />
      ))}
      
      {/* Critical CSS - inlined for fastest rendering */}
      <style dangerouslySetInnerHTML={{
        __html: getCriticalCSS()
      }} />
      
      {/* Resource hints for better loading */}
      <link rel="prefetch" href="/api/contractors/services" />
      <link rel="prefetch" href="/api/contractors/products" />
      
      {/* Performance monitoring */}
      {process.env.NODE_ENV === 'production' && (
        <script
          dangerouslySetInnerHTML={{
            __html: getWebVitalsScript()
          }}
        />
      )}
    </Head>
  );
}

/**
 * Get critical CSS that should be inlined
 */
function getCriticalCSS(): string {
  return `
    /* Critical CSS for above-the-fold content */
    * {
      box-sizing: border-box;
    }
    
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      color: #333;
      background-color: #fff;
    }
    
    /* Hero section critical styles */
    .hero {
      min-height: 60vh;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    
    .hero h1 {
      font-size: clamp(2rem, 5vw, 3.5rem);
      font-weight: 700;
      margin: 0 0 1rem 0;
      line-height: 1.2;
    }
    
    .hero p {
      font-size: clamp(1.1rem, 2.5vw, 1.25rem);
      margin: 0 0 2rem 0;
      opacity: 0.9;
    }
    
    /* CTA button critical styles */
    .cta-button {
      display: inline-block;
      padding: 1rem 2rem;
      background: #ff6b6b;
      color: white;
      text-decoration: none;
      border-radius: 8px;
      font-weight: 600;
      transition: transform 0.2s ease;
    }
    
    .cta-button:hover {
      transform: translateY(-2px);
    }
    
    /* Loading states */
    .loading {
      opacity: 0.7;
      pointer-events: none;
    }
    
    /* Prevent layout shift */
    img {
      max-width: 100%;
      height: auto;
    }
    
    /* Container for consistent spacing */
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 1rem;
    }
    
    @media (max-width: 768px) {
      .container {
        padding: 0 0.75rem;
      }
    }
  `;
}

/**
 * Get Web Vitals monitoring script
 */
function getWebVitalsScript(): string {
  return `
    // Web Vitals monitoring
    function sendToAnalytics(metric) {
      // Send to your analytics service
      console.log('Web Vital:', metric);
      
      // Example: Send to Google Analytics
      if (typeof gtag !== 'undefined') {
        gtag('event', metric.name, {
          value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
          event_category: 'Web Vitals',
          event_label: metric.id,
          non_interaction: true,
        });
      }
    }
    
    // Monitor Core Web Vitals
    if ('web-vitals' in window) {
      import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
        getCLS(sendToAnalytics);
        getFID(sendToAnalytics);
        getFCP(sendToAnalytics);
        getLCP(sendToAnalytics);
        getTTFB(sendToAnalytics);
      });
    }
  `;
}

/**
 * Optimize third-party scripts loading
 */
function optimizeThirdPartyScripts() {
  // Defer non-critical scripts
  const scripts = document.querySelectorAll('script[src]');
  scripts.forEach(script => {
    const src = script.getAttribute('src');
    if (src && !src.includes('critical')) {
      script.setAttribute('loading', 'lazy');
    }
  });
}

/**
 * Monitor Web Vitals and send to analytics
 */
function monitorWebVitals() {
  // This would integrate with your analytics service
  // For now, just log to console in production
  if (typeof window !== 'undefined' && 'performance' in window) {
    // Monitor page load performance
    window.addEventListener('load', () => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
      
      console.log('Page Load Time:', loadTime);
      
      // Monitor largest contentful paint
      if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          console.log('LCP:', lastEntry.startTime);
        });
        
        observer.observe({ entryTypes: ['largest-contentful-paint'] });
      }
    });
  }
}
