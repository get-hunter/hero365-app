/**
 * Dynamic Booking Form Component
 * 
 * Renders booking forms dynamically based on activity's required and default booking fields.
 * Supports various field types and validation.
 */

'use client';

import { useState, useMemo } from 'react';
import { WebsiteActivityInfo, WebsiteBookingField, WebsiteBusinessInfo } from '@/lib/shared/hooks/useWebsiteContext';

interface BookingFormProps {
  activity: WebsiteActivityInfo;
  businessInfo: WebsiteBusinessInfo;
  onSubmit: (data: BookingFormData) => void;
  className?: string;
}

export interface BookingFormData {
  // Customer information
  name: string;
  email: string;
  phone: string;
  
  // Service details
  activity_slug: string;
  activity_name: string;
  
  // Dynamic fields based on activity
  [key: string]: any;
  
  // Metadata
  source: 'website';
  business_id: string;
}

export default function BookingForm({
  activity,
  businessInfo,
  onSubmit,
  className = ''
}: BookingFormProps) {
  
  // Combine required and default fields
  const allFields = useMemo(() => {
    const fields: (WebsiteBookingField & { isRequired: boolean })[] = [];
    
    // Add required fields
    activity.required_booking_fields.forEach(field => {
      fields.push({ ...field, isRequired: true });
    });
    
    // Add default fields (optional)
    activity.default_booking_fields.forEach(field => {
      // Don't duplicate if already in required fields
      if (!fields.some(f => f.key === field.key)) {
        fields.push({ ...field, isRequired: false });
      }
    });
    
    return fields;
  }, [activity]);
  
  // Form state
  const [formData, setFormData] = useState<Record<string, any>>({
    name: '',
    email: '',
    phone: '',
    activity_slug: activity.slug,
    activity_name: activity.name,
    business_id: businessInfo.id,
    source: 'website'
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Handle field change
  const handleFieldChange = (key: string, value: any) => {
    setFormData(prev => ({ ...prev, [key]: value }));
    
    // Clear error when user starts typing
    if (errors[key]) {
      setErrors(prev => ({ ...prev, [key]: '' }));
    }
  };
  
  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    // Validate required customer fields
    if (!formData.name?.trim()) {
      newErrors.name = 'Name is required';
    }
    if (!formData.email?.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    if (!formData.phone?.trim()) {
      newErrors.phone = 'Phone number is required';
    }
    
    // Validate required activity fields
    allFields.forEach(field => {
      if (field.isRequired && !formData[field.key]) {
        newErrors[field.key] = `${field.label} is required`;
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      await onSubmit(formData as BookingFormData);
    } catch (error) {
      console.error('Booking submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Render field based on type
  const renderField = (field: WebsiteBookingField & { isRequired: boolean }) => {
    const fieldId = `field-${field.key}`;
    const hasError = !!errors[field.key];
    
    const baseClasses = `w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
      hasError ? 'border-red-500' : 'border-gray-300'
    }`;
    
    switch (field.type) {
      case 'text':
      case 'email':
      case 'tel':
        return (
          <div key={field.key} className="mb-4">
            <label htmlFor={fieldId} className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
              {field.isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            <input
              type={field.type}
              id={fieldId}
              value={formData[field.key] || ''}
              onChange={(e) => handleFieldChange(field.key, e.target.value)}
              placeholder={field.placeholder}
              className={baseClasses}
            />
            {field.help_text && (
              <p className="text-xs text-gray-500 mt-1">{field.help_text}</p>
            )}
            {hasError && (
              <p className="text-xs text-red-500 mt-1">{errors[field.key]}</p>
            )}
          </div>
        );
      
      case 'textarea':
        return (
          <div key={field.key} className="mb-4">
            <label htmlFor={fieldId} className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
              {field.isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            <textarea
              id={fieldId}
              value={formData[field.key] || ''}
              onChange={(e) => handleFieldChange(field.key, e.target.value)}
              placeholder={field.placeholder}
              rows={4}
              className={baseClasses}
            />
            {field.help_text && (
              <p className="text-xs text-gray-500 mt-1">{field.help_text}</p>
            )}
            {hasError && (
              <p className="text-xs text-red-500 mt-1">{errors[field.key]}</p>
            )}
          </div>
        );
      
      case 'select':
        return (
          <div key={field.key} className="mb-4">
            <label htmlFor={fieldId} className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
              {field.isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            <select
              id={fieldId}
              value={formData[field.key] || ''}
              onChange={(e) => handleFieldChange(field.key, e.target.value)}
              className={baseClasses}
            >
              <option value="">Select an option</option>
              {field.options?.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            {field.help_text && (
              <p className="text-xs text-gray-500 mt-1">{field.help_text}</p>
            )}
            {hasError && (
              <p className="text-xs text-red-500 mt-1">{errors[field.key]}</p>
            )}
          </div>
        );
      
      case 'radio':
        return (
          <div key={field.key} className="mb-4">
            <fieldset>
              <legend className="block text-sm font-medium text-gray-700 mb-2">
                {field.label}
                {field.isRequired && <span className="text-red-500 ml-1">*</span>}
              </legend>
              <div className="space-y-2">
                {field.options?.map((option) => (
                  <label key={option} className="flex items-center">
                    <input
                      type="radio"
                      name={field.key}
                      value={option}
                      checked={formData[field.key] === option}
                      onChange={(e) => handleFieldChange(field.key, e.target.value)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">{option}</span>
                  </label>
                ))}
              </div>
            </fieldset>
            {field.help_text && (
              <p className="text-xs text-gray-500 mt-1">{field.help_text}</p>
            )}
            {hasError && (
              <p className="text-xs text-red-500 mt-1">{errors[field.key]}</p>
            )}
          </div>
        );
      
      case 'checkbox':
        return (
          <div key={field.key} className="mb-4">
            <div className="flex items-start">
              <input
                type="checkbox"
                id={fieldId}
                checked={formData[field.key] || false}
                onChange={(e) => handleFieldChange(field.key, e.target.checked)}
                className="mt-1 mr-2"
              />
              <label htmlFor={fieldId} className="text-sm text-gray-700">
                {field.label}
                {field.isRequired && <span className="text-red-500 ml-1">*</span>}
              </label>
            </div>
            {field.help_text && (
              <p className="text-xs text-gray-500 mt-1 ml-6">{field.help_text}</p>
            )}
            {hasError && (
              <p className="text-xs text-red-500 mt-1 ml-6">{errors[field.key]}</p>
            )}
          </div>
        );
      
      case 'date':
        return (
          <div key={field.key} className="mb-4">
            <label htmlFor={fieldId} className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
              {field.isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            <input
              type="date"
              id={fieldId}
              value={formData[field.key] || ''}
              onChange={(e) => handleFieldChange(field.key, e.target.value)}
              className={baseClasses}
            />
            {field.help_text && (
              <p className="text-xs text-gray-500 mt-1">{field.help_text}</p>
            )}
            {hasError && (
              <p className="text-xs text-red-500 mt-1">{errors[field.key]}</p>
            )}
          </div>
        );
      
      case 'number':
        return (
          <div key={field.key} className="mb-4">
            <label htmlFor={fieldId} className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
              {field.isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            <input
              type="number"
              id={fieldId}
              value={formData[field.key] || ''}
              onChange={(e) => handleFieldChange(field.key, e.target.value)}
              placeholder={field.placeholder}
              className={baseClasses}
            />
            {field.help_text && (
              <p className="text-xs text-gray-500 mt-1">{field.help_text}</p>
            )}
            {hasError && (
              <p className="text-xs text-red-500 mt-1">{errors[field.key]}</p>
            )}
          </div>
        );
      
      default:
        return (
          <div key={field.key} className="mb-4">
            <label htmlFor={fieldId} className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
              {field.isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            <input
              type="text"
              id={fieldId}
              value={formData[field.key] || ''}
              onChange={(e) => handleFieldChange(field.key, e.target.value)}
              placeholder={field.placeholder}
              className={baseClasses}
            />
            {field.help_text && (
              <p className="text-xs text-gray-500 mt-1">{field.help_text}</p>
            )}
            {hasError && (
              <p className="text-xs text-red-500 mt-1">{errors[field.key]}</p>
            )}
          </div>
        );
    }
  };
  
  return (
    <div className={`booking-form ${className}`}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Customer Information */}
        <div className="customer-info">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h3>
          
          <div className="mb-4">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Full Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => handleFieldChange('name', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter your full name"
            />
            {errors.name && (
              <p className="text-xs text-red-500 mt-1">{errors.name}</p>
            )}
          </div>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email Address <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                id="email"
                value={formData.email}
                onChange={(e) => handleFieldChange('email', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="your@email.com"
              />
              {errors.email && (
                <p className="text-xs text-red-500 mt-1">{errors.email}</p>
              )}
            </div>
            
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number <span className="text-red-500">*</span>
              </label>
              <input
                type="tel"
                id="phone"
                value={formData.phone}
                onChange={(e) => handleFieldChange('phone', e.target.value)}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.phone ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="(555) 123-4567"
              />
              {errors.phone && (
                <p className="text-xs text-red-500 mt-1">{errors.phone}</p>
              )}
            </div>
          </div>
        </div>
        
        {/* Service-Specific Fields */}
        {allFields.length > 0 && (
          <div className="service-details">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Service Details</h3>
            {allFields.map(renderField)}
          </div>
        )}
        
        {/* Submit Button */}
        <div className="submit-section pt-4">
          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full py-3 px-6 rounded-md font-semibold text-white transition-colors ${
              isSubmitting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isSubmitting ? 'Submitting...' : 'Request Service'}
          </button>
          
          <p className="text-xs text-gray-500 text-center mt-2">
            By submitting this form, you agree to be contacted about your service request.
          </p>
        </div>
      </form>
    </div>
  );
}