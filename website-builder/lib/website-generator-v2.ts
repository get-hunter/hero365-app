/**
 * Website Generator V2 - 10X Engineer Approach
 * Uses existing business data and branding for instant deployment
 */

import { promises as fs } from 'fs';
import path from 'path';
import { generateStaticParams } from 'next/dist/build/utils';

interface BusinessData {
  id: string;
  name: string;
  primary_trade: string;
  phone: string;
  email: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  year_established: number;
  certifications: string[];
  services: ServiceData[];
  locations: LocationData[];
}

interface ServiceData {
  service_name: string;
  service_slug: string;
  description: string;
  price_min: number;
  price_max: number;
  category: string;
}

interface LocationData {
  city: string;
  state: string;
  zip_code: string;
  service_radius: number;
}

interface BrandingData {
  color_scheme: {
    primary: string;
    secondary: string;
    accent: string;
  };
  typography: {
    heading: string;
    body: string;
  };
  assets: {
    logo_url?: string;
    favicon_url?: string;
  };
}

interface WebsiteConfig {
  enabled_pages: {
    home: boolean;
    services: boolean;
    products: boolean;
    projects: boolean;
    booking: boolean;
    pricing: boolean;
    about: boolean;
    contact: boolean;
    locations?: string[];
  };
  seo_config: {
    title_template: string;
    meta_description: string;
    keywords: string[];
    business_schema: any;
  };
  content_overrides: Record<string, string>;
}

export class WebsiteGeneratorV2 {
  private buildDir: string;
  private outputDir: string;

  constructor(buildId: string) {
    this.buildDir = path.join(process.cwd(), 'builds', buildId);
    this.outputDir = path.join(this.buildDir, 'out');
  }

  /**
   * Generate complete website from business data
   */
  async generateWebsite(
    businessData: BusinessData,
    branding: BrandingData,
    config: WebsiteConfig
  ): Promise<{
    buildPath: string;
    pages: string[];
    buildTime: number;
    lighthouseScore?: number;
  }> {
    const startTime = Date.now();

    try {
      // 1. Setup build environment
      await this.setupBuildEnvironment();

      // 2. Apply branding (CSS variables)
      await this.applyBranding(branding);

      // 3. Generate configuration files
      await this.generateConfigFiles(businessData, config);

      // 4. Generate only enabled pages
      const pages = await this.generatePages(businessData, config);

      // 5. Generate dynamic SEO pages
      const seoPages = await this.generateSEOPages(businessData, config);

      // 6. Build static site
      await this.buildStaticSite();

      // 7. Optimize assets
      await this.optimizeAssets();

      const buildTime = Date.now() - startTime;

      return {
        buildPath: this.outputDir,
        pages: [...pages, ...seoPages],
        buildTime,
      };
    } catch (error) {
      console.error('Website generation failed:', error);
      throw error;
    }
  }

  /**
   * Apply branding using CSS variables
   */
  private async applyBranding(branding: BrandingData): Promise<void> {
    const cssVariables = `
      :root {
        /* Brand Colors */
        --color-primary: ${branding.color_scheme.primary};
        --color-secondary: ${branding.color_scheme.secondary};
        --color-accent: ${branding.color_scheme.accent};
        
        /* Typography */
        --font-heading: '${branding.typography.heading}', system-ui, sans-serif;
        --font-body: '${branding.typography.body}', system-ui, sans-serif;
        
        /* Logo */
        --logo-url: ${branding.assets.logo_url ? `url('${branding.assets.logo_url}')` : 'none'};
      }

      /* Apply variables to components */
      .hero {
        background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
        font-family: var(--font-heading);
      }

      .btn-primary {
        background: var(--color-accent);
        border-color: var(--color-accent);
      }

      .btn-primary:hover {
        background: color-mix(in srgb, var(--color-accent) 85%, black);
      }

      .text-primary {
        color: var(--color-primary);
      }

      .border-primary {
        border-color: var(--color-primary);
      }

      .logo {
        background-image: var(--logo-url);
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
      }

      h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-heading);
      }

      body {
        font-family: var(--font-body);
      }
    `;

    await fs.writeFile(
      path.join(this.buildDir, 'styles', 'branding.css'),
      cssVariables
    );
  }

  /**
   * Generate configuration files for Next.js
   */
  private async generateConfigFiles(
    businessData: BusinessData,
    config: WebsiteConfig
  ): Promise<void> {
    // Generate site configuration
    const siteConfig = {
      business: {
        name: businessData.name,
        phone: businessData.phone,
        email: businessData.email,
        address: {
          street: businessData.address,
          city: businessData.city,
          state: businessData.state,
          zip: businessData.zip_code,
        },
        trade: businessData.primary_trade,
        yearEstablished: businessData.year_established,
        certifications: businessData.certifications,
      },
      seo: config.seo_config,
      pages: config.enabled_pages,
      contentOverrides: config.content_overrides,
    };

    await fs.writeFile(
      path.join(this.buildDir, 'config', 'site.json'),
      JSON.stringify(siteConfig, null, 2)
    );

    // Generate services data
    await fs.writeFile(
      path.join(this.buildDir, 'data', 'services.json'),
      JSON.stringify(businessData.services, null, 2)
    );

    // Generate locations data
    await fs.writeFile(
      path.join(this.buildDir, 'data', 'locations.json'),
      JSON.stringify(businessData.locations, null, 2)
    );
  }

  /**
   * Generate only enabled pages
   */
  private async generatePages(
    businessData: BusinessData,
    config: WebsiteConfig
  ): Promise<string[]> {
    const pages: string[] = [];
    const { enabled_pages } = config;

    // Always generate home page
    if (enabled_pages.home) {
      await this.generateHomePage(businessData, config);
      pages.push('/');
    }

    // Services page
    if (enabled_pages.services) {
      await this.generateServicesPage(businessData);
      pages.push('/services');
    }

    // Products page (only if they have products)
    if (enabled_pages.products) {
      await this.generateProductsPage(businessData);
      pages.push('/products');
    }

    // Projects page (only if they have projects)
    if (enabled_pages.projects) {
      await this.generateProjectsPage(businessData);
      pages.push('/projects');
    }

    // Booking page (only if they have bookable services)
    if (enabled_pages.booking) {
      await this.generateBookingPage(businessData);
      pages.push('/booking');
    }

    // Pricing page (only if they want public pricing)
    if (enabled_pages.pricing) {
      await this.generatePricingPage(businessData);
      pages.push('/pricing');
    }

    // About page
    if (enabled_pages.about) {
      await this.generateAboutPage(businessData);
      pages.push('/about');
    }

    // Contact page
    if (enabled_pages.contact) {
      await this.generateContactPage(businessData);
      pages.push('/contact');
    }

    return pages;
  }

  /**
   * Generate SEO location pages
   */
  private async generateSEOPages(
    businessData: BusinessData,
    config: WebsiteConfig
  ): Promise<string[]> {
    const pages: string[] = [];
    const { enabled_pages } = config;

    if (!enabled_pages.locations?.length) {
      return pages;
    }

    // Generate location overview pages
    for (const locationSlug of enabled_pages.locations) {
      const location = businessData.locations.find(
        l => this.slugify(`${l.city}-${l.state}`) === locationSlug
      );

      if (location) {
        await this.generateLocationPage(location, businessData);
        pages.push(`/locations/${locationSlug}`);

        // Generate service + location combo pages (SEO gold)
        for (const service of businessData.services.slice(0, 5)) {
          const serviceLocationSlug = `${service.service_slug}-${locationSlug}`;
          await this.generateServiceLocationPage(service, location, businessData);
          pages.push(`/services/${serviceLocationSlug}`);
        }
      }
    }

    return pages;
  }

  /**
   * Generate home page with dynamic content
   */
  private async generateHomePage(
    businessData: BusinessData,
    config: WebsiteConfig
  ): Promise<void> {
    const { content_overrides } = config;
    
    const homePageData = {
      hero: {
        title: content_overrides.hero_title || 
               `${businessData.primary_trade} Services in ${businessData.city}`,
        subtitle: content_overrides.hero_subtitle || 
                 `Professional ${businessData.primary_trade.toLowerCase()} services since ${businessData.year_established}`,
        cta: content_overrides.cta_text || 'Get Free Estimate',
        phone: businessData.phone,
      },
      services: businessData.services.slice(0, 6), // Top 6 services
      trustSignals: {
        yearsInBusiness: new Date().getFullYear() - businessData.year_established,
        certifications: businessData.certifications,
        serviceAreas: businessData.locations.length,
      },
      emergencyService: businessData.primary_trade === 'HVAC' || 
                      businessData.primary_trade === 'Plumbing',
    };

    await fs.writeFile(
      path.join(this.buildDir, 'data', 'home.json'),
      JSON.stringify(homePageData, null, 2)
    );
  }

  /**
   * Generate service + location landing page
   */
  private async generateServiceLocationPage(
    service: ServiceData,
    location: LocationData,
    businessData: BusinessData
  ): Promise<void> {
    const pageData = {
      service,
      location,
      business: businessData,
      seo: {
        title: `${service.service_name} in ${location.city}, ${location.state} | ${businessData.name}`,
        description: `Professional ${service.service_name.toLowerCase()} services in ${location.city}, ${location.state}. Licensed, insured, and available 24/7.`,
        h1: `Expert ${service.service_name} in ${location.city}`,
      },
      schema: {
        '@context': 'https://schema.org',
        '@type': 'Service',
        name: service.service_name,
        description: service.description,
        provider: {
          '@type': 'LocalBusiness',
          name: businessData.name,
          telephone: businessData.phone,
          address: {
            '@type': 'PostalAddress',
            addressLocality: location.city,
            addressRegion: location.state,
          },
        },
        areaServed: {
          '@type': 'City',
          name: location.city,
        },
        offers: {
          '@type': 'Offer',
          priceRange: `$${service.price_min}-$${service.price_max}`,
        },
      },
    };

    const slug = `${service.service_slug}-${this.slugify(`${location.city}-${location.state}`)}`;
    
    await fs.writeFile(
      path.join(this.buildDir, 'data', 'service-locations', `${slug}.json`),
      JSON.stringify(pageData, null, 2)
    );
  }

  /**
   * Build static site using Next.js
   */
  private async buildStaticSite(): Promise<void> {
    const { spawn } = require('child_process');
    
    return new Promise((resolve, reject) => {
      const buildProcess = spawn('npm', ['run', 'build'], {
        cwd: this.buildDir,
        stdio: 'inherit',
      });

      buildProcess.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`Build failed with code ${code}`));
        }
      });
    });
  }

  /**
   * Optimize assets for performance
   */
  private async optimizeAssets(): Promise<void> {
    // Compress images
    // Minify CSS/JS
    // Generate WebP versions
    // This would integrate with image optimization service
    console.log('Optimizing assets...');
  }

  /**
   * Setup build environment
   */
  private async setupBuildEnvironment(): Promise<void> {
    // Create build directories
    await fs.mkdir(this.buildDir, { recursive: true });
    await fs.mkdir(path.join(this.buildDir, 'data'), { recursive: true });
    await fs.mkdir(path.join(this.buildDir, 'data', 'service-locations'), { recursive: true });
    await fs.mkdir(path.join(this.buildDir, 'styles'), { recursive: true });
    await fs.mkdir(path.join(this.buildDir, 'config'), { recursive: true });

    // Copy base website template
    // This would copy our existing Next.js website as the base
    console.log('Setting up build environment...');
  }

  private slugify(text: string): string {
    return text
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  }

  // Placeholder methods for other page types
  private async generateServicesPage(businessData: BusinessData): Promise<void> {
    // Generate services listing page
  }

  private async generateProductsPage(businessData: BusinessData): Promise<void> {
    // Generate products page (only if they have products)
  }

  private async generateProjectsPage(businessData: BusinessData): Promise<void> {
    // Generate projects/portfolio page
  }

  private async generateBookingPage(businessData: BusinessData): Promise<void> {
    // Generate online booking page
  }

  private async generatePricingPage(businessData: BusinessData): Promise<void> {
    // Generate pricing page
  }

  private async generateAboutPage(businessData: BusinessData): Promise<void> {
    // Generate about page
  }

  private async generateContactPage(businessData: BusinessData): Promise<void> {
    // Generate contact page
  }

  private async generateLocationPage(
    location: LocationData,
    businessData: BusinessData
  ): Promise<void> {
    // Generate location overview page
  }
}
