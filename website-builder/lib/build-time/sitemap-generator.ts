/**
 * Sitemap and Robots.txt Generator
 * 
 * Generates sitemap.xml and robots.txt from the generated content
 */

import fs from 'fs/promises';
import path from 'path';

interface SitemapUrl {
  loc: string;
  lastmod: string;
  changefreq: string;
  priority: number;
}

interface SitemapData {
  generated_at: string;
  business_id: string;
  urls: SitemapUrl[];
}

/**
 * Generate sitemap.xml content
 */
export function generateSitemapXML(sitemapData: SitemapData, baseUrl: string): string {
  const urls = sitemapData.urls.map(url => `
  <url>
    <loc>${baseUrl}${url.loc}</loc>
    <lastmod>${url.lastmod}</lastmod>
    <changefreq>${url.changefreq}</changefreq>
    <priority>${url.priority.toFixed(1)}</priority>
  </url>`).join('');

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Generated at: ${sitemapData.generated_at} -->
  <!-- Business ID: ${sitemapData.business_id} -->${urls}
</urlset>`;
}

/**
 * Generate robots.txt content
 */
export function generateRobotsTxt(baseUrl: string, businessName: string): string {
  return `# Robots.txt for ${businessName}
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
}

/**
 * Write sitemap and robots files to public directory
 */
export async function writeSitemapFiles(
  sitemapData: SitemapData, 
  baseUrl: string, 
  businessName: string,
  publicDir: string
) {
  try {
    // Generate content
    const sitemapXML = generateSitemapXML(sitemapData, baseUrl);
    const robotsTxt = generateRobotsTxt(baseUrl, businessName);
    
    // Write files
    await Promise.all([
      fs.writeFile(path.join(publicDir, 'sitemap.xml'), sitemapXML, 'utf-8'),
      fs.writeFile(path.join(publicDir, 'robots.txt'), robotsTxt, 'utf-8')
    ]);
    
    console.log('✅ Generated sitemap.xml and robots.txt');
    return true;
  } catch (error) {
    console.error('❌ Failed to write sitemap files:', error.message);
    return false;
  }
}

/**
 * Load sitemap data from generated content
 */
export async function loadSitemapData(generatedDir: string): Promise<SitemapData | null> {
  try {
    const sitemapDataPath = path.join(generatedDir, 'sitemap-data.json');
    const content = await fs.readFile(sitemapDataPath, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.warn('⚠️ Could not load sitemap data:', error.message);
    return null;
  }
}
