# Deployment Scripts

## Cloudflare Pages Deployment

### Quick Start

```bash
# Deploy with defaults (Austin Elite Home Services)
npm run deploy

# Or run the script directly
./scripts/deploy-cloudflare.sh
```

### Prerequisites

1. **Backend server running**:
   ```bash
   cd backend
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **ngrok tunnel active**:
   ```bash
   ngrok http 8000
   ```

3. **Cloudflare API token** (optional, will prompt for login if not set):
   ```bash
   export CLOUDFLARE_API_TOKEN="your-token-here"
   # Or add to website-builder/.env.local
   ```

### Usage Options

```bash
# Show help
npm run deploy:help

# Deploy for specific business
./scripts/deploy-cloudflare.sh -b "custom-business-id"

# Use specific ngrok URL
./scripts/deploy-cloudflare.sh -u "https://abc123.ngrok-free.app"

# Deploy to different Cloudflare project
./scripts/deploy-cloudflare.sh -p "my-custom-project"

# Combine options
./scripts/deploy-cloudflare.sh -b "business-123" -u "https://xyz.ngrok-free.app"
```

### Environment Variables

The script supports these environment variables:

- `NGROK_PUBLIC_URL` - ngrok tunnel URL (auto-detected if not set)
- `NEXT_PUBLIC_BUSINESS_ID` - Business ID for the website
- `CLOUDFLARE_API_TOKEN` - Cloudflare API token for deployment

### What the Script Does

1. ✅ **Checks dependencies** (npm, npx, curl)
2. ✅ **Gets ngrok URL** (from env var or API)
3. ✅ **Tests backend connectivity** (ensures API is working)
4. ✅ **Builds website with SSR** (loads real data during build)
5. ✅ **Deploys to Cloudflare Pages** (using wrangler)
6. ✅ **Shows deployment URL** (ready to test)

### Troubleshooting

**Error: "Could not get ngrok URL"**
- Ensure ngrok is running: `ngrok http 8000`
- Or set manually: `export NGROK_PUBLIC_URL="https://your-url.ngrok-free.app"`

**Error: "Backend test failed"**
- Check backend is running on port 8000
- Verify business ID exists in database
- Test manually: `curl "https://your-ngrok-url.ngrok-free.app/api/v1/public/contractors/profile/business-id"`

**Error: "Website build failed"**
- Check for TypeScript errors
- Ensure all dependencies are installed: `npm install`

**Error: "Deployment failed"**
- Login to wrangler: `npx wrangler login`
- Or set API token: `export CLOUDFLARE_API_TOKEN="your-token"`
- Check project name exists in Cloudflare Pages

### Manual Steps (if script fails)

```bash
# 1. Set environment variables
export NGROK_PUBLIC_URL="https://your-ngrok-url.ngrok-free.app"
export NEXT_PUBLIC_BUSINESS_ID="your-business-id"

# 2. Build website
npm run build:ssr

# 3. Deploy to Cloudflare
npx wrangler pages deploy .vercel/output/static --project-name hero365-contractors-webs
```