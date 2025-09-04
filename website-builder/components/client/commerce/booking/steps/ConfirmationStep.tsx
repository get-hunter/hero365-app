/**
 * Confirmation Step (Step 7)
 * 
 * Shows booking confirmation and next steps
 */

'use client';

import React, { useEffect, useState } from 'react';
import { 
  CheckCircle, Calendar, MapPin, Clock, Phone, Mail, 
  Download, Share, MessageSquare, Star, Home 
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useBookingWizard } from '../Hero365BookingContext';

interface ConfirmationStepProps {
  businessId: string;
  businessName?: string;
  businessPhone?: string;
  businessEmail?: string;
  onClose?: () => void;
}

export default function ConfirmationStep({ 
  businessId,
  businessName = 'Professional Services',
  businessPhone,
  businessEmail,
  onClose
}: ConfirmationStepProps) {
  const { state, resetWizard } = useBookingWizard();
  
  const [bookingId] = useState(() => 
    'BK-' + Math.random().toString(36).substr(2, 9).toUpperCase()
  );
  const [showCalendarOptions, setShowCalendarOptions] = useState(false);

  // Auto-close after successful booking (optional)
  useEffect(() => {
    const timer = setTimeout(() => {
      // Could auto-close here if desired
    }, 30000); // 30 seconds

    return () => clearTimeout(timer);
  }, []);

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const generateCalendarEvent = () => {
    if (!state.slot) return '';

    const startDate = new Date(state.slot.start);
    const endDate = new Date(state.slot.end);
    
    const formatCalendarDate = (date: Date) => {
      return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    };

    const title = encodeURIComponent(`${businessName} Service Appointment`);
    const details = encodeURIComponent(
      `Service: ${state.categoryId}\n` +
      `Address: ${state.address?.line1}, ${state.address?.city}, ${state.address?.region}\n` +
      `Booking ID: ${bookingId}\n` +
      `Contact: ${businessPhone || businessEmail || ''}`
    );
    const location = encodeURIComponent(
      `${state.address?.line1}, ${state.address?.city}, ${state.address?.region} ${state.address?.postalCode}`
    );

    const googleCalendarUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${formatCalendarDate(startDate)}/${formatCalendarDate(endDate)}&details=${details}&location=${location}`;
    
    return googleCalendarUrl;
  };

  const handleAddToCalendar = () => {
    const calendarUrl = generateCalendarEvent();
    window.open(calendarUrl, '_blank');
  };

  const handleShare = async () => {
    const shareData = {
      title: `${businessName} Service Appointment`,
      text: `I have a service appointment scheduled for ${formatDate(state.slot?.start || '')} at ${formatTime(state.slot?.start || '')}`,
      url: window.location.href
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
      } catch (err) {
        console.log('Error sharing:', err);
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(
        `${shareData.title}\n${shareData.text}\nBooking ID: ${bookingId}`
      );
      alert('Booking details copied to clipboard!');
    }
  };

  const handleNewBooking = () => {
    resetWizard();
  };

  const handleClose = () => {
    resetWizard();
    onClose?.();
  };

  const getResponseTime = () => {
    if (!state.zipInfo) return 'within 24 hours';
    return `${state.zipInfo.minResponseTimeHours}-${state.zipInfo.maxResponseTimeHours} hours`;
  };

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      {/* Success Header */}
      <div className="text-center">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-12 h-12 text-green-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Booking Confirmed!
        </h1>
        <p className="text-lg text-gray-600 mb-4">
          Your service appointment has been scheduled
        </p>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 inline-block">
          <p className="text-sm font-medium text-green-900">
            Booking ID: <span className="font-mono">{bookingId}</span>
          </p>
        </div>
      </div>

      {/* Appointment Details */}
      <Card className="border-green-200">
        <CardHeader className="bg-green-50">
          <CardTitle className="flex items-center space-x-2 text-green-900">
            <Calendar className="w-5 h-5" />
            <span>Your Appointment</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 space-y-4">
          {/* Date & Time */}
          {state.slot && (
            <div className="flex items-start space-x-3">
              <Clock className="w-5 h-5 text-gray-500 mt-0.5" />
              <div>
                <p className="font-semibold text-gray-900 text-lg">
                  {formatDate(state.slot.start)}
                </p>
                <p className="text-gray-600">
                  {formatTime(state.slot.start)} - {formatTime(state.slot.end)}
                </p>
                <Badge variant="outline" className="mt-1">
                  {state.slot.timezone}
                </Badge>
              </div>
            </div>
          )}

          {/* Location */}
          {state.address && (
            <div className="flex items-start space-x-3">
              <MapPin className="w-5 h-5 text-gray-500 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">
                  {state.address.line1}
                  {state.address.line2 && `, ${state.address.line2}`}
                </p>
                <p className="text-gray-600">
                  {state.address.city}, {state.address.region} {state.address.postalCode}
                </p>
              </div>
            </div>
          )}

          {/* Service */}
          <div className="flex items-start space-x-3">
            <Star className="w-5 h-5 text-gray-500 mt-0.5" />
            <div>
              <p className="font-medium text-gray-900">Service Type</p>
              <p className="text-gray-600">{state.categoryId}</p>
              {state.details?.urgencyLevel && state.details.urgencyLevel !== 'normal' && (
                <Badge variant="outline" className="mt-1 capitalize">
                  {state.details.urgencyLevel} Priority
                </Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* What Happens Next */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="w-5 h-5" />
            <span>What Happens Next</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold text-blue-600">1</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Confirmation Email</p>
                <p className="text-sm text-gray-600">
                  We've sent confirmation details to {state.contact?.email}
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold text-blue-600">2</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Technician Assignment</p>
                <p className="text-sm text-gray-600">
                  A qualified technician will be assigned {getResponseTime()}
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold text-blue-600">3</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Pre-Arrival Contact</p>
                <p className="text-sm text-gray-600">
                  {state.contact?.smsConsent 
                    ? 'You\'ll receive SMS updates and a call 30 minutes before arrival'
                    : 'You\'ll receive a call 30 minutes before arrival'
                  }
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold text-blue-600">4</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Service Completion</p>
                <p className="text-sm text-gray-600">
                  After service, you'll receive a detailed report and invoice
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contact Information */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="p-4">
          <div className="text-center">
            <p className="text-sm font-medium text-blue-900 mb-2">
              Need to make changes or have questions?
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-4 text-sm text-blue-700">
              {businessPhone && (
                <div className="flex items-center space-x-1">
                  <Phone className="w-4 h-4" />
                  <span>{businessPhone}</span>
                </div>
              )}
              {businessEmail && (
                <div className="flex items-center space-x-1">
                  <Mail className="w-4 h-4" />
                  <span>{businessEmail}</span>
                </div>
              )}
            </div>
            <p className="text-xs text-blue-600 mt-2">
              Reference Booking ID: {bookingId}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 pt-4">
        <Button
          onClick={handleAddToCalendar}
          variant="outline"
          className="flex-1"
        >
          <Calendar className="w-4 h-4 mr-2" />
          Add to Calendar
        </Button>
        
        <Button
          onClick={handleShare}
          variant="outline"
          className="flex-1"
        >
          <Share className="w-4 h-4 mr-2" />
          Share Details
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <Button
          onClick={handleNewBooking}
          variant="outline"
          className="flex-1"
        >
          Book Another Service
        </Button>
        
        <Button
          onClick={handleClose}
          className="flex-1"
        >
          <Home className="w-4 h-4 mr-2" />
          Back to Website
        </Button>
      </div>

      {/* Footer */}
      <div className="text-center pt-6 border-t">
        <p className="text-sm text-gray-500">
          Thank you for choosing {businessName}!
        </p>
        <p className="text-xs text-gray-400 mt-1">
          We look forward to serving you.
        </p>
      </div>
    </div>
  );
}
