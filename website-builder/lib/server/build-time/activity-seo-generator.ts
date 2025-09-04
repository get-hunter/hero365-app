#!/usr/bin/env tsx

/**
 * Activity-First SEO Content Generator for Website Builder
 * 
 * This script generates SEO content using activity content packs and business data
 * to create activity-specific pages and SEO metadata.
 * 
 * Usage:
 *   npx tsx lib/build-time/activity-seo-generator.ts --businessId=<uuid> [options]
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { activityContentPacks } from '../templates/activity-content-packs';
import { ActivityContentPack, BusinessActivityData } from '../templates/types';

// Types for the generated content structure
interface ActivitySEOPage {
  slug: string;
  path: string;
  title: string;
  meta_description: string;
  keywords: string[];
  content: {
    hero: ActivityContentPack['hero'];
    benefits: ActivityContentPack['benefits'];
    process: ActivityContentPack['process'];
    faqs: ActivityContentPack['faqs'];
    pricing?: ActivityContentPack['pricing'];
  };
  schema: ActivityContentPack['schema'];
  canonical_url: string;
  og_type: string;
  priority_score: number;
  created_at: string;
}

interface BusinessData {
  id: string;
  name: string;
  description: string;
  phone: string;
  email: string;
  address: string;
  city: string;
  state: string;
  postal_code: string;
  service_areas: string[];
  selected_activity_slugs: string[];
}

interface GeneratedActivityContent {
  pages: ActivitySEOPage[];
  business: BusinessData;
  generation_metadata: {
    generated_at: string;
    business_id: string;
    business_name: string;
    total_pages: number;
    method: 'activity-content-packs';
  };
}

// Configuration
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, '../..');
const OUTPUT_DIR = path.join(PROJECT_ROOT, 'lib/generated');

/**
 * Main activity SEO generator function
 */
async function generateActivitySEOContent(options: {
  businessId?: string;
  backendUrl?: string;
  outputDir?: string;
  baseUrl?: string;
}) {
  console.log('🔄 Starting activity-first SEO content generation...');
  
  try {
    // Step 1: Load business data
    const businessData = await loadBusinessData(options);
    
    if (!businessData) {
      throw new Error('No business data available');
    }
    
    console.log(`✅ Loaded business: ${businessData.name} with ${businessData.selected_activity_slugs.length} activities`);
    
    // Step 2: Generate activity pages
    const activityPages = generateActivityPages(businessData, options.baseUrl);
    
    console.log(`✅ Generated ${activityPages.length} activity pages`);
    
    // Step 3: Create generated content structure
    const generatedContent: GeneratedActivityContent = {
      pages: activityPages,
      business: businessData,
      generation_metadata: {
        generated_at: new Date().toISOString(),
        business_id: businessData.id,
        business_name: businessData.name,
        total_pages: activityPages.length,
        method: 'activity-content-packs'
      }
    };
    
    // Step 4: Transform and write output files
    const outputDir = options.outputDir || OUTPUT_DIR;
    await ensureDirectoryExists(outputDir);
    
    const seoPages = transformToSEOPages(generatedContent);
    const routeManifest = generateRouteManifest(generatedContent);
    const sitemapData = generateSitemapData(generatedContent);
    
    await Promise.all([
      writeActivitySEOPagesModule(seoPages, outputDir),
      writeRouteManifest(routeManifest, outputDir),
      writeSitemapData(sitemapData, outputDir),
      writeMetadata(generatedContent.generation_metadata, outputDir)
    ]);
    
    console.log('✅ Activity SEO content generation completed successfully');
    console.log(`📁 Output directory: ${outputDir}`);
    console.log(`📄 Generated ${Object.keys(seoPages).length} SEO pages`);
    console.log(`🗺️ Generated route manifest with ${routeManifest.routes.length} routes`);
    
    return {
      success: true,
      pagesGenerated: Object.keys(seoPages).length,
      routesGenerated: routeManifest.routes.length,
      outputDir
    };
    
  } catch (error) {
    console.error('❌ Activity SEO content generation failed:', error.message);
    throw error;
  }
}

/**
 * Load business data from backend API
 */
async function loadBusinessData(options: {
  businessId?: string;
  backendUrl?: string;
}): Promise<BusinessData | null> {
  
  if (!options.businessId || !options.backendUrl) {
    console.warn('⚠️ No business ID or backend URL provided, using mock data');
    return getMockBusinessData();
  }
  
  console.log(`🌐 Fetching business data for: ${options.businessId}`);
  
  try {
    const response = await fetch(`${options.backendUrl}/api/v1/businesses/${options.businessId}`);
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    
    const businessData = await response.json();
    
    // Transform to our expected format
    return {
      id: businessData.id,
      name: businessData.name,
      description: businessData.description || `Professional services in ${businessData.city}`,
      phone: businessData.phone || '',
      email: businessData.email || '',
      address: businessData.address || '',
      city: businessData.city || '',
      state: businessData.state || '',
      postal_code: businessData.postal_code || '',
      service_areas: businessData.service_areas || [businessData.city].filter(Boolean),
      selected_activity_slugs: businessData.selected_activity_slugs || []
    };
    
  } catch (error) {
    console.error(`Failed to fetch business data: ${error.message}`);
    console.log('📝 Using mock business data for development');
    return getMockBusinessData();
  }
}

/**
 * Get mock business data for development
 */
function getMockBusinessData(): BusinessData {
  return {
    id: 'demo-business-id',
    name: 'Professional Home Services',
    description: 'Expert home services you can trust',
    phone: '(555) 123-4567',
    email: 'info@example.com',
    address: '123 Main St',
    city: 'Austin',
    state: 'TX',
    postal_code: '78701',
    service_areas: ['Austin', 'Round Rock', 'Cedar Park'],
    selected_activity_slugs: ['ac-installation', 'ac-repair', 'hvac-maintenance', 'heating-repair', 'drain-cleaning', 'leak-repair', 'toilet-repair', 'water-heater-repair']
  };
}

/**
 * Generate activity pages from business data and content packs
 */
function generateActivityPages(businessData: BusinessData, baseUrl?: string): ActivitySEOPage[] {
  const pages: ActivitySEOPage[] = [];
  const currentTime = new Date().toISOString();
  
  for (const activitySlug of businessData.selected_activity_slugs) {
    const contentPack = activityContentPacks[activitySlug];
    
    if (!contentPack) {
      console.warn(`⚠️ No content pack found for activity: ${activitySlug}`);
      continue;
    }
    
    // Generate SEO metadata with business context
    const title = contentPack.seo.title_template
      .replace('{businessName}', businessData.name)
      .replace('{city}', businessData.city);
    
    const metaDescription = contentPack.seo.description_template
      .replace('{businessName}', businessData.name)
      .replace('{city}', businessData.city)
      .replace('{phone}', businessData.phone);
    
    const path = `/services/${activitySlug}`;
    const canonicalUrl = baseUrl ? `${baseUrl}${path}` : path;
    
    // Calculate priority score based on content completeness and business factors
    let priorityScore = 70; // Base score
    if (contentPack.pricing) priorityScore += 10;
    if (contentPack.faqs.length >= 3) priorityScore += 10;
    if (contentPack.process.steps.length >= 4) priorityScore += 5;
    if (contentPack.benefits.bullets.length >= 5) priorityScore += 5;
    
    const page: ActivitySEOPage = {
      slug: activitySlug,
      path,
      title,
      meta_description: metaDescription,
      keywords: [
        ...contentPack.seo.keywords,
        businessData.name.toLowerCase(),
        businessData.city.toLowerCase(),
        contentPack.schema.service_type.toLowerCase()
      ],
      content: {
        hero: contentPack.hero,
        benefits: contentPack.benefits,
        process: contentPack.process,
        faqs: contentPack.faqs,
        pricing: contentPack.pricing
      },
      schema: contentPack.schema,
      canonical_url: canonicalUrl,
      og_type: 'article',
      priority_score: Math.min(priorityScore, 100),
      created_at: currentTime
    };
    
    pages.push(page);
  }
  
  // Sort by priority score (highest first)
  pages.sort((a, b) => b.priority_score - a.priority_score);
  
  return pages;
}

/**
 * Transform generated content to SEO pages format
 */
function transformToSEOPages(content: GeneratedActivityContent): Record<string, any> {
  const seoPages: Record<string, any> = {};
  
  for (const page of content.pages) {
    seoPages[page.path] = {
      title: page.title,
      meta_description: page.meta_description,
      keywords: page.keywords,
      content: page.content,
      schema: page.schema,
      canonical_url: page.canonical_url,
      og_type: page.og_type,
      priority_score: page.priority_score,
      created_at: page.created_at,
      activity_slug: page.slug
    };
  }
  
  return seoPages;
}

/**
 * Generate route manifest for static site generation
 */
function generateRouteManifest(content: GeneratedActivityContent) {
  const routes = content.pages.map(page => ({
    path: page.path,
    slug: page.slug,
    priority: page.priority_score,
    lastModified: page.created_at,
    changeFreq: page.priority_score > 80 ? 'weekly' : 'monthly',
    type: 'activity'
  }));
  
  // Add services index page
  routes.unshift({
    path: '/services',
    slug: 'services-index',
    priority: 90,
    lastModified: content.generation_metadata.generated_at,
    changeFreq: 'weekly',
    type: 'index'
  });
  
  return {
    generated_at: new Date().toISOString(),
    business_id: content.generation_metadata.business_id,
    business_name: content.generation_metadata.business_name,
    total_routes: routes.length,
    routes
  };
}

/**
 * Generate sitemap data
 */
function generateSitemapData(content: GeneratedActivityContent) {
  const urls = content.pages.map(page => ({
    loc: page.path,
    lastmod: page.created_at,
    changefreq: page.priority_score > 80 ? 'weekly' : 'monthly',
    priority: Math.min(page.priority_score / 100, 1.0)
  }));
  
  // Add services index page
  urls.unshift({
    loc: '/services',
    lastmod: content.generation_metadata.generated_at,
    changefreq: 'weekly',
    priority: 0.9
  });
  
  return {
    generated_at: new Date().toISOString(),
    business_id: content.generation_metadata.business_id,
    urls
  };
}

/**
 * Write activity SEO pages module
 */
async function writeActivitySEOPagesModule(seoPages: Record<string, any>, outputDir: string) {
  const moduleContent = `// Auto-generated Activity SEO pages data
// Generated at: ${new Date().toISOString()}
// Do not edit this file manually

import { ActivityContentPack } from '../templates/types';

export interface ActivitySEOPageData {
  title: string;
  meta_description: string;
  keywords: string[];
  content: {
    hero: ActivityContentPack['hero'];
    benefits: ActivityContentPack['benefits'];
    process: ActivityContentPack['process'];
    faqs: ActivityContentPack['faqs'];
    pricing?: ActivityContentPack['pricing'];
  };
  schema: ActivityContentPack['schema'];
  canonical_url: string;
  og_type: string;
  priority_score: number;
  created_at: string;
  activity_slug: string;
}

export const activitySEOPages: Record<string, ActivitySEOPageData> = ${JSON.stringify(seoPages, null, 2)};

export function getActivitySEOPageData(urlPath: string): ActivitySEOPageData | null {
  return activitySEOPages[urlPath] || null;
}

export function getAllActivitySEOPages(): Record<string, ActivitySEOPageData> {
  return activitySEOPages;
}

export function getActivitySEOPagePaths(): string[] {
  return Object.keys(activitySEOPages);
}

export function getActivitySEOPagesByPriority(): ActivitySEOPageData[] {
  return Object.values(activitySEOPages).sort((a, b) => b.priority_score - a.priority_score);
}
`;
  
  const filePath = path.join(outputDir, 'activity-seo-pages.ts');
  await fs.writeFile(filePath, moduleContent, 'utf-8');
  console.log(`📝 Written activity SEO pages module: ${filePath}`);
}

/**
 * Write route manifest
 */
async function writeRouteManifest(manifest: any, outputDir: string) {
  const filePath = path.join(outputDir, 'activity-route-manifest.json');
  await fs.writeFile(filePath, JSON.stringify(manifest, null, 2), 'utf-8');
  console.log(`📝 Written activity route manifest: ${filePath}`);
}

/**
 * Write sitemap data
 */
async function writeSitemapData(sitemapData: any, outputDir: string) {
  const filePath = path.join(outputDir, 'activity-sitemap-data.json');
  await fs.writeFile(filePath, JSON.stringify(sitemapData, null, 2), 'utf-8');
  console.log(`📝 Written activity sitemap data: ${filePath}`);
}

/**
 * Write generation metadata
 */
async function writeMetadata(metadata: any, outputDir: string) {
  const filePath = path.join(outputDir, 'activity-generation-metadata.json');
  await fs.writeFile(filePath, JSON.stringify(metadata, null, 2), 'utf-8');
  console.log(`📝 Written activity generation metadata: ${filePath}`);
}

/**
 * Ensure directory exists
 */
async function ensureDirectoryExists(dirPath: string) {
  try {
    await fs.access(dirPath);
  } catch {
    await fs.mkdir(dirPath, { recursive: true });
    console.log(`📁 Created directory: ${dirPath}`);
  }
}

/**
 * CLI interface
 */
async function main() {
  const args = process.argv.slice(2);
  const options: any = {};
  
  // Parse command line arguments
  for (const arg of args) {
    if (arg.startsWith('--businessId=')) {
      options.businessId = arg.split('=')[1];
    } else if (arg.startsWith('--backend=')) {
      options.backendUrl = arg.split('=')[1];
    } else if (arg.startsWith('--output=')) {
      options.outputDir = arg.split('=')[1];
    } else if (arg.startsWith('--baseUrl=')) {
      options.baseUrl = arg.split('=')[1];
    }
  }
  
  // Set defaults
  if (!options.backendUrl) {
    options.backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
  }
  
  if (!options.baseUrl) {
    options.baseUrl = process.env.BASE_URL || 'https://example.com';
  }
  
  try {
    await generateActivitySEOContent(options);
    console.log('🎉 Activity SEO content generation completed successfully');
  } catch (error) {
    console.error('💥 Activity SEO content generation failed:', error.message);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { generateActivitySEOContent };
