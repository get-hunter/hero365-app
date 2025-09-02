#!/usr/bin/env node

/**
 *  Deployment Script with Business ID Configuration
 * 
 * This script allows deploying websites with specific business IDs,
 * automatically configuring the frontend to use the correct business data.
 * 
 * Usage:
 *   node scripts/deploy-with-business.js --businessId=<uuid> --env=<environment> [options]
 * 
 * Examples:
 *   # Deploy for specific business to development
 *   node scripts/deploy-with-business.js --businessId=abc123 --env=development
 * 
 *   # Deploy to staging with custom project name
 *   node scripts/deploy-with-business.js --businessId=abc123 --env=staging --project=elite-hvac
 * 
 *   # Deploy to production with custom domain
 *   node scripts/deploy-with-business.js --businessId=abc123 --env=production --domain=elitehvac.com
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const minimist = require('minimist');

// Parse command line arguments
const args = minimist(process.argv.slice(2), {
  string: ['businessId', 'env', 'project', 'domain', 'businessName', 'businessPhone', 'businessEmail'],
  boolean: ['build-only', 'verbose', 'preview', 'help'],
  default: {
    env: 'development',
    'build-only': false,
    verbose: false,
    preview: false
  },
  alias: {
    b: 'businessId',
    e: 'env',
    p: 'project',
    d: 'domain',
    h: 'help',
    v: 'verbose'
  }
});

// Show help
if (args.help) {
  console.log(`
Enhanced Website Deployment with Business Configuration

Usage: node scripts/deploy-with-business.js [options]

Required:
  --businessId, -b    Business UUID to configure the website for
  
Options:
  --env, -e          Target environment (development|staging|production) [default: development]
  --project, -p      Custom Cloudflare project name
  --domain, -d       Custom domain for the website
  --businessName     Override business name (optional)
  --businessPhone    Override business phone (optional)
  --businessEmail    Override business email (optional)
  --build-only       Only build, don't deploy
  --preview          Deploy as preview (staging only)
  --verbose, -v      Verbose output
  --help, -h         Show this help

Examples:
  # Local development build
  node scripts/deploy-with-business.js -b abc123 -e development --build-only
  
  # Deploy to staging
  node scripts/deploy-with-business.js -b abc123 -e staging -p elite-hvac-staging
  
  # Production deployment with custom domain
  node scripts/deploy-with-business.js -b abc123 -e production -d elitehvac.com
`);
  process.exit(0);
}

// Validate required arguments
if (!args.businessId) {
  console.error('❌ Error: --businessId is required');
  console.error('Use --help for usage information');
  process.exit(1);
}

// Validate business ID format (basic UUID check)
const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
if (!uuidRegex.test(args.businessId)) {
  console.error('❌ Error: businessId must be a valid UUID format');
  console.error('Example: 123e4567-e89b-12d3-a456-426614174000');
  process.exit(1);
}

// Configuration
const CONFIG = {
  businessId: args.businessId,
  environment: args.env,
  projectName: args.project,
  customDomain: args.domain,
  buildOnly: args['build-only'],
  verbose: args.verbose,
  preview: args.preview,
  businessOverrides: {
    name: args.businessName,
    phone: args.businessPhone,
    email: args.businessEmail
  }
};

// Paths
const PATHS = {
  root: path.resolve(__dirname, '..'),
  config: path.resolve(__dirname, '../config'),
  deploymentConfig: path.resolve(__dirname, '../config/deployment.json'),
  businessConfig: path.resolve(__dirname, '../config/business-config.json'),
  envLocal: path.resolve(__dirname, '../.env.local'),
  buildOutput: path.resolve(__dirname, '../out')
};

/**
 * Logging utilities
 */
function log(message, type = 'info') {
  const timestamp = new Date().toISOString().slice(11, 19);
  const colors = {
    info: '\x1b[36m',    // Cyan
    success: '\x1b[32m', // Green
    warning: '\x1b[33m', // Yellow
    error: '\x1b[31m',   // Red
    reset: '\x1b[0m'
  };
  
  const color = colors[type] || colors.info;
  console.log(`${color}[${timestamp}] ${message}${colors.reset}`);
}

function verbose(message) {
  if (CONFIG.verbose) {
    log(message, 'info');
  }
}

/**
 * Load deployment configuration
 */
function loadDeploymentConfig() {
  try {
    const configData = fs.readFileSync(PATHS.deploymentConfig, 'utf8');
    return JSON.parse(configData);
  } catch (error) {
    log(`Failed to load deployment config: ${error.message}`, 'error');
    process.exit(1);
  }
}

/**
 * Fetch business data from API (optional)
 */
async function fetchBusinessData(businessId, apiBaseUrl) {
  try {
    verbose(`Fetching business data from API: ${apiBaseUrl}`);
    
    const fetch = (await import('node-fetch')).default;
    const response = await fetch(`${apiBaseUrl}/api/v1/public/contractors/profile/${businessId}`);
    
    if (response.ok) {
      const businessData = await response.json();
      log(`✅ Fetched business data: ${businessData.business_name}`, 'success');
      return businessData;
    } else {
      log(`⚠️ Business data not found (${response.status}), using defaults`, 'warning');
      return null;
    }
  } catch (error) {
    log(`⚠️ Failed to fetch business data: ${error.message}`, 'warning');
    return null;
  }
}

/**
 * Fetch SEO pages for the business using the new SEO API
 */
async function fetchSEOPages(businessId, apiUrl) {
  if (!businessId || !apiUrl) {
    log('⚠️ No business ID or API URL provided for SEO pages fetch', 'warn');
    return null;
  }

  try {
    log(`🔍 Fetching SEO pages for business ${businessId}...`, 'info');
    
    // First, trigger the SEO deployment pipeline
    const deployUrl = `${apiUrl}/api/v1/seo/deploy/${businessId}`;
    const deployResponse = await fetch(deployUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Hero365-Website-Builder/1.0'
      },
      timeout: 60000 // 60 second timeout for deployment
    });

    if (deployResponse.ok) {
      const deployResult = await deployResponse.json();
      log(`✅ SEO deployment completed: ${deployResult.total_pages} pages generated`, 'info');
      return deployResult;
    } else {
      log(`⚠️ SEO deployment failed: ${deployResponse.status}, trying direct fetch...`, 'warn');
    }
    
    // Fallback: try to get existing SEO pages
    const pagesUrl = `${apiUrl}/api/v1/seo/pages/${businessId}`;
    const pagesResponse = await fetch(pagesUrl, {
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Hero365-Website-Builder/1.0'
      },
      timeout: 30000 // 30 second timeout
    });

    if (pagesResponse.ok) {
      const seoPages = await pagesResponse.json();
      log(`✅ Fetched SEO pages: ${seoPages.total_pages || 0} pages`, 'info');
      return seoPages;
    } else {
      log(`⚠️ Failed to fetch SEO pages: ${pagesResponse.status} ${pagesResponse.statusText}`, 'warn');
      return null;
    }
  } catch (error) {
    log(`⚠️ Error fetching SEO pages: ${error.message}`, 'warn');
    return null;
  }
}

/**
 * Generate SEO content using the build-time generator
 */
async function generateSEOContent(businessId, seoData) {
  try {
    log('🔍 Generating SEO content for website builder...', 'info');
    
    if (seoData && seoData.pages) {
      // Generate SEO pages from backend data
      await generateSEOPagesFromContent(seoData);
      log('✅ SEO content generation completed from backend data', 'info');
      return true;
    } else {
      log('📝 No LLM content available, using fallback SEO generation', 'info');
      
      // Create fallback content for demo
      log('📝 Creating fallback SEO content...', 'info');
      
      const fallbackContent = {
        pages: [
          {
            slug: 'home',
            path: '/',
            title: `${businessId} - Professional Services`,
            meta_description: 'Professional services for your home and business needs.',
            content: { hero: { headline: 'Professional Services You Can Trust' } },
            seo: { canonical: '/', og_type: 'website' }
          },
          {
            slug: 'about',
            path: '/about',
            title: `About ${businessId}`,
            meta_description: 'Learn about our professional services.',
            content: { hero: { headline: 'About Us' } },
            seo: { canonical: '/about', og_type: 'article' }
          },
          {
            slug: 'services',
            path: '/services',
            title: `Services - ${businessId}`,
            meta_description: 'Complete professional services.',
            content: { hero: { headline: 'Our Services' } },
            seo: { canonical: '/services', og_type: 'article' }
          },
          {
            slug: 'contact',
            path: '/contact',
            title: `Contact ${businessId}`,
            meta_description: 'Contact us for professional services.',
            content: { hero: { headline: 'Contact Us' } },
            seo: { canonical: '/contact', og_type: 'article' }
          }
        ],
        content_items: [],
        seo_configs: {},
        quality_score: 75,
        generation_metadata: {
          generated_at: new Date().toISOString(),
          business_id: businessId,
          business_name: 'Professional Services',
          total_pages: 4,
          total_content_items: 0
        }
      };
      
      // Write fallback content and generate SEO files
      const tempContentFile = path.join(__dirname, '..', 'temp-fallback-content.json');
      fs.writeFileSync(tempContentFile, JSON.stringify(fallbackContent, null, 2));
      
      // Generate SEO pages using Node.js instead of tsx
      await generateSEOPagesFromContent(fallbackContent);
      
      // Clean up
      fs.unlinkSync(tempContentFile);
      
      log('✅ Fallback SEO content generation completed', 'info');
      return true;
    }
  } catch (error) {
    log(`❌ SEO content generation failed: ${error.message}`, 'error');
    return false;
  }
}

/**
 * Generate SEO pages from content using pure JavaScript
 */
async function generateSEOPagesFromContent(content) {
  try {
    log('🔍 Generating SEO pages from content...', 'info');
    
    // Create output directory
    const outputDir = path.join(__dirname, '..', 'lib', 'generated');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    let seoPages = {};
    let sitemapUrls = [];
    
    // Handle new backend SEO data format
    if (content.pages && typeof content.pages === 'object' && !Array.isArray(content.pages)) {
      // Backend format: { pages: { "/url": { title, content, ... } } }
      seoPages = content.pages;
      sitemapUrls = Object.keys(content.pages).map(url => ({
        loc: url,
        lastmod: new Date().toISOString(),
        changefreq: url === '/' ? 'weekly' : 'monthly',
        priority: url === '/' ? 1.0 : (url.startsWith('/services/') ? 0.8 : 0.6)
      }));
    } else if (content.pages && Array.isArray(content.pages)) {
      // Legacy format: { pages: [{ path, title, ... }] }
      for (const page of content.pages) {
        const contentText = extractTextFromContent(page.content);
        seoPages[page.path] = {
          title: page.title,
          meta_description: page.meta_description,
          content: contentText,
          keywords: [page.slug, 'professional', 'services'],
          canonical_url: page.seo?.canonical || page.path,
          og_type: page.seo?.og_type || 'article',
          word_count: contentText.split(' ').length,
          created_at: new Date().toISOString()
        };
      }
      sitemapUrls = content.pages.map(page => ({
        loc: page.path,
        lastmod: new Date().toISOString(),
        changefreq: 'monthly',
        priority: page.path === '/' ? 1.0 : 0.8
      }));
    }
    
    // Generate SEO pages module
    const moduleContent = `// Auto-generated SEO pages data
// Generated at: ${new Date().toISOString()}
// Do not edit this file manually

export const seoPages = ${JSON.stringify(seoPages, null, 2)};

export const navigation = ${JSON.stringify(content.navigation || {}, null, 2)};

export const navigationCategories = ${JSON.stringify(content.navigation?.categories || [], null, 2)};

export function getSEOPageData(urlPath) {
  return seoPages[urlPath] || null;
}

export function getAllSEOPages() {
  return seoPages;
}

export function getSEOPagePaths() {
  return Object.keys(seoPages);
}

export function getNavigation() {
  return navigation;
}

export function getNavigationCategories() {
  return navigationCategories;
}
`;
    
    // Write SEO pages module
    const seoFilePath = path.join(outputDir, 'seo-pages.js');
    fs.writeFileSync(seoFilePath, moduleContent, 'utf-8');
    
    // Generate sitemap data
    const sitemapData = {
      generated_at: new Date().toISOString(),
      business_id: content.business_id || content.generation_metadata?.business_id,
      total_pages: content.total_pages || Object.keys(seoPages).length,
      urls: sitemapUrls
    };
    
    const sitemapFilePath = path.join(outputDir, 'sitemap-data.json');
    fs.writeFileSync(sitemapFilePath, JSON.stringify(sitemapData, null, 2), 'utf-8');
    
    log(`✅ Generated SEO pages: ${Object.keys(seoPages).length} pages`, 'info');
    log(`✅ Generated sitemap: ${sitemapUrls.length} URLs`, 'info');
    return true;
  } catch (error) {
    log(`❌ SEO pages generation failed: ${error.message}`, 'error');
    return false;
  }
}

/**
 * Extract text content from page content object
 */
function extractTextFromContent(content) {
  let text = '';
  
  function extractFromObject(obj) {
    if (typeof obj === 'string') {
      text += obj + ' ';
    } else if (typeof obj === 'object' && obj !== null) {
      if (Array.isArray(obj)) {
        obj.forEach(extractFromObject);
      } else {
        Object.values(obj).forEach(extractFromObject);
      }
    }
  }
  
  extractFromObject(content);
  return text.trim();
}

/**
 * Generate sitemap and robots.txt files
 */
async function generateSitemapFiles(businessConfig) {
  try {
    log('🗺️ Generating sitemap and robots.txt files...', 'info');
    
    // Load sitemap data from generated content
    const generatedDir = path.join(__dirname, '..', 'lib', 'generated');
    const sitemapDataPath = path.join(generatedDir, 'sitemap-data.json');
    
    let sitemapData = null;
    try {
      const content = fs.readFileSync(sitemapDataPath, 'utf-8');
      sitemapData = JSON.parse(content);
    } catch (error) {
      log('⚠️ No sitemap data available, creating basic sitemap', 'warn');
    }
    
    if (!sitemapData) {
      // Create basic sitemap data
      sitemapData = {
        generated_at: new Date().toISOString(),
        business_id: CONFIG.businessId,
        urls: [
          { loc: '/', lastmod: new Date().toISOString(), changefreq: 'weekly', priority: 1.0 },
          { loc: '/about', lastmod: new Date().toISOString(), changefreq: 'monthly', priority: 0.8 },
          { loc: '/services', lastmod: new Date().toISOString(), changefreq: 'weekly', priority: 0.9 },
          { loc: '/contact', lastmod: new Date().toISOString(), changefreq: 'monthly', priority: 0.7 },
          { loc: '/pricing', lastmod: new Date().toISOString(), changefreq: 'monthly', priority: 0.6 }
        ]
      };
    }
    
    // Generate sitemap.xml and robots.txt
    const publicDir = path.join(__dirname, '..', 'public');
    const baseUrl = businessConfig.websiteConfig?.baseUrl || 'http://localhost:3001';
    const businessName = businessConfig.businessData?.business_name || 'Professional Services';
    
    const success = await writeSitemapFiles(sitemapData, baseUrl, businessName, publicDir);
    
    if (success) {
      log(`✅ Generated sitemap with ${sitemapData.urls.length} URLs`, 'info');
    }
    
    return success;
  } catch (error) {
    log(`❌ Sitemap generation failed: ${error.message}`, 'error');
    return false;
  }
}

/**
 * Write sitemap and robots files to public directory
 */
async function writeSitemapFiles(sitemapData, baseUrl, businessName, publicDir) {
  try {
    // Generate sitemap.xml content
    const urls = sitemapData.urls.map(url => `
  <url>
    <loc>${baseUrl}${url.loc}</loc>
    <lastmod>${url.lastmod}</lastmod>
    <changefreq>${url.changefreq}</changefreq>
    <priority>${url.priority.toFixed(1)}</priority>
  </url>`).join('');

    const sitemapXML = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Generated at: ${sitemapData.generated_at} -->
  <!-- Business ID: ${sitemapData.business_id} -->${urls}
</urlset>`;

    // Generate robots.txt content
    const robotsTxt = `# Robots.txt for ${businessName}
# Generated at: ${new Date().toISOString()}

User-agent: *
Allow: /

# Sitemap
Sitemap: ${baseUrl}/sitemap.xml

# Crawl-delay for respectful crawling
Crawl-delay: 1

# Disallow admin and private areas
Disallow: /admin/
Disallow: /api/
Disallow: /_next/
Disallow: /temp-*

# Allow important pages
Allow: /
Allow: /about
Allow: /services
Allow: /contact
Allow: /pricing
Allow: /projects
`;

    // Ensure public directory exists
    if (!fs.existsSync(publicDir)) {
      fs.mkdirSync(publicDir, { recursive: true });
    }

    // Write files
    fs.writeFileSync(path.join(publicDir, 'sitemap.xml'), sitemapXML, 'utf-8');
    fs.writeFileSync(path.join(publicDir, 'robots.txt'), robotsTxt, 'utf-8');

    log('✅ Generated sitemap.xml and robots.txt', 'info');
    return true;
  } catch (error) {
    log(`❌ Failed to write sitemap files: ${error.message}`, 'error');
    return false;
  }
}

/**
 * Generate business-specific configuration
 */
async function generateBusinessConfig(deploymentConfig) {
  const envConfig = deploymentConfig.environments[CONFIG.environment];
  
  // Try to fetch real business data using ngrok-aware API URL
  let businessData = null;
  const apiUrl = getApiUrlForEnvironment(CONFIG.environment);
  if (apiUrl) {
    businessData = await fetchBusinessData(CONFIG.businessId, apiUrl);
  }
  
  // Create business configuration with override support
  const defaultBusinessData = {
    business_name: CONFIG.businessOverrides.name || envConfig.business?.defaultBusinessName || 'Professional Services',
    phone: CONFIG.businessOverrides.phone || envConfig.business?.defaultBusinessPhone || '+1-555-123-4567',
    email: CONFIG.businessOverrides.email || envConfig.business?.defaultBusinessEmail || 'contact@example.com',
    trade_type: 'HVAC',
    description: 'Professional service provider committed to excellence.',
    service_areas: ['Local Area'],
    emergency_service: true,
    years_in_business: 10,
    license_number: 'Licensed & Insured',
    insurance_verified: true,
    average_rating: 4.8,
    total_reviews: 150
  };

  // Merge fetched data with overrides and defaults
  const finalBusinessData = businessData ? {
    ...businessData,
    // Override empty fields with provided values
    business_name: businessData.business_name || CONFIG.businessOverrides.name || defaultBusinessData.business_name,
    phone: businessData.phone || CONFIG.businessOverrides.phone || defaultBusinessData.phone,
    email: businessData.email || CONFIG.businessOverrides.email || defaultBusinessData.email
  } : defaultBusinessData;

  const businessConfig = {
    businessId: CONFIG.businessId,
    environment: CONFIG.environment,
    businessData: finalBusinessData,
    apiConfig: envConfig.api,
    websiteConfig: envConfig.website,
    features: envConfig.features,
    generatedAt: new Date().toISOString()
  };
  
  // Save business config for frontend
  fs.writeFileSync(PATHS.businessConfig, JSON.stringify(businessConfig, null, 2));
  log(`✅ Generated business configuration for: ${businessConfig.businessData.business_name}`, 'success');
  
  return businessConfig;
}

/**
 * Generate environment configuration
 */
function generateEnvironmentConfig(deploymentConfig, businessConfig) {
  const envConfig = deploymentConfig.environments[CONFIG.environment];
  
  // Get the correct API URL (with ngrok support for staging/production)
  const apiUrl = getApiUrlForEnvironment(CONFIG.environment);
  
  const envVars = {
    // Environment (critical for SSR consistency)
    NODE_ENV: CONFIG.environment === 'development' ? 'development' : 'production',
    NEXT_PUBLIC_ENVIRONMENT: CONFIG.environment,
    
    // API Configuration
    NEXT_PUBLIC_API_URL: apiUrl,
    NEXT_PUBLIC_API_TIMEOUT: envConfig.api.timeout.toString(),
    
    // Business Configuration
    NEXT_PUBLIC_BUSINESS_ID: CONFIG.businessId,
    NEXT_PUBLIC_BUSINESS_NAME: businessConfig.businessData.business_name,
    NEXT_PUBLIC_BUSINESS_PHONE: businessConfig.businessData.phone,
    NEXT_PUBLIC_BUSINESS_EMAIL: businessConfig.businessData.email,
    
    // Feature Flags
    NEXT_PUBLIC_ANALYTICS_ENABLED: envConfig.features.analytics.toString(),
    NEXT_PUBLIC_ERROR_REPORTING_ENABLED: envConfig.features.errorReporting.toString(),
    NEXT_PUBLIC_DEBUG_MODE: envConfig.features.debugMode.toString(),
    NEXT_PUBLIC_BOOKING_WIDGET_ENABLED: envConfig.features.bookingWidget.toString(),
    
    // Website Configuration
    NEXT_PUBLIC_WEBSITE_BASE_URL: envConfig.website.baseUrl,
    
    // Deployment Configuration
    NEXT_PUBLIC_DEPLOYMENT_ID: `${CONFIG.businessId}-${Date.now()}`,
    NEXT_PUBLIC_DEPLOYED_AT: new Date().toISOString()
  };
  
  // Add custom domain if specified
  if (CONFIG.customDomain) {
    envVars.NEXT_PUBLIC_CUSTOM_DOMAIN = CONFIG.customDomain;
  }
  
  // Generate .env.local file
  const envContent = Object.entries(envVars)
    .map(([key, value]) => `${key}=${value}`)
    .join('\n');
  
  fs.writeFileSync(PATHS.envLocal, envContent);
  log(`✅ Generated environment configuration (.env.local)`, 'success');
  
  verbose('Environment variables:');
  if (CONFIG.verbose) {
    Object.entries(envVars).forEach(([key, value]) => {
      console.log(`  ${key}=${value}`);
    });
  }
  
  return envVars;
}

/**
 * Build the Next.js website
 */
function buildWebsite() {
  log('🔨 Building Next.js website...', 'info');
  
  try {
    // Use the standard Next.js build for OpenNext
    const buildCommand = 'npm run build';
    verbose(`Executing: ${buildCommand}`);
    
    const output = execSync(buildCommand, { 
      cwd: PATHS.root,
      stdio: CONFIG.verbose ? 'inherit' : 'pipe',
      encoding: 'utf8'
    });
    
    if (!CONFIG.verbose && output) {
      verbose(output);
    }
    
    log('✅ Website build completed successfully', 'success');
    return true;
  } catch (error) {
    log(`❌ Build failed: ${error.message}`, 'error');
    return false;
  }
}

/**
 * Update wrangler.toml with business-specific configuration
 */
function updateWranglerConfig(businessConfig) {
  try {
    const wranglerPath = path.resolve(PATHS.root, 'wrangler.toml');
    
    // Read current wrangler.toml
    let wranglerContent = fs.readFileSync(wranglerPath, 'utf8');
    
    // Update business-specific environment variables
    const businessId = businessConfig.businessId;
    const businessName = businessConfig.businessData.business_name;
    
    // Update the staging environment variables
    const envSection = `[env.${CONFIG.environment}.vars]`;
    const newVars = `
NEXT_PUBLIC_BUSINESS_ID = "${businessId}"
NEXT_PUBLIC_BUSINESS_NAME = "${businessName}"
NEXT_PUBLIC_BUSINESS_PHONE = "${businessConfig.businessData.phone || ''}"
NEXT_PUBLIC_BUSINESS_EMAIL = "${businessConfig.businessData.email || ''}"
NEXT_PUBLIC_API_URL = "${getApiUrlForEnvironment(CONFIG.environment)}"
NEXT_PUBLIC_API_VERSION = "v1"
NEXT_PUBLIC_DEBUG_MODE = "${CONFIG.environment === 'production' ? 'false' : 'true'}"
NEXT_PUBLIC_ANALYTICS_ENABLED = "true"
NEXT_PUBLIC_ENVIRONMENT = "${CONFIG.environment}"
`;

    // Replace or add the environment section
    const envSectionRegex = new RegExp(`\\[env\\.${CONFIG.environment}\\.vars\\][\\s\\S]*?(?=\\n\\[|$)`, 'g');
    if (wranglerContent.match(envSectionRegex)) {
      wranglerContent = wranglerContent.replace(envSectionRegex, envSection + newVars);
    } else {
      wranglerContent += '\n' + envSection + newVars;
    }
    
    // Write updated wrangler.toml
    fs.writeFileSync(wranglerPath, wranglerContent);
    log('✅ Updated wrangler.toml with business configuration', 'success');
    
  } catch (error) {
    log(`⚠️ Failed to update wrangler.toml: ${error.message}`, 'warning');
  }
}

/**
 * Get API URL for environment
 */
function getApiUrlForEnvironment(environment) {
  // For staging/production, try to get ngrok URL first
  if (environment === 'staging' || environment === 'production') {
    const ngrokUrl = process.env.NGROK_PUBLIC_URL;
    if (ngrokUrl) {
      log(`🌐 Using ngrok URL for ${environment}: ${ngrokUrl}`, 'info');
      return ngrokUrl;
    }
  }
  
  switch (environment) {
    case 'development':
      return 'http://127.0.0.1:8000';
    case 'staging':
      // Fallback to localhost if no ngrok URL available
      log('⚠️  No NGROK_PUBLIC_URL found, falling back to localhost (may cause CORS issues)', 'warn');
      return 'http://127.0.0.1:8000';
    case 'production':
      return 'https://api.hero365.ai';
    default:
      return 'http://127.0.0.1:8000';
  }
}

/**
 * Deploy to Cloudflare Workers
 */
function deployToCloudflare(businessConfig) {
  if (CONFIG.buildOnly) {
    log('🏁 Build-only mode, skipping deployment', 'info');
    return { success: true, buildOnly: true };
  }
  
  log('🚀 Deploying to Cloudflare Workers...', 'info');
  
  try {
    // Update wrangler.toml with business-specific configuration
    updateWranglerConfig(businessConfig);
    
    // Build deployment command using OpenNext for Cloudflare Workers
    let deployCommand = `npm run deploy:${CONFIG.environment}`;
    
    // Fallback to generic deploy if environment-specific command doesn't exist
    if (!['development', 'staging', 'production'].includes(CONFIG.environment)) {
      deployCommand = 'npm run deploy';
    }
    
    verbose(`Executing: ${deployCommand}`);
    
    const output = execSync(deployCommand, {
      cwd: PATHS.root,
      stdio: CONFIG.verbose ? 'inherit' : 'pipe',
      encoding: 'utf8'
    });
    
    // Extract deployment URL from output
    const urlMatch = output && typeof output === 'string' ? output.match(/https:\/\/[^\s]+/) : null;
    const deploymentUrl = urlMatch ? urlMatch[0] : null;
    
    log('✅ Deployment completed successfully', 'success');
    
    if (deploymentUrl) {
      log(`🌐 Website URL: ${deploymentUrl}`, 'success');
    }
    
    // Generate expected worker URL based on environment
    const workerName = `hero365-website-${CONFIG.environment}`;
    const expectedUrl = `https://${workerName}.hero365.workers.dev`;
    
    return {
      success: true,
      workerName,
      deploymentUrl: deploymentUrl || expectedUrl,
      output: CONFIG.verbose ? null : output
    };
  } catch (error) {
    log(`❌ Deployment failed: ${error.message}`, 'error');
    return { success: false, error: error.message };
  }
}

/**
 * Main deployment process
 */
async function main() {
  const startTime = Date.now();
  
  log('🚀 Starting Enhanced Website Deployment', 'info');
  log(`Business ID: ${CONFIG.businessId}`, 'info');
  log(`Environment: ${CONFIG.environment}`, 'info');
  log(`Build Only: ${CONFIG.buildOnly}`, 'info');
  
  try {
    // Step 1: Load deployment configuration
    log('📋 Loading deployment configuration...', 'info');
    const deploymentConfig = loadDeploymentConfig();
    
    // Step 2: Generate business-specific configuration
    log('🏢 Generating business configuration...', 'info');
    const businessConfig = await generateBusinessConfig(deploymentConfig);
    
    // Step 3: Fetch SEO pages from backend
    log('🔍 Fetching SEO pages from backend...', 'info');
    const apiUrl = getApiUrlForEnvironment(CONFIG.environment);
    const seoData = await fetchSEOPages(CONFIG.businessId, apiUrl);
    
    // Step 4: Generate SEO content for website builder
    log('🔍 Generating SEO content...', 'info');
    const seoSuccess = await generateSEOContent(CONFIG.businessId, seoData);
    
    if (!seoSuccess) {
      log('⚠️ SEO content generation failed, continuing with fallback content', 'warn');
    }
    
    // Step 4.5: Generate sitemap and robots.txt
    log('🗺️ Generating sitemap and robots.txt...', 'info');
    const sitemapSuccess = await generateSitemapFiles(businessConfig);
    
    if (!sitemapSuccess) {
      log('⚠️ Sitemap generation failed, continuing without sitemap', 'warn');
    }
    
    // Step 5: Generate environment configuration
    log('⚙️ Generating environment configuration...', 'info');
    const envConfig = generateEnvironmentConfig(deploymentConfig, businessConfig);
    
    // Step 6: Build website
    log('🔨 Building website...', 'info');
    const buildSuccess = buildWebsite();
    
    if (!buildSuccess) {
      process.exit(1);
    }
    
    // Step 5: Deploy (if not build-only)
    const deployResult = deployToCloudflare(businessConfig);
    
    // Summary
    const duration = ((Date.now() - startTime) / 1000).toFixed(1);
    
    log('', 'info');
    log('🎉 Deployment Summary', 'success');
    log('═'.repeat(50), 'info');
    log(`Business: ${businessConfig.businessData.business_name}`, 'info');
    log(`Business ID: ${CONFIG.businessId}`, 'info');
    log(`Environment: ${CONFIG.environment}`, 'info');
    log(`Duration: ${duration}s`, 'info');
    
    if (deployResult.deploymentUrl) {
      log(`Website URL: ${deployResult.deploymentUrl}`, 'success');
    }
    
    if (deployResult.buildOnly) {
      log('Build completed (deployment skipped)', 'info');
    }
    
    log('', 'info');
    log('✅ All operations completed successfully!', 'success');
    
  } catch (error) {
    log(`❌ Deployment failed: ${error.message}`, 'error');
    process.exit(1);
  }
}

// Run the deployment
main().catch(error => {
  log(`❌ Unexpected error: ${error.message}`, 'error');
  process.exit(1);
});
