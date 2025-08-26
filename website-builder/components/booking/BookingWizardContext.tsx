/**
 * Booking Wizard Context
 * 
 * Manages state for the multi-step booking wizard with ZIP validation
 */

'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { useBookingAnalytics } from '../../lib/analytics/booking-analytics';

// Types for the booking wizard state
export interface ZipInfo {
  postalCode: string;
  countryCode: string;
  city?: string;
  region?: string;
  timezone: string;
  supported: boolean;
  dispatchFeeCents?: number;
  minResponseTimeHours?: number;
  maxResponseTimeHours?: number;
  emergencyAvailable?: boolean;
  regularAvailable?: boolean;
}

export interface Address {
  line1: string;
  line2?: string;
  city: string;
  region: string;
  postalCode: string;
  countryCode: string;
  geo?: {
    lat: number;
    lng: number;
  };
  accessNotes?: string;
}

export interface TimeSlot {
  start: string; // ISO datetime
  end: string;   // ISO datetime
  timezone: string;
}

export interface Contact {
  firstName: string;
  lastName: string;
  phoneE164: string; // +1234567890
  email: string;
  smsConsent: boolean;
  marketingConsent?: boolean;
}

export interface BookingDetails {
  notes?: string;
  attachments?: File[];
  urgencyLevel: 'emergency' | 'urgent' | 'normal' | 'flexible';
}

export interface BookingWizardState {
  // Current step
  currentStep: number;
  
  // Step data
  zipInfo?: ZipInfo;
  categoryId?: string;
  serviceId?: string;
  address?: Address;
  slot?: TimeSlot;
  contact?: Contact;
  details?: BookingDetails;
  
  // Flags
  dispatchFeeAccepted: boolean;
  termsAccepted: boolean;
  
  // UI state
  isLoading: boolean;
  error?: string;
}

export interface BookingWizardContextType {
  state: BookingWizardState;
  
  // Navigation
  nextStep: () => void;
  prevStep: () => void;
  goToStep: (step: number) => void;
  canProceed: () => boolean;
  
  // Data updates
  updateZipInfo: (zipInfo: ZipInfo) => void;
  updateService: (categoryId: string, serviceId: string) => void;
  updateAddress: (address: Address) => void;
  updateSlot: (slot: TimeSlot) => void;
  updateContact: (contact: Contact) => void;
  updateDetails: (details: BookingDetails) => void;
  updateFlags: (flags: Partial<{ dispatchFeeAccepted: boolean; termsAccepted: boolean }>) => void;
  
  // UI state
  setLoading: (loading: boolean) => void;
  setError: (error?: string) => void;
  
  // Reset
  resetWizard: () => void;
}

const BookingWizardContext = createContext<BookingWizardContextType | undefined>(undefined);

// Wizard steps
export const WIZARD_STEPS = {
  ZIP_CHECK: 0,
  CATEGORY: 1,
  ADDRESS: 2,
  DATETIME: 3,
  CONTACT: 4,
  DETAILS: 5,
  REVIEW: 6,
  CONFIRMATION: 7
} as const;

export const TOTAL_STEPS = Object.keys(WIZARD_STEPS).length;

interface BookingWizardProviderProps {
  children: ReactNode;
  businessId: string;
  onComplete?: (bookingData: any) => void;
  onError?: (error: string) => void;
}

export function BookingWizardProvider({
  children,
  businessId,
  onComplete,
  onError
}: BookingWizardProviderProps) {
  const [state, setState] = useState<BookingWizardState>({
    currentStep: WIZARD_STEPS.ZIP_CHECK,
    dispatchFeeAccepted: false,
    termsAccepted: false,
    isLoading: false
  });
  
  const analytics = useBookingAnalytics();

  // Track step views
  useEffect(() => {
    const stepNames = ['zip_gate', 'category', 'address', 'datetime', 'contact', 'details', 'review', 'confirmation'];
    const currentStepName = stepNames[state.currentStep] as any;
    analytics.trackStep(currentStepName, 'view', { businessId });
  }, [state.currentStep, analytics, businessId]);

  // Navigation functions
  const nextStep = useCallback(() => {
    if (state.currentStep < TOTAL_STEPS - 1) {
      const stepNames = ['zip_gate', 'category', 'address', 'datetime', 'contact', 'details', 'review', 'confirmation'];
      const currentStepName = stepNames[state.currentStep] as any;
      analytics.trackStep(currentStepName, 'next', { businessId });
      setState(prev => ({ ...prev, currentStep: prev.currentStep + 1, error: undefined }));
    }
  }, [state.currentStep, analytics, businessId]);

  const prevStep = useCallback(() => {
    if (state.currentStep > 0) {
      const stepNames = ['zip_gate', 'category', 'address', 'datetime', 'contact', 'details', 'review', 'confirmation'];
      const currentStepName = stepNames[state.currentStep] as any;
      analytics.trackStep(currentStepName, 'back', { businessId });
      setState(prev => ({ ...prev, currentStep: prev.currentStep - 1, error: undefined }));
    }
  }, [state.currentStep, analytics, businessId]);

  const goToStep = useCallback((step: number) => {
    if (step >= 0 && step < TOTAL_STEPS) {
      const stepNames = ['zip_gate', 'category', 'address', 'datetime', 'contact', 'details', 'review', 'confirmation'];
      const stepName = stepNames[step] as any;
      analytics.trackStep(stepName, 'view', { businessId });
      setState(prev => ({ ...prev, currentStep: step, error: undefined }));
    }
  }, [analytics, businessId]);

  // Validation function to check if user can proceed
  const canProceed = useCallback(() => {
    switch (state.currentStep) {
      case WIZARD_STEPS.ZIP_CHECK:
        return state.zipInfo?.supported === true;
      
      case WIZARD_STEPS.CATEGORY:
        return !!(state.categoryId && state.serviceId);
      
      case WIZARD_STEPS.ADDRESS:
        return !!(state.address?.line1 && state.address?.city && state.address?.region);
      
      case WIZARD_STEPS.DATETIME:
        return !!(state.slot?.start && state.slot?.end);
      
      case WIZARD_STEPS.CONTACT:
        return !!(state.contact?.firstName && state.contact?.lastName && 
                 state.contact?.phoneE164 && state.contact?.email);
      
      case WIZARD_STEPS.DETAILS:
        return true; // Details are optional
      
      case WIZARD_STEPS.REVIEW:
        return state.termsAccepted;
      
      default:
        return false;
    }
  }, [state]);

  // Data update functions
  const updateZipInfo = useCallback((zipInfo: ZipInfo) => {
    setState(prev => ({ ...prev, zipInfo, error: undefined }));
  }, []);

  const updateService = useCallback((categoryId: string, serviceId: string) => {
    setState(prev => ({ ...prev, categoryId, serviceId, error: undefined }));
  }, []);

  const updateAddress = useCallback((address: Address) => {
    setState(prev => ({ ...prev, address, error: undefined }));
  }, []);

  const updateSlot = useCallback((slot: TimeSlot) => {
    setState(prev => ({ ...prev, slot, error: undefined }));
  }, []);

  const updateContact = useCallback((contact: Contact) => {
    setState(prev => ({ ...prev, contact, error: undefined }));
  }, []);

  const updateDetails = useCallback((details: BookingDetails) => {
    setState(prev => ({ ...prev, details, error: undefined }));
  }, []);

  const updateFlags = useCallback((flags: Partial<{ dispatchFeeAccepted: boolean; termsAccepted: boolean }>) => {
    setState(prev => ({ ...prev, ...flags, error: undefined }));
  }, []);

  // UI state functions
  const setLoading = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoading: loading }));
  }, []);

  const setError = useCallback((error?: string) => {
    setState(prev => ({ ...prev, error }));
    if (error && onError) {
      onError(error);
    }
  }, [onError]);

  // Reset function
  const resetWizard = useCallback(() => {
    setState({
      currentStep: WIZARD_STEPS.ZIP_CHECK,
      dispatchFeeAccepted: false,
      termsAccepted: false,
      isLoading: false
    });
  }, []);

  const contextValue: BookingWizardContextType = {
    state,
    nextStep,
    prevStep,
    goToStep,
    canProceed,
    updateZipInfo,
    updateService,
    updateAddress,
    updateSlot,
    updateContact,
    updateDetails,
    updateFlags,
    setLoading,
    setError,
    resetWizard
  };

  return (
    <BookingWizardContext.Provider value={contextValue}>
      {children}
    </BookingWizardContext.Provider>
  );
}

// Hook to use the booking wizard context
export function useBookingWizard(): BookingWizardContextType {
  const context = useContext(BookingWizardContext);
  if (!context) {
    throw new Error('useBookingWizard must be used within a BookingWizardProvider');
  }
  return context;
}

// Helper functions for step validation and navigation
export function getStepName(step: number): string {
  const stepNames = [
    'ZIP Code',
    'Service',
    'Address',
    'Date & Time',
    'Contact',
    'Details',
    'Review',
    'Confirmation'
  ];
  return stepNames[step] || 'Unknown';
}

export function isStepComplete(state: BookingWizardState, step: number): boolean {
  switch (step) {
    case WIZARD_STEPS.ZIP_CHECK:
      return state.zipInfo?.supported === true;
    case WIZARD_STEPS.CATEGORY:
      return !!(state.categoryId && state.serviceId);
    case WIZARD_STEPS.ADDRESS:
      return !!(state.address?.line1 && state.address?.city);
    case WIZARD_STEPS.DATETIME:
      return !!(state.slot?.start);
    case WIZARD_STEPS.CONTACT:
      return !!(state.contact?.firstName && state.contact?.email);
    case WIZARD_STEPS.DETAILS:
      return true; // Always considered complete
    case WIZARD_STEPS.REVIEW:
      return state.termsAccepted;
    default:
      return false;
  }
}

export function getCompletedSteps(state: BookingWizardState): number[] {
  const completed = [];
  for (let i = 0; i < TOTAL_STEPS; i++) {
    if (isStepComplete(state, i)) {
      completed.push(i);
    }
  }
  return completed;
}
