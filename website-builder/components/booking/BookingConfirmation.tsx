/**
 * Booking Confirmation Component
 * 
 * Displays booking confirmation details and next steps
 */

'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { 
  CheckCircle, 
  Calendar, 
  Clock, 
  MapPin, 
  User, 
  Phone, 
  Mail, 
  FileText,
  Download,
  Share2,
  Plus
} from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '../../lib/utils';

import { BookingConfirmationProps } from '../../lib/types/booking';

export default function BookingConfirmation({
  booking,
  onNewBooking,
  className
}: BookingConfirmationProps) {

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'Confirmed';
      case 'pending':
        return 'Pending Confirmation';
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status.charAt(0).toUpperCase() + status.slice(1);
    }
  };

  const formatDateTime = (dateTimeString: string) => {
    const date = new Date(dateTimeString);
    return {
      date: format(date, 'EEEE, MMMM d, yyyy'),
      time: format(date, 'h:mm a'),
    };
  };

  const scheduledDateTime = booking.scheduled_at || booking.requested_at;
  const { date, time } = formatDateTime(scheduledDateTime);

  const handleDownloadConfirmation = () => {
    // Create a simple text confirmation
    const confirmationText = `
BOOKING CONFIRMATION
${booking.booking_number ? `Booking #: ${booking.booking_number}` : ''}

Service: ${booking.service_name}
Date: ${date}
Time: ${time}
Status: ${getStatusText(booking.status)}

Customer: ${booking.customer_name}
Phone: ${booking.customer_phone}
${booking.customer_email ? `Email: ${booking.customer_email}` : ''}

Service Address:
${booking.service_address}
${booking.service_city ? `${booking.service_city}, ` : ''}${booking.service_state || ''} ${booking.service_zip || ''}

${booking.problem_description ? `Service Details:\n${booking.problem_description}` : ''}
${booking.special_instructions ? `\nSpecial Instructions:\n${booking.special_instructions}` : ''}
${booking.access_instructions ? `\nAccess Instructions:\n${booking.access_instructions}` : ''}

Thank you for choosing our services!
    `.trim();

    const blob = new Blob([confirmationText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `booking-confirmation-${booking.booking_number || booking.id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleShareBooking = async () => {
    const shareData = {
      title: 'Service Appointment Confirmation',
      text: `My ${booking.service_name} appointment is scheduled for ${date} at ${time}`,
      url: window.location.href,
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      // Fallback: copy to clipboard
      const shareText = `${shareData.text}\nBooking #: ${booking.booking_number || booking.id}`;
      navigator.clipboard.writeText(shareText).then(() => {
        alert('Booking details copied to clipboard!');
      });
    }
  };

  return (
    <div className={cn("space-y-6", className)}>
      {/* Success Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-green-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Booking {booking.status === 'confirmed' ? 'Confirmed' : 'Submitted'}!
        </h2>
        <p className="text-gray-600">
          {booking.status === 'confirmed' 
            ? "Your appointment has been confirmed. We'll see you soon!"
            : "We've received your booking request and will confirm it within 2 hours."
          }
        </p>
      </div>

      {/* Booking Details */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Appointment Details
            </CardTitle>
            <Badge className={cn("border", getStatusColor(booking.status))}>
              {getStatusText(booking.status)}
            </Badge>
          </div>
          {booking.booking_number && (
            <p className="text-sm text-gray-600">
              Booking #{booking.booking_number}
            </p>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Service & DateTime */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <FileText className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="font-medium">{booking.service_name}</p>
                  <p className="text-sm text-gray-600">
                    Duration: {booking.estimated_duration_minutes} minutes
                  </p>
                  {booking.quoted_price && (
                    <p className="text-sm text-gray-600">
                      Estimated Cost: {new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD',
                      }).format(booking.quoted_price)}
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <Clock className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="font-medium">{date}</p>
                  <p className="text-sm text-gray-600">{time}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Customer Info */}
          <div className="border-t pt-4">
            <h4 className="font-medium mb-3 flex items-center gap-2">
              <User className="w-4 h-4" />
              Customer Information
            </h4>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <User className="w-4 h-4 text-gray-400" />
                  <span>{booking.customer_name}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Phone className="w-4 h-4 text-gray-400" />
                  <span>{booking.customer_phone}</span>
                </div>
                {booking.customer_email && (
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="w-4 h-4 text-gray-400" />
                    <span>{booking.customer_email}</span>
                  </div>
                )}
              </div>
              
              <div className="space-y-2">
                <div className="flex items-start gap-2 text-sm">
                  <MapPin className="w-4 h-4 text-gray-400 mt-0.5" />
                  <div>
                    <p>{booking.service_address}</p>
                    {(booking.service_city || booking.service_state || booking.service_zip) && (
                      <p className="text-gray-600">
                        {booking.service_city && `${booking.service_city}, `}
                        {booking.service_state} {booking.service_zip}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Service Details */}
          {(booking.problem_description || booking.special_instructions || booking.access_instructions) && (
            <div className="border-t pt-4">
              <h4 className="font-medium mb-3">Service Details</h4>
              <div className="space-y-3 text-sm">
                {booking.problem_description && (
                  <div>
                    <p className="font-medium text-gray-700">Issue Description:</p>
                    <p className="text-gray-600">{booking.problem_description}</p>
                  </div>
                )}
                {booking.special_instructions && (
                  <div>
                    <p className="font-medium text-gray-700">Special Instructions:</p>
                    <p className="text-gray-600">{booking.special_instructions}</p>
                  </div>
                )}
                {booking.access_instructions && (
                  <div>
                    <p className="font-medium text-gray-700">Access Instructions:</p>
                    <p className="text-gray-600">{booking.access_instructions}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Next Steps */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-800">What Happens Next?</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm text-blue-700">
            {booking.status === 'pending' ? (
              <>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold">1</span>
                  </div>
                  <p>We'll review your request and confirm your appointment within 2 hours</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold">2</span>
                  </div>
                  <p>You'll receive a confirmation {booking.sms_consent ? 'text message' : 'email'} with appointment details</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold">3</span>
                  </div>
                  <p>We'll send a reminder 24 hours before your appointment</p>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  </div>
                  <p>Your appointment is confirmed and scheduled</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold">1</span>
                  </div>
                  <p>You'll receive a reminder 24 hours before your appointment</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold">2</span>
                  </div>
                  <p>Our technician will arrive at the scheduled time</p>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <Button
          onClick={handleDownloadConfirmation}
          variant="outline"
          className="flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          Download Confirmation
        </Button>
        
        <Button
          onClick={handleShareBooking}
          variant="outline"
          className="flex items-center gap-2"
        >
          <Share2 className="w-4 h-4" />
          Share Booking
        </Button>

        {onNewBooking && (
          <Button
            onClick={onNewBooking}
            className="flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Book Another Service
          </Button>
        )}
      </div>

      {/* Contact Information */}
      <Card className="bg-gray-50">
        <CardContent className="pt-6">
          <div className="text-center">
            <h4 className="font-medium mb-2">Need to make changes?</h4>
            <p className="text-sm text-gray-600 mb-3">
              Contact us if you need to reschedule or have any questions about your appointment.
            </p>
            <div className="flex flex-col sm:flex-row gap-2 justify-center text-sm">
              <span className="flex items-center gap-1">
                <Phone className="w-4 h-4" />
                (555) 123-4567
              </span>
              <span className="flex items-center gap-1">
                <Mail className="w-4 h-4" />
                support@hero365.ai
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
