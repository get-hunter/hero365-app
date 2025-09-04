/**
 * Membership Plans Comparison Component
 * 
 * Professional membership display inspired by elite service companies
 * Features residential, commercial, and premium membership tiers
 */

'use client';

import React, { useState } from 'react';
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  CheckCircle, 
  Star, 
  Crown, 
  Zap, 
  Shield, 
  Phone, 
  Calendar,
  Percent,
  Clock,
  Award
} from 'lucide-react';
import { MembershipPlan } from '@/lib/shared/types/membership';
import { cn } from '@/lib/shared/utils';

interface MembershipPlansComparisonProps {
  plans: MembershipPlan[];
  selectedPlan?: string;
  onPlanSelect?: (planId: string) => void;
  onJoinNow?: (plan: MembershipPlan) => void;
  showAnnualSavings?: boolean;
  className?: string;
}

const iconMap = {
  'calendar-check': Calendar,
  'percent': Percent,
  'search': CheckCircle,
  'wrench': Award,
  'shield-check': Shield,
  'zap': Zap,
  'phone': Phone,
  'calendar': Calendar,
  'user-check': CheckCircle,
  'crown': Crown,
  'siren': Zap,
  'calendar-days': Calendar,
  'headphones': Phone,
  'cog': Award
};

export default function MembershipPlansComparison({
  plans,
  selectedPlan,
  onPlanSelect,
  onJoinNow,
  showAnnualSavings = true,
  className
}: MembershipPlansComparisonProps) {
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');

  const getIcon = (iconName: string) => {
    const IconComponent = iconMap[iconName as keyof typeof iconMap] || CheckCircle;
    return IconComponent;
  };

  const getPlanIcon = (type: string) => {
    switch (type) {
      case 'residential':
        return Shield;
      case 'commercial':
        return Zap;
      case 'premium':
        return Crown;
      default:
        return Shield;
    }
  };

  const getPlanColor = (type: string, isSelected: boolean) => {
    const baseColors = {
      residential: 'border-green-200 bg-green-50',
      commercial: 'border-blue-200 bg-blue-50',
      premium: 'border-purple-200 bg-purple-50'
    };
    
    const selectedColors = {
      residential: 'border-green-500 bg-green-100 shadow-lg',
      commercial: 'border-blue-500 bg-blue-100 shadow-lg', 
      premium: 'border-purple-500 bg-purple-100 shadow-lg'
    };
    
    return isSelected 
      ? selectedColors[type as keyof typeof selectedColors] 
      : baseColors[type as keyof typeof baseColors];
  };

  const formatPrice = (monthly?: number, yearly?: number) => {
    const price = billingPeriod === 'yearly' ? yearly : monthly;
    if (!price) return 'Contact Us';
    
    if (billingPeriod === 'yearly') {
      return `$${(price / 12).toFixed(0)}/mo`;
    }
    return `$${price}/mo`;
  };

  const getYearlySavings = (monthly?: number, yearly?: number) => {
    if (!monthly || !yearly) return 0;
    return (monthly * 12) - yearly;
  };

  // Sort plans: featured first, then by sort_order
  const sortedPlans = [...plans].sort((a, b) => {
    if (a.is_featured && !b.is_featured) return -1;
    if (!a.is_featured && b.is_featured) return 1;
    return a.sort_order - b.sort_order;
  });

  return (
    <div className={cn("w-full", className)}>
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Choose Your Membership Plan
        </h2>
        <p className="text-lg text-gray-600 mb-6">
          Get priority service, exclusive discounts, and peace of mind with our membership plans
        </p>
        
        {/* Billing Period Toggle */}
        {showAnnualSavings && (
          <div className="flex items-center justify-center space-x-4 mb-6">
            <span className="text-sm text-gray-600">Monthly</span>
            <button
              onClick={() => setBillingPeriod(billingPeriod === 'monthly' ? 'yearly' : 'monthly')}
              className={cn(
                "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                billingPeriod === 'yearly' ? "bg-blue-600" : "bg-gray-300"
              )}
            >
              <span className={cn(
                "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                billingPeriod === 'yearly' ? "translate-x-6" : "translate-x-1"
              )} />
            </button>
            <span className="text-sm text-gray-600">
              Annual
              <Badge variant="secondary" className="ml-2 bg-green-100 text-green-800">
                Save up to $300
              </Badge>
            </span>
          </div>
        )}
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {sortedPlans.map((plan) => {
          const isSelected = selectedPlan === plan.id;
          const PlanIcon = getPlanIcon(plan.type);
          const yearlySavings = getYearlySavings(plan.price_monthly, plan.price_yearly);

          return (
            <Card
              key={plan.id}
              className={cn(
                "relative cursor-pointer transition-all duration-200 hover:shadow-lg",
                getPlanColor(plan.type, isSelected),
                plan.is_featured && "ring-2 ring-blue-500 scale-105"
              )}
              onClick={() => onPlanSelect?.(plan.id)}
            >
              {plan.is_featured && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-blue-600 text-white px-3 py-1">
                    {plan.popular_badge || 'Most Popular'}
                  </Badge>
                </div>
              )}

              <CardHeader className="text-center pb-4">
                <div className="flex justify-center mb-3">
                  <div className={cn(
                    "p-3 rounded-full",
                    plan.type === 'residential' && "bg-green-100",
                    plan.type === 'commercial' && "bg-blue-100",
                    plan.type === 'premium' && "bg-purple-100"
                  )}>
                    <PlanIcon className={cn(
                      "h-8 w-8",
                      plan.type === 'residential' && "text-green-600",
                      plan.type === 'commercial' && "text-blue-600",
                      plan.type === 'premium' && "text-purple-600"
                    )} />
                  </div>
                </div>
                
                <CardTitle className="text-xl font-bold">
                  {plan.name}
                </CardTitle>
                
                <CardDescription className="text-sm">
                  {plan.tagline}
                </CardDescription>

                {/* Pricing */}
                <div className="py-4">
                  <div className="flex items-baseline justify-center">
                    <span className="text-3xl font-bold">
                      {formatPrice(plan.price_monthly, plan.price_yearly)}
                    </span>
                    {billingPeriod === 'yearly' && plan.price_yearly && (
                      <span className="text-sm text-gray-500 ml-1">
                        (billed annually)
                      </span>
                    )}
                  </div>
                  
                  {billingPeriod === 'yearly' && yearlySavings > 0 && (
                    <div className="text-sm text-green-600 font-medium mt-1">
                      Save ${yearlySavings}/year
                    </div>
                  )}
                </div>
              </CardHeader>

              <CardContent className="space-y-3">
                {/* Key Benefits */}
                <div className="space-y-2">
                  {plan.benefits
                    .filter(benefit => benefit.is_highlighted)
                    .slice(0, 3)
                    .map((benefit) => {
                    const BenefitIcon = getIcon(benefit.icon || 'check-circle');
                    return (
                      <div key={benefit.id} className="flex items-start space-x-3">
                        <BenefitIcon className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <span className="text-sm font-medium text-gray-900">
                            {benefit.title}
                          </span>
                          {benefit.value && (
                            <Badge variant="outline" className="ml-2 text-xs">
                              {benefit.value}
                            </Badge>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Additional Benefits */}
                <div className="pt-2 border-t border-gray-200">
                  <div className="text-xs text-gray-600 space-y-1">
                    {plan.benefits
                      .filter(benefit => !benefit.is_highlighted)
                      .slice(0, 3)
                      .map((benefit) => (
                      <div key={benefit.id} className="flex items-center space-x-2">
                        <CheckCircle className="h-3 w-3 text-gray-400" />
                        <span>{benefit.title}</span>
                      </div>
                    ))}
                    
                    {plan.benefits.length > 6 && (
                      <div className="text-blue-600 font-medium pt-1">
                        +{plan.benefits.length - 6} more benefits
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>

              <CardFooter className="pt-4">
                <Button
                  onClick={(e) => {
                    e.stopPropagation();
                    onJoinNow?.(plan);
                  }}
                  className={cn(
                    "w-full font-medium",
                    plan.type === 'residential' && "bg-green-600 hover:bg-green-700",
                    plan.type === 'commercial' && "bg-blue-600 hover:bg-blue-700",
                    plan.type === 'premium' && "bg-purple-600 hover:bg-purple-700"
                  )}
                  size="sm"
                >
                  Join Now
                </Button>
              </CardFooter>
            </Card>
          );
        })}
      </div>

      {/* Additional Info */}
      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Lower Prices with Membership
        </h3>
        <p className="text-gray-600 text-sm mb-4">
          All membership plans include priority service, extended warranties, and significant savings on repairs and maintenance.
        </p>
        <div className="flex justify-center items-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <Clock className="h-4 w-4 text-blue-600" />
            <span>24/7 Support Available</span>
          </div>
          <div className="flex items-center space-x-2">
            <Shield className="h-4 w-4 text-green-600" />
            <span>Up to 5 Years Warranty</span>
          </div>
          <div className="flex items-center space-x-2">
            <Award className="h-4 w-4 text-purple-600" />
            <span>15 Years Experience</span>
          </div>
        </div>
      </div>
    </div>
  );
}
