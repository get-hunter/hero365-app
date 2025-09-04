/**
 * Enhanced Promotional Banner System
 * 
 * Supports multiple banner types, seasonal offers, A/B testing, and dynamic placement
 */

'use client';

import React, { useState, useEffect } from 'react';
import { X, ArrowRight, Clock, Gift, Star, Zap, Calendar, Phone } from 'lucide-react';
import { Badge } from "@/components/ui/badge";
import { SimpleCTAButton } from '@/components/client/interactive/cta-button';

export interface Promotion {
  id: string;
  title: string;
  subtitle?: string;
  description?: string;
  offer_type: 'percentage_discount' | 'fixed_amount' | 'buy_one_get_one' | 'free_service' | 'seasonal_special' | 'new_customer' | 'referral';
  price_label?: string;
  badge_text?: string;
  cta_text?: string;
  cta_link?: string;
  placement: 'hero_banner' | 'promo_carousel' | 'sidebar' | 'footer' | 'popup' | 'inline';
  priority: number;
  start_date?: Date;
  end_date?: Date;
  is_active: boolean;
  is_featured: boolean;
  target_services?: string[];
  target_trades?: string[];
  service_areas?: string[];
  // Visual styling
  background_color?: string;
  text_color?: string;
  accent_color?: string;
  banner_style?: 'gradient' | 'solid' | 'pattern' | 'seasonal';
}

interface PromotionalBannerSystemProps {
  promotions: Promotion[];
  placement: 'hero_banner' | 'promo_carousel' | 'sidebar' | 'footer' | 'popup' | 'inline';
  phone?: string;
  currentTrade?: string;
  currentLocation?: string;
  onPromotionClick?: (promotion: Promotion) => void;
  onPromotionView?: (promotion: Promotion) => void;
  className?: string;
}

export default function PromotionalBannerSystem({
  promotions,
  placement,
  phone,
  currentTrade,
  currentLocation,
  onPromotionClick,
  onPromotionView,
  className = ""
}: PromotionalBannerSystemProps) {
  const [currentPromoIndex, setCurrentPromoIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(true);
  const [dismissedPromos, setDismissedPromos] = useState<Set<string>>(new Set());

  // Filter promotions based on placement, targeting, and active status
  const filteredPromotions = promotions.filter(promo => {
    if (!promo.is_active || dismissedPromos.has(promo.id)) return false;
    if (promo.placement !== placement) return false;
    
    // Check date validity
    const now = new Date();
    if (promo.start_date && new Date(promo.start_date) > now) return false;
    if (promo.end_date && new Date(promo.end_date) < now) return false;
    
    // Check trade targeting
    if (currentTrade && promo.target_trades?.length && !promo.target_trades.includes(currentTrade)) {
      return false;
    }
    
    // Check location targeting
    if (currentLocation && promo.service_areas?.length && !promo.service_areas.includes(currentLocation)) {
      return false;
    }
    
    return true;
  }).sort((a, b) => b.priority - a.priority);

  // Auto-rotate promotions for carousel placement
  useEffect(() => {
    if (placement === 'promo_carousel' && filteredPromotions.length > 1) {
      const interval = setInterval(() => {
        setCurrentPromoIndex((prev) => (prev + 1) % filteredPromotions.length);
      }, 5000); // Rotate every 5 seconds
      
      return () => clearInterval(interval);
    }
  }, [filteredPromotions.length, placement]);

  // Track promotion views
  useEffect(() => {
    if (filteredPromotions.length > 0 && onPromotionView) {
      const currentPromo = filteredPromotions[currentPromoIndex];
      if (currentPromo) {
        onPromotionView(currentPromo);
      }
    }
  }, [currentPromoIndex, filteredPromotions, onPromotionView]);

  if (!isVisible || filteredPromotions.length === 0) {
    return null;
  }

  const currentPromotion = filteredPromotions[currentPromoIndex];

  const handlePromotionClick = () => {
    if (onPromotionClick) {
      onPromotionClick(currentPromotion);
    }
  };

  const handleDismiss = (promoId: string) => {
    setDismissedPromos(prev => new Set([...prev, promoId]));
    if (filteredPromotions.length === 1) {
      setIsVisible(false);
    }
  };

  const getPromotionIcon = (offerType: string) => {
    switch (offerType) {
      case 'percentage_discount':
      case 'fixed_amount':
        return <Gift className="w-5 h-5" />;
      case 'seasonal_special':
        return <Calendar className="w-5 h-5" />;
      case 'new_customer':
        return <Star className="w-5 h-5" />;
      case 'free_service':
        return <Zap className="w-5 h-5" />;
      default:
        return <Gift className="w-5 h-5" />;
    }
  };

  const getBannerStyle = (promo: Promotion) => {
    const baseStyle = "relative overflow-hidden";
    
    switch (promo.banner_style) {
      case 'gradient':
        return `${baseStyle} bg-gradient-to-r from-green-600 to-green-700`;
      case 'seasonal':
        return `${baseStyle} bg-gradient-to-r from-orange-600 to-red-600`;
      case 'pattern':
        return `${baseStyle} bg-blue-600 bg-opacity-90`;
      default:
        return `${baseStyle} bg-gradient-to-r from-green-600 to-green-700`;
    }
  };

  const getPlacementStyles = () => {
    switch (placement) {
      case 'hero_banner':
        return "w-full py-3 px-4 text-white";
      case 'promo_carousel':
        return "w-full py-4 px-6 text-white rounded-lg mb-6";
      case 'sidebar':
        return "w-full py-3 px-4 text-white rounded-lg";
      case 'inline':
        return "w-full py-2 px-4 text-white rounded-md";
      case 'popup':
        return "fixed top-4 right-4 z-50 max-w-md py-4 px-6 text-white rounded-lg shadow-2xl";
      default:
        return "w-full py-3 px-4 text-white";
    }
  };

  return (
    <div className={`${getBannerStyle(currentPromotion)} ${getPlacementStyles()} ${className}`}>
      {/* Background Pattern for seasonal/special offers */}
      {currentPromotion.banner_style === 'pattern' && (
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-repeat bg-center" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }} />
        </div>
      )}

      <div className="relative max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-4 flex-1">
          {/* Promotion Icon */}
          <div className="flex-shrink-0">
            {getPromotionIcon(currentPromotion.offer_type)}
          </div>

          {/* Promotion Content */}
          <div className="flex-1">
            <div className="flex items-center space-x-3">
              <span className="font-bold text-lg">{currentPromotion.title}</span>
              
              {currentPromotion.badge_text && (
                <Badge className="bg-yellow-400 text-yellow-900 font-bold animate-pulse">
                  {currentPromotion.badge_text}
                </Badge>
              )}
              
              {currentPromotion.price_label && (
                <span className="font-bold text-xl text-yellow-300">
                  {currentPromotion.price_label}
                </span>
              )}
            </div>
            
            {currentPromotion.subtitle && (
              <p className="text-sm opacity-90 mt-1">{currentPromotion.subtitle}</p>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3 flex-shrink-0">
          {/* Carousel Indicators */}
          {placement === 'promo_carousel' && filteredPromotions.length > 1 && (
            <div className="flex space-x-1">
              {filteredPromotions.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentPromoIndex(index)}
                  className={`w-2 h-2 rounded-full transition-colors ${
                    index === currentPromoIndex ? 'bg-white' : 'bg-white/50'
                  }`}
                />
              ))}
            </div>
          )}

          {/* Primary CTA */}
          {currentPromotion.cta_text && (
            <button
              onClick={handlePromotionClick}
              className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium border-2 border-white text-white hover:bg-white hover:text-green-700 rounded-md transition-colors duration-200"
            >
              {currentPromotion.cta_text}
              <ArrowRight className="ml-2 w-4 h-4" />
            </button>
          )}

          {/* Phone CTA for emergency/urgent offers */}
          {phone && (currentPromotion.offer_type === 'seasonal_special' || currentPromotion.badge_text?.includes('Emergency')) && (
            <a
              href={`tel:${phone}`}
              className="inline-flex items-center justify-center px-3 py-2 text-sm font-medium bg-white/20 border border-white/30 text-white hover:bg-white hover:text-green-700 rounded-md transition-colors backdrop-blur-sm"
            >
              <Phone className="w-4 h-4 mr-1" />
              Call Now
            </a>
          )}

          {/* Booking CTA for service offers */}
          {(currentPromotion.offer_type === 'free_service' || currentPromotion.target_services?.length) && (
            <SimpleCTAButton
              size="sm"
              className="bg-white/20 border border-white/30 text-white hover:bg-white hover:text-green-700 backdrop-blur-sm"
            >
              Book Now
            </SimpleCTAButton>
          )}

          {/* Dismiss Button for popup/sidebar */}
          {(placement === 'popup' || placement === 'sidebar') && (
            <button
              onClick={() => handleDismiss(currentPromotion.id)}
              className="p-1 hover:bg-white/20 rounded-full transition-colors"
              aria-label="Dismiss promotion"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Urgency Timer for time-sensitive offers */}
      {currentPromotion.end_date && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/20">
          <div 
            className="h-full bg-yellow-400 transition-all duration-1000"
            style={{
              width: `${Math.max(0, Math.min(100, 
                (new Date(currentPromotion.end_date).getTime() - Date.now()) / 
                (24 * 60 * 60 * 1000) * 10 // Rough calculation for visual effect
              ))}%`
            }}
          />
        </div>
      )}
    </div>
  );
}

// Seasonal promotion helper
export const getSeasonalPromotions = (basePromotions: Promotion[]): Promotion[] => {
  const now = new Date();
  const month = now.getMonth();
  const seasonalPromotions: Promotion[] = [];

  // Spring promotions (March-May)
  if (month >= 2 && month <= 4) {
    seasonalPromotions.push({
      id: 'spring-tune-up',
      title: 'Spring System Tune-Up Special',
      subtitle: 'Get your HVAC ready for summer!',
      offer_type: 'seasonal_special',
      price_label: 'Starting at $99',
      badge_text: 'Spring Special',
      cta_text: 'Schedule Now',
      placement: 'hero_banner',
      priority: 8,
      is_active: true,
      is_featured: true,
      banner_style: 'gradient',
      background_color: '#10b981',
      target_trades: ['HVAC', 'Plumbing']
    });
  }

  // Summer promotions (June-August)
  if (month >= 5 && month <= 7) {
    seasonalPromotions.push({
      id: 'summer-cooling',
      title: 'Beat the Heat - AC Installation Special',
      subtitle: 'Stay cool with our summer deals!',
      offer_type: 'seasonal_special',
      price_label: 'Save up to $500',
      badge_text: 'Summer Sale',
      cta_text: 'Cool Down Now',
      placement: 'hero_banner',
      priority: 9,
      is_active: true,
      is_featured: true,
      banner_style: 'seasonal',
      target_trades: ['HVAC']
    });
  }

  // Fall promotions (September-November)
  if (month >= 8 && month <= 10) {
    seasonalPromotions.push({
      id: 'fall-maintenance',
      title: 'Fall Maintenance Package',
      subtitle: 'Prepare for winter with our comprehensive service',
      offer_type: 'seasonal_special',
      price_label: 'From $149',
      badge_text: 'Fall Ready',
      cta_text: 'Get Ready',
      placement: 'hero_banner',
      priority: 8,
      is_active: true,
      is_featured: true,
      banner_style: 'seasonal',
      target_trades: ['HVAC', 'Plumbing', 'Electrical']
    });
  }

  // Winter promotions (December-February)
  if (month >= 11 || month <= 1) {
    seasonalPromotions.push({
      id: 'winter-heating',
      title: 'Winter Heating Emergency Service',
      subtitle: '24/7 emergency heating repairs',
      offer_type: 'seasonal_special',
      price_label: 'No Overtime Charges',
      badge_text: 'Emergency Ready',
      cta_text: 'Get Warm Now',
      placement: 'hero_banner',
      priority: 10,
      is_active: true,
      is_featured: true,
      banner_style: 'pattern',
      background_color: '#dc2626',
      target_trades: ['HVAC']
    });
  }

  return [...basePromotions, ...seasonalPromotions];
};
