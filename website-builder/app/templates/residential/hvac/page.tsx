'use client';

import React from 'react';
import Layout from '@/components/base/Layout';
import Hero from '@/components/base/Hero';
import ContactForm from '@/components/base/ContactForm';
import BookingWidget from '@/components/base/BookingWidget';
import ServiceCard from '@/components/base/ServiceCard';
import { Thermometer, Wind, Shield, Wrench } from 'lucide-react';

// This would normally come from props/API
const defaultContent = {
  "business": {
    "name": "Austin Elite HVAC",
    "phone": "(512) 555-COOL",
    "email": "service@austinelitehvac.com",
    "address": "456 Tech Ridge Blvd, Austin, TX 78753",
    "hours": "Mon-Fri 7AM-8PM, Sat-Sun 8AM-6PM",
    "description": "Premier HVAC services for Austin homes and businesses",
    "serviceAreas": [
      "Austin",
      "Round Rock",
      "Cedar Park",
      "Leander",
      "Georgetown"
    ]
  },
  "hero": {
    "headline": "Austin's Premier HVAC Experts",
    "subtitle": "Fast, Reliable Service \u2022 Licensed & Insured \u2022 100% Satisfaction Guaranteed",
    "ctaButtons": [
      {
        "text": "Get Free Quote",
        "action": "open_quote",
        "style": "primary"
      },
      {
        "text": "Call Now",
        "action": "call",
        "style": "secondary"
      }
    ],
    "trustIndicators": [
      "Licensed & Insured",
      "25+ Years Experience",
      "A+ BBB Rating"
    ],
    "showEmergencyBanner": true,
    "emergencyMessage": "\ud83d\udea8 HVAC Emergency? We're Available 24/7 - Call Now!"
  },
  "services": [
    {
      "title": "Emergency AC Repair",
      "description": "24/7 emergency air conditioning repair service",
      "price": "From $99",
      "features": [
        "Same-day service",
        "All major brands",
        "Parts warranty"
      ],
      "isPopular": true
    },
    {
      "title": "Heating System Repair",
      "description": "Expert furnace and heating system repair",
      "price": "From $89",
      "features": [
        "Safety inspection",
        "Energy efficiency check",
        "Emergency service"
      ]
    },
    {
      "title": "New HVAC Installation",
      "description": "Complete HVAC system installation and replacement",
      "price": "Free Quote",
      "features": [
        "Energy-efficient systems",
        "Financing available",
        "10-year warranty"
      ]
    },
    {
      "title": "Maintenance Plans",
      "description": "Preventive maintenance to keep your system running",
      "price": "$25/month",
      "features": [
        "Bi-annual tune-ups",
        "Priority service",
        "20% off repairs"
      ]
    }
  ],
  "seo": {
    "title": "Austin Elite HVAC - HVAC Repair & Installation in Austin, TX",
    "description": "Professional HVAC services in Austin. Emergency AC repair, heating installation, and maintenance. Licensed & insured. Call (512) 555-COOL for same-day service.",
    "keywords": [
      "hvac austin tx",
      "ac repair austin",
      "heating repair austin",
      "hvac installation",
      "emergency hvac"
    ]
  }
};









export default function HVACTemplate() {
  const { business, hero, services, contact, booking, seo } = defaultContent;

  return (
    <Layout seo={seo} business={business}>
      {/* Hero Section */}
      <Hero
        {...hero}
        business={business}
      />

      {/* Services Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Our HVAC Services</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              From emergency repairs to new installations, we provide comprehensive HVAC solutions for your home
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {services.map((service, index) => (
              <ServiceCard key={index} {...service} />
            ))}
          </div>
        </div>
      </section>

      {/* Why Choose Us Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why Choose {business.name}?</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Licensed & Insured</h3>
              <p className="text-gray-600">
                Fully licensed HVAC contractors with comprehensive insurance coverage for your peace of mind
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Thermometer className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Expert Technicians</h3>
              <p className="text-gray-600">
                Factory-trained technicians with years of experience servicing all major HVAC brands
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Wind className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Energy Efficient</h3>
              <p className="text-gray-600">
                We help you save money with energy-efficient solutions and smart thermostat installations
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Booking Widget */}
      <BookingWidget {...booking} />

      {/* Contact Form */}
      <ContactForm {...contact} />

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">{business.name}</h3>
              <p className="text-gray-400">
                Your trusted HVAC partner for all heating and cooling needs.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-3">Contact Info</h4>
              <p className="text-gray-400">{business.phone}</p>
              <p className="text-gray-400">{business.email}</p>
              <p className="text-gray-400">{business.address}</p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-3">Business Hours</h4>
              <p className="text-gray-400">{business.hours}</p>
              <p className="text-orange-400 mt-2">24/7 Emergency Service Available</p>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; {new Date().getFullYear()} {business.name}. All rights reserved.</p>
            <p className="mt-2">Powered by Hero365</p>
          </div>
        </div>
      </footer>
    </Layout>
  );
}
