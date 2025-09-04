import { ActivityContentPack } from '../types';

export const hvacContentPacks: Record<string, ActivityContentPack> = {
  'ac-installation': {
    hero: {
      title: 'Professional AC Installation Services',
      subtitle: 'Stay cool with expert air conditioning installation from certified HVAC technicians',
      ctaLabel: 'Get Free Quote',
      icon: 'snowflake'
    },
    benefits: {
      heading: 'Why Choose Our AC Installation?',
      bullets: [
        'Licensed and insured HVAC technicians',
        'Energy-efficient system recommendations',
        'Proper sizing and load calculations',
        'Warranty on parts and labor',
        'Same-day service available',
        'Financing options available'
      ]
    },
    process: {
      heading: 'Our Installation Process',
      steps: [
        'Free in-home consultation and estimate',
        'System sizing and equipment selection',
        'Professional installation by certified techs',
        'System testing and commissioning',
        'Customer walkthrough and maintenance tips'
      ]
    },
    faqs: [
      {
        q: 'How long does AC installation take?',
        a: 'Most installations take 4-8 hours depending on system complexity and any required electrical or ductwork modifications.'
      },
      {
        q: 'Do you provide warranties?',
        a: 'Yes, we provide manufacturer warranties on equipment plus our own labor warranty for complete peace of mind.'
      },
      {
        q: 'What size AC unit do I need?',
        a: 'We perform detailed load calculations considering your home size, insulation, windows, and local climate to recommend the perfect size.'
      }
    ],
    seo: {
      titleTemplate: '{businessName} - Professional AC Installation in {city}',
      descriptionTemplate: 'Expert air conditioning installation services in {city}. Licensed HVAC technicians, energy-efficient systems, warranties included. Call {phone} for free quote.',
      keywords: ['ac installation', 'air conditioning installation', 'hvac installation', 'central air installation', 'cooling system installation']
    },
    schema: {
      serviceType: 'Air Conditioning Installation',
      description: 'Professional installation of residential and commercial air conditioning systems',
      category: 'HVAC Services'
    },
    pricing: {
      startingPrice: 3500,
      priceRange: '$3,500 - $8,000',
      unit: 'complete system'
    }
  },

  'ac-repair': {
    hero: {
      title: 'Fast AC Repair Services',
      subtitle: 'Emergency air conditioning repair available 24/7 to keep you comfortable',
      ctaLabel: 'Call Now',
      icon: 'wrench'
    },
    benefits: {
      heading: 'Expert AC Repair Services',
      bullets: [
        '24/7 emergency service available',
        'Diagnostic fee waived with repair',
        'All major brands serviced',
        'Upfront pricing with no surprises',
        'Same-day repairs when possible',
        '100% satisfaction guarantee'
      ]
    },
    process: {
      heading: 'Our Repair Process',
      steps: [
        'Emergency dispatch or scheduled appointment',
        'Comprehensive system diagnosis',
        'Transparent pricing before work begins',
        'Professional repair with quality parts',
        'System testing and performance verification'
      ]
    },
    faqs: [
      {
        q: 'Do you offer emergency AC repair?',
        a: 'Yes, we provide 24/7 emergency AC repair services because we know cooling failures don\'t wait for business hours.'
      },
      {
        q: 'How much does AC repair cost?',
        a: 'Repair costs vary by issue complexity. We provide upfront pricing after diagnosis, with no hidden fees.'
      },
      {
        q: 'Should I repair or replace my AC?',
        a: 'We\'ll help you decide based on your system\'s age, repair costs, and efficiency. Generally, if repairs cost more than 50% of replacement, we recommend upgrading.'
      }
    ],
    seo: {
      titleTemplate: '{businessName} - 24/7 AC Repair Services in {city}',
      descriptionTemplate: 'Emergency air conditioning repair in {city}. Fast, reliable HVAC repair services. Licensed technicians, upfront pricing. Call {phone} now.',
      keywords: ['ac repair', 'air conditioning repair', 'hvac repair', 'emergency ac repair', 'cooling system repair']
    },
    schema: {
      serviceType: 'Air Conditioning Repair',
      description: '24/7 emergency and scheduled air conditioning repair services',
      category: 'HVAC Services'
    },
    pricing: {
      startingPrice: 150,
      priceRange: '$150 - $800',
      unit: 'per repair'
    }
  },

  'hvac-maintenance': {
    hero: {
      title: 'HVAC Maintenance & Tune-Ups',
      subtitle: 'Keep your heating and cooling systems running efficiently with regular maintenance',
      ctaLabel: 'Schedule Service',
      icon: 'settings'
    },
    benefits: {
      heading: 'Benefits of Regular HVAC Maintenance',
      bullets: [
        'Extend equipment lifespan',
        'Improve energy efficiency',
        'Prevent costly breakdowns',
        'Maintain warranty coverage',
        'Better indoor air quality',
        'Priority scheduling for repairs'
      ]
    },
    process: {
      heading: 'Our Maintenance Service',
      steps: [
        'Comprehensive system inspection',
        'Clean and replace filters',
        'Check refrigerant levels and connections',
        'Test all electrical components',
        'Provide detailed service report'
      ]
    },
    faqs: [
      {
        q: 'How often should I service my HVAC system?',
        a: 'We recommend twice yearly - spring for cooling prep and fall for heating prep. This ensures optimal performance year-round.'
      },
      {
        q: 'What\'s included in maintenance?',
        a: 'Our comprehensive service includes inspection, cleaning, filter replacement, refrigerant check, electrical testing, and a detailed report.'
      },
      {
        q: 'Do you offer maintenance plans?',
        a: 'Yes, our maintenance plans include priority scheduling, discounted repairs, and regular tune-ups to keep your system running smoothly.'
      }
    ],
    seo: {
      titleTemplate: '{businessName} - HVAC Maintenance Services in {city}',
      descriptionTemplate: 'Professional HVAC maintenance and tune-ups in {city}. Extend equipment life, improve efficiency. Maintenance plans available. Call {phone}.',
      keywords: ['hvac maintenance', 'ac tune up', 'heating maintenance', 'hvac service', 'preventive maintenance']
    },
    schema: {
      serviceType: 'HVAC Maintenance',
      description: 'Preventive maintenance and tune-up services for heating and cooling systems',
      category: 'HVAC Services'
    },
    pricing: {
      startingPrice: 120,
      priceRange: '$120 - $200',
      unit: 'per visit'
    }
  },

  'heating-repair': {
    hero: {
      title: 'Emergency Heating Repair',
      subtitle: 'Don\'t let a broken heater leave you in the cold - fast, reliable heating repair',
      ctaLabel: 'Get Help Now',
      icon: 'flame'
    },
    benefits: {
      heading: 'Reliable Heating Repair',
      bullets: [
        'Emergency service available',
        'All heating system types',
        'Licensed and insured techs',
        'Upfront pricing guarantee',
        'Quality replacement parts',
        'Satisfaction guaranteed'
      ]
    },
    process: {
      heading: 'Our Heating Repair Process',
      steps: [
        'Emergency response or scheduled visit',
        'Complete heating system diagnosis',
        'Clear explanation of issues and costs',
        'Professional repair with warrantied parts',
        'System testing and safety check'
      ]
    },
    faqs: [
      {
        q: 'What heating systems do you repair?',
        a: 'We service all types: furnaces, heat pumps, boilers, radiant heating, and ductless mini-splits from all major manufacturers.'
      },
      {
        q: 'How quickly can you respond to heating emergencies?',
        a: 'We prioritize heating emergencies and typically respond within 2-4 hours, even on weekends and holidays.'
      },
      {
        q: 'Do you provide estimates before starting work?',
        a: 'Absolutely. We provide clear, upfront pricing after diagnosis so you know exactly what to expect before we begin repairs.'
      }
    ],
    seo: {
      titleTemplate: '{businessName} - Emergency Heating Repair in {city}',
      descriptionTemplate: 'Fast heating repair services in {city}. Furnace, heat pump, boiler repair. Emergency service available. Licensed technicians. Call {phone}.',
      keywords: ['heating repair', 'furnace repair', 'heat pump repair', 'boiler repair', 'emergency heating repair']
    },
    schema: {
      serviceType: 'Heating System Repair',
      description: 'Emergency and scheduled repair services for all types of heating systems',
      category: 'HVAC Services'
    },
    pricing: {
      startingPrice: 150,
      priceRange: '$150 - $1,200',
      unit: 'per repair'
    }
  }
};
