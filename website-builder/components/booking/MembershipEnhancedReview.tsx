/**
 * Membership Enhanced Review Component
 * 
 * Enhanced booking review that shows membership benefits and pricing
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { 
  Star, 
  Shield, 
  Clock, 
  MapPin, 
  Calendar, 
  User, 
  Phone,
  Mail,
  FileText,
  Crown,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { useBookingWizard } from './BookingWizardContext';
import { MembershipPlan, ServicePricing } from '../../lib/types/membership';

interface MembershipEnhancedReviewProps {
  businessId: string;
  businessName?: string;
  businessPhone?: string;
  businessEmail?: string;
  membershipPlans?: MembershipPlan[];
  servicePricing?: ServicePricing[];
  customerMembershipType?: 'residential' | 'commercial' | 'premium' | null;
}

export default function MembershipEnhancedReview({
  businessId,
  businessName = 'Professional Services',
  businessPhone,
  businessEmail,
  membershipPlans = [],
  servicePricing = [],
  customerMembershipType = null
}: MembershipEnhancedReviewProps) {
  const { state, nextStep, setLoading, setError, updateFlags } = useBookingWizard();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showMembershipOffer, setShowMembershipOffer] = useState(false);

  // Find selected service pricing
  const selectedServicePricing = servicePricing.find(
    service => service.id === state.serviceId
  );

  // Calculate pricing based on membership
  const getServicePrice = () => {
    if (!selectedServicePricing) return null;
    
    const basePrice = selectedServicePricing.base_price;
    let memberPrice = basePrice;
    
    if (customerMembershipType) {
      switch (customerMembershipType) {
        case 'residential':
          memberPrice = selectedServicePricing.residential_member_price || basePrice;
          break;
        case 'commercial':
          memberPrice = selectedServicePricing.commercial_member_price || basePrice;
          break;
        case 'premium':
          memberPrice = selectedServicePricing.premium_member_price || basePrice;
          break;
      }
    }
    
    return {
      base: basePrice,
      member: memberPrice,
      savings: basePrice - memberPrice,
      hasSavings: memberPrice < basePrice
    };
  };

  // Get member benefits for current membership
  const getMemberBenefits = () => {
    if (!customerMembershipType) return [];
    
    const plan = membershipPlans.find(p => p.type === customerMembershipType);
    return plan?.benefits.filter(b => b.is_highlighted).slice(0, 3) || [];
  };

  // Format service details
  const formatServiceDetails = () => {
    if (!state.serviceId || !state.categoryId) return 'Service consultation';
    
    // Try to get service name from booking context or use fallback
    return selectedServicePricing?.service_name || 'Professional Service';
  };

  const pricing = getServicePrice();
  const memberBenefits = getMemberBenefits();

  const handleConfirmBooking = async () => {
    if (!state.termsAccepted) {
      setError('Please accept the terms and conditions to proceed');
      return;
    }

    setIsSubmitting(true);
    setLoading(true);
    setError(undefined);

    try {
      // Include membership information in booking request
      const bookingRequest = {
        business_id: businessId,
        service_id: state.serviceId!,
        customer_contact: {
          first_name: state.contact?.firstName || '',
          last_name: state.contact?.lastName || '',
          phone_e164: state.contact?.phoneE164 || '',
          email: state.contact?.email || '',
          sms_consent: state.contact?.smsConsent || false
        },
        service_address: {
          line1: state.address?.line1 || '',
          line2: state.address?.line2,
          city: state.address?.city || '',
          region: state.address?.region || '',
          postal_code: state.address?.postalCode || '',
          country_code: state.address?.countryCode || 'US'
        },
        scheduled_at: state.slot?.start || new Date().toISOString(),
        timezone: state.zipInfo?.timezone || 'America/New_York',
        problem_description: state.details?.notes || '',
        urgency_level: 'normal',
        // Membership specific fields
        customer_membership_type: customerMembershipType,
        member_pricing_applied: pricing?.hasSavings || false,
        quoted_price: pricing?.member || pricing?.base || 0,
        dispatch_fee_accepted: state.dispatchFeeAccepted || false,
        terms_accepted: state.termsAccepted,
        source: 'booking_widget_enhanced'
      };

      // Simulate API call (replace with actual API integration)
      console.log('Booking request:', bookingRequest);
      
      // Simulate success
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      nextStep();
    } catch (error) {
      console.error('Booking error:', error);
      setError('Failed to create booking. Please try again or call us directly.');
    } finally {
      setIsSubmitting(false);
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Booking Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-600" />
            Booking Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Service Information */}
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold text-gray-900">
                {formatServiceDetails()}
              </h3>
              <p className="text-sm text-gray-600">
                {selectedServicePricing?.description || 'Professional service consultation'}
              </p>
            </div>
            {customerMembershipType && (
              <Badge className="bg-blue-100 text-blue-800">
                <Star className="h-3 w-3 mr-1" />
                Member
              </Badge>
            )}
          </div>

          <div className="border-t my-4" />

          {/* Location */}
          <div className="flex items-start gap-3">
            <MapPin className="h-4 w-4 text-gray-500 mt-0.5" />
            <div>
              <p className="text-sm font-medium">Service Location</p>
              <p className="text-sm text-gray-600">
                {state.address?.line1}
                {state.address?.line2 && `, ${state.address?.line2}`}
                <br />
                {state.address?.city}, {state.address?.region} {state.address?.postalCode}
              </p>
            </div>
          </div>

          {/* Date & Time */}
          <div className="flex items-start gap-3">
            <Calendar className="h-4 w-4 text-gray-500 mt-0.5" />
            <div>
              <p className="text-sm font-medium">Scheduled Time</p>
              <p className="text-sm text-gray-600">
                {state.slot?.start ? new Date(state.slot.start).toLocaleString() : 'To be scheduled'}
              </p>
            </div>
          </div>

          {/* Contact */}
          <div className="flex items-start gap-3">
            <User className="h-4 w-4 text-gray-500 mt-0.5" />
            <div>
              <p className="text-sm font-medium">Contact Information</p>
              <p className="text-sm text-gray-600">
                {state.contact?.firstName} {state.contact?.lastName}
                <br />
                <Phone className="h-3 w-3 inline mr-1" />
                {state.contact?.phoneE164}
                <br />
                <Mail className="h-3 w-3 inline mr-1" />
                {state.contact?.email}
              </p>
            </div>
          </div>

          {/* Problem Description */}
          {state.details?.notes && (
            <div className="flex items-start gap-3">
              <FileText className="h-4 w-4 text-gray-500 mt-0.5" />
              <div>
                <p className="text-sm font-medium">Problem Description</p>
                <p className="text-sm text-gray-600">
                  {state.details.notes}
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pricing Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-green-600" />
            Pricing Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          {pricing ? (
            <div className="space-y-3">
              {pricing.hasSavings ? (
                <>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Regular Price:</span>
                    <span className="text-gray-500 line-through">
                      ${pricing.base.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-blue-600">Member Price:</span>
                    <span className="font-bold text-blue-600 text-lg">
                      ${pricing.member.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-green-600">Your Savings:</span>
                    <span className="font-semibold text-green-600">
                      ${pricing.savings.toLocaleString()}
                    </span>
                  </div>
                </>
              ) : (
                <div className="flex justify-between items-center">
                  <span className="font-semibold">Service Price:</span>
                  <span className="font-bold text-lg">
                    {pricing.base === 0 ? 'FREE' : `$${pricing.base.toLocaleString()}`}
                  </span>
                </div>
              )}
              
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mt-4">
                <p className="text-xs text-yellow-700">
                  <AlertCircle className="h-3 w-3 inline mr-1" />
                  Final pricing may vary based on actual service requirements. 
                  This is an estimate for planning purposes.
                </p>
              </div>
            </div>
          ) : (
            <p className="text-gray-600">Pricing will be provided during consultation</p>
          )}
        </CardContent>
      </Card>

      {/* Member Benefits (if applicable) */}
      {customerMembershipType && memberBenefits.length > 0 && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-800">
              <Crown className="h-5 w-5" />
              Your Member Benefits
            </CardTitle>
            <CardDescription className="text-blue-700">
              As a {customerMembershipType} member, you enjoy these exclusive benefits:
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {memberBenefits.map((benefit) => (
                <div key={benefit.id} className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-blue-600" />
                  <span className="text-sm text-blue-800">
                    {benefit.title}
                    {benefit.value && (
                      <Badge variant="outline" className="ml-2 text-xs border-blue-300">
                        {benefit.value}
                      </Badge>
                    )}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Membership Offer for Non-Members */}
      {!customerMembershipType && membershipPlans.length > 0 && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-800">
              <Star className="h-5 w-5" />
              Save with Membership
            </CardTitle>
            <CardDescription className="text-green-700">
              Join our membership program and save on this service and future visits!
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <p className="text-sm text-green-800">
                With our Residential Membership, you could save ${pricing?.base ? Math.round(pricing.base * 0.15) : 50} on this service alone!
              </p>
              <Button
                size="sm"
                variant="outline"
                className="border-green-300 text-green-700 hover:bg-green-100"
                onClick={() => setShowMembershipOffer(true)}
              >
                Learn More About Membership
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Terms and Conditions */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-start space-x-3">
            <input
              type="checkbox"
              id="terms"
              checked={state.termsAccepted}
              onChange={(e) => updateFlags({ termsAccepted: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-0.5"
            />
            <label htmlFor="terms" className="text-sm text-gray-600 leading-relaxed">
              I accept the{' '}
              <a href="/terms" className="text-blue-600 hover:underline" target="_blank">
                terms of service
              </a>{' '}
              and{' '}
              <a href="/privacy" className="text-blue-600 hover:underline" target="_blank">
                privacy policy
              </a>
              . I understand that final pricing may vary based on actual service requirements.
              {state.contact?.smsConsent && (
                <span>
                  {' '}I consent to receive SMS updates about my appointment.
                </span>
              )}
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex flex-col gap-4">
        <Button
          onClick={handleConfirmBooking}
          disabled={!state.termsAccepted || isSubmitting}
          className="w-full bg-blue-600 hover:bg-blue-700"
          size="lg"
        >
          {isSubmitting ? (
            <Clock className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <CheckCircle className="h-4 w-4 mr-2" />
          )}
          {isSubmitting ? 'Confirming Booking...' : 'Confirm Booking'}
        </Button>
        
        <div className="text-center text-sm text-gray-600">
          <p>Need immediate help?</p>
          <Button variant="link" className="p-0 h-auto font-medium">
            <Phone className="h-4 w-4 mr-1" />
            Call {businessPhone || '(555) 123-4567'}
          </Button>
        </div>
      </div>
    </div>
  );
}
