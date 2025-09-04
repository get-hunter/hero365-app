/**
 * Embeddable Booking Widget
 * 
 * Standalone booking widget that can be embedded in any website via iframe or script
 */

'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, Phone, Mail, ExternalLink, Minimize2, Maximize2 } from 'lucide-react';
import { cn } from '@/lib/shared/utils';

import Hero365BookingWizard from './Hero365BookingWizard';
import { BookableService, Booking } from '@/lib/shared/types/booking';

interface EmbeddableBookingWidgetProps {
  businessId: string;
  services: BookableService[];
  
  // Widget Configuration
  theme?: 'light' | 'dark' | 'auto';
  primaryColor?: string;
  companyName?: string;
  companyLogo?: string;
  companyPhone?: string;
  companyEmail?: string;
  
  // Widget Behavior
  mode?: 'popup' | 'inline' | 'sidebar';
  showHeader?: boolean;
  showFooter?: boolean;
  allowMinimize?: boolean;
  
  // Callbacks
  onBookingComplete?: (booking: Booking) => void;
  onBookingError?: (error: string) => void;
  onWidgetClose?: () => void;
  
  className?: string;
}

export default function EmbeddableBookingWidget({
  businessId,
  services,
  theme = 'light',
  primaryColor = '#3b82f6',
  companyName = 'Professional Services',
  companyLogo,
  companyPhone,
  companyEmail,
  mode = 'inline',
  showHeader = true,
  showFooter = true,
  allowMinimize = false,
  onBookingComplete,
  onBookingError,
  onWidgetClose,
  className
}: EmbeddableBookingWidgetProps) {
  const [isMinimized, setIsMinimized] = useState(false);
  const [isVisible, setIsVisible] = useState(true);

  const handleBookingComplete = (booking: Booking) => {
    if (onBookingComplete) {
      onBookingComplete(booking);
    }
    
    // Send postMessage to parent window for iframe integration
    if (typeof window !== 'undefined' && window.parent !== window) {
      window.parent.postMessage({
        type: 'HERO365_BOOKING_COMPLETE',
        data: booking
      }, '*');
    }
  };

  const handleBookingError = (error: string) => {
    if (onBookingError) {
      onBookingError(error);
    }
    
    // Send postMessage to parent window for iframe integration
    if (typeof window !== 'undefined' && window.parent !== window) {
      window.parent.postMessage({
        type: 'HERO365_BOOKING_ERROR',
        data: { error }
      }, '*');
    }
  };

  const handleClose = () => {
    setIsVisible(false);
    if (onWidgetClose) {
      onWidgetClose();
    }
    
    // Send postMessage to parent window for iframe integration
    if (typeof window !== 'undefined' && window.parent !== window) {
      window.parent.postMessage({
        type: 'HERO365_WIDGET_CLOSE'
      }, '*');
    }
  };

  const handleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  if (!isVisible) {
    return null;
  }

  const widgetContent = (
    <div 
      className={cn(
        "bg-white shadow-lg border rounded-lg overflow-hidden",
        mode === 'popup' && "fixed bottom-4 right-4 z-50 max-w-md w-full",
        mode === 'sidebar' && "fixed right-0 top-0 h-full w-96 z-50",
        mode === 'inline' && "w-full max-w-4xl mx-auto",
        isMinimized && "h-16",
        className
      )}
      style={{
        '--primary-color': primaryColor,
      } as React.CSSProperties}
    >
      {/* Widget Header */}
      {showHeader && (
        <div className="bg-gray-50 border-b px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {companyLogo && (
              <img 
                src={companyLogo} 
                alt={companyName}
                className="w-8 h-8 rounded object-cover"
              />
            )}
            <div>
              <h3 className="font-semibold text-gray-900">{companyName}</h3>
              <p className="text-xs text-gray-600">Book Your Appointment</p>
            </div>
          </div>
          
          <div className="flex items-center gap-1">
            {allowMinimize && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleMinimize}
                className="w-8 h-8 p-0"
              >
                {isMinimized ? (
                  <Maximize2 className="w-4 h-4" />
                ) : (
                  <Minimize2 className="w-4 h-4" />
                )}
              </Button>
            )}
            
            {(mode === 'popup' || mode === 'sidebar') && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClose}
                className="w-8 h-8 p-0"
              >
                ×
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Widget Content */}
      {!isMinimized && (
        <div className={cn(
          "p-4",
          mode === 'sidebar' && "h-full overflow-y-auto"
        )}>
          {services.length === 0 ? (
            <div className="text-center py-8">
              <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-semibold mb-2">Booking Unavailable</h3>
              <p className="text-gray-600 mb-4">
                Online booking is not currently available. Please contact us directly.
              </p>
              
              <div className="space-y-2">
                {companyPhone && (
                  <Button
                    variant="outline"
                    className="w-full flex items-center gap-2"
                    onClick={() => window.open(`tel:${companyPhone}`)}
                  >
                    <Phone className="w-4 h-4" />
                    Call {companyPhone}
                  </Button>
                )}
                
                {companyEmail && (
                  <Button
                    variant="outline"
                    className="w-full flex items-center gap-2"
                    onClick={() => window.open(`mailto:${companyEmail}`)}
                  >
                    <Mail className="w-4 h-4" />
                    Email Us
                  </Button>
                )}
              </div>
            </div>
          ) : (
            <Hero365BookingWizard
              businessId={businessId}
              services={services}
              onComplete={handleBookingComplete}
              className="max-w-none"
            />
          )}
        </div>
      )}

      {/* Widget Footer */}
      {showFooter && !isMinimized && (
        <div className="bg-gray-50 border-t px-4 py-2 text-center">
          <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
            <span>Powered by</span>
            <a 
              href="https://hero365.ai" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium"
            >
              Hero365
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      )}
    </div>
  );

  // For popup mode, add backdrop
  if (mode === 'popup') {
    return (
      <div className="fixed inset-0 z-40">
        <div 
          className="absolute inset-0 bg-black bg-opacity-25"
          onClick={handleClose}
        />
        {widgetContent}
      </div>
    );
  }

  return widgetContent;
}

// Widget Launcher Button (for popup mode)
export function BookingWidgetLauncher({
  onClick,
  companyName = 'Book Appointment',
  primaryColor = '#3b82f6',
  className
}: {
  onClick: () => void;
  companyName?: string;
  primaryColor?: string;
  className?: string;
}) {
  return (
    <Button
      onClick={onClick}
      className={cn(
        "fixed bottom-4 right-4 z-40 rounded-full shadow-lg",
        className
      )}
      style={{
        backgroundColor: primaryColor,
      }}
    >
      <Calendar className="w-5 h-5 mr-2" />
      {companyName}
    </Button>
  );
}

// Utility function to generate embed code
export function generateEmbedCode(config: {
  businessId: string;
  mode?: 'popup' | 'inline' | 'sidebar';
  theme?: 'light' | 'dark' | 'auto';
  primaryColor?: string;
  companyName?: string;
  width?: string;
  height?: string;
}) {
  const {
    businessId,
    mode = 'inline',
    theme = 'light',
    primaryColor = '#3b82f6',
    companyName = 'Book Appointment',
    width = '100%',
    height = '600px'
  } = config;

  const baseUrl = process.env.NEXT_PUBLIC_WIDGET_URL || 'https://hero365.ai/widget';
  const params = new URLSearchParams({
    businessId,
    mode,
    theme,
    primaryColor,
    companyName
  });

  const iframeCode = `<iframe 
  src="${baseUrl}?${params.toString()}" 
  width="${width}" 
  height="${height}"
  frameborder="0"
  style="border: none; border-radius: 8px;"
  title="Book Appointment - ${companyName}">
</iframe>`;

  const scriptCode = `<script>
  (function() {
    var script = document.createElement('script');
    script.src = '${baseUrl}/embed.js';
    script.setAttribute('data-business-id', '${businessId}');
    script.setAttribute('data-mode', '${mode}');
    script.setAttribute('data-theme', '${theme}');
    script.setAttribute('data-primary-color', '${primaryColor}');
    script.setAttribute('data-company-name', '${companyName}');
    document.head.appendChild(script);
  })();
</script>`;

  return {
    iframe: iframeCode,
    script: scriptCode,
    directUrl: `${baseUrl}?${params.toString()}`
  };
}
