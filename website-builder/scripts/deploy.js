#!/usr/bin/env node

/**
 * Deployment Script for Hero365 Website Builder
 * 
 * Configures environment-specific settings and deploys to different platforms
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Load deployment configuration
const deploymentConfig = require('../config/deployment.json');

/**
 * Get environment from command line arguments or detect from current context
 */
function getEnvironment() {
  const args = process.argv.slice(2);
  const envArg = args.find(arg => arg.startsWith('--env='));
  
  if (envArg) {
    return envArg.split('=')[1];
  }
  
  // Auto-detect environment
  if (process.env.NODE_ENV === 'production') {
    return 'production';
  } else if (process.env.NODE_ENV === 'staging' || process.env.VERCEL_ENV === 'preview') {
    return 'staging';
  } else {
    return 'development';
  }
}

/**
 * Generate environment variables for the specified environment
 */
function generateEnvVars(environment) {
  const config = deploymentConfig.environments[environment];
  
  if (!config) {
    throw new Error(`Unknown environment: ${environment}`);
  }
  
  const envVars = {
    // Node environment
    NODE_ENV: environment === 'development' ? 'development' : 'production',
    
    // API configuration
    NEXT_PUBLIC_API_URL: config.api.baseUrl,
    NEXT_PUBLIC_API_TIMEOUT: config.api.timeout.toString(),
    NEXT_PUBLIC_API_RETRIES: config.api.retries.toString(),
    
    // Website configuration
    NEXT_PUBLIC_WEBSITE_URL: config.website.baseUrl,
    
    // Feature flags
    NEXT_PUBLIC_ANALYTICS_ENABLED: config.features.analytics.toString(),
    NEXT_PUBLIC_ERROR_REPORTING_ENABLED: config.features.errorReporting.toString(),
    NEXT_PUBLIC_DEBUG_MODE: config.features.debugMode.toString(),
    NEXT_PUBLIC_VOICE_AGENT_ENABLED: config.features.voiceAgent.toString(),
    NEXT_PUBLIC_BOOKING_WIDGET_ENABLED: config.features.bookingWidget.toString(),
    
    // Business configuration
    NEXT_PUBLIC_DEFAULT_BUSINESS_ID: config.business.defaultBusinessId,
    NEXT_PUBLIC_DEFAULT_BUSINESS_NAME: config.business.defaultBusinessName,
    NEXT_PUBLIC_DEFAULT_BUSINESS_PHONE: config.business.defaultBusinessPhone,
    NEXT_PUBLIC_DEFAULT_BUSINESS_EMAIL: config.business.defaultBusinessEmail,
    
    // Environment identifier
    NEXT_PUBLIC_ENVIRONMENT: environment
  };
  
  return envVars;
}

/**
 * Write environment variables to .env.local file
 */
function writeEnvFile(envVars, environment) {
  const envContent = [
    `# Auto-generated environment configuration for ${environment}`,
    `# Generated at: ${new Date().toISOString()}`,
    `# DO NOT EDIT MANUALLY - Use scripts/deploy.js to regenerate`,
    '',
    ...Object.entries(envVars).map(([key, value]) => `${key}=${value}`),
    ''
  ].join('\n');
  
  const envFilePath = path.join(__dirname, '..', '.env.local');
  fs.writeFileSync(envFilePath, envContent);
  
  console.log(`✅ Generated .env.local for ${environment} environment`);
}

/**
 * Build the application
 */
function buildApplication() {
  console.log('🔨 Building application...');
  
  try {
    execSync('npm run build', { 
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });
    console.log('✅ Build completed successfully');
  } catch (error) {
    console.error('❌ Build failed:', error.message);
    process.exit(1);
  }
}

/**
 * Deploy to Cloudflare Pages
 */
function deployToCloudflare(environment) {
  console.log(`🚀 Deploying to Cloudflare Pages (${environment})...`);
  
  const projectName = environment === 'production' ? 'hero365-professional' : `hero365-professional-${environment}`;
  
  try {
    execSync(`npx wrangler pages deploy out --project-name=${projectName}`, {
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });
    console.log('✅ Deployment to Cloudflare Pages completed');
  } catch (error) {
    console.error('❌ Cloudflare deployment failed:', error.message);
    process.exit(1);
  }
}

/**
 * Deploy to Vercel
 */
function deployToVercel(environment) {
  console.log(`🚀 Deploying to Vercel (${environment})...`);
  
  const vercelArgs = environment === 'production' ? '--prod' : '';
  
  try {
    execSync(`npx vercel ${vercelArgs}`, {
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });
    console.log('✅ Deployment to Vercel completed');
  } catch (error) {
    console.error('❌ Vercel deployment failed:', error.message);
    process.exit(1);
  }
}

/**
 * Main deployment function
 */
function main() {
  const args = process.argv.slice(2);
  const environment = getEnvironment();
  const platform = args.find(arg => arg.startsWith('--platform='))?.split('=')[1] || 'cloudflare';
  const buildOnly = args.includes('--build-only');
  
  console.log(`🌟 Hero365 Deployment Script`);
  console.log(`📦 Environment: ${environment}`);
  console.log(`🏗️  Platform: ${platform}`);
  console.log('');
  
  try {
    // Generate environment configuration
    const envVars = generateEnvVars(environment);
    writeEnvFile(envVars, environment);
    
    // Build application
    buildApplication();
    
    if (buildOnly) {
      console.log('✅ Build-only mode: Deployment skipped');
      return;
    }
    
    // Deploy to specified platform
    switch (platform) {
      case 'cloudflare':
        deployToCloudflare(environment);
        break;
      case 'vercel':
        deployToVercel(environment);
        break;
      default:
        console.error(`❌ Unknown platform: ${platform}`);
        process.exit(1);
    }
    
    console.log('');
    console.log('🎉 Deployment completed successfully!');
    
    // Show deployment URLs
    const config = deploymentConfig.environments[environment];
    console.log(`🌐 Website URL: ${config.website.baseUrl}`);
    console.log(`🔗 API URL: ${config.api.baseUrl}`);
    
  } catch (error) {
    console.error('💥 Deployment failed:', error.message);
    process.exit(1);
  }
}

// Show help if requested
if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log(`
Hero365 Deployment Script

Usage:
  node scripts/deploy.js [options]

Options:
  --env=<environment>     Set environment (development, staging, production)
  --platform=<platform>   Set deployment platform (cloudflare, vercel)
  --build-only           Only build, don't deploy
  --help, -h             Show this help message

Examples:
  node scripts/deploy.js --env=staging --platform=cloudflare
  node scripts/deploy.js --env=production --build-only
  node scripts/deploy.js --platform=vercel

Environment Detection:
  - If --env is not specified, environment is auto-detected from:
    - NODE_ENV environment variable
    - VERCEL_ENV environment variable
    - Defaults to 'development'
`);
  process.exit(0);
}

// Run the deployment
if (require.main === module) {
  main();
}

module.exports = {
  getEnvironment,
  generateEnvVars,
  writeEnvFile,
  buildApplication,
  deployToCloudflare,
  deployToVercel
};
