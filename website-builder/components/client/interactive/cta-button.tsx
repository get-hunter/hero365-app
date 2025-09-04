/**
 * Simple CTA Button - No context required
 * 
 * Basic CTA button for use in headers without requiring booking provider context
 */

'use client';

import React from 'react';

interface SimpleCTAButtonProps {
  children: React.ReactNode;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
}

export function SimpleCTAButton({ 
  children, 
  className = '', 
  size = 'md',
  onClick 
}: SimpleCTAButtonProps) {
  const sizeClasses = {
    sm: 'text-xs px-3 py-1',
    md: 'text-sm px-4 py-2',
    lg: 'text-base px-6 py-3'
  };

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      // Default behavior - scroll to booking section or open booking
      const bookingSection = document.querySelector('#booking');
      if (bookingSection) {
        bookingSection.scrollIntoView({ behavior: 'smooth' });
      } else {
        // Navigate to booking page
        window.location.href = '/booking';
      }
    }
  };

  return (
    <button
      onClick={handleClick}
      className={`bg-blue-600 hover:bg-blue-700 text-white font-medium rounded transition-colors ${sizeClasses[size]} ${className}`}
    >
      {children}
    </button>
  );
}
