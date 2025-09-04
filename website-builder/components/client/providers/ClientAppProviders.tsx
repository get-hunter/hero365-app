'use client';

import React from 'react';
import { CartProvider } from '@/lib/client/contexts/CartContext';
import { Hero365BookingProvider } from '@/components/client/commerce/booking/Hero365BookingProvider';
import type { BookableService } from '@/lib/shared/types/booking';

interface ClientAppProvidersProps {
  businessId: string;
  services: BookableService[];
  companyName?: string;
  companyPhone?: string;
  companyEmail?: string;
  children: React.ReactNode;
}

export default function ClientAppProviders({
  businessId,
  services,
  companyName,
  companyPhone,
  companyEmail,
  children,
}: ClientAppProvidersProps) {
  return (
    <CartProvider businessId={businessId}>
      <Hero365BookingProvider
        businessId={businessId}
        services={services}
        companyName={companyName}
        companyPhone={companyPhone}
        companyEmail={companyEmail}
      >
        {children}
      </Hero365BookingProvider>
    </CartProvider>
  );
}


