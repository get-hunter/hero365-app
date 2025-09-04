/**
 * Simple Cart Indicator - No context required
 * 
 * Basic cart indicator for use in headers without requiring cart provider context
 */

'use client';

import React from 'react';
import { ShoppingBag } from 'lucide-react';

export function SimpleCartIndicator() {
  const handleClick = () => {
    // Navigate to cart page
    window.location.href = '/cart';
  };

  return (
    <button
      onClick={handleClick}
      className="relative p-2 text-gray-600 hover:text-gray-900 transition-colors"
      aria-label="Shopping cart"
    >
      <ShoppingBag className="w-6 h-6" />
      {/* Static badge for demo purposes */}
      <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
        0
      </span>
    </button>
  );
}
