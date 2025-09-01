/**
 * Conversion Tracking Widget - 10X Engineer Approach
 * Track every interaction that makes contractors money
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface ConversionTrackerProps {
  businessId: string;
  websiteId: string;
  apiUrl: string;
}

interface ConversionEvent {
  type: 'phone_call' | 'form_submit' | 'booking' | 'chat' | 'email';
  page_url: string;
  contact_info?: {
    name?: string;
    phone?: string;
    email?: string;
    service_needed?: string;
    message?: string;
  };
  traffic_source?: string;
}

export default function ConversionTracker({ 
  businessId, 
  websiteId, 
  apiUrl 
}: ConversionTrackerProps) {
  const router = useRouter();

  useEffect(() => {
    // Initialize conversion tracking
    initializeTracking();
    
    // Track page views
    trackPageView();
    
    // Setup event listeners
    setupEventListeners();
    
    return () => {
      // Cleanup event listeners
      cleanupEventListeners();
    };
  }, []);

  const initializeTracking = () => {
    // Set up session tracking
    const sessionId = getOrCreateSessionId();
    const trafficSource = getTrafficSource();
    
    // Store tracking data
    window.conversionTracker = {
      businessId,
      websiteId,
      sessionId,
      trafficSource,
      pageViews: 0,
      interactions: 0
    };
  };

  const trackPageView = () => {
    if (typeof window !== 'undefined') {
      window.conversionTracker.pageViews++;
      
      // Track component impressions
      trackComponentImpressions();
    }
  };

  const setupEventListeners = () => {
    // Track phone number clicks
    document.addEventListener('click', handlePhoneClick);
    
    // Track form submissions
    document.addEventListener('submit', handleFormSubmit);
    
    // Track chat widget interactions
    document.addEventListener('chat-opened', handleChatInteraction);
    
    // Track booking button clicks
    document.addEventListener('click', handleBookingClick);
    
    // Track email clicks
    document.addEventListener('click', handleEmailClick);
  };

  const cleanupEventListeners = () => {
    document.removeEventListener('click', handlePhoneClick);
    document.removeEventListener('submit', handleFormSubmit);
    document.removeEventListener('chat-opened', handleChatInteraction);
    document.removeEventListener('click', handleBookingClick);
    document.removeEventListener('click', handleEmailClick);
  };

  const handlePhoneClick = (event: Event) => {
    const target = event.target as HTMLElement;
    
    // Check if clicked element is a phone link
    if (target.tagName === 'A' && target.getAttribute('href')?.startsWith('tel:')) {
      const phoneNumber = target.getAttribute('href')?.replace('tel:', '');
      
      trackConversion({
        type: 'phone_call',
        page_url: window.location.href,
        contact_info: {
          phone: phoneNumber
        }
      });
    }
  };

  const handleFormSubmit = (event: Event) => {
    const form = event.target as HTMLFormElement;
    
    // Extract form data
    const formData = new FormData(form);
    const contactInfo: any = {};
    
    // Common form field mappings
    const fieldMappings = {
      'name': ['name', 'full_name', 'customer_name'],
      'phone': ['phone', 'telephone', 'phone_number'],
      'email': ['email', 'email_address'],
      'service_needed': ['service', 'service_type', 'service_needed'],
      'message': ['message', 'comments', 'description', 'details']
    };
    
    // Extract contact information
    Object.entries(fieldMappings).forEach(([key, fields]) => {
      for (const field of fields) {
        const value = formData.get(field);
        if (value) {
          contactInfo[key] = value.toString();
          break;
        }
      }
    });
    
    trackConversion({
      type: 'form_submit',
      page_url: window.location.href,
      contact_info: contactInfo
    });
  };

  const handleChatInteraction = () => {
    trackConversion({
      type: 'chat',
      page_url: window.location.href
    });
  };

  const handleBookingClick = (event: Event) => {
    const target = event.target as HTMLElement;
    
    // Check if clicked element is a booking button
    if (target.classList.contains('booking-btn') || 
        target.closest('.booking-widget') ||
        target.textContent?.toLowerCase().includes('book') ||
        target.textContent?.toLowerCase().includes('schedule')) {
      
      trackConversion({
        type: 'booking',
        page_url: window.location.href
      });
    }
  };

  const handleEmailClick = (event: Event) => {
    const target = event.target as HTMLElement;
    
    // Check if clicked element is an email link
    if (target.tagName === 'A' && target.getAttribute('href')?.startsWith('mailto:')) {
      const email = target.getAttribute('href')?.replace('mailto:', '');
      
      trackConversion({
        type: 'email',
        page_url: window.location.href,
        contact_info: {
          email: email
        }
      });
    }
  };

  const trackConversion = async (conversionData: ConversionEvent) => {
    try {
      const response = await fetch(`${apiUrl}/analytics/track-conversion?business_id=${businessId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: conversionData.type,
          value: 0, // Will be calculated by backend based on conversion type
          page: conversionData.page_url,
          visitor: {
            userAgent: navigator.userAgent,
            referrer: document.referrer,
            trafficSource: window.conversionTracker?.trafficSource || 'direct'
          },
          details: {
            contact_info: conversionData.contact_info
          }
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Show success feedback to user
        showConversionFeedback(conversionData.type, result.estimated_value);
        
        // Track in analytics
        if (typeof gtag !== 'undefined') {
          gtag('event', 'conversion', {
            event_category: 'website',
            event_label: conversionData.type,
            value: result.estimated_value
          });
        }
      }
    } catch (error) {
      console.error('Conversion tracking failed:', error);
    }
  };

  const trackComponentImpressions = () => {
    // Track which components are visible
    const components = [
      { selector: '.hero', type: 'hero' },
      { selector: '.services', type: 'services' },
      { selector: '.testimonials', type: 'testimonials' },
      { selector: '.cta', type: 'cta' },
      { selector: '.contact-form', type: 'contact_form' }
    ];

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const componentType = entry.target.getAttribute('data-component');
          if (componentType) {
            trackComponentImpression(componentType);
          }
        }
      });
    }, { threshold: 0.5 });

    components.forEach(({ selector, type }) => {
      const elements = document.querySelectorAll(selector);
      elements.forEach((element) => {
        element.setAttribute('data-component', type);
        observer.observe(element);
      });
    });
  };

  const trackComponentImpression = async (componentType: string) => {
    try {
      await fetch(`${apiUrl}/website/track-component`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          website_id: websiteId,
          component_type: componentType,
          page_url: window.location.href,
          impression: true
        })
      });
    } catch (error) {
      console.error('Component tracking failed:', error);
    }
  };

  const showConversionFeedback = (type: string, value: number) => {
    // Show subtle success message
    const messages = {
      phone_call: "Thanks for calling! We'll answer right away.",
      form_submit: "Thanks! We'll get back to you within 1 hour.",
      booking: "Booking confirmed! You'll receive a confirmation email.",
      chat: "Chat started! How can we help you today?",
      email: "Thanks for reaching out! We'll respond quickly."
    };

    const message = messages[type as keyof typeof messages] || "Thanks for your interest!";
    
    // Create and show toast notification
    const toast = document.createElement('div');
    toast.className = 'conversion-toast';
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #10B981;
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      font-family: system-ui, sans-serif;
      font-size: 14px;
      animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    // Remove after 5 seconds
    setTimeout(() => {
      toast.remove();
    }, 5000);
  };

  const getOrCreateSessionId = (): string => {
    let sessionId = sessionStorage.getItem('conversion_session_id');
    if (!sessionId) {
      sessionId = Math.random().toString(36).substring(2, 15);
      sessionStorage.setItem('conversion_session_id', sessionId);
    }
    return sessionId;
  };

  const getTrafficSource = (): string => {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Check UTM parameters
    if (urlParams.get('utm_source')) {
      return urlParams.get('utm_source') || 'unknown';
    }
    
    // Check referrer
    const referrer = document.referrer;
    if (referrer) {
      if (referrer.includes('google.com')) return 'google';
      if (referrer.includes('facebook.com')) return 'facebook';
      if (referrer.includes('bing.com')) return 'bing';
      if (referrer.includes('yahoo.com')) return 'yahoo';
      return 'referral';
    }
    
    return 'direct';
  };

  // This component doesn't render anything visible
  return null;
}

// Add CSS for toast animation
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    
    .conversion-toast {
      animation: slideIn 0.3s ease-out;
    }
  `;
  document.head.appendChild(style);
}

// Extend window interface for TypeScript
declare global {
  interface Window {
    conversionTracker?: {
      businessId: string;
      websiteId: string;
      sessionId: string;
      trafficSource: string;
      pageViews: number;
      interactions: number;
    };
    gtag?: (...args: any[]) => void;
  }
}
