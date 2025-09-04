/**
 * Artifact Offers Section Component
 * 
 * Renders pricing and offers from an ActivityPageArtifact.
 */

'use client';

import React from 'react';
import { DollarSign, Check, Star, Phone } from 'lucide-react';
import { ArtifactSectionWithBusinessProps } from '@/lib/shared/types/seo-artifacts';
import { useABTest, useABTestTracking } from '@/components/testing/ABTestingProvider';

export function ArtifactOffers({ artifact, businessData, testKey = 'offers', className = '' }: ArtifactSectionWithBusinessProps) {
  const { getVariant } = useABTest();
  const { trackClick, trackConversion } = useABTestTracking(testKey);

  // Get variant content or use default
  const offersContent = getVariant(testKey, artifact.offers);

  if (!offersContent || Object.keys(offersContent).length === 0) {
    return null;
  }

  const handleOfferClick = (offerTitle: string) => {
    trackClick(`offer_${offerTitle.toLowerCase().replace(/\s+/g, '_')}`);
    trackConversion('offer_interest');
  };

  const handleCallClick = () => {
    trackClick('offers_call');
    trackConversion('phone_call');
    window.location.href = `tel:${businessData.phone}`;
  };

  return (
    <section className={`py-20 bg-gradient-to-br from-blue-50 to-indigo-50 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            {offersContent.title || `${artifact.activity_name} Pricing & Packages`}
          </h2>
          {offersContent.subtitle && (
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              {offersContent.subtitle}
            </p>
          )}
        </div>

        {/* Pricing Cards */}
        {offersContent.packages && offersContent.packages.length > 0 && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
            {offersContent.packages.map((pkg: any, index: number) => (
              <div
                key={index}
                onClick={() => handleOfferClick(pkg.name)}
                className={`bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer border-2 transform hover:-translate-y-2 ${
                  pkg.featured ? 'border-blue-500 ring-4 ring-blue-100' : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                {pkg.featured && (
                  <div className="bg-blue-500 text-white text-sm font-bold py-2 px-4 rounded-full inline-block mb-4">
                    <Star className="w-4 h-4 inline mr-1" />
                    Most Popular
                  </div>
                )}

                <div className="mb-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{pkg.name}</h3>
                  <p className="text-gray-600">{pkg.description}</p>
                </div>

                <div className="mb-6">
                  <div className="flex items-baseline">
                    <span className="text-4xl font-bold text-gray-900">${pkg.price}</span>
                    {pkg.unit && <span className="text-gray-600 ml-2">/{pkg.unit}</span>}
                  </div>
                  {pkg.originalPrice && (
                    <div className="text-sm text-gray-500 line-through">
                      Originally ${pkg.originalPrice}
                    </div>
                  )}
                </div>

                {pkg.features && (
                  <div className="mb-8">
                    <ul className="space-y-3">
                      {pkg.features.map((feature: string, featureIndex: number) => (
                        <li key={featureIndex} className="flex items-start space-x-3">
                          <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-gray-700">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleOfferClick(pkg.name);
                  }}
                  className={`w-full py-4 px-6 rounded-lg font-bold text-lg transition-all duration-200 ${
                    pkg.featured
                      ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                  }`}
                >
                  {pkg.cta || 'Get This Package'}
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Starting Price */}
        {offersContent.starting_price && (
          <div className="text-center mb-12">
            <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200 inline-block">
              <div className="flex items-center justify-center space-x-3 mb-4">
                <DollarSign className="w-8 h-8 text-green-600" />
                <h3 className="text-2xl font-bold text-gray-900">Starting Price</h3>
              </div>
              <div className="text-4xl font-bold text-green-600 mb-2">
                ${offersContent.starting_price}
              </div>
              <p className="text-gray-600">
                {offersContent.starting_price_note || `For basic ${artifact.activity_name.toLowerCase()}`}
              </p>
            </div>
          </div>
        )}

        {/* Special Offers */}
        {offersContent.special_offers && offersContent.special_offers.length > 0 && (
          <div className="grid md:grid-cols-2 gap-8 mb-16">
            {offersContent.special_offers.map((offer: any, index: number) => (
              <div
                key={index}
                onClick={() => handleOfferClick(offer.title)}
                className="bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-2"
              >
                <div className="flex items-center space-x-3 mb-4">
                  <Star className="w-6 h-6" />
                  <h3 className="text-2xl font-bold">{offer.title}</h3>
                </div>
                <p className="text-orange-100 mb-6 text-lg">{offer.description}</p>
                {offer.savings && (
                  <div className="text-3xl font-bold mb-4">Save ${offer.savings}</div>
                )}
                {offer.expires && (
                  <div className="text-sm text-orange-200">
                    Expires: {offer.expires}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Financing */}
        {offersContent.financing && (
          <div className="bg-white rounded-2xl p-8 lg:p-12 shadow-lg border border-gray-200 mb-16">
            <div className="text-center">
              <h3 className="text-3xl font-bold text-gray-900 mb-4">
                {offersContent.financing.title || 'Flexible Financing Available'}
              </h3>
              <p className="text-lg text-gray-600 mb-8 max-w-3xl mx-auto">
                {offersContent.financing.description || 'Make your project affordable with our financing options'}
              </p>
              
              {offersContent.financing.options && (
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                  {offersContent.financing.options.map((option: any, index: number) => (
                    <div key={index} className="text-center">
                      <div className="text-2xl font-bold text-blue-600 mb-2">{option.rate}</div>
                      <div className="font-medium text-gray-900 mb-1">{option.term}</div>
                      <div className="text-sm text-gray-600">{option.description}</div>
                    </div>
                  ))}
                </div>
              )}
              
              <button
                onClick={() => trackClick('financing_cta')}
                className="bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
              >
                Learn About Financing
              </button>
            </div>
          </div>
        )}

        {/* Call to Action */}
        <div className="text-center">
          <div className="bg-gray-900 rounded-2xl p-8 lg:p-12 text-white">
            <h3 className="text-3xl font-bold mb-4">Ready to Get Started?</h3>
            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
              Get a free, no-obligation quote for your {artifact.activity_name.toLowerCase()} project
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={handleCallClick}
                className="bg-orange-500 hover:bg-orange-600 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center space-x-2"
              >
                <Phone className="w-5 h-5" />
                <span>Call {businessData.phone}</span>
              </button>
              <button
                onClick={() => trackClick('offers_quote')}
                className="bg-white hover:bg-gray-100 text-gray-900 font-bold py-4 px-8 rounded-lg text-lg transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
              >
                Get Free Quote Online
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
