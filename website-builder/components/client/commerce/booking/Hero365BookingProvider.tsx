/**
 * Hero365 Booking Provider
 * 
 * Provides Hero365 booking widget functionality throughout the website with popup integration
 */

'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import { X } from 'lucide-react';
import Hero365BookingWizard from './Hero365BookingWizard';
import Hero365BookingErrorBoundary from './Hero365BookingErrorBoundary';
import { BookingWidgetLauncher } from '@/components/client/commerce/booking/Hero365BookingWidget';
import { BookableService, Booking } from '@/lib/shared/types/booking';

interface Hero365BookingContextType {
  isOpen: boolean;
  openBookingWidget: (serviceId?: string) => void;
  closeBookingWidget: () => void;
  selectedServiceId?: string;
}

const BookingWidgetContext = createContext<BookingWidgetContextType | undefined>(undefined);

interface BookingWidgetProviderProps {
  children: React.ReactNode;
  businessId: string;
  services: BookableService[];
  companyName?: string;
  companyLogo?: string;
  companyPhone?: string;
  companyEmail?: string;
  primaryColor?: string;
  showLauncher?: boolean;
  countryCode?: string;
}

export function Hero365BookingProvider({
  children,
  businessId,
  services,
  companyName = 'Professional Services',
  companyLogo,
  companyPhone,
  companyEmail,
  primaryColor = '#3b82f6',
  showLauncher = false,
  countryCode
}: BookingWidgetProviderProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedServiceId, setSelectedServiceId] = useState<string | undefined>();

  const openBookingWidget = useCallback((serviceId?: string) => {
    setSelectedServiceId(serviceId);
    setIsOpen(true);
    
    // Prevent body scroll when widget is open
    document.body.style.overflow = 'hidden';
    
    // Send analytics event
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'booking_widget_opened', {
        business_id: businessId,
        service_id: serviceId,
      });
    }
  }, [businessId]);

  const closeBookingWidget = useCallback(() => {
    setIsOpen(false);
    setSelectedServiceId(undefined);
    
    // Restore body scroll
    document.body.style.overflow = '';
    
    // Send analytics event
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'booking_widget_closed', {
        business_id: businessId,
      });
    }
  }, [businessId]);

  const handleBookingComplete = (booking: Booking) => {
    // Send analytics event
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'booking_completed', {
        business_id: businessId,
        service_id: booking.service_id,
        booking_id: booking.id,
        value: booking.quoted_price || 0,
      });
    }

    // Keep widget open to show confirmation
    // User can close manually or start new booking
  };

  const handleBookingError = (error: string) => {
    console.error('Booking error:', error);
    
    // Send analytics event
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'booking_error', {
        business_id: businessId,
        error_message: error,
      });
    }
  };

  // Filter services if a specific service is selected
  const filteredServices = selectedServiceId 
    ? services.filter(service => service.id === selectedServiceId)
    : services;

  const contextValue: BookingWidgetContextType = {
    isOpen,
    openBookingWidget,
    closeBookingWidget,
    selectedServiceId
  };

  return (
    <BookingWidgetContext.Provider value={contextValue}>
      {children}
      
      {/* Floating Launcher Button */}
      {showLauncher && !isOpen && (
        <BookingWidgetLauncher
          onClick={() => openBookingWidget()}
          companyName={`Book ${companyName}`}
          primaryColor={primaryColor}
        />
      )}

      {/* Popup Booking Widget */}
      {isOpen && (
        <div className="fixed inset-0 z-50">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
            onClick={closeBookingWidget}
          />
          
          {/* Widget Container: fullscreen on mobile, centered modal on desktop */}
          <div className="relative z-10 flex items-start md:items-center justify-center min-h-screen p-0 md:p-6">
            <div 
              className="w-full h-full md:h-auto md:w-full md:max-w-4xl md:max-h-[90vh] flex flex-col bg-white md:rounded-xl shadow-2xl overflow-hidden relative"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close Button */}
              <button
                onClick={closeBookingWidget}
                className="absolute top-4 right-4 z-20 p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors duration-200 shadow-sm"
                aria-label="Close booking widget"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
              
              <div className="flex-1 overflow-y-auto">
                <Hero365BookingErrorBoundary
                  businessName={companyName}
                  businessPhone={companyPhone}
                  businessEmail={companyEmail}
                  onReset={() => {
                    // Reset the booking widget state
                    closeBookingWidget();
                    setTimeout(() => openBookingWidget(), 100);
                  }}
                  onGoBack={closeBookingWidget}
                >
                  <Hero365BookingWizard
                    businessId={businessId}
                    businessName={companyName}
                    businessPhone={companyPhone}
                    businessEmail={companyEmail}
                    services={filteredServices}
                    onClose={closeBookingWidget}
                    onComplete={handleBookingComplete}
                    className="h-full"
                    countryCode={countryCode}
                  />
                </Hero365BookingErrorBoundary>
              </div>
            </div>
          </div>
        </div>
      )}
    </BookingWidgetContext.Provider>
  );
}

// Hook to use booking widget context
export function useBookingWidget() {
  const context = useContext(BookingWidgetContext);
  if (context === undefined) {
    throw new Error('useBookingWidget must be used within a BookingWidgetProvider');
  }
  return context;
}

// Booking CTA Button Component
export function BookingCTAButton({
  children,
  serviceId,
  variant = 'primary',
  size = 'default',
  className = '',
  ...props
}: {
  children: React.ReactNode;
  serviceId?: string;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'default' | 'lg';
  className?: string;
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const { openBookingWidget } = useBookingWidget();

  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  
  const variantClasses = {
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    outline: 'border border-input hover:bg-accent hover:text-accent-foreground'
  } as const;

  const sizeClasses = {
    sm: 'h-9 px-3 text-sm',
    default: 'h-10 py-2 px-4',
    lg: 'h-11 px-8 text-lg'
  } as const;

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      onClick={() => openBookingWidget(serviceId)}
      {...props}
    >
      {children}
    </button>
  );
}

export default Hero365BookingProvider;
