'use client';

import React from 'react';
import Layout from '@/components/base/Layout';
import Navigation from '@/components/base/Navigation';
import Hero from '@/components/base/Hero';
import ContactForm from '@/components/base/ContactForm';
import BookingWidget from '@/components/base/BookingWidget';
import ServiceCard from '@/components/base/ServiceCard';
import Reviews from '@/components/base/Reviews';
import ServiceAreas from '@/components/base/ServiceAreas';
import AboutUs from '@/components/base/AboutUs';
import { Thermometer, Wind, Shield, Wrench } from 'lucide-react';

// This would normally come from props/API
const defaultContent = {
  "business": {
    "name": "Austin Elite HVAC",
    "phone": "(512) 555-COOL",
    "email": "info@austinelitehvac.com",
    "address": "123 Main St",
    "hours": "Mon-Fri 7AM-8PM, Sat-Sun 8AM-6PM, 24/7 Emergency Service",
    "description": "Premier HVAC services for Austin homes and businesses. Specializing in energy-efficient installations, emergency repairs, and preventative maintenance.",
    "serviceAreas": [
      "Austin",
      "Round Rock",
      "Cedar Park",
      "Pflugerville",
      "Georgetown"
    ]
  },
  "hero": {
    "headline": "Austin's Most Trusted HVAC Experts",
    "subtitle": "24/7 Emergency Service \u2022 Same-Day Repairs \u2022 100% Satisfaction Guaranteed \u2022 NATE Certified Technicians",
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
      "A+ BBB Rating",
      "NATE Certified",
      "5-Star Reviews"
    ],
    "showEmergencyBanner": true,
    "emergencyMessage": "\ud83d\udea8 HVAC Emergency? We're Available 24/7 - No Overtime Charges!"
  },
  "services": [
    {
      "title": "Emergency HVAC Repair",
      "description": "24/7 emergency heating and air conditioning repair throughout Austin metro.",
      "price": "From $149",
      "features": [
        "Same-day service",
        "All major brands",
        "Parts warranty",
        "Upfront pricing"
      ],
      "isPopular": true
    },
    {
      "title": "HVAC System Installation",
      "description": "Complete HVAC system installation and replacement with energy-efficient solutions.",
      "price": "Free Quote",
      "features": [
        "Energy-efficient systems",
        "Financing available",
        "10-year warranty"
      ]
    },
    {
      "title": "Preventative Maintenance",
      "description": "Preventive maintenance plans to keep your system running efficiently year-round.",
      "price": "From $199",
      "features": [
        "Bi-annual tune-ups",
        "Priority service",
        "20% off repairs"
      ]
    }
  ],
  "seo": {
    "title": "Austin Elite HVAC - Professional HVAC Services in Austin, TX | 24/7 Emergency Repair",
    "description": "Expert HVAC services in Austin, TX. 24/7 emergency AC & heating repair, installation, and maintenance. Licensed & insured NATE-certified technicians. Call (512) 555-COOL for same-day service and free estimates.",
    "keywords": [
      "hvac austin tx",
      "ac repair austin",
      "heating repair austin",
      "hvac installation austin",
      "emergency hvac austin",
      "austin hvac contractor",
      "nate certified hvac austin",
      "hvac maintenance austin"
    ]
  }
};



















































export default function Home() {
  const { business, hero, services, seo } = defaultContent;

  return (
    <Layout seo={seo} business={business}>
      {/* Navigation */}
      <Navigation business={business} />
      
      {/* Hero Section */}
      <div id="home">
        <Hero
          {...hero}
          business={business}
        />
      </div>

      {/* Services Section */}
      <section id="services" className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Our Professional HVAC Services</h2>
            <p className="text-gray-600 max-w-3xl mx-auto text-lg">
              From emergency repairs to complete system installations, we provide comprehensive HVAC solutions 
              for homes and businesses throughout the Austin area. All work backed by our 100% satisfaction guarantee.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {services.map((service, index) => (
              <ServiceCard 
                key={index} 
                {...service} 
                icon={
                  index === 0 ? <Thermometer className="w-6 h-6" /> :
                  index === 1 ? <Wind className="w-6 h-6" /> :
                  index === 2 ? <Shield className="w-6 h-6" /> :
                  <Wrench className="w-6 h-6" />
                }
              />
            ))}
          </div>
          
          {/* Service Features */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl p-6 shadow-lg text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Licensed & Insured</h3>
              <p className="text-gray-600">All technicians are fully licensed and insured for your protection and peace of mind.</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-lg text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Wrench className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Expert Technicians</h3>
              <p className="text-gray-600">NATE-certified professionals with ongoing training on the latest HVAC technology.</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-lg text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Thermometer className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">24/7 Emergency</h3>
              <p className="text-gray-600">Round-the-clock emergency service when you need it most, no overtime charges.</p>
            </div>
          </div>
        </div>
      </section>

      {/* About Us Section */}
      <AboutUs 
        business={{
          name: business.name,
          description: business.description
        }}
        stats={{
          yearsInBusiness: 25,
          customersServed: 5000,
          projectsCompleted: 8500,
          satisfactionRate: 98
        }}
      />

      {/* Reviews Section */}
      <Reviews 
        averageRating={4.9}
        totalReviews={247}
      />
      
      {/* Service Areas */}
      <ServiceAreas 
        primaryArea="Austin, TX"
        phone={business.phone}
      />
      
      {/* Booking Widget */}
      <BookingWidget 
        title="Schedule Your HVAC Service"
        subtitle="Pick a time that works for you"
        services={["AC Repair", "Heating Service", "Installation Consultation", "Maintenance Check"]}
        showPricing={true}
      />

      {/* Contact Form */}
      <div id="contact">
        <ContactForm 
          title="Get Your Free HVAC Quote Today"
          subtitle="Professional service, transparent pricing, no surprises"
          services={["AC Repair", "Heating Repair", "New Installation", "Maintenance", "Emergency Service"]}
          urgencyOptions={["Emergency (Within 1 hour)", "Today", "Tomorrow", "This Week", "Just Planning"]}
        />
      </div>

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