# 🚀 Deployment Scripts

This directory contains scripts for deploying the Hero365 website builder to Cloudflare Pages.

## 📁 Files

### `deploy-to-cloudflare.js`
**Node.js deployment script** with comprehensive error handling and validation.

**Features:**
- ✅ Prerequisites checking (Wrangler CLI, authentication)
- ✅ Build output validation
- ✅ Project management (create/update Cloudflare Pages projects)
- ✅ Production and preview deployments
- ✅ Deployment status tracking
- ✅ Verbose logging options

**Usage:**
```bash
node scripts/deploy-to-cloudflare.js [options]
# or
npm run deploy
npm run deploy:preview
npm run deploy:verbose
```

### `build-and-deploy.sh`
**Bash script** for complete build and deployment pipeline.

**Features:**
- ✅ Dependency installation
- ✅ Next.js build process
- ✅ Build output validation
- ✅ Cloudflare Pages deployment
- ✅ Status reporting
- ✅ Error handling with colored output

**Usage:**
```bash
./scripts/build-and-deploy.sh [options]
# or
npm run build-and-deploy
npm run build-and-deploy:preview
```

### `test-deployment.js`
**Testing script** that validates deployment readiness without actually deploying.

**Features:**
- ✅ Build validation
- ✅ File structure analysis
- ✅ HTML content verification
- ✅ Critical files checking
- ✅ Deployment simulation

**Usage:**
```bash
node scripts/test-deployment.js
# or
npm run test-deployment
```

## 🎯 Quick Start

### 1. First Time Setup
```bash
# Install Wrangler CLI globally
npm install -g wrangler

# Authenticate with Cloudflare
wrangler login

# Test deployment readiness
npm run test-deployment
```

### 2. Deploy to Production
```bash
# Option A: All-in-one (recommended)
npm run build-and-deploy

# Option B: Step by step
npm run build
npm run deploy
```

### 3. Deploy Preview
```bash
# Option A: All-in-one
npm run build-and-deploy:preview

# Option B: Step by step
npm run build
npm run deploy:preview
```

## 🛠️ Script Options

### Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--preview` | Deploy as preview branch | `--preview` |
| `--verbose` | Enable detailed logging | `--verbose` |
| `--project-name` | Custom project name | `--project-name my-site` |
| `--skip-build` | Skip build step (bash only) | `--skip-build` |
| `--help` | Show help message | `--help` |

### Examples

```bash
# Deploy with custom project name
npm run deploy -- --project-name hero365-custom

# Deploy preview with verbose output
npm run deploy:preview -- --verbose

# Build and deploy with custom settings
./scripts/build-and-deploy.sh --project-name custom-site --preview --verbose

# Deploy existing build as preview
./scripts/build-and-deploy.sh --skip-build --preview

# Test deployment without actually deploying
npm run test-deployment
```

## 📊 Output Examples

### Successful Deployment
```
🚀 Starting Cloudflare Pages deployment...

✅ All prerequisites met
✅ Build output validation passed
✅ Project 'hero365-professional' already exists
✅ Deployment successful!
✅ URL: https://hero365-professional.pages.dev

🎉 Deployment completed successfully!
📍 URL: https://hero365-professional.pages.dev
🔗 Project: https://dash.cloudflare.com/pages/view/hero365-professional
📊 Status: success
⏰ Created: 8/25/2025, 3:28:00 PM
```

### Test Results
```
🧪 Testing Cloudflare Pages deployment process...

✅ Build validation passed
✅ All critical files present
✅ HTML content looks good
✅ Ready for actual deployment

Total files: 74
HTML size: 188.6 KB
```

## 🔧 Configuration

### Environment Variables
Set these in your environment or CI/CD:
```bash
CLOUDFLARE_API_TOKEN=your_api_token
CLOUDFLARE_ACCOUNT_ID=your_account_id
```

### Project Settings
Default project name: `hero365-professional`

To use a different project name:
```bash
# Via command line
npm run deploy -- --project-name my-custom-site

# Via environment variable
export CF_PROJECT_NAME=my-custom-site
npm run deploy
```

## 🚨 Troubleshooting

### Common Issues

1. **Wrangler not found**
   ```bash
   npm install -g wrangler
   ```

2. **Not authenticated**
   ```bash
   wrangler login
   ```

3. **Build fails**
   ```bash
   rm -rf .next out node_modules
   npm install
   npm run build
   ```

4. **Deployment fails**
   ```bash
   # Check wrangler version
   wrangler --version
   
   # Update if needed
   npm install -g wrangler@latest
   ```

### Debug Commands
```bash
# Test deployment readiness
npm run test-deployment

# Deploy with verbose output
npm run deploy:verbose

# Check build output
ls -la out/
ls -la out/templates/professional/

# Validate HTML
npm run test-deployment
```

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
- name: Deploy to Cloudflare Pages
  run: |
    npm install -g wrangler
    cd website-builder
    npm install
    npm run build-and-deploy
  env:
    CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

### GitLab CI
```yaml
deploy:
  script:
    - npm install -g wrangler
    - cd website-builder
    - npm install
    - npm run build-and-deploy
  variables:
    CLOUDFLARE_API_TOKEN: $CLOUDFLARE_API_TOKEN
```

## 📈 Performance

### Build Times
- **Clean build**: ~30-60 seconds
- **Incremental build**: ~10-20 seconds
- **Deployment**: ~30-60 seconds

### Optimization
- Static export for fast CDN delivery
- Automatic asset optimization
- Gzip compression enabled
- Cache headers configured

## 📞 Support

For deployment issues:
1. Run `npm run test-deployment` first
2. Check deployment logs with `--verbose`
3. Verify Wrangler authentication
4. Check Cloudflare dashboard for errors

---

**Happy Deploying! 🎉**
