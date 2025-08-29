# Deployment Scripts

## 🚀 Production Deployment (Recommended)

For production deployments with business configuration:

```bash
# Deploy to production with business ID
node scripts/deploy-with-business.js --businessId=your-business-id --env=production

# Deploy to staging for testing
node scripts/deploy-with-business.js --businessId=your-business-id --env=staging

# Build only (no deployment)
node scripts/deploy-with-business.js --businessId=your-business-id --env=production --build-only
```

### Production Script Features
- ✅ Environment-aware (dev/staging/production)
- ✅ Business configuration management
- ✅ Fetches real business data from API
- ✅ SSR-compatible environment setup
- ✅ Custom domain support
- ✅ Comprehensive error handling
- ✅ Verbose logging option

### Production Usage Examples

```bash
# Production deployment with custom domain
node scripts/deploy-with-business.js \
  --businessId=abc123 \
  --env=production \
  --domain=elitehvac.com

# Staging with custom project name  
node scripts/deploy-with-business.js \
  --businessId=abc123 \
  --env=staging \
  --project=elite-hvac-staging \
  --verbose

# Build and test locally
node scripts/deploy-with-business.js \
  --businessId=abc123 \
  --env=development \
  --build-only
```

## 🛠 Development Testing (Quick & Dirty)

For quick development testing with ngrok:

```bash
# Quick development deployment
./scripts/deploy-cloudflare.sh

# With custom business ID
./scripts/deploy-cloudflare.sh -b "your-business-id"
```

### Development Prerequisites

1. **Backend server running**:
   ```bash
   cd backend
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **ngrok tunnel active**:
   ```bash
   ngrok http 8000
   ```

⚠️ **Note**: The shell script is for development testing only. Use the Node.js script for production.

## 📝 Environment Variables

### Production Deployment
```bash
# Set via deployment script or environment
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_API_URL=https://api.hero365.ai
NEXT_PUBLIC_BUSINESS_ID=your-business-id
```

### Development Testing  
```bash
# Auto-detected or set manually
NGROK_PUBLIC_URL=https://your-tunnel.ngrok-free.app
NEXT_PUBLIC_BUSINESS_ID=your-business-id
```

## 🔧 Utility Scripts

- **`set-ngrok-env.mjs`** - Automatically sets ngrok URL in environment
- **`test-deployment.js`** - Tests deployment after completion

## 📚 Migration Guide

If you were using the old shell script:

```bash
# OLD (development only):
./scripts/deploy-cloudflare.sh -b business-id

# NEW (production ready):
node scripts/deploy-with-business.js --businessId=business-id --env=production
```

## 🐛 Troubleshooting

### Production Deployment Issues
```bash
# Check API connectivity
curl "https://api.hero365.ai/api/v1/public/contractors/profile/your-business-id"

# Test with staging first
node scripts/deploy-with-business.js --businessId=your-business-id --env=staging
```

### Development Issues
```bash
# Check ngrok is running
curl "http://127.0.0.1:4040/api/tunnels"

# Test backend connectivity  
curl "https://your-tunnel.ngrok-free.app/api/v1/public/contractors/profile/business-id"
```

## 🏆 Best Practices

1. **Use production script** for all staging/production deployments
2. **Test with staging** before production deployment  
3. **Use build-only mode** for local testing
4. **Set environment variables** explicitly rather than relying on defaults
5. **Use verbose mode** for debugging deployment issues