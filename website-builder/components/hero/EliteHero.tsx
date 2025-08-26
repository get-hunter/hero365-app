/**
 * Elite Hero Component
 * 
 * Professional hero section with enhanced promotional banners, trust badges, A/B testing, and dynamic CTAs
 */

'use client';

import React from 'react';
import { Star, Award, Shield, Clock, Phone, Calendar, ArrowRight } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { BookingCTAButton } from '../booking/BookingWidgetProvider';
import PromotionalBannerSystem, { Promotion, getSeasonalPromotions } from './PromotionalBannerSystem';

interface EliteHeroProps {
  businessName: string;
  headline: string;
  subheadline: string;
  city: string;
  phone: string;
  averageRating: number;
  totalReviews: number;
  promotions?: Promotion[];
  currentTrade?: string;
  emergencyMessage?: string;
  backgroundImage?: string;
  primaryColor?: string;
}

export default function EliteHero({
  businessName,
  headline,
  subheadline,
  city,
  phone,
  averageRating,
  totalReviews,
  promotions = [],
  currentTrade = 'HVAC',
  emergencyMessage,
  backgroundImage,
  primaryColor = "#3b82f6"
}: EliteHeroProps) {
  
  // Enhanced promotional system with seasonal offers
  const enhancedPromotions = getSeasonalPromotions(promotions);

  return (
    <div className="relative">
      {/* Enhanced Promotional Banner System */}
      <PromotionalBannerSystem
        promotions={enhancedPromotions}
        placement="hero_banner"
        phone={phone}
        currentTrade={currentTrade}
      />

      {/* Main Hero Section */}
      <section 
        className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 text-white py-20 lg:py-32"
        style={{
          backgroundImage: backgroundImage ? `linear-gradient(rgba(59, 130, 246, 0.8), rgba(29, 78, 216, 0.8)), url(${backgroundImage})` : undefined,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Content */}
            <div className="space-y-8">
              {/* Ratings Badge */}
              <div className="flex items-center space-x-4">
                <div className="flex items-center bg-white/10 backdrop-blur-sm rounded-full px-4 py-2 border border-white/20">
                  <div className="flex items-center mr-3">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < Math.floor(averageRating) 
                            ? 'text-yellow-400 fill-current' 
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-sm font-medium">
                    <span className="text-yellow-400 font-bold">{averageRating}</span> Average Trust Rating
                  </span>
                </div>
                <div className="text-sm text-blue-200">
                  {totalReviews.toLocaleString()}+ Reviews
                </div>
              </div>

              {/* Main Headline */}
              <div>
                <h1 className="text-4xl lg:text-6xl font-bold leading-tight mb-4">
                  {headline}
                </h1>
                <p className="text-xl lg:text-2xl text-blue-100 leading-relaxed">
                  {subheadline}
                </p>
              </div>

              {/* Original Trust Indicators */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <div className="flex items-center text-sm text-blue-100">
                  <div className="text-green-400 mr-2">
                    <Shield className="w-4 h-4" />
                  </div>
                  Licensed & Insured
                </div>
                <div className="flex items-center text-sm text-blue-100">
                  <div className="text-green-400 mr-2">
                    <Award className="w-4 h-4" />
                  </div>
                  25+ Years Experience
                </div>
                <div className="flex items-center text-sm text-blue-100">
                  <div className="text-green-400 mr-2">
                    <Clock className="w-4 h-4" />
                  </div>
                  Same-Day Service
                </div>
                <div className="flex items-center text-sm text-blue-100">
                  <div className="text-green-400 mr-2">
                    <Star className="w-4 h-4" />
                  </div>
                  100% Satisfaction
                </div>
              </div>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-4">
                <BookingCTAButton 
                  size="lg" 
                  className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-4 text-lg font-semibold"
                >
                  <Calendar className="w-5 h-5 mr-2" />
                  Book Service Online
                </BookingCTAButton>
                <a 
                  href={`tel:${phone}`}
                  className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold border-2 border-white text-white hover:bg-white hover:text-blue-900 rounded-md transition-colors duration-200"
                >
                  <Phone className="w-5 h-5 mr-2" />
                  Call {phone}
                </a>
              </div>

              {/* Additional Promotions Carousel */}
              {enhancedPromotions.length > 1 && (
                <div className="mt-8">
                  <PromotionalBannerSystem
                    promotions={enhancedPromotions.slice(1, 4)}
                    placement="promo_carousel"
                    phone={phone}
                    currentTrade={currentTrade}
                    className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20"
                  />
                </div>
              )}
            </div>

            {/* Right Column - Service Highlights */}
            <div className="space-y-6">
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
                <h3 className="text-2xl font-bold mb-6 text-center">
                  Professional Services in {city}
                </h3>
                
                <div className="space-y-4">
                  {[
                    { name: "Emergency Service", description: "24/7 emergency response", price: "From $149" },
                    { name: "System Installation", description: "Complete system installation", price: "Free Quote" },
                    { name: "Preventive Maintenance", description: "Keep your system running efficiently", price: "From $99" }
                  ].map((service, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10">
                      <div>
                        <div className="font-semibold text-white">{service.name}</div>
                        <div className="text-sm text-blue-200">{service.description}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-orange-300 font-bold">{service.price}</div>
                        <BookingCTAButton 
                          size="sm" 
                          className="mt-1 bg-white/20 border border-white/30 text-white hover:bg-white hover:text-blue-900 backdrop-blur-sm"
                        >
                          Book Now
                        </BookingCTAButton>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 pt-6 border-t border-white/20 text-center">
                  <p className="text-blue-200 text-sm mb-3">
                    Same-day service available • Licensed & Insured • 100% Satisfaction Guaranteed
                  </p>
                  <button className="inline-flex items-center justify-center px-6 py-2 border-2 border-white text-white hover:bg-white hover:text-blue-900 rounded-md transition-colors duration-200 font-medium">
                    View All Services
                    <ArrowRight className="ml-2 w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Decorative Elements */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg className="w-full h-12 text-white" viewBox="0 0 1200 120" preserveAspectRatio="none">
            <path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" fill="currentColor"></path>
            <path d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" opacity=".5" fill="currentColor"></path>
            <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" fill="currentColor"></path>
          </svg>
        </div>
      </section>
    </div>
  );
}
