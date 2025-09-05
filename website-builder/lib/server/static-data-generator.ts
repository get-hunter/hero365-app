/**
 * Static Data Generator
 * 
 * This service pre-generates all static content at build time to eliminate
 * runtime API calls and improve performance. It creates static JSON files
 * that can be served directly without hitting the backend.
 */

import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';
import type { BusinessContext } from '../types/business-context';
import type { ActivityPageArtifact } from '../types/artifact';
import type { LocationData } from '../types/location';

interface StaticDataConfig {
  businessId: string;
  outputDir: string;
  generateArtifacts: boolean;
  generateBusinessContext: boolean;
  generateLocations: boolean;
}

interface ServiceLocationMatrix {
  services: string[];
  locations: string[];
  variants: ('standard' | 'emergency' | 'commercial')[];
}

export class StaticDataGenerator {
  private config: StaticDataConfig;
  private backendUrl: string;

  constructor(config: StaticDataConfig) {
    this.config = config;
    this.backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
  }

  /**
   * Generate all static data files
   */
  async generateAll(): Promise<void> {
    console.log('🏗️ [STATIC] Starting static data generation...');
    
    // Ensure output directory exists
    this.ensureOutputDir();

    try {
      // Generate business context (cached for entire build)
      let businessContext: BusinessContext | null = null;
      if (this.config.generateBusinessContext) {
        businessContext = await this.generateBusinessContext();
      }

      // Generate service-location matrix
      const matrix = await this.generateServiceLocationMatrix();
      
      // Generate artifacts for all service-location combinations
      if (this.config.generateArtifacts) {
        await this.generateAllArtifacts(matrix, businessContext);
      }

      // Generate location data
      if (this.config.generateLocations) {
        await this.generateLocationData(matrix.locations);
      }

      console.log('✅ [STATIC] Static data generation completed successfully');
      
    } catch (error) {
      console.error('❌ [STATIC] Static data generation failed:', error);
      throw error;
    }
  }

  /**
   * Generate business context and save to static file
   */
  private async generateBusinessContext(): Promise<BusinessContext> {
    console.log('🏢 [STATIC] Generating business context...');
    
    try {
      // Try to fetch from backend first
      const response = await fetch(`${this.backendUrl}/api/v1/public/professional/business-context?business_id=${this.config.businessId}`);
      
      let businessContext: BusinessContext;
      
      if (response.ok) {
        businessContext = await response.json();
        console.log('✅ [STATIC] Business context fetched from API');
      } else {
        console.error(`❌ [STATIC] Business context API failed: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to fetch business context: ${response.status} ${response.statusText}`);
      }

      // Save to static file
      const filePath = join(this.config.outputDir, 'business-context.json');
      writeFileSync(filePath, JSON.stringify(businessContext, null, 2));
      console.log(`💾 [STATIC] Business context saved to ${filePath}`);

      return businessContext;
      
    } catch (error) {
      console.error('❌ [STATIC] Error fetching business context:', error);
      throw new Error(`Failed to generate static business context: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Generate service-location matrix
   */
  private async generateServiceLocationMatrix(): Promise<ServiceLocationMatrix> {
    console.log('📊 [STATIC] Generating service-location matrix...');
    
    // Define comprehensive service list
    const services = [
      'hvac-repair', 'hvac-installation', 'hvac-maintenance',
      'ac-repair', 'ac-installation', 'ac-maintenance',
      'heating-repair', 'heating-installation', 'heating-maintenance',
      'plumbing-repair', 'plumbing-installation', 'plumbing-maintenance',
      'electrical-repair', 'electrical-installation', 'electrical-maintenance',
      'water-heater-repair', 'water-heater-installation',
      'drain-cleaning', 'pipe-repair', 'fixture-installation',
      'emergency-plumbing', 'emergency-hvac', 'emergency-electrical'
    ];

    // Define comprehensive location list for Texas
    const locations = [
      'austin-tx', 'houston-tx', 'dallas-tx', 'san-antonio-tx',
      'fort-worth-tx', 'el-paso-tx', 'arlington-tx', 'corpus-christi-tx',
      'plano-tx', 'lubbock-tx', 'laredo-tx', 'garland-tx',
      'irving-tx', 'amarillo-tx', 'grand-prairie-tx', 'brownsville-tx',
      'mckinney-tx', 'frisco-tx', 'pasadena-tx', 'killeen-tx',
      'mesquite-tx', 'mcallen-tx', 'carrollton-tx', 'midland-tx',
      'denton-tx', 'abilene-tx', 'beaumont-tx', 'round-rock-tx',
      'richardson-tx', 'odessa-tx', 'waco-tx', 'lewisville-tx',
      'tyler-tx', 'college-station-tx', 'pearland-tx', 'sugar-land-tx',
      'cedar-park-tx', 'pflugerville-tx', 'georgetown-tx', 'kyle-tx'
    ];

    const variants: ('standard' | 'emergency' | 'commercial')[] = ['standard', 'emergency', 'commercial'];

    const matrix = { services, locations, variants };
    
    // Save matrix to static file
    const filePath = join(this.config.outputDir, 'service-location-matrix.json');
    writeFileSync(filePath, JSON.stringify(matrix, null, 2));
    
    console.log(`📊 [STATIC] Matrix: ${services.length} services × ${locations.length} locations × ${variants.length} variants = ${services.length * locations.length * variants.length} total pages`);
    
    return matrix;
  }

  /**
   * Generate artifacts for all service-location combinations
   */
  private async generateAllArtifacts(matrix: ServiceLocationMatrix, businessContext: BusinessContext | null): Promise<void> {
    console.log('🎯 [STATIC] Generating artifacts for all combinations...');
    
    const artifactsDir = join(this.config.outputDir, 'artifacts');
    this.ensureDir(artifactsDir);

    let generated = 0;
    const total = matrix.services.length * matrix.locations.length * matrix.variants.length;

    for (const service of matrix.services) {
      for (const location of matrix.locations) {
        for (const variant of matrix.variants) {
          try {
            const artifact = await this.generateArtifact(service, location, variant, businessContext);
            
            // Save artifact to static file
            const fileName = `${service}-${location}-${variant}.json`;
            const filePath = join(artifactsDir, fileName);
            writeFileSync(filePath, JSON.stringify(artifact, null, 2));
            
            generated++;
            
            if (generated % 100 === 0) {
              console.log(`📄 [STATIC] Generated ${generated}/${total} artifacts...`);
            }
            
          } catch (error) {
            console.warn(`⚠️ [STATIC] Failed to generate artifact for ${service}-${location}-${variant}:`, error);
          }
        }
      }
    }

    console.log(`✅ [STATIC] Generated ${generated} artifacts`);
  }

  /**
   * Generate a single artifact
   */
  private async generateArtifact(
    service: string, 
    location: string, 
    variant: 'standard' | 'emergency' | 'commercial',
    businessContext: BusinessContext | null
  ): Promise<ActivityPageArtifact> {
    
    // Parse location
    const [city, state] = location.split('-');
    const cityName = city.split('-').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
    
    // Parse service
    const serviceName = service.split('-').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');

    // Get business name
    const businessName = businessContext?.business?.name || 'Elite HVAC Austin';

    // Generate variant-specific content
    let titlePrefix = '';
    let descriptionPrefix = '';
    
    switch (variant) {
      case 'emergency':
        titlePrefix = '24/7 Emergency ';
        descriptionPrefix = 'Emergency ';
        break;
      case 'commercial':
        titlePrefix = 'Commercial ';
        descriptionPrefix = 'Professional commercial ';
        break;
      default:
        titlePrefix = '';
        descriptionPrefix = 'Professional ';
    }

    const artifact: ActivityPageArtifact = {
      artifact_id: `${service}-${location}-${variant}`,
      business_id: this.config.businessId,
      activity_name: serviceName,
      activity_slug: service,
      location_slug: location,
      page_variant: variant,
      
      // SEO Meta Data
      meta_title: `${titlePrefix}${serviceName} in ${cityName}, ${state.toUpperCase()} | ${businessName}`,
      meta_description: businessContext?.business?.phone 
        ? `${descriptionPrefix}${serviceName.toLowerCase()} services in ${cityName}, ${state.toUpperCase()}. Licensed, insured, and available 24/7. Call ${businessContext.business.phone} for immediate service.`
        : `${descriptionPrefix}${serviceName.toLowerCase()} services in ${cityName}, ${state.toUpperCase()}. Licensed, insured, and available 24/7.`,
      canonical_url: variant === 'standard' 
        ? `/services/${service}/${location}`
        : `/${variant}/${service}/${location}`,
      
      // Content Blocks
      content_blocks: {
        overview: `Expert ${serviceName.toLowerCase()} services for ${cityName} residents and businesses. Our licensed technicians provide reliable, professional service with upfront pricing and guaranteed satisfaction.`,
        benefits: [
          {
            title: 'Licensed & Insured',
            description: 'Fully licensed technicians with comprehensive insurance coverage for your peace of mind.'
          },
          {
            title: 'Upfront Pricing',
            description: 'No hidden fees or surprise charges. You know the cost before we start the work.'
          },
          {
            title: variant === 'emergency' ? '24/7 Availability' : 'Same-Day Service',
            description: variant === 'emergency' 
              ? 'Emergency service available 24 hours a day, 7 days a week, including holidays.'
              : 'Most repairs completed the same day. We respect your time and schedule.'
          }
        ]
      },

      // Activity Modules
      activity_modules: [
        {
          module_id: `${service}-booking`,
          module_type: 'booking_form',
          title: `Schedule Your ${serviceName}`,
          description: `Book your ${serviceName.toLowerCase()} service online or call us directly.`,
          config: {
            service_type: service,
            location: location,
            variant: variant
          }
        }
      ],

      // Process Steps
      process: {
        'Initial Assessment': `We assess your ${serviceName.toLowerCase()} needs and provide upfront pricing.`,
        'Professional Service': 'Our licensed technicians complete the work using quality parts and proven methods.',
        'Quality Guarantee': 'We stand behind our work with comprehensive warranties and satisfaction guarantees.'
      },

      // Benefits
      benefits: {
        'Expert Technicians': `Highly trained professionals specializing in ${serviceName.toLowerCase()}.`,
        'Quality Parts': 'We use only high-quality, manufacturer-approved parts and materials.',
        'Satisfaction Guaranteed': '100% satisfaction guarantee on all work performed.',
        'Competitive Pricing': 'Fair, transparent pricing with no hidden fees or surprises.'
      },

      // Offers
      offers: {
        items: [
          {
            title: `${serviceName} Special`,
            description: `Save on your ${serviceName.toLowerCase()} service. Call for details.`,
            price: 'Call for Pricing'
          }
        ]
      },

      // FAQs
      faqs: [
        {
          question: `How quickly can you provide ${serviceName.toLowerCase()} service?`,
          answer: variant === 'emergency' 
            ? 'We provide 24/7 emergency service and can typically arrive within 1-2 hours of your call.'
            : 'We offer same-day service for most repairs and can schedule installations at your convenience.'
        },
        {
          question: 'Are you licensed and insured?',
          answer: `Yes, we are fully licensed and insured. All our technicians are certified professionals with extensive experience in ${serviceName.toLowerCase()}.`
        },
        {
          question: 'Do you provide warranties on your work?',
          answer: 'Yes, we provide comprehensive warranties on both parts and labor. Warranty terms vary by service type.'
        }
      ],

      // CTA Sections
      cta_sections: [
        {
          title: `Need ${titlePrefix}${serviceName}?`,
          subtitle: `Professional ${serviceName.toLowerCase()} services in ${cityName}, ${state.toUpperCase()}`,
          cta_text: 'Call Now',
          cta_url: businessContext?.business?.phone ? `tel:${businessContext.business.phone.replace(/\D/g, '')}` : undefined
        }
      ],

      // JSON-LD Schemas (basic structure)
      json_ld_schemas: [],

      // Metadata
      status: 'published' as const,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      active_experiment_keys: []
    };

    return artifact;
  }

  /**
   * Generate location data for all locations
   */
  private async generateLocationData(locations: string[]): Promise<void> {
    console.log('📍 [STATIC] Generating location data...');
    
    const locationsDir = join(this.config.outputDir, 'locations');
    this.ensureDir(locationsDir);

    for (const location of locations) {
      const locationData = this.generateLocationInfo(location);
      
      const filePath = join(locationsDir, `${location}.json`);
      writeFileSync(filePath, JSON.stringify(locationData, null, 2));
    }

    console.log(`📍 [STATIC] Generated ${locations.length} location files`);
  }

  /**
   * Generate location information
   */
  private generateLocationInfo(locationSlug: string): LocationData {
    const [city, state] = locationSlug.split('-');
    const cityName = city.split('-').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');

    return {
      slug: locationSlug,
      city: cityName,
      state: state.toUpperCase(),
      full_name: `${cityName}, ${state.toUpperCase()}`,
      coordinates: {
        latitude: 30.2672, // Default to Austin coordinates
        longitude: -97.7431
      },
      timezone: 'America/Chicago',
      population: 0, // Would be populated from real data
      service_area_radius: 25
    };
  }


  /**
   * Ensure directory exists
   */
  private ensureDir(dir: string): void {
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }
  }

  /**
   * Ensure output directory exists
   */
  private ensureOutputDir(): void {
    this.ensureDir(this.config.outputDir);
  }
}

/**
 * Build-time static data generation
 */
export async function generateStaticData(businessId?: string): Promise<void> {
  const config: StaticDataConfig = {
    businessId: businessId || process.env.NEXT_PUBLIC_BUSINESS_ID || '550e8400-e29b-41d4-a716-446655440010',
    outputDir: join(process.cwd(), 'public', 'static-data'),
    generateArtifacts: true,
    generateBusinessContext: true,
    generateLocations: true
  };

  const generator = new StaticDataGenerator(config);
  await generator.generateAll();
}
