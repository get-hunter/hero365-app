/**
 * ZIP Gate Step (Step 0)
 * 
 * Validates postal code before allowing user to proceed with booking
 */

'use client';

import React, { useState, useEffect } from 'react';
import { MapPin, Truck, Clock, AlertCircle, CheckCircle, Phone, Mail } from 'lucide-react';
import { serviceAreasApi, ServiceAreaCheckResponse } from '@/lib/api/service-areas-client';
import { useBookingAnalytics } from '@/lib/client/analytics/booking-analytics';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useBookingWizard, ZipInfo } from '../Hero365BookingContext';

interface ZipGateStepProps {
  businessId: string;
  businessName?: string;
  businessPhone?: string;
  businessEmail?: string;
  countryCode: string; // new: provided by wizard based on business
}

export default function ZipGateStep({
  businessId,
  businessName = 'our team',
  businessPhone,
  businessEmail,
  countryCode
}: ZipGateStepProps) {
  const { state, updateZipInfo, nextStep, setLoading, setError } = useBookingWizard();
  const analytics = useBookingAnalytics();
  
  const resolvedCountryCode = (countryCode || 'US').toUpperCase();
  const [postalCode, setPostalCode] = useState(state.zipInfo?.postalCode || '');
  const [checkResult, setCheckResult] = useState<ServiceAreaCheckResponse | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [autoAttempted, setAutoAttempted] = useState(false);
  const [lastCheckedCode, setLastCheckedCode] = useState<string | null>(null);

  useEffect(() => {
    // Clear previous errors when component mounts or country changes
    setError();
    setCheckResult(null);
    setLastCheckedCode(null);
  }, [resolvedCountryCode, setError]);

  useEffect(() => {
    // Auto-check when the postal code becomes valid (debounced)
    if (!postalCode) return;
    const normalized = serviceAreasApi.normalizePostalCode(postalCode, resolvedCountryCode);
    if (!serviceAreasApi.validatePostalCode(normalized, resolvedCountryCode)) return;
    if (isChecking || normalized === lastCheckedCode) return;
    const t = setTimeout(() => {
      setLastCheckedCode(normalized);
      void checkServiceArea(normalized);
    }, 350);
    return () => clearTimeout(t);
  }, [postalCode, resolvedCountryCode, isChecking, lastCheckedCode]);

  useEffect(() => {
    // Try auto-detect once if user already granted permission and no postal filled
    if (autoAttempted || postalCode || typeof window === 'undefined') return;
    const permissions: any = (navigator as any).permissions;
    if (permissions && permissions.query) {
      permissions.query({ name: 'geolocation' as any }).then((result: any) => {
        if (result.state === 'granted') {
          setAutoAttempted(true);
          void handleUseMyLocation(true);
        }
      }).catch(() => {/* noop */});
    }
  }, [autoAttempted, postalCode]);

  const reverseGeocodePostal = async (lat: number, lon: number): Promise<string | null> => {
    // Try BigDataCloud first, then fall back to OpenStreetMap Nominatim
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 7000);
    try {
      const url = `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${encodeURIComponent(lat)}&longitude=${encodeURIComponent(lon)}&localityLanguage=en`;
      const res = await fetch(url, { signal: controller.signal });
      if (res.ok) {
        const data: any = await res.json();
        const candidates: Array<any> = [
          data.postcode,
          data.postalCode,
          data?.localityInfo?.administrative?.find?.((x: any) => /postal|zip/i.test(x.description || ''))?.name,
          data?.localityInfo?.informative?.find?.((x: any) => /postal|zip/i.test(x.description || ''))?.name
        ];
        const raw = candidates.find(Boolean) || null;
        if (raw) {
          const normalized = serviceAreasApi.normalizePostalCode(String(raw), resolvedCountryCode);
          if (serviceAreasApi.validatePostalCode(normalized, resolvedCountryCode)) return normalized;
        }
      }
    } catch (_) {
      // ignore and try fallback
    } finally {
      clearTimeout(timeout);
    }

    // Fallback: OSM Nominatim
    try {
      const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&addressdetails=1`;
      const res = await fetch(url, {
        headers: { 'User-Agent': 'hero365-booking/1.0 (+https://hero365.app)' }
      });
      if (!res.ok) return null;
      const data: any = await res.json();
      const addr = data.address || {};
      const raw = addr.postcode || addr['postal_code'] || addr['zip'] || null;
      if (!raw) return null;
      const normalized = serviceAreasApi.normalizePostalCode(String(raw), resolvedCountryCode);
      return serviceAreasApi.validatePostalCode(normalized, resolvedCountryCode) ? normalized : null;
    } catch (_) {
      return null;
    }
  };

  const handleUseMyLocation = async (silent?: boolean) => {
    if (!('geolocation' in navigator)) {
      if (!silent) setError('Geolocation is not supported on this device');
      return;
    }
    setIsDetecting(true);
    setError();
    setCheckResult(null);

    const getPosition = () => new Promise<GeolocationPosition>((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: false,
        maximumAge: 5 * 60 * 1000,
        timeout: 8000
      });
    });

    try {
      const position = await getPosition();
      const { latitude, longitude } = position.coords;
      const detected = await reverseGeocodePostal(latitude, longitude);
      if (detected) {
        setPostalCode(detected);
        // Run check using the freshly detected value to avoid stale state
        await checkServiceArea(detected);
      } else if (!silent) {
        setError('Unable to detect postal code from your location');
      }
    } catch (err: any) {
      if (!silent) {
        const message = err?.code === 1
          ? 'Location permission denied'
          : 'Unable to access your location';
        setError(message);
      }
    } finally {
      setIsDetecting(false);
    }
  };

  const handlePostalCodeChange = (value: string) => {
    setPostalCode(value.toUpperCase());
    setCheckResult(null);
    setError();
  };

  const checkServiceArea = async (overridePostal?: string) => {
    const code = (overridePostal ?? postalCode).trim();
    if (!code) {
      setError('Please enter a postal code');
      return;
    }

    // Validate postal code format
    if (!serviceAreasApi.validatePostalCode(code, resolvedCountryCode)) {
      setError(`Please enter a valid ${serviceAreasApi.getPostalCodeLabel(resolvedCountryCode).toLowerCase()}`);
      return;
    }

    setIsChecking(true);
    setLoading(true);
    setError();

    const normalizedPostalCode = serviceAreasApi.normalizePostalCode(code, resolvedCountryCode);

    try {
      const result = await serviceAreasApi.checkServiceAreaSupport({
        business_id: businessId,
        postal_code: normalizedPostalCode,
        country_code: resolvedCountryCode
      });

      // Track ZIP validation analytics
      analytics.trackZipValidation(
        normalizedPostalCode, 
        resolvedCountryCode, 
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
        setCheckResult(null); // do not render success card
        nextStep();
      } else {
        setCheckResult(result);
        updateZipInfo({
          postalCode: normalizedPostalCode,
          countryCode: resolvedCountryCode,
          timezone: 'America/New_York', // Default
          supported: false
        });
      }

    } catch (error) {
      // Graceful fallback on server errors: treat as unsupported instead of hard error
      console.error('Error checking service area:', error);
      setCheckResult({ supported: false });
      updateZipInfo({
        postalCode: normalizedPostalCode,
        countryCode: resolvedCountryCode,
        timezone: 'America/New_York',
        supported: false
      });
      // Do not set a blocking error banner; the UI will show the unsupported card
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
          Enter your {serviceAreasApi.getPostalCodeLabel(resolvedCountryCode).toLowerCase()} so we can check if we provide service in your area
        </p>
      </div>

      {/* Input Form */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {serviceAreasApi.getPostalCodeLabel(resolvedCountryCode)} *
              </label>
              <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-3 space-y-3 sm:space-y-0">
                <Input
                  value={postalCode}
                  onChange={(e) => handlePostalCodeChange(e.target.value)}
                  placeholder={serviceAreasApi.getPostalCodePlaceholder(resolvedCountryCode)}
                  className="flex-1"
                  maxLength={10}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      checkServiceArea();
                    }
                  }}
                />
                <div className="flex items-center space-x-2">
                  <Button
                    onClick={() => checkServiceArea()}
                    disabled={!postalCode.trim() || isChecking}
                    className="px-6"
                  >
                    {isChecking ? 'Checking...' : 'Check'}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => handleUseMyLocation(false)}
                    disabled={isDetecting}
                  >
                    {isDetecting ? (
                      <span className="inline-flex items-center"><span className="w-4 h-4 mr-2 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></span>Detecting</span>
                    ) : (
                      'Use my location'
                    )}
                  </Button>
                </div>
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
