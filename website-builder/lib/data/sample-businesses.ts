/**
 * Sample Business Profiles
 * 
 * Example business profiles for different trades to demonstrate the dynamic template system
 */

import { BusinessProfile } from '../types/trade-config';

// Austin Elite HVAC - Residential HVAC
export const austinEliteHVAC: BusinessProfile = {
  name: 'Austin Elite HVAC',
  trade: 'hvac',
  type: 'residential',
  
  phone: '(512) 555-COOL',
  email: 'info@austinelitehvac.com',
  website_url: 'https://austinelitehvac.com',
  
  address: '123 Main St',
  city: 'Austin',
  state: 'TX',
  zip: '78701',
  service_areas: ['Austin', 'Round Rock', 'Cedar Park', 'Pflugerville', 'Georgetown'],
  service_radius_miles: 50,
  
  established_year: 1999,
  license_number: 'TACLA123456',
  insurance_info: 'Fully Licensed & Insured',
  certifications: ['NATE Certified', 'EPA Licensed', 'BBB A+ Rating'],
  
  brand_colors: {
    primary: '#3b82f6',
    secondary: '#1e40af'
  },
  
  social_media: {
    facebook: 'https://facebook.com/austinelitehvac',
    google_business: 'https://g.page/austinelitehvac'
  },
  
  hours: {
    'Monday': { open: '7:00 AM', close: '8:00 PM' },
    'Tuesday': { open: '7:00 AM', close: '8:00 PM' },
    'Wednesday': { open: '7:00 AM', close: '8:00 PM' },
    'Thursday': { open: '7:00 AM', close: '8:00 PM' },
    'Friday': { open: '7:00 AM', close: '8:00 PM' },
    'Saturday': { open: '8:00 AM', close: '6:00 PM' },
    'Sunday': { open: '8:00 AM', close: '6:00 PM' }
  },
  emergency_available: true,
  
  years_in_business: 25,
  customers_served: 5000,
  projects_completed: 8500,
  satisfaction_rate: 98,
  
  team_size: 12,
  owner_name: 'Mike Johnson',
  owner_bio: 'Founded in 1999, Austin Elite HVAC began as a small family business with a simple mission: provide honest, reliable HVAC services to the Austin community. What started with just one truck and a commitment to quality has grown into one of the area\'s most trusted HVAC companies.'
};

// Dallas Pro Plumbing - Residential Plumbing
export const dallasProPlumbing: BusinessProfile = {
  name: 'Dallas Pro Plumbing',
  trade: 'plumbing',
  type: 'residential',
  
  phone: '(214) 555-PIPE',
  email: 'service@dallasplumbing.com',
  website_url: 'https://dallasplumbing.com',
  
  address: '456 Commerce St',
  city: 'Dallas',
  state: 'TX',
  zip: '75201',
  service_areas: ['Dallas', 'Plano', 'Richardson', 'Garland', 'Irving'],
  service_radius_miles: 35,
  
  established_year: 2005,
  license_number: 'MP-39847',
  certifications: ['Licensed Master Plumber', 'Insured & Bonded'],
  
  brand_colors: {
    primary: '#0ea5e9',
    secondary: '#0284c7'
  },
  
  hours: {
    'Monday': { open: '6:00 AM', close: '10:00 PM' },
    'Tuesday': { open: '6:00 AM', close: '10:00 PM' },
    'Wednesday': { open: '6:00 AM', close: '10:00 PM' },
    'Thursday': { open: '6:00 AM', close: '10:00 PM' },
    'Friday': { open: '6:00 AM', close: '10:00 PM' },
    'Saturday': { open: '7:00 AM', close: '8:00 PM' },
    'Sunday': { open: '8:00 AM', close: '6:00 PM' }
  },
  emergency_available: true,
  
  years_in_business: 19,
  customers_served: 3200,
  projects_completed: 5800,
  satisfaction_rate: 96,
  
  team_size: 8,
  owner_name: 'Sarah Martinez',
  owner_bio: 'With nearly two decades of experience, Dallas Pro Plumbing has built a reputation for reliable, professional plumbing services throughout the Dallas metroplex.'
};

// Houston Electrical Solutions - Residential Electrical
export const houstonElectrical: BusinessProfile = {
  name: 'Houston Electrical Solutions',
  trade: 'electrical',
  type: 'residential',
  
  phone: '(713) 555-VOLT',
  email: 'info@houstonelectrical.com',
  
  address: '789 Energy Blvd',
  city: 'Houston',
  state: 'TX',
  zip: '77002',
  service_areas: ['Houston', 'Katy', 'Sugar Land', 'The Woodlands', 'Pearland'],
  service_radius_miles: 40,
  
  established_year: 2010,
  license_number: 'EL-28394',
  certifications: ['Licensed Electrician', 'Code Certified', 'Safety Trained'],
  
  brand_colors: {
    primary: '#eab308',
    secondary: '#ca8a04'
  },
  
  hours: {
    'Monday': { open: '7:00 AM', close: '7:00 PM' },
    'Tuesday': { open: '7:00 AM', close: '7:00 PM' },
    'Wednesday': { open: '7:00 AM', close: '7:00 PM' },
    'Thursday': { open: '7:00 AM', close: '7:00 PM' },
    'Friday': { open: '7:00 AM', close: '7:00 PM' },
    'Saturday': { open: '8:00 AM', close: '5:00 PM' },
    'Sunday': { closed: true, open: '', close: '' }
  },
  emergency_available: true,
  
  years_in_business: 14,
  customers_served: 2800,
  projects_completed: 4200,
  satisfaction_rate: 97,
  
  team_size: 6,
  owner_name: 'David Chen'
};

// Metro Commercial Mechanical - Commercial Mechanical
export const metroMechanical: BusinessProfile = {
  name: 'Metro Commercial Mechanical',
  trade: 'mechanical',
  type: 'commercial',
  
  phone: '(469) 555-MECH',
  email: 'service@metromechanical.com',
  website_url: 'https://metromechanical.com',
  
  address: '1000 Industrial Blvd',
  city: 'Dallas',
  state: 'TX',
  zip: '75207',
  service_areas: ['Dallas', 'Fort Worth', 'Arlington', 'Plano', 'Irving'],
  service_radius_miles: 75,
  
  established_year: 1995,
  license_number: 'CM-15672',
  certifications: ['Licensed Mechanical Engineer', 'Commercial Certified', 'EPA Certified'],
  
  brand_colors: {
    primary: '#374151',
    secondary: '#1f2937'
  },
  
  hours: {
    'Monday': { open: '6:00 AM', close: '6:00 PM' },
    'Tuesday': { open: '6:00 AM', close: '6:00 PM' },
    'Wednesday': { open: '6:00 AM', close: '6:00 PM' },
    'Thursday': { open: '6:00 AM', close: '6:00 PM' },
    'Friday': { open: '6:00 AM', close: '6:00 PM' },
    'Saturday': { open: '8:00 AM', close: '4:00 PM' },
    'Sunday': { closed: true, open: '', close: '' }
  },
  emergency_available: true,
  
  years_in_business: 29,
  customers_served: 850,
  projects_completed: 1200,
  satisfaction_rate: 99,
  
  team_size: 25,
  owner_name: 'Robert Kim',
  owner_bio: 'Metro Commercial Mechanical has been the trusted partner for commercial facilities throughout the Dallas-Fort Worth metroplex for nearly three decades, specializing in large-scale HVAC systems, boiler maintenance, and energy-efficient solutions.'
};

// Export all sample businesses
export const SAMPLE_BUSINESSES = {
  hvac: austinEliteHVAC,
  plumbing: dallasProPlumbing,
  electrical: houstonElectrical,
  mechanical: metroMechanical
};

// Helper function to get sample business by trade
export function getSampleBusiness(trade: string): BusinessProfile | undefined {
  return SAMPLE_BUSINESSES[trade as keyof typeof SAMPLE_BUSINESSES];
}
