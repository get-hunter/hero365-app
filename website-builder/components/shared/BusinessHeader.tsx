/**
 * Shared Business Header Component
 * 
 * Consistent header implementation across all pages
 * Uses real business data with proper fallbacks
 */

import React from 'react';
import Header from '@/components/server/layout/header';
import { SimpleCTAButton } from '@/components/client/interactive/cta-button';
import { SimpleCartIndicator } from '@/components/client/interactive/cart-indicator';

interface BusinessProfile {
  business_id: string;
  business_name: string;
  phone: string;
  phone_display?: string;
  email: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  logo_url?: string;
}

interface BusinessHeaderProps {
  businessProfile: BusinessProfile;
  showCTA?: boolean;
  showCart?: boolean;
  supportHours?: string;
  primaryColor?: string;
  logoUrl?: string;
}

export default function BusinessHeader({
  businessProfile,
  showCTA = false,
  showCart = false,
  supportHours = "24/7",
  primaryColor = "#2563eb",
  logoUrl = "/logo.png"
}: BusinessHeaderProps) {
  
  // Prepare business data for Header component
  const headerProps = {
    businessName: businessProfile.business_name || 'Professional Services',
    city: businessProfile.city || 'Austin',
    state: businessProfile.state || 'TX',
    phone: businessProfile.phone_display || businessProfile.phone || '',
    supportHours,
    primaryColor,
    // Only pass logo if business has one, otherwise Header will show business name
    ...(businessProfile.logo_url && { logo: businessProfile.logo_url }),
    // Only include slots if requested
    ...(showCTA && { ctaSlot: <SimpleCTAButton /> }),
    ...(showCart && { cartSlot: <SimpleCartIndicator /> })
  };

  return <Header {...headerProps} />;
}
