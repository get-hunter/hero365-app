/**
 * Booking Wizard Component
 * 
 * Multi-step booking flow for customers to book services
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { CheckCircle, Circle, ArrowLeft, ArrowRight, Calendar, User, MapPin, FileText } from 'lucide-react';
import { cn } from '../../lib/utils';

import { 
  BookingWizardProps, 
  BookingFormData, 
  BookingStep, 
  BookableService,
  TimeSlot,
  Booking
} from '../../lib/types/booking';
import { bookingApi } from '../../lib/api/booking-client';

import ServiceSelector from './ServiceSelector';
import DateTimeSelector from './DateTimeSelector';
import CustomerForm from './CustomerForm';
import BookingConfirmation from './BookingConfirmation';

const BOOKING_STEPS: BookingStep[] = [
  {
    id: 'service',
    title: 'Select Service',
    description: 'Choose the service you need',
    isComplete: false,
    isActive: true,
  },
  {
    id: 'datetime',
    title: 'Pick Date & Time',
    description: 'Select your preferred appointment time',
    isComplete: false,
    isActive: false,
  },
  {
    id: 'details',
    title: 'Your Information',
    description: 'Provide contact and service details',
    isComplete: false,
    isActive: false,
  },
  {
    id: 'confirmation',
    title: 'Confirmation',
    description: 'Review and confirm your booking',
    isComplete: false,
    isActive: false,
  },
];

const STEP_ICONS = {
  service: FileText,
  datetime: Calendar,
  details: User,
  confirmation: CheckCircle,
};

export default function BookingWizard({
  businessId,
  services,
  onBookingComplete,
  onBookingError,
  className
}: BookingWizardProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [steps, setSteps] = useState(BOOKING_STEPS);
  const [formData, setFormData] = useState<Partial<BookingFormData>>({
    smsConsent: false,
    emailConsent: true,
    preferredContactMethod: 'phone',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [completedBooking, setCompletedBooking] = useState<Booking | null>(null);
  const [error, setError] = useState<string | null>(null);

  const currentStep = steps[currentStepIndex];
  const isLastStep = currentStepIndex === steps.length - 1;
  const isFirstStep = currentStepIndex === 0;

  // Update step completion status
  useEffect(() => {
    setSteps(prevSteps => prevSteps.map((step, index) => ({
      ...step,
      isComplete: index < currentStepIndex || (index === currentStepIndex && isStepComplete(step.id)),
      isActive: index === currentStepIndex,
    })));
  }, [currentStepIndex, formData]);

  const isStepComplete = (stepId: string): boolean => {
    switch (stepId) {
      case 'service':
        return !!formData.serviceId;
      case 'datetime':
        return !!(formData.selectedDate && formData.selectedTimeSlot);
      case 'details':
        return !!(
          formData.customerName &&
          formData.customerPhone &&
          formData.serviceAddress &&
          (formData.customerEmail || formData.customerPhone)
        );
      case 'confirmation':
        return !!completedBooking;
      default:
        return false;
    }
  };

  const canProceedToNext = (): boolean => {
    return isStepComplete(currentStep.id);
  };

  const handleNext = () => {
    if (canProceedToNext() && !isLastStep) {
      setCurrentStepIndex(prev => prev + 1);
      setError(null);
    }
  };

  const handlePrevious = () => {
    if (!isFirstStep) {
      setCurrentStepIndex(prev => prev - 1);
      setError(null);
    }
  };

  const handleFormDataChange = (data: Partial<BookingFormData>) => {
    setFormData(prev => ({ ...prev, ...data }));
  };

  const handleSubmitBooking = async () => {
    if (!canProceedToNext()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      // Get user IP and user agent
      const [ipAddress, userAgent] = await Promise.all([
        bookingApi.getUserIpAddress(),
        bookingApi.getUserAgent(),
      ]);

      // Prepare booking request
      const bookingRequest = {
        business_id: businessId,
        service_id: formData.serviceId!,
        requested_at: bookingApi.formatDateTime(
          new Date(formData.selectedDate!.getTime() + 
            new Date(`1970-01-01T${formData.selectedTimeSlot!.start_time.split('T')[1]}`).getTime())
        ),
        customer_name: formData.customerName!,
        customer_email: formData.customerEmail,
        customer_phone: formData.customerPhone!,
        service_address: formData.serviceAddress!,
        service_city: formData.serviceCity,
        service_state: formData.serviceState,
        service_zip: formData.serviceZip,
        problem_description: formData.problemDescription,
        special_instructions: formData.specialInstructions,
        access_instructions: formData.accessInstructions,
        preferred_contact_method: formData.preferredContactMethod!,
        sms_consent: formData.smsConsent!,
        email_consent: formData.emailConsent!,
        source: 'website' as const,
        user_agent: userAgent,
        ip_address: ipAddress,
        idempotency_key: bookingApi.generateIdempotencyKey(),
      };

      // Create booking
      const response = await bookingApi.createBooking(bookingRequest, true); // Auto-confirm if possible
      
      setCompletedBooking(response.booking);
      setCurrentStepIndex(steps.length - 1); // Go to confirmation step
      
      if (onBookingComplete) {
        onBookingComplete(response.booking);
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create booking';
      setError(errorMessage);
      
      if (onBookingError) {
        onBookingError(errorMessage);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep.id) {
      case 'service':
        return (
          <ServiceSelector
            services={services}
            selectedServiceId={formData.serviceId}
            onServiceSelect={(serviceId) => handleFormDataChange({ serviceId })}
          />
        );

      case 'datetime':
        return (
          <DateTimeSelector
            businessId={businessId}
            serviceId={formData.serviceId!}
            selectedDate={formData.selectedDate}
            selectedTimeSlot={formData.selectedTimeSlot}
            onDateSelect={(date) => handleFormDataChange({ selectedDate: date })}
            onTimeSlotSelect={(slot) => handleFormDataChange({ selectedTimeSlot: slot })}
          />
        );

      case 'details':
        return (
          <CustomerForm
            formData={formData}
            onFormDataChange={handleFormDataChange}
            onSubmit={handleSubmitBooking}
            isSubmitting={isSubmitting}
          />
        );

      case 'confirmation':
        return completedBooking ? (
          <BookingConfirmation
            booking={completedBooking}
            onNewBooking={() => {
              setFormData({
                smsConsent: false,
                emailConsent: true,
                preferredContactMethod: 'phone',
              });
              setCompletedBooking(null);
              setCurrentStepIndex(0);
            }}
          />
        ) : null;

      default:
        return null;
    }
  };

  return (
    <div className={cn("max-w-4xl mx-auto", className)}>
      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const Icon = STEP_ICONS[step.id as keyof typeof STEP_ICONS];
            const isConnected = index < steps.length - 1;
            
            return (
              <React.Fragment key={step.id}>
                <div className="flex flex-col items-center">
                  <div
                    className={cn(
                      "flex items-center justify-center w-12 h-12 rounded-full border-2 transition-colors",
                      step.isComplete
                        ? "bg-green-500 border-green-500 text-white"
                        : step.isActive
                        ? "bg-blue-500 border-blue-500 text-white"
                        : "bg-gray-100 border-gray-300 text-gray-400"
                    )}
                  >
                    {step.isComplete ? (
                      <CheckCircle className="w-6 h-6" />
                    ) : (
                      <Icon className="w-6 h-6" />
                    )}
                  </div>
                  <div className="mt-2 text-center">
                    <div className={cn(
                      "text-sm font-medium",
                      step.isActive ? "text-blue-600" : "text-gray-600"
                    )}>
                      {step.title}
                    </div>
                    <div className="text-xs text-gray-500 hidden sm:block">
                      {step.description}
                    </div>
                  </div>
                </div>
                
                {isConnected && (
                  <div
                    className={cn(
                      "flex-1 h-0.5 mx-4 transition-colors",
                      step.isComplete ? "bg-green-500" : "bg-gray-300"
                    )}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Step Content */}
      <Card className="min-h-[500px]">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {React.createElement(STEP_ICONS[currentStep.id as keyof typeof STEP_ICONS], {
              className: "w-5 h-5"
            })}
            {currentStep.title}
          </CardTitle>
          <p className="text-gray-600">{currentStep.description}</p>
        </CardHeader>
        
        <CardContent>
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}
          
          {renderStepContent()}
        </CardContent>
      </Card>

      {/* Navigation */}
      {currentStep.id !== 'confirmation' && (
        <div className="flex justify-between mt-6">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={isFirstStep}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Previous
          </Button>

          {currentStep.id === 'details' ? (
            <Button
              onClick={handleSubmitBooking}
              disabled={!canProceedToNext() || isSubmitting}
              className="flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Creating Booking...
                </>
              ) : (
                <>
                  Book Appointment
                  <CheckCircle className="w-4 h-4" />
                </>
              )}
            </Button>
          ) : (
            <Button
              onClick={handleNext}
              disabled={!canProceedToNext()}
              className="flex items-center gap-2"
            >
              Next
              <ArrowRight className="w-4 h-4" />
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
