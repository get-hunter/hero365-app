'use client';

import { ShoppingBag } from 'lucide-react';
import { useCart } from '@/lib/client/contexts/CartContext';

export function Hero365CartIndicator() {
  const { cartSummary } = useCart();
  const itemCount = cartSummary?.item_count || 0;

  return (
    <a 
      href="/cart"
      className="relative flex items-center text-gray-700 hover:text-gray-900 font-medium"
    >
      <ShoppingBag className="w-5 h-5" />
      {itemCount > 0 && (
        <span className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
          {itemCount > 9 ? '9+' : itemCount}
        </span>
      )}

    </a>
  );
}
