/**
 * Artifact Hero Section Component
 * 
 * Renders the hero section from an ActivityPageArtifact with A/B testing support.
 */

'use client';

import React from 'react';
import { Phone, Calendar, Shield, Award } from 'lucide-react';
import { ArtifactSectionWithBusinessProps } from '@/lib/shared/types/seo-artifacts';
import { useABTest, useABTestTracking } from '@/components/testing/ABTestingProvider';

export function ArtifactHero({ artifact, businessData, testKey = 'hero', className = '' }: ArtifactSectionWithBusinessProps) {
  const { getVariant } = useABTest();
  const { trackClick, trackConversion } = useABTestTracking(testKey);

  // Get variant content or use default
  const heroContent = getVariant(testKey, artifact.hero);

  // Default hero structure if not provided
  const defaultHero = {
    headline: `Professional ${artifact.activity_name} Services`,
    subheading: `Expert ${artifact.activity_name.toLowerCase()} by licensed technicians in ${businessData.city}, ${businessData.state}`,
    cta_primary: { text: 'Get Free Estimate', action: 'quote' },
    cta_secondary: { text: `Call ${businessData.phone}`, action: 'phone' },
    trust_badges: ['Licensed & Insured', '24/7 Service', '5-Year Warranty'],
    quick_facts: [
      'Same-day service available',
      'Upfront pricing',
      'Satisfaction guaranteed'
    ]
  };

  const hero = { ...defaultHero, ...heroContent };

  const handlePrimaryClick = () => {
    trackClick('primary_cta');
    if (hero.cta_primary.action === 'quote') {
      trackConversion('quote_request');
      // Scroll to quote form or open modal
      const quoteSection = document.getElementById('quote-form');
      if (quoteSection) {
        quoteSection.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  const handleSecondaryClick = () => {
    trackClick('secondary_cta');
    if (hero.cta_secondary.action === 'phone') {
      trackConversion('phone_call');
      window.location.href = `tel:${businessData.phone}`;
    }
  };

  return (
    <section className={`relative bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 text-white overflow-hidden ${className}`}>
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-black/20">
        <div className="absolute inset-0 bg-[url('/patterns/grid.svg')] opacity-10"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-28">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div className="space-y-8">
            {/* Main Headline */}
            <div className="space-y-4">
              <h1 className="text-4xl lg:text-6xl font-bold leading-tight">
                {hero.headline}
              </h1>
              <p className="text-xl lg:text-2xl text-blue-100 leading-relaxed">
                {hero.subheading}
              </p>
            </div>

            {/* Trust Badges */}
            {hero.trust_badges && hero.trust_badges.length > 0 && (
              <div className="flex flex-wrap gap-4">
                {hero.trust_badges.map((badge: string, index: number) => (
                  <div key={index} className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2">
                    <Shield className="w-4 h-4 text-blue-200" />
                    <span className="text-sm font-medium">{badge}</span>
                  </div>
                ))}
              </div>
            )}

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={handlePrimaryClick}
                className="bg-orange-500 hover:bg-orange-600 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
              >
                {hero.cta_primary.text}
              </button>
              <button
                onClick={handleSecondaryClick}
                className="bg-white/10 hover:bg-white/20 backdrop-blur-sm border-2 border-white/30 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-200 flex items-center justify-center space-x-2"
              >
                <Phone className="w-5 h-5" />
                <span>{hero.cta_secondary.text}</span>
              </button>
            </div>

            {/* Quick Facts */}
            {hero.quick_facts && hero.quick_facts.length > 0 && (
              <div className="grid sm:grid-cols-3 gap-4 pt-8 border-t border-white/20">
                {hero.quick_facts.map((fact: string, index: number) => (
                  <div key={index} className="flex items-center space-x-2">
                    <Award className="w-5 h-5 text-orange-400 flex-shrink-0" />
                    <span className="text-sm text-blue-100">{fact}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Visual Element */}
          <div className="relative">
            {/* Service Image Placeholder */}
            <div className="relative bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
              <div className="aspect-square bg-gradient-to-br from-orange-400 to-orange-600 rounded-xl flex items-center justify-center">
                <div className="text-center text-white">
                  <Calendar className="w-16 h-16 mx-auto mb-4" />
                  <h3 className="text-2xl font-bold mb-2">Book Today</h3>
                  <p className="text-orange-100">Same-day service available</p>
                </div>
              </div>
              
              {/* Floating Elements */}
              <div className="absolute -top-4 -right-4 bg-green-500 text-white rounded-full p-3 shadow-lg">
                <Shield className="w-6 h-6" />
              </div>
              <div className="absolute -bottom-4 -left-4 bg-blue-500 text-white rounded-full p-3 shadow-lg">
                <Award className="w-6 h-6" />
              </div>
            </div>

            {/* Background Decoration */}
            <div className="absolute -z-10 top-8 left-8 w-full h-full bg-gradient-to-br from-orange-500/20 to-blue-500/20 rounded-2xl blur-xl"></div>
          </div>
        </div>
      </div>

      {/* Bottom Wave */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto">
          <path d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" fill="white"/>
        </svg>
      </div>
    </section>
  );
}
