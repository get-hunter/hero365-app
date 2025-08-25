/**
 * Service Selector Component
 * 
 * Allows customers to select from available bookable services
 */

'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Clock, DollarSign, Users, CheckCircle } from 'lucide-react';
import { cn } from '../../lib/utils';

import { ServiceSelectorProps, BookableService } from '../../lib/types/booking';

export default function ServiceSelector({
  services,
  selectedServiceId,
  onServiceSelect,
  className
}: ServiceSelectorProps) {
  
  const formatDuration = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    if (remainingMinutes === 0) {
      return `${hours} hr${hours > 1 ? 's' : ''}`;
    }
    return `${hours}h ${remainingMinutes}m`;
  };

  const formatPrice = (price: number, priceType: string): string => {
    const formatted = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
    
    switch (priceType) {
      case 'hourly':
        return `${formatted}/hr`;
      case 'estimate':
        return `From ${formatted}`;
      default:
        return formatted;
    }
  };

  const getServiceIcon = (category?: string) => {
    // You can expand this mapping based on your service categories
    const iconMap: { [key: string]: string } = {
      hvac: '🌡️',
      plumbing: '🔧',
      electrical: '⚡',
      roofing: '🏠',
      security: '🔒',
      landscaping: '🌿',
    };
    
    return iconMap[category?.toLowerCase() || ''] || '🔧';
  };

  if (services.length === 0) {
    return (
      <div className={cn("text-center py-12", className)}>
        <div className="text-gray-500 mb-4">
          <Clock className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p className="text-lg">No services available for booking</p>
          <p className="text-sm">Please contact us directly to schedule an appointment.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Select a Service</h3>
        <p className="text-gray-600">Choose the service you need to get started with booking your appointment.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {services.map((service) => (
          <Card
            key={service.id}
            className={cn(
              "cursor-pointer transition-all duration-200 hover:shadow-lg",
              selectedServiceId === service.id
                ? "ring-2 ring-blue-500 border-blue-500 bg-blue-50"
                : "hover:border-gray-400"
            )}
            onClick={() => onServiceSelect(service.id)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="text-2xl">{getServiceIcon(service.category)}</div>
                  <div>
                    <CardTitle className="text-lg">{service.name}</CardTitle>
                    {service.category && (
                      <Badge variant="secondary" className="mt-1 text-xs">
                        {service.category}
                      </Badge>
                    )}
                  </div>
                </div>
                
                {selectedServiceId === service.id && (
                  <CheckCircle className="w-6 h-6 text-blue-500 flex-shrink-0" />
                )}
              </div>
            </CardHeader>

            <CardContent className="pt-0">
              {service.description && (
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {service.description}
                </p>
              )}

              <div className="space-y-2">
                {/* Duration */}
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="w-4 h-4" />
                  <span>{formatDuration(service.estimated_duration_minutes)}</span>
                  {service.min_duration_minutes && service.max_duration_minutes && (
                    <span className="text-xs text-gray-500">
                      ({formatDuration(service.min_duration_minutes)} - {formatDuration(service.max_duration_minutes)})
                    </span>
                  )}
                </div>

                {/* Price */}
                {service.base_price && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <DollarSign className="w-4 h-4" />
                    <span>{formatPrice(service.base_price, service.price_type)}</span>
                    {service.price_type === 'estimate' && (
                      <span className="text-xs text-gray-500">(Final price after inspection)</span>
                    )}
                  </div>
                )}

                {/* Technicians Required */}
                {service.min_technicians > 1 || service.max_technicians > 1 && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Users className="w-4 h-4" />
                    <span>
                      {service.min_technicians === service.max_technicians
                        ? `${service.min_technicians} technician${service.min_technicians > 1 ? 's' : ''}`
                        : `${service.min_technicians}-${service.max_technicians} technicians`
                      }
                    </span>
                  </div>
                )}

                {/* Site Visit Required */}
                {service.requires_site_visit && (
                  <div className="flex items-center gap-2 text-sm text-amber-600">
                    <div className="w-4 h-4 rounded-full bg-amber-100 flex items-center justify-center">
                      <div className="w-2 h-2 rounded-full bg-amber-500" />
                    </div>
                    <span>On-site service required</span>
                  </div>
                )}
              </div>

              {/* Lead Time Notice */}
              {service.min_lead_time_hours > 0 && (
                <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-800">
                  <strong>Notice:</strong> This service requires at least {service.min_lead_time_hours} hours advance notice.
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Service Information */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium mb-2">What to Expect</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• All technicians are licensed and insured</li>
          <li>• You'll receive confirmation within 2 hours</li>
          <li>• 24-hour reminder before your appointment</li>
          <li>• Satisfaction guarantee on all work</li>
        </ul>
      </div>
    </div>
  );
}
