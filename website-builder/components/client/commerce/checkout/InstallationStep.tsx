'use client';

import { CheckoutFormData, CheckoutValidation } from '@/lib/shared/types/checkout';

interface InstallationStepProps {
  formData: CheckoutFormData;
  setFormData: (data: CheckoutFormData) => void;
  validation: CheckoutValidation;
  onNext: () => void;
  onPrevious?: () => void;
}

export function InstallationStep({ 
  formData, 
  setFormData, 
  validation, 
  onNext, 
  onPrevious 
}: InstallationStepProps) {
  
  const updateInstallation = (field: keyof CheckoutFormData['installation'], value: string) => {
    setFormData({
      ...formData,
      installation: {
        ...formData.installation,
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

  // Get minimum date (tomorrow)
  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  // Get maximum date (90 days from now)
  const getMaxDate = () => {
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 90);
    return maxDate.toISOString().split('T')[0];
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Installation Scheduling</h2>
        <p className="text-sm text-gray-600 mt-1">
          Choose your preferred installation date and provide any special instructions
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Installation Date */}
        <div>
          <label htmlFor="preferred_date" className="block text-sm font-medium text-gray-700 mb-1">
            Preferred Installation Date *
          </label>
          <input
            type="date"
            id="preferred_date"
            value={formData.installation.preferred_date}
            onChange={(e) => updateInstallation('preferred_date', e.target.value)}
            min={getMinDate()}
            max={getMaxDate()}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validation.errors.preferred_date ? 'border-red-300' : 'border-gray-300'
            }`}
          />
          {validation.errors.preferred_date && (
            <p className="mt-1 text-xs text-red-600">{validation.errors.preferred_date}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Our team will contact you within 24 hours to confirm the exact appointment time
          </p>
        </div>

        {/* Time Preference */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Preferred Time of Day *
          </label>
          <div className="space-y-2">
            {[
              { value: 'morning', label: 'Morning (8:00 AM - 12:00 PM)', desc: 'Best for early birds' },
              { value: 'afternoon', label: 'Afternoon (12:00 PM - 5:00 PM)', desc: 'Most popular time slot' },
              { value: 'evening', label: 'Evening (5:00 PM - 8:00 PM)', desc: 'After work convenience' }
            ].map((option) => (
              <label key={option.value} className="flex items-start space-x-3">
                <input
                  type="radio"
                  name="preferred_time"
                  value={option.value}
                  checked={formData.installation.preferred_time === option.value}
                  onChange={(e) => updateInstallation('preferred_time', e.target.value)}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">{option.label}</div>
                  <div className="text-xs text-gray-500">{option.desc}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Special Instructions */}
        <div>
          <label htmlFor="special_instructions" className="block text-sm font-medium text-gray-700 mb-1">
            Special Installation Instructions
          </label>
          <textarea
            id="special_instructions"
            value={formData.installation.special_instructions || ''}
            onChange={(e) => updateInstallation('special_instructions', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Any special requirements or preferences for the installation..."
          />
          <p className="mt-1 text-xs text-gray-500">
            Optional: Let us know about any specific needs or concerns
          </p>
        </div>

        {/* Access Instructions */}
        <div>
          <label htmlFor="access_instructions" className="block text-sm font-medium text-gray-700 mb-1">
            Property Access Instructions
          </label>
          <textarea
            id="access_instructions"
            value={formData.installation.access_instructions || ''}
            onChange={(e) => updateInstallation('access_instructions', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Gate codes, key location, parking instructions, dog warnings, etc."
          />
          <p className="mt-1 text-xs text-gray-500">
            Optional: Help our technicians access your property safely and efficiently
          </p>
        </div>

        {/* Installation Info Box */}
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <div className="flex">
            <svg className="h-5 w-5 text-blue-400 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="text-sm font-medium text-blue-900">Installation Process</h4>
              <div className="text-sm text-blue-800 mt-1">
                <p className="mb-2">Our professional installation team will:</p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li>Confirm appointment 24 hours in advance</li>
                  <li>Arrive within the scheduled time window</li>
                  <li>Provide all necessary tools and equipment</li>
                  <li>Clean up after installation is complete</li>
                  <li>Test all equipment and provide warranty information</li>
                </ul>
              </div>
            </div>
          </div>
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
            Continue to Payment
          </button>
        </div>
      </form>
    </div>
  );
}
