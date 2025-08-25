/**
 * Customer Form Component
 * 
 * Collects customer information and service details for booking
 */

'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Checkbox } from '../ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { User, Phone, Mail, MapPin, MessageSquare, FileText, Shield } from 'lucide-react';
import { cn } from '../../lib/utils';

import { CustomerFormProps } from '../../lib/types/booking';

export default function CustomerForm({
  formData,
  onFormDataChange,
  onSubmit,
  isSubmitting = false,
  className
}: CustomerFormProps) {

  const handleInputChange = (field: string, value: string | boolean) => {
    onFormDataChange({ [field]: value });
  };

  const isFormValid = (): boolean => {
    return !!(
      formData.customerName &&
      formData.customerPhone &&
      formData.serviceAddress &&
      (formData.customerEmail || formData.customerPhone) &&
      (!formData.smsConsent || formData.customerPhone) // SMS consent requires phone
    );
  };

  return (
    <div className={cn("space-y-6", className)}>
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Your Information</h3>
        <p className="text-gray-600">Please provide your contact information and service details.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Contact Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              Contact Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Full Name */}
            <div>
              <label htmlFor="customerName" className="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <Input
                id="customerName"
                type="text"
                placeholder="Enter your full name"
                value={formData.customerName || ''}
                onChange={(e) => handleInputChange('customerName', e.target.value)}
                required
              />
            </div>

            {/* Phone Number */}
            <div>
              <label htmlFor="customerPhone" className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number *
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  id="customerPhone"
                  type="tel"
                  placeholder="(555) 123-4567"
                  value={formData.customerPhone || ''}
                  onChange={(e) => handleInputChange('customerPhone', e.target.value)}
                  className="pl-10"
                  required
                />
              </div>
            </div>

            {/* Email Address */}
            <div>
              <label htmlFor="customerEmail" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  id="customerEmail"
                  type="email"
                  placeholder="your.email@example.com"
                  value={formData.customerEmail || ''}
                  onChange={(e) => handleInputChange('customerEmail', e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Preferred Contact Method */}
            <div>
              <label htmlFor="preferredContactMethod" className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Contact Method
              </label>
              <Select
                value={formData.preferredContactMethod || 'phone'}
                onValueChange={(value) => handleInputChange('preferredContactMethod', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select contact method" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="phone">Phone Call</SelectItem>
                  <SelectItem value="sms">Text Message</SelectItem>
                  <SelectItem value="email">Email</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Service Address */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              Service Address
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Street Address */}
            <div>
              <label htmlFor="serviceAddress" className="block text-sm font-medium text-gray-700 mb-2">
                Street Address *
              </label>
              <Input
                id="serviceAddress"
                type="text"
                placeholder="123 Main Street"
                value={formData.serviceAddress || ''}
                onChange={(e) => handleInputChange('serviceAddress', e.target.value)}
                required
              />
            </div>

            {/* City */}
            <div>
              <label htmlFor="serviceCity" className="block text-sm font-medium text-gray-700 mb-2">
                City
              </label>
              <Input
                id="serviceCity"
                type="text"
                placeholder="City"
                value={formData.serviceCity || ''}
                onChange={(e) => handleInputChange('serviceCity', e.target.value)}
              />
            </div>

            {/* State & ZIP */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="serviceState" className="block text-sm font-medium text-gray-700 mb-2">
                  State
                </label>
                <Input
                  id="serviceState"
                  type="text"
                  placeholder="TX"
                  value={formData.serviceState || ''}
                  onChange={(e) => handleInputChange('serviceState', e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="serviceZip" className="block text-sm font-medium text-gray-700 mb-2">
                  ZIP Code
                </label>
                <Input
                  id="serviceZip"
                  type="text"
                  placeholder="12345"
                  value={formData.serviceZip || ''}
                  onChange={(e) => handleInputChange('serviceZip', e.target.value)}
                />
              </div>
            </div>

            {/* Access Instructions */}
            <div>
              <label htmlFor="accessInstructions" className="block text-sm font-medium text-gray-700 mb-2">
                Access Instructions
              </label>
              <Textarea
                id="accessInstructions"
                placeholder="Gate codes, key location, parking instructions, etc."
                value={formData.accessInstructions || ''}
                onChange={(e) => handleInputChange('accessInstructions', e.target.value)}
                rows={3}
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Service Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Service Details
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Problem Description */}
          <div>
            <label htmlFor="problemDescription" className="block text-sm font-medium text-gray-700 mb-2">
              Describe the Issue or Service Needed
            </label>
            <Textarea
              id="problemDescription"
              placeholder="Please describe what you need help with, any symptoms you've noticed, or specific work you'd like done..."
              value={formData.problemDescription || ''}
              onChange={(e) => handleInputChange('problemDescription', e.target.value)}
              rows={4}
            />
          </div>

          {/* Special Instructions */}
          <div>
            <label htmlFor="specialInstructions" className="block text-sm font-medium text-gray-700 mb-2">
              Special Instructions or Requests
            </label>
            <Textarea
              id="specialInstructions"
              placeholder="Any special requirements, preferred technician, timing constraints, etc."
              value={formData.specialInstructions || ''}
              onChange={(e) => handleInputChange('specialInstructions', e.target.value)}
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Communication Preferences & Consent */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-800">
            <Shield className="w-5 h-5" />
            Communication Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Email Consent */}
          <div className="flex items-start space-x-3">
            <Checkbox
              id="emailConsent"
              checked={formData.emailConsent || false}
              onCheckedChange={(checked) => handleInputChange('emailConsent', checked as boolean)}
            />
            <div className="grid gap-1.5 leading-none">
              <label
                htmlFor="emailConsent"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Email Communications
              </label>
              <p className="text-xs text-gray-600">
                Receive appointment confirmations, reminders, and service updates via email.
              </p>
            </div>
          </div>

          {/* SMS Consent */}
          <div className="flex items-start space-x-3">
            <Checkbox
              id="smsConsent"
              checked={formData.smsConsent || false}
              onCheckedChange={(checked) => handleInputChange('smsConsent', checked as boolean)}
            />
            <div className="grid gap-1.5 leading-none">
              <label
                htmlFor="smsConsent"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                SMS Text Messages
              </label>
              <p className="text-xs text-gray-600">
                I consent to receive SMS messages for appointment reminders and service updates. 
                Message and data rates may apply. Reply STOP to opt out.
                {!formData.customerPhone && (
                  <span className="text-red-600 block mt-1">
                    Phone number required for SMS consent.
                  </span>
                )}
              </p>
            </div>
          </div>

          {/* Privacy Notice */}
          <div className="mt-4 p-3 bg-white border border-blue-200 rounded text-xs text-gray-600">
            <p className="font-medium mb-1">Privacy Notice:</p>
            <p>
              Your information is used solely for providing services and communication. 
              We never share your personal information with third parties. 
              You can update your preferences or unsubscribe at any time.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Submit Button */}
      <div className="flex justify-center pt-4">
        <Button
          onClick={onSubmit}
          disabled={!isFormValid() || isSubmitting}
          size="lg"
          className="w-full sm:w-auto px-8"
        >
          {isSubmitting ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
              Creating Your Booking...
            </>
          ) : (
            <>
              <MessageSquare className="w-5 h-5 mr-2" />
              Book My Appointment
            </>
          )}
        </Button>
      </div>

      {/* Form Validation Messages */}
      {!isFormValid() && (
        <div className="text-center text-sm text-gray-600">
          <p>Please fill in all required fields (*) to continue.</p>
        </div>
      )}
    </div>
  );
}
