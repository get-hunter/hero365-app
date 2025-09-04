import { TemplateConfig } from '../types';

export const hvacResidentialTemplate: TemplateConfig = {
  id: 'residential-hvac',
  trade: 'HVAC',
  category: 'RESIDENTIAL',
  name: 'Residential HVAC Services',
  description: 'Professional HVAC template for residential heating and cooling services',
  
  // Content fields that can be filled by AI or user
  contentFields: {
    business: {
      name: { type: 'text', required: true },
      phone: { type: 'phone', required: true },
      email: { type: 'email', required: true },
      address: { type: 'text', required: true },
      hours: { type: 'text', default: 'Mon-Fri 8AM-6PM, Sat 9AM-4PM' },
      description: { type: 'textarea', required: true },
      serviceAreas: { type: 'array', required: true },
    },
    hero: {
      headline: { type: 'text', default: 'Your Comfort is Our Priority' },
      subtitle: { type: 'text', default: 'Professional HVAC services for your home' },
      ctaButtons: {
        type: 'array',
        default: [
          { text: 'Schedule Service', action: 'open_booking', style: 'primary' },
          { text: 'Get Free Estimate', action: 'open_quote_form', style: 'secondary' },
        ],
      },
      trustIndicators: {
        type: 'array',
        default: ['Licensed & Insured', 'Same-Day Service', 'Free Estimates'],
      },
      showEmergencyBanner: { type: 'boolean', default: true },
      emergencyMessage: { type: 'text', default: '24/7 Emergency HVAC Service - No Overtime Charges' },
    },
    services: {
      list: {
        type: 'array',
        default: [
          {
            title: 'AC Repair & Installation',
            description: 'Expert cooling system services to keep your home comfortable',
            price: 'From $89',
            features: ['24/7 Emergency Service', 'All Brands Serviced', 'Warranty Included'],
            isPopular: true,
          },
          {
            title: 'Heating System Service',
            description: 'Furnace repair, maintenance, and installation',
            price: 'From $99',
            features: ['Energy Efficiency Analysis', 'Safety Inspection', 'Same-Day Service'],
          },
          {
            title: 'Ductwork & Air Quality',
            description: 'Improve your home\'s air quality and efficiency',
            price: 'Free Inspection',
            features: ['Duct Cleaning', 'Air Purification', 'Humidity Control'],
          },
          {
            title: 'Preventive Maintenance',
            description: 'Keep your HVAC system running efficiently year-round',
            price: '$19/month',
            features: ['Bi-Annual Tune-ups', 'Priority Service', '15% Off Repairs'],
          },
        ],
      },
    },
    contact: {
      title: { type: 'text', default: 'Get Your Free HVAC Estimate' },
      subtitle: { type: 'text', default: 'No obligation, honest pricing' },
      services: {
        type: 'array',
        default: ['AC Repair', 'Heating Repair', 'New Installation', 'Maintenance', 'Emergency Service'],
      },
      urgencyOptions: {
        type: 'array',
        default: ['Emergency (ASAP)', 'Within 24 hours', 'Within a week', 'Within a month', 'Just planning'],
      },
    },
    booking: {
      title: { type: 'text', default: 'Schedule Your HVAC Service' },
      subtitle: { type: 'text', default: 'Choose a convenient time that works for you' },
      services: {
        type: 'array',
        default: ['Repair', 'Maintenance', 'Installation', 'Consultation'],
      },
      showPricing: { type: 'boolean', default: true },
    },
    seo: {
      title: { type: 'text', generate: true },
      description: { type: 'text', generate: true },
      keywords: {
        type: 'array',
        default: ['hvac repair', 'air conditioning', 'heating services', 'furnace repair', 'ac installation'],
      },
    },
  },
  
  // Page structure
  pages: [
    {
      path: '/',
      name: 'Home',
      sections: [
        { component: 'Hero', props: 'hero' },
        { component: 'ServiceGrid', props: 'services' },
        { component: 'BookingWidget', props: 'booking' },
        { component: 'ContactForm', props: 'contact' },
      ],
    },
  ],
  
  // Theme configuration
  theme: {
    primaryColor: '#3B82F6', // Blue
    secondaryColor: '#10B981', // Green
    fontFamily: 'Inter, system-ui, sans-serif',
  },
}
