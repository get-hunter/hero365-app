/**
 * Dynamic Template Generator
 * 
 * Generates professional website content based on business profile and trade configuration
 */

import { BusinessProfile, TradeConfiguration } from '../types/trade-config';
import { getTradeConfig } from '../config/trade-configs';

export interface GeneratedContent {
  business: EnhancedBusinessData;
  hero: HeroContent;
  services: ServiceContent;
  about: AboutContent;
  trust: TrustContent;
  seo: SEOContent;
  booking: BookingContent;
  colors: ColorScheme;
}

export interface EnhancedBusinessData extends BusinessProfile {
  display_name: string;
  professional_title: string;
  service_description: string;
  emergency_phone: string;
  formatted_address: string;
  years_in_business_display: string;
}

export interface HeroContent {
  headline: string;
  subtitle_points: string[];
  emergency_message?: string;
  primary_cta: string;
  secondary_cta: string;
  trust_indicators: string[];
  background_image?: string;
}

export interface ServiceContent {
  section_title: string;
  section_description: string;
  categories: Array<{
    id: string;
    name: string;
    description: string;
    icon: string;
    starting_price?: number;
    is_emergency?: boolean;
    is_popular?: boolean;
    cta_text: string;
    services: Array<{
      name: string;
      description: string;
      price_display: string;
      features: string[];
    }>;
  }>;
  emergency_section?: {
    title: string;
    description: string;
    cta_text: string;
    phone: string;
  };
}

export interface AboutContent {
  section_title: string;
  company_story: string;
  mission_statement: string;
  stats: Array<{
    value: string;
    label: string;
    description: string;
  }>;
  values: Array<{
    title: string;
    description: string;
    icon: string;
  }>;
  team?: Array<{
    name: string;
    title: string;
    bio: string;
    certifications: string[];
  }>;
}

export interface TrustContent {
  certifications: Array<{
    name: string;
    issuer: string;
    icon: string;
  }>;
  guarantees: string[];
  features: string[];
  reviews_summary: {
    average_rating: number;
    total_reviews: number;
    platform: string;
  };
}

export interface SEOContent {
  title: string;
  description: string;
  keywords: string[];
  structured_data: any;
}

export interface BookingContent {
  section_title: string;
  section_description: string;
  default_services: string[];
  emergency_services: string[];
  lead_times: {
    emergency_display: string;
    standard_display: string;
    maintenance_display: string;
  };
}

export interface ColorScheme {
  primary: string;
  secondary: string;
  accent: string;
  emergency: string;
  success: string;
  warning: string;
}

export class TemplateGenerator {
  private business: BusinessProfile;
  private tradeConfig: TradeConfiguration;

  constructor(business: BusinessProfile) {
    this.business = business;
    this.tradeConfig = getTradeConfig(business.trade);
  }

  generate(): GeneratedContent {
    return {
      business: this.generateBusinessData(),
      hero: this.generateHeroContent(),
      services: this.generateServiceContent(),
      about: this.generateAboutContent(),
      trust: this.generateTrustContent(),
      seo: this.generateSEOContent(),
      booking: this.generateBookingContent(),
      colors: this.generateColorScheme()
    };
  }

  private generateBusinessData(): EnhancedBusinessData {
    const currentYear = new Date().getFullYear();
    const yearsInBusiness = this.business.established_year 
      ? currentYear - this.business.established_year 
      : this.business.years_in_business || 0;

    return {
      ...this.business,
      display_name: this.business.name,
      professional_title: this.tradeConfig.industry_terms.professional_title,
      service_description: this.tradeConfig.industry_terms.service_area,
      emergency_phone: this.business.phone,
      formatted_address: `${this.business.address}, ${this.business.city}, ${this.business.state} ${this.business.zip}`,
      years_in_business_display: yearsInBusiness > 0 ? `${yearsInBusiness}+ Years` : 'Experienced'
    };
  }

  private generateHeroContent(): HeroContent {
    const headline = this.tradeConfig.hero.headline_template
      .replace('{city}', this.business.city)
      .replace('{trade}', this.tradeConfig.display_name);

    return {
      headline,
      subtitle_points: this.tradeConfig.hero.subtitle_points,
      emergency_message: this.tradeConfig.hero.emergency_message,
      primary_cta: this.tradeConfig.hero.primary_cta,
      secondary_cta: this.tradeConfig.hero.secondary_cta,
      trust_indicators: this.tradeConfig.trust_indicators.features
    };
  }

  private generateServiceContent(): ServiceContent {
    const categories = this.tradeConfig.service_categories.map(category => ({
      ...category,
      cta_text: `Book ${category.name}`,
      services: category.services.map(service => ({
        name: service.name,
        description: service.description,
        price_display: this.formatPrice(service.base_price, service.price_type),
        features: this.generateServiceFeatures(service)
      }))
    }));

    const emergencyCategory = categories.find(cat => cat.is_emergency);
    const emergencySection = emergencyCategory ? {
      title: `24/7 ${this.tradeConfig.industry_terms.emergency_type.charAt(0).toUpperCase() + this.tradeConfig.industry_terms.emergency_type.slice(1)} Service`,
      description: `Don't wait when you have an emergency. Our certified ${this.tradeConfig.industry_terms.professional_title.toLowerCase()}s are standing by to help.`,
      cta_text: `Call Emergency Line`,
      phone: this.business.phone
    } : undefined;

    return {
      section_title: `Our Professional ${this.tradeConfig.display_name}`,
      section_description: `From emergency repairs to complete installations, we provide comprehensive ${this.tradeConfig.industry_terms.service_area} for homes and businesses throughout the ${this.business.city} area. All work backed by our 100% satisfaction guarantee.`,
      categories,
      emergency_section: emergencySection
    };
  }

  private generateAboutContent(): AboutContent {
    const currentYear = new Date().getFullYear();
    const establishedYear = this.business.established_year || currentYear - (this.business.years_in_business || 5);
    const yearsInBusiness = currentYear - establishedYear;

    const stats = [
      {
        value: `${yearsInBusiness}+`,
        label: 'Years in Business',
        description: `Serving ${this.business.city} since ${establishedYear}`
      },
      {
        value: `${this.business.customers_served || '5K'}+`,
        label: 'Happy Customers',
        description: 'Satisfied homeowners and businesses'
      },
      {
        value: `${this.business.projects_completed || '8K'}+`,
        label: 'Projects Completed',
        description: 'Successful installations and repairs'
      },
      {
        value: `${this.business.satisfaction_rate || 98}%`,
        label: 'Satisfaction Rate',
        description: 'Customer satisfaction guaranteed'
      }
    ];

    const companyStory = this.business.owner_bio || 
      `Founded in ${establishedYear}, ${this.business.name} began as a small family business with a simple mission: provide honest, reliable ${this.tradeConfig.industry_terms.service_area} to the ${this.business.city} community. What started with just one truck and a commitment to quality has grown into one of the area's most trusted ${this.tradeConfig.display_name.toLowerCase()} companies.`;

    return {
      section_title: `About ${this.business.name}`,
      company_story: companyStory,
      mission_statement: `We believe that your home's comfort shouldn't be compromised, which is why we're available ${this.business.emergency_available ? '24/7 for emergency services' : 'when you need us most'}.`,
      stats,
      values: [
        {
          title: 'Integrity First',
          description: 'We believe in honest, transparent service with no hidden fees or unnecessary upsells.',
          icon: 'shield'
        },
        {
          title: 'Quality Workmanship',
          description: 'Every job is completed to the highest standards with attention to detail and craftsmanship.',
          icon: 'award'
        },
        {
          title: 'Customer Focus',
          description: 'Your comfort and satisfaction are our top priorities. We listen and deliver solutions.',
          icon: 'users'
        },
        {
          title: 'Reliable Service',
          description: 'On-time service, quick response, and dependable solutions you can count on.',
          icon: 'clock'
        }
      ]
    };
  }

  private generateTrustContent(): TrustContent {
    const certifications = this.tradeConfig.trust_indicators.certifications.map(cert => ({
      name: cert,
      issuer: this.getCertificationIssuer(cert),
      icon: this.getCertificationIcon(cert)
    }));

    return {
      certifications,
      guarantees: this.tradeConfig.trust_indicators.guarantees,
      features: this.tradeConfig.trust_indicators.features,
      reviews_summary: {
        average_rating: 4.9,
        total_reviews: 247,
        platform: 'Google'
      }
    };
  }

  private generateSEOContent(): SEOContent {
    const title = this.tradeConfig.seo.title_template
      .replace('{business_name}', this.business.name)
      .replace('{city}', this.business.city)
      .replace('{state}', this.business.state);

    const description = this.tradeConfig.seo.description_template
      .replace('{city}', this.business.city)
      .replace('{state}', this.business.state);

    return {
      title,
      description,
      keywords: this.tradeConfig.seo.keywords,
      structured_data: this.generateStructuredData()
    };
  }

  private generateBookingContent(): BookingContent {
    return {
      section_title: `Schedule Your ${this.tradeConfig.display_name}`,
      section_description: 'Book your appointment online in just a few simple steps. Choose your service, pick a convenient time, and we\'ll take care of the rest.',
      default_services: this.tradeConfig.booking.default_services,
      emergency_services: this.tradeConfig.booking.emergency_services,
      lead_times: {
        emergency_display: `${this.tradeConfig.booking.lead_times.emergency_hours} hours`,
        standard_display: `${this.tradeConfig.booking.lead_times.standard_hours} hours`,
        maintenance_display: `${this.tradeConfig.booking.lead_times.maintenance_days} days`
      }
    };
  }

  private generateColorScheme(): ColorScheme {
    const brandColors = this.business.brand_colors;
    
    return {
      primary: brandColors?.primary || this.tradeConfig.colors.primary,
      secondary: brandColors?.secondary || this.tradeConfig.colors.secondary,
      accent: this.tradeConfig.colors.accent,
      emergency: this.tradeConfig.colors.emergency,
      success: '#10b981',
      warning: '#f59e0b'
    };
  }

  private formatPrice(price?: number, type?: string): string {
    if (!price) return 'Free Quote';
    
    switch (type) {
      case 'fixed':
        return `$${price}`;
      case 'hourly':
        return `$${price}/hr`;
      case 'estimate':
      default:
        return `From $${price}`;
    }
  }

  private generateServiceFeatures(service: any): string[] {
    const baseFeatures = [];
    
    if (service.is_emergency) {
      baseFeatures.push('24/7 Emergency Service');
    }
    
    if (service.requires_site_visit) {
      baseFeatures.push('On-site Service');
    }
    
    if (service.price_type === 'fixed') {
      baseFeatures.push('Fixed Price');
    }
    
    baseFeatures.push('Licensed & Insured');
    baseFeatures.push('Satisfaction Guaranteed');
    
    return baseFeatures;
  }

  private getCertificationIssuer(cert: string): string {
    const issuers: Record<string, string> = {
      'NATE Certified': 'North American Technician Excellence',
      'EPA Licensed': 'Environmental Protection Agency',
      'BBB A+ Rating': 'Better Business Bureau',
      'Licensed Electrician': 'State Licensing Board',
      'Licensed Plumber': 'State Licensing Board',
      'Master Plumber Certified': 'State Master Plumber Board'
    };
    
    return issuers[cert] || 'Professional Certification';
  }

  private getCertificationIcon(cert: string): string {
    const icons: Record<string, string> = {
      'NATE Certified': 'award',
      'EPA Licensed': 'shield',
      'BBB A+ Rating': 'star',
      'Licensed Electrician': 'zap',
      'Licensed Plumber': 'droplets'
    };
    
    return icons[cert] || 'certificate';
  }

  private generateStructuredData(): any {
    return {
      "@context": "https://schema.org",
      "@type": "LocalBusiness",
      "name": this.business.name,
      "description": `Professional ${this.tradeConfig.industry_terms.service_area} in ${this.business.city}, ${this.business.state}`,
      "telephone": this.business.phone,
      "email": this.business.email,
      "address": {
        "@type": "PostalAddress",
        "streetAddress": this.business.address,
        "addressLocality": this.business.city,
        "addressRegion": this.business.state,
        "postalCode": this.business.zip
      },
      "geo": {
        "@type": "GeoCoordinates"
      },
      "openingHours": this.formatOpeningHours(),
      "serviceArea": {
        "@type": "GeoCircle",
        "geoMidpoint": {
          "@type": "GeoCoordinates"
        },
        "geoRadius": `${this.business.service_radius_miles || 25} miles`
      }
    };
  }

  private formatOpeningHours(): string[] {
    const hours = this.business.hours;
    const formatted: string[] = [];
    
    Object.entries(hours).forEach(([day, schedule]) => {
      if (!schedule.closed) {
        formatted.push(`${day} ${schedule.open}-${schedule.close}`);
      }
    });
    
    return formatted;
  }
}

// Factory function to create template generator
export function createTemplateGenerator(business: BusinessProfile): TemplateGenerator {
  return new TemplateGenerator(business);
}
