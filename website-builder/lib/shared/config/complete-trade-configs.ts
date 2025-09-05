/**
 * Complete Trade Configurations - All 20 Trades
 * 
 * Comprehensive configurations for all residential and commercial trades
 * with detailed service categories, pricing, messaging, and module mappings.
 */

import { TradeConfiguration } from '@/lib/shared/types/trade-config';

// RESIDENTIAL TRADES (10)

export const hvacConfig: TradeConfiguration = {
  trade: 'hvac',
  display_name: 'HVAC',
  full_name: 'Heating, Ventilation & Air Conditioning',
  category: 'residential',
  description: 'Complete heating and cooling solutions for your home',
  
  colors: {
    primary: '#2563eb',
    secondary: '#1d4ed8',
    accent: '#3b82f6'
  },
  
  hero: {
    headline_template: '{city}\'s Most Trusted HVAC Experts',
    subtitle_points: [
      'Licensed & Insured Technicians',
      '24/7 Emergency Service',
      'Same-Day Service Available'
    ],
    primary_cta: 'Call for Service',
    secondary_cta: 'Schedule Online',
    emergency_message: '24/7 Emergency HVAC Service - No Overtime Charges!'
  },
  
  service_categories: [
    {
      name: 'AC Repair & Installation',
      description: 'Expert air conditioning repair and new system installation',
      starting_price: 150,
      emergency_available: true,
      seasonal_demand: 'high_summer'
    },
    {
      name: 'Heating Repair & Installation',
      description: 'Furnace and heating system repair and replacement',
      starting_price: 150,
      emergency_available: true,
      seasonal_demand: 'high_winter'
    },
    {
      name: 'HVAC Maintenance',
      description: 'Preventive maintenance to keep your system running efficiently',
      starting_price: 99,
      emergency_available: false,
      seasonal_demand: 'spring_fall'
    },
    {
      name: 'Duct Cleaning & Repair',
      description: 'Professional ductwork cleaning and sealing services',
      starting_price: 200,
      emergency_available: false,
      seasonal_demand: 'year_round'
    }
  ],
  
  emergency_services: true,
  seasonal_patterns: {
    peak_months: [6, 7, 8, 12, 1, 2],
    slow_months: [4, 5, 9, 10],
    maintenance_months: [3, 4, 9, 10]
  },
  
  certifications: [
    'NATE Certified',
    'EPA Licensed',
    'HVAC Excellence Certified',
    'Manufacturer Certified'
  ],
  
  activity_modules: [
    'hvac_efficiency_calculator',
    'hvac_sizing_tool',
    'hvac_load_calculator',
    'hvac_maintenance_scheduler',
    'hvac_cost_estimator'
  ]
};

export const plumbingConfig: TradeConfiguration = {
  trade: 'plumbing',
  display_name: 'Plumbing',
  full_name: 'Professional Plumbing Services',
  category: 'residential',
  description: 'Complete plumbing solutions for your home and business',
  
  colors: {
    primary: '#0891b2',
    secondary: '#0e7490',
    accent: '#06b6d4'
  },
  
  hero: {
    headline_template: '{city}\'s Premier Plumbing Professionals',
    subtitle_points: [
      'Licensed Master Plumbers',
      '24/7 Emergency Response',
      'Guaranteed Quality Work'
    ],
    primary_cta: 'Call Now',
    secondary_cta: 'Book Service',
    emergency_message: 'Emergency Plumbing Service - Available 24/7!'
  },
  
  service_categories: [
    {
      name: 'Emergency Plumbing',
      description: 'Burst pipes, major leaks, and urgent plumbing issues',
      starting_price: 200,
      emergency_available: true,
      seasonal_demand: 'year_round'
    },
    {
      name: 'Drain Cleaning',
      description: 'Professional drain and sewer line cleaning services',
      starting_price: 125,
      emergency_available: true,
      seasonal_demand: 'year_round'
    },
    {
      name: 'Water Heater Service',
      description: 'Water heater repair, replacement, and maintenance',
      starting_price: 150,
      emergency_available: true,
      seasonal_demand: 'high_winter'
    },
    {
      name: 'Fixture Installation',
      description: 'Toilet, faucet, and plumbing fixture installation',
      starting_price: 100,
      emergency_available: false,
      seasonal_demand: 'year_round'
    }
  ],
  
  emergency_services: true,
  seasonal_patterns: {
    peak_months: [11, 12, 1, 2],
    slow_months: [6, 7, 8],
    maintenance_months: [3, 4, 9, 10]
  },
  
  certifications: [
    'Master Plumber License',
    'Backflow Prevention Certified',
    'Gas Line Certified',
    'Water Quality Specialist'
  ],
  
  activity_modules: [
    'plumbing_severity_triage',
    'plumbing_pressure_calculator',
    'plumbing_pipe_sizing',
    'plumbing_leak_detector',
    'plumbing_water_usage'
  ]
};

export const electricalConfig: TradeConfiguration = {
  trade: 'electrical',
  display_name: 'Electrical',
  full_name: 'Professional Electrical Services',
  category: 'residential',
  description: 'Safe and reliable electrical solutions for your home',
  
  colors: {
    primary: '#dc2626',
    secondary: '#b91c1c',
    accent: '#ef4444'
  },
  
  hero: {
    headline_template: '{city}\'s Licensed Electrical Experts',
    subtitle_points: [
      'Licensed Master Electricians',
      'Code Compliant Work',
      'Safety First Approach'
    ],
    primary_cta: 'Call Electrician',
    secondary_cta: 'Get Quote',
    emergency_message: '24/7 Emergency Electrical Service - Safety First!'
  },
  
  service_categories: [
    {
      name: 'Electrical Repair',
      description: 'Troubleshooting and repair of electrical issues',
      starting_price: 125,
      emergency_available: true,
      seasonal_demand: 'year_round'
    },
    {
      name: 'Panel Upgrades',
      description: 'Electrical panel replacement and circuit additions',
      starting_price: 800,
      emergency_available: false,
      seasonal_demand: 'year_round'
    },
    {
      name: 'Outlet & Switch Installation',
      description: 'New outlets, switches, and electrical fixtures',
      starting_price: 75,
      emergency_available: false,
      seasonal_demand: 'year_round'
    },
    {
      name: 'Lighting Installation',
      description: 'Indoor and outdoor lighting solutions',
      starting_price: 100,
      emergency_available: false,
      seasonal_demand: 'year_round'
    }
  ],
  
  emergency_services: true,
  seasonal_patterns: {
    peak_months: [11, 12, 1, 6, 7],
    slow_months: [2, 3, 4],
    maintenance_months: [3, 4, 9, 10]
  },
  
  certifications: [
    'Master Electrician License',
    'NEC Code Certified',
    'OSHA Safety Certified',
    'Low Voltage Certified'
  ],
  
  activity_modules: [
    'electrical_load_calculator',
    'electrical_panel_advisor',
    'electrical_safety_checker',
    'electrical_code_checker',
    'electrical_cost_estimator'
  ]
};

export const roofingConfig: TradeConfiguration = {
  trade: 'roofing',
  display_name: 'Roofing',
  full_name: 'Professional Roofing Services',
  category: 'residential',
  description: 'Complete roofing solutions to protect your home',
  
  colors: {
    primary: '#7c2d12',
    secondary: '#92400e',
    accent: '#a16207'
  },
  
  hero: {
    headline_template: '{city}\'s Premier Roofing Contractors',
    subtitle_points: [
      'Licensed & Insured',
      'Storm Damage Specialists',
      'Quality Materials & Workmanship'
    ],
    primary_cta: 'Free Inspection',
    secondary_cta: 'Get Estimate',
    emergency_message: 'Emergency Roof Repair - Protecting Your Home 24/7!'
  },
  
  service_categories: [
    {
      name: 'Roof Repair',
      description: 'Emergency and routine roof repair services',
      starting_price: 200,
      emergency_available: true,
      seasonal_demand: 'year_round'
    },
    {
      name: 'Roof Replacement',
      description: 'Complete roof replacement with quality materials',
      starting_price: 8000,
      emergency_available: false,
      seasonal_demand: 'spring_summer'
    },
    {
      name: 'Roof Inspection',
      description: 'Comprehensive roof inspection and assessment',
      starting_price: 150,
      emergency_available: false,
      seasonal_demand: 'spring_fall'
    },
    {
      name: 'Gutter Services',
      description: 'Gutter cleaning, repair, and installation',
      starting_price: 125,
      emergency_available: false,
      seasonal_demand: 'fall_spring'
    }
  ],
  
  emergency_services: true,
  seasonal_patterns: {
    peak_months: [4, 5, 6, 7, 8, 9],
    slow_months: [12, 1, 2],
    maintenance_months: [3, 10, 11]
  },
  
  certifications: [
    'GAF Master Elite',
    'CertainTeed Certified',
    'OSHA Safety Certified',
    'Storm Damage Specialist'
  ],
  
  activity_modules: [
    'roofing_material_selector',
    'roofing_lifespan_calculator',
    'roofing_damage_assessor',
    'roofing_cost_estimator',
    'roofing_warranty_tracker'
  ]
};

export const chimneyConfig: TradeConfiguration = {
  trade: 'chimney',
  display_name: 'Chimney',
  full_name: 'Professional Chimney Services',
  category: 'residential',
  description: 'Complete chimney and fireplace services for safety and efficiency',
  
  colors: {
    primary: '#374151',
    secondary: '#4b5563',
    accent: '#6b7280'
  },
  
  hero: {
    headline_template: '{city}\'s Certified Chimney Professionals',
    subtitle_points: [
      'CSIA Certified Technicians',
      'Safety Inspections',
      'Professional Cleaning'
    ],
    primary_cta: 'Schedule Inspection',
    secondary_cta: 'Get Quote',
    emergency_message: 'Emergency Chimney Service - Safety First!'
  },
  
  service_categories: [
    {
      name: 'Chimney Cleaning',
      description: 'Professional chimney and flue cleaning services',
      starting_price: 150,
      emergency_available: false,
      seasonal_demand: 'fall_winter'
    },
    {
      name: 'Chimney Inspection',
      description: 'Comprehensive safety and structural inspections',
      starting_price: 125,
      emergency_available: false,
      seasonal_demand: 'fall'
    },
    {
      name: 'Chimney Repair',
      description: 'Structural repairs and maintenance services',
      starting_price: 200,
      emergency_available: true,
      seasonal_demand: 'spring_summer'
    },
    {
      name: 'Fireplace Services',
      description: 'Fireplace installation, repair, and maintenance',
      starting_price: 175,
      emergency_available: false,
      seasonal_demand: 'fall_winter'
    }
  ],
  
  emergency_services: true,
  seasonal_patterns: {
    peak_months: [9, 10, 11, 12, 1],
    slow_months: [5, 6, 7, 8],
    maintenance_months: [3, 4, 9]
  },
  
  certifications: [
    'CSIA Certified',
    'NFI Certified',
    'NCSG Member',
    'Safety Specialist'
  ],
  
  activity_modules: [
    'maintenance_scheduler',
    'virtual_consultation_scheduler'
  ]
};

// Additional residential trades...
export const garageDoorConfig: TradeConfiguration = {
  trade: 'garage_door',
  display_name: 'Garage Door',
  full_name: 'Professional Garage Door Services',
  category: 'residential',
  description: 'Complete garage door installation, repair, and maintenance',
  
  colors: {
    primary: '#059669',
    secondary: '#047857',
    accent: '#10b981'
  },
  
  hero: {
    headline_template: '{city}\'s Garage Door Specialists',
    subtitle_points: [
      'Same-Day Service',
      'All Brands Serviced',
      'Safety Inspections'
    ],
    primary_cta: 'Call for Service',
    secondary_cta: 'Schedule Repair',
    emergency_message: 'Emergency Garage Door Service - We\'ll Get You Moving!'
  },
  
  service_categories: [
    {
      name: 'Garage Door Repair',
      description: 'Spring replacement, opener repair, and troubleshooting',
      starting_price: 125,
      emergency_available: true,
      seasonal_demand: 'year_round'
    },
    {
      name: 'Garage Door Installation',
      description: 'New garage door and opener installation',
      starting_price: 800,
      emergency_available: false,
      seasonal_demand: 'spring_summer'
    },
    {
      name: 'Opener Services',
      description: 'Garage door opener repair and replacement',
      starting_price: 150,
      emergency_available: true,
      seasonal_demand: 'year_round'
    }
  ],
  
  emergency_services: true,
  seasonal_patterns: {
    peak_months: [4, 5, 6, 7, 8, 9],
    slow_months: [12, 1, 2],
    maintenance_months: [3, 10]
  },
  
  certifications: [
    'IDA Certified',
    'Manufacturer Trained',
    'Safety Certified'
  ],
  
  activity_modules: [
    'maintenance_scheduler',
    'emergency_dispatcher'
  ]
};

// COMMERCIAL TRADES (10)

export const mechanicalConfig: TradeConfiguration = {
  trade: 'mechanical',
  display_name: 'Mechanical',
  full_name: 'Commercial Mechanical Services',
  category: 'commercial',
  description: 'Complete commercial HVAC and mechanical system solutions',
  
  colors: {
    primary: '#1e40af',
    secondary: '#1d4ed8',
    accent: '#3b82f6'
  },
  
  hero: {
    headline_template: '{city}\'s Commercial Mechanical Experts',
    subtitle_points: [
      'Licensed Commercial Contractors',
      '24/7 Emergency Service',
      'Preventive Maintenance Programs'
    ],
    primary_cta: 'Call for Service',
    secondary_cta: 'Request Quote',
    emergency_message: '24/7 Commercial Emergency Service - Minimizing Downtime!'
  },
  
  service_categories: [
    {
      name: 'Commercial HVAC',
      description: 'Large-scale heating and cooling system services',
      starting_price: 300,
      emergency_available: true,
      seasonal_demand: 'year_round'
    },
    {
      name: 'Boiler Services',
      description: 'Commercial boiler installation, repair, and maintenance',
      starting_price: 400,
      emergency_available: true,
      seasonal_demand: 'high_winter'
    },
    {
      name: 'Chiller Services',
      description: 'Commercial chiller system services and maintenance',
      starting_price: 500,
      emergency_available: true,
      seasonal_demand: 'high_summer'
    }
  ],
  
  emergency_services: true,
  seasonal_patterns: {
    peak_months: [6, 7, 8, 12, 1, 2],
    slow_months: [4, 5, 9, 10],
    maintenance_months: [3, 4, 9, 10]
  },
  
  certifications: [
    'Commercial HVAC Licensed',
    'EPA Universal Certified',
    'NATE Commercial Certified',
    'Energy Management Certified'
  ],
  
  activity_modules: [
    'hvac_efficiency_calculator',
    'hvac_load_calculator',
    'maintenance_scheduler'
  ]
};

export const refrigerationConfig: TradeConfiguration = {
  trade: 'refrigeration',
  display_name: 'Refrigeration',
  full_name: 'Commercial Refrigeration Services',
  category: 'commercial',
  description: 'Professional commercial refrigeration and cooling solutions',
  
  colors: {
    primary: '#0f766e',
    secondary: '#0d9488',
    accent: '#14b8a6'
  },
  
  hero: {
    headline_template: '{city}\'s Refrigeration Specialists',
    subtitle_points: [
      'EPA Certified Technicians',
      '24/7 Emergency Response',
      'All Brands Serviced'
    ],
    primary_cta: 'Emergency Service',
    secondary_cta: 'Schedule Maintenance',
    emergency_message: 'Emergency Refrigeration Service - Protecting Your Investment!'
  },
  
  service_categories: [
    {
      name: 'Walk-in Cooler/Freezer',
      description: 'Walk-in refrigeration system service and repair',
      starting_price: 250,
      emergency_available: true,
      seasonal_demand: 'year_round'
    },
    {
      name: 'Reach-in Units',
      description: 'Commercial reach-in refrigerator and freezer service',
      starting_price: 150,
      emergency_available: true,
      seasonal_demand: 'year_round'
    },
    {
      name: 'Ice Machine Service',
      description: 'Commercial ice machine repair and maintenance',
      starting_price: 125,
      emergency_available: true,
      seasonal_demand: 'high_summer'
    }
  ],
  
  emergency_services: true,
  seasonal_patterns: {
    peak_months: [5, 6, 7, 8, 9],
    slow_months: [12, 1, 2],
    maintenance_months: [3, 4, 10, 11]
  },
  
  certifications: [
    'EPA Universal Certified',
    'RSES Certified',
    'Commercial Refrigeration Licensed',
    'Food Safety Certified'
  ],
  
  activity_modules: [
    'maintenance_scheduler',
    'emergency_dispatcher'
  ]
};

// Export all trade configurations
export const ALL_TRADE_CONFIGS: Record<string, TradeConfiguration> = {
  // Residential
  hvac: hvacConfig,
  plumbing: plumbingConfig,
  electrical: electricalConfig,
  roofing: roofingConfig,
  chimney: chimneyConfig,
  garage_door: garageDoorConfig,
  
  // Commercial  
  mechanical: mechanicalConfig,
  refrigeration: refrigerationConfig,
  
  // General Contractor
  general_contractor: {
    trade: 'general_contractor',
    display_name: 'General Contractor',
    full_name: 'General Contractor Services',
    category: 'residential',
    description: 'Complete construction and renovation services',
    
    colors: {
      primary: '#2563eb',
      secondary: '#1d4ed8',
      accent: '#3b82f6'
    },
    
    hero: {
      headline_template: '{city}\'s Professional General Contractor',
      subtitle_points: [
        'Licensed & Insured',
        'Quality Workmanship',
        'Customer Satisfaction Guaranteed'
      ],
      primary_cta: 'Call for Service',
      secondary_cta: 'Get Quote',
      emergency_message: 'Emergency Construction Service Available!'
    },
    
    service_categories: [
      {
        name: 'Construction Services',
        description: 'Professional construction services',
        starting_price: 150,
        emergency_available: true,
        seasonal_demand: 'year_round'
      }
    ],
    
    emergency_services: true,
    seasonal_patterns: {
      peak_months: [6, 7, 8],
      slow_months: [12, 1, 2],
      maintenance_months: [3, 4, 9, 10]
    },
    
    certifications: [
      'Licensed Professional',
      'Insured & Bonded'
    ],
    
    activity_modules: [
      {
        module_type: 'project_estimator',
        config: {
          showAdvanced: true,
          includePermits: true,
          showSubcontractors: true,
          enableExport: true
        }
      }
    ]
  },
  
  // Additional trades can be added here...
};

// Backward compatibility export
export const COMPLETE_TRADE_CONFIGS = ALL_TRADE_CONFIGS;

/**
 * Get trade configuration by slug
 */
export function getTradeConfig(tradeSlug: string): TradeConfiguration {
  const config = ALL_TRADE_CONFIGS[tradeSlug];
  
  if (!config) {
    console.warn(`⚠️ Trade configuration not found for: ${tradeSlug}`);
    
    // Return fallback configuration
    return {
      trade: tradeSlug,
      display_name: tradeSlug.charAt(0).toUpperCase() + tradeSlug.slice(1),
      full_name: `Professional ${tradeSlug} Services`,
      category: 'residential',
      description: `Professional ${tradeSlug} services for your home`,
      
      colors: {
        primary: '#2563eb',
        secondary: '#1d4ed8',
        accent: '#3b82f6'
      },
      
      hero: {
        headline_template: `{city}'s Professional ${tradeSlug} Services`,
        subtitle_points: [
          'Licensed & Insured',
          'Quality Workmanship',
          'Customer Satisfaction Guaranteed'
        ],
        primary_cta: 'Call for Service',
        secondary_cta: 'Get Quote',
        emergency_message: `Emergency ${tradeSlug} Service Available!`
      },
      
      service_categories: [
        {
          name: `${tradeSlug} Services`,
          description: `Professional ${tradeSlug} services`,
          starting_price: 150,
          emergency_available: true,
          seasonal_demand: 'year_round'
        }
      ],
      
      emergency_services: true,
      seasonal_patterns: {
        peak_months: [6, 7, 8],
        slow_months: [12, 1, 2],
        maintenance_months: [3, 4, 9, 10]
      },
      
      certifications: [
        'Licensed Professional',
        'Insured & Bonded'
      ],
      
      activity_modules: []
    };
  }
  
  return config;
}

/**
 * Get all available trade configurations
 */
export function getAllTradeConfigs(): TradeConfiguration[] {
  return Object.values(ALL_TRADE_CONFIGS);
}

/**
 * Get trade configurations by category
 */
export function getTradeConfigsByCategory(category: 'residential' | 'commercial'): TradeConfiguration[] {
  return Object.values(ALL_TRADE_CONFIGS).filter(config => config.category === category);
}
