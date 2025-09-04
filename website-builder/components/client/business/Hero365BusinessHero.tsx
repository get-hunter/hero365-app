'use client';

import React from 'react';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Phone, Star, Award, Shield, Calendar } from 'lucide-react';
import type { BusinessData, Rating, PromoOffer } from '@/lib/shared/types/content';
import { SimpleCTAButton } from '@/components/client/interactive/cta-button';
import { useWebsiteContext } from '@/lib/shared/hooks/useWebsiteContext';

interface Hero365BusinessHeroProps {
  business: BusinessData;
  ratings: Rating[];
  promos: PromoOffer[];
}

export default function Hero365BusinessHero({ business, ratings, promos }: Hero365BusinessHeroProps) {
  // Get website context for activity-first approach
  const { data: websiteContext, loading, error } = useWebsiteContext(business.id);
  
  // Get featured promos for hero placement
  const heroPromos = promos.filter(p => p.placement === 'hero_banner' && p.is_featured);
  
  // Get average rating
  const avgRating = ratings.length > 0 
    ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length 
    : 0;
  
  const totalReviews = ratings.reduce((sum, r) => sum + r.review_count, 0);

  // Activity-first service name generation
  const getServiceName = () => {
    // NEW: Activity-first approach
    if (websiteContext?.activities && websiteContext.activities.length > 0) {
      const primaryActivity = websiteContext.activities[0];
      return primaryActivity.name;
    }
    
    // FALLBACK: Trade-based approach
    if (websiteContext?.business?.primary_trade_slug) {
      const tradeProfile = websiteContext.trades?.find(t => t.slug === websiteContext.business.primary_trade_slug);
      if (tradeProfile) {
        return tradeProfile.name;
      }
    }
    
    // LEGACY: Old field (deprecated)
    if (business.primary_trade) {
      return business.primary_trade.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    // DEFAULT: Generic fallback
    return 'Services';
  };

  // Activity-first service description generation
  const getServiceDescription = () => {
    // NEW: Activity-first approach with rich descriptions
    if (websiteContext?.activities && websiteContext.activities.length > 0) {
      const activityNames = websiteContext.activities.slice(0, 3).map(a => a.name.toLowerCase()).join(', ');
      return `Expert ${activityNames} services with guaranteed satisfaction. Available 24/7 for emergencies.`;
    }
    
    // FALLBACK: Use business description or generate from trade
    if (business.description) {
      return business.description;
    }
    
    // LEGACY: Generate from primary_trade
    const serviceName = getServiceName().toLowerCase();
    return `Expert ${serviceName} services with guaranteed satisfaction. Available 24/7 for emergencies.`;
  };

  return (
    <section className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 text-white overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.05%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%222%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div className="space-y-8">
            {/* Trust Indicators */}
            <div className="flex flex-wrap gap-4">
              <Badge variant="secondary" className="bg-white/10 text-white border-white/20">
                <Shield className="w-3 h-3 mr-1" />
                Licensed & Insured
              </Badge>
              <Badge variant="secondary" className="bg-white/10 text-white border-white/20">
                <Award className="w-3 h-3 mr-1" />
                25+ Years Experience
              </Badge>
              {avgRating > 0 && (
                <Badge variant="secondary" className="bg-white/10 text-white border-white/20">
                  <Star className="w-3 h-3 mr-1 fill-current" />
                  {avgRating.toFixed(1)} ({totalReviews} Reviews)
                </Badge>
              )}
            </div>

            {/* Main Headline */}
            <div className="space-y-4">
              <h1 className="text-4xl lg:text-6xl font-bold leading-tight">
                Professional{' '}
                <span className="text-blue-300">
                  {getServiceName()}
                </span>{' '}
                You Can Trust
              </h1>
              
              <p className="text-xl lg:text-2xl text-blue-100 max-w-2xl">
                {getServiceDescription()}
              </p>
            </div>

            {/* Service Areas */}
            {business.service_areas.length > 0 && (
              <div className="text-blue-200">
                <span className="font-semibold">Serving:</span> {business.service_areas.slice(0, 3).join(', ')}
                {business.service_areas.length > 3 && ' and more areas'}
              </div>
            )}

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <SimpleCTAButton 
                size="lg" 
                className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-4 text-lg"
              >
                <Calendar className="w-5 h-5 mr-2" />
                Book Appointment Online
              </SimpleCTAButton>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-900 px-8 py-4 text-lg">
                <Phone className="w-5 h-5 mr-2" />
                {business.phone_number || 'Call Now'}
              </Button>
            </div>

            {/* Promotional Offers */}
            {heroPromos.length > 0 && (
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
                <div className="space-y-3">
                  {heroPromos.slice(0, 2).map((promo) => (
                    <div key={promo.id} className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-lg">{promo.title}</h3>
                          {promo.badge_text && (
                            <Badge variant="destructive" className="bg-red-500 text-white">
                              {promo.badge_text}
                            </Badge>
                          )}
                        </div>
                        {promo.subtitle && (
                          <p className="text-blue-100 text-sm">{promo.subtitle}</p>
                        )}
                      </div>
                      {promo.price_label && (
                        <div className="text-right">
                          <div className="text-2xl font-bold text-orange-300">{promo.price_label}</div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Image/Visual */}
          <div className="relative">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
              <div className="aspect-square bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl flex items-center justify-center">
                {business.logo_url ? (
                  <img 
                    src={business.logo_url} 
                    alt={`${business.name} logo`}
                    className="max-w-full max-h-full object-contain"
                  />
                ) : (
                  <div className="text-center">
                    <div className="text-6xl mb-4">🔧</div>
                    <div className="text-2xl font-bold">{business.name}</div>
                  </div>
                )}
              </div>
            </div>
            
            {/* Floating Elements */}
            <div className="absolute -top-4 -right-4 bg-orange-500 text-white p-4 rounded-full shadow-lg">
              <Phone className="w-6 h-6" />
            </div>
            
            <div className="absolute -bottom-4 -left-4 bg-green-500 text-white p-4 rounded-full shadow-lg">
              <Award className="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Wave */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-12 fill-white">
          <path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z"></path>
        </svg>
      </div>
    </section>
  );
}