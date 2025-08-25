/**
 * Professional Template - Booking Page
 * 
 * Complete booking page with service selection and appointment scheduling
 */

'use client';

import React from 'react';
import BookingWizard from '../../../../components/booking/BookingWizard';
import { Button } from '../../../../components/ui/button';
import { ArrowLeft, Phone, Mail, MapPin } from 'lucide-react';
import Link from 'next/link';

// Sample data - in production this would come from the backend
const SAMPLE_BUSINESS_ID = "123e4567-e89b-12d3-a456-426614174000";

const SAMPLE_SERVICES = [
  {
    id: "service-1",
    business_id: SAMPLE_BUSINESS_ID,
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
    available_days: [1, 2, 3, 4, 5], // Monday-Friday
    available_times: {
      start: "08:00",
      end: "17:00"
    }
  },
  {
    id: "service-2",
    business_id: SAMPLE_BUSINESS_ID,
    name: "Emergency HVAC Repair",
    category: "HVAC",
    description: "24/7 emergency repair service for heating and cooling system failures. Same-day service available.",
    is_bookable: true,
    requires_site_visit: true,
    estimated_duration_minutes: 120,
    min_duration_minutes: 60,
    max_duration_minutes: 240,
    base_price: 299.99,
    price_type: "estimate" as const,
    required_skills: [],
    min_technicians: 1,
    max_technicians: 2,
    min_lead_time_hours: 2,
    max_advance_days: 30,
    available_days: [1, 2, 3, 4, 5, 6, 7], // 7 days a week
    available_times: {
      start: "06:00",
      end: "22:00"
    }
  },
  {
    id: "service-3",
    business_id: SAMPLE_BUSINESS_ID,
    name: "HVAC System Installation",
    category: "HVAC",
    description: "Complete installation of new heating and cooling systems. Includes consultation, sizing, and professional installation.",
    is_bookable: true,
    requires_site_visit: true,
    estimated_duration_minutes: 480, // 8 hours
    min_duration_minutes: 360,
    max_duration_minutes: 600,
    base_price: 2499.99,
    price_type: "estimate" as const,
    required_skills: [],
    min_technicians: 2,
    max_technicians: 3,
    min_lead_time_hours: 48,
    max_advance_days: 90,
    available_days: [1, 2, 3, 4, 5], // Monday-Friday
    available_times: {
      start: "07:00",
      end: "16:00"
    }
  },
  {
    id: "service-4",
    business_id: SAMPLE_BUSINESS_ID,
    name: "Preventive Maintenance",
    category: "HVAC",
    description: "Seasonal maintenance to keep your HVAC system running efficiently. Includes cleaning, tune-up, and safety check.",
    is_bookable: true,
    requires_site_visit: true,
    estimated_duration_minutes: 60,
    min_duration_minutes: 45,
    max_duration_minutes: 90,
    base_price: 99.99,
    price_type: "fixed" as const,
    required_skills: [],
    min_technicians: 1,
    max_technicians: 1,
    min_lead_time_hours: 24,
    max_advance_days: 120,
    available_days: [1, 2, 3, 4, 5], // Monday-Friday
    available_times: {
      start: "08:00",
      end: "17:00"
    }
  }
];

export default function BookingPage() {
  const handleBookingComplete = (booking: any) => {
    console.log('Booking completed:', booking);
    // In production, you might want to:
    // - Send analytics event
    // - Redirect to a thank you page
    // - Show additional upsells
  };

  const handleBookingError = (error: string) => {
    console.error('Booking error:', error);
    // In production, you might want to:
    // - Send error to monitoring service
    // - Show user-friendly error message
    // - Offer alternative contact methods
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Back Button */}
            <Link href="/templates/professional">
              <Button variant="ghost" className="flex items-center gap-2">
                <ArrowLeft className="w-4 h-4" />
                Back to Home
              </Button>
            </Link>

            {/* Logo/Brand */}
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">
                Professional Services
              </h1>
            </div>

            {/* Contact Info */}
            <div className="hidden md:flex items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <Phone className="w-4 h-4" />
                <span>(555) 123-4567</span>
              </div>
              <div className="flex items-center gap-1">
                <Mail className="w-4 h-4" />
                <span>info@company.com</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Book Your Service Appointment
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Schedule your HVAC service with our certified technicians. 
            Choose your service, pick a convenient time, and we'll take care of the rest.
          </p>
        </div>

        {/* Booking Wizard */}
        <BookingWizard
          businessId={SAMPLE_BUSINESS_ID}
          services={SAMPLE_SERVICES}
          onBookingComplete={handleBookingComplete}
          onBookingError={handleBookingError}
          className="mb-12"
        />

        {/* Additional Information */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <div className="text-center p-6 bg-white rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Phone className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold mb-2">24/7 Emergency Service</h3>
            <p className="text-gray-600 text-sm">
              Need immediate help? Call us anytime for emergency repairs and urgent service needs.
            </p>
            <Button variant="outline" size="sm" className="mt-3">
              Call Now: (555) 123-4567
            </Button>
          </div>

          <div className="text-center p-6 bg-white rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <MapPin className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-semibold mb-2">Service Area</h3>
            <p className="text-gray-600 text-sm">
              We proudly serve the greater metropolitan area with fast, reliable service to your location.
            </p>
            <Button variant="outline" size="sm" className="mt-3">
              Check Coverage
            </Button>
          </div>

          <div className="text-center p-6 bg-white rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="font-semibold mb-2">Questions?</h3>
            <p className="text-gray-600 text-sm">
              Have questions about our services or need help with booking? We're here to help.
            </p>
            <Button variant="outline" size="sm" className="mt-3">
              Contact Support
            </Button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600 text-sm">
            <p>&copy; 2025 Professional Services. All rights reserved.</p>
            <p className="mt-2">
              Licensed, Insured, and Committed to Excellence
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
