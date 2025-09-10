/**
 * Google Places Autocomplete Component
 * 
 * Provides address autocomplete functionality using Google Places API
 */

'use client';

import React, { useRef, useEffect, useState } from 'react';
import { Input } from '@/components/ui/input';

interface GooglePlacesAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onPlaceSelect?: (place: google.maps.places.PlaceResult) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  autoFocus?: boolean;
}

interface ParsedAddress {
  line1: string;
  city: string;
  region: string;
  postalCode: string;
  countryCode: string;
}

export default function GooglePlacesAutocomplete({
  value,
  onChange,
  onPlaceSelect,
  placeholder = "Enter your address",
  className = "",
  disabled = false,
  autoFocus = false
}: GooglePlacesAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);
  const placeElContainerRef = useRef<HTMLDivElement>(null);
  const placeElementRef = useRef<any>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [usingPlaceElement, setUsingPlaceElement] = useState(false);

  // Load Google Maps API
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Check if already loaded
      if (window.google?.maps?.places) {
        // Ensure places lib is ready (importLibrary is idempotent)
        const importPlaces = (window.google as any)?.maps?.importLibrary;
        if (importPlaces) {
          importPlaces('places').then(() => setIsLoaded(true));
        } else {
          setIsLoaded(true);
        }
        return;
      }
      
      // Check if script is already being loaded
      const existingScript = document.querySelector('script[src*="maps.googleapis.com"]');
      if (existingScript) {
        const handleLoad = () => {
          const importPlaces = (window.google as any)?.maps?.importLibrary;
          if (importPlaces) {
            importPlaces('places').then(() => setIsLoaded(true));
          } else if (window.google?.maps?.places) {
            setIsLoaded(true);
          }
        };
        existingScript.addEventListener('load', handleLoad);
        return () => existingScript.removeEventListener('load', handleLoad);
      }
      
      // Load API if not present
      loadGoogleMapsAPI();
    }
  }, []);

  // Initialize autocomplete when API is loaded
  useEffect(() => {
    if (!isLoaded) return;
    if (autocompleteRef.current || placeElementRef.current) return;
    initializeAutocomplete();

    return () => {
      if (autocompleteRef.current) {
        google.maps.event.clearInstanceListeners(autocompleteRef.current);
      }
      if (placeElementRef.current && placeElContainerRef.current) {
        // Detach and cleanup custom element
        try {
          placeElContainerRef.current.removeChild(placeElementRef.current);
        } catch {}
        placeElementRef.current = null;
      }
    };
  }, [isLoaded]);

  const loadGoogleMapsAPI = () => {
    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
    
    if (!apiKey) {
      console.error('Google Maps API key not found');
      return;
    }

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&loading=async`;
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      const importPlaces = (window.google as any)?.maps?.importLibrary;
      if (importPlaces) {
        importPlaces('places').then(() => setIsLoaded(true));
      } else {
        setIsLoaded(true);
      }
    };
    
    script.onerror = () => {
      console.error('Failed to load Google Maps API');
    };

    document.head.appendChild(script);
  };

  const initializeAutocomplete = () => {
    if (!inputRef.current) return;

    const placesLib: any = (google as any)?.maps?.places;
    if (!placesLib) return;

    // Prefer new PlaceAutocompleteElement if classic Autocomplete is unavailable
    if (!placesLib.Autocomplete && placesLib.PlaceAutocompleteElement && placeElContainerRef.current) {
      setUsingPlaceElement(true);
      const el = new placesLib.PlaceAutocompleteElement();
      // Basic attributes
      try {
        if (typeof placeholder === 'string') el.setAttribute('placeholder', placeholder);
        if (disabled) el.setAttribute('disabled', 'true');
        if (value) (el as any).value = value;
      } catch {}

      // Handle selection
      el.addEventListener('gmp-placeselect', async (evt: any) => {
        try {
          const place = evt?.detail?.place;
          if (place?.fetchFields) {
            await place.fetchFields({ fields: ['formattedAddress', 'addressComponents'] });
          }

          // Update display value
          const formatted = place?.formattedAddress || (el as any).value || '';
          if (formatted) onChange(formatted);

          if (onPlaceSelect) {
            // Convert to legacy-like PlaceResult shape expected by callers
            const addressComponents = (place?.addressComponents || []).map((c: any) => ({
              long_name: c.longText,
              short_name: c.shortText,
              types: c.types || []
            }));

            const legacyLike: any = {
              formatted_address: formatted,
              address_components: addressComponents
            };
            onPlaceSelect(legacyLike as google.maps.places.PlaceResult);
          }
        } catch {}
      });

      placeElementRef.current = el;
      placeElContainerRef.current.appendChild(el);
      if (autoFocus) {
        try { (el as any).focus?.(); } catch {}
      }
      return;
    }

    // Fallback to classic Autocomplete when available
    if (placesLib.Autocomplete) {
      const autocomplete = new placesLib.Autocomplete(inputRef.current, {
        types: ['address'],
        componentRestrictions: { country: ['us', 'ca'] },
        fields: [
          'address_components',
          'formatted_address',
          'geometry',
          'name',
          'place_id'
        ]
      });

      autocompleteRef.current = autocomplete;

      if (autoFocus) {
        try { inputRef.current?.focus(); } catch {}
      }

      autocomplete.addListener('place_changed', () => {
        const place = autocomplete.getPlace();
        if (place?.formatted_address) {
          onChange(place.formatted_address);
        }
        if (onPlaceSelect && place?.address_components) {
          onPlaceSelect(place);
        }
      });
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  return (
    <div className="relative">
      <div ref={placeElContainerRef} className={`${usingPlaceElement ? '' : 'hidden'} ${className}`} />
      {!usingPlaceElement && (
        <Input
          ref={inputRef}
          value={value}
          onChange={handleInputChange}
          placeholder={placeholder}
          className={className}
          disabled={disabled}
          autoComplete="off"
        />
      )}
      {!isLoaded && (
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
          <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
        </div>
      )}
    </div>
  );
}

// Utility function to parse Google Places result into our Address format
export function parseGooglePlaceResult(place: google.maps.places.PlaceResult): Partial<ParsedAddress> {
  const components = place.address_components || [];
  const result: Partial<ParsedAddress> = {};

  // Extract address components
  let streetNumber = '';
  let streetName = '';

  components.forEach((component) => {
    const types = component.types;
    
    if (types.includes('street_number')) {
      streetNumber = component.long_name;
    } else if (types.includes('route')) {
      streetName = component.long_name;
    } else if (types.includes('locality')) {
      result.city = component.long_name;
    } else if (types.includes('administrative_area_level_1')) {
      result.region = component.short_name; // State abbreviation
    } else if (types.includes('postal_code')) {
      result.postalCode = component.long_name;
    } else if (types.includes('country')) {
      result.countryCode = component.short_name;
    }
  });

  // Combine street number and name
  if (streetNumber && streetName) {
    result.line1 = `${streetNumber} ${streetName}`;
  } else if (streetName) {
    result.line1 = streetName;
  }

  return result;
}
