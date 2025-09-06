'use client';

import React from 'react';
import SimpleErrorBoundary from '@/components/error/SimpleErrorBoundary';

export default function ClientRoot({ children }: { children: React.ReactNode }) {
  return (
    <SimpleErrorBoundary 
      businessName="Professional Services"
      showErrorDetails={process.env.NODE_ENV === 'development'}
    >
      {children}
    </SimpleErrorBoundary>
  );
}


