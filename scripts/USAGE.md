# 🚀 Hero365 Deployment System - Usage Guide

## Quick Start

We've completely redesigned the deployment system for simplicity and performance. Use these **2 unified scripts** for all your deployment needs:

### **🏗️ Production Deployment**
```bash
# Deploy any business to Cloudflare
./scripts/build-static-website.sh \
  --business-id YOUR_BUSINESS_ID \
  --environment production
```

### **🛠️ Development Environment**
```bash
# Start development with static data (no API spam!)
./scripts/dev-with-static-data.sh \
  --business-id YOUR_BUSINESS_ID
```

## ✨ What's New

### **🧹 Legacy Cleanup**
- ❌ Removed **6 legacy scripts** that caused confusion
- ❌ Eliminated **API spam** and logging noise
- ❌ No more complex interactive prompts
- ✅ **2 clean, focused scripts** with clear purposes

### **⚡ Performance Improvements**
- **Static generation** instead of runtime API calls
- **30-60 second builds** instead of 2-5 minutes
- **Clean logs** with meaningful messages only
- **Zero API dependencies** for static content

## 📋 Usage Examples

### **1. Development**
```bash
# Full development environment
./scripts/dev-with-static-data.sh --business-id 550e8400-e29b-41d4-a716-446655440010

# Frontend only (no backend)
./scripts/dev-with-static-data.sh --business-id YOUR_ID --no-backend

# Skip static generation (use existing)
./scripts/dev-with-static-data.sh --business-id YOUR_ID --no-static
```

### **2. Build & Deploy**
```bash
# Build only (no deployment)
./scripts/build-static-website.sh --business-id YOUR_ID --build-only

# Deploy to development
./scripts/build-static-website.sh --business-id YOUR_ID --environment development

# Deploy to production with custom project name
./scripts/build-static-website.sh \
  --business-id YOUR_ID \
  --environment production \
  --project-name elite-hvac-austin
```

## 🎯 Business-Specific Deployment

Each business gets its own Cloudflare project and URL:

```bash
Business ID: 550e8400-e29b-41d4-a716-446655440010
Environment: production
↓
Project: hero365-550e8400-e29b-41d4-a716-446655440010-production
URL: https://hero365-550e8400-e29b-41d4-a716-446655440010-production.pages.dev
```

## 🔧 Configuration

### **Required Environment Variables**
```bash
# For Cloudflare deployment
export CLOUDFLARE_API_TOKEN="your-cloudflare-api-token"
export CLOUDFLARE_ACCOUNT_ID="your-account-id"  # optional
```

### **Business Configuration**
```bash
# Business-specific settings (optional - has fallbacks)
export NEXT_PUBLIC_BUSINESS_NAME="Elite HVAC Austin"
export NEXT_PUBLIC_BUSINESS_PHONE="(512) 555-0100"
export NEXT_PUBLIC_BUSINESS_EMAIL="info@elitehvac.com"
```

## 📊 Example Session

```bash
$ ./scripts/build-static-website.sh --business-id 550e8400-e29b-41d4-a716-446655440010 --environment production

🏗️ Unified Static Website Builder

🚀 Starting static website build...
Business ID: 550e8400-e29b-41d4-a716-446655440010
Environment: production
Cloud Provider: cloudflare
Cloudflare Project: hero365-550e8400-e29b-41d4-a716-446655440010-production
Build only: false

🔍 Checking backend health...
✅ Backend is healthy at http://localhost:8000

📊 Generating static data...
✅ Static data generated successfully

🏗️ Building Next.js application...
✅ Next.js build completed successfully

🚀 Deploying to Cloudflare Pages...
✅ Deployment completed successfully
🌐 Website URL: https://hero365-550e8400-e29b-41d4-a716-446655440010-production.pages.dev

✅ Validating deployment...
✅ Generated 1247 static files

🎉 Build completed! Next steps:
   🌐 Website deployed successfully!
   🔗 URL: https://hero365-550e8400-e29b-41d4-a716-446655440010-production.pages.dev
   📊 Monitor in Cloudflare dashboard: https://dash.cloudflare.com/
   📋 Project: hero365-550e8400-e29b-41d4-a716-446655440010-production

🎯 All done!
```

## 🆘 Help & Troubleshooting

### **Get Help**
```bash
./scripts/build-static-website.sh --help
./scripts/dev-with-static-data.sh --help
```

### **Common Issues**

**1. Missing Business ID**
```bash
❌ Business ID is required
✅ Use: --business-id YOUR_BUSINESS_ID
```

**2. Cloudflare Authentication**
```bash
❌ Cloudflare deployment failed
✅ Set: export CLOUDFLARE_API_TOKEN="your-token"
```

**3. Build Failures**
```bash
❌ Next.js build failed
✅ Check: npm install in website-builder/
```

## 🎉 Migration from Legacy Scripts

### **Old Way (Deprecated)**
```bash
# Don't use these anymore - they've been removed
./scripts/deploy-seo-matrix.sh
./scripts/interactive-website-deployer.py
./website-builder/scripts/prebuild-seo.js
```

### **New Way (Use This)**
```bash
# Simple, clean, fast
./scripts/build-static-website.sh --business-id YOUR_ID --environment production
```

---

## 📚 Additional Resources

- **Legacy Cleanup Plan**: `docs/LEGACY-CODE-CLEANUP-PLAN.md`
- **Unified Deployment System**: `docs/UNIFIED-DEPLOYMENT-SYSTEM.md`
- **Static Data Generator**: `website-builder/lib/server/static-data-generator.ts`

The new system is **faster**, **cleaner**, and **more reliable** than the legacy approach!
