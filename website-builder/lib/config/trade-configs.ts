/**
 * Trade-Specific Configurations
 * 
 * Defines the specific content, services, and branding for each trade
 */

import { TradeConfiguration, Trade } from '../types/trade-config';

// HVAC Configuration
const hvacConfig: TradeConfiguration = {
  trade: 'hvac',
  type: 'residential',
  display_name: 'HVAC Services',
  industry_terms: {
    professional_title: 'HVAC Technician',
    service_area: 'heating and cooling services',
    emergency_type: 'HVAC emergency',
    maintenance_term: 'tune-up'
  },
  hero: {
    headline_template: "{city}'s Most Trusted HVAC Experts",
    subtitle_points: [
      '24/7 Emergency Service',
      'Same-Day Repairs',
      '100% Satisfaction Guaranteed',
      'NATE Certified Technicians'
    ],
    emergency_message: '🚨 HVAC Emergency? We\'re Available 24/7 - No Overtime Charges!',
    primary_cta: 'Book HVAC Service',
    secondary_cta: 'Call Now'
  },
  service_categories: [
    {
      id: 'emergency-repair',
      name: 'Emergency HVAC Repair',
      description: '24/7 emergency heating and air conditioning repair service',
      icon: 'wrench',
      is_emergency: true,
      is_popular: true,
      starting_price: 149,
      services: [
        {
          id: 'ac-repair',
          name: 'Air Conditioning Repair',
          description: 'Diagnose and repair AC units of all makes and models',
          estimated_duration_minutes: 90,
          base_price: 149,
          price_type: 'estimate',
          requires_site_visit: true,
          is_emergency: true,
          tags: ['cooling', 'repair', 'emergency']
        }
      ]
    },
    {
      id: 'installation',
      name: 'HVAC System Installation',
      description: 'Complete HVAC system installation and replacement',
      icon: 'settings',
      starting_price: 3500,
      services: [
        {
          id: 'hvac-install',
          name: 'Complete HVAC Installation',
          description: 'Full system installation with energy-efficient units',
          estimated_duration_minutes: 480,
          price_type: 'estimate',
          requires_site_visit: true,
          tags: ['installation', 'new-system']
        }
      ]
    },
    {
      id: 'maintenance',
      name: 'Preventive Maintenance',
      description: 'Regular maintenance to keep your system running efficiently',
      icon: 'shield',
      starting_price: 99,
      services: [
        {
          id: 'hvac-tuneup',
          name: 'HVAC Tune-Up',
          description: 'Comprehensive system inspection and maintenance',
          estimated_duration_minutes: 60,
          base_price: 99,
          price_type: 'fixed',
          requires_site_visit: true,
          tags: ['maintenance', 'preventive']
        }
      ]
    }
  ],
  trust_indicators: {
    certifications: ['NATE Certified', 'EPA Licensed', 'BBB A+ Rating'],
    guarantees: ['100% Satisfaction Guarantee', '24/7 Emergency Service', 'Licensed & Insured'],
    features: ['Same-Day Service', 'Upfront Pricing', 'Clean Background Checks']
  },
  booking: {
    default_services: ['HVAC Inspection', 'AC Repair', 'Heating Repair', 'Maintenance'],
    emergency_services: ['Emergency AC Repair', 'Emergency Heating Repair', 'System Failure'],
    lead_times: {
      emergency_hours: 2,
      standard_hours: 4,
      maintenance_days: 7
    }
  },
  seo: {
    title_template: '{business_name} - Professional HVAC Services in {city}, {state} | 24/7 Emergency Repair',
    description_template: 'Expert HVAC services in {city}, {state}. 24/7 emergency AC & heating repair, installation, and maintenance. Licensed & insured NATE-certified technicians.',
    keywords: ['hvac', 'air conditioning', 'heating', 'ac repair', 'furnace repair', 'hvac installation']
  },
  colors: {
    primary: '#3b82f6', // Blue
    secondary: '#1e40af',
    accent: '#f59e0b', // Orange
    emergency: '#dc2626' // Red
  }
};

// Plumbing Configuration
const plumbingConfig: TradeConfiguration = {
  trade: 'plumbing',
  type: 'residential',
  display_name: 'Plumbing Services',
  industry_terms: {
    professional_title: 'Licensed Plumber',
    service_area: 'plumbing services',
    emergency_type: 'plumbing emergency',
    maintenance_term: 'inspection'
  },
  hero: {
    headline_template: "{city}'s Most Reliable Plumbing Experts",
    subtitle_points: [
      '24/7 Emergency Service',
      'Licensed & Insured Plumbers',
      'Upfront Pricing',
      'Same-Day Service Available'
    ],
    emergency_message: '🚨 Plumbing Emergency? Burst Pipes, Leaks, Clogs - We\'re Here 24/7!',
    primary_cta: 'Book Plumbing Service',
    secondary_cta: 'Call Now'
  },
  service_categories: [
    {
      id: 'emergency-plumbing',
      name: 'Emergency Plumbing',
      description: '24/7 emergency plumbing repairs for leaks, clogs, and burst pipes',
      icon: 'droplets',
      is_emergency: true,
      is_popular: true,
      starting_price: 125,
      services: [
        {
          id: 'leak-repair',
          name: 'Leak Repair',
          description: 'Fast repair of pipe leaks, faucet leaks, and water damage prevention',
          estimated_duration_minutes: 60,
          base_price: 125,
          price_type: 'estimate',
          requires_site_visit: true,
          is_emergency: true,
          tags: ['leak', 'repair', 'emergency']
        }
      ]
    },
    {
      id: 'drain-cleaning',
      name: 'Drain Cleaning',
      description: 'Professional drain cleaning and clog removal services',
      icon: 'rotate-ccw',
      starting_price: 89,
      services: [
        {
          id: 'drain-snake',
          name: 'Drain Snaking',
          description: 'Professional drain cleaning with specialized equipment',
          estimated_duration_minutes: 45,
          base_price: 89,
          price_type: 'fixed',
          requires_site_visit: true,
          tags: ['drain', 'cleaning', 'maintenance']
        }
      ]
    },
    {
      id: 'fixture-installation',
      name: 'Fixture Installation',
      description: 'Installation of faucets, toilets, sinks, and other plumbing fixtures',
      icon: 'wrench',
      starting_price: 150,
      services: [
        {
          id: 'toilet-install',
          name: 'Toilet Installation',
          description: 'Professional toilet installation and replacement',
          estimated_duration_minutes: 90,
          base_price: 150,
          price_type: 'fixed',
          requires_site_visit: true,
          tags: ['installation', 'fixture', 'toilet']
        }
      ]
    }
  ],
  trust_indicators: {
    certifications: ['Licensed Plumber', 'Insured & Bonded', 'Master Plumber Certified'],
    guarantees: ['100% Satisfaction Guarantee', '24/7 Emergency Service', 'Warranty on Parts & Labor'],
    features: ['Same-Day Service', 'Clean & Professional', 'Upfront Pricing']
  },
  booking: {
    default_services: ['Plumbing Inspection', 'Leak Repair', 'Drain Cleaning', 'Fixture Installation'],
    emergency_services: ['Emergency Leak Repair', 'Burst Pipe Repair', 'Sewer Backup'],
    lead_times: {
      emergency_hours: 1,
      standard_hours: 4,
      maintenance_days: 3
    }
  },
  seo: {
    title_template: '{business_name} - Licensed Plumbers in {city}, {state} | 24/7 Emergency Service',
    description_template: 'Professional plumbing services in {city}, {state}. 24/7 emergency repairs, drain cleaning, fixture installation. Licensed & insured plumbers.',
    keywords: ['plumber', 'plumbing repair', 'drain cleaning', 'leak repair', 'emergency plumbing', 'fixture installation']
  },
  colors: {
    primary: '#0ea5e9', // Sky blue
    secondary: '#0284c7',
    accent: '#f59e0b', // Orange
    emergency: '#dc2626' // Red
  }
};

// Electrical Configuration
const electricalConfig: TradeConfiguration = {
  trade: 'electrical',
  type: 'residential',
  display_name: 'Electrical Services',
  industry_terms: {
    professional_title: 'Licensed Electrician',
    service_area: 'electrical services',
    emergency_type: 'electrical emergency',
    maintenance_term: 'inspection'
  },
  hero: {
    headline_template: "{city}'s Most Trusted Electrical Experts",
    subtitle_points: [
      '24/7 Emergency Service',
      'Licensed & Insured Electricians',
      'Safety First Approach',
      'Code Compliant Work'
    ],
    emergency_message: '⚡ Electrical Emergency? Power Outages, Sparks, Shorts - Call Now!',
    primary_cta: 'Book Electrical Service',
    secondary_cta: 'Call Now'
  },
  service_categories: [
    {
      id: 'emergency-electrical',
      name: 'Emergency Electrical',
      description: '24/7 emergency electrical repairs for power outages and safety hazards',
      icon: 'zap',
      is_emergency: true,
      is_popular: true,
      starting_price: 150,
      services: [
        {
          id: 'power-restoration',
          name: 'Power Restoration',
          description: 'Emergency power restoration and electrical fault diagnosis',
          estimated_duration_minutes: 90,
          base_price: 150,
          price_type: 'estimate',
          requires_site_visit: true,
          is_emergency: true,
          tags: ['power', 'emergency', 'restoration']
        }
      ]
    },
    {
      id: 'panel-upgrade',
      name: 'Panel Upgrades',
      description: 'Electrical panel upgrades and circuit breaker installations',
      icon: 'settings',
      starting_price: 800,
      services: [
        {
          id: 'panel-upgrade',
          name: 'Electrical Panel Upgrade',
          description: 'Complete electrical panel replacement and upgrade',
          estimated_duration_minutes: 240,
          base_price: 800,
          price_type: 'estimate',
          requires_site_visit: true,
          tags: ['panel', 'upgrade', 'installation']
        }
      ]
    },
    {
      id: 'wiring-installation',
      name: 'Wiring & Installation',
      description: 'New wiring, outlets, switches, and lighting installation',
      icon: 'plug',
      starting_price: 120,
      services: [
        {
          id: 'outlet-install',
          name: 'Outlet Installation',
          description: 'New electrical outlet and switch installation',
          estimated_duration_minutes: 60,
          base_price: 120,
          price_type: 'fixed',
          requires_site_visit: true,
          tags: ['outlet', 'installation', 'wiring']
        }
      ]
    }
  ],
  trust_indicators: {
    certifications: ['Licensed Electrician', 'Insured & Bonded', 'Code Certified'],
    guarantees: ['100% Satisfaction Guarantee', '24/7 Emergency Service', 'Safety Guaranteed'],
    features: ['Same-Day Service', 'Code Compliant', 'Safety First']
  },
  booking: {
    default_services: ['Electrical Inspection', 'Outlet Installation', 'Panel Upgrade', 'Wiring Repair'],
    emergency_services: ['Power Restoration', 'Electrical Fire Prevention', 'Circuit Repair'],
    lead_times: {
      emergency_hours: 1,
      standard_hours: 6,
      maintenance_days: 5
    }
  },
  seo: {
    title_template: '{business_name} - Licensed Electricians in {city}, {state} | 24/7 Emergency Service',
    description_template: 'Professional electrical services in {city}, {state}. 24/7 emergency repairs, panel upgrades, wiring installation. Licensed & insured electricians.',
    keywords: ['electrician', 'electrical repair', 'panel upgrade', 'wiring installation', 'emergency electrical', 'outlet installation']
  },
  colors: {
    primary: '#eab308', // Yellow
    secondary: '#ca8a04',
    accent: '#3b82f6', // Blue
    emergency: '#dc2626' // Red
  }
};

// Commercial Mechanical Configuration
const mechanicalConfig: TradeConfiguration = {
  trade: 'mechanical',
  type: 'commercial',
  display_name: 'Commercial Mechanical Services',
  industry_terms: {
    professional_title: 'Mechanical Engineer',
    service_area: 'commercial mechanical systems',
    emergency_type: 'mechanical system emergency',
    maintenance_term: 'preventive maintenance'
  },
  hero: {
    headline_template: "{city}'s Premier Commercial Mechanical Experts",
    subtitle_points: [
      '24/7 Emergency Response',
      'Certified Mechanical Engineers',
      'Preventive Maintenance Programs',
      'Energy Efficiency Solutions'
    ],
    emergency_message: '🏢 Commercial System Emergency? Critical Equipment Down - We Respond 24/7!',
    primary_cta: 'Schedule Service',
    secondary_cta: 'Emergency Call'
  },
  service_categories: [
    {
      id: 'hvac-commercial',
      name: 'Commercial HVAC',
      description: 'Large-scale HVAC systems for commercial buildings and facilities',
      icon: 'building',
      is_popular: true,
      starting_price: 250,
      services: [
        {
          id: 'commercial-hvac-repair',
          name: 'Commercial HVAC Repair',
          description: 'Repair and maintenance of commercial HVAC systems',
          estimated_duration_minutes: 180,
          base_price: 250,
          price_type: 'estimate',
          requires_site_visit: true,
          tags: ['hvac', 'commercial', 'repair']
        }
      ]
    },
    {
      id: 'boiler-systems',
      name: 'Boiler Systems',
      description: 'Commercial boiler installation, repair, and maintenance',
      icon: 'flame',
      starting_price: 300,
      services: [
        {
          id: 'boiler-service',
          name: 'Boiler Service & Repair',
          description: 'Commercial boiler system service and emergency repair',
          estimated_duration_minutes: 240,
          base_price: 300,
          price_type: 'estimate',
          requires_site_visit: true,
          is_emergency: true,
          tags: ['boiler', 'heating', 'commercial']
        }
      ]
    }
  ],
  trust_indicators: {
    certifications: ['Licensed Mechanical Engineer', 'Commercial Certified', 'EPA Certified'],
    guarantees: ['24/7 Emergency Response', 'Preventive Maintenance Plans', 'Energy Efficiency Guaranteed'],
    features: ['Commercial Grade Equipment', 'Certified Engineers', 'Maintenance Contracts']
  },
  booking: {
    default_services: ['System Inspection', 'Preventive Maintenance', 'Emergency Repair', 'Energy Audit'],
    emergency_services: ['System Failure', 'Equipment Breakdown', 'Critical Repair'],
    lead_times: {
      emergency_hours: 2,
      standard_hours: 8,
      maintenance_days: 14
    }
  },
  seo: {
    title_template: '{business_name} - Commercial Mechanical Services in {city}, {state} | 24/7 Emergency',
    description_template: 'Professional commercial mechanical services in {city}, {state}. HVAC, boiler systems, preventive maintenance. Licensed engineers.',
    keywords: ['commercial mechanical', 'commercial hvac', 'boiler service', 'mechanical engineer', 'commercial maintenance']
  },
  colors: {
    primary: '#374151', // Gray
    secondary: '#1f2937',
    accent: '#f59e0b', // Orange
    emergency: '#dc2626' // Red
  }
};

// Export all configurations
export const TRADE_CONFIGS: Record<Trade, TradeConfiguration> = {
  // Residential
  hvac: hvacConfig,
  plumbing: plumbingConfig,
  electrical: electricalConfig,
  chimney: {
    ...hvacConfig,
    trade: 'chimney',
    display_name: 'Chimney Services',
    industry_terms: {
      professional_title: 'Chimney Specialist',
      service_area: 'chimney services',
      emergency_type: 'chimney emergency',
      maintenance_term: 'inspection'
    }
  } as TradeConfiguration,
  roofing: {
    ...hvacConfig,
    trade: 'roofing',
    display_name: 'Roofing Services',
    industry_terms: {
      professional_title: 'Roofing Contractor',
      service_area: 'roofing services',
      emergency_type: 'roofing emergency',
      maintenance_term: 'inspection'
    }
  } as TradeConfiguration,
  garage_door: {
    ...hvacConfig,
    trade: 'garage_door',
    display_name: 'Garage Door Services'
  } as TradeConfiguration,
  septic: {
    ...plumbingConfig,
    trade: 'septic',
    display_name: 'Septic Services'
  } as TradeConfiguration,
  pest_control: {
    ...hvacConfig,
    trade: 'pest_control',
    display_name: 'Pest Control Services'
  } as TradeConfiguration,
  irrigation: {
    ...plumbingConfig,
    trade: 'irrigation',
    display_name: 'Irrigation Services'
  } as TradeConfiguration,
  painting: {
    ...hvacConfig,
    trade: 'painting',
    display_name: 'Painting Services'
  } as TradeConfiguration,
  
  // Commercial
  mechanical: mechanicalConfig,
  refrigeration: {
    ...mechanicalConfig,
    trade: 'refrigeration',
    display_name: 'Commercial Refrigeration'
  } as TradeConfiguration,
  security_systems: {
    ...electricalConfig,
    trade: 'security_systems',
    type: 'commercial',
    display_name: 'Security Systems'
  } as TradeConfiguration,
  landscaping: {
    ...hvacConfig,
    trade: 'landscaping',
    type: 'commercial',
    display_name: 'Commercial Landscaping'
  } as TradeConfiguration,
  kitchen_equipment: {
    ...mechanicalConfig,
    trade: 'kitchen_equipment',
    display_name: 'Commercial Kitchen Equipment'
  } as TradeConfiguration,
  water_treatment: {
    ...plumbingConfig,
    trade: 'water_treatment',
    type: 'commercial',
    display_name: 'Water Treatment Systems'
  } as TradeConfiguration,
  pool_spa: {
    ...plumbingConfig,
    trade: 'pool_spa',
    type: 'commercial',
    display_name: 'Pool & Spa Services'
  } as TradeConfiguration
};

// Helper function to get trade configuration
export function getTradeConfig(trade: Trade): TradeConfiguration {
  const config = TRADE_CONFIGS[trade];
  if (!config) {
    throw new Error(`Trade configuration not found for: ${trade}`);
  }
  return config;
}

// Helper function to get all trades by type
export function getTradesByType(type: TradeType): TradeConfiguration[] {
  return Object.values(TRADE_CONFIGS).filter(config => config.type === type);
}
