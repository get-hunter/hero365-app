import { ActivityContentPack } from '../types';
import { hvacContentPacks } from './hvac';
import { plumbingContentPacks } from './plumbing';

// Registry of all activity content packs
export const activityContentPacks: Record<string, ActivityContentPack> = {
  ...hvacContentPacks,
  ...plumbingContentPacks,
  
  // Electrical activities
  'electrical-repair': {
    hero: {
      title: 'Professional Electrical Repair Services',
      subtitle: 'Safe, reliable electrical repairs by licensed electricians',
      ctaLabel: 'Get Electrical Help',
      icon: 'zap'
    },
    benefits: {
      heading: 'Licensed Electrical Services',
      bullets: [
        'Licensed and insured electricians',
        '24/7 emergency service',
        'Code-compliant installations',
        'Safety inspections included',
        'Upfront pricing guarantee',
        'Warranty on all work'
      ]
    },
    process: {
      heading: 'Our Electrical Repair Process',
      steps: [
        'Safety assessment and power isolation',
        'Comprehensive electrical diagnosis',
        'Clear explanation of issues and solutions',
        'Professional repair with quality materials',
        'Testing and safety verification'
      ]
    },
    faqs: [
      {
        q: 'When should I call an electrician?',
        a: 'Call immediately for flickering lights, burning smells, frequent breaker trips, or any electrical safety concerns.'
      },
      {
        q: 'Do you handle emergency electrical issues?',
        a: 'Yes, we provide 24/7 emergency electrical services for safety hazards and urgent electrical problems.'
      },
      {
        q: 'Are your electricians licensed?',
        a: 'All our electricians are fully licensed, insured, and stay current with electrical codes and safety standards.'
      }
    ],
    seo: {
      titleTemplate: '{businessName} - Licensed Electrical Repair in {city}',
      descriptionTemplate: 'Professional electrical repair services in {city}. Licensed electricians, 24/7 emergency service. Safe, code-compliant work. Call {phone}.',
      keywords: ['electrical repair', 'electrician', 'electrical service', 'emergency electrician', 'electrical troubleshooting']
    },
    schema: {
      serviceType: 'Electrical Repair',
      description: 'Professional electrical repair and troubleshooting services',
      category: 'Electrical Services'
    },
    pricing: {
      startingPrice: 150,
      priceRange: '$150 - $800',
      unit: 'per repair'
    }
  },

  // General Contractor activities
  'home-renovation': {
    hero: {
      title: 'Complete Home Renovation Services',
      subtitle: 'Transform your home with our full-service renovation expertise',
      ctaLabel: 'Start My Project',
      icon: 'home'
    },
    benefits: {
      heading: 'Full-Service Renovation',
      bullets: [
        'Licensed general contractor',
        'Complete project management',
        'Quality craftsmanship guaranteed',
        'Transparent pricing and timeline',
        'Permit handling included',
        'Insurance and bonding'
      ]
    },
    process: {
      heading: 'Our Renovation Process',
      steps: [
        'Initial consultation and design',
        'Detailed project planning and permits',
        'Professional construction and management',
        'Quality inspections throughout',
        'Final walkthrough and warranty'
      ]
    },
    faqs: [
      {
        q: 'How long does a home renovation take?',
        a: 'Timeline varies by project scope. Kitchen remodels typically take 4-6 weeks, while whole-home renovations can take 3-6 months.'
      },
      {
        q: 'Do you handle permits?',
        a: 'Yes, we handle all necessary permits and inspections to ensure your renovation meets local building codes.'
      },
      {
        q: 'Can I live in my home during renovation?',
        a: 'Depends on the scope. We work with you to minimize disruption and can phase work to keep parts of your home livable.'
      }
    ],
    seo: {
      titleTemplate: '{businessName} - Home Renovation Contractor in {city}',
      descriptionTemplate: 'Professional home renovation services in {city}. Licensed contractor, complete project management. Kitchen, bath, whole-home remodels. Call {phone}.',
      keywords: ['home renovation', 'home remodeling', 'general contractor', 'kitchen remodel', 'bathroom remodel']
    },
    schema: {
      serviceType: 'Home Renovation',
      description: 'Complete home renovation and remodeling services',
      category: 'Construction Services'
    },
    pricing: {
      startingPrice: 5000,
      priceRange: '$5,000 - $100,000+',
      unit: 'per project'
    }
  },

  // Roofing activities
  'roof-repair': {
    hero: {
      title: 'Professional Roof Repair Services',
      subtitle: 'Protect your home with expert roof repair and maintenance',
      ctaLabel: 'Fix My Roof',
      icon: 'home'
    },
    benefits: {
      heading: 'Expert Roof Repair',
      bullets: [
        'Licensed and insured roofers',
        'All roofing materials and types',
        'Emergency leak repair',
        'Free roof inspections',
        'Warranty on repairs',
        'Insurance claim assistance'
      ]
    },
    process: {
      heading: 'Our Roof Repair Process',
      steps: [
        'Comprehensive roof inspection',
        'Detailed damage assessment',
        'Clear repair recommendations',
        'Professional repair with quality materials',
        'Final inspection and cleanup'
      ]
    },
    faqs: [
      {
        q: 'How do I know if I need roof repair?',
        a: 'Signs include missing shingles, leaks, granules in gutters, or visible damage. We offer free inspections to assess your roof.'
      },
      {
        q: 'Do you work with insurance companies?',
        a: 'Yes, we help with insurance claims and can work directly with your adjuster to ensure proper coverage.'
      },
      {
        q: 'Can you repair all types of roofs?',
        a: 'We repair all roofing materials including asphalt shingles, metal, tile, slate, and flat roofing systems.'
      }
    ],
    seo: {
      titleTemplate: '{businessName} - Professional Roof Repair in {city}',
      descriptionTemplate: 'Expert roof repair services in {city}. Licensed roofers, emergency leak repair, insurance claims. Free inspections. Call {phone}.',
      keywords: ['roof repair', 'roof leak repair', 'roofing contractor', 'emergency roof repair', 'roof inspection']
    },
    schema: {
      serviceType: 'Roof Repair',
      description: 'Professional roof repair and maintenance services',
      category: 'Roofing Services'
    },
    pricing: {
      startingPrice: 300,
      priceRange: '$300 - $3,000',
      unit: 'per repair'
    }
  }
};

// Helper function to get content pack for an activity
export function getActivityContentPack(activitySlug: string): ActivityContentPack | null {
  return activityContentPacks[activitySlug] || null;
}

// Helper function to get all available activity slugs
export function getAvailableActivitySlugs(): string[] {
  return Object.keys(activityContentPacks);
}

// Helper function to get content packs by trade
export function getContentPacksByTrade(tradeSlug: string): Record<string, ActivityContentPack> {
  // This would be enhanced to filter by trade when we have trade mapping
  // For now, return all packs
  return activityContentPacks;
}
