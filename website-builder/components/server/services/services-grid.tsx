/**
 * Hero365 Services Grid Component - Server Component Version
 * 
 * Professional services grid with feature highlights and CTAs
 * Pure server component for SSR compatibility
 */

import React from 'react';

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
  primaryColor?: string;
}

export default function ServicesGrid({
  businessName,
  city,
  phone,
  primaryColor = "#3b82f6"
}: Hero365ServicesGridProps) {

  const serviceCategories: ServiceCategory[] = [
    {
      id: "hvac-installation",
      name: "HVAC Installation",
      description: "Expert installation of new heating and cooling systems.",
      iconPath: "M3 12h18m-9-9v18",
      iconColor: "text-blue-600",
      features: [
        { 
          name: "Energy-efficient systems", 
          description: "Save on utility bills", 
          iconPath: "M13 10V3L4 14h7v7l9-11h-7z",
          iconColor: "text-green-500"
        },
        { 
          name: "Professional sizing & design", 
          description: "Optimal comfort", 
          iconPath: "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z",
          iconColor: "text-yellow-500"
        },
        { 
          name: "Extended warranties", 
          description: "Peace of mind", 
          iconPath: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
          iconColor: "text-purple-500"
        },
      ],
      startingPrice: "Call for Quote",
      isPopular: true,
    },
    {
      id: "hvac-repair",
      name: "HVAC Repair & Maintenance",
      description: "Fast, reliable repairs and preventive maintenance to keep your system running smoothly.",
      iconPath: "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z",
      iconColor: "text-green-600",
      features: [
        { 
          name: "24/7 Emergency Service", 
          description: "Immediate assistance", 
          iconPath: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
          iconColor: "text-red-500"
        },
        { 
          name: "Certified technicians", 
          description: "Experienced professionals", 
          iconPath: "M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z",
          iconColor: "text-yellow-500"
        },
        { 
          name: "Preventive tune-ups", 
          description: "Extend system life", 
          iconPath: "M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z",
          iconColor: "text-blue-500"
        },
      ],
      startingPrice: "Diagnostic Fee",
    },
    {
      id: "plumbing-services",
      name: "Plumbing Services",
      description: "Comprehensive plumbing solutions from leak repair to water heater installation.",
      iconPath: "M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z",
      iconColor: "text-blue-600",
      features: [
        { 
          name: "Leak detection & repair", 
          description: "Stop water damage", 
          iconPath: "M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z",
          iconColor: "text-blue-500"
        },
        { 
          name: "Water heater installation", 
          description: "Reliable hot water", 
          iconPath: "M3 12h18m-9-9v18",
          iconColor: "text-red-500"
        },
        { 
          name: "Drain cleaning", 
          description: "Clear blockages", 
          iconPath: "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z",
          iconColor: "text-yellow-500"
        },
      ],
      startingPrice: "Call for Estimate",
    },
    {
      id: "electrical-services",
      name: "Electrical Services",
      description: "Safe and reliable electrical installations, repairs, and upgrades.",
      iconPath: "M13 10V3L4 14h7v7l9-11h-7z",
      iconColor: "text-yellow-600",
      features: [
        { 
          name: "Panel upgrades", 
          description: "Increase capacity", 
          iconPath: "M13 10V3L4 14h7v7l9-11h-7z",
          iconColor: "text-orange-500"
        },
        { 
          name: "Lighting installation", 
          description: "Enhance ambiance", 
          iconPath: "M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z",
          iconColor: "text-yellow-500"
        },
        { 
          name: "Wiring & rewiring", 
          description: "Modernize your home", 
          iconPath: "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z",
          iconColor: "text-gray-500"
        },
      ],
      startingPrice: "Call for Estimate",
    },
  ];

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

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {serviceCategories.map((category) => (
            <div 
              key={category.id} 
              className="bg-white rounded-lg border shadow-sm flex flex-col h-full hover:shadow-xl transition-shadow duration-200"
            >
              <div className="flex flex-row items-center space-x-4 p-6">
                <div className="p-3 rounded-full bg-blue-50">
                  <svg className={`h-8 w-8 ${category.iconColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={category.iconPath} />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900">
                  {category.name}
                </h3>
              </div>
              <div className="flex-grow p-6 pt-0">
                <p className="text-gray-600 mb-4">
                  {category.description}
                </p>
                <ul className="space-y-2 mb-6">
                  {category.features.map((feature, index) => (
                    <li key={index} className="flex items-center text-sm text-gray-700">
                      <svg className={`h-4 w-4 ${feature.iconColor} mr-2`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={feature.iconPath} />
                      </svg>
                      <span className="font-medium">{feature.name}</span>
                    </li>
                  ))}
                </ul>
                <div className="mt-auto">
                  {category.startingPrice && (
                    <p className="text-sm text-gray-500 mb-2">
                      Starting from: <span className="font-semibold text-gray-800">{category.startingPrice}</span>
                    </p>
                  )}
                  <a 
                    href={`tel:${phone}`}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium inline-flex items-center justify-center transition-colors"
                  >
                    Get a Quote 
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
            View All Services
          </a>
        </div>
      </div>
    </section>
  );
}
