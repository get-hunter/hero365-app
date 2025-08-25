/**
 * Multi-Trade Demo Page
 * 
 * Showcases the dynamic template system with different trades
 */

'use client';

import React, { useState } from 'react';
import { createTemplateGenerator } from '../../lib/services/template-generator';
import { SAMPLE_BUSINESSES } from '../../lib/data/sample-businesses';
import { Trade } from '../../lib/types/trade-config';

export default function DemoPage() {
  const [selectedTrade, setSelectedTrade] = useState<Trade>('hvac');
  
  const availableTrades = Object.keys(SAMPLE_BUSINESSES) as Trade[];
  
  const generatePreview = (trade: Trade) => {
    const business = SAMPLE_BUSINESSES[trade];
    if (!business) return null;
    
    const generator = createTemplateGenerator(business);
    const content = generator.generate();
    
    return content;
  };

  const currentContent = generatePreview(selectedTrade);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Hero365 Dynamic Template System
              </h1>
              <p className="text-gray-600 mt-2">
                One template system supporting all trades - residential and commercial
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedTrade}
                onChange={(e) => setSelectedTrade(e.target.value as Trade)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="hvac">HVAC (Residential)</option>
                <option value="plumbing">Plumbing (Residential)</option>
                <option value="electrical">Electrical (Residential)</option>
                <option value="mechanical">Mechanical (Commercial)</option>
              </select>
              <a
                href="/"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                View Live Site
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Content Preview */}
      {currentContent && (
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Business Info Card */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  {currentContent.business.name}
                </h2>
                <p className="text-lg text-gray-600 mb-4">
                  {currentContent.business.professional_title} • {currentContent.business.service_description}
                </p>
                <div className="flex items-center space-x-6 text-sm text-gray-500">
                  <span>📍 {currentContent.business.city}, {currentContent.business.state}</span>
                  <span>📞 {currentContent.business.phone}</span>
                  <span>⭐ {currentContent.trust.reviews_summary.average_rating} ({currentContent.trust.reviews_summary.total_reviews}+ reviews)</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500 mb-1">Trade Type</div>
                <div className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  {currentContent.business.type === 'residential' ? '🏠 Residential' : '🏢 Commercial'}
                </div>
              </div>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Hero Content */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">🎯 Hero Section</h3>
              <div className="space-y-4">
                <div>
                  <div className="text-sm font-medium text-gray-500 mb-1">Headline</div>
                  <div className="text-lg font-bold text-gray-900">
                    {currentContent.hero.headline}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500 mb-1">Subtitle Points</div>
                  <ul className="space-y-1">
                    {currentContent.hero.subtitle_points.map((point, index) => (
                      <li key={index} className="flex items-center text-gray-700">
                        <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
                {currentContent.hero.emergency_message && (
                  <div>
                    <div className="text-sm font-medium text-gray-500 mb-1">Emergency Message</div>
                    <div className="text-red-600 font-medium">
                      {currentContent.hero.emergency_message}
                    </div>
                  </div>
                )}
                <div className="flex space-x-3">
                  <button 
                    className="px-4 py-2 rounded-lg text-white font-medium"
                    style={{ backgroundColor: currentContent.colors.primary }}
                  >
                    {currentContent.hero.primary_cta}
                  </button>
                  <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium">
                    {currentContent.hero.secondary_cta}
                  </button>
                </div>
              </div>
            </div>

            {/* Services */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">🔧 Services</h3>
              <div className="space-y-4">
                {currentContent.services.categories.map((category, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-semibold text-gray-900">{category.name}</h4>
                        <p className="text-sm text-gray-600">{category.description}</p>
                      </div>
                      <div className="flex space-x-2">
                        {category.is_emergency && (
                          <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                            Emergency
                          </span>
                        )}
                        {category.is_popular && (
                          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                            Popular
                          </span>
                        )}
                      </div>
                    </div>
                    {category.starting_price && (
                      <div className="text-sm font-medium text-green-600">
                        Starting at ${category.starting_price}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Trust Indicators */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">🛡️ Trust & Credentials</h3>
              <div className="space-y-4">
                <div>
                  <div className="text-sm font-medium text-gray-500 mb-2">Certifications</div>
                  <div className="flex flex-wrap gap-2">
                    {currentContent.trust.certifications.map((cert, index) => (
                      <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                        {cert.name}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500 mb-2">Guarantees</div>
                  <ul className="space-y-1">
                    {currentContent.trust.guarantees.map((guarantee, index) => (
                      <li key={index} className="flex items-center text-sm text-gray-700">
                        <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                        {guarantee}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* SEO & Technical */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">🔍 SEO & Technical</h3>
              <div className="space-y-4">
                <div>
                  <div className="text-sm font-medium text-gray-500 mb-1">Page Title</div>
                  <div className="text-sm text-gray-900 font-medium">
                    {currentContent.seo.title}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500 mb-1">Meta Description</div>
                  <div className="text-sm text-gray-700">
                    {currentContent.seo.description}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500 mb-1">Keywords</div>
                  <div className="flex flex-wrap gap-1">
                    {currentContent.seo.keywords.map((keyword, index) => (
                      <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500 mb-1">Color Scheme</div>
                  <div className="flex space-x-2">
                    <div 
                      className="w-8 h-8 rounded border"
                      style={{ backgroundColor: currentContent.colors.primary }}
                      title={`Primary: ${currentContent.colors.primary}`}
                    ></div>
                    <div 
                      className="w-8 h-8 rounded border"
                      style={{ backgroundColor: currentContent.colors.secondary }}
                      title={`Secondary: ${currentContent.colors.secondary}`}
                    ></div>
                    <div 
                      className="w-8 h-8 rounded border"
                      style={{ backgroundColor: currentContent.colors.accent }}
                      title={`Accent: ${currentContent.colors.accent}`}
                    ></div>
                    <div 
                      className="w-8 h-8 rounded border"
                      style={{ backgroundColor: currentContent.colors.emergency }}
                      title={`Emergency: ${currentContent.colors.emergency}`}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* About Section */}
          <div className="bg-white rounded-lg shadow-lg p-6 mt-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">📖 About Section</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <div className="text-sm font-medium text-gray-500 mb-2">Company Story</div>
                <p className="text-gray-700 text-sm leading-relaxed">
                  {currentContent.about.company_story}
                </p>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-500 mb-2">Business Stats</div>
                <div className="grid grid-cols-2 gap-4">
                  {currentContent.about.stats.map((stat, index) => (
                    <div key={index} className="text-center">
                      <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                      <div className="text-sm text-gray-600">{stat.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}
