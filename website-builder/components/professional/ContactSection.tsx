'use client'

import React, { useState } from 'react'
import { Business } from '../../lib/types/business'
import { 
  Phone, 
  Mail, 
  MapPin, 
  Clock, 
  Send,
  User,
  MessageSquare
} from 'lucide-react'

interface ContactSectionProps {
  business: Business
}

interface FormData {
  name: string
  phone: string
  email: string
  address: string
  message: string
  service_needed: string
  preferred_contact: 'phone' | 'email'
  urgency: 'routine' | 'urgent' | 'emergency'
}

export default function ContactSection({ business }: ContactSectionProps) {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    phone: '',
    email: '',
    address: '',
    message: '',
    service_needed: '',
    preferred_contact: 'phone',
    urgency: 'routine'
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle')

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      // Here you would typically send the form data to your backend
      // For now, we'll simulate the submission
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setSubmitStatus('success')
      setFormData({
        name: '',
        phone: '',
        email: '',
        address: '',
        message: '',
        service_needed: '',
        preferred_contact: 'phone',
        urgency: 'routine'
      })
    } catch (error) {
      setSubmitStatus('error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleEmergencyCall = () => {
    window.location.href = `tel:${business.phone_number}`
  }

  return (
    <section id="contact" className="py-16 lg:py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            Get in Touch
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Feel free to contact us or book services. {business.name} – your best solution for accurate, immediate, and professional help with all of your service needs.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-16">
          
          {/* Contact Form */}
          <div className="bg-gray-50 rounded-2xl p-8">
            <div className="mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Request Service</h3>
              <p className="text-gray-600">
                Fill out the form below and we'll get back to you within 30 minutes during business hours.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Name and Phone */}
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                    Name *
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      id="name"
                      name="name"
                      required
                      value={formData.name}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Your full name"
                    />
                  </div>
                </div>
                
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                    Phone *
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <input
                      type="tel"
                      id="phone"
                      name="phone"
                      required
                      value={formData.phone}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="(555) 123-4567"
                    />
                  </div>
                </div>
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email *
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                  <input
                    type="email"
                    id="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="your@email.com"
                  />
                </div>
              </div>

              {/* Address */}
              <div>
                <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
                  Service Address
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    id="address"
                    name="address"
                    value={formData.address}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Where do you need service?"
                  />
                </div>
              </div>

              {/* Service Type and Urgency */}
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="service_needed" className="block text-sm font-medium text-gray-700 mb-2">
                    Service Needed
                  </label>
                  <input
                    type="text"
                    id="service_needed"
                    name="service_needed"
                    value={formData.service_needed}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g. AC Repair, Plumbing Installation"
                  />
                </div>
                
                <div>
                  <label htmlFor="urgency" className="block text-sm font-medium text-gray-700 mb-2">
                    Urgency Level
                  </label>
                  <select
                    id="urgency"
                    name="urgency"
                    value={formData.urgency}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="routine">Routine Service</option>
                    <option value="urgent">Urgent (Same Day)</option>
                    <option value="emergency">Emergency (ASAP)</option>
                  </select>
                </div>
              </div>

              {/* Message */}
              <div>
                <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                  Message *
                </label>
                <div className="relative">
                  <MessageSquare className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                  <textarea
                    id="message"
                    name="message"
                    required
                    rows={4}
                    value={formData.message}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Please describe your service needs in detail..."
                  />
                </div>
              </div>

              {/* Preferred Contact Method */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Contact Method
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="preferred_contact"
                      value="phone"
                      checked={formData.preferred_contact === 'phone'}
                      onChange={handleInputChange}
                      className="mr-2"
                    />
                    Phone Call
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="preferred_contact"
                      value="email"
                      checked={formData.preferred_contact === 'email'}
                      onChange={handleInputChange}
                      className="mr-2"
                    />
                    Email
                  </label>
                </div>
              </div>

              {/* Privacy Agreement */}
              <div className="text-sm text-gray-600 bg-white p-4 rounded-lg border">
                <p className="mb-2">
                  I agree to receive text messages from {business.name} at the phone number provided above. This includes SMS messages for appointment scheduling, appointment reminders, post-visit instructions, and billing notifications.
                </p>
                <p>
                  Reply STOP to opt-out. Reply HELP to {business.phone_number} for assistance. Message and data rates may apply.
                </p>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold py-4 px-8 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Submitting...
                  </>
                ) : (
                  <>
                    <Send className="h-5 w-5" />
                    Submit Request
                  </>
                )}
              </button>

              {/* Status Messages */}
              {submitStatus === 'success' && (
                <div className="bg-green-50 text-green-800 p-4 rounded-lg">
                  ✅ Thank you! Your request has been submitted. We'll contact you within 30 minutes.
                </div>
              )}
              
              {submitStatus === 'error' && (
                <div className="bg-red-50 text-red-800 p-4 rounded-lg">
                  ❌ Sorry, there was an error submitting your request. Please try again or call us directly.
                </div>
              )}
            </form>
          </div>

          {/* Contact Information */}
          <div className="space-y-8">
            
            {/* Business Info */}
            <div className="bg-blue-50 rounded-2xl p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Contact Information</h3>
              
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-blue-600 rounded-lg">
                    <Phone className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Phone</h4>
                    <p className="text-blue-600 font-bold text-lg">{business.phone_number}</p>
                    <p className="text-sm text-gray-600">24/7 Emergency Service Available</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="p-3 bg-blue-600 rounded-lg">
                    <MapPin className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Address</h4>
                    <p className="text-gray-700">{business.address}</p>
                    <p className="text-gray-700">{business.city}, {business.state} {business.zip_code}</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="p-3 bg-blue-600 rounded-lg">
                    <Mail className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Email</h4>
                    <p className="text-gray-700">{business.business_email}</p>
                    <p className="text-sm text-gray-600">We respond within 1 hour</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="p-3 bg-blue-600 rounded-lg">
                    <Clock className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Business Hours</h4>
                    <p className="text-gray-700">8am – 8pm Every Day</p>
                    <p className="text-sm text-gray-600">Customer support 24/7</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Emergency Call-to-Action */}
            <div className="bg-red-600 text-white rounded-2xl p-8 text-center">
              <h3 className="text-2xl font-bold mb-4">Emergency Service?</h3>
              <p className="text-red-100 mb-6">
                Don't wait! Call us now for immediate assistance with urgent service needs.
              </p>
              <button
                onClick={handleEmergencyCall}
                className="bg-white hover:bg-red-50 text-red-600 font-bold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2 mx-auto"
              >
                <Phone className="h-5 w-5" />
                Call Now: {business.phone_number}
              </button>
            </div>

            {/* Service Guarantees */}
            <div className="bg-green-50 rounded-2xl p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Our Promise</h3>
              <ul className="space-y-3">
                <li className="flex items-center gap-3">
                  <div className="w-6 h-6 bg-green-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">✓</span>
                  </div>
                  <span className="text-gray-700">24/7 Friendly Support</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-6 h-6 bg-green-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">✓</span>
                  </div>
                  <span className="text-gray-700">Professional Specialists</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-6 h-6 bg-green-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">✓</span>
                  </div>
                  <span className="text-gray-700">15+ Years Experience</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-6 h-6 bg-green-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">✓</span>
                  </div>
                  <span className="text-gray-700">Up to 12 Years Labor Warranty</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-6 h-6 bg-green-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">✓</span>
                  </div>
                  <span className="text-gray-700">Same-day Service Available</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
