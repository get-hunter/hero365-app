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
  disabled = false
}: GooglePlacesAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load Google Maps API
  useEffect(() => {
    if (typeof window !== 'undefined' && !window.google) {
      loadGoogleMapsAPI();
    } else if (window.google) {
      setIsLoaded(true);
    }
  }, []);

  // Initialize autocomplete when API is loaded
  useEffect(() => {
    if (isLoaded && inputRef.current && !autocompleteRef.current) {
      initializeAutocomplete();
    }

    return () => {
      if (autocompleteRef.current) {
        google.maps.event.clearInstanceListeners(autocompleteRef.current);
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
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      setIsLoaded(true);
    };
    
    script.onerror = () => {
      console.error('Failed to load Google Maps API');
    };

    document.head.appendChild(script);
  };

  const initializeAutocomplete = () => {
    if (!inputRef.current) return;

    const autocomplete = new google.maps.places.Autocomplete(inputRef.current, {
      types: ['address'],
      componentRestrictions: { country: ['us', 'ca'] }, // Restrict to US and Canada
      fields: [
        'address_components',
        'formatted_address',
        'geometry',
        'name',
        'place_id'
      ]
    });

    autocompleteRef.current = autocomplete;

    // Handle place selection
    autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace();
      
      if (place.formatted_address) {
        onChange(place.formatted_address);
      }

      if (onPlaceSelect && place.address_components) {
        onPlaceSelect(place);
      }
    });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  return (
    <div className="relative">
      <Input
        ref={inputRef}
        value={value}
        onChange={handleInputChange}
        placeholder={placeholder}
        className={className}
        disabled={disabled}
        autoComplete="off"
      />
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
