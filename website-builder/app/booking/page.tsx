/**
 * Booking Page
 * 
 * Complete booking page with service selection and appointment scheduling
 */

'use client';

import React from 'react';
import BookingWizard from '../../components/booking/BookingWizard';
import { BookableService } from '../../lib/types/booking';

// Sample services for booking
const SAMPLE_SERVICES: BookableService[] = [
  {
    id: "hvac-inspection",
    business_id: "123e4567-e89b-12d3-a456-426614174000",
    name: "HVAC System Inspection",
    category: "HVAC",
    description: "Comprehensive inspection of your heating and cooling system including filters, ducts, and efficiency testing.",
    is_bookable: true,
    requires_site_visit: true,
    estimated_duration_minutes: 90,
    min_duration_minutes: 60,
    max_duration_minutes: 120,
    base_price: 149.99,
    price_type: "fixed" as const,
    required_skills: [],
    min_technicians: 1,
    max_technicians: 1,
    min_lead_time_hours: 4,
    max_advance_days: 60,
    available_days: [1, 2, 3, 4, 5],
    available_times: { start: "08:00", end: "17:00" }
  },
  {
    id: "emergency-repair",
    business_id: "123e4567-e89b-12d3-a456-426614174000",
    name: "Emergency HVAC Repair",
    category: "HVAC",
    description: "24/7 emergency repair service for heating and cooling system failures.",
    is_bookable: true,
    requires_site_visit: true,
    estimated_duration_minutes: 120,
    base_price: 299.99,
    price_type: "estimate" as const,
    required_skills: [],
    min_technicians: 1,
    max_technicians: 2,
    min_lead_time_hours: 2,
    max_advance_days: 30,
    available_days: [1, 2, 3, 4, 5, 6, 7],
    available_times: { start: "06:00", end: "22:00" }
  },
  {
    id: "maintenance",
    business_id: "123e4567-e89b-12d3-a456-426614174000",
    name: "Preventive Maintenance",
    category: "HVAC",
    description: "Seasonal maintenance to keep your HVAC system running efficiently.",
    is_bookable: true,
    requires_site_visit: true,
    estimated_duration_minutes: 60,
    base_price: 99.99,
    price_type: "fixed" as const,
    required_skills: [],
    min_technicians: 1,
    max_technicians: 1,
    min_lead_time_hours: 24,
    max_advance_days: 120,
    available_days: [1, 2, 3, 4, 5],
    available_times: { start: "08:00", end: "17:00" }
  }
];

export default function BookingPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                Professional HVAC Services
              </h1>
            </div>
            <div className="text-sm text-gray-600">
              <span className="font-medium">Need help?</span>{' '}
              <a href="tel:(555) 123-4567" className="text-blue-600 hover:text-blue-800">
                Call (555) 123-4567
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Schedule Your HVAC Service
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Book your appointment online in just a few simple steps. 
            Choose your service, pick a convenient time, and we'll take care of the rest.
          </p>
        </div>

        {/* Booking Wizard */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <BookingWizard
            businessId="123e4567-e89b-12d3-a456-426614174000"
            services={SAMPLE_SERVICES}
            companyName="Professional HVAC Services"
            companyPhone="(555) 123-4567"
            companyEmail="info@professionalhvac.com"
            onBookingComplete={(booking) => {
              console.log('Booking completed:', booking);
            }}
            onBookingError={(error) => {
              console.error('Booking error:', error);
            }}
          />
        </div>

        {/* Trust Indicators */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900">Licensed & Insured</h3>
            <p className="text-sm text-gray-600">Fully licensed professionals</p>
          </div>
          
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-3">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900">Same-Day Service</h3>
            <p className="text-sm text-gray-600">Available when you need us</p>
          </div>
          
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mb-3">
              <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900">100% Satisfaction</h3>
            <p className="text-sm text-gray-600">Guaranteed quality work</p>
          </div>
        </div>
      </main>
    </div>
  );
}
