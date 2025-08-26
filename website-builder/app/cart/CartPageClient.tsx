'use client';

import { useCart } from '@/lib/contexts/CartContext';
import { CartItem } from '@/lib/types/products';
import { BookingCTAButton } from '@/components/booking/BookingWidgetProvider';
import { useState } from 'react';
import Image from 'next/image';

interface CartPageClientProps {
  businessProfile: any;
}

export function CartPageClient({ businessProfile }: CartPageClientProps) {
  const { cart, cartSummary, isLoading, error, updateCartItem, removeFromCart, clearCart } = useCart();
  const [updatingItems, setUpdatingItems] = useState<Set<string>>(new Set());

  const formatPrice = (price: number) => {
    return price.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  };

  const handleQuantityChange = async (itemId: string, newQuantity: number) => {
    if (newQuantity < 1 || newQuantity > 10) return;
    
    setUpdatingItems(prev => new Set(prev).add(itemId));
    
    try {
      await updateCartItem(itemId, newQuantity);
    } finally {
      setUpdatingItems(prev => {
        const next = new Set(prev);
        next.delete(itemId);
        return next;
      });
    }
  };

  const handleRemoveItem = async (itemId: string) => {
    if (!confirm('Remove this item from your cart?')) return;
    
    setUpdatingItems(prev => new Set(prev).add(itemId));
    
    try {
      await removeFromCart(itemId);
    } finally {
      setUpdatingItems(prev => {
        const next = new Set(prev);
        next.delete(itemId);
        return next;
      });
    }
  };

  const handleClearCart = async () => {
    if (!confirm('Clear all items from your cart?')) return;
    await clearCart();
  };

  if (isLoading && !cart) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your cart...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            <strong className="font-bold">Error: </strong>
            <span>{error}</span>
          </div>
          <a 
            href="/products"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Continue Shopping
          </a>
        </div>
      </div>
    );
  }

  // Empty cart state
  if (!cart || !cart.items || cart.items.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <svg className="mx-auto h-24 w-24 text-gray-400 mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l-1 12H6L5 9z" />
          </svg>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Your Cart is Empty</h1>
          <p className="text-lg text-gray-600 mb-8">
            Add some professional equipment to get started with your project.
          </p>
          <div className="space-x-4">
            <a 
              href="/products"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              Browse Products
              <svg className="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
              </svg>
            </a>
            <a 
              href="/"
              className="inline-flex items-center px-6 py-3 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
            >
              Back to Home
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav className="flex mb-8" aria-label="Breadcrumb">
        <ol className="inline-flex items-center space-x-1 md:space-x-3">
          <li className="inline-flex items-center">
            <a href="/" className="text-gray-500 hover:text-gray-700">
              Home
            </a>
          </li>
          <li>
            <div className="flex items-center">
              <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 111.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
              <span className="ml-1 text-gray-500">Shopping Cart</span>
            </div>
          </li>
        </ol>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900">
              Shopping Cart ({cart.item_count} {cart.item_count === 1 ? 'item' : 'items'})
            </h1>
            {cart.items.length > 0 && (
              <button
                onClick={handleClearCart}
                className="text-red-600 hover:text-red-800 text-sm font-medium"
              >
                Clear Cart
              </button>
            )}
          </div>

          <div className="space-y-4">
            {cart.items.map((item) => (
              <div key={item.id} className="bg-white border border-gray-200 rounded-lg p-6">
                <div className="flex flex-col sm:flex-row gap-4">
                  {/* Product Image Placeholder */}
                  <div className="flex-shrink-0">
                    <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg flex items-center justify-center">
                      <svg className="h-8 w-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H3m2 0h4M9 7h6m-6 4h6m-2 4h2" />
                      </svg>
                    </div>
                  </div>

                  {/* Product Details */}
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {item.product_name}
                    </h3>
                    <p className="text-sm text-gray-600 mb-2">SKU: {item.product_sku}</p>
                    
                    {item.installation_option_name && (
                      <div className="flex items-center text-sm text-blue-600 mb-2">
                        <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        Installation: {item.installation_option_name}
                      </div>
                    )}

                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                      {/* Quantity Controls */}
                      <div className="flex items-center space-x-3">
                        <label className="text-sm font-medium text-gray-700">Qty:</label>
                        <div className="flex items-center border border-gray-300 rounded">
                          <button
                            onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                            disabled={item.quantity <= 1 || updatingItems.has(item.id)}
                            className="px-3 py-1 text-gray-600 hover:text-gray-800 disabled:text-gray-400 disabled:cursor-not-allowed"
                          >
                            −
                          </button>
                          <span className="px-4 py-1 text-gray-900 font-medium min-w-[3rem] text-center">
                            {updatingItems.has(item.id) ? '...' : item.quantity}
                          </span>
                          <button
                            onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                            disabled={item.quantity >= 10 || updatingItems.has(item.id)}
                            className="px-3 py-1 text-gray-600 hover:text-gray-800 disabled:text-gray-400 disabled:cursor-not-allowed"
                          >
                            +
                          </button>
                        </div>
                      </div>

                      {/* Pricing */}
                      <div className="text-right">
                        <div className="text-lg font-semibold text-gray-900">
                          {formatPrice(item.item_total)}
                        </div>
                        {(item.discount_amount > 0 || item.membership_discount > 0 || item.bundle_savings > 0) && (
                          <div className="text-sm text-green-600">
                            Save {formatPrice(item.discount_amount + item.membership_discount + item.bundle_savings)}
                          </div>
                        )}
                        <div className="text-xs text-gray-600">
                          {formatPrice(item.unit_price)} + {formatPrice(item.installation_price)} install
                        </div>
                      </div>
                    </div>

                    {/* Remove Button */}
                    <div className="mt-4 flex justify-end">
                      <button
                        onClick={() => handleRemoveItem(item.id)}
                        disabled={updatingItems.has(item.id)}
                        className="text-red-600 hover:text-red-800 text-sm font-medium disabled:text-gray-400"
                      >
                        {updatingItems.has(item.id) ? 'Removing...' : 'Remove'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="bg-gray-50 rounded-lg p-6 sticky top-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Order Summary</h2>
            
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-medium">{formatPrice(cart.subtotal)}</span>
              </div>
              
              {cart.total_savings > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Savings</span>
                  <span>-{formatPrice(cart.total_savings)}</span>
                </div>
              )}
              
              {cart.tax_amount > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax</span>
                  <span className="font-medium">{formatPrice(cart.tax_amount)}</span>
                </div>
              )}
              
              <hr className="my-4" />
              
              <div className="flex justify-between text-xl font-bold">
                <span>Total</span>
                <span>{formatPrice(cart.total_amount)}</span>
              </div>

              {cartSummary && cartSummary.savings_percentage > 0 && (
                <div className="text-sm text-green-600 text-center">
                  You're saving {cartSummary.savings_percentage.toFixed(0)}% on this order!
                </div>
              )}
            </div>

            <div className="mt-6 space-y-3">
              <button 
                className="w-full bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors"
                disabled={isLoading}
              >
                Proceed to Checkout
              </button>
              
              <div className="flex space-x-3">
                <BookingCTAButton className="flex-1 text-sm py-2">
                  Schedule Install
                </BookingCTAButton>
                <a 
                  href={`tel:${businessProfile.phone}`}
                  className="flex-1 border border-gray-300 text-gray-700 font-medium py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors text-center text-sm"
                >
                  Call for Quote
                </a>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="text-center">
                <a 
                  href="/products"
                  className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium"
                >
                  <svg className="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
                  </svg>
                  Continue Shopping
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
