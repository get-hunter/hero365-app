#!/usr/bin/env tsx

/**
 * SEO Content Generator for Website Builder
 * 
 * This script fetches LLM-generated content from the backend and creates
 * static data modules for the website builder to consume during build time.
 * 
 * Usage:
 *   npx tsx lib/build-time/seo-generator.ts --businessId=<uuid> [options]
 *   npx tsx lib/build-time/seo-generator.ts --input=<path-to-content.json>
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

// Types for the generated content structure
interface GeneratedPage {
  slug: string;
  path: string;
  title: string;
  meta_description: string;
  content: Record<string, any>;
  seo: Record<string, any>;
  priority_score?: number;
  generation_method?: string;
  generated_at?: string;
}

interface GeneratedContent {
  pages: GeneratedPage[];
  content_items: Array<{
    type: string;
    service_id?: string;
    service_name?: string;
    content: Record<string, any>;
    seo?: Record<string, any>;
  }>;
  seo_configs: Record<string, any>;
  quality_score: number;
  generation_metadata: {
    generated_at: string;
    business_id: string;
    business_name: string;
    total_pages: number;
    total_content_items: number;
  };
}

interface SEOPageData {
  title: string;
  meta_description: string;
  content: string;
  keywords: string[];
  canonical_url: string;
  og_type: string;
  word_count: number;
  created_at: string;
}

// Configuration
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, '../..');
const OUTPUT_DIR = path.join(PROJECT_ROOT, 'lib/generated');

/**
 * Main SEO generator function
 */
async function generateSEOContent(options: {
  businessId?: string;
  inputFile?: string;
  backendUrl?: string;
  outputDir?: string;
}) {
  console.log('🔄 Starting SEO content generation...');
  
  try {
    // Step 1: Load generated content
    const generatedContent = await loadGeneratedContent(options);
    
    if (!generatedContent) {
      throw new Error('No generated content available');
    }
    
    console.log(`✅ Loaded content: ${generatedContent.pages.length} pages, ${generatedContent.content_items.length} items`);
    
    // Step 2: Transform content for website builder
    const seoPages = transformToSEOPages(generatedContent);
    const routeManifest = generateRouteManifest(generatedContent);
    const sitemapData = generateSitemapData(generatedContent);
    
    // Step 3: Write output files
    const outputDir = options.outputDir || OUTPUT_DIR;
    await ensureDirectoryExists(outputDir);
    
    await Promise.all([
      writeSEOPagesModule(seoPages, outputDir),
      writeRouteManifest(routeManifest, outputDir),
      writeSitemapData(sitemapData, outputDir),
      writeMetadata(generatedContent.generation_metadata, outputDir)
    ]);
    
    console.log('✅ SEO content generation completed successfully');
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
    console.error('❌ SEO content generation failed:', error.message);
    throw error;
  }
}

/**
 * Load generated content from backend or input file
 */
async function loadGeneratedContent(options: {
  businessId?: string;
  inputFile?: string;
  backendUrl?: string;
}): Promise<GeneratedContent | null> {
  
  // Option 1: Load from input file (preferred for build-time)
  if (options.inputFile) {
    console.log(`📂 Loading content from file: ${options.inputFile}`);
    
    try {
      const fileContent = await fs.readFile(options.inputFile, 'utf-8');
      return JSON.parse(fileContent);
    } catch (error) {
      console.error(`Failed to load content from file: ${error.message}`);
      return null;
    }
  }
  
  // Option 2: Fetch from backend API
  if (options.businessId && options.backendUrl) {
    console.log(`🌐 Fetching content from backend for business: ${options.businessId}`);
    
    try {
      const response = await fetch(`${options.backendUrl}/api/v1/llm-content/${options.businessId}/latest`);
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Failed to fetch content from backend: ${error.message}`);
      return null;
    }
  }
  
  console.warn('⚠️ No input file or backend configuration provided');
  return null;
}

/**
 * Transform generated content to SEO pages format
 */
function transformToSEOPages(content: GeneratedContent): Record<string, SEOPageData> {
  const seoPages: Record<string, SEOPageData> = {};
  
  for (const page of content.pages) {
    const urlPath = page.path;
    const contentText = extractTextContent(page.content);
    
    seoPages[urlPath] = {
      title: page.title,
      meta_description: page.meta_description,
      content: contentText,
      keywords: extractKeywords(page),
      canonical_url: page.seo?.canonical || urlPath,
      og_type: page.seo?.og_type || 'article',
      word_count: countWords(contentText),
      created_at: page.generated_at || content.generation_metadata.generated_at
    };
  }
  
  return seoPages;
}

/**
 * Generate route manifest for static site generation
 */
function generateRouteManifest(content: GeneratedContent) {
  const routes = content.pages.map(page => ({
    path: page.path,
    slug: page.slug,
    priority: page.priority_score || 50,
    lastModified: page.generated_at || content.generation_metadata.generated_at,
    changeFreq: page.priority_score && page.priority_score > 80 ? 'weekly' : 'monthly'
  }));
  
  // Sort by priority (highest first)
  routes.sort((a, b) => b.priority - a.priority);
  
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
function generateSitemapData(content: GeneratedContent) {
  const urls = content.pages.map(page => ({
    loc: page.path,
    lastmod: page.generated_at || content.generation_metadata.generated_at,
    changefreq: page.priority_score && page.priority_score > 80 ? 'weekly' : 'monthly',
    priority: Math.min((page.priority_score || 50) / 100, 1.0)
  }));
  
  return {
    generated_at: new Date().toISOString(),
    business_id: content.generation_metadata.business_id,
    urls
  };
}

/**
 * Extract text content from page content structure
 */
function extractTextContent(content: Record<string, any>): string {
  let text = '';
  
  function extractFromObject(obj: any): void {
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
 * Extract keywords from page data
 */
function extractKeywords(page: GeneratedPage): string[] {
  const keywords: string[] = [];
  
  // Extract from SEO data
  if (page.seo?.keywords) {
    keywords.push(...page.seo.keywords);
  }
  
  // Extract from title and description
  const titleWords = page.title.toLowerCase().split(/\s+/).filter(word => word.length > 3);
  const descWords = page.meta_description.toLowerCase().split(/\s+/).filter(word => word.length > 3);
  
  keywords.push(...titleWords.slice(0, 3));
  keywords.push(...descWords.slice(0, 2));
  
  // Remove duplicates and return
  return [...new Set(keywords)];
}

/**
 * Count words in text
 */
function countWords(text: string): number {
  return text.trim().split(/\s+/).filter(word => word.length > 0).length;
}

/**
 * Write SEO pages module
 */
async function writeSEOPagesModule(seoPages: Record<string, SEOPageData>, outputDir: string) {
  const moduleContent = `// Auto-generated SEO pages data
// Generated at: ${new Date().toISOString()}
// Do not edit this file manually

export interface SEOPageData {
  title: string;
  meta_description: string;
  content: string;
  keywords: string[];
  canonical_url: string;
  og_type: string;
  word_count: number;
  created_at: string;
}

export const seoPages: Record<string, SEOPageData> = ${JSON.stringify(seoPages, null, 2)};

export function getSEOPageData(urlPath: string): SEOPageData | null {
  return seoPages[urlPath] || null;
}

export function getAllSEOPages(): Record<string, SEOPageData> {
  return seoPages;
}

export function getSEOPagePaths(): string[] {
  return Object.keys(seoPages);
}
`;
  
  const filePath = path.join(outputDir, 'seo-pages.ts');
  await fs.writeFile(filePath, moduleContent, 'utf-8');
  console.log(`📝 Written SEO pages module: ${filePath}`);
}

/**
 * Write route manifest
 */
async function writeRouteManifest(manifest: any, outputDir: string) {
  const filePath = path.join(outputDir, 'route-manifest.json');
  await fs.writeFile(filePath, JSON.stringify(manifest, null, 2), 'utf-8');
  console.log(`📝 Written route manifest: ${filePath}`);
}

/**
 * Write sitemap data
 */
async function writeSitemapData(sitemapData: any, outputDir: string) {
  const filePath = path.join(outputDir, 'sitemap-data.json');
  await fs.writeFile(filePath, JSON.stringify(sitemapData, null, 2), 'utf-8');
  console.log(`📝 Written sitemap data: ${filePath}`);
}

/**
 * Write generation metadata
 */
async function writeMetadata(metadata: any, outputDir: string) {
  const filePath = path.join(outputDir, 'generation-metadata.json');
  await fs.writeFile(filePath, JSON.stringify(metadata, null, 2), 'utf-8');
  console.log(`📝 Written generation metadata: ${filePath}`);
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
    } else if (arg.startsWith('--input=')) {
      options.inputFile = arg.split('=')[1];
    } else if (arg.startsWith('--backend=')) {
      options.backendUrl = arg.split('=')[1];
    } else if (arg.startsWith('--output=')) {
      options.outputDir = arg.split('=')[1];
    }
  }
  
  // Validate options
  if (!options.inputFile && !options.businessId) {
    console.error('❌ Either --input or --businessId must be provided');
    process.exit(1);
  }
  
  if (options.businessId && !options.backendUrl) {
    options.backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
  }
  
  try {
    await generateSEOContent(options);
    console.log('🎉 SEO content generation completed successfully');
  } catch (error) {
    console.error('💥 SEO content generation failed:', error.message);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { generateSEOContent };
