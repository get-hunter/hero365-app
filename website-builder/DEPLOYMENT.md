# 🚀 Cloudflare Pages Deployment Guide

This guide explains how to deploy the Hero365 website builder to Cloudflare Pages.

## 📋 Prerequisites

1. **Wrangler CLI** installed globally:
   ```bash
   npm install -g wrangler
   ```

2. **Cloudflare account** and authentication:
   ```bash
   wrangler login
   ```

3. **Built website** (or the script will build it for you):
   ```bash
   npm run build
   ```

## 🎯 Quick Deployment

### Option 1: All-in-One Script (Recommended)
```bash
# Build and deploy to production
npm run build-and-deploy

# Build and deploy as preview
npm run build-and-deploy:preview

# With verbose output
./scripts/build-and-deploy.sh --verbose

# Skip build (use existing out/ directory)
./scripts/build-and-deploy.sh --skip-build --preview
```

### Option 2: Deploy Only (Build Separately)
```bash
# Build first
npm run build

# Deploy to production
npm run deploy

# Deploy as preview
npm run deploy:preview

# Deploy with verbose logging
npm run deploy:verbose
```

### Option 3: Direct Wrangler Commands
```bash
# Build first
npm run build

# Deploy directly with wrangler
npm run cf:deploy

# Deploy as preview
npm run cf:deploy:preview
```

## 🛠️ Script Options

### JavaScript Deployment Script
```bash
node scripts/deploy-to-cloudflare.js [options]

Options:
  --preview              Deploy as preview (not production)
  --verbose, -v          Verbose logging
  --project-name <name>  Cloudflare Pages project name
  --output-dir <dir>     Build output directory
  --help, -h             Show help message
```

### Bash Deployment Script
```bash
./scripts/build-and-deploy.sh [options]

Options:
  -p, --preview          Deploy as preview (not production)
  -n, --project-name     Cloudflare Pages project name
  -v, --verbose          Enable verbose output
  -s, --skip-build       Skip the build step
  -h, --help             Show help message
```

## 📁 Project Structure

The deployment creates the following structure on Cloudflare Pages:

```
hero365-professional/
├── index.html                    # Main homepage
├── templates/
│   └── professional/
│       └── index.html           # Professional template
├── about/
│   └── index.html               # About page
├── services/
│   └── index.html               # Services page
├── contact/
│   └── index.html               # Contact page
├── _next/                       # Next.js assets
│   ├── static/
│   └── chunks/
└── favicon.ico
```

## 🌐 Deployment URLs

### Production Deployment
- **URL Pattern**: `https://hero365-professional.pages.dev`
- **Custom Domain**: Configure in Cloudflare dashboard

### Preview Deployments
- **URL Pattern**: `https://<branch-name>.hero365-professional.pages.dev`
- **Branch Naming**: `preview-YYYYMMDD-HHMMSS`

## 📊 Monitoring & Management

### Cloudflare Dashboard
- **Project URL**: `https://dash.cloudflare.com/pages/view/hero365-professional`
- **Deployments**: View all deployments and their status
- **Analytics**: Traffic and performance metrics
- **Settings**: Custom domains, environment variables

### CLI Status Commands
```bash
# List all deployments
wrangler pages deployment list --project-name hero365-professional

# Get project info
wrangler pages project list

# View deployment logs
wrangler pages deployment tail --project-name hero365-professional
```

## 🔧 Configuration

### Environment Variables
Set in Cloudflare dashboard under **Settings > Environment Variables**:
- `NODE_ENV=production`
- `NEXT_PUBLIC_API_URL=https://api.hero365.com`

### Custom Domain
1. Go to **Custom domains** in Cloudflare dashboard
2. Add your domain (e.g., `professional.hero365.com`)
3. Update DNS records as instructed

### Build Settings
- **Build command**: `npm run build`
- **Build output directory**: `out`
- **Root directory**: `/website-builder`

## 🚨 Troubleshooting

### Common Issues

1. **Wrangler not authenticated**
   ```bash
   wrangler login
   ```

2. **Build fails**
   ```bash
   # Check for TypeScript errors
   npm run build
   
   # Clear cache and rebuild
   rm -rf .next out node_modules
   npm install
   npm run build
   ```

3. **Deployment fails**
   ```bash
   # Check wrangler version
   wrangler --version
   
   # Update wrangler
   npm install -g wrangler@latest
   ```

4. **Missing files in deployment**
   - Ensure `next.config.ts` has `output: 'export'`
   - Check that all required files are in `out/` directory
   - Verify build completed successfully

### Debug Mode
```bash
# Run with maximum verbosity
DEBUG=* npm run deploy:verbose

# Check build output
ls -la out/
ls -la out/templates/professional/
```

## 📈 Performance Optimization

### Lighthouse Scores
The deployment automatically optimizes for:
- **Performance**: Static files, CDN delivery
- **SEO**: Meta tags, structured data
- **Accessibility**: Semantic HTML, ARIA labels
- **Best Practices**: Security headers, HTTPS

### Caching
Cloudflare automatically handles:
- **Static assets**: Long-term caching
- **HTML files**: Short-term caching with purge on deploy
- **API responses**: Configurable caching rules

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy to Cloudflare Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build
      - run: npx wrangler pages deploy out --project-name hero365-professional
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

## 📞 Support

For deployment issues:
1. Check the [Cloudflare Pages documentation](https://developers.cloudflare.com/pages/)
2. Review deployment logs in the Cloudflare dashboard
3. Run deployment with `--verbose` flag for detailed output
4. Check the [Wrangler CLI documentation](https://developers.cloudflare.com/workers/wrangler/)

---

**Happy Deploying! 🎉**
