/**
 * Artifact FAQs Section Component
 * 
 * Renders the FAQ section from an ActivityPageArtifact with structured data.
 */

'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';
import { ArtifactSectionProps } from '@/lib/shared/types/seo-artifacts';
import { useABTest, useABTestTracking } from '@/components/testing/ABTestingProvider';

export function ArtifactFAQs({ artifact, testKey = 'faqs', className = '' }: ArtifactSectionProps) {
  const { getVariant } = useABTest();
  const { trackClick } = useABTestTracking(testKey);
  const [openFAQ, setOpenFAQ] = useState<number | null>(null);

  // Get variant content or use default
  const faqsContent = getVariant(testKey, { faqs: artifact.faqs });

  if (!faqsContent.faqs || faqsContent.faqs.length === 0) {
    return null;
  }

  const handleFAQClick = (index: number, question: string) => {
    setOpenFAQ(openFAQ === index ? null : index);
    trackClick(`faq_${index}_${question.toLowerCase().replace(/[^a-z0-9]/g, '_').substring(0, 20)}`);
  };

  // Generate FAQ structured data
  const faqStructuredData = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqsContent.faqs.map((faq: any) => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer
      }
    }))
  };

  return (
    <>
      {/* FAQ Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqStructuredData) }}
      />

      <section className={`py-20 bg-white ${className}`}>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="flex items-center justify-center space-x-3 mb-6">
              <HelpCircle className="w-8 h-8 text-blue-600" />
              <h2 className="text-4xl lg:text-5xl font-bold text-gray-900">
                Frequently Asked Questions
              </h2>
            </div>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Get answers to common questions about our {artifact.activity_name.toLowerCase()} services
            </p>
          </div>

          {/* FAQ Items */}
          <div className="space-y-4">
            {faqsContent.faqs.map((faq: any, index: number) => (
              <div
                key={index}
                className="bg-gray-50 rounded-2xl border border-gray-200 hover:border-blue-200 transition-all duration-200 overflow-hidden"
              >
                <button
                  onClick={() => handleFAQClick(index, faq.question)}
                  className="w-full px-8 py-6 text-left flex items-center justify-between hover:bg-gray-100 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
                >
                  <h3 className="text-lg font-semibold text-gray-900 pr-8">
                    {faq.question}
                  </h3>
                  <div className="flex-shrink-0">
                    {openFAQ === index ? (
                      <ChevronUp className="w-6 h-6 text-blue-600" />
                    ) : (
                      <ChevronDown className="w-6 h-6 text-gray-400" />
                    )}
                  </div>
                </button>
                
                {openFAQ === index && (
                  <div className="px-8 pb-6">
                    <div className="pt-4 border-t border-gray-200">
                      <div 
                        className="text-gray-700 leading-relaxed prose prose-blue max-w-none"
                        dangerouslySetInnerHTML={{ __html: faq.answer }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Contact CTA */}
          <div className="mt-16 text-center">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 lg:p-12 border border-blue-100">
              <h3 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-4">
                Still Have Questions?
              </h3>
              <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
                Our expert technicians are here to help. Get personalized answers and a free consultation.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => trackClick('faq_contact_phone')}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  Call for Answers
                </button>
                <button
                  onClick={() => trackClick('faq_contact_quote')}
                  className="bg-white hover:bg-gray-50 text-blue-600 font-bold py-4 px-8 rounded-lg text-lg transition-all duration-200 border-2 border-blue-600 hover:border-blue-700"
                >
                  Get Free Quote
                </button>
              </div>
            </div>
          </div>

          {/* FAQ Categories (if provided) */}
          {faqsContent.categories && faqsContent.categories.length > 0 && (
            <div className="mt-16">
              <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">
                Browse by Category
              </h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {faqsContent.categories.map((category: any, index: number) => (
                  <div
                    key={index}
                    className="bg-white rounded-xl p-6 border border-gray-200 hover:border-blue-200 hover:shadow-lg transition-all duration-200 cursor-pointer"
                    onClick={() => trackClick(`faq_category_${category.name.toLowerCase().replace(/\s+/g, '_')}`)}
                  >
                    <h4 className="font-semibold text-gray-900 mb-2">{category.name}</h4>
                    <p className="text-sm text-gray-600 mb-3">{category.description}</p>
                    <div className="text-sm text-blue-600 font-medium">
                      {category.count} questions
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Search Hint */}
          <div className="mt-12 text-center">
            <p className="text-sm text-gray-500">
              💡 <strong>Tip:</strong> Use Ctrl+F (Cmd+F on Mac) to search for specific topics on this page
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
