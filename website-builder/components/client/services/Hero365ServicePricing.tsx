/**
 * Service Pricing Table Component
 * 
 * Professional pricing display inspired by elite service companies
 * Features member pricing, "from" pricing model, and detailed service descriptions
 */

'use client';

import React from 'react';
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle, Star, Clock, Shield, Phone } from 'lucide-react';
import { ServicePricing } from '@/lib/shared/types/membership';
import { cn } from '@/lib/shared/utils';

interface ServicePricingTableProps {
  services: ServicePricing[];
  category: string;
  showMemberPricing?: boolean;
  selectedMembershipType?: 'residential' | 'commercial' | 'premium';
  onServiceSelect?: (service: ServicePricing) => void;
  onBookNow?: (service: ServicePricing) => void;
  className?: string;
}

export default function ServicePricingTable({
  services,
  category,
  showMemberPricing = true,
  selectedMembershipType = 'residential',
  onServiceSelect,
  onBookNow,
  className
}: ServicePricingTableProps) {
  
  const getMemberPrice = (service: ServicePricing) => {
    switch (selectedMembershipType) {
      case 'commercial':
        return service.commercial_member_price;
      case 'premium':
        return service.premium_member_price;
      default:
        return service.residential_member_price;
    }
  };

  const formatPrice = (price: number | null | undefined, display: ServicePricing['price_display']) => {
    if (price === null || price === undefined) return 'Quote Required';
    if (price === 0) return 'FREE';
    if (display === 'quote_required') return 'Quote Required';
    if (display === 'free') return 'FREE';
    
    const formattedPrice = price.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
    
    return display === 'from' ? `from ${formattedPrice}` : formattedPrice;
  };

  const calculateSavings = (basePrice: number | null | undefined, memberPrice?: number | null) => {
    if (!basePrice || !memberPrice || memberPrice >= basePrice) return 0;
    return basePrice - memberPrice;
  };

  return (
    <div className={cn("w-full", className)}>
      {/* Category Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{category}</h2>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Shield className="h-4 w-4 text-blue-600" />
          <span>Our Policy: "NO satisfaction – NO charge"</span>
        </div>
      </div>

      {/* Pricing Table */}
      <div className="overflow-x-auto bg-white rounded-lg shadow-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="text-left py-4 px-6 font-semibold text-gray-900">
                Type of Service
              </th>
              <th className="text-left py-4 px-6 font-semibold text-gray-900">
                Price (Average)
              </th>
              {showMemberPricing && (
                <th className="text-left py-4 px-6 font-semibold text-blue-600">
                  Member Price
                </th>
              )}
              <th className="text-center py-4 px-6 font-semibold text-gray-900">
                Action
              </th>
            </tr>
          </thead>
          <tbody>
            {services.map((service, index) => {
              const memberPrice = getMemberPrice(service);
              const savings = calculateSavings(service.base_price, memberPrice);
              const hasSavings = showMemberPricing && savings > 0;

              return (
                <tr 
                  key={service.id}
                  className={cn(
                    "border-b border-gray-100 hover:bg-gray-50 transition-colors",
                    index % 2 === 0 ? "bg-white" : "bg-gray-50/50"
                  )}
                >
                  {/* Service Name & Description */}
                  <td className="py-4 px-6">
                    <div className="space-y-1">
                      <div className="flex items-start justify-between">
                        <h3 className="font-medium text-gray-900 text-sm leading-tight">
                          {service.service_name}
                        </h3>
                        {service.price_display === 'free' && (
                          <Badge variant="secondary" className="ml-2 bg-green-100 text-green-800">
                            FREE
                          </Badge>
                        )}
                      </div>
                      
                      {service.description && (
                        <p className="text-xs text-gray-600 leading-tight">
                          {service.description}
                        </p>
                      )}
                      
                      {service.includes && service.includes.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {service.includes.slice(0, 2).map((include, idx) => (
                            <span key={idx} className="inline-flex items-center text-xs text-blue-600">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              {include}
                            </span>
                          ))}
                          {service.includes.length > 2 && (
                            <span className="text-xs text-gray-500">
                              +{service.includes.length - 2} more
                            </span>
                          )}
                        </div>
                      )}
                      
                      {service.duration_estimate && (
                        <div className="flex items-center text-xs text-gray-500 mt-1">
                          <Clock className="h-3 w-3 mr-1" />
                          {service.duration_estimate}
                        </div>
                      )}
                    </div>
                  </td>

                  {/* Regular Price */}
                  <td className="py-4 px-6">
                    <div className="text-sm">
                      <span className={cn(
                        "font-semibold",
                        service.price_display === 'free' ? "text-green-600" : 
                        hasSavings ? "text-gray-500 line-through" : "text-gray-900"
                      )}>
                        {formatPrice(service.base_price, service.price_display)}
                      </span>
                      
                      {service.minimum_labor_fee && service.base_price && service.base_price > 0 && (
                        <div className="text-xs text-gray-500 mt-1">
                          Minimum labor fee: ${service.minimum_labor_fee}
                        </div>
                      )}
                      
                      {service.parts_separate && (
                        <div className="text-xs text-orange-600 mt-1">
                          Parts separate
                        </div>
                      )}
                      
                      {service.height_surcharge && (
                        <div className="text-xs text-gray-500 mt-1">
                          Height surcharge may apply
                        </div>
                      )}
                    </div>
                  </td>

                  {/* Member Price */}
                  {showMemberPricing && (
                    <td className="py-4 px-6">
                      {memberPrice !== undefined ? (
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Star className="h-4 w-4 text-blue-600" />
                            <span className="font-semibold text-blue-600 text-sm">
                              {formatPrice(memberPrice, service.price_display)}
                            </span>
                          </div>
                          {savings > 0 && (
                            <div className="text-xs text-green-600 font-medium">
                              Save ${savings.toLocaleString()}
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="text-xs text-gray-500">Member rate applies</span>
                      )}
                    </td>
                  )}

                  {/* Actions */}
                  <td className="py-4 px-6 text-center">
                    <div className="flex gap-2 justify-center">
                      {service.price_display === 'free' ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => onServiceSelect?.(service)}
                          className="text-xs px-3 py-1"
                        >
                          Get Estimate
                        </Button>
                      ) : (
                        <>
                          <Button
                            size="sm"
                            onClick={() => onBookNow?.(service)}
                            className="text-xs px-3 py-1 bg-blue-600 hover:bg-blue-700"
                          >
                            Book Now
                          </Button>
                          {service.base_price > 1000 && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => onServiceSelect?.(service)}
                              className="text-xs px-2 py-1"
                            >
                              <Phone className="h-3 w-3" />
                            </Button>
                          )}
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Footer Notes */}
      <div className="mt-4 space-y-2 text-xs text-gray-600">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <h4 className="font-medium text-yellow-800 mb-2">Important Notes:</h4>
          <ul className="space-y-1 text-yellow-700">
            <li>• Sometimes repair requires two or three technicians (additional fee applies)</li>
            <li>• Jobs higher than 3½ ft will cost 1.5x coefficient</li>
            <li>• All prices for labor don't include parts, discounts and coupons</li>
            <li>• Prices are tentative and may change during work performance</li>
          </ul>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-center gap-2 text-blue-800">
            <CheckCircle className="h-4 w-4" />
            <span className="font-medium">
              In 70-80% of cases, breakdowns are minor and charge will be about $199
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
