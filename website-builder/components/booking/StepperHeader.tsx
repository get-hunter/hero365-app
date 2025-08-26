/**
 * Stepper Header Component
 * 
 * Shows progress through the booking wizard with step indicators
 */

'use client';

import React from 'react';
import { Check, MapPin, Grid3x3, Home, Calendar, User, FileText, Eye, CheckCircle } from 'lucide-react';
import { useBookingWizard, WIZARD_STEPS, getStepName, isStepComplete } from './BookingWizardContext';

interface StepperHeaderProps {
  className?: string;
  showLabels?: boolean;
}

export default function StepperHeader({ className = '', showLabels = true }: StepperHeaderProps) {
  const { state, goToStep } = useBookingWizard();
  const { currentStep } = state;

  const steps = [
    { key: WIZARD_STEPS.ZIP_CHECK, icon: MapPin, label: 'Location' },
    { key: WIZARD_STEPS.CATEGORY, icon: Grid3x3, label: 'Service' },
    { key: WIZARD_STEPS.ADDRESS, icon: Home, label: 'Address' },
    { key: WIZARD_STEPS.DATETIME, icon: Calendar, label: 'Date & Time' },
    { key: WIZARD_STEPS.CONTACT, icon: User, label: 'Contact' },
    { key: WIZARD_STEPS.DETAILS, icon: FileText, label: 'Details' },
    { key: WIZARD_STEPS.REVIEW, icon: Eye, label: 'Review' },
    { key: WIZARD_STEPS.CONFIRMATION, icon: CheckCircle, label: 'Done' }
  ];

  const getStepStatus = (stepIndex: number) => {
    if (stepIndex < currentStep) {
      return isStepComplete(state, stepIndex) ? 'completed' : 'skipped';
    } else if (stepIndex === currentStep) {
      return 'current';
    } else {
      return 'upcoming';
    }
  };

  const getStepClasses = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500 text-white border-green-500';
      case 'current':
        return 'bg-blue-500 text-white border-blue-500';
      case 'skipped':
        return 'bg-gray-300 text-gray-600 border-gray-300';
      default:
        return 'bg-white text-gray-400 border-gray-300';
    }
  };

  const getConnectorClasses = (stepIndex: number) => {
    const status = getStepStatus(stepIndex);
    return status === 'completed' || status === 'current' 
      ? 'bg-green-500' 
      : 'bg-gray-300';
  };

  const canNavigateToStep = (stepIndex: number) => {
    // Can navigate to completed steps or current step
    return stepIndex <= currentStep || isStepComplete(state, stepIndex);
  };

  return (
    <div className={`w-full bg-white border-b border-gray-200 ${className}`}>
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const status = getStepStatus(index);
            const Icon = step.icon;
            const isClickable = canNavigateToStep(index);

            return (
              <React.Fragment key={step.key}>
                {/* Step Circle */}
                <div className="flex flex-col items-center">
                  <button
                    onClick={() => isClickable && goToStep(index)}
                    disabled={!isClickable}
                    className={`
                      relative w-10 h-10 md:w-12 md:h-12 rounded-full border-2 
                      flex items-center justify-center transition-all duration-200
                      ${getStepClasses(status)}
                      ${isClickable ? 'cursor-pointer hover:scale-105' : 'cursor-not-allowed'}
                      focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                    `}
                    aria-label={`${step.label} - ${status}`}
                  >
                    {status === 'completed' ? (
                      <Check className="w-5 h-5 md:w-6 md:h-6" />
                    ) : (
                      <Icon className="w-5 h-5 md:w-6 md:h-6" />
                    )}
                    
                    {/* Step number for mobile */}
                    <span className="absolute -top-2 -right-2 w-5 h-5 bg-gray-100 text-gray-600 text-xs rounded-full flex items-center justify-center md:hidden">
                      {index + 1}
                    </span>
                  </button>
                  
                  {/* Step Label */}
                  {showLabels && (
                    <div className="mt-2 text-center">
                      <div className={`
                        text-xs md:text-sm font-medium
                        ${status === 'current' ? 'text-blue-600' : 
                          status === 'completed' ? 'text-green-600' : 'text-gray-500'}
                      `}>
                        {step.label}
                      </div>
                      {status === 'current' && (
                        <div className="text-xs text-gray-500 mt-1 hidden md:block">
                          Step {index + 1} of {steps.length}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div className="flex-1 mx-2 md:mx-4">
                    <div className={`
                      h-0.5 md:h-1 rounded transition-colors duration-300
                      ${getConnectorClasses(index)}
                    `} />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Progress Bar (Mobile) */}
        <div className="mt-4 md:hidden">
          <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
            <span>Progress</span>
            <span>{currentStep + 1} of {steps.length}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Current Step Info */}
        <div className="mt-4 text-center">
          <h2 className="text-lg md:text-xl font-semibold text-gray-900">
            {getStepName(currentStep)}
          </h2>
          {state.error && (
            <div className="mt-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-2">
              {state.error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Compact version for mobile sticky header
export function CompactStepperHeader({ className = '' }: { className?: string }) {
  const { state } = useBookingWizard();
  const { currentStep } = state;

  return (
    <div className={`bg-white border-b border-gray-200 ${className}`}>
      <div className="max-w-4xl mx-auto px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="text-sm font-medium text-gray-900">
            {getStepName(currentStep)}
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="text-xs text-gray-500">
              {currentStep + 1} of {Object.keys(WIZARD_STEPS).length}
            </div>
            <div className="w-16 bg-gray-200 rounded-full h-1">
              <div 
                className="bg-blue-500 h-1 rounded-full transition-all duration-300"
                style={{ width: `${((currentStep + 1) / Object.keys(WIZARD_STEPS).length) * 100}%` }}
              />
            </div>
          </div>
        </div>
        
        {state.error && (
          <div className="mt-2 text-xs text-red-600 bg-red-50 border border-red-200 rounded-md p-2">
            {state.error}
          </div>
        )}
      </div>
    </div>
  );
}
