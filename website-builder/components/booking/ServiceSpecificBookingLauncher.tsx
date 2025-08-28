/**
 * Service-Specific Booking Launcher
 * 
 * Launches booking flow for a specific service with membership integration
 */

'use client';

import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { 
  Calendar, 
  Phone, 
  Star, 
  Clock, 
  CheckCircle, 
  Shield,
  Crown,
  Zap
} from 'lucide-react';
// Inline fallback instead of dialog to avoid missing dependency in build
import { ServicePricing, MembershipPlan } from '../../lib/types/membership';
import BookingWizard from './BookingWizard';
import { cn } from '../../lib/utils';

interface ServiceSpecificBookingLauncherProps {
  service: ServicePricing;
  businessId: string;
  businessName?: string;
  businessPhone?: string;
  businessEmail?: string;
  customerMembershipType?: 'residential' | 'commercial' | 'premium' | null;
  membershipPlans?: MembershipPlan[];
  
  // Styling
  variant?: 'primary' | 'outline' | 'ghost';
  size?: 'sm' | 'default' | 'lg';
  showPricing?: boolean;
  showMembershipBadge?: boolean;
  className?: string;
  
  // Event handlers
  onBookingComplete?: (bookingData: any) => void;
  onBookingError?: (error: string) => void;
}

export default function ServiceSpecificBookingLauncher({
  service,
  businessId,
  businessName = 'Professional Services',
  businessPhone,
  businessEmail,
  customerMembershipType = null,
  membershipPlans = [],
  variant = 'primary',
  size = 'default',
  showPricing = true,
  showMembershipBadge = true,
  className,
  onBookingComplete,
  onBookingError
}: ServiceSpecificBookingLauncherProps) {
  const [isBookingOpen, setIsBookingOpen] = useState(false);

  // Calculate pricing based on membership
  const getPricing = () => {
    const basePrice = service.base_price;
    let memberPrice = basePrice;
    let discountPercentage = 0;
    
    if (customerMembershipType) {
      const plan = membershipPlans.find(p => p.type === customerMembershipType);
      discountPercentage = plan?.discount_percentage || 0;
      
      switch (customerMembershipType) {
        case 'residential':
          memberPrice = service.residential_member_price || basePrice;
          break;
        case 'commercial':
          memberPrice = service.commercial_member_price || basePrice;
          break;
        case 'premium':
          memberPrice = service.premium_member_price || basePrice;
          break;
      }
    }
    
    return {
      base: basePrice,
      member: memberPrice,
      savings: basePrice - memberPrice,
      hasSavings: memberPrice < basePrice,
      discountPercentage
    };
  };

  // Format price display
  const formatPrice = (price: number) => {
    if (price === 0) return 'FREE';
    if (service.price_display === 'quote_required') return 'Quote Required';
    if (service.price_display === 'free') return 'FREE';
    
    const formattedPrice = price.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
    
    return service.price_display === 'from' ? `from ${formattedPrice}` : formattedPrice;
  };

  // Get membership badge icon
  const getMembershipIcon = () => {
    switch (customerMembershipType) {
      case 'commercial':
        return Zap;
      case 'premium':
        return Crown;
      default:
        return Star;
    }
  };

  const pricing = getPricing();
  const MembershipIcon = getMembershipIcon();
  
  // Determine button text and style
  const getButtonConfig = () => {
    if (service.price_display === 'free') {
      return {
        text: 'Get Free Estimate',
        icon: CheckCircle,
        urgency: false
      };
    }
    
    // No explicit emergency flag in ServicePricing; treat all as standard for now
    return {
      text: 'Book Now',
      icon: Calendar,
      urgency: false
    };
  };

  const buttonConfig = getButtonConfig();
  const ButtonIcon = buttonConfig.icon;

  const handleBookingLaunch = () => {
    setIsBookingOpen(true);
  };

  const handleBookingClose = () => {
    setIsBookingOpen(false);
  };

  const handleBookingSuccess = (bookingData: any) => {
    setIsBookingOpen(false);
    onBookingComplete?.(bookingData);
  };

  const handleBookingFailure = (error: string) => {
    onBookingError?.(error);
  };

  return (
    <>
      <div className={cn("space-y-2", className)}>
        {/* Pricing Display */}
        {showPricing && (
          <div className="space-y-1">
            {pricing.hasSavings ? (
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500 line-through">
                    {formatPrice(pricing.base)}
                  </span>
                  {showMembershipBadge && customerMembershipType && (
                    <Badge variant="secondary" className="bg-blue-100 text-blue-800 text-xs">
                      <MembershipIcon className="h-3 w-3 mr-1" />
                      Member
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-blue-600">
                    {formatPrice(pricing.member)}
                  </span>
                  <span className="text-xs text-green-600 font-medium">
                    Save ${pricing.savings.toLocaleString()}
                  </span>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <span className="font-semibold">
                  {formatPrice(pricing.base)}
                </span>
                {showMembershipBadge && customerMembershipType && (
                  <Badge variant="secondary" className="bg-blue-100 text-blue-800 text-xs">
                    <MembershipIcon className="h-3 w-3 mr-1" />
                    Member
                  </Badge>
                )}
              </div>
            )}
            
            {service.duration_estimate && (
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock className="h-3 w-3" />
                <span>{service.duration_estimate}</span>
              </div>
            )}
          </div>
        )}

        {/* Booking Button */}
        <Button
          onClick={handleBookingLaunch}
          variant={variant === 'primary' ? 'default' : variant}
          size={size}
          className={cn(
            "w-full",
            buttonConfig.urgency && "bg-red-600 hover:bg-red-700 animate-pulse",
            customerMembershipType && !buttonConfig.urgency && "bg-blue-600 hover:bg-blue-700"
          )}
        >
          <ButtonIcon className="h-4 w-4 mr-2" />
          {buttonConfig.text}
        </Button>

        {/* Member Benefits Preview */}
        {customerMembershipType && (
          <div className="text-xs text-gray-600">
            <div className="flex items-center gap-1">
              <Shield className="h-3 w-3 text-blue-600" />
              <span>Priority service • Extended warranty • Free diagnostics</span>
            </div>
          </div>
        )}

        {/* Call Option for High-Value Services */}
        {service.base_price > 1000 && (
          <Button
            variant="outline"
            size="sm"
            className="w-full text-xs"
            onClick={() => businessPhone && window.open(`tel:${businessPhone}`)}
          >
            <Phone className="h-3 w-3 mr-1" />
            Call for Consultation
          </Button>
        )}
      </div>

      {/* Booking Inline Panel (fallback for missing dialog component) */}
      {isBookingOpen && (
        <div className="fixed inset-0 z-40 bg-black/40">
          <div className="absolute inset-0 flex items-center justify-center p-4" onClick={handleBookingClose}>
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
              <div className="p-6 pb-0 flex items-center gap-2 border-b">
                <Calendar className="h-5 w-5 text-blue-600" />
                <h3 className="text-lg font-semibold">Book {service.service_name}</h3>
                {customerMembershipType && (
                  <Badge className="ml-2 bg-blue-100 text-blue-800">
                    <MembershipIcon className="h-3 w-3 mr-1" />
                    {customerMembershipType.charAt(0).toUpperCase() + customerMembershipType.slice(1)} Member
                  </Badge>
                )}
              </div>
              <div className="flex-1 overflow-y-auto">
                <BookingWizard
                  businessId={businessId}
                  businessName={businessName}
                  businessPhone={businessPhone}
                  businessEmail={businessEmail}
                  services={[{
                    id: service.id,
                    name: service.service_name,
                    category: service.category,
                    description: service.description,
                    duration_minutes: service.duration_estimate ? 
                      parseInt(service.duration_estimate.replace(/\D/g, '')) * 60 : 90,
                    price_cents: (customerMembershipType ? pricing.member : pricing.base) * 100
                  }]}
                  onComplete={handleBookingSuccess}
                  className="h-full"
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
