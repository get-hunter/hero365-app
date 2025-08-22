import React from 'react';
import { Phone, MapPin, Clock, ArrowRight } from 'lucide-react';

interface HeroProps {
  headline: string;
  subtitle?: string;
  ctaButtons?: Array<{
    text: string;
    action: string;
    style?: 'primary' | 'secondary' | 'outline';
  }>;
  trustIndicators?: string[];
  showEmergencyBanner?: boolean;
  emergencyMessage?: string;
  backgroundImage?: string;
  business?: {
    name: string;
    phone?: string;
    address?: string;
    hours?: string;
  };
}

export default function Hero({
  headline,
  subtitle,
  ctaButtons = [],
  trustIndicators = [],
  showEmergencyBanner,
  emergencyMessage,
  backgroundImage,
  business,
}: HeroProps) {
  return (
    <section className="relative">
      {/* Emergency Banner */}
      {showEmergencyBanner && (
        <div className="bg-red-600 text-white py-3 px-4 text-center animate-pulse">
          <p className="font-semibold">
            {emergencyMessage || '🚨 24/7 Emergency Service Available - Call Now!'}
          </p>
        </div>
      )}
      
      {/* Hero Section */}
      <div
        className="relative min-h-[600px] flex items-center justify-center bg-gradient-to-br from-blue-50 to-green-50"
        style={{
          backgroundImage: backgroundImage ? `url(${backgroundImage})` : undefined,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        {/* Overlay for better text readability */}
        {backgroundImage && (
          <div className="absolute inset-0 bg-black bg-opacity-50" />
        )}
        
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 text-gray-900">
            {headline}
          </h1>
          
          {subtitle && (
            <p className="text-xl md:text-2xl mb-8 text-gray-600 max-w-3xl mx-auto">
              {subtitle}
            </p>
          )}
          
          {/* CTA Buttons */}
          {ctaButtons.length > 0 && (
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              {ctaButtons.map((button, index) => (
                <button
                  key={index}
                  className={`
                    px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 flex items-center justify-center gap-2
                    ${button.style === 'primary' 
                      ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl' 
                      : button.style === 'secondary'
                      ? 'bg-green-600 text-white hover:bg-green-700 shadow-lg hover:shadow-xl'
                      : 'border-2 border-gray-800 text-gray-800 hover:bg-gray-800 hover:text-white'
                    }
                  `}
                  data-action={button.action}
                >
                  {button.text}
                  <ArrowRight className="w-5 h-5" />
                </button>
              ))}
            </div>
          )}
          
          {/* Trust Indicators */}
          {trustIndicators.length > 0 && (
            <div className="flex flex-wrap justify-center gap-6 mb-8">
              {trustIndicators.map((indicator, index) => (
                <span
                  key={index}
                  className="bg-white px-4 py-2 rounded-full shadow-md text-sm font-medium text-gray-700"
                >
                  ✓ {indicator}
                </span>
              ))}
            </div>
          )}
          
          {/* Business Info Bar */}
          {business && (
            <div className="bg-white bg-opacity-95 rounded-lg shadow-xl p-6 max-w-4xl mx-auto">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-gray-700">
                {business.phone && (
                  <div className="flex items-center justify-center gap-2">
                    <Phone className="w-5 h-5 text-blue-600" />
                    <a href={`tel:${business.phone}`} className="font-semibold hover:text-blue-600">
                      {business.phone}
                    </a>
                  </div>
                )}
                {business.address && (
                  <div className="flex items-center justify-center gap-2">
                    <MapPin className="w-5 h-5 text-green-600" />
                    <span>{business.address}</span>
                  </div>
                )}
                {business.hours && (
                  <div className="flex items-center justify-center gap-2">
                    <Clock className="w-5 h-5 text-orange-600" />
                    <span>{business.hours}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
