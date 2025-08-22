import React, { useState } from 'react';
import { Send, User, Mail, Phone, MessageSquare, Calendar, DollarSign, Home } from 'lucide-react';

interface ContactFormProps {
  title?: string;
  subtitle?: string;
  fields?: string[];
  services?: string[];
  urgencyOptions?: string[];
  budgetOptions?: string[];
  apiEndpoint?: string;
}

export default function ContactForm({
  title = 'Get Your Free Quote',
  subtitle = 'Fill out the form below and we\'ll get back to you within 24 hours',
  fields = ['name', 'email', 'phone', 'service', 'urgency', 'description'],
  services = [],
  urgencyOptions = ['Emergency (ASAP)', 'Within 24 hours', 'Within a week', 'Within a month', 'Just planning'],
  budgetOptions = ['Under $500', '$500-$1,000', '$1,000-$5,000', '$5,000-$10,000', '$10,000+', 'Not sure'],
  apiEndpoint = '/api/contact',
}: ContactFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    service: '',
    urgency: '',
    budget: '',
    address: '',
    description: '',
    preferredContact: 'phone',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // In production, this would send to the actual API
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        setSubmitStatus('success');
        setFormData({
          name: '',
          email: '',
          phone: '',
          service: '',
          urgency: '',
          budget: '',
          address: '',
          description: '',
          preferredContact: 'phone',
        });
      } else {
        setSubmitStatus('error');
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-3xl font-bold text-center mb-2">{title}</h2>
          {subtitle && (
            <p className="text-gray-600 text-center mb-8">{subtitle}</p>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Name Field */}
              {fields.includes('name') && (
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <User className="w-4 h-4" />
                    Full Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="John Doe"
                  />
                </div>
              )}
              
              {/* Email Field */}
              {fields.includes('email') && (
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <Mail className="w-4 h-4" />
                    Email Address *
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="john@example.com"
                  />
                </div>
              )}
              
              {/* Phone Field */}
              {fields.includes('phone') && (
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <Phone className="w-4 h-4" />
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="(555) 123-4567"
                  />
                </div>
              )}
              
              {/* Service Field */}
              {fields.includes('service') && services.length > 0 && (
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <MessageSquare className="w-4 h-4" />
                    Service Needed *
                  </label>
                  <select
                    name="service"
                    value={formData.service}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select a service</option>
                    {services.map((service) => (
                      <option key={service} value={service}>
                        {service}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              
              {/* Urgency Field */}
              {fields.includes('urgency') && (
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <Calendar className="w-4 h-4" />
                    When do you need service? *
                  </label>
                  <select
                    name="urgency"
                    value={formData.urgency}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select timeframe</option>
                    {urgencyOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              
              {/* Budget Field */}
              {fields.includes('budget') && (
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <DollarSign className="w-4 h-4" />
                    Budget Range
                  </label>
                  <select
                    name="budget"
                    value={formData.budget}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select budget</option>
                    {budgetOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              
              {/* Address Field */}
              {fields.includes('address') && (
                <div className="md:col-span-2">
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <Home className="w-4 h-4" />
                    Service Address
                  </label>
                  <input
                    type="text"
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="123 Main St, City, State ZIP"
                  />
                </div>
              )}
            </div>
            
            {/* Description Field */}
            {fields.includes('description') && (
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                  <MessageSquare className="w-4 h-4" />
                  Describe your project or issue *
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  required
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Please provide details about what you need help with..."
                />
              </div>
            )}
            
            {/* Preferred Contact Method */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Preferred Contact Method
              </label>
              <div className="flex gap-4">
                {['phone', 'email', 'text'].map((method) => (
                  <label key={method} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="preferredContact"
                      value={method}
                      checked={formData.preferredContact === method}
                      onChange={handleChange}
                      className="text-blue-600"
                    />
                    <span className="capitalize">{method}</span>
                  </label>
                ))}
              </div>
            </div>
            
            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className={`
                w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all duration-200 flex items-center justify-center gap-2
                ${isSubmitting 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl'
                }
              `}
            >
              {isSubmitting ? (
                <>Processing...</>
              ) : (
                <>
                  Get Free Quote
                  <Send className="w-5 h-5" />
                </>
              )}
            </button>
            
            {/* Status Messages */}
            {submitStatus === 'success' && (
              <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
                ✓ Thank you! We'll contact you within 24 hours.
              </div>
            )}
            {submitStatus === 'error' && (
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
                ✗ Something went wrong. Please try again or call us directly.
              </div>
            )}
          </form>
        </div>
      </div>
    </section>
  );
}
