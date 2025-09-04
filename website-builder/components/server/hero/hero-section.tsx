/**
 * Hero365 Hero Component - Server Component Version
 * 
 * Professional hero section with enhanced promotional banners, trust badges, and dynamic CTAs
 * Pure server component for SSR compatibility
 */

import React from 'react';

// SSR-safe phone formatting
function formatPhoneForDisplay(phone: string): string {
  if (!phone) return '';
  // Simple formatting for SSR compatibility
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  if (cleaned.length === 11 && cleaned[0] === '1') {
    return `(${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  }
  return phone; // Return as-is if can't format
}

// SSR-safe seasonal promotions (simplified)
function getSeasonalPromotions(): Array<{
  id: string;
  title: string;
  subtitle?: string;
  badge_text?: string;
  cta_text: string;
}> {
  const now = new Date();
  const month = now.getMonth();
  
  // Spring promotions (March-May)
  if (month >= 2 && month <= 4) {
    return [{
      id: 'spring-tune-up',
      title: 'Spring System Tune-Up Special',
      subtitle: 'Get your HVAC ready for summer!',
      badge_text: 'LIMITED TIME',
      cta_text: 'Schedule Now'
    }];
  }
  
  // Summer promotions (June-August)
  if (month >= 5 && month <= 7) {
    return [{
      id: 'summer-cooling',
      title: 'Beat the Heat Special',
      subtitle: 'AC installation & repair discounts',
      badge_text: 'SAVE NOW',
      cta_text: 'Get Quote'
    }];
  }
  
  // Fall promotions (September-November)
  if (month >= 8 && month <= 10) {
    return [{
      id: 'fall-maintenance',
      title: 'Fall Maintenance Package',
      subtitle: 'Prepare for winter with our maintenance special',
      badge_text: 'SEASONAL',
      cta_text: 'Book Service'
    }];
  }
  
  // Winter promotions (December-February)
  return [{
    id: 'winter-heating',
    title: 'Winter Heating Special',
    subtitle: 'Heating system check & repair discounts',
    badge_text: 'WINTER READY',
    cta_text: 'Schedule'
  }];
}

interface Hero365HeroProps {
  businessName: string;
  headline: string;
  subheadline: string;
  city: string;
  phone: string;
  averageRating: number;
  totalReviews: number;
  promotions?: Array<any>;
  currentTrade?: string;
  emergencyMessage?: string;
  backgroundImage?: string;
  primaryColor?: string;
}

export default function HeroSection({
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
}: Hero365HeroProps) {
  
  // Enhanced promotional system with seasonal offers
  const enhancedPromotions = getSeasonalPromotions();
  const displayPhone = formatPhoneForDisplay(phone);

  return (
    <section 
      className="relative overflow-hidden bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 text-white"
      style={{ 
        backgroundImage: backgroundImage ? `linear-gradient(rgba(30, 58, 138, 0.8), rgba(30, 58, 138, 0.8)), url(${backgroundImage})` : undefined,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-900/20 to-transparent">
        <div className="absolute inset-0 opacity-30" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='7' cy='7' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}></div>
      </div>

      {/* Promotional Banner */}
      {enhancedPromotions.length > 0 && (
        <div className="relative bg-gradient-to-r from-yellow-500 to-orange-500 text-black py-3">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-center text-center">
              <span className="bg-red-600 text-white mr-3 animate-pulse px-2 py-1 rounded text-xs font-bold">
                {enhancedPromotions[0].badge_text}
              </span>
              <span className="font-semibold text-sm sm:text-base">
                {enhancedPromotions[0].title} - {enhancedPromotions[0].subtitle}
              </span>
              <span className="ml-4 bg-black text-white hover:bg-gray-800 hidden sm:inline-flex items-center px-3 py-1 rounded text-sm font-medium transition-colors">
                {enhancedPromotions[0].cta_text}
                <svg className="ml-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                </svg>
              </span>
            </div>
          </div>
        </div>
      )}

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-28">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div className="text-center lg:text-left">
            {/* Emergency Message */}
            {emergencyMessage && (
              <div className="inline-flex items-center bg-red-600 text-white px-4 py-2 rounded-full text-sm font-medium mb-6 animate-pulse">
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                {emergencyMessage}
              </div>
            )}

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight mb-6">
              <span className="block">{headline}</span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl sm:text-2xl text-blue-100 mb-8 leading-relaxed">
              {subheadline}
            </p>

            {/* Trust Indicators */}
            <div className="flex flex-wrap justify-center lg:justify-start gap-4 mb-8">
              <div className="flex items-center bg-white/10 backdrop-blur-sm rounded-lg px-3 py-2">
                <svg className="h-5 w-5 text-yellow-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span className="text-sm font-medium">Licensed & Insured</span>
              </div>
              <div className="flex items-center bg-white/10 backdrop-blur-sm rounded-lg px-3 py-2">
                <svg className="h-5 w-5 text-yellow-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
                <span className="text-sm font-medium">5-Star Rated</span>
              </div>
              <div className="flex items-center bg-white/10 backdrop-blur-sm rounded-lg px-3 py-2">
                <svg className="h-5 w-5 text-yellow-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-medium">24/7 Emergency</span>
              </div>
            </div>

            {/* Rating Display */}
            <div className="flex items-center justify-center lg:justify-start mb-8">
              <div className="flex items-center bg-white/10 backdrop-blur-sm rounded-lg px-4 py-3">
                <div className="flex items-center mr-4">
                  {[...Array(5)].map((_, i) => (
                    <svg
                      key={i}
                      className={`h-5 w-5 ${i < Math.floor(averageRating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                      />
                    </svg>
                  ))}
                </div>
                <div className="text-left">
                  <div className="text-lg font-bold">{averageRating.toFixed(1)} Stars</div>
                  <div className="text-sm text-blue-200">{totalReviews} Reviews</div>
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <a 
                href={`tel:${phone}`} 
                className="bg-yellow-500 hover:bg-yellow-400 text-black font-bold text-lg px-8 py-4 rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center justify-center"
              >
                <svg className="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                Call {displayPhone}
              </a>
              
              <a 
                href="/booking" 
                className="border-2 border-white text-white hover:bg-white hover:text-blue-900 font-bold text-lg px-8 py-4 rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center justify-center"
              >
                <svg className="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Schedule Service
              </a>
            </div>

            {/* Additional Info */}
            <div className="mt-8 text-center lg:text-left">
              <p className="text-blue-200 text-sm">
                Serving {city} and surrounding areas • Licensed & Insured • Same-day service available
              </p>
            </div>
          </div>

          {/* Visual Element */}
          <div className="hidden lg:block">
            <div className="relative">
              {/* Decorative Elements */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-3xl transform rotate-6"></div>
              <div className="relative bg-white/10 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-yellow-500 rounded-full mb-6">
                    <svg className="h-10 w-10 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold mb-4">Professional {currentTrade} Services</h3>
                  <p className="text-blue-100 mb-6">
                    Expert technicians, quality workmanship, and customer satisfaction guaranteed.
                  </p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-400">{totalReviews}+</div>
                      <div className="text-blue-200">Happy Customers</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-400">24/7</div>
                      <div className="text-blue-200">Emergency Service</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
