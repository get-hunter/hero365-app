import { ActivityContentPack } from '../types';

export const plumbingContentPacks: Record<string, ActivityContentPack> = {
  'drain-cleaning': {
    hero: {
      title: 'Professional Drain Cleaning Services',
      subtitle: 'Fast, effective drain cleaning to restore proper flow and prevent backups',
      ctaLabel: 'Clear My Drains',
      icon: 'droplet'
    },
    benefits: {
      heading: 'Expert Drain Cleaning',
      bullets: [
        'Advanced drain cleaning equipment',
        'Video camera inspections available',
        'Eco-friendly cleaning methods',
        'Same-day service available',
        'Preventive maintenance plans',
        '100% satisfaction guarantee'
      ]
    },
    process: {
      heading: 'Our Drain Cleaning Process',
      steps: [
        'Initial assessment and diagnosis',
        'Video inspection if needed',
        'Professional drain cleaning service',
        'Flow testing and verification',
        'Preventive maintenance recommendations'
      ]
    },
    faqs: [
      {
        q: 'How do you clean drains?',
        a: 'We use professional-grade equipment including drain snakes, hydro-jetting, and video inspection to thoroughly clean and clear your drains.'
      },
      {
        q: 'How often should drains be cleaned?',
        a: 'For prevention, we recommend annual drain cleaning. High-use drains may need more frequent service.'
      },
      {
        q: 'Do you offer emergency drain cleaning?',
        a: 'Yes, we provide emergency drain cleaning services for severe backups and urgent situations.'
      }
    ],
    seo: {
      titleTemplate: '{businessName} - Professional Drain Cleaning in {city}',
      descriptionTemplate: 'Expert drain cleaning services in {city}. Clear clogs, prevent backups. Same-day service available. Licensed plumbers. Call {phone}.',
      keywords: ['drain cleaning', 'clogged drain', 'drain snake', 'hydro jetting', 'sewer cleaning']
    },
    schema: {
      serviceType: 'Drain Cleaning',
      description: 'Professional drain cleaning and clog removal services',
      category: 'Plumbing Services'
    },
    pricing: {
      startingPrice: 150,
      priceRange: '$150 - $400',
      unit: 'per drain'
    }
  },

  'leak-repair': {
    hero: {
      title: 'Emergency Leak Repair Services',
      subtitle: 'Stop water damage in its tracks with fast, professional leak repair',
      ctaLabel: 'Stop My Leak',
      icon: 'droplets'
    },
    benefits: {
      heading: 'Fast Leak Detection & Repair',
      bullets: [
        '24/7 emergency service',
        'Advanced leak detection technology',
        'Minimize water damage',
        'Insurance claim assistance',
        'Permanent repair solutions',
        'Licensed and insured'
      ]
    },
    process: {
      heading: 'Our Leak Repair Process',
      steps: [
        'Emergency response and assessment',
        'Precise leak location using technology',
        'Water shut-off to prevent damage',
        'Professional repair with quality materials',
        'System testing and cleanup'
      ]
    },
    faqs: [
      {
        q: 'How do you find hidden leaks?',
        a: 'We use electronic leak detection, thermal imaging, and acoustic equipment to locate leaks behind walls and under slabs without damage.'
      },
      {
        q: 'Will insurance cover leak repairs?',
        a: 'Coverage varies by policy and cause. We can help document the damage and work with your insurance company.'
      },
      {
        q: 'Can small leaks wait?',
        a: 'Even small leaks can cause significant damage over time. We recommend immediate repair to prevent costly water damage.'
      }
    ],
    seo: {
      titleTemplate: '{businessName} - Emergency Leak Repair in {city}',
      descriptionTemplate: 'Fast leak repair services in {city}. 24/7 emergency response. Advanced leak detection. Prevent water damage. Call {phone} now.',
      keywords: ['leak repair', 'water leak', 'pipe leak', 'emergency plumber', 'leak detection']
    },
    schema: {
      serviceType: 'Leak Repair',
      description: '24/7 emergency leak detection and repair services',
      category: 'Plumbing Services'
    },
    pricing: {
      startingPrice: 200,
      priceRange: '$200 - $800',
      unit: 'per repair'
    }
  },

  'toilet-repair': {
    hero: {
      title: 'Toilet Repair & Installation',
      subtitle: 'Expert toilet repair and replacement services for all makes and models',
      ctaLabel: 'Fix My Toilet',
      icon: 'home'
    },
    benefits: {
      heading: 'Professional Toilet Services',
      bullets: [
        'All toilet brands and models',
        'Same-day repair service',
        'High-efficiency toilet options',
        'Proper installation guaranteed',
        'Cleanup included',
        'Parts and labor warranty'
      ]
    },
    process: {
      heading: 'Our Toilet Service Process',
      steps: [
        'Diagnosis of toilet issues',
        'Repair or replacement recommendation',
        'Professional installation or repair',
        'Testing for proper operation',
        'Complete cleanup and disposal'
      ]
    },
    faqs: [
      {
        q: 'Should I repair or replace my toilet?',
        a: 'We recommend replacement for toilets over 15 years old, frequent repairs, or significant efficiency upgrades. Otherwise, repair is usually cost-effective.'
      },
      {
        q: 'How long does toilet installation take?',
        a: 'Most toilet installations take 1-2 hours, including removal of the old toilet and proper disposal.'
      },
      {
        q: 'Do you install water-saving toilets?',
        a: 'Yes, we install high-efficiency toilets that can save thousands of gallons per year while maintaining performance.'
      }
    ],
    seo: {
      titleTemplate: '{businessName} - Toilet Repair & Installation in {city}',
      descriptionTemplate: 'Professional toilet repair and installation in {city}. Same-day service, all brands. High-efficiency options available. Call {phone}.',
      keywords: ['toilet repair', 'toilet installation', 'toilet replacement', 'running toilet', 'clogged toilet']
    },
    schema: {
      serviceType: 'Toilet Repair and Installation',
      description: 'Complete toilet repair, installation, and replacement services',
      category: 'Plumbing Services'
    },
    pricing: {
      startingPrice: 150,
      priceRange: '$150 - $600',
      unit: 'per service'
    }
  },

  'water-heater-repair': {
    hero: {
      title: 'Water Heater Repair & Installation',
      subtitle: 'Restore hot water fast with expert water heater services',
      ctaLabel: 'Get Hot Water',
      icon: 'flame'
    },
    benefits: {
      heading: 'Water Heater Experts',
      bullets: [
        'All water heater types serviced',
        'Energy-efficient replacements',
        'Same-day installation available',
        'Manufacturer warranties honored',
        'Proper sizing and installation',
        'Emergency service available'
      ]
    },
    process: {
      heading: 'Our Water Heater Service',
      steps: [
        'Complete system diagnosis',
        'Repair vs. replacement analysis',
        'Professional installation or repair',
        'Safety and code compliance check',
        'System testing and walkthrough'
      ]
    },
    faqs: [
      {
        q: 'How long do water heaters last?',
        a: 'Traditional tank water heaters last 8-12 years, while tankless units can last 15-20 years with proper maintenance.'
      },
      {
        q: 'Should I choose tank or tankless?',
        a: 'Tankless provides endless hot water and saves space, while tank units have lower upfront costs. We\'ll help you choose based on your needs.'
      },
      {
        q: 'Do you offer emergency water heater service?',
        a: 'Yes, we provide emergency water heater repair and replacement because we know hot water is essential.'
      }
    ],
    seo: {
      titleTemplate: '{businessName} - Water Heater Repair & Installation in {city}',
      descriptionTemplate: 'Expert water heater repair and installation in {city}. Tank and tankless options. Same-day service available. Call {phone}.',
      keywords: ['water heater repair', 'water heater installation', 'tankless water heater', 'hot water heater', 'water heater replacement']
    },
    schema: {
      serviceType: 'Water Heater Services',
      description: 'Complete water heater repair, installation, and replacement services',
      category: 'Plumbing Services'
    },
    pricing: {
      startingPrice: 200,
      priceRange: '$200 - $3,500',
      unit: 'per service'
    }
  }
};
