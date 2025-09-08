/**
 * Hero365 Services Grid Component - Server Component Version
 * 
 * Professional services grid with feature highlights and CTAs
 * Pure server component for SSR compatibility
 */

import React from 'react';
import type { ServiceItem } from '@/lib/shared/types/api-responses';

interface ServiceFeature {
  name: string;
  description: string;
  iconPath: string;
  iconColor: string;
}

interface ServiceCategory {
  id: string;
  name: string;
  description: string;
  iconPath: string;
  iconColor: string;
  features: ServiceFeature[];
  startingPrice?: string;
  isPopular?: boolean;
}

interface Hero365ServicesGridProps {
  businessName: string;
  city: string;
  phone: string;
  services?: ServiceItem[];
  primaryColor?: string;
}

export default function ServicesGrid({
  businessName,
  city,
  phone,
  services = [],
  primaryColor = "#3b82f6"
}: Hero365ServicesGridProps) {
  // Flat list (no grouping), show category label on each card
  const items = (services || []).slice(0, 8).map((s) => ({
    id: String((s as any).id ?? s.slug),
    name: s.name,
    description: `Professional ${s.name.toLowerCase()} services`,
    slug: s.slug,
    category: (s as any).category_name || (s as any).category || (s as any).category_slug || 'Service',
    isPopular: Boolean((s as any).is_featured),
    isEmergency: Boolean((s as any).is_emergency),
  }));

  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Comprehensive {businessName || 'Professional'} Services
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Expert services for {city || 'your area'} homes and businesses.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {items.map((item) => (
            <div key={item.id} className="bg-white rounded-lg border shadow-sm flex flex-col h-full hover:shadow-xl transition-shadow duration-200">
              <div className="flex flex-row items-center space-x-4 p-6">
                <div className="p-3 rounded-full bg-blue-50">
                  <svg className={`h-8 w-8 ${item.isEmergency ? 'text-red-600' : item.isPopular ? 'text-green-600' : 'text-blue-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div className="min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">{item.name}</h3>
                  <p className="text-xs text-gray-500 mt-1 truncate">{item.category}</p>
                </div>
              </div>
              <div className="flex-grow p-6 pt-0">
                <p className="text-gray-600 mb-4 line-clamp-3">{item.description}</p>
                <div className="mt-auto">
                  <a href={`/services/${item.slug}`} className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium inline-flex items-center justify-center transition-colors">
                    View Service
                    <svg className="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-12">
          <a
            href="/services"
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 text-lg font-bold shadow-lg rounded-md inline-flex items-center transition-colors"
          >
            Explore All Services
          </a>
        </div>
      </div>
    </section>
  );
}
