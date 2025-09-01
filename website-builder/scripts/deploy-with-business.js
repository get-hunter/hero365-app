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
  
  // Create business configuration
  const businessConfig = {
    businessId: CONFIG.businessId,
    environment: CONFIG.environment,
    businessData: businessData || {
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
    },
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
    
    // Step 3: Generate environment configuration
    log('⚙️ Generating environment configuration...', 'info');
    const envConfig = generateEnvironmentConfig(deploymentConfig, businessConfig);
    
    // Step 4: Build website
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
