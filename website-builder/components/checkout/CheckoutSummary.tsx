'use client';

import { ShoppingCart } from '@/lib/types/products';

interface CheckoutSummaryProps {
  cart: ShoppingCart | null;
  membershipType: string;
  businessProfile: any;
}

export function CheckoutSummary({ cart, membershipType, businessProfile }: CheckoutSummaryProps) {
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(price);
  };

  const getMembershipLabel = (type: string): string => {
    switch (type) {
      case 'residential': return 'Residential Member';
      case 'commercial': return 'Commercial Member';
      case 'premium': return 'Premium Member';
      default: return 'No Membership';
    }
  };

  // Handle null cart safely to avoid runtime errors during initial render
  if (!cart) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Summary</h3>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Summary</h3>
      
      {/* Cart Items */}
      <div className="space-y-4 mb-6">
        {cart.items && cart.items.map((item) => (
          <div key={`${item.product_id}-${item.installation_option_id}`} className="flex justify-between">
            <div className="flex-1">
              <div className="text-sm font-medium text-gray-900">
                {item.product_name}
              </div>
              <div className="text-xs text-gray-500">
                {item.installation_option_name || 'No Installation'} × {item.quantity}
              </div>
              {membershipType !== 'none' && (
                <div className="text-xs text-green-600">
                  {getMembershipLabel(membershipType)} Pricing
                </div>
              )}
            </div>
            <div className="text-sm font-medium text-gray-900">
              {formatPrice(item.item_total)}
            </div>
          </div>
        ))}
      </div>
      
      {/* Membership Badge */}
      {membershipType !== 'none' && (
        <div className="mb-6 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-blue-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <div className="text-sm font-medium text-blue-900">
                {getMembershipLabel(membershipType)}
              </div>
              <div className="text-xs text-blue-700">
                Exclusive pricing applied
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Price Breakdown */}
      <div className="space-y-2 pt-4 border-t border-gray-200">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Subtotal ({cart.item_count} items)</span>
          <span className="font-medium">{formatPrice(cart.subtotal)}</span>
        </div>
        
        {cart.total_savings > 0 && (
          <div className="flex justify-between text-sm text-green-600">
            <span>Savings</span>
            <span>-{formatPrice(cart.total_savings)}</span>
          </div>
        )}
        
        {cart.tax_amount > 0 && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Tax</span>
            <span className="font-medium">{formatPrice(cart.tax_amount)}</span>
          </div>
        )}
        
        <div className="flex justify-between text-base font-bold text-gray-900 pt-2 border-t border-gray-200">
          <span>Total</span>
          <span>{formatPrice(cart.total_amount)}</span>
        </div>
      </div>
      
      {/* Business Info */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="text-sm text-gray-600">
          <div className="font-medium text-gray-900">{businessProfile.business_name}</div>
          <div>{businessProfile.phone}</div>
          <div>{businessProfile.email}</div>
        </div>
      </div>
      
      {/* Security Badge */}
      <div className="mt-6 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center text-sm text-gray-600">
          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
          </svg>
          <span>Secure SSL Encryption</span>
        </div>
      </div>
    </div>
  );
}
