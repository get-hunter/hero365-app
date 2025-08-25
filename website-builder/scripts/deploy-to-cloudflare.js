#!/usr/bin/env node

/**
 * Cloudflare Pages Deployment Script
 * 
 * This script builds and deploys the website to Cloudflare Pages.
 * It can be used standalone or integrated with the backend deployment service.
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

class CloudflareDeployer {
  constructor(options = {}) {
    this.projectName = options.projectName || 'hero365-professional';
    this.outputDir = options.outputDir || 'out';
    this.isPreview = options.isPreview || false;
    this.verbose = options.verbose || false;
    this.compatibilityDate = options.compatibilityDate || '2024-01-01';
  }

  log(message) {
    if (this.verbose) {
      console.log(`[${new Date().toISOString()}] ${message}`);
    }
  }

  error(message) {
    console.error(`❌ Error: ${message}`);
  }

  success(message) {
    console.log(`✅ ${message}`);
  }

  /**
   * Check if required tools are installed
   */
  checkPrerequisites() {
    this.log('Checking prerequisites...');
    
    try {
      // Check if wrangler is installed
      execSync('wrangler --version', { stdio: 'pipe' });
      this.success('Wrangler CLI is installed');
    } catch (error) {
      this.error('Wrangler CLI is not installed. Please install it with: npm install -g wrangler');
      throw new Error('Missing wrangler CLI');
    }

    try {
      // Check if authenticated
      execSync('wrangler whoami', { stdio: 'pipe' });
      this.success('Wrangler is authenticated');
    } catch (error) {
      this.error('Wrangler is not authenticated. Please run: wrangler login');
      throw new Error('Wrangler not authenticated');
    }

    // Check if output directory exists
    if (!fs.existsSync(this.outputDir)) {
      this.error(`Output directory '${this.outputDir}' does not exist. Please run 'npm run build' first.`);
      throw new Error('Missing build output');
    }

    this.success('All prerequisites met');
  }

  /**
   * Validate the build output
   */
  validateBuild() {
    this.log('Validating build output...');
    
    const indexPath = path.join(this.outputDir, 'index.html');
    if (!fs.existsSync(indexPath)) {
      this.error('index.html not found in build output');
      throw new Error('Invalid build output');
    }

    const templatePath = path.join(this.outputDir, 'templates', 'professional', 'index.html');
    if (!fs.existsSync(templatePath)) {
      this.error('Professional template not found in build output');
      throw new Error('Missing template in build');
    }

    // Check for essential assets
    const nextDir = path.join(this.outputDir, '_next');
    if (!fs.existsSync(nextDir)) {
      this.error('Next.js assets not found in build output');
      throw new Error('Missing Next.js assets');
    }

    this.success('Build output validation passed');
  }

  /**
   * Create or update Cloudflare Pages project
   */
  async ensureProject() {
    this.log(`Ensuring Cloudflare Pages project: ${this.projectName}`);
    
    try {
      // Check if project exists
      const result = execSync(`wrangler pages project list --json`, { 
        stdio: 'pipe',
        encoding: 'utf8'
      });
      
      const projects = JSON.parse(result);
      const existingProject = projects.find(p => p.name === this.projectName);
      
      if (existingProject) {
        this.success(`Project '${this.projectName}' already exists`);
        return existingProject;
      }
      
      // Create new project
      this.log(`Creating new project: ${this.projectName}`);
      execSync(`wrangler pages project create ${this.projectName} --production-branch main`, {
        stdio: this.verbose ? 'inherit' : 'pipe'
      });
      
      this.success(`Created new project: ${this.projectName}`);
      
    } catch (error) {
      this.error(`Failed to ensure project: ${error.message}`);
      throw error;
    }
  }

  /**
   * Deploy to Cloudflare Pages
   */
  async deploy() {
    this.log('Starting deployment to Cloudflare Pages...');
    
    const deploymentType = this.isPreview ? 'preview' : 'production';
    this.log(`Deployment type: ${deploymentType}`);
    
    try {
      // Build the wrangler command
      const cmd = [
        'wrangler',
        'pages',
        'deploy',
        this.outputDir,
        '--project-name',
        this.projectName
      ];

      // Add preview flag if needed
      if (this.isPreview) {
        cmd.push('--branch', `preview-${Date.now()}`);
      }

      this.log(`Running: ${cmd.join(' ')}`);
      
      // Execute deployment
      const result = execSync(cmd.join(' '), {
        stdio: this.verbose ? 'inherit' : 'pipe',
        encoding: 'utf8'
      });
      
      // Extract deployment URL from output
      const urlMatch = result.match(/https:\/\/[^\s]+\.pages\.dev/);
      const deploymentUrl = urlMatch ? urlMatch[0] : null;
      
      if (deploymentUrl) {
        this.success(`Deployment successful!`);
        this.success(`URL: ${deploymentUrl}`);
        return {
          success: true,
          url: deploymentUrl,
          type: deploymentType,
          timestamp: new Date().toISOString()
        };
      } else {
        throw new Error('Could not extract deployment URL from output');
      }
      
    } catch (error) {
      this.error(`Deployment failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get deployment status
   */
  async getDeploymentStatus() {
    try {
      const result = execSync(`wrangler pages deployment list --project-name ${this.projectName} --json`, {
        stdio: 'pipe',
        encoding: 'utf8'
      });
      
      const deployments = JSON.parse(result);
      return deployments[0]; // Most recent deployment
      
    } catch (error) {
      this.error(`Failed to get deployment status: ${error.message}`);
      return null;
    }
  }

  /**
   * Full deployment process
   */
  async run() {
    console.log('🚀 Starting Cloudflare Pages deployment...\n');
    
    try {
      // Step 1: Check prerequisites
      this.checkPrerequisites();
      
      // Step 2: Validate build
      this.validateBuild();
      
      // Step 3: Ensure project exists
      await this.ensureProject();
      
      // Step 4: Deploy
      const deployment = await this.deploy();
      
      // Step 5: Get final status
      const status = await this.getDeploymentStatus();
      
      console.log('\n🎉 Deployment completed successfully!');
      console.log(`📍 URL: ${deployment.url}`);
      console.log(`🔗 Project: https://dash.cloudflare.com/pages/view/${this.projectName}`);
      
      if (status) {
        console.log(`📊 Status: ${status.stage}`);
        console.log(`⏰ Created: ${new Date(status.created_on).toLocaleString()}`);
      }
      
      return deployment;
      
    } catch (error) {
      console.error('\n💥 Deployment failed!');
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  }
}

// CLI Interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const options = {};
  
  // Parse command line arguments
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    switch (arg) {
      case '--preview':
        options.isPreview = true;
        break;
      case '--verbose':
      case '-v':
        options.verbose = true;
        break;
      case '--project-name':
        options.projectName = args[++i];
        break;
      case '--output-dir':
        options.outputDir = args[++i];
        break;
      case '--help':
      case '-h':
        console.log(`
Cloudflare Pages Deployment Script

Usage: node deploy-to-cloudflare.js [options]

Options:
  --preview              Deploy as preview (not production)
  --verbose, -v          Verbose logging
  --project-name <name>  Cloudflare Pages project name (default: hero365-professional)
  --output-dir <dir>     Build output directory (default: out)
  --help, -h             Show this help message

Examples:
  node deploy-to-cloudflare.js                    # Deploy to production
  node deploy-to-cloudflare.js --preview          # Deploy as preview
  node deploy-to-cloudflare.js --verbose          # Deploy with verbose logging
  node deploy-to-cloudflare.js --project-name my-site --preview
        `);
        process.exit(0);
        break;
    }
  }
  
  // Run deployment
  const deployer = new CloudflareDeployer(options);
  deployer.run().catch(console.error);
}

module.exports = CloudflareDeployer;
