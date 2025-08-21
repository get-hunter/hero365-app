"""
Next.js Template Components

TypeScript React components for generating Hero365 websites.
These components are used by the website builder to create
static sites with trade-specific optimizations.
"""

from typing import Dict, Any, List
from pathlib import Path


class NextJSComponentGenerator:
    """Generates Next.js TypeScript components for website templates."""
    
    @staticmethod
    def generate_hero_component() -> str:
        """Generate hero section component."""
        
        return '''import React from 'react';
import { Phone, Calendar, ArrowRight } from 'lucide-react';

interface HeroProps {
  headline: string;
  subheadline: string;
  ctaPrimary: string;
  ctaSecondary?: string;
  backgroundType: string;
  businessName: string;
  phoneNumber?: string;
  onPrimaryClick: () => void;
  onSecondaryClick?: () => void;
}

export const HeroSection: React.FC<HeroProps> = ({
  headline,
  subheadline,
  ctaPrimary,
  ctaSecondary,
  backgroundType,
  businessName,
  phoneNumber,
  onPrimaryClick,
  onSecondaryClick
}) => {
  const backgroundImages = {
    'commercial_mechanical': '/images/backgrounds/commercial-mechanical.jpg',
    'commercial_refrigeration': '/images/backgrounds/commercial-refrigeration.jpg',
    'commercial_plumbing': '/images/backgrounds/commercial-plumbing.jpg',
    'residential_hvac': '/images/backgrounds/residential-hvac.jpg',
    'residential_plumbing': '/images/backgrounds/residential-plumbing.jpg',
    'default': '/images/backgrounds/default-hero.jpg'
  };

  const backgroundImage = backgroundImages[backgroundType] || backgroundImages.default;

  return (
    <section 
      className="relative min-h-screen flex items-center justify-center bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url(${backgroundImage})` }}
    >
      <div className="container mx-auto px-4 text-center text-white">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
            {headline}
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-gray-200 max-w-3xl mx-auto">
            {subheadline}
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={onPrimaryClick}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-colors duration-200 flex items-center gap-2 min-w-[200px] justify-center"
            >
              <Phone className="w-5 h-5" />
              {ctaPrimary}
            </button>
            
            {ctaSecondary && onSecondaryClick && (
              <button
                onClick={onSecondaryClick}
                className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-gray-900 font-bold py-4 px-8 rounded-lg text-lg transition-colors duration-200 flex items-center gap-2 min-w-[200px] justify-center"
              >
                <Calendar className="w-5 h-5" />
                {ctaSecondary}
              </button>
            )}
          </div>
          
          {phoneNumber && (
            <div className="mt-8">
              <a 
                href={`tel:${phoneNumber}`}
                className="text-2xl font-bold text-yellow-400 hover:text-yellow-300 transition-colors duration-200"
              >
                {phoneNumber}
              </a>
            </div>
          )}
        </div>
      </div>
      
      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <ArrowRight className="w-6 h-6 text-white rotate-90" />
      </div>
    </section>
  );
};'''
    
    @staticmethod
    def generate_emergency_banner_component() -> str:
        """Generate emergency banner component."""
        
        return '''import React from 'react';
import { AlertTriangle, Phone } from 'lucide-react';

interface EmergencyBannerProps {
  message: string;
  phoneNumber?: string;
  urgencyLevel: 'high' | 'critical';
  phoneDisplay: boolean;
}

export const EmergencyBanner: React.FC<EmergencyBannerProps> = ({
  message,
  phoneNumber,
  urgencyLevel,
  phoneDisplay
}) => {
  const urgencyColors = {
    high: 'bg-orange-600 border-orange-500',
    critical: 'bg-red-600 border-red-500'
  };

  const urgencyClass = urgencyColors[urgencyLevel] || urgencyColors.high;

  return (
    <div className={`${urgencyClass} text-white py-3 px-4 border-l-4 sticky top-0 z-50 shadow-lg`}>
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 animate-pulse" />
          <span className="font-semibold text-lg">{message}</span>
        </div>
        
        {phoneDisplay && phoneNumber && (
          <a
            href={`tel:${phoneNumber}`}
            className="bg-white text-gray-900 hover:bg-gray-100 font-bold py-2 px-6 rounded-lg transition-colors duration-200 flex items-center gap-2"
          >
            <Phone className="w-4 h-4" />
            Call Now
          </a>
        )}
      </div>
    </div>
  );
};'''
    
    @staticmethod
    def generate_services_grid_component() -> str:
        """Generate services grid component."""
        
        return '''import React from 'react';
import { CheckCircle, ArrowRight } from 'lucide-react';

interface ServicesGridProps {
  services: string[];
  onServiceClick?: (service: string) => void;
}

export const ServicesGrid: React.FC<ServicesGridProps> = ({
  services,
  onServiceClick
}) => {
  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Our Professional Services
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Comprehensive solutions delivered by licensed, insured professionals with years of experience
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {services.map((service, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow duration-300 cursor-pointer group"
              onClick={() => onServiceClick?.(service)}
            >
              <div className="flex items-start gap-4">
                <CheckCircle className="w-8 h-8 text-green-600 flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors duration-200">
                    {service}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Professional {service.toLowerCase()} services with guaranteed satisfaction and upfront pricing.
                  </p>
                  <div className="flex items-center text-blue-600 font-semibold group-hover:text-blue-700">
                    <span>Learn More</span>
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-200" />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};'''
    
    @staticmethod
    def generate_quick_quote_component() -> str:
        """Generate quick quote form component."""
        
        return '''import React, { useState } from 'react';
import { Send, User, MapPin, Wrench, Clock } from 'lucide-react';

interface QuickQuoteProps {
  title: string;
  fields: string[];
  leadType: string;
  onSubmit: (data: any) => void;
}

export const QuickQuote: React.FC<QuickQuoteProps> = ({
  title,
  fields,
  leadType,
  onSubmit
}) => {
  const [formData, setFormData] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fieldConfigs = {
    business_name: { label: 'Business Name', type: 'text', icon: User, required: true },
    facility_type: { label: 'Facility Type', type: 'select', icon: MapPin, required: true,
      options: ['Office Building', 'Restaurant', 'Retail Store', 'Warehouse', 'Manufacturing', 'Other'] },
    square_footage: { label: 'Square Footage', type: 'select', icon: MapPin, required: false,
      options: ['Under 1,000 sq ft', '1,000-5,000 sq ft', '5,000-10,000 sq ft', '10,000-25,000 sq ft', 'Over 25,000 sq ft'] },
    service_needed: { label: 'Service Needed', type: 'textarea', icon: Wrench, required: true },
    timeline: { label: 'Timeline', type: 'select', icon: Clock, required: true,
      options: ['Emergency (ASAP)', 'Within 24 hours', 'Within a week', 'Within a month', 'Planning ahead'] },
    contact_info: { label: 'Contact Information', type: 'group', required: true },
    home_details: { label: 'Home Details', type: 'group', required: false },
    issue_description: { label: 'Describe the Issue', type: 'textarea', icon: Wrench, required: true },
    location_in_home: { label: 'Location in Home', type: 'text', icon: MapPin, required: false },
    urgency: { label: 'Urgency Level', type: 'select', icon: Clock, required: true,
      options: ['Emergency', 'Same day', 'Within 24 hours', 'Within a week', 'Not urgent'] },
    preferred_time: { label: 'Preferred Time', type: 'select', icon: Clock, required: false,
      options: ['Morning (8AM-12PM)', 'Afternoon (12PM-5PM)', 'Evening (5PM-8PM)', 'Anytime'] }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await onSubmit({
        ...formData,
        leadType,
        submittedAt: new Date().toISOString()
      });
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderField = (fieldName: string) => {
    const config = fieldConfigs[fieldName];
    if (!config) return null;

    const Icon = config.icon;

    if (config.type === 'group') {
      if (fieldName === 'contact_info') {
        return (
          <div key={fieldName} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Name *
                </label>
                <input
                  type="text"
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone *
                </label>
                <input
                  type="tel"
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>
          </div>
        );
      }
      return null;
    }

    return (
      <div key={fieldName}>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <div className="flex items-center gap-2">
            {Icon && <Icon className="w-4 h-4" />}
            {config.label} {config.required && '*'}
          </div>
        </label>
        
        {config.type === 'select' ? (
          <select
            required={config.required}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            onChange={(e) => setFormData({...formData, [fieldName]: e.target.value})}
          >
            <option value="">Select {config.label}</option>
            {config.options?.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        ) : config.type === 'textarea' ? (
          <textarea
            required={config.required}
            rows={4}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={`Describe your ${config.label.toLowerCase()}...`}
            onChange={(e) => setFormData({...formData, [fieldName]: e.target.value})}
          />
        ) : (
          <input
            type={config.type}
            required={config.required}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            onChange={(e) => setFormData({...formData, [fieldName]: e.target.value})}
          />
        )}
      </div>
    );
  };

  return (
    <section className="py-16 bg-blue-50">
      <div className="container mx-auto px-4">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
              {title}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {fields.map(renderField)}
              
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold py-4 px-6 rounded-lg text-lg transition-colors duration-200 flex items-center justify-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Submitting...
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    Get My Quote
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
};'''
    
    @staticmethod
    def generate_booking_widget_component() -> str:
        """Generate booking widget component."""
        
        return '''import React, { useState } from 'react';
import { Calendar, Clock, User, MapPin, Phone } from 'lucide-react';

interface BookingWidgetProps {
  title: string;
  serviceTypes: string[];
  timeSlots: string;
  leadType: string;
  onBooking: (data: any) => void;
}

export const BookingWidget: React.FC<BookingWidgetProps> = ({
  title,
  serviceTypes,
  timeSlots,
  leadType,
  onBooking
}) => {
  const [step, setStep] = useState(1);
  const [bookingData, setBookingData] = useState({
    serviceType: '',
    date: '',
    time: '',
    customerInfo: {},
    notes: ''
  });

  const timeSlotOptions = {
    business_hours: [
      '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM',
      '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM'
    ],
    business_hours_plus_emergency: [
      '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM',
      '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM',
      'Emergency (ASAP)'
    ]
  };

  const availableSlots = timeSlotOptions[timeSlots] || timeSlotOptions.business_hours;

  const handleNext = () => {
    if (step < 3) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = async () => {
    try {
      await onBooking({
        ...bookingData,
        leadType,
        submittedAt: new Date().toISOString()
      });
    } catch (error) {
      console.error('Booking submission error:', error);
    }
  };

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
              {title}
            </h2>
            
            {/* Progress indicator */}
            <div className="flex justify-center mb-8">
              <div className="flex items-center space-x-4">
                {[1, 2, 3].map((stepNum) => (
                  <div key={stepNum} className="flex items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                      step >= stepNum ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
                    }`}>
                      {stepNum}
                    </div>
                    {stepNum < 3 && (
                      <div className={`w-12 h-1 mx-2 ${
                        step > stepNum ? 'bg-blue-600' : 'bg-gray-200'
                      }`} />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Step 1: Service Selection */}
            {step === 1 && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Select Service Type
                </h3>
                
                <div className="grid grid-cols-1 gap-4">
                  {serviceTypes.map((service) => (
                    <label key={service} className="cursor-pointer">
                      <input
                        type="radio"
                        name="serviceType"
                        value={service}
                        checked={bookingData.serviceType === service}
                        onChange={(e) => setBookingData({...bookingData, serviceType: e.target.value})}
                        className="sr-only"
                      />
                      <div className={`p-4 border-2 rounded-lg transition-colors ${
                        bookingData.serviceType === service
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}>
                        <span className="font-medium">{service}</span>
                      </div>
                    </label>
                  ))}
                </div>
                
                <button
                  onClick={handleNext}
                  disabled={!bookingData.serviceType}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  Continue
                </button>
              </div>
            )}

            {/* Step 2: Date & Time Selection */}
            {step === 2 && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Select Date & Time
                </h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred Date
                  </label>
                  <input
                    type="date"
                    min={new Date().toISOString().split('T')[0]}
                    value={bookingData.date}
                    onChange={(e) => setBookingData({...bookingData, date: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred Time
                  </label>
                  <select
                    value={bookingData.time}
                    onChange={(e) => setBookingData({...bookingData, time: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select time</option>
                    {availableSlots.map((slot) => (
                      <option key={slot} value={slot}>{slot}</option>
                    ))}
                  </select>
                </div>
                
                <div className="flex gap-4">
                  <button
                    onClick={handleBack}
                    className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 font-bold py-3 px-6 rounded-lg transition-colors"
                  >
                    Back
                  </button>
                  <button
                    onClick={handleNext}
                    disabled={!bookingData.date || !bookingData.time}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                  >
                    Continue
                  </button>
                </div>
              </div>
            )}

            {/* Step 3: Contact Information */}
            {step === 3 && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                  <Phone className="w-5 h-5" />
                  Contact Information
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Name *
                    </label>
                    <input
                      type="text"
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      onChange={(e) => setBookingData({
                        ...bookingData,
                        customerInfo: {...bookingData.customerInfo, name: e.target.value}
                      })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone *
                    </label>
                    <input
                      type="tel"
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      onChange={(e) => setBookingData({
                        ...bookingData,
                        customerInfo: {...bookingData.customerInfo, phone: e.target.value}
                      })}
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    onChange={(e) => setBookingData({
                      ...bookingData,
                      customerInfo: {...bookingData.customerInfo, email: e.target.value}
                    })}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Service Address *
                  </label>
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter the address where service is needed"
                    onChange={(e) => setBookingData({
                      ...bookingData,
                      customerInfo: {...bookingData.customerInfo, address: e.target.value}
                    })}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Additional Notes
                  </label>
                  <textarea
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Any additional details or special requirements..."
                    onChange={(e) => setBookingData({...bookingData, notes: e.target.value})}
                  />
                </div>
                
                <div className="flex gap-4">
                  <button
                    onClick={handleBack}
                    className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 font-bold py-3 px-6 rounded-lg transition-colors"
                  >
                    Back
                  </button>
                  <button
                    onClick={handleSubmit}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                  >
                    Book Service
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};'''
    
    @staticmethod
    def generate_contact_form_component() -> str:
        """Generate contact form component."""
        
        return '''import React, { useState } from 'react';
import { Send, User, Mail, Phone, MessageSquare } from 'lucide-react';

interface ContactFormProps {
  title: string;
  fields: string[];
  leadType: string;
  onSubmit: (data: any) => void;
}

export const ContactForm: React.FC<ContactFormProps> = ({
  title,
  fields,
  leadType,
  onSubmit
}) => {
  const [formData, setFormData] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await onSubmit({
        ...formData,
        leadType,
        submittedAt: new Date().toISOString()
      });
      setSubmitted(true);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-green-50 border border-green-200 rounded-lg p-8">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Send className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Thank You!
              </h2>
              <p className="text-gray-600 mb-6">
                Your message has been received. We'll get back to you within 2 hours during business hours.
              </p>
              <button
                onClick={() => setSubmitted(false)}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg transition-colors"
              >
                Send Another Message
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 bg-white">
      <div className="container mx-auto px-4">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              {title}
            </h2>
            <p className="text-xl text-gray-600">
              Get in touch with our team for professional service and free estimates
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    Name *
                  </div>
                </label>
                <input
                  type="text"
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4" />
                    Phone *
                  </div>
                </label>
                <input
                  type="tel"
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Email
                </div>
              </label>
              <input
                type="email"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Service Needed
              </label>
              <select
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onChange={(e) => setFormData({...formData, serviceType: e.target.value})}
              >
                <option value="">Select a service</option>
                <option value="repair">Repair Service</option>
                <option value="installation">Installation</option>
                <option value="maintenance">Maintenance</option>
                <option value="emergency">Emergency Service</option>
                <option value="consultation">Consultation</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Message *
                </div>
              </label>
              <textarea
                required
                rows={5}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Please describe your needs or questions..."
                onChange={(e) => setFormData({...formData, message: e.target.value})}
              />
            </div>
            
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold py-4 px-6 rounded-lg text-lg transition-colors duration-200 flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Sending...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Send Message
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
};'''
    
    @staticmethod
    def generate_page_template() -> str:
        """Generate Next.js page template."""
        
        return '''import React from 'react';
import Head from 'next/head';
import { HeroSection } from '../components/HeroSection';
import { EmergencyBanner } from '../components/EmergencyBanner';
import { ServicesGrid } from '../components/ServicesGrid';
import { QuickQuote } from '../components/QuickQuote';
import { BookingWidget } from '../components/BookingWidget';
import { ContactForm } from '../components/ContactForm';

interface PageProps {
  pageData: any;
  businessData: any;
  brandingData: any;
}

const Page: React.FC<PageProps> = ({ pageData, businessData, brandingData }) => {
  const handleFormSubmit = async (formData: any) => {
    try {
      const response = await fetch('/api/forms/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          websiteId: businessData.websiteId,
          businessId: businessData.id,
          formType: formData.leadType,
          formData: formData,
          visitorInfo: {
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            page: window.location.pathname
          }
        }),
      });

      if (!response.ok) {
        throw new Error('Form submission failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Form submission error:', error);
      throw error;
    }
  };

  const handleBooking = async (bookingData: any) => {
    try {
      const response = await fetch('/api/bookings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          websiteId: businessData.websiteId,
          serviceType: bookingData.serviceType,
          appointmentDate: bookingData.date,
          startTime: bookingData.time,
          durationMinutes: 60,
          customerName: bookingData.customerInfo.name,
          customerEmail: bookingData.customerInfo.email,
          customerPhone: bookingData.customerInfo.phone,
          serviceAddress: bookingData.customerInfo.address,
          bookingNotes: bookingData.notes
        }),
      });

      if (!response.ok) {
        throw new Error('Booking submission failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Booking submission error:', error);
      throw error;
    }
  };

  const renderSection = (section: any) => {
    switch (section.type) {
      case 'hero':
        return (
          <HeroSection
            key={section.type}
            headline={section.config.headline.replace('{{business_name}}', businessData.name)}
            subheadline={section.config.subheadline}
            ctaPrimary={section.config.cta_primary}
            ctaSecondary={section.config.cta_secondary}
            backgroundType={section.config.background_type}
            businessName={businessData.name}
            phoneNumber={businessData.phone}
            onPrimaryClick={() => {
              if (businessData.phone) {
                window.location.href = `tel:${businessData.phone}`;
              }
            }}
            onSecondaryClick={() => {
              const bookingSection = document.getElementById('booking');
              if (bookingSection) {
                bookingSection.scrollIntoView({ behavior: 'smooth' });
              }
            }}
          />
        );

      case 'emergency-banner':
        return (
          <EmergencyBanner
            key={section.type}
            message={section.config.message}
            phoneNumber={businessData.phone}
            urgencyLevel={section.config.urgency_level}
            phoneDisplay={section.config.phone_display}
          />
        );

      case 'services-grid':
        return (
          <ServicesGrid
            key={section.type}
            services={section.config.services}
            onServiceClick={(service) => {
              // Scroll to contact form or booking
              const contactSection = document.getElementById('contact');
              if (contactSection) {
                contactSection.scrollIntoView({ behavior: 'smooth' });
              }
            }}
          />
        );

      case 'quick-quote':
        return (
          <QuickQuote
            key={section.type}
            title={section.config.title}
            fields={section.config.fields}
            leadType={section.config.lead_type}
            onSubmit={handleFormSubmit}
          />
        );

      case 'booking-widget':
        return (
          <div key={section.type} id="booking">
            <BookingWidget
              title={section.config.title}
              serviceTypes={section.config.service_types}
              timeSlots={section.config.time_slots}
              leadType={section.config.lead_type}
              onBooking={handleBooking}
            />
          </div>
        );

      case 'contact-form':
        return (
          <div key={section.type} id="contact">
            <ContactForm
              title={section.config.title}
              fields={section.config.fields}
              leadType={section.config.lead_type}
              onSubmit={handleFormSubmit}
            />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <>
      <Head>
        <title>{pageData.title.replace('{{business_name}}', businessData.name)}</title>
        <meta name="description" content={pageData.metaDescription} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        
        {/* Open Graph */}
        <meta property="og:title" content={pageData.title.replace('{{business_name}}', businessData.name)} />
        <meta property="og:description" content={pageData.metaDescription} />
        <meta property="og:type" content="website" />
        
        {/* Schema.org structured data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "LocalBusiness",
              "name": businessData.name,
              "description": pageData.metaDescription,
              "telephone": businessData.phone,
              "address": {
                "@type": "PostalAddress",
                "addressLocality": businessData.city,
                "addressRegion": businessData.state,
                "postalCode": businessData.zipCode
              },
              "serviceArea": businessData.serviceAreas,
              "priceRange": "$$"
            })
          }}
        />
      </Head>

      <main>
        {pageData.sections.map(renderSection)}
      </main>
    </>
  );
};

export default Page;'''

    @staticmethod
    def generate_layout_component() -> str:
        """Generate Next.js layout component."""
        
        return '''import React from 'react';
import { Phone, Mail, MapPin, Clock } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  businessData: any;
  brandingData: any;
}

const Layout: React.FC<LayoutProps> = ({ children, businessData, brandingData }) => {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-40">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                {businessData.name}
              </h1>
            </div>
            
            <div className="hidden md:flex items-center space-x-6">
              {businessData.phone && (
                <a
                  href={`tel:${businessData.phone}`}
                  className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors"
                >
                  <Phone className="w-4 h-4" />
                  {businessData.phone}
                </a>
              )}
              
              <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition-colors">
                Get Quote
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">{businessData.name}</h3>
              <p className="text-gray-300 mb-4">
                Professional {businessData.primaryTrade} services with guaranteed satisfaction.
              </p>
              <div className="flex items-center gap-2 text-gray-300">
                <Clock className="w-4 h-4" />
                <span>24/7 Emergency Service Available</span>
              </div>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold mb-4">Contact Info</h4>
              <div className="space-y-3">
                {businessData.phone && (
                  <div className="flex items-center gap-2 text-gray-300">
                    <Phone className="w-4 h-4" />
                    <a href={`tel:${businessData.phone}`} className="hover:text-white transition-colors">
                      {businessData.phone}
                    </a>
                  </div>
                )}
                
                {businessData.email && (
                  <div className="flex items-center gap-2 text-gray-300">
                    <Mail className="w-4 h-4" />
                    <a href={`mailto:${businessData.email}`} className="hover:text-white transition-colors">
                      {businessData.email}
                    </a>
                  </div>
                )}
                
                {businessData.address && (
                  <div className="flex items-center gap-2 text-gray-300">
                    <MapPin className="w-4 h-4" />
                    <span>{businessData.address}</span>
                  </div>
                )}
              </div>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold mb-4">Service Areas</h4>
              <div className="text-gray-300">
                {businessData.serviceAreas?.map((area: string, index: number) => (
                  <div key={index}>{area}</div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; {new Date().getFullYear()} {businessData.name}. All rights reserved.</p>
            <p className="mt-2">Licensed, Bonded & Insured</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;'''
