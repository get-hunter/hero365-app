# Multi-Tenant SEO & Deployment System

## 🎯 Overview

This system enables automatic deployment of business-specific websites with dynamic SEO generation. Each business gets their own subdomain with customized sitemaps and robots.txt files.

## 🏗️ Architecture

### **Deployment Patterns**

1. **Subdomain-Based (Recommended)**
   ```
   elite-hvac-austin.hero365.com
   dallas-plumbing-pro.hero365.com
   houston-electrical.hero365.com
   ```

2. **Custom Domain**
   ```
   elitehvacaustin.com
   dallasplumbingpro.com
   houstonelectrical.com
   ```

3. **Path-Based**
   ```
   hero365.com/elite-hvac-austin
   hero365.com/dallas-plumbing-pro
   ```

## 🔧 API Endpoints

### **1. Deployment Configuration**

```bash
GET /api/v1/public/contractors/{business_id}/deployment-config
```

**Response:**
```json
{
  "business_id": "550e8400-e29b-41d4-a716-446655440010",
  "subdomain": "elite-hvac-austin",
  "site_url": "https://elite-hvac-austin.hero365.com",
  "site_name": "Elite HVAC Austin",
  "site_description": "Elite HVAC Austin - Professional home services in Austin",
  "primary_color": "#2563eb",
  "enable_booking": true,
  "enable_products": true,
  "enable_reviews": true
}
```

### **2. Environment Variables**

```bash
GET /api/v1/public/contractors/{business_id}/env-vars?site_url=https://custom-domain.com
```

**Response:**
```json
{
  "NEXT_PUBLIC_BUSINESS_ID": "550e8400-e29b-41d4-a716-446655440010",
  "NEXT_PUBLIC_SITE_URL": "https://elite-hvac-austin.hero365.com",
  "NEXT_PUBLIC_BACKEND_URL": "https://api.hero365.com",
  "NEXT_PUBLIC_BUSINESS_NAME": "Elite HVAC Austin",
  "NEXT_PUBLIC_PRIMARY_COLOR": "#2563eb",
  "NEXT_PUBLIC_ENABLE_BOOKING": "true"
}
```

### **3. Business-Specific Sitemap**

```bash
GET /api/v1/public/contractors/{business_id}/sitemap.xml?base_url=https://elite-hvac-austin.hero365.com
```

**Generated Sitemap:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Business: Elite HVAC Austin -->
  
  <!-- Homepage -->
  <url>
    <loc>https://elite-hvac-austin.hero365.com</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  
  <!-- Hub Pages -->
  <url>
    <loc>https://elite-hvac-austin.hero365.com/services</loc>
    <priority>0.9</priority>
  </url>
  
  <!-- Service + Location Pages -->
  <url>
    <loc>https://elite-hvac-austin.hero365.com/services/ac-repair/austin-tx</loc>
    <priority>0.7</priority>
  </url>
  <!-- ... 144+ service/location combinations ... -->
</urlset>
```

### **4. Business-Specific Robots.txt**

```bash
GET /api/v1/public/contractors/{business_id}/robots.txt?base_url=https://elite-hvac-austin.hero365.com
```

**Generated Robots.txt:**
```
User-Agent: *
Allow: /
Disallow: /api/
Disallow: /admin/

# Business: Elite HVAC Austin
Sitemap: https://elite-hvac-austin.hero365.com/sitemap.xml
```

## 🚀 Deployment Workflow

### **Step 1: Get Deployment Config**
```bash
curl "https://api.hero365.com/api/v1/public/contractors/550e8400-e29b-41d4-a716-446655440010/deployment-config"
```

### **Step 2: Get Environment Variables**
```bash
curl "https://api.hero365.com/api/v1/public/contractors/550e8400-e29b-41d4-a716-446655440010/env-vars?site_url=https://elite-hvac-austin.hero365.com"
```

### **Step 3: Deploy with Platform**

#### **Vercel Deployment**
```bash
# Set environment variables
vercel env add NEXT_PUBLIC_BUSINESS_ID 550e8400-e29b-41d4-a716-446655440010
vercel env add NEXT_PUBLIC_SITE_URL https://elite-hvac-austin.hero365.com
vercel env add NEXT_PUBLIC_BACKEND_URL https://api.hero365.com

# Deploy
vercel --prod
```

#### **Netlify Deployment**
```bash
# netlify.toml
[build.environment]
  NEXT_PUBLIC_BUSINESS_ID = "550e8400-e29b-41d4-a716-446655440010"
  NEXT_PUBLIC_SITE_URL = "https://elite-hvac-austin.hero365.com"
  NEXT_PUBLIC_BACKEND_URL = "https://api.hero365.com"
```

### **Step 4: Configure DNS**
```bash
# Subdomain CNAME
elite-hvac-austin.hero365.com → vercel-deployment.vercel.app

# Custom Domain A Record  
elitehvacaustin.com → 76.76.19.61
```

## 🔄 Dynamic SEO Generation

### **Frontend Integration**

The Next.js app automatically generates SEO files using the business ID:

```typescript
// app/sitemap.ts
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const businessId = process.env.NEXT_PUBLIC_BUSINESS_ID
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL
  
  // Fetch from business-specific API
  const response = await fetch(
    `${backendUrl}/api/v1/public/contractors/${businessId}/sitemap.xml?base_url=${siteUrl}`
  )
  
  return parseSitemapResponse(response)
}
```

```typescript
// app/robots.ts
export default function robots(): MetadataRoute.Robots {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL
  
  return {
    rules: [{ userAgent: '*', allow: '/' }],
    sitemap: `${siteUrl}/sitemap.xml`,
  }
}
```

## 📊 Scaling Strategy

### **Automated Deployment Pipeline**

1. **Business Registration** → Trigger deployment
2. **Content Updates** → Regenerate sitemap
3. **Service Changes** → Update SEO pages
4. **Location Expansion** → Add new URLs

### **Performance Optimization**

- **CDN Distribution**: Cloudflare/AWS CloudFront
- **Edge Caching**: 1-hour sitemap cache, 24-hour robots.txt
- **ISR (Incremental Static Regeneration)**: Update pages on-demand
- **Parallel Builds**: Deploy multiple businesses simultaneously

### **Monitoring & Analytics**

- **Deployment Status**: Track build success/failure
- **SEO Performance**: Monitor Google Search Console
- **Site Health**: Uptime monitoring per subdomain
- **Traffic Analytics**: Business-specific Google Analytics

## 🛠️ Implementation Examples

### **Bulk Deployment Script**
```bash
#!/bin/bash
# Deploy multiple businesses

BUSINESSES=("550e8400-e29b-41d4-a716-446655440010" "another-business-id")

for business_id in "${BUSINESSES[@]}"; do
  echo "Deploying $business_id..."
  
  # Get config
  config=$(curl -s "https://api.hero365.com/api/v1/public/contractors/$business_id/deployment-config")
  subdomain=$(echo $config | jq -r '.subdomain')
  
  # Deploy to Vercel
  vercel --prod --env NEXT_PUBLIC_BUSINESS_ID=$business_id
  
  echo "✅ Deployed: https://$subdomain.hero365.com"
done
```

### **Webhook Integration**
```python
# Auto-deploy when business data changes
@app.post("/webhooks/business-updated")
async def business_updated(business_id: str):
    # Trigger redeployment
    deployment_config = await get_deployment_config(business_id)
    
    # Call deployment platform API
    await trigger_vercel_deployment(
        business_id=business_id,
        env_vars=deployment_config.env_vars
    )
```

## 🔍 SEO Benefits

### **Per-Business Optimization**
- ✅ Unique sitemaps with business-specific URLs
- ✅ Custom robots.txt with proper sitemap references  
- ✅ Business name in meta tags and structured data
- ✅ Location-specific landing pages
- ✅ Service-specific SEO optimization

### **Scalable Discovery**
- ✅ Google discovers 144+ pages per business automatically
- ✅ Internal linking structure for crawl efficiency
- ✅ Hub pages for topical authority
- ✅ Cross-linking between services and locations

### **Multi-Tenant Benefits**
- ✅ Isolated SEO performance per business
- ✅ Custom domain support for brand authority
- ✅ Independent analytics and monitoring
- ✅ Scalable to thousands of businesses

## 📈 Next Steps

1. **Integrate with Deployment Platform** (Vercel/Netlify API)
2. **Add Custom Domain Management** 
3. **Implement Automated SSL Certificate Generation**
4. **Build Business Dashboard** for deployment management
5. **Add SEO Performance Monitoring**
6. **Implement A/B Testing** for conversion optimization

This system provides a complete foundation for scaling SEO-optimized websites across multiple businesses while maintaining performance and discoverability.
