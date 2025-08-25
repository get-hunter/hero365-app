'use client';

import React, { useState } from 'react';
import { MapPin, Clock, Phone, Navigation, ChevronDown, ChevronUp } from 'lucide-react';

interface ServiceArea {
  city: string;
  state: string;
  zipCodes?: string[];
  estimatedTime?: string; // "30 minutes", "45 minutes"
  isMainArea?: boolean;
  description?: string;
}

interface ServiceAreasProps {
  business: {
    name: string;
    phone: string;
    address: string;
  };
  serviceAreas: ServiceArea[];
  primaryArea?: string;
  showEmergencyService?: boolean;
  showViewAll?: boolean;
  maxInitialDisplay?: number;
}

export default function ServiceAreas({
  business,
  serviceAreas,
  primaryArea = "Austin, TX",
  showEmergencyService = true,
  showViewAll = true,
  maxInitialDisplay = 8
}: ServiceAreasProps) {
  const [showAllAreas, setShowAllAreas] = useState(false);

  // Default service areas based on Austin area (can be dynamic)
  const defaultServiceAreas: ServiceArea[] = [
    { city: 'Austin', state: 'TX', estimatedTime: '20 minutes', isMainArea: true, description: 'Our main service area with fastest response times' },
    { city: 'Round Rock', state: 'TX', estimatedTime: '25 minutes', zipCodes: ['78664', '78665', '78681'] },
    { city: 'Cedar Park', state: 'TX', estimatedTime: '30 minutes', zipCodes: ['78613', '78630'] },
    { city: 'Pflugerville', state: 'TX', estimatedTime: '25 minutes', zipCodes: ['78660', '78691'] },
    { city: 'Georgetown', state: 'TX', estimatedTime: '35 minutes', zipCodes: ['78626', '78627', '78628'] },
    { city: 'Leander', state: 'TX', estimatedTime: '35 minutes', zipCodes: ['78641', '78645'] },
    { city: 'Kyle', state: 'TX', estimatedTime: '40 minutes', zipCodes: ['78640'] },
    { city: 'Buda', state: 'TX', estimatedTime: '40 minutes', zipCodes: ['78610'] },
    { city: 'Dripping Springs', state: 'TX', estimatedTime: '45 minutes', zipCodes: ['78620'] },
    { city: 'Lakeway', state: 'TX', estimatedTime: '35 minutes', zipCodes: ['78734'] },
    { city: 'Bee Cave', state: 'TX', estimatedTime: '35 minutes', zipCodes: ['78738'] },
    { city: 'West Lake Hills', state: 'TX', estimatedTime: '25 minutes', zipCodes: ['78746'] },
    { city: 'Rollingwood', state: 'TX', estimatedTime: '25 minutes', zipCodes: ['78746'] },
    { city: 'Manor', state: 'TX', estimatedTime: '30 minutes', zipCodes: ['78653'] }
  ];

  const areas = serviceAreas.length > 0 ? serviceAreas : defaultServiceAreas;
  const displayedAreas = showAllAreas ? areas : areas.slice(0, maxInitialDisplay);
  const mainArea = areas.find(area => area.isMainArea) || areas[0];

  const handleAreaClick = (area: ServiceArea) => {
    // This could navigate to a location-specific page
    // For now, we'll just scroll to contact or call
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleCallClick = () => {
    window.location.href = `tel:${business.phone}`;
  };

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center mb-4">
            <div className="bg-blue-100 rounded-full p-3">
              <MapPin size={32} className="text-blue-600" />
            </div>
          </div>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Proudly Serving Customers in
          </h2>
          <p className="text-2xl text-blue-600 font-semibold mb-4">
            {primaryArea} and Surrounding Areas
          </p>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            {business.name} provides professional services throughout the greater Austin metropolitan area. 
            We're committed to serving our local community with fast, reliable service.
          </p>
        </div>

        {/* Main Service Area Highlight */}
        {mainArea && (
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg p-8 mb-12 text-center">
            <h3 className="text-3xl font-bold mb-2">
              {mainArea.city}, {mainArea.state}
            </h3>
            <p className="text-blue-100 mb-4 text-lg">
              {mainArea.description || 'Our primary service area'}
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <Clock size={16} className="text-blue-200" />
                <span>Average response: {mainArea.estimatedTime}</span>
              </div>
              {showEmergencyService && (
                <div className="flex items-center gap-2">
                  <Phone size={16} className="text-blue-200" />
                  <span>24/7 Emergency Service Available</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Service Areas Grid */}
        <div className="mb-8">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Cities We Serve
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {displayedAreas.map((area, index) => (
              <div
                key={index}
                onClick={() => handleAreaClick(area)}
                className={`p-4 rounded-lg border-2 transition-all duration-200 cursor-pointer hover:shadow-md ${
                  area.isMainArea 
                    ? 'border-blue-500 bg-blue-50 hover:bg-blue-100' 
                    : 'border-gray-200 bg-white hover:border-blue-300 hover:bg-blue-50'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <MapPin size={16} className={area.isMainArea ? 'text-blue-600' : 'text-gray-500'} />
                    <h4 className="font-semibold text-gray-900">
                      {area.city}
                    </h4>
                  </div>
                  {area.isMainArea && (
                    <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
                      Primary
                    </span>
                  )}
                </div>
                
                {area.estimatedTime && (
                  <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                    <Clock size={14} />
                    <span>{area.estimatedTime} response</span>
                  </div>
                )}
                
                {area.zipCodes && (
                  <div className="text-xs text-gray-500">
                    ZIP: {area.zipCodes.join(', ')}
                  </div>
                )}
                
                <div className="text-blue-600 text-sm font-medium mt-2 flex items-center gap-1">
                  Learn More
                  <Navigation size={12} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* View All Button */}
        {showViewAll && areas.length > maxInitialDisplay && (
          <div className="text-center mb-8">
            <button
              onClick={() => setShowAllAreas(!showAllAreas)}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200"
            >
              {showAllAreas ? (
                <>
                  View Less Areas
                  <ChevronUp size={16} />
                </>
              ) : (
                <>
                  View All {areas.length} Areas
                  <ChevronDown size={16} />
                </>
              )}
            </button>
          </div>
        )}

        {/* Service Area Benefits */}
        <div className="bg-gray-50 rounded-lg p-8">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Local Service Benefits
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-green-100 rounded-full p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Clock size={24} className="text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Fast Response Times</h4>
              <p className="text-gray-600 text-sm">
                Local technicians mean faster service. Most areas served within 45 minutes.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-blue-100 rounded-full p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <MapPin size={24} className="text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Local Knowledge</h4>
              <p className="text-gray-600 text-sm">
                We understand local building codes, weather patterns, and common issues.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-purple-100 rounded-full p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Phone size={24} className="text-purple-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Community Focused</h4>
              <p className="text-gray-600 text-sm">
                We're part of your community and committed to long-term relationships.
              </p>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-12 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg p-8">
          <h3 className="text-2xl font-bold mb-4">
            Don't See Your Area Listed?
          </h3>
          <p className="text-green-100 mb-6 text-lg">
            We may still be able to serve you! Give us a call to check availability in your area.
          </p>
          <button
            onClick={handleCallClick}
            className="bg-white text-green-600 px-8 py-3 rounded-lg font-semibold hover:bg-green-50 transition-colors duration-200 text-lg flex items-center gap-2 mx-auto"
          >
            <Phone size={20} />
            Call {business.phone}
          </button>
        </div>
      </div>
    </section>
  );
}
