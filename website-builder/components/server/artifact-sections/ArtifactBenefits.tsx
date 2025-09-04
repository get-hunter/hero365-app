/**
 * Artifact Benefits Section Component
 * 
 * Renders the benefits section from an ActivityPageArtifact with A/B testing support.
 */

'use client';

import React from 'react';
import { Shield, Clock, Award, Users, Wrench, Star } from 'lucide-react';
import { ArtifactSectionProps } from '@/lib/shared/types/seo-artifacts';
import { useABTest, useABTestTracking } from '@/components/testing/ABTestingProvider';

const iconMap = {
  shield: Shield,
  clock: Clock,
  award: Award,
  users: Users,
  wrench: Wrench,
  star: Star,
  warranty: Shield,
  licensed: Shield,
  insured: Shield,
  experience: Award,
  quality: Star,
  service: Users,
  tools: Wrench,
  time: Clock
};

export function ArtifactBenefits({ artifact, testKey = 'benefits', className = '' }: ArtifactSectionProps) {
  const { getVariant } = useABTest();
  const { trackClick } = useABTestTracking(testKey);

  // Get variant content or use default
  const benefitsContent = getVariant(testKey, artifact.benefits);

  // Default benefits structure if not provided
  const defaultBenefits = {
    title: `Why Choose Us for ${artifact.activity_name}`,
    subtitle: 'Experience the difference of working with licensed professionals',
    benefits: [
      {
        title: 'Licensed & Insured',
        description: 'Fully licensed professionals with comprehensive insurance coverage for your peace of mind.',
        icon: 'shield'
      },
      {
        title: 'Expert Technicians',
        description: 'Highly trained and certified technicians with years of experience in the field.',
        icon: 'users'
      },
      {
        title: 'Quality Guarantee',
        description: 'We stand behind our work with industry-leading warranties and satisfaction guarantees.',
        icon: 'award'
      },
      {
        title: 'Fast Response',
        description: 'Same-day service available with emergency response when you need it most.',
        icon: 'clock'
      }
    ]
  };

  const benefits = { ...defaultBenefits, ...benefitsContent };

  const handleBenefitClick = (benefitTitle: string) => {
    trackClick(`benefit_${benefitTitle.toLowerCase().replace(/\s+/g, '_')}`);
  };

  const getIcon = (iconName: string) => {
    const IconComponent = iconMap[iconName as keyof typeof iconMap] || Shield;
    return IconComponent;
  };

  return (
    <section className={`py-20 bg-white ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            {benefits.title}
          </h2>
          {benefits.subtitle && (
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              {benefits.subtitle}
            </p>
          )}
        </div>

        {/* Benefits Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {benefits.benefits.map((benefit: any, index: number) => {
            const IconComponent = getIcon(benefit.icon);
            
            return (
              <div
                key={index}
                onClick={() => handleBenefitClick(benefit.title)}
                className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer border border-gray-100 hover:border-blue-200 transform hover:-translate-y-2"
              >
                {/* Icon */}
                <div className="mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center group-hover:from-blue-600 group-hover:to-blue-700 transition-all duration-300 shadow-lg">
                    <IconComponent className="w-8 h-8 text-white" />
                  </div>
                </div>

                {/* Content */}
                <div className="space-y-4">
                  <h3 className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors duration-300">
                    {benefit.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {benefit.description}
                  </p>
                </div>

                {/* Hover Indicator */}
                <div className="mt-6 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="w-12 h-1 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"></div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Additional Content */}
        {benefits.additional_content && (
          <div className="mt-16 text-center">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 lg:p-12">
              <h3 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-4">
                {benefits.additional_content.title}
              </h3>
              <p className="text-lg text-gray-600 mb-8 max-w-3xl mx-auto">
                {benefits.additional_content.description}
              </p>
              {benefits.additional_content.cta && (
                <button
                  onClick={() => trackClick('additional_cta')}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  {benefits.additional_content.cta.text}
                </button>
              )}
            </div>
          </div>
        )}

        {/* Stats Section */}
        {benefits.stats && benefits.stats.length > 0 && (
          <div className="mt-16 bg-gray-900 rounded-2xl p-8 lg:p-12">
            <div className="grid md:grid-cols-3 gap-8 text-center">
              {benefits.stats.map((stat: any, index: number) => (
                <div key={index} className="text-white">
                  <div className="text-4xl lg:text-5xl font-bold text-orange-400 mb-2">
                    {stat.value}
                  </div>
                  <div className="text-lg text-gray-300">
                    {stat.label}
                  </div>
                  {stat.description && (
                    <div className="text-sm text-gray-400 mt-2">
                      {stat.description}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
