/**
 * Contact Step (Step 4)
 * 
 * Collects customer contact information with SMS consent
 */

'use client';

import React, { useState } from 'react';
import { User, Phone, Mail, MessageSquare, Shield, CheckCircle } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useBookingWizard, Contact } from '../Hero365BookingContext';

interface ContactStepProps {
  businessId: string;
  businessName?: string;
}

export default function ContactStep({ 
  businessId, 
  businessName = 'our team' 
}: ContactStepProps) {
  const { state, updateContact, nextStep, setError } = useBookingWizard();
  
  const [formData, setFormData] = useState<Partial<Contact>>({
    firstName: state.contact?.firstName || '',
    lastName: state.contact?.lastName || '',
    phoneE164: state.contact?.phoneE164 || '',
    email: state.contact?.email || '',
    smsConsent: state.contact?.smsConsent || false,
    marketingConsent: state.contact?.marketingConsent || false
  });

  const [phoneFormatted, setPhoneFormatted] = useState('');
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const handleInputChange = (field: keyof Contact, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: '' }));
    }
    
    setError();
  };

  const formatPhoneNumber = (value: string) => {
    // Remove all non-digits
    const digits = value.replace(/\D/g, '');
    
    // Format as (XXX) XXX-XXXX
    if (digits.length <= 3) {
      return digits;
    } else if (digits.length <= 6) {
      return `(${digits.slice(0, 3)}) ${digits.slice(3)}`;
    } else {
      return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6, 10)}`;
    }
  };

  const handlePhoneChange = (value: string) => {
    const formatted = formatPhoneNumber(value);
    setPhoneFormatted(formatted);
    
    // Convert to E.164 format for storage
    const digits = value.replace(/\D/g, '');
    if (digits.length === 10) {
      handleInputChange('phoneE164', `+1${digits}`);
    } else if (digits.length === 11 && digits.startsWith('1')) {
      handleInputChange('phoneE164', `+${digits}`);
    } else {
      handleInputChange('phoneE164', '');
    }
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};

    // First name validation
    if (!formData.firstName?.trim()) {
      errors.firstName = 'First name is required';
    }

    // Last name validation
    if (!formData.lastName?.trim()) {
      errors.lastName = 'Last name is required';
    }

    // Phone validation
    if (!formData.phoneE164) {
      errors.phoneE164 = 'Phone number is required';
    } else if (!formData.phoneE164.match(/^\+1\d{10}$/)) {
      errors.phoneE164 = 'Please enter a valid US phone number';
    }

    // Email validation
    if (!formData.email?.trim()) {
      errors.email = 'Email address is required';
    } else if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      errors.email = 'Please enter a valid email address';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleContinue = () => {
    if (validateForm()) {
      const contact: Contact = {
        firstName: formData.firstName!,
        lastName: formData.lastName!,
        phoneE164: formData.phoneE164!,
        email: formData.email!,
        smsConsent: formData.smsConsent!,
        marketingConsent: formData.marketingConsent
      };

      updateContact(contact);
      nextStep();
    }
  };

  const isFormValid = formData.firstName?.trim() && 
                     formData.lastName?.trim() && 
                     formData.phoneE164 && 
                     formData.email?.trim();

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <User className="w-8 h-8 text-blue-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          How can we reach you?
        </h1>
        <p className="text-gray-600">
          We'll use this information to confirm your appointment and send updates
        </p>
      </div>

      {/* Contact Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <User className="w-5 h-5" />
            <span>Contact Information</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Name Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                First Name *
              </label>
              <Input
                value={formData.firstName || ''}
                onChange={(e) => handleInputChange('firstName', e.target.value)}
                placeholder="John"
                className={validationErrors.firstName ? 'border-red-500' : ''}
              />
              {validationErrors.firstName && (
                <p className="text-sm text-red-600 mt-1">{validationErrors.firstName}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Last Name *
              </label>
              <Input
                value={formData.lastName || ''}
                onChange={(e) => handleInputChange('lastName', e.target.value)}
                placeholder="Doe"
                className={validationErrors.lastName ? 'border-red-500' : ''}
              />
              {validationErrors.lastName && (
                <p className="text-sm text-red-600 mt-1">{validationErrors.lastName}</p>
              )}
            </div>
          </div>

          {/* Phone Number */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number *
            </label>
            <div className="relative">
              <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                value={phoneFormatted}
                onChange={(e) => handlePhoneChange(e.target.value)}
                placeholder="(555) 123-4567"
                className={`pl-10 ${validationErrors.phoneE164 ? 'border-red-500' : ''}`}
                maxLength={14}
              />
            </div>
            {validationErrors.phoneE164 && (
              <p className="text-sm text-red-600 mt-1">{validationErrors.phoneE164}</p>
            )}
            <p className="text-xs text-gray-500 mt-1">
              We'll use this to confirm your appointment and provide updates
            </p>
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address *
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                type="email"
                value={formData.email || ''}
                onChange={(e) => handleInputChange('email', e.target.value)}
                placeholder="john.doe@example.com"
                className={`pl-10 ${validationErrors.email ? 'border-red-500' : ''}`}
              />
            </div>
            {validationErrors.email && (
              <p className="text-sm text-red-600 mt-1">{validationErrors.email}</p>
            )}
            <p className="text-xs text-gray-500 mt-1">
              For appointment confirmations and service receipts
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Communication Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="w-5 h-5" />
            <span>Communication Preferences</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* SMS Consent */}
          <div className="flex items-start space-x-3">
            <Checkbox
              id="sms-consent"
              checked={formData.smsConsent}
              onCheckedChange={(checked) => handleInputChange('smsConsent', checked as boolean)}
              className="mt-1"
            />
            <div className="flex-1">
              <label htmlFor="sms-consent" className="text-sm font-medium text-gray-900 cursor-pointer">
                Send me text message updates about my appointment
              </label>
              <p className="text-xs text-gray-500 mt-1">
                Get real-time updates about your technician's arrival time and service status. 
                Standard message rates may apply. You can opt out anytime.
              </p>
            </div>
          </div>

          {/* Marketing Consent */}
          <div className="flex items-start space-x-3">
            <Checkbox
              id="marketing-consent"
              checked={formData.marketingConsent}
              onCheckedChange={(checked) => handleInputChange('marketingConsent', checked as boolean)}
              className="mt-1"
            />
            <div className="flex-1">
              <label htmlFor="marketing-consent" className="text-sm font-medium text-gray-900 cursor-pointer">
                Send me promotional offers and maintenance reminders
              </label>
              <p className="text-xs text-gray-500 mt-1">
                Receive seasonal maintenance tips, special offers, and service reminders from {businessName}. 
                You can unsubscribe anytime.
              </p>
            </div>
          </div>

          {/* Privacy Notice */}
          <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
            <div className="flex items-start space-x-2">
              <Shield className="w-4 h-4 text-gray-500 mt-0.5" />
              <div>
                <p className="text-xs text-gray-600">
                  <strong>Privacy Notice:</strong> Your information is secure and will only be used to provide 
                  service and communicate about your appointment. We never sell or share your data with third parties.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Appointment Summary */}
      {state.zipInfo && state.slot && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-start space-x-3">
              <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-blue-900 mb-1">
                  Appointment Summary
                </p>
                <div className="text-xs text-blue-700 space-y-1">
                  <p>📍 {state.address?.line1}, {state.address?.city}, {state.address?.region}</p>
                  <p>📅 {new Date(state.slot.start).toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}</p>
                  <p>🕐 {new Date(state.slot.start).toLocaleTimeString('en-US', { 
                    hour: 'numeric', 
                    minute: '2-digit',
                    hour12: true 
                  })} - {new Date(state.slot.end).toLocaleTimeString('en-US', { 
                    hour: 'numeric', 
                    minute: '2-digit',
                    hour12: true 
                  })}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          onClick={handleContinue}
          disabled={!isFormValid}
          size="lg"
          className="px-8"
        >
          Continue to Details
        </Button>
      </div>

      {/* Help Text */}
      <div className="text-center">
        <p className="text-sm text-gray-500">
          All fields marked with * are required to complete your booking
        </p>
      </div>
    </div>
  );
}
