'use client';

import { CheckoutFormData, CheckoutValidation, US_STATES } from '@/lib/types/checkout';

interface CustomerInfoStepProps {
  formData: CheckoutFormData;
  setFormData: (data: CheckoutFormData) => void;
  validation: CheckoutValidation;
  onNext: () => void;
  onPrevious?: () => void;
}

export function CustomerInfoStep({ 
  formData, 
  setFormData, 
  validation, 
  onNext 
}: CustomerInfoStepProps) {
  
  const updateCustomer = (field: keyof CheckoutFormData['customer'], value: string) => {
    setFormData({
      ...formData,
      customer: {
        ...formData.customer,
        [field]: value
      }
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
        <h2 className="text-xl font-semibold text-gray-900">Customer Information</h2>
        <p className="text-sm text-gray-600 mt-1">
          Please provide your contact information and service address
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Full Name *
          </label>
          <input
            type="text"
            id="name"
            value={formData.customer.name}
            onChange={(e) => updateCustomer('name', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validation.errors.name ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Enter your full name"
          />
          {validation.errors.name && (
            <p className="mt-1 text-xs text-red-600">{validation.errors.name}</p>
          )}
        </div>

        {/* Email */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email Address *
          </label>
          <input
            type="email"
            id="email"
            value={formData.customer.email}
            onChange={(e) => updateCustomer('email', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validation.errors.email ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Enter your email address"
          />
          {validation.errors.email && (
            <p className="mt-1 text-xs text-red-600">{validation.errors.email}</p>
          )}
        </div>

        {/* Phone */}
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
            Phone Number *
          </label>
          <input
            type="tel"
            id="phone"
            value={formData.customer.phone}
            onChange={(e) => updateCustomer('phone', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validation.errors.phone ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="(555) 123-4567"
          />
          {validation.errors.phone && (
            <p className="mt-1 text-xs text-red-600">{validation.errors.phone}</p>
          )}
        </div>

        {/* Address */}
        <div>
          <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
            Service Address *
          </label>
          <input
            type="text"
            id="address"
            value={formData.customer.address}
            onChange={(e) => updateCustomer('address', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validation.errors.address ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="123 Main Street"
          />
          {validation.errors.address && (
            <p className="mt-1 text-xs text-red-600">{validation.errors.address}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            This is where the installation will take place
          </p>
        </div>

        {/* City, State, ZIP */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-1">
            <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-1">
              City *
            </label>
            <input
              type="text"
              id="city"
              value={formData.customer.city}
              onChange={(e) => updateCustomer('city', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                validation.errors.city ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Austin"
            />
            {validation.errors.city && (
              <p className="mt-1 text-xs text-red-600">{validation.errors.city}</p>
            )}
          </div>

          <div className="md:col-span-1">
            <label htmlFor="state" className="block text-sm font-medium text-gray-700 mb-1">
              State *
            </label>
            <select
              id="state"
              value={formData.customer.state}
              onChange={(e) => updateCustomer('state', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                validation.errors.state ? 'border-red-300' : 'border-gray-300'
              }`}
            >
              <option value="">Select State</option>
              {US_STATES.map((state) => (
                <option key={state} value={state}>
                  {state}
                </option>
              ))}
            </select>
            {validation.errors.state && (
              <p className="mt-1 text-xs text-red-600">{validation.errors.state}</p>
            )}
          </div>

          <div className="md:col-span-1">
            <label htmlFor="zip_code" className="block text-sm font-medium text-gray-700 mb-1">
              ZIP Code *
            </label>
            <input
              type="text"
              id="zip_code"
              value={formData.customer.zip_code}
              onChange={(e) => updateCustomer('zip_code', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                validation.errors.zip_code ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="78701"
              maxLength={10}
            />
            {validation.errors.zip_code && (
              <p className="mt-1 text-xs text-red-600">{validation.errors.zip_code}</p>
            )}
          </div>
        </div>

        {/* Next Button */}
        <div className="flex justify-end pt-6">
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            Continue to Installation
          </button>
        </div>
      </form>
    </div>
  );
}
