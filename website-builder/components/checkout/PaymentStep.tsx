'use client';

import { CheckoutFormData, CheckoutValidation } from '@/lib/types/checkout';

interface PaymentStepProps {
  formData: CheckoutFormData;
  setFormData: (data: CheckoutFormData) => void;
  validation: CheckoutValidation;
  onNext: () => void;
  onPrevious?: () => void;
}

export function PaymentStep({ 
  formData, 
  setFormData, 
  validation, 
  onNext, 
  onPrevious 
}: PaymentStepProps) {
  
  const updatePaymentMethod = (method: 'card' | 'check' | 'cash') => {
    setFormData({
      ...formData,
      payment_method: method
    });
  };

  const updateMembershipType = (type: string) => {
    setFormData({
      ...formData,
      membership_type: type
    });
  };

  const updateNotes = (notes: string) => {
    setFormData({
      ...formData,
      notes: notes
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validation.isValid) {
      onNext();
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Payment & Membership</h2>
        <p className="text-sm text-gray-600 mt-1">
          Select your payment method and membership level
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Membership Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Membership Level
          </label>
          <div className="space-y-3">
            {[
              { 
                value: 'none', 
                label: 'No Membership', 
                desc: 'Standard pricing',
                savings: null
              },
              { 
                value: 'residential', 
                label: 'Residential Membership', 
                desc: 'Special pricing for homeowners',
                savings: 'Save 10-15%'
              },
              { 
                value: 'commercial', 
                label: 'Commercial Membership', 
                desc: 'Business & property manager rates',
                savings: 'Save 15-20%'
              },
              { 
                value: 'premium', 
                label: 'Premium Membership', 
                desc: 'VIP service with maximum savings',
                savings: 'Save 20-25%'
              }
            ].map((option) => (
              <label key={option.value} className="flex items-start space-x-3 p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors cursor-pointer">
                <input
                  type="radio"
                  name="membership_type"
                  value={option.value}
                  checked={formData.membership_type === option.value}
                  onChange={(e) => updateMembershipType(e.target.value)}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-medium text-gray-900">{option.label}</div>
                    {option.savings && (
                      <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded">
                        {option.savings}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">{option.desc}</div>
                </div>
              </label>
            ))}
          </div>
          <p className="mt-2 text-xs text-gray-500">
            Membership pricing is automatically applied to your cart total
          </p>
        </div>

        {/* Payment Method */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Payment Method *
          </label>
          <div className="space-y-2">
            {[
              { 
                value: 'card', 
                label: 'Credit/Debit Card', 
                desc: 'Secure payment processing',
                icon: (
                  <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4zM18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" />
                  </svg>
                )
              },
              { 
                value: 'check', 
                label: 'Check Payment', 
                desc: 'Pay by check upon completion',
                icon: (
                  <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V4a2 2 0 00-2-2H6zm1 2a1 1 0 000 2h6a1 1 0 100-2H7zm6 7a1 1 0 011 1v3a1 1 0 11-2 0v-3a1 1 0 011-1zm-3 3a1 1 0 100 2h.01a1 1 0 100-2H10zm-4 1a1 1 0 011-1h.01a1 1 0 110 2H7a1 1 0 01-1-1zm1-4a1 1 0 100 2h.01a1 1 0 100-2H7zm2 0a1 1 0 100 2h.01a1 1 0 100-2H9zm2 0a1 1 0 100 2h.01a1 1 0 100-2H11z" clipRule="evenodd" />
                  </svg>
                )
              },
              { 
                value: 'cash', 
                label: 'Cash Payment', 
                desc: 'Pay cash upon completion',
                icon: (
                  <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" />
                  </svg>
                )
              }
            ].map((option) => (
              <label key={option.value} className="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors cursor-pointer">
                <input
                  type="radio"
                  name="payment_method"
                  value={option.value}
                  checked={formData.payment_method === option.value}
                  onChange={(e) => updatePaymentMethod(e.target.value as 'card' | 'check' | 'cash')}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <div className="mr-3 mt-0.5">
                  {option.icon}
                </div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">{option.label}</div>
                  <div className="text-xs text-gray-500">{option.desc}</div>
                </div>
              </label>
            ))}
          </div>
          {validation.errors.payment_method && (
            <p className="mt-1 text-xs text-red-600">{validation.errors.payment_method}</p>
          )}
        </div>

        {/* Payment Information */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex">
            <svg className="h-5 w-5 text-yellow-400 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="text-sm font-medium text-yellow-900">Payment Information</h4>
              <div className="text-sm text-yellow-800 mt-1">
                {formData.payment_method === 'card' && (
                  <p>Credit card payment will be processed securely after installation completion and your satisfaction confirmation.</p>
                )}
                {formData.payment_method === 'check' && (
                  <p>Please have a check ready for the total amount upon completion of installation. We accept personal and business checks.</p>
                )}
                {formData.payment_method === 'cash' && (
                  <p>Please have the exact cash amount ready upon completion of installation. We cannot provide change for large bills.</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Additional Notes */}
        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
            Additional Notes
          </label>
          <textarea
            id="notes"
            value={formData.notes}
            onChange={(e) => updateNotes(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Any additional information or special requests..."
          />
          <p className="mt-1 text-xs text-gray-500">
            Optional: Any other details we should know about your order
          </p>
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between pt-6">
          {onPrevious && (
            <button
              type="button"
              onClick={onPrevious}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Previous
            </button>
          )}
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Review Order
          </button>
        </div>
      </form>
    </div>
  );
}
