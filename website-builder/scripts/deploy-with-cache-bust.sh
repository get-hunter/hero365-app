#!/bin/bash

# Deploy with Cache Busting - Ensures Cloudflare always serves latest version
# Usage: ./scripts/deploy-with-cache-bust.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
ZONE_ID="c28e66bcb1f56af2ac253ae47bf341f4"

echo "🚀 Starting deployment to $ENVIRONMENT with cache busting..."

# Step 1: Build the application
echo "📦 Building application..."
npm run build
npx opennextjs-cloudflare build

# Step 2: Deploy to Cloudflare Workers
echo "🌐 Deploying to Cloudflare Workers..."
npx wrangler deploy --env $ENVIRONMENT

# Step 3: Get the latest worker version
echo "🔍 Getting latest worker version..."
LATEST_VERSION=$(npx wrangler versions list --env $ENVIRONMENT --json | jq -r '.[0].id')
echo "Latest version: $LATEST_VERSION"

# Step 4: Deploy 100% traffic to the latest version
echo "📌 Deploying 100% traffic to latest version..."
npx wrangler versions deploy $LATEST_VERSION@100 --env $ENVIRONMENT --yes

# Step 5: Verify deployment
echo "✅ Verifying version deployment..."
npx wrangler versions list --env $ENVIRONMENT

# Step 6: Purge Cloudflare cache
echo "🧹 Purging Cloudflare cache..."

# Check if CLOUDFLARE_API_TOKEN is set
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "⚠️  CLOUDFLARE_API_TOKEN not set. Skipping cache purge."
    echo "   To enable automatic cache purging, set CLOUDFLARE_API_TOKEN environment variable."
    echo "   You can manually purge cache at: https://dash.cloudflare.com"
else
    # Purge everything for the zone
    curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
         -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
         -H "Content-Type: application/json" \
         --data '{"purge_everything":true}' \
         --silent --show-error | jq '.'
    
    echo "✅ Cache purged successfully"
fi

# Step 7: Wait a moment for propagation
echo "⏳ Waiting for propagation..."
sleep 5

# Step 8: Test the deployment
if [ "$ENVIRONMENT" = "staging" ]; then
    TEST_URL="https://elite-hvac-austin.tradesites.app"
else
    TEST_URL="https://hero365contractors.com"
fi

echo "🧪 Testing deployment at $TEST_URL..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$TEST_URL")

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Deployment successful! Site is responding with HTTP $HTTP_STATUS"
    
    # Test the debug endpoint to verify backend connectivity
    if [ "$ENVIRONMENT" = "staging" ]; then
        echo "🔍 Testing backend connectivity..."
        curl -s "$TEST_URL/api/debug/home" | jq '.backendUrl' || echo "Debug endpoint not available"
    fi
else
    echo "❌ Deployment may have issues. Site responding with HTTP $HTTP_STATUS"
    exit 1
fi

echo ""
echo "🎉 Deployment complete!"
echo "   Environment: $ENVIRONMENT"
echo "   Worker Version: $LATEST_VERSION"
echo "   URL: $TEST_URL"
echo ""
echo "💡 Tips to avoid stale deployments:"
echo "   - Always use this script instead of 'wrangler deploy' directly"
echo "   - Set CLOUDFLARE_API_TOKEN for automatic cache purging"
echo "   - Check worker versions with: npx wrangler versions list --env $ENVIRONMENT"
