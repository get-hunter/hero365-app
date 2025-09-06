# Deployment Scripts

This directory contains scripts to ensure reliable deployments to Cloudflare Workers without stale code issues.

## Problem Solved

Previously, deployments would sometimes serve old code due to:
- Cloudflare edge caching of HTML responses
- Worker versions not being properly pinned to routes
- No cache invalidation after deployments

## Solution

The `deploy-with-cache-bust.js` script automates:

1. **Build Process**: Runs `npm run build` and `npx opennextjs-cloudflare build`
2. **Deployment**: Deploys to Cloudflare Workers
3. **Version Pinning**: Automatically pins routes to the latest worker version
4. **Cache Purging**: Purges Cloudflare cache to ensure fresh content
5. **Testing**: Verifies the deployment is working correctly

## Usage

### Quick Deploy (Staging)
```bash
npm run deploy
# or
npm run deploy:staging
```

### Production Deploy
```bash
npm run deploy:production
```

### Legacy Deploy (without cache busting)
```bash
npm run deploy:legacy:staging
npm run deploy:legacy:production
```

## Environment Variables

### Required for Cache Purging
Set `CLOUDFLARE_API_TOKEN` to enable automatic cache purging:

```bash
export CLOUDFLARE_API_TOKEN="your-token-here"
```

**Token Permissions Required:**
- Zone:Zone Settings:Read
- Zone:Zone:Read  
- Zone:Cache Purge:Edit

### Optional Environment Variables
- `NEXT_PUBLIC_API_URL`: Backend API URL (set in wrangler.toml)
- `NEXT_PUBLIC_BUSINESS_ID`: Business ID for staging

## Files

### `deploy-with-cache-bust.js`
Main deployment script with full automation:
- Node.js script for cross-platform compatibility
- Handles version pinning and cache purging
- Tests deployment after completion
- Provides detailed logging and error handling

### `deploy-with-cache-bust.sh`
Bash version of the deployment script:
- Uses curl and jq for API calls
- Suitable for CI/CD environments with bash

## Cache Control

The deployment process also includes middleware changes to prevent HTML caching:

### Middleware Headers
- `Cache-Control: no-store, no-cache, must-revalidate, proxy-revalidate`
- `Pragma: no-cache`
- `Expires: 0`
- `Surrogate-Control: no-store`

### Next.js Configuration
- `export const dynamic = 'force-dynamic'`
- `export const revalidate = 0`

## Troubleshooting

### Still Seeing Old Code?
1. Check worker versions: `npx wrangler versions list --env staging`
2. Check current deployment: Look for versions with 100% traffic
3. Manually purge cache in Cloudflare Dashboard
4. Verify CLOUDFLARE_API_TOKEN is set correctly

### Deployment Fails?
1. Check if wrangler is authenticated: `npx wrangler whoami`
2. Verify zone ID in script matches your Cloudflare zone
3. Check build process: `npm run build && npx opennextjs-cloudflare build`

### Backend Connectivity Issues?
1. Check ngrok tunnel is running: `curl https://5ab8f8ec32f1.ngrok-free.app/health`
2. Verify wrangler.toml has correct NEXT_PUBLIC_API_URL
3. Test debug endpoint: `curl https://elite-hvac-austin.tradesites.app/api/debug/home`

## Manual Commands

If you need to run steps manually:

```bash
# Build
npm run build
npx opennextjs-cloudflare build

# Deploy
npx wrangler deploy --env staging

# Get latest version
npx wrangler versions list --env staging --json

# Deploy 100% traffic to specific version
npx wrangler versions deploy VERSION_ID@100 --env staging --yes

# Purge cache (requires CLOUDFLARE_API_TOKEN)
curl -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/purge_cache" \
     -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"purge_everything":true}'
```

## Best Practices

1. **Always use the deployment scripts** instead of `wrangler deploy` directly
2. **Set CLOUDFLARE_API_TOKEN** for automatic cache purging
3. **Test after deployment** using the provided URLs
4. **Monitor worker versions** to ensure routes are pinned correctly
5. **Keep ngrok tunnel running** for staging deployments
