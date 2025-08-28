'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Check, 
  Star, 
  Crown, 
  Shield, 
  Clock, 
  Wrench,
  Phone,
  AlertCircle
} from 'lucide-react';

interface MembershipPlan {
  id: string;
  name: string;
  plan_type: 'residential' | 'commercial' | 'premium';
  description: string;
  tagline: string;
  price_monthly: number;
  price_yearly: number;
  yearly_savings: number;
  discount_percentage: number;
  priority_service: boolean;
  extended_warranty: boolean;
  maintenance_included: boolean;
  emergency_response: boolean;
  free_diagnostics: boolean;
  annual_tune_ups: number;
  is_featured: boolean;
  popular_badge?: string;
  color_scheme: string;
}

interface PricingBreakdown {
  product_unit_price: number;
  installation_base_price: number;
  subtotal_before_discounts: number;
  product_discount_amount: number;
  installation_discount_amount: number;
  total_discount_amount: number;
  subtotal_after_discounts: number;
  total_amount: number;
  total_savings: number;
  savings_percentage: number;
  membership_type?: string;
}

interface MembershipPricingDisplayProps {
  productPrice: number;
  installationPrice: number;
  membershipPlans: MembershipPlan[];
  onMembershipSelect?: (planType: string | null) => void;
  selectedMembership?: string | null;
  className?: string;
}

export default function MembershipPricingDisplay({
  productPrice,
  installationPrice,
  membershipPlans,
  onMembershipSelect,
  selectedMembership,
  className = ''
}: MembershipPricingDisplayProps) {
  const [showDetails, setShowDetails] = useState(false);

  // Calculate pricing for each membership level
  const calculatePricing = (discountPercentage: number): PricingBreakdown => {
    const subtotalBeforeDiscounts = productPrice + installationPrice;
    const productDiscount = productPrice * (discountPercentage / 100);
    const installationDiscount = installationPrice * (discountPercentage / 100);
    const totalDiscount = productDiscount + installationDiscount;
    const subtotalAfterDiscounts = subtotalBeforeDiscounts - totalDiscount;
    
    return {
      product_unit_price: productPrice,
      installation_base_price: installationPrice,
      subtotal_before_discounts: subtotalBeforeDiscounts,
      product_discount_amount: productDiscount,
      installation_discount_amount: installationDiscount,
      total_discount_amount: totalDiscount,
      subtotal_after_discounts: subtotalAfterDiscounts,
      total_amount: subtotalAfterDiscounts,
      total_savings: totalDiscount,
      savings_percentage: (totalDiscount / subtotalBeforeDiscounts) * 100
    };
  };

  const regularPricing = calculatePricing(0);

  const getPlanIcon = (planType: string) => {
    switch (planType) {
      case 'residential':
        return <Shield className="w-5 h-5" />;
      case 'commercial':
        return <Star className="w-5 h-5" />;
      case 'premium':
        return <Crown className="w-5 h-5" />;
      default:
        return <Check className="w-5 h-5" />;
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  if (!membershipPlans || membershipPlans.length === 0) return null;

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Membership Plans Overview */}
      <Card className="border border-blue-100 bg-blue-50/60">
        <CardHeader className="py-3">
          <CardTitle className="flex items-center gap-2 text-blue-800 text-base">
            <Star className="w-4 h-4" />
            Member Exclusive Pricing
          </CardTitle>
          <p className="text-blue-700 text-xs">
            Join our membership program for instant savings on products and installation
          </p>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4 items-stretch">
            {/* Regular Pricing */}
            <div className={`p-3 rounded-lg border ${
              selectedMembership === null 
                ? 'border-gray-300 bg-gray-50' 
                : 'border-gray-200 bg-white hover:border-gray-300'
            } transition-all cursor-pointer h-full`}
            onClick={() => onMembershipSelect?.(null)}>
              <div className="text-center">
                <h4 className="font-medium text-gray-800 mb-1 text-sm">Regular Price</h4>
                <div className="text-xl font-semibold text-gray-900 mb-1">
                  {formatPrice(regularPricing.total_amount)}
                </div>
                <p className="text-xs text-gray-600">No membership required</p>
                {selectedMembership === null && (
                  <Badge variant="secondary" className="mt-2 text-[10px]">Selected</Badge>
                )}
              </div>
            </div>

            {/* Membership Plans */}
            {membershipPlans.map((plan) => {
              const pricing = calculatePricing(plan.discount_percentage);
              const isSelected = selectedMembership === plan.plan_type;
              
              return (
                <div
                  key={plan.id}
                  className={`p-3 rounded-lg border ${
                    isSelected 
                      ? 'border-blue-400 bg-blue-50 shadow-sm' 
                      : 'border-gray-200 bg-white hover:border-blue-300'
                  } transition-all cursor-pointer relative h-full`}
                  onClick={() => onMembershipSelect?.(plan.plan_type)}
                  style={{ borderColor: isSelected ? plan.color_scheme : undefined }}
                >
                  {plan.popular_badge && (
                    <Badge 
                      className="absolute -top-2 left-1/2 transform -translate-x-1/2 text-[10px]"
                      style={{ backgroundColor: plan.color_scheme }}
                    >
                      {plan.popular_badge}
                    </Badge>
                  )}
                  
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-2 mb-1">
                      {getPlanIcon(plan.plan_type)}
                      <h4 className="font-medium text-gray-800 text-sm">{plan.name}</h4>
                    </div>
                    
                    <div className="mb-1">
                      <div className="text-lg font-bold" style={{ color: plan.color_scheme }}>
                        {formatPrice(pricing.total_amount)}
                      </div>
                      <div className="text-xs text-gray-500 line-through">
                        {formatPrice(regularPricing.total_amount)}
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      <Badge 
                        variant="secondary" 
                        className="text-[10px]"
                        style={{ backgroundColor: `${plan.color_scheme}20`, color: plan.color_scheme }}
                      >
                        Save {formatPrice(pricing.total_savings)} ({plan.discount_percentage}% off)
                      </Badge>
                      <p className="text-[11px] text-gray-600">{plan.tagline}</p>
                    </div>
                    
                    {isSelected && (
                      <Badge variant="default" className="mt-2 text-[10px]" style={{ backgroundColor: plan.color_scheme }}>
                        Selected
                      </Badge>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Membership Benefits Toggle */}
          <div className="mt-4 text-center">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowDetails(!showDetails)}
              className="text-blue-600 border-blue-200 hover:bg-blue-50"
            >
              {showDetails ? 'Hide' : 'Show'} Membership Benefits
              <AlertCircle className="w-4 h-4 ml-2" />
            </Button>
          </div>

          {/* Detailed Benefits */}
          {showDetails && (
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {membershipPlans.map((plan) => (
                <Card key={plan.id} className="border" style={{ borderColor: `${plan.color_scheme}40` }}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base flex items-center gap-2">
                      {getPlanIcon(plan.plan_type)}
                      {plan.name}
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium" style={{ color: plan.color_scheme }}>
                        {formatPrice(plan.price_monthly)}/month
                      </span>
                      <span className="text-[11px] text-gray-500">
                        or {formatPrice(plan.price_yearly)}/year
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <ul className="space-y-2 text-xs">
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-green-500" />
                        {plan.discount_percentage}% off all services
                      </li>
                      {plan.priority_service && (
                        <li className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-blue-500" />
                          Priority scheduling
                        </li>
                      )}
                      {plan.free_diagnostics && (
                        <li className="flex items-center gap-2">
                          <Wrench className="w-4 h-4 text-orange-500" />
                          Free diagnostics
                        </li>
                      )}
                      {plan.emergency_response && (
                        <li className="flex items-center gap-2">
                          <Phone className="w-4 h-4 text-red-500" />
                          24/7 emergency response
                        </li>
                      )}
                      {plan.annual_tune_ups > 0 && (
                        <li className="flex items-center gap-2">
                          <Check className="w-4 h-4 text-green-500" />
                          {plan.annual_tune_ups} annual tune-ups
                        </li>
                      )}
                      {plan.extended_warranty && (
                        <li className="flex items-center gap-2">
                          <Shield className="w-4 h-4 text-purple-500" />
                          Extended warranty
                        </li>
                      )}
                    </ul>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Selected Pricing Breakdown */}
      {selectedMembership && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader className="py-3">
            <CardTitle className="text-green-800 flex items-center gap-2 text-base">
              <Check className="w-5 h-5" />
              Your Membership Savings
            </CardTitle>
          </CardHeader>
          <CardContent>
            {(() => {
              const selectedPlan = membershipPlans.find(p => p.plan_type === selectedMembership);
              if (!selectedPlan) return null;
              
              const pricing = calculatePricing(selectedPlan.discount_percentage);
              
              return (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 text-sm">Product Price:</span>
                    <span className="font-medium text-sm">{formatPrice(pricing.product_unit_price)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 text-sm">Installation Price:</span>
                    <span className="font-medium text-sm">{formatPrice(pricing.installation_base_price)}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm border-t pt-2">
                    <span className="text-gray-600">Subtotal:</span>
                    <span>{formatPrice(pricing.subtotal_before_discounts)}</span>
                  </div>
                  <div className="flex justify-between items-center text-green-600">
                    <span className="text-sm">Member Discount ({selectedPlan.discount_percentage}%):</span>
                    <span className="text-sm">-{formatPrice(pricing.total_discount_amount)}</span>
                  </div>
                  <div className="flex justify-between items-center text-lg font-bold border-t pt-2">
                    <span>Your Price:</span>
                    <span className="text-green-600">{formatPrice(pricing.total_amount)}</span>
                  </div>
                  <div className="text-center text-sm text-green-600 font-medium">
                    You save {formatPrice(pricing.total_savings)} with {selectedPlan.name}!
                  </div>
                </div>
              );
            })()}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
