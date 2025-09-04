/**
 * Artifact Process Section Component
 * 
 * Renders the process/how-it-works section from an ActivityPageArtifact.
 */

'use client';

import React from 'react';
import { CheckCircle, ArrowRight, Clock } from 'lucide-react';
import { ArtifactSectionProps } from '@/lib/shared/types/seo-artifacts';
import { useABTest, useABTestTracking } from '@/components/testing/ABTestingProvider';

export function ArtifactProcess({ artifact, testKey = 'process', className = '' }: ArtifactSectionProps) {
  const { getVariant } = useABTest();
  const { trackClick } = useABTestTracking(testKey);

  // Get variant content or use default
  const processContent = getVariant(testKey, artifact.process);

  // Default process structure if not provided
  const defaultProcess = {
    title: `Our ${artifact.activity_name} Process`,
    description: `Here's how we handle your ${artifact.activity_name.toLowerCase()} from start to finish`,
    steps: [
      {
        name: 'Initial Assessment',
        description: 'We evaluate your needs and provide a detailed assessment',
        duration: '30 minutes',
        icon: 'assessment'
      },
      {
        name: 'Custom Solution',
        description: 'We design a solution tailored to your specific requirements',
        duration: 'Same day',
        icon: 'design'
      },
      {
        name: 'Professional Installation',
        description: 'Our certified technicians complete the work to the highest standards',
        duration: '2-4 hours',
        icon: 'installation'
      },
      {
        name: 'Quality Assurance',
        description: 'We test everything and ensure your complete satisfaction',
        duration: '15 minutes',
        icon: 'quality'
      }
    ]
  };

  const process = { ...defaultProcess, ...processContent };

  const handleStepClick = (stepName: string) => {
    trackClick(`process_step_${stepName.toLowerCase().replace(/\s+/g, '_')}`);
  };

  return (
    <section className={`py-20 bg-gray-50 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            {process.title}
          </h2>
          {process.description && (
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              {process.description}
            </p>
          )}
        </div>

        {/* Process Steps */}
        <div className="relative">
          {/* Connection Line */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-200 via-blue-400 to-blue-200 transform -translate-y-1/2 z-0"></div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 relative z-10">
            {process.steps.map((step: any, index: number) => (
              <div
                key={index}
                onClick={() => handleStepClick(step.name)}
                className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer border border-gray-100 hover:border-blue-200 transform hover:-translate-y-2 relative"
              >
                {/* Step Number */}
                <div className="absolute -top-4 left-8">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm group-hover:bg-blue-700 transition-colors shadow-lg">
                    {index + 1}
                  </div>
                </div>

                {/* Icon */}
                <div className="mb-6 pt-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center group-hover:from-blue-200 group-hover:to-blue-300 transition-all duration-300">
                    <CheckCircle className="w-8 h-8 text-blue-600" />
                  </div>
                </div>

                {/* Content */}
                <div className="space-y-4">
                  <h3 className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors duration-300">
                    {step.name}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {step.description}
                  </p>
                  
                  {step.duration && (
                    <div className="flex items-center space-x-2 text-sm text-blue-600">
                      <Clock className="w-4 h-4" />
                      <span className="font-medium">{step.duration}</span>
                    </div>
                  )}
                </div>

                {/* Arrow for desktop */}
                {index < process.steps.length - 1 && (
                  <div className="hidden lg:block absolute -right-4 top-1/2 transform -translate-y-1/2 z-20">
                    <div className="w-8 h-8 bg-white rounded-full shadow-lg flex items-center justify-center border border-gray-200">
                      <ArrowRight className="w-4 h-4 text-blue-600" />
                    </div>
                  </div>
                )}

                {/* Hover Indicator */}
                <div className="mt-6 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="w-12 h-1 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Additional Information */}
        {process.additional_info && (
          <div className="mt-16 text-center">
            <div className="bg-white rounded-2xl p-8 lg:p-12 shadow-lg border border-gray-100">
              <h3 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-4">
                {process.additional_info.title}
              </h3>
              <p className="text-lg text-gray-600 mb-8 max-w-3xl mx-auto">
                {process.additional_info.description}
              </p>
              {process.additional_info.features && (
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                  {process.additional_info.features.map((feature: string, index: number) => (
                    <div key={index} className="flex items-center space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>
              )}
              {process.additional_info.cta && (
                <button
                  onClick={() => trackClick('process_cta')}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  {process.additional_info.cta.text}
                </button>
              )}
            </div>
          </div>
        )}

        {/* Timeline Summary */}
        {process.total_duration && (
          <div className="mt-16 bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-8 text-white text-center">
            <h3 className="text-2xl font-bold mb-4">Complete Process Timeline</h3>
            <div className="text-4xl font-bold mb-2">{process.total_duration}</div>
            <p className="text-blue-100">From initial contact to project completion</p>
          </div>
        )}
      </div>
    </section>
  );
}
