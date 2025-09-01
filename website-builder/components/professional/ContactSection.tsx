import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Phone, Mail, MapPin, Clock, MessageSquare } from 'lucide-react';
import { BusinessData, Location } from '../../lib/data-loader';
import { formatPhoneForDisplay, normalizeToE164 } from '../../lib/phone';

interface ContactSectionProps {
  business: BusinessData;
  locations: Location[];
}

export default function ContactSection({ business, locations = [] }: ContactSectionProps) {
  const primaryLocation = locations.find(l => l.is_primary) || locations[0];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            Get In Touch Today
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Ready to get started? Contact us for a free consultation and estimate. 
            We're here to help with all your service needs.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Contact Form */}
          <Card className="shadow-xl">
            <CardHeader>
              <CardTitle className="text-2xl font-bold text-gray-900">
                Request Free Estimate
              </CardTitle>
              <p className="text-gray-600">
                Fill out the form below and we'll get back to you within 24 hours.
              </p>
            </CardHeader>
            <CardContent>
              <form className="space-y-6">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-2">
                      First Name *
                    </label>
                    <input
                      type="text"
                      id="firstName"
                      name="firstName"
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="John"
                    />
                  </div>
                  <div>
                    <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-2">
                      Last Name *
                    </label>
                    <input
                      type="text"
                      id="lastName"
                      name="lastName"
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Doe"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="john@example.com"
                  />
                </div>

                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    id="phone"
                    name="phone"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="(555) 123-4567"
                  />
                </div>

                <div>
                  <label htmlFor="service" className="block text-sm font-medium text-gray-700 mb-2">
                    Service Needed
                  </label>
                  <select
                    id="service"
                    name="service"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select a service...</option>
                    {(business.trades || []).map((trade) => (
                      <option key={trade} value={trade}>
                        {trade.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                    Project Details
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    rows={4}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Please describe your project or service needs..."
                  />
                </div>

                {/* SMS Consent */}
                <div className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    id="smsConsent"
                    name="smsConsent"
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="smsConsent" className="text-sm text-gray-600">
                    I consent to receive SMS messages for appointment reminders and service updates. 
                    Message and data rates may apply. Reply STOP to opt out.
                  </label>
                </div>

                <Button type="submit" size="lg" className="w-full bg-blue-600 hover:bg-blue-700">
                  <MessageSquare className="w-5 h-5 mr-2" />
                  Send Message
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <div className="space-y-8">
            {/* Quick Contact */}
            <Card className="shadow-lg">
              <CardContent className="p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">
                  Contact Information
                </h3>
                
                <div className="space-y-6">
                  {/* Phone */}
                  {business.phone_number && (
                    <div className="flex items-center space-x-4">
                      <div className="bg-blue-100 p-3 rounded-full">
                        <Phone className="w-6 h-6 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">Call Us</p>
                        <a 
                          href={`tel:${normalizeToE164(business.phone_number)}`}
                          className="text-blue-600 hover:text-blue-800 text-lg font-medium"
                        >
                          {formatPhoneForDisplay(business.phone_number)}
                        </a>
                      </div>
                    </div>
                  )}

                  {/* Email */}
                  {business.business_email && (
                    <div className="flex items-center space-x-4">
                      <div className="bg-green-100 p-3 rounded-full">
                        <Mail className="w-6 h-6 text-green-600" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">Email Us</p>
                        <a 
                          href={`mailto:${business.business_email}`}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          {business.business_email}
                        </a>
                      </div>
                    </div>
                  )}

                  {/* Address */}
                  {primaryLocation && (
                    <div className="flex items-start space-x-4">
                      <div className="bg-orange-100 p-3 rounded-full">
                        <MapPin className="w-6 h-6 text-orange-600" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">Visit Us</p>
                        <p className="text-gray-600">
                          {primaryLocation.address}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Business Hours */}
                  {business.business_hours && (
                    <div className="flex items-start space-x-4">
                      <div className="bg-purple-100 p-3 rounded-full">
                        <Clock className="w-6 h-6 text-purple-600" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">Business Hours</p>
                        <div className="text-gray-600 text-sm">
                          <p>Monday - Friday: 8:00 AM - 6:00 PM</p>
                          <p>Saturday: 9:00 AM - 4:00 PM</p>
                          <p>Sunday: Emergency Only</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Emergency Contact */}
            <Card className="shadow-lg bg-red-50 border-red-200">
              <CardContent className="p-8 text-center">
                <h3 className="text-2xl font-bold text-red-800 mb-4">
                  24/7 Emergency Service
                </h3>
                <p className="text-red-700 mb-6">
                  Need immediate assistance? Our emergency team is standing by.
                </p>
                <Button size="lg" className="bg-red-600 hover:bg-red-700 text-white">
                  <Phone className="w-5 h-5 mr-2" />
                  Call Emergency Line
                </Button>
              </CardContent>
            </Card>

            {/* Service Areas */}
            {business.service_areas && business.service_areas.length > 0 && (
              <Card className="shadow-lg">
                <CardContent className="p-8">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">
                    Service Areas
                  </h3>
                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                    {business.service_areas.slice(0, 8).map((area, index) => (
                      <div key={index} className="flex items-center">
                        <MapPin className="w-3 h-3 mr-2 text-blue-600" />
                        {area}
                      </div>
                    ))}
                  </div>
                  {business.service_areas.length > 8 && (
                    <p className="text-sm text-gray-500 mt-2">
                      And {business.service_areas.length - 8} more areas
                    </p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}