'use client';

import React from 'react';
import Layout from '@/components/base/Layout';
import Navigation from '@/components/base/Navigation';
import ContactForm from '@/components/base/ContactForm';
import BookingWidget from '@/components/base/BookingWidget';
import ServiceAreas from '@/components/base/ServiceAreas';
import { Phone, Mail, MapPin, Clock, MessageCircle } from 'lucide-react';

export default function ContactPage() {
  const business = {
    name: "Austin Elite HVAC",
    phone: "(512) 555-COOL",
    email: "service@austinelitehvac.com",
    address: "456 Tech Ridge Blvd, Austin, TX 78753",
    hours: "Mon-Fri 7AM-8PM, Sat-Sun 8AM-6PM, 24/7 Emergency Service"
  };

  const seo = {
    title: "Contact Austin Elite HVAC | Call (512) 555-COOL for HVAC Service",
    description: "Contact Austin Elite HVAC for professional HVAC service. Call (512) 555-COOL, email, or book online. 24/7 emergency service available in Austin, TX.",
    keywords: ["contact austin elite hvac", "hvac service austin", "emergency hvac", "hvac phone number austin"]
  };

  return (
    <Layout seo={seo} business={business}>
      <Navigation business={business} />
      
      {/* Page Header */}
      <section className="bg-gradient-to-r from-blue-600 to-green-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Contact Us</h1>
          <p className="text-xl md:text-2xl mb-6 max-w-3xl mx-auto">
            Get in touch for professional HVAC service in Austin
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href={`tel:${business.phone}`}
              className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors duration-200 inline-flex items-center justify-center gap-2"
            >
              <Phone className="w-6 h-6" />
              Call {business.phone}
            </a>
            <a
              href={`mailto:${business.email}`}
              className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-blue-600 transition-colors duration-200 inline-flex items-center justify-center gap-2"
            >
              <Mail className="w-6 h-6" />
              Email Us
            </a>
          </div>
        </div>
      </section>

      {/* Contact Information */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            
            {/* Contact Details */}
            <div>
              <h2 className="text-3xl font-bold mb-8">Get In Touch</h2>
              
              <div className="space-y-6">
                {/* Phone */}
                <div className="flex items-start gap-4 p-6 bg-blue-50 rounded-xl">
                  <div className="bg-blue-600 text-white p-3 rounded-lg">
                    <Phone className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Call Us</h3>
                    <p className="text-gray-600 mb-2">For immediate service or emergency repairs</p>
                    <a href={`tel:${business.phone}`} className="text-2xl font-bold text-blue-600 hover:text-blue-700">
                      {business.phone}
                    </a>
                    <p className="text-sm text-gray-500 mt-1">Available 24/7 for emergencies</p>
                  </div>
                </div>

                {/* Email */}
                <div className="flex items-start gap-4 p-6 bg-green-50 rounded-xl">
                  <div className="bg-green-600 text-white p-3 rounded-lg">
                    <Mail className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Email Us</h3>
                    <p className="text-gray-600 mb-2">For quotes, questions, or scheduling</p>
                    <a href={`mailto:${business.email}`} className="text-lg font-semibold text-green-600 hover:text-green-700">
                      {business.email}
                    </a>
                    <p className="text-sm text-gray-500 mt-1">We respond within 2 hours during business hours</p>
                  </div>
                </div>

                {/* Address */}
                <div className="flex items-start gap-4 p-6 bg-orange-50 rounded-xl">
                  <div className="bg-orange-600 text-white p-3 rounded-lg">
                    <MapPin className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Visit Us</h3>
                    <p className="text-gray-600 mb-2">Our office and warehouse location</p>
                    <p className="text-lg font-semibold text-orange-600">{business.address}</p>
                    <p className="text-sm text-gray-500 mt-1">By appointment only</p>
                  </div>
                </div>

                {/* Hours */}
                <div className="flex items-start gap-4 p-6 bg-purple-50 rounded-xl">
                  <div className="bg-purple-600 text-white p-3 rounded-lg">
                    <Clock className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Business Hours</h3>
                    <div className="space-y-1">
                      <p className="text-gray-700"><span className="font-medium">Monday - Friday:</span> 7:00 AM - 8:00 PM</p>
                      <p className="text-gray-700"><span className="font-medium">Saturday - Sunday:</span> 8:00 AM - 6:00 PM</p>
                      <p className="text-red-600 font-semibold mt-2">🚨 24/7 Emergency Service Available</p>
                    </div>
                  </div>
                </div>

                {/* Text/SMS */}
                <div className="flex items-start gap-4 p-6 bg-gray-50 rounded-xl">
                  <div className="bg-gray-600 text-white p-3 rounded-lg">
                    <MessageCircle className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Text Us</h3>
                    <p className="text-gray-600 mb-2">Quick questions or appointment requests</p>
                    <a href={`sms:${business.phone}`} className="text-lg font-semibold text-gray-600 hover:text-gray-700">
                      {business.phone}
                    </a>
                    <p className="text-sm text-gray-500 mt-1">Text for quick responses during business hours</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Map Placeholder */}
            <div>
              <h2 className="text-3xl font-bold mb-8">Find Us</h2>
              <div className="bg-gray-100 rounded-xl h-96 flex items-center justify-center relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-green-50"></div>
                <div className="relative z-10 text-center p-8">
                  <MapPin className="w-16 h-16 text-blue-600 mx-auto mb-4" />
                  <h3 className="text-xl font-bold mb-2">Service Area Map</h3>
                  <p className="text-gray-600 mb-4">
                    We serve Austin and surrounding areas within a 50-mile radius
                  </p>
                  <div className="grid grid-cols-2 gap-3 max-w-sm mx-auto">
                    {["Austin", "Round Rock", "Cedar Park", "Pflugerville"].map((area, index) => (
                      <div key={area} className="bg-white rounded-lg p-3 shadow-md">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                          <span className="font-medium text-sm">{area}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Quick Stats */}
              <div className="mt-8 grid grid-cols-2 gap-4">
                <div className="bg-blue-600 text-white p-6 rounded-xl text-center">
                  <div className="text-3xl font-bold mb-2">&lt; 30min</div>
                  <div className="text-sm">Average Response Time</div>
                </div>
                <div className="bg-green-600 text-white p-6 rounded-xl text-center">
                  <div className="text-3xl font-bold mb-2">24/7</div>
                  <div className="text-sm">Emergency Service</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Emergency Contact Section */}
      <section className="py-16 bg-red-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">HVAC Emergency?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Don't wait when your HVAC system fails. Our emergency technicians are standing by 24/7 to help.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href={`tel:${business.phone}`}
              className="bg-white text-red-600 px-8 py-4 rounded-lg font-bold text-xl hover:bg-gray-100 transition-colors duration-200 inline-flex items-center justify-center gap-2"
            >
              <Phone className="w-6 h-6" />
              Call Emergency Line
            </a>
            <a
              href={`sms:${business.phone}?body=HVAC Emergency - Please call ASAP`}
              className="border-2 border-white text-white px-8 py-4 rounded-lg font-bold text-xl hover:bg-white hover:text-red-600 transition-colors duration-200 inline-flex items-center justify-center gap-2"
            >
              <MessageCircle className="w-6 h-6" />
              Text Emergency
            </a>
          </div>
          <p className="text-sm mt-4 opacity-90">
            No overtime charges for emergency service calls
          </p>
        </div>
      </section>

      {/* Service Areas */}
      <ServiceAreas 
        primaryArea="Austin, TX"
        phone={business.phone}
      />

      {/* Booking Widget */}
      <BookingWidget
        title="Schedule Your Service Online"
        subtitle="Choose a convenient time for your HVAC service appointment"
        services={["AC Repair", "Heating Service", "Installation Consultation", "Maintenance Check", "Emergency Service"]}
        showPricing={true}
      />

      {/* Contact Form */}
      <ContactForm
        title="Send Us a Message"
        subtitle="Fill out the form below and we'll get back to you promptly"
        services={["AC Repair", "Heating Repair", "New Installation", "Maintenance", "Emergency Service", "General Question"]}
        urgencyOptions={["Emergency (ASAP)", "Today", "Tomorrow", "This Week", "Just Planning"]}
      />
    </Layout>
  );
}
