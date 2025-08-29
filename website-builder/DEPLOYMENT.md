# 🚀 Hero365 Deployment Guide

## Quick Start

```bash
# Production deployment (recommended)
npm run deploy:production --businessId=your-business-id

# Or with explicit script
node scripts/deploy-with-business.js --businessId=your-business-id --env=production
```

## 📋 Available Scripts

| Command | Purpose | Environment |
|---------|---------|-------------|
| `npm run deploy` | Default deployment | Development |
| `npm run deploy:production` | Production deployment | Production |
| `npm run deploy:staging` | Staging deployment | Staging |
| `npm run deploy:dev` | Quick dev deployment (ngrok) | Development |
| `npm run deploy:help` | Show help and options | N/A |

## 🛠 Script Overview

### ✅ `deploy-with-business.js` (Primary)
**Production-ready deployment with business configuration**

Features:
- Environment management (dev/staging/production)
- Business ID configuration and data fetching
- SSR-compatible environment variables
- Custom domain support
- Comprehensive error handling

```bash
# Full example
node scripts/deploy-with-business.js \
  --businessId=abc-123 \
  --env=production \
  --project=elite-hvac \
  --domain=elitehvac.com \
  --verbose
```

### 🧪 `deploy-cloudflare.sh` (Development)
**Quick testing with ngrok (development only)**

Features:
- Rapid development testing
- Automatic ngrok URL detection
- Simple backend connectivity testing

```bash
# Quick test deployment
./scripts/deploy-cloudflare.sh -b "your-business-id"
```

## 🌍 Environment Configuration

### Production
- API URL: `https://api.hero365.ai`
- Auto-fetches real business data
- Sets `NODE_ENV=production`

### Staging  
- API URL: `https://api-staging.hero365.ai`
- Testing environment
- Sets `NODE_ENV=production`

### Development
- API URL: `http://localhost:8000` or ngrok URL
- Local backend required
- Sets `NODE_ENV=development`

## 💡 Best Practices

1. **Always specify business ID**: `--businessId=your-actual-business-id`
2. **Test in staging first**: `npm run deploy:staging --businessId=...`
3. **Use verbose mode for debugging**: `--verbose`
4. **Build-only for testing**: `--build-only`

## 🐛 Common Issues

### "Business ID not found"
```bash
# Test API connectivity first
curl "https://api.hero365.ai/api/v1/public/contractors/profile/your-business-id"
```

### "Environment variable missing"  
```bash
# Ensure you're passing the business ID
node scripts/deploy-with-business.js --businessId=REQUIRED --env=production
```

### "Build failed"
```bash
# Check for TypeScript/lint errors
npm run lint
```

## 📁 File Structure (Cleaned Up)

```
scripts/
├── deploy-with-business.js     # ✅ Main production deployment
├── deploy-cloudflare.sh        # 🧪 Development testing  
├── set-ngrok-env.mjs          # 🛠 Utility: Set ngrok URL
├── test-deployment.js         # 🛠 Utility: Test deployment
└── README.md                  # 📚 Detailed documentation
```

## 🔄 Migration from Old Scripts

If you were using old scripts:

```bash
# OLD (removed):
# ./scripts/deploy.js
# ./scripts/deploy-to-cloudflare.js

# NEW:
node scripts/deploy-with-business.js --businessId=... --env=production
```

## 🎯 Next Steps

After deployment:
1. ✅ Test the deployed website
2. ✅ Verify projects load correctly on home page  
3. ✅ Check all API endpoints work
4. ✅ Test mobile responsiveness
5. ✅ Verify business data is correct
