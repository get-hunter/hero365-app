/**
 * Trade Service Step (Step 2)
 * 
 * Two-phase selection:
 * 1. Select trade category (HVAC, Plumbing, Electrical, etc.)
 * 2. Select specific service within that trade
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { ChevronRight, CheckCircle, ArrowLeft } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useBookingWizard } from '../Hero365BookingContext';

// Icon mapping for trade icons
const ICON_MAP = {
  'thermometer': '🌡️',
  'wrench': '🔧',
  'zap': '⚡',
  'droplets': '💧',
  'wind': '💨',
  'shield': '🛡️',
  'scissors': '✂️',
  'home': '🏠',
  'coffee': '☕',
  'hammer': '🔨',
  'waves': '🌊'
} as const;

interface BookingService {
  id: string;
  service_id: string;
  name: string;
  description?: string;
  base_price?: number;
  estimated_duration_minutes?: number;
  is_bookable: boolean;
  service_type_code?: string;
  service_type_display_name?: string;
}

interface BookingTrade {
  trade_slug: string;
  trade_display_name: string;
  trade_icon: string;
  trade_color: string;
  market_type: string;
  service_count: number;
  services: BookingService[];
}

interface BookingTradesResponse {
  trades: BookingTrade[];
  total_services: number;
}

interface TradeServiceStepProps {
  businessId: string;
}

export default function TradeServiceStep({ businessId }: TradeServiceStepProps) {
  const { state, updateService, nextStep, prevStep, setLoading, setError } = useBookingWizard();
  
  const [tradesData, setTradesData] = useState<BookingTradesResponse | null>(null);
  const [selectedTrade, setSelectedTrade] = useState<string>(state.categoryId || '');
  const [selectedServiceId, setSelectedServiceId] = useState<string>(state.serviceId || '');
  const [isLoadingTrades, setIsLoadingTrades] = useState(true);
  const servicesSectionRef = useRef<HTMLDivElement>(null);

  const locationLabel = state.zipInfo
    ? `${state.zipInfo.city || ''}${state.zipInfo.city ? ', ' : ''}${state.zipInfo.region || ''} ${state.zipInfo.postalCode}`.trim()
    : '';

  // Load trades and services
  useEffect(() => {
    loadBookingTrades();
  }, [businessId]);

  const loadBookingTrades = async () => {
    try {
      setIsLoadingTrades(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/public/contractors/${businessId}/booking-trades`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to load trades: ${response.status}`);
      }
      
      const data: BookingTradesResponse = await response.json();
      setTradesData(data);
      
      // If we have a previously selected trade, validate it still exists
      if (selectedTrade && !data.trades.find(t => t.trade_slug === selectedTrade)) {
        setSelectedTrade('');
        setSelectedServiceId('');
      }
      
    } catch (error) {
      console.error('Error loading booking trades:', error);
      setError('Failed to load available services. Please try again.');
    } finally {
      setIsLoadingTrades(false);
    }
  };

  const handleTradeSelect = (tradeSlug: string) => {
    setSelectedTrade(tradeSlug);
    setSelectedServiceId(''); // Reset service selection when trade changes
    // After selecting a trade, scroll services section into view
    setTimeout(() => {
      servicesSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 0);
  };

  const handleServiceSelect = (serviceId: string) => {
    setSelectedServiceId(serviceId);
  };

  const handleContinue = () => {
    if (selectedTrade && selectedServiceId) {
      updateService(selectedTrade, selectedServiceId);
      nextStep();
    }
  };


  const formatDuration = (minutes?: number) => {
    if (!minutes) return null;
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    if (h && m) return `${h}h ${m}m`;
    if (h) return `${h}h`;
    return `${m}m`;
  };

  const formatPrice = (price?: number) => {
    if (typeof price !== 'number') return null;
    return `$${price.toLocaleString()}`;
  };

  const getTradeIcon = (iconName: string) => {
    return ICON_MAP[iconName as keyof typeof ICON_MAP] || '🔧';
  };

  const selectedTradeData = tradesData?.trades.find(t => t.trade_slug === selectedTrade);
  const selectedService = selectedTradeData?.services.find(s => s.id === selectedServiceId);

  if (isLoadingTrades) {
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading available services...</p>
        </div>
      </div>
    );
  }

  if (!tradesData || tradesData.trades.length === 0) {
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        <div className="text-center">
          <p className="text-gray-600">No services available for booking at this time.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
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
        {locationLabel && (
          <div className="inline-flex items-center px-3 py-1 mb-3 text-sm rounded-full bg-blue-50 border border-blue-200 text-blue-800">
            <span className="w-2 h-2 rounded-full bg-blue-500 mr-2" />
            Service area: {locationLabel}
          </div>
        )}
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          What type of service do you need?
        </h1>
        <p className="text-gray-600">
          {!selectedTrade 
            ? 'Select the category that best matches your needs'
            : 'Now choose the specific service you need'
          }
        </p>
      </div>

      {/* Trade Categories (always visible) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tradesData.trades.map((trade) => {
          const isSelected = selectedTrade === trade.trade_slug;
          
          return (
            <Card
              key={trade.trade_slug}
              className={`cursor-pointer transition-all duration-200 hover:shadow-md border-2 ${
                isSelected 
                  ? 'border-blue-400 ring-2 ring-blue-100 bg-blue-50' 
                  : 'border-gray-200 hover:border-blue-400'
              }`}
              onClick={() => handleTradeSelect(trade.trade_slug)}
            >
              <CardContent className="p-6 text-center">
                <div 
                  className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center text-2xl"
                  style={{ backgroundColor: `${trade.trade_color}20`, border: `2px solid ${trade.trade_color}` }}
                >
                  {getTradeIcon(trade.trade_icon)}
                </div>
                <h3 className="font-semibold text-lg text-gray-900 mb-2">
                  {trade.trade_display_name}
                </h3>
                <Badge variant="outline" className="mb-2">
                  {trade.service_count} service{trade.service_count !== 1 ? 's' : ''}
                </Badge>
                {isSelected && (
                  <div className="flex items-center justify-center text-blue-600">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    <span className="text-sm font-medium">Selected</span>
                  </div>
                )}
                {!isSelected && (
                  <div className="flex items-center justify-center text-blue-600">
                    <span className="text-sm">Select category</span>
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Services within selected trade (shown below trade categories) */}
      {selectedTrade && selectedTradeData && (
        <div ref={servicesSectionRef} className="space-y-4 pt-6 border-t border-gray-200">
          {/* Services grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {selectedTradeData.services.map((service) => {
              const isSelected = selectedServiceId === service.id;
              const duration = formatDuration(service.estimated_duration_minutes);
              const price = formatPrice(service.base_price);

              return (
                <Card
                  key={service.id}
                  className={`cursor-pointer transition-all duration-200 hover:shadow-md border-2 ${
                    isSelected 
                      ? 'border-blue-400 ring-2 ring-blue-100 bg-blue-50' 
                      : 'border-gray-200 hover:border-blue-300'
                  }`}
                  onClick={() => handleServiceSelect(service.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-semibold text-gray-900">{service.name}</h3>
                          {isSelected && (
                            <CheckCircle className="w-5 h-5 text-blue-600" />
                          )}
                        </div>
                        
                        {service.description && (
                          <p className="text-sm text-gray-600 mb-3">{service.description}</p>
                        )}
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          {duration && (
                            <span className="flex items-center">
                              ⏱️ {duration}
                            </span>
                          )}
                          {price && (
                            <span className="flex items-center font-medium text-gray-900">
                              💰 Starting at {price}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* Continue button */}
      {selectedServiceId && (
        <div className="flex justify-center pt-6">
          <Button
            onClick={handleContinue}
            size="lg"
            className="px-8 py-3"
          >
            Continue with {selectedService?.name}
            <ChevronRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      )}
    </div>
  );
}
