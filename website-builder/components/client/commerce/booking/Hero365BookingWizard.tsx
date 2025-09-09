/**
 * Booking Wizard Component
 * 
 * Main wizard component that orchestrates the multi-step booking flow
 */

'use client';

import React from 'react';
import type { BookableService } from '@/lib/shared/types/booking';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { 
  useBookingWizard, 
  BookingWizardProvider, 
  WIZARD_STEPS 
} from './Hero365BookingContext';
import StepperHeader from './StepperHeader';
import ZipGateStep from './steps/ZipGateStep';
import TradeServiceStep from './steps/TradeServiceStep';
import AddressStep from './steps/AddressStep';
import DateTimeStep from './steps/DateTimeStep';
import ContactStep from './steps/ContactStep';
import DetailsStep from './steps/DetailsStep';
import ReviewStep from './steps/ReviewStep';
import ConfirmationStep from './steps/ConfirmationStep';

interface BookingWizardProps {
  businessId: string;
  businessName?: string;
  businessPhone?: string;
  businessEmail?: string;
  services?: BookableService[];
  onClose?: () => void;
  onComplete?: (bookingData: any) => void;
  className?: string;
  countryCode?: string;
}

function BookingWizardContent({
  businessId,
  businessName,
  businessPhone,
  businessEmail,
  services,
  onClose,
  onComplete,
  countryCode
}: BookingWizardProps) {
  const { state, prevStep, canProceed, resetWizard } = useBookingWizard();
  const { currentStep, isLoading } = state;

  const resolvedCountryCode = (countryCode || 'US').toUpperCase();

  const renderCurrentStep = () => {
    switch (currentStep) {
      case WIZARD_STEPS.ZIP_CHECK:
        return (
          <ZipGateStep
            businessId={businessId}
            businessName={businessName}
            businessPhone={businessPhone}
            businessEmail={businessEmail}
            countryCode={resolvedCountryCode}
          />
        );
      
      case WIZARD_STEPS.CATEGORY:
        return (
          <TradeServiceStep
            businessId={businessId}
          />
        );
      
      case WIZARD_STEPS.ADDRESS:
        return <AddressStep businessId={businessId} />;
      
      case WIZARD_STEPS.DATETIME:
        return <DateTimeStep businessId={businessId} />;
      
      case WIZARD_STEPS.CONTACT:
        return <ContactStep businessId={businessId} businessName={businessName} />;
      
      case WIZARD_STEPS.DETAILS:
        return <DetailsStep businessId={businessId} />;
      
      case WIZARD_STEPS.REVIEW:
        return (
          <ReviewStep 
            businessId={businessId} 
            businessName={businessName}
            businessPhone={businessPhone}
            businessEmail={businessEmail}
          />
        );
      
      case WIZARD_STEPS.CONFIRMATION:
        return (
          <ConfirmationStep 
            businessId={businessId} 
            businessName={businessName}
            businessPhone={businessPhone}
            businessEmail={businessEmail}
            onClose={onClose}
          />
        );
      
      default:
        return <div className="p-6 text-center">Unknown step</div>;
    }
  };

  const handleClose = () => {
    resetWizard();
    onClose?.();
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="flex-shrink-0">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <h1 className="text-lg font-semibold text-gray-900">
              Book Service
            </h1>
            {businessName && (
              <span className="text-sm text-gray-500">with {businessName}</span>
            )}
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>
        
        <StepperHeader showLabels={false} />
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {renderCurrentStep()}
      </div>

      {/* Footer Navigation */}
      <div className="flex-shrink-0 border-t border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            {/* Back button removed - each step handles its own navigation */}
          </div>

          <div className="flex items-center space-x-3">
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
                <span>Loading...</span>
              </div>
            )}

            {/* Progress indicator */}
            <div className="text-sm text-gray-500">
              Step {currentStep + 1} of {Object.keys(WIZARD_STEPS).length}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function BookingWizard(props: BookingWizardProps) {
  const { businessId, onComplete, onClose, className = '' } = props;

  const handleComplete = (bookingData: any) => {
    console.log('Booking completed:', bookingData);
    onComplete?.(bookingData);
  };

  const handleError = (error: string) => {
    console.error('Booking error:', error);
    // Could show a toast or error message
  };

  return (
    <div className={`w-full h-full ${className}`}>
      <BookingWizardProvider
        businessId={businessId}
        onComplete={handleComplete}
        onError={handleError}
      >
        <BookingWizardContent {...props} />
      </BookingWizardProvider>
    </div>
  );
}