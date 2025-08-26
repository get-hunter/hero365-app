/**
 * ZIP Gate Step (Step 0)
 * 
 * Validates postal code before allowing user to proceed with booking
 */

'use client';

import React, { useState, useEffect } from 'react';
import { MapPin, Truck, Clock, AlertCircle, CheckCircle, Phone, Mail } from 'lucide-react';
import { serviceAreasApi, ServiceAreaCheckResponse } from '../../../lib/api/service-areas-client';
import { useBookingAnalytics } from '../../../lib/analytics/booking-analytics';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/card';
import { Badge } from '../../ui/badge';
import { useBookingWizard, ZipInfo } from '../BookingWizardContext';

interface ZipGateStepProps {
  businessId: string;
  businessName?: string;
  businessPhone?: string;
  businessEmail?: string;
}

// ServiceAreaCheckResponse is now imported from the API client

const COUNTRIES = [
  { code: 'US', name: 'United States', flag: '🇺🇸' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺' }
];

export default function ZipGateStep({
  businessId,
  businessName = 'our team',
  businessPhone,
  businessEmail
}: ZipGateStepProps) {
  const { state, updateZipInfo, nextStep, setLoading, setError } = useBookingWizard();
  const analytics = useBookingAnalytics();
  
  const [postalCode, setPostalCode] = useState(state.zipInfo?.postalCode || '');
  const [countryCode, setCountryCode] = useState(state.zipInfo?.countryCode || 'US');
  const [checkResult, setCheckResult] = useState<ServiceAreaCheckResponse | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  // Auto-detect country from browser if available
  useEffect(() => {
    if (!state.zipInfo && 'geolocation' in navigator) {
      // Could implement IP-based country detection here
      // For now, default to US
    }
  }, [state.zipInfo]);

  const handlePostalCodeChange = (value: string) => {
    setPostalCode(value.toUpperCase());
    setCheckResult(null);
    setError();
  };

  const checkServiceArea = async () => {
    if (!postalCode.trim()) {
      setError('Please enter a postal code');
      return;
    }

    // Validate postal code format
    if (!serviceAreasApi.validatePostalCode(postalCode, countryCode)) {
      setError(`Please enter a valid ${serviceAreasApi.getPostalCodeLabel(countryCode).toLowerCase()}`);
      return;
    }

    setIsChecking(true);
    setLoading(true);
    setError();

    try {
      const normalizedPostalCode = serviceAreasApi.normalizePostalCode(postalCode, countryCode);
      
      const result = await serviceAreasApi.checkServiceAreaSupport({
        business_id: businessId,
        postal_code: normalizedPostalCode,
        country_code: countryCode
      });

      setCheckResult(result);

      // Track ZIP validation analytics
      analytics.trackZipValidation(
        normalizedPostalCode, 
        countryCode, 
        result.supported, 
        result.suggestions
      );

      if (result.supported && result.normalized) {
        const zipInfo: ZipInfo = {
          postalCode: result.normalized.postal_code,
          countryCode: result.normalized.country_code,
          city: result.normalized.city,
          region: result.normalized.region,
          timezone: result.normalized.timezone,
          supported: true,
          dispatchFeeCents: result.normalized.dispatch_fee_cents,
          minResponseTimeHours: result.normalized.min_response_time_hours,
          maxResponseTimeHours: result.normalized.max_response_time_hours,
          emergencyAvailable: result.normalized.emergency_available,
          regularAvailable: result.normalized.regular_available
        };

        updateZipInfo(zipInfo);
      } else {
        updateZipInfo({
          postalCode: normalizedPostalCode,
          countryCode: countryCode,
          timezone: 'America/New_York', // Default
          supported: false
        });
      }

    } catch (error) {
      console.error('Error checking service area:', error);
      setError('Unable to check service area. Please try again.');
    } finally {
      setIsChecking(false);
      setLoading(false);
    }
  };

  const handleContinue = () => {
    if (state.zipInfo?.supported) {
      nextStep();
    }
  };

  const handleRequestService = async () => {
    if (!businessEmail && !businessPhone) {
      setError('Contact information not available');
      return;
    }

    // For now, just show contact info. Later we can implement the availability request API
    setError('Please contact us directly to request service in your area');
  };

  const selectedCountry = COUNTRIES.find(c => c.code === countryCode);

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <MapPin className="w-8 h-8 text-blue-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          What's your location?
        </h1>
        <p className="text-gray-600">
          Enter your postal code so we can check if we provide service in your area
        </p>
      </div>

      {/* Input Form */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Country
              </label>
              <Select value={countryCode} onValueChange={setCountryCode}>
                <SelectTrigger>
                  <SelectValue>
                    {selectedCountry && (
                      <span className="flex items-center">
                        <span className="mr-2">{selectedCountry.flag}</span>
                        {selectedCountry.name}
                      </span>
                    )}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent>
                  {COUNTRIES.map((country) => (
                    <SelectItem key={country.code} value={country.code}>
                      <span className="flex items-center">
                        <span className="mr-2">{country.flag}</span>
                        {country.name}
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {serviceAreasApi.getPostalCodeLabel(countryCode)} *
              </label>
              <div className="flex space-x-3">
                <Input
                  value={postalCode}
                  onChange={(e) => handlePostalCodeChange(e.target.value)}
                  placeholder={serviceAreasApi.getPostalCodePlaceholder(countryCode)}
                  className="flex-1"
                  maxLength={10}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      checkServiceArea();
                    }
                  }}
                />
                <Button
                  onClick={checkServiceArea}
                  disabled={!postalCode.trim() || isChecking}
                  className="px-6"
                >
                  {isChecking ? 'Checking...' : 'Check'}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {checkResult && (
        <div className="space-y-4">
          {checkResult.supported ? (
            /* Supported Area */
            <Card className="border-green-200 bg-green-50">
              <CardContent className="p-6">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-6 h-6 text-green-600 mt-1" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-green-900 mb-2">
                      Great! We service your area
                    </h3>
                    
                    {checkResult.normalized && (
                      <div className="space-y-3">
                        <div className="text-sm text-green-800">
                          <strong>Service Area:</strong> {checkResult.normalized.city}, {checkResult.normalized.region} {checkResult.normalized.postal_code}
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                          <div className="flex items-center space-x-2">
                            <Clock className="w-4 h-4 text-green-600" />
                            <span>Response: {checkResult.normalized.min_response_time_hours}-{checkResult.normalized.max_response_time_hours} hours</span>
                          </div>
                          
                          {checkResult.normalized.dispatch_fee_cents > 0 && (
                            <div className="flex items-center space-x-2">
                              <Truck className="w-4 h-4 text-green-600" />
                              <span>Service fee: ${(checkResult.normalized.dispatch_fee_cents / 100).toFixed(2)}</span>
                            </div>
                          )}
                        </div>

                        <div className="flex flex-wrap gap-2">
                          {checkResult.normalized.emergency_available && (
                            <Badge variant="secondary" className="bg-red-100 text-red-800">
                              24/7 Emergency
                            </Badge>
                          )}
                          {checkResult.normalized.regular_available && (
                            <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                              Regular Service
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
                    
                    <Button 
                      onClick={handleContinue}
                      className="mt-4 w-full md:w-auto"
                    >
                      Continue Booking
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            /* Unsupported Area */
            <Card className="border-orange-200 bg-orange-50">
              <CardContent className="p-6">
                <div className="flex items-start space-x-3">
                  <AlertCircle className="w-6 h-6 text-orange-600 mt-1" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-orange-900 mb-2">
                      Service not yet available in your area
                    </h3>
                    <p className="text-sm text-orange-800 mb-4">
                      We're expanding our service area and would love to help you in the future.
                    </p>

                    {/* Suggestions */}
                    {checkResult.suggestions && checkResult.suggestions.length > 0 && (
                      <div className="mb-4">
                        <p className="text-sm font-medium text-orange-900 mb-2">
                          We do service these nearby areas:
                        </p>
                        <div className="space-y-1">
                          {checkResult.suggestions.map((suggestion, index) => (
                            <div key={index} className="text-sm text-orange-800">
                              • {suggestion.city}, {suggestion.region} {suggestion.postal_code}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Contact Options */}
                    <div className="space-y-3">
                      <p className="text-sm font-medium text-orange-900">
                        Get in touch with {businessName}:
                      </p>
                      
                      <div className="flex flex-col sm:flex-row gap-3">
                        {businessPhone && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="border-orange-300 text-orange-700 hover:bg-orange-100"
                            asChild
                          >
                            <a href={`tel:${businessPhone}`}>
                              <Phone className="w-4 h-4 mr-2" />
                              Call {businessPhone}
                            </a>
                          </Button>
                        )}
                        
                        {businessEmail && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="border-orange-300 text-orange-700 hover:bg-orange-100"
                            asChild
                          >
                            <a href={`mailto:${businessEmail}`}>
                              <Mail className="w-4 h-4 mr-2" />
                              Email Us
                            </a>
                          </Button>
                        )}
                      </div>

                      <Button
                        onClick={handleRequestService}
                        size="sm"
                        className="w-full sm:w-auto"
                      >
                        Request Service Notification
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Emergency Override */}
      {checkResult && !checkResult.supported && (
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="text-red-900 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" />
              Emergency Service
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-red-800 mb-4">
              If this is an emergency, please call us directly. We may be able to provide emergency service even outside our regular service area.
            </p>
            {businessPhone && (
              <Button
                variant="destructive"
                asChild
                className="w-full sm:w-auto"
              >
                <a href={`tel:${businessPhone}`}>
                  <Phone className="w-4 h-4 mr-2" />
                  Emergency: {businessPhone}
                </a>
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
