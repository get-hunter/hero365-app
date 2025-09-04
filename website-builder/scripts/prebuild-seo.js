#!/usr/bin/env node

/**
 * Prebuild SEO Content Generator
 * 
 * This script runs before the Next.js build to:
 * 1. Trigger backend SEO content generation
 * 2. Fetch generated content and create static modules
 * 3. Generate route manifests for static site generation
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const BUSINESS_ID = process.env.BUSINESS_ID || '550e8400-e29b-41d4-a716-446655440010'; // Real business ID
const OUTPUT_DIR = path.join(__dirname, '../lib/generated');

/**
 * CONFIGURATION NOTES:
 * 
 * To use real business data instead of fallback data:
 * 1. Set BUSINESS_ID environment variable to a valid business UUID from your database
 * 2. Ensure the business exists in the 'businesses' table with proper service areas
 * 3. Ensure the business has services configured in the 'business_services' table
 * 
 * Example:
 *   export BUSINESS_ID="your-real-business-uuid-here"
 *   npm run prebuild
 * 
 * The script will automatically fall back to hardcoded data if:
 * - Backend is not running
 * - Business ID doesn't exist
 * - API endpoints return errors
 * - No services or service areas are configured
 */

/**
 * Main prebuild function
 */
async function prebuildSEO() {
  console.log('🚀 Starting prebuild SEO content generation...');
  
  try {
    // Step 1: Ensure backend is running
    await checkBackendHealth();
    
    // Step 2: Trigger backend content generation
    console.log('🔄 Triggering backend content generation...');
    const generatedContent = await triggerBackendGeneration();
    
    // Step 3: Create static modules
    console.log('📝 Creating static modules...');
    await createStaticModules(generatedContent);
    
    // Step 4: Generate route manifests
    console.log('🗺️ Generating route manifests...');
    await generateRouteManifests(generatedContent);
    
    console.log('✅ Prebuild SEO content generation completed successfully');
    console.log(`📊 Generated ${generatedContent.pages?.length || 0} pages`);
    
  } catch (error) {
    console.error('❌ Prebuild SEO generation failed:', error.message);
    process.exit(1);
  }
}

/**
 * Check if backend is healthy
 */
async function checkBackendHealth() {
  try {
    const response = await fetch(`${BACKEND_URL}/health`);
    if (!response.ok) {
      throw new Error(`Backend health check failed: ${response.status}`);
    }
    console.log('✅ Backend is healthy');
  } catch (error) {
    console.error('❌ Backend health check failed:', error.message);
    console.log('💡 Make sure the backend is running on', BACKEND_URL);
    throw error;
  }
}

/**
 * Fetch business services from backend
 */
async function fetchBusinessServices() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/public/contractors/services/${BUSINESS_ID}`);
    if (!response.ok) {
      console.warn(`⚠️ Failed to fetch services from backend: ${response.status}`);
      return getFallbackServices();
    }
    
    const services = await response.json();
    return services.map(service => ({
      slug: generateSlug(service.name),
      name: service.name,
      id: service.id,
      category: service.category,
      description: service.description
    }));
  } catch (error) {
    console.warn(`⚠️ Error fetching services: ${error.message}`);
    return getFallbackServices();
  }
}

/**
 * Fetch service areas from backend
 */
async function fetchServiceAreas() {
  try {
    console.log('🔄 Fetching service areas from backend...');
    const response = await fetch(`${BACKEND_URL}/api/v1/public/service-areas/${BUSINESS_ID}`);
    
    if (!response.ok) {
      console.warn(`⚠️ Failed to fetch service areas from backend: ${response.status}`);
      return getFallbackLocations();
    }
    
    const serviceAreas = await response.json();
    
    if (!Array.isArray(serviceAreas) || serviceAreas.length === 0) {
      console.warn('⚠️ No service areas found in backend, using fallback data');
      return getFallbackLocations();
    }
    
    console.log(`✅ Found ${serviceAreas.length} service areas from backend`);
    
    // Convert service areas to location format expected by the script
    return serviceAreas.map(area => ({
      slug: generateSlug(`${area.city}-${area.postal_code}`),
      name: `${area.city}, ${area.postal_code}`,
      city: area.city,
      state: area.region || 'TX', // Default to TX if no region specified
      postal_code: area.postal_code,
      country_code: area.country_code || 'US'
    }));
    
  } catch (error) {
    console.warn(`⚠️ Error fetching service areas: ${error.message}`);
    return getFallbackLocations();
  }
}

/**
 * Generate URL-friendly slug from service name
 */
function generateSlug(name) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '') // Remove special characters
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single
    .trim();
}

/**
 * Fallback services when backend is unavailable
 */
function getFallbackServices() {
  return [
    { slug: 'ac-installation', name: 'AC Installation', category: 'HVAC' },
    { slug: 'hvac-repair', name: 'HVAC Repair', category: 'HVAC' },
    { slug: 'heating-installation', name: 'Heating Installation', category: 'HVAC' },
    { slug: 'cooling-repair', name: 'Cooling Repair', category: 'HVAC' },
    { slug: 'duct-cleaning', name: 'Duct Cleaning', category: 'HVAC' },
    { slug: 'air-quality', name: 'Indoor Air Quality', category: 'HVAC' }
  ];
}

/**
 * Fallback locations when backend is unavailable
 */
function getFallbackLocations() {
  return [
    { slug: 'austin-tx', name: 'Austin, TX', city: 'Austin', state: 'TX' },
    { slug: 'round-rock-tx', name: 'Round Rock, TX', city: 'Round Rock', state: 'TX' },
    { slug: 'cedar-park-tx', name: 'Cedar Park, TX', city: 'Cedar Park', state: 'TX' },
    { slug: 'pflugerville-tx', name: 'Pflugerville, TX', city: 'Pflugerville', state: 'TX' },
    { slug: 'leander-tx', name: 'Leander, TX', city: 'Leander', state: 'TX' },
    { slug: 'georgetown-tx', name: 'Georgetown, TX', city: 'Georgetown', state: 'TX' }
  ];
}

/**
 * Trigger backend content generation
 */
async function triggerBackendGeneration() {
  try {
    console.log('🔄 Triggering backend LLM content generation...');
    
    // Step 1: Trigger LLM content generation
    const generateResponse = await fetch(`${BACKEND_URL}/api/v1/seo/content/${BUSINESS_ID}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });
    
    if (!generateResponse.ok) {
      console.warn(`⚠️ LLM generation failed: ${generateResponse.status}, falling back to static generation`);
      return await generateStaticFallback();
    }
    
    const generateResult = await generateResponse.json();
    console.log(`✅ Backend generated content for ${generateResult.generated_count} pages`);
    
    // Step 2: Fetch the generated pages and content blocks
    console.log('🔄 Fetching generated SEO pages from backend...');
    const pagesResponse = await fetch(`${BACKEND_URL}/api/v1/seo/pages/${BUSINESS_ID}?include_content=true`);
    
    if (!pagesResponse.ok) {
      console.warn(`⚠️ Failed to fetch generated pages: ${pagesResponse.status}, falling back to static generation`);
      return await generateStaticFallback();
    }
    
    const pagesData = await pagesResponse.json();
    
    // Transform backend data to expected format
    const pages = [];
    const contentBlocks = [];
    
    for (const [url, pageData] of Object.entries(pagesData.pages || {})) {
      pages.push({
        slug: url.split('/').pop() || url,
        path: url,
        title: pageData.title,
        meta_description: pageData.meta_description,
        content: {
          h1_heading: pageData.h1_heading,
          description: pageData.meta_description
        },
        seo: {
          canonical: url,
          og_type: 'website'
        },
        priority_score: pageData.page_type === 'service_location' ? 85 : 75,
        generation_method: pageData.generation_method || 'llm',
        generated_at: pageData.created_at || new Date().toISOString()
      });
    }
    
    // Transform content blocks
    for (const [url, blocks] of Object.entries(pagesData.content_blocks || {})) {
      if (blocks.content_blocks && Array.isArray(blocks.content_blocks)) {
        for (const block of blocks.content_blocks) {
          contentBlocks.push({
            ...block,
            page_url: url,
            service_slug: url.split('/')[2] || null,
            location_slug: url.split('/')[3] || null
          });
        }
      }
    }
    
    console.log(`📊 Processed ${pages.length} pages and ${contentBlocks.length} content blocks from backend`);
    
    return {
      pages,
      content_blocks: contentBlocks,
      business_info: pagesData.business || {},
      generation_metadata: {
        generated_at: new Date().toISOString(),
        business_id: BUSINESS_ID,
        business_name: pagesData.business?.name || 'Professional Services',
        total_pages: pages.length,
        total_content_blocks: contentBlocks.length,
        generation_method: 'backend_llm'
      }
    };
    
  } catch (error) {
    console.error('❌ Backend generation failed:', error.message);
    console.log('🔄 Falling back to static generation...');
    return await generateStaticFallback();
  }
}

/**
 * Fallback static generation when backend is unavailable
 */
async function generateStaticFallback() {
  try {
    // Fetch services from backend
    console.log('🔄 Fetching services from backend...');
    const services = await fetchBusinessServices();
    
    // Fetch locations from backend
    console.log('🔄 Fetching service areas from backend...');
    const locations = await fetchServiceAreas();
    
    console.log(`📍 Found ${services.length} services and ${locations.length} locations`);
    
    // Generate static content for all service-location combinations
    const pages = [];
    const contentBlocks = [];
    
    console.log(`🔄 Generating static content for ${services.length * (locations.length + 1)} pages...`);
    
    // Generate main service pages (without location) - these are pillar pages
    for (const service of services) {
      const page = generateStaticServicePage(service, null);
      const blocks = generateStaticContentBlocks(service, null, services, locations);
      pages.push(page);
      contentBlocks.push(...blocks);
    }
    
    // Generate service-location pages
    for (const service of services) {
      for (const location of locations) {
        const page = generateStaticServicePage(service, location);
        const blocks = generateStaticContentBlocks(service, location, services, locations);
        pages.push(page);
        contentBlocks.push(...blocks);
      }
    }
    
    return {
      pages,
      content_blocks: contentBlocks,
      business_info: { services, locations },
      generation_metadata: {
        generated_at: new Date().toISOString(),
        business_id: BUSINESS_ID,
        business_name: 'Professional Services',
        total_pages: pages.length,
        total_content_blocks: contentBlocks.length,
        generation_method: 'static_fallback'
      }
    };
    
  } catch (error) {
    console.error('❌ Static fallback generation failed:', error.message);
    throw error;
  }
}

/**
 * Generate static page data for a service-location combination
 */
function generateStaticServicePage(service, location = null) {
  const pageUrl = location 
    ? `/services/${service.slug}/${location.slug}`
    : `/services/${service.slug}`;
  
  const locationName = location ? location.name : '';
  const title = location 
    ? `${service.name} in ${locationName} | Elite HVAC`
    : `${service.name} Services | Elite HVAC`;
  
  const metaDescription = location
    ? `Professional ${service.name} services in ${locationName}. Licensed technicians, same-day service available. Call for free estimate.`
    : `Expert ${service.name} services. Licensed and insured professionals with 15+ years experience. Same-day service available.`;
  
  return {
    slug: location ? `${service.slug}-${location.slug}` : service.slug,
    path: pageUrl,
    title: title,
    meta_description: metaDescription,
    content: {
      h1_heading: location ? `Expert ${service.name} in ${locationName}` : `Professional ${service.name} Services`,
      description: metaDescription
    },
    seo: {
      canonical: pageUrl,
      og_type: 'website'
    },
    priority_score: location ? 85 : 75,
    generation_method: 'static',
    generated_at: new Date().toISOString()
  };
}

/**
 * Generate static content blocks for a service-location combination
 */
function generateStaticContentBlocks(service, location = null, allServices = [], allLocations = []) {
  const pageUrl = location 
    ? `/services/${service.slug}/${location.slug}`
    : `/services/${service.slug}`;
  
  const locationName = location ? location.name : '';
  const isOverviewPage = !location;
  
  const blocks = [
    {
      type: 'hero',
      order: 1,
      content: {
        h1: location ? `Expert ${service.name} in ${locationName}` : `Professional ${service.name} Services`,
        subheading: location 
          ? `Trusted ${service.name} specialists serving ${locationName} and surrounding areas`
          : `Licensed and insured ${service.name} specialists with 15+ years experience`,
        description: location
          ? `Get reliable ${service.name} services in ${locationName}. Our certified technicians provide same-day service with upfront pricing and 100% satisfaction guarantee.`
          : `Professional ${service.name} services with licensed technicians, transparent pricing, and exceptional customer service. Serving multiple locations across Texas.`,
        primary_cta: {
          text: 'Get Free Estimate',
          href: '/booking'
        },
        secondary_cta: {
          text: 'Call (512) 555-0100',
          href: 'tel:5125550100'
        },
        trust_badges: ['Licensed & Insured', '15+ Years Experience', 'Same-Day Service'],
        quick_facts: [
          'Free estimates',
          'Upfront pricing',
          '100% satisfaction guarantee'
        ]
      },
      visible: true,
      page_url: pageUrl,
      service_slug: service.slug,
      location_slug: location?.slug
    },
    {
      type: 'benefits',
      order: 2,
      content: {
        title: `Why Choose Elite HVAC for ${service.name}?`,
        benefits: [
          {
            title: 'Licensed & Insured',
            description: 'Fully licensed and insured professionals you can trust',
            icon: 'shield-check'
          },
          {
            title: 'Same-Day Service',
            description: 'Fast response times and same-day service available',
            icon: 'clock'
          },
          {
            title: 'Upfront Pricing',
            description: 'Transparent, upfront pricing with no hidden fees',
            icon: 'dollar-sign'
          },
          {
            title: '100% Satisfaction',
            description: 'We guarantee your complete satisfaction with our work',
            icon: 'star'
          }
        ]
      },
      visible: true,
      page_url: pageUrl,
      service_slug: service.slug,
      location_slug: location?.slug
    },
    {
      type: 'process_steps',
      order: 3,
      content: {
        title: `Our ${service.name} Process`,
        description: 'We follow a proven process to ensure quality results every time',
        steps: [
          {
            step: 1,
            title: 'Initial Assessment',
            description: 'We thoroughly assess your needs and provide upfront pricing'
          },
          {
            step: 2,
            title: 'Professional Service',
            description: 'Our certified technicians perform the work to the highest standards'
          },
          {
            step: 3,
            title: 'Quality Assurance',
            description: 'We test everything and ensure your complete satisfaction'
          },
          {
            step: 4,
            title: 'Follow-Up',
            description: 'We follow up to ensure everything is working perfectly'
          }
        ]
      },
      visible: true,
      page_url: pageUrl,
      service_slug: service.slug,
      location_slug: location?.slug
    },
    {
      type: 'faq',
      order: 4,
      content: {
        title: `Frequently Asked Questions About ${service.name}`,
        faqs: [
          {
            question: `How much does ${service.name} cost?`,
            answer: 'We provide upfront, transparent pricing with no hidden fees. Contact us for a free estimate tailored to your specific needs.'
          },
          {
            question: 'Do you offer emergency service?',
            answer: 'Yes, we offer 24/7 emergency service for urgent situations. Our emergency technicians can respond quickly to minimize downtime.'
          },
          {
            question: 'Are you licensed and insured?',
            answer: 'Yes, we are fully licensed and insured. All our technicians are certified professionals with extensive training and experience.'
          },
          {
            question: 'Do you guarantee your work?',
            answer: 'Absolutely! We stand behind our work with a 100% satisfaction guarantee. If you\'re not completely satisfied, we\'ll make it right.'
          }
        ]
      },
      visible: true,
      page_url: pageUrl,
      service_slug: service.slug,
      location_slug: location?.slug
    }
  ];

  // Add service areas block for overview pages (pillar pages)
  if (isOverviewPage && allLocations.length > 0) {
    blocks.push({
      type: 'service_areas',
      order: 5,
      content: {
        title: `${service.name} Service Areas`,
        description: `We provide professional ${service.name} services across multiple locations in Texas. Click on your area to see local pricing and availability.`,
        locations: allLocations.slice(0, 12).map(loc => ({
          name: loc.name,
          slug: loc.slug,
          url: `/services/${service.slug}/${loc.slug}`,
          city: loc.city,
          state: loc.state,
          postal_code: loc.postal_code
        })),
        cta: {
          text: 'View All Service Areas',
          href: `/services/${service.slug}/areas`
        }
      },
      visible: true,
      page_url: pageUrl,
      service_slug: service.slug,
      location_slug: null
    });

    // Add related services block for overview pages
    const relatedServices = allServices.filter(s => s.slug !== service.slug).slice(0, 6);
    if (relatedServices.length > 0) {
      blocks.push({
        type: 'related_services',
        order: 6,
        content: {
          title: 'Other HVAC Services We Offer',
          description: 'Complete HVAC solutions for your home or business',
          services: relatedServices.map(s => ({
            name: s.name,
            slug: s.slug,
            url: `/services/${s.slug}`,
            category: s.category,
            description: s.description || `Professional ${s.name} services with licensed technicians`
          }))
        },
        visible: true,
        page_url: pageUrl,
        service_slug: service.slug,
        location_slug: null
      });
    }

    // Add comprehensive content block for overview pages
    blocks.push({
      type: 'comprehensive_content',
      order: 7,
      content: {
        title: `Complete ${service.name} Solutions`,
        sections: [
          {
            title: 'What We Do',
            content: `Our ${service.name} services include comprehensive solutions for residential and commercial properties. We handle everything from initial consultation to final installation and ongoing maintenance.`
          },
          {
            title: 'Our Expertise',
            content: `With over 15 years of experience in the HVAC industry, our certified technicians have the knowledge and skills to handle any ${service.name} project, big or small.`
          },
          {
            title: 'Quality Guarantee',
            content: `We stand behind our work with a comprehensive warranty and 100% satisfaction guarantee. Your comfort and peace of mind are our top priorities.`
          }
        ]
      },
      visible: true,
      page_url: pageUrl,
      service_slug: service.slug,
      location_slug: null
    });
  }

  // Add JSON-LD schema block for all pages
  blocks.push({
    type: 'json_ld_schema',
    order: 10,
    content: {
      schemas: [
        // Service schema
        {
          '@context': 'https://schema.org',
          '@type': 'Service',
          name: location ? `${service.name} in ${locationName}` : service.name,
          description: location 
            ? `Professional ${service.name} services in ${locationName}. Licensed technicians, same-day service available.`
            : `Expert ${service.name} services. Licensed and insured professionals with 15+ years experience.`,
          provider: {
            '@type': 'LocalBusiness',
            name: 'Elite HVAC',
            telephone: '(512) 555-0100',
            url: 'https://elitehvac.com',
            address: location ? {
              '@type': 'PostalAddress',
              addressLocality: location.city,
              addressRegion: location.state,
              postalCode: location.postal_code,
              addressCountry: 'US'
            } : undefined
          },
          areaServed: location ? {
            '@type': 'City',
            name: location.city,
            containedInPlace: {
              '@type': 'State',
              name: location.state
            }
          } : allLocations.slice(0, 10).map(loc => ({
            '@type': 'City',
            name: loc.city,
            containedInPlace: {
              '@type': 'State', 
              name: loc.state
            }
          }))
        },
        // FAQ schema
        {
          '@context': 'https://schema.org',
          '@type': 'FAQPage',
          mainEntity: [
            {
              '@type': 'Question',
              name: `How much does ${service.name} cost?`,
              acceptedAnswer: {
                '@type': 'Answer',
                text: 'We provide upfront, transparent pricing with no hidden fees. Contact us for a free estimate tailored to your specific needs.'
              }
            },
            {
              '@type': 'Question', 
              name: 'Do you offer emergency service?',
              acceptedAnswer: {
                '@type': 'Answer',
                text: 'Yes, we offer 24/7 emergency service for urgent situations. Our emergency technicians can respond quickly to minimize downtime.'
              }
            },
            {
              '@type': 'Question',
              name: 'Are you licensed and insured?', 
              acceptedAnswer: {
                '@type': 'Answer',
                text: 'Yes, we are fully licensed and insured. All our technicians are certified professionals with extensive training and experience.'
              }
            }
          ]
        },
        // Breadcrumb schema
        {
          '@context': 'https://schema.org',
          '@type': 'BreadcrumbList',
          itemListElement: location ? [
            {
              '@type': 'ListItem',
              position: 1,
              name: 'Home',
              item: 'https://elitehvac.com'
            },
            {
              '@type': 'ListItem',
              position: 2,
              name: 'Services',
              item: 'https://elitehvac.com/services'
            },
            {
              '@type': 'ListItem',
              position: 3,
              name: service.name,
              item: `https://elitehvac.com/services/${service.slug}`
            },
            {
              '@type': 'ListItem',
              position: 4,
              name: locationName,
              item: `https://elitehvac.com/services/${service.slug}/${location.slug}`
            }
          ] : [
            {
              '@type': 'ListItem',
              position: 1,
              name: 'Home',
              item: 'https://elitehvac.com'
            },
            {
              '@type': 'ListItem',
              position: 2,
              name: 'Services',
              item: 'https://elitehvac.com/services'
            },
            {
              '@type': 'ListItem',
              position: 3,
              name: service.name,
              item: `https://elitehvac.com/services/${service.slug}`
            }
          ]
        }
      ]
    },
    visible: false, // Schema blocks are not visually rendered
    page_url: pageUrl,
    service_slug: service.slug,
    location_slug: location?.slug
  });
  
  return blocks;
}

/**
 * Create static modules for Next.js consumption
 */
async function createStaticModules(generatedContent) {
  await ensureDirectoryExists(OUTPUT_DIR);
  
  // Create SEO pages module
  const seoPages = {};
  const contentBlocksMap = {};
  
  for (const page of generatedContent.pages) {
    seoPages[page.path] = {
      title: page.title,
      meta_description: page.meta_description,
      target_keywords: extractKeywords(page),
      page_url: page.path,
      content: page.content,
      created_at: page.generated_at
    };
  }
  
  // Group content blocks by page path
  for (const block of generatedContent.content_blocks) {
    const pagePath = block.page_url ? block.page_url : (block.service_slug ? `/services/${block.service_slug}` : '/');
    if (!contentBlocksMap[pagePath]) {
      contentBlocksMap[pagePath] = [];
    }
    contentBlocksMap[pagePath].push(block);
  }
  
  // Write SEO pages module
  const seoModule = `// Auto-generated SEO pages data
// Generated at: ${new Date().toISOString()}
// Do not edit this file manually

export const seoPages = ${JSON.stringify(seoPages, null, 2)};

export const contentBlocks = ${JSON.stringify(contentBlocksMap, null, 2)};

export function getSEOPageData(urlPath: string) {
  return seoPages[urlPath] || null;
}

export function getAllSEOPages() {
  return seoPages;
}

export function getAllContentBlocks() {
  return contentBlocks;
}

export function getContentBlocks(urlPath: string) {
  return contentBlocks[urlPath] || [];
}

export function getBusinessNavigation() {
  // Extract navigation from business info
  const services = ${JSON.stringify(generatedContent.business_info?.services || [])};
  const locations = ${JSON.stringify(generatedContent.business_info?.locations || [])};
  
  return {
    services: services.map(s => ({ name: s.name, slug: s.slug, href: \`/services/\${s.slug}\` })),
    locations: locations.map(l => ({ name: l.name, slug: l.slug, href: \`/locations/\${l.slug}\` }))
  };
}

export function getBusinessLocations() {
  return ${JSON.stringify(generatedContent.business_info?.locations || [])};
}
`;
  
  await fs.writeFile(path.join(OUTPUT_DIR, 'seo-pages.ts'), seoModule);
  console.log('📝 Created SEO pages module');
}

/**
 * Generate route manifests for static generation
 */
async function generateRouteManifests(generatedContent) {
  // Generate static params for Next.js
  const staticParams = generatedContent.pages
    .filter(page => page.path.startsWith('/') && page.path !== '/')
    .map(page => ({
      slug: page.path.split('/').filter(Boolean)
    }));
  
  const routeManifest = {
    generated_at: new Date().toISOString(),
    business_id: BUSINESS_ID,
    total_routes: staticParams.length,
    routes: generatedContent.pages.map(page => ({
      path: page.path,
      slug: page.slug,
      priority: page.priority_score || 50,
      lastModified: page.generated_at,
      changeFreq: page.priority_score > 80 ? 'weekly' : 'monthly'
    })),
    staticParams
  };
  
  await fs.writeFile(
    path.join(OUTPUT_DIR, 'route-manifest.json'), 
    JSON.stringify(routeManifest, null, 2)
  );
  
  // Generate sitemap data
  const sitemapData = {
    generated_at: new Date().toISOString(),
    business_id: BUSINESS_ID,
    urls: generatedContent.pages.map(page => ({
      loc: page.path,
      lastmod: page.generated_at,
      changefreq: page.priority_score > 80 ? 'weekly' : 'monthly',
      priority: Math.min((page.priority_score || 50) / 100, 1.0)
    }))
  };
  
  await fs.writeFile(
    path.join(OUTPUT_DIR, 'sitemap-data.json'), 
    JSON.stringify(sitemapData, null, 2)
  );
  
  console.log('🗺️ Generated route manifests');
}

/**
 * Extract keywords from page data
 */
function extractKeywords(page) {
  const keywords = [];
  
  // Extract from title
  const titleWords = page.title.toLowerCase().split(/\s+/).filter(word => word.length > 3);
  keywords.push(...titleWords.slice(0, 3));
  
  // Extract from meta description
  if (page.meta_description) {
    const descWords = page.meta_description.toLowerCase().split(/\s+/).filter(word => word.length > 3);
    keywords.push(...descWords.slice(0, 2));
  }
  
  return [...new Set(keywords)];
}

/**
 * Ensure directory exists
 */
async function ensureDirectoryExists(dirPath) {
  try {
    await fs.access(dirPath);
  } catch {
    await fs.mkdir(dirPath, { recursive: true });
    console.log(`📁 Created directory: ${dirPath}`);
  }
}

// Run if called directly
if (require.main === module) {
  prebuildSEO();
}

module.exports = { prebuildSEO };
