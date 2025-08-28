'use client';

import { CheckoutFormData, CheckoutValidation } from '@/lib/types/checkout';
import { ShoppingCart } from '@/lib/types/products';

interface ReviewStepProps {
  formData: CheckoutFormData;
  setFormData: (data: CheckoutFormData) => void;
  validation: CheckoutValidation;
  onPrevious?: () => void;
  onSubmit: () => void;
  isProcessing: boolean;
  cart: ShoppingCart;
  businessProfile: any;
}

export function ReviewStep({ 
  formData, 
  setFormData, 
  validation, 
  onPrevious, 
  onSubmit, 
  isProcessing,
  cart,
  businessProfile
}: ReviewStepProps) {
  
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

  const getPaymentMethodLabel = (method: string): string => {
    switch (method) {
      case 'card': return 'Credit/Debit Card';
      case 'check': return 'Check Payment';
      case 'cash': return 'Cash Payment';
      default: return method;
    }
  };

  const getTimeSlotLabel = (time: string): string => {
    switch (time) {
      case 'morning': return 'Morning (8:00 AM - 12:00 PM)';
      case 'afternoon': return 'Afternoon (12:00 PM - 5:00 PM)';
      case 'evening': return 'Evening (5:00 PM - 8:00 PM)';
      default: return time;
    }
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const updateTermsAccepted = (accepted: boolean) => {
    setFormData({
      ...formData,
      terms_accepted: accepted
    });
  };

  const updateEmailConsent = (consent: boolean) => {
    setFormData({
      ...formData,
      email_consent: consent
    });
  };

  const updateSMSConsent = (consent: boolean) => {
    setFormData({
      ...formData,
      sms_consent: consent
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validation.isValid && !isProcessing) {
      onSubmit();
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Review Your Order</h2>
        <p className="text-sm text-gray-600 mt-1">
          Please review all details before confirming your order
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Order Summary */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Order Summary</h3>
          
          <div className="space-y-3">
            {cart.items && cart.items.map((item) => (
              <div key={`${item.product_id}-${item.installation_option_id}`} className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">
                    {item.product_name}
                  </div>
                  <div className="text-xs text-gray-600">
                    {item.installation_option_name} × {item.quantity}
                  </div>
                  {(item as any).membership_type && (item as any).membership_type !== 'none' && (
                    <div className="text-xs text-green-600">
                      {getMembershipLabel((item as any).membership_type)} Pricing
                    </div>
                  )}
                </div>
                <div className="text-sm font-medium text-gray-900">
                  {formatPrice(item.item_total)}
                </div>
              </div>
            ))}
          </div>

          <div className="border-t border-gray-200 mt-4 pt-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Subtotal</span>
              <span className="font-medium">{formatPrice(cart.subtotal)}</span>
            </div>
            
            {cart.total_savings > 0 && (
              <div className="flex justify-between text-sm text-green-600">
                <span>Total Savings</span>
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
        </div>

        {/* Customer Information */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Customer Information</h3>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm font-medium text-gray-700">Name</div>
                <div className="text-sm text-gray-900">{formData.customer.name}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-700">Email</div>
                <div className="text-sm text-gray-900">{formData.customer.email}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-700">Phone</div>
                <div className="text-sm text-gray-900">{formData.customer.phone}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-700">Service Address</div>
                <div className="text-sm text-gray-900">
                  {formData.customer.address}<br />
                  {formData.customer.city}, {formData.customer.state} {formData.customer.zip_code}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Installation Details */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Installation Details</h3>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm font-medium text-gray-700">Preferred Date</div>
                <div className="text-sm text-gray-900">
                  {formatDate(formData.installation.preferred_date)}
                </div>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-700">Time Preference</div>
                <div className="text-sm text-gray-900">
                  {getTimeSlotLabel(formData.installation.preferred_time)}
                </div>
              </div>
              {formData.installation.special_instructions && (
                <div className="md:col-span-2">
                  <div className="text-sm font-medium text-gray-700">Special Instructions</div>
                  <div className="text-sm text-gray-900">{formData.installation.special_instructions}</div>
                </div>
              )}
              {formData.installation.access_instructions && (
                <div className="md:col-span-2">
                  <div className="text-sm font-medium text-gray-700">Access Instructions</div>
                  <div className="text-sm text-gray-900">{formData.installation.access_instructions}</div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Payment Information */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Payment Information</h3>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm font-medium text-gray-700">Membership Level</div>
                <div className="text-sm text-gray-900">{getMembershipLabel(formData.membership_type)}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-700">Payment Method</div>
                <div className="text-sm text-gray-900">{getPaymentMethodLabel(formData.payment_method)}</div>
              </div>
              {formData.notes && (
                <div className="md:col-span-2">
                  <div className="text-sm font-medium text-gray-700">Additional Notes</div>
                  <div className="text-sm text-gray-900">{formData.notes}</div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Terms and Agreements */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Terms & Agreements</h3>
          
          <div className="space-y-3">
            <label className="flex items-start space-x-3">
              <input
                type="checkbox"
                checked={formData.terms_accepted}
                onChange={(e) => updateTermsAccepted(e.target.checked)}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <div className="text-sm">
                <span className="text-gray-900">I accept the </span>
                <a href="/terms" target="_blank" className="text-blue-600 hover:text-blue-700 underline">
                  Terms and Conditions
                </a>
                <span className="text-gray-900"> and </span>
                <a href="/privacy" target="_blank" className="text-blue-600 hover:text-blue-700 underline">
                  Privacy Policy
                </a>
                <span className="text-red-500"> *</span>
              </div>
            </label>
            
            <label className="flex items-start space-x-3">
              <input
                type="checkbox"
                checked={formData.email_consent}
                onChange={(e) => updateEmailConsent(e.target.checked)}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <div className="text-sm text-gray-900">
                I consent to receive email updates about my order and installation
              </div>
            </label>
            
            <label className="flex items-start space-x-3">
              <input
                type="checkbox"
                checked={formData.sms_consent}
                onChange={(e) => updateSMSConsent(e.target.checked)}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <div className="text-sm text-gray-900">
                I consent to receive SMS notifications about my installation appointment
              </div>
            </label>
          </div>
          
          {validation.errors.terms_accepted && (
            <p className="text-xs text-red-600">{validation.errors.terms_accepted}</p>
          )}
        </div>

        {/* Business Contact */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900">Need Help?</h4>
          <div className="text-sm text-blue-800 mt-1">
            <p>Contact {businessProfile.business_name}:</p>
            <p>Phone: {businessProfile.phone}</p>
            <p>Email: {businessProfile.email}</p>
          </div>
        </div>

        {/* Submit Buttons */}
        <div className="flex justify-between pt-6">
          {onPrevious && (
            <button
              type="button"
              onClick={onPrevious}
              disabled={isProcessing}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              Previous
            </button>
          )}
          <button
            type="submit"
            disabled={!validation.isValid || isProcessing}
            className="px-8 py-3 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isProcessing ? (
              <div className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing Order...
              </div>
            ) : (
              `Confirm Order • ${formatPrice(cart.total_amount)}`
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
