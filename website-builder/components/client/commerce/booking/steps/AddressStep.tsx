/**
 * Address Step (Step 2)
 * 
 * Collects service address with optional autocomplete and validation
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { MapPin, Home, Edit3, AlertCircle, CheckCircle, ArrowLeft, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useBookingWizard, Address } from '../Hero365BookingContext';
import GooglePlacesAutocomplete, { parseGooglePlaceResult } from '@/components/client/maps/GooglePlacesAutocomplete';
import BookingSummaryCard from '../shared/BookingSummaryCard';

interface AddressStepProps {
  businessId: string;
}

export default function AddressStep({ businessId }: AddressStepProps) {
  const { state, updateAddress, nextStep, prevStep, setLoading, setError } = useBookingWizard();
  
  // State for service details
  const [selectedServiceDetails, setSelectedServiceDetails] = useState<any>(null);
  const [isPlaceSelected, setIsPlaceSelected] = useState(false);
  const firstInputRef = useRef<HTMLInputElement>(null);
  
  // Form state
  const [formData, setFormData] = useState<Partial<Address>>({
    line1: state.address?.line1 || '',
    line2: state.address?.line2 || '',
    city: state.zipInfo?.city || state.address?.city || '',
    region: state.zipInfo?.region || state.address?.region || '',
    postalCode: state.zipInfo?.postalCode || state.address?.postalCode || '',
    countryCode: state.zipInfo?.countryCode || state.address?.countryCode || 'US',
    accessNotes: state.address?.accessNotes || ''
  });

  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    message?: string;
    suggestions?: Array<{
      line1: string;
      city: string;
      region: string;
      postalCode: string;
    }>;
  } | null>(null);

  // Pre-fill from ZIP info if available
  useEffect(() => {
    if (state.zipInfo && !formData.city) {
      setFormData(prev => ({
        ...prev,
        city: state.zipInfo?.city || '',
        region: state.zipInfo?.region || '',
        postalCode: state.zipInfo?.postalCode || '',
        countryCode: state.zipInfo?.countryCode || 'US'
      }));
    }
  }, [state.zipInfo]);

  // On mount, scroll the street address input into view and focus it
  useEffect(() => {
    setTimeout(() => {
      const el = firstInputRef.current as any;
      if (el) {
        try { el.focus?.(); } catch {}
        (el as HTMLElement).scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 0);
  }, []);

  // Load service details when component mounts
  useEffect(() => {
    if (state.serviceId && businessId) {
      loadServiceDetails();
    }
  }, [state.serviceId, businessId]);

  const loadServiceDetails = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/public/contractors/${businessId}/booking-trades`
      );
      
      if (response.ok) {
        const data = await response.json();
        // Find the selected service across all trades
        for (const trade of data.trades) {
          const service = trade.services.find((s: any) => s.id === state.serviceId);
          if (service) {
            setSelectedServiceDetails({
              ...service,
              tradeName: trade.trade_display_name,
              tradeIcon: trade.trade_icon,
              tradeColor: trade.trade_color
            });
            break;
          }
        }
      }
    } catch (error) {
      console.error('Error loading service details:', error);
    }
  };

  const handleInputChange = (field: keyof Address, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setValidationResult(null);
    setError();
    
    // Reset place selection flag if user manually edits the address
    if (field === 'line1') {
      setIsPlaceSelected(false);
    }
  };

  const validateAddress = async () => {
    if (!formData.line1?.trim()) {
      setError('Street address is required');
      return false;
    }

    if (!formData.city?.trim()) {
      setError('City is required');
      return false;
    }

    if (!formData.region?.trim()) {
      setError('State/Province is required');
      return false;
    }

    if (!formData.postalCode?.trim()) {
      setError('Postal code is required');
      return false;
    }

    setIsValidating(true);
    setLoading(true);

    try {
      // Mock address validation - in real implementation, this would call a geocoding service
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Simulate validation result
      const isValid = Math.random() > 0.2; // 80% success rate for demo
      
      if (isValid) {
        setValidationResult({
          valid: true,
          message: 'Address validated successfully'
        });
        return true;
      } else {
        setValidationResult({
          valid: false,
          message: 'Address could not be verified. Please check and try again.',
          suggestions: [
            {
              line1: `${formData.line1} (Suggested)`,
              city: formData.city!,
              region: formData.region!,
              postalCode: formData.postalCode!
            }
          ]
        });
        return false;
      }
    } catch (error) {
      console.error('Address validation error:', error);
      setError('Unable to validate address. Please check your input.');
      return false;
    } finally {
      setIsValidating(false);
      setLoading(false);
    }
  };

  const handleContinue = async () => {
    const isValid = await validateAddress();
    
    if (isValid && formData.line1 && formData.city && formData.region && formData.postalCode) {
      const address: Address = {
        line1: formData.line1,
        line2: formData.line2,
        city: formData.city,
        region: formData.region,
        postalCode: formData.postalCode,
        countryCode: formData.countryCode || 'US',
        accessNotes: formData.accessNotes
      };

      updateAddress(address);
      nextStep();
    }
  };

  const applySuggestion = (suggestion: any) => {
    setFormData(prev => ({
      ...prev,
      line1: suggestion.line1,
      city: suggestion.city,
      region: suggestion.region,
      postalCode: suggestion.postalCode
    }));
    setValidationResult(null);
  };

  const handlePlaceSelect = (place: google.maps.places.PlaceResult) => {
    const parsedAddress = parseGooglePlaceResult(place);
    
    setFormData(prev => ({
      ...prev,
      line1: parsedAddress.line1 || prev.line1,
      city: parsedAddress.city || prev.city,
      region: parsedAddress.region || prev.region,
      postalCode: parsedAddress.postalCode || prev.postalCode,
      countryCode: parsedAddress.countryCode || prev.countryCode
    }));
    
    // Mark that a place was selected from Google Places
    setIsPlaceSelected(true);
    
    // Clear any previous validation errors
    setValidationResult(null);
    setError();
  };

  const isFormValid = formData.line1?.trim() && formData.city?.trim() && 
                     formData.region?.trim() && formData.postalCode?.trim();

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      {/* Back Button */}
      <div className="flex items-center justify-start mb-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={prevStep}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </Button>
      </div>

      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Home className="w-8 h-8 text-blue-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Where do you need service?
        </h1>
        <p className="text-gray-600">
          Please provide the address where our technician should visit
        </p>
      </div>

      {/* Progress Summary */}
      <BookingSummaryCard
        items={[
          ...(selectedServiceDetails ? [{
            icon: FileText,
            title: 'Service Selected',
            subtitle: selectedServiceDetails.name,
            details: `${selectedServiceDetails.tradeName} • ${selectedServiceDetails.base_price ? `Starting at $${selectedServiceDetails.base_price.toLocaleString()}` : 'Custom pricing'}`
          }] : []),
          ...(state.zipInfo ? [{
            icon: MapPin,
            title: 'Service Area Confirmed',
            subtitle: `${state.zipInfo.city}, ${state.zipInfo.region}`,
            details: `Response time: ${state.zipInfo.minResponseTimeHours}-${state.zipInfo.maxResponseTimeHours} hours`
          }] : [])
        ]}
      />


      {/* Address Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MapPin className="w-5 h-5" />
            <span>Service Address</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Street Address with Google Places Autocomplete */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Street Address *
            </label>
            <GooglePlacesAutocomplete
              value={formData.line1 || ''}
              onChange={(value) => handleInputChange('line1', value)}
              onPlaceSelect={handlePlaceSelect}
              placeholder="Start typing your address..."
              className="w-full"
              autoFocus
            />
            {isPlaceSelected ? (
              <div className="flex items-center space-x-2 mt-1">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <p className="text-xs text-green-600 font-medium">
                  Address verified with Google Maps
                </p>
              </div>
            ) : (
              <p className="text-xs text-gray-500 mt-1">
                Start typing and select from suggestions for faster, accurate address entry
              </p>
            )}
          </div>

          {/* Address Line 2 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Apartment, Suite, etc. (Optional)
            </label>
            <Input
              value={formData.line2 || ''}
              onChange={(e) => handleInputChange('line2', e.target.value)}
              placeholder="Apt 4B, Suite 200, etc."
              className="w-full"
            />
          </div>

          {/* City, State, ZIP */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                City *
              </label>
              <Input
                value={formData.city || ''}
                onChange={(e) => handleInputChange('city', e.target.value)}
                placeholder="City"
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                State/Province *
              </label>
              <Input
                value={formData.region || ''}
                onChange={(e) => handleInputChange('region', e.target.value)}
                placeholder="State"
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ZIP/Postal Code *
              </label>
              <Input
                value={formData.postalCode || ''}
                onChange={(e) => handleInputChange('postalCode', e.target.value)}
                placeholder="12345"
                className="w-full"
              />
            </div>
          </div>

          {/* Access Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Access Instructions (Optional)
            </label>
            <Textarea
              value={formData.accessNotes || ''}
              onChange={(e) => handleInputChange('accessNotes', e.target.value)}
              placeholder="Gate code, parking instructions, pet information, etc."
              rows={3}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              Help our technician find and access your property easily
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Validation Results */}
      {validationResult && (
        <Card className={validationResult.valid ? 'border-green-200 bg-green-50' : 'border-orange-200 bg-orange-50'}>
          <CardContent className="p-4">
            <div className="flex items-start space-x-3">
              {validationResult.valid ? (
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              ) : (
                <AlertCircle className="w-5 h-5 text-orange-600 mt-0.5" />
              )}
              <div className="flex-1">
                <p className={`text-sm font-medium ${validationResult.valid ? 'text-green-900' : 'text-orange-900'}`}>
                  {validationResult.message}
                </p>
                
                {/* Address Suggestions */}
                {validationResult.suggestions && validationResult.suggestions.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-orange-900 mb-2">
                      Did you mean:
                    </p>
                    <div className="space-y-2">
                      {validationResult.suggestions.map((suggestion, index) => (
                        <div
                          key={index}
                          className="p-3 bg-white border border-orange-200 rounded-md cursor-pointer hover:bg-orange-25 transition-colors"
                          onClick={() => applySuggestion(suggestion)}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-gray-900">
                                {suggestion.line1}
                              </p>
                              <p className="text-xs text-gray-600">
                                {suggestion.city}, {suggestion.region} {suggestion.postalCode}
                              </p>
                            </div>
                            <Button variant="outline" size="sm">
                              Use This
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          onClick={handleContinue}
          disabled={!isFormValid || isValidating}
          size="lg"
          className="px-8"
        >
          {isValidating ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              Validating Address...
            </>
          ) : (
            'Continue to Date & Time'
          )}
        </Button>
      </div>

      {/* Help Text */}
      <div className="text-center">
        <p className="text-sm text-gray-500">
          We'll validate this address to ensure our technician can reach you
        </p>
      </div>
    </div>
  );
}
